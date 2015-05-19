import paramiko
import threading
import socket
import sys

class ParamikoServer(paramiko.ServerInterface):
    def __init__(self):
        self._event = threading.Event()

    # Tempoary testing auth - use keys in production
    def check_auth_password(self, username, password):
        if username=="foo" and password=="bar":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

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
            self._sock.bind(('', 2200)) # TODO: Don't have hardcoded port
        except Exception as ex:
            print("*** Error binding port: {0}".format(str(ex)))
            sys.exit(1) # TODO: Don't have this exit

        try:
            self._sock.listen(100) # TODO: Make backlog configurable
            print("Awaiting connection...")
            client, addr = self._sock.accept()
        except Exception as ex:
            print("*** Failed to listen: {0}".format(set(ex)))
            raise

        print("Connected!")

        try:
            transport = paramiko.Transport(client)

            try:
                transport.load_server_moduli()
            except:
                print("*** Cannot load moduli")
                raise

            # TODO: Make this key file configurable
            transport.add_server_key(paramiko.RSAKey(filename='keys/server_rsa.key'))
            server = ParamikoServer()

            try:
                transport.start_server(server=server)
            except Exception as ex:
                print("*** SSH negotiation failed: {0}".format(str(ex)))
                raise

            self._channel = transport.accept(30)
            if self._channel == None:
                print("*** No channel")
                raise

            server.event.wait(30)
            if not server.event.is_set():
                print("*** Connected system never asked for a shell")
                raise

            while (True):
                recv_bytes = self._channel.recv(1024)
                self.message_received_callback(self, recv_bytes.decode('utf8'))

        # TODO: This is too broad
        except Exception as ex:
            # If we hit an exception, close everything and restart the server
            print("Caught Exception: {0}".format(str(ex)))

            try:
                transport.close()
                self._sock.close()
            except:
                pass
            self.start()
