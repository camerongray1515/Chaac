import json
import remote_methods
from ssh_server import SSHServer

# This method is called whenever a message is received down the SSH
# connection.  It will decode the JSON and execute the specified method
# from the "remote_message" plugin then send the result back up the SSH
# connection encoded as JSON. The "srv" argument is an instance of the
# SSHServer class and can be used to send data back up the connection
def server_message_received(srv, msg):
    request = json.loads(msg)

    # Check that the method requested is allowed to be called remotely
    if request['method'] in remote_methods.permitted_methods:
        # Attempt to call the remote method and catch errors if the system
        # did not expect the given method in its current state or if the
        # specified plugin could not be found in the system
        try:
            method = getattr(remote_methods, request['method'])
            result = method(**request['arguments'])
            error = False
        except remote_methods.PluginNotFoundException:
            result = "plugin_not_found"
            error = True
    else:
        result = "invalid_method"
        error = True

    # Format the data obtained above into the correct JSON string and then
    # send this back to the connected system through the SSH connection
    response = json.dumps({"error": error, "result": result})
    srv.send(response)

if __name__ == "__main__":
    # Create an instance of the SSH server, set the callback method that
    # will be executed whenever a message is receieved down the connection
    # and then start the SSH server running
    server = SSHServer()
    server.message_received_callback = server_message_received
    server.start()
