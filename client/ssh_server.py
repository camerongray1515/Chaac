import paramiko
import threading
import socket
import sys
import traceback
import re
import os

class ParamikoServer(paramiko.ServerInterface):
    def __init__(self, keys_directory, authorized_keys_file):
        self._event = threading.Event()
        self._keys_directory = keys_directory
        self._authorized_keys_file = authorized_keys_file

    def check_auth_publickey(self, username, key):
        # We need to loop through all authorized keys and if any match we allow
        # the connection, otherwise we do not allow it.
        with open(os.path.join(self._keys_directory, self._authorized_keys_file), 'r') as keyfile:
            for entry in keyfile:
                # Extract the key portion from the rest of the line
                match = re.match(r"^.* ([^ ]*) .*$", entry)
                if match == None:
                    print("*** Invalid key format found in authorized_keys, ignoring!")
                    continue

                authorized_key = paramiko.RSAKey(data=paramiko.py3compat.decodebytes(
                                                        match.group(1).encode('UTF-8')))

                # Allow connection if the keys match
                if key == authorized_key:
                    return paramiko.AUTH_SUCCESSFUL

            print("*** Client authentication failed")
            return paramiko.AUTH_FAILED


        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return 'publickey'

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self._event.set()
        return True

    @property
    def event(self):
        return self._event


# TODO: Add some sort of constructor to this so we can pass in
# configurable options such as port numbers, addresses, buffer
# sizes.etc
class SSHServer():
    def __init__(self, port, keys_directory, host_key_file, authorized_keys_file, buffer_size=1024, backlog=100):
        self._port = port
        self._buffer_size = buffer_size
        self._backlog = backlog
        self._keys_directory = keys_directory
        self._host_key_file = host_key_file
        self._authorized_keys_file = authorized_keys_file

    # This callback function is called whenever a message is
    # receieved down the SSH connection
    @property
    def message_received_callback(self):
        return self._message_received_callback
    @message_received_callback.setter
    def message_received_callback(self, value):
        self._message_received_callback = value
    
    # This sends a message back to the connected client
    def send(self, msg):
        self._channel.send(msg)

    # TODO: This should probably be split up more
    def start(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind(('', self._port))
        except Exception as ex:
            print("*** Error binding port: {0}".format(str(ex)))
            sys.exit(1) # TODO: Don't have this exit

        try:
            self._sock.listen(self._backlog)
            print("Awaiting connection...")
            client, addr = self._sock.accept()
        except Exception as ex:
            print("*** Failed to listen: {0}".format(str(ex)))
            raise

        print("Connected!")

        try:
            self.transport = paramiko.Transport(client)

            try:
                self.transport.load_server_moduli()
            except:
                print("*** Cannot load moduli")
                raise

            # TODO: Make this key file configurable
            self.transport.add_server_key(paramiko.RSAKey(filename=os.path.join(self._keys_directory, self._host_key_file)))
            server = ParamikoServer(keys_directory=self._keys_directory,
                                    authorized_keys_file=self._authorized_keys_file)

            try:
                self.transport.start_server(server=server)
            except Exception as ex:
                print("*** SSH negotiation failed: {0}".format(str(ex)))
                raise

            self._channel = self.transport.accept(30)
            if self._channel == None:
                print("*** No channel - End system possibly failed authentication")
                self.restart()

            server.event.wait(30)
            if not server.event.is_set():
                print("*** Connected system never asked for a shell")
                raise

            recv_buffer = ""
            while (True):
                recv_buffer += self._channel.recv(self._buffer_size).decode('utf8')
                # If the received buffer is empty, then the remote system has disconnected.
                # Restart the SSH server awaiting another client to connect
                if recv_buffer == "":
                    self.restart()
                    return

                # If this is the end of the message (buffer has a newline at the end)
                # pass the full buffer to the callback method and then clear the buffer
                # out awaiting the next message
                if recv_buffer[-1] == "\n":
                    self.message_received_callback(self, recv_buffer)
                    recv_buffer = ""

        # TODO: This is too broad
        except Exception as ex:
            # If we hit an exception, close everything and restart the server
            print("Caught Exception: {0}".format(str(ex)))
            print(traceback.format_exc())
            self.restart()

    def restart(self):
        try:
            self.transport.close()
            self._sock.close()
        except:
            pass
        self.start()
