import json
import remote_methods
from ssh_server import SSHServer
from fsm import InvalidStateException

# This method is called whenever a message is received down the SSH
# connection.  It will decode the JSON and execute the specified method
# from the "remote_message" module then send the result back up the SSH
# connection encoded as JSON. The "srv" argument is an instance of the
# SSHServer class and can be used to send data back up the connection
def server_message_received(srv, msg):
    request = json.loads(msg)

    if request['method'] in remote_methods.permitted_methods:
        try:
            method = getattr(remote_methods, request['method'])
            result = method(**request['arguments'])
            error = False
        except InvalidStateException:
            result = "invalid_state"
            error = True
        except remote_methods.ModuleNotFoundException:
            result = "module_not_found"
            error = True
    else:
        result = "invalid_method"
        error = True

    response = json.dumps({"error": error, "result": result})
    srv.send(response)

if __name__ == "__main__":
    server = SSHServer()
    server.message_received_callback = server_message_received
    server.start()
