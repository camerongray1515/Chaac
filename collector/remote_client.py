import paramiko
import socket
import json

from common.exceptions import NoConnectionError, RemoteCommandFailedError

class RemoteClient(object):
    def __init__(self, hostname, port, username, key_path):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.key_path = key_path

    def open(self):
        print("Starting SSH connection to client...")
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.WarningPolicy())

        key = paramiko.RSAKey.from_private_key_file(self.key_path)

        self._client.connect(hostname=self.hostname, port=self.port,
                             username=self.username, pkey=key)

        self._transport = self._client.get_transport()
        self._channel = self._transport.open_session()

        print("Connected to client!")

    def _execute_command(self, method, arguments_dict):
        # Build up a dictionary to hold the command, dump it as json, append a newline to
        # the JSON string (to signify the end of a comamnd to the remote system) and then
        # send it down the SSH connection
        command = {"method": method, "arguments": arguments_dict}
        command_string = json.dumps(command) + "\n"

        # If self does not have the _channel attribute, then the client has not been
        # connected yet!
        try:
            self._channel.send(command_string)
        except AttributeError:
            raise NoConnectionError

        # Now receive the response from the channel - To ensure that we receive data even if
        # is is larger than the channel's buffer we keep receiving data until we recieve a
        # newline character signifying the end of the transmission
        recieve_buffer = bytearray()
        end_of_transmission = False
        while(not end_of_transmission):
            recieve_buffer.extend(self._channel.recv(1024))
            if recieve_buffer.endswith(b"\n"):
                end_of_transmission = True

        response = json.loads(recieve_buffer.decode("UTF-8"))
        if response["error"]:
            raise RemoteCommmandFailedError
        else:
            return response["result"]

    def check_version(self, plugin_name, plugin_version):
        arguments_dict = {  "plugin_name": plugin_name,
                            "plugin_version": plugin_version}

        return self._execute_command("check_version", arguments_dict)

    def update_client(self, plugin_name, payload):
        arguments_dict = {  "plugin_name": plugin_name,
                            "payload": payload}

        return self._execute_command("update_client", arguments_dict)

    def get_data(self, plugin_name):
        arguments_dict = {"plugin_name": plugin_name}

        return self._execute_command("get_data", arguments_dict)

    def close(self):
        print("Closing SSH connection to client...")
        self._channel.close()
        self._client.close()
        print("Connection closed!")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

if __name__ == "__main__":
    with RemoteClient("127.0.0.1", 2200, "foo", "../client/keys/id_rsa.key") as client:
        print(client.get_data("test_plugin"))
