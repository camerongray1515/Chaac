import json
from importlib import import_module
from fsm import FSM, States

fsm = FSM()

# The methods specified here can be called by the server
permitted_methods = ["init_plugin", "update_client", "get_data"]

current_plugin_info = None
currently_loaded_plugin = None

class PluginNotFoundException(Exception):
    pass

def init_plugin(plugin_name, plugin_version):
    global current_plugin_info

    fsm.enforce_state(States.ready)

    # Read in the plugin's information file and decode the JSON
    safe_plugin_name = plugin_name.strip('/').strip('\\')
    try:
        with open("plugins/{0}/info.json".format(safe_plugin_name), 'r') as f:
            current_plugin_info = json.load(f)
    except FileNotFoundError:
        raise PluginNotFoundException

    # Do we want to update the plugin or not?
    if plugin_version > current_plugin_info['version']:
        fsm.transition_to_state(States.out_of_date)
        return {"want_update": True}
    else:
        fsm.transition_to_state(States.up_to_date)
        load_plugin()
        return {"want_update": False}

# Called remotely - Receives the plugin as a binary payload, unpacks it and stores it
# on disk, replacing any plugins that already exist.
def update_client(payload):
    fsm.enforce_state(States.out_of_date)

    fsm.transition_to_state(States.up_to_date)
    load_plugin() # We are up to date so can now load the plugin

# Called internally whenever we transition into the up_to_date state.  Imports
# the plugin's module and instantiates the plugin's main class.
def load_plugin():
    global currently_loaded_plugin

    fsm.enforce_state(States.up_to_date)

    # Import the plugin and instantiate its main class
    plugin = import_module("plugins.{0}".format(current_plugin_info["plugin_name"]))
    try:
        MainClass = getattr(plugin, current_plugin_info["classname"])
    except AttributeError:
        raise PluginNotFoundException

    currently_loaded_plugin = MainClass()

    fsm.transition_to_state(States.plugin_loaded)

# Called remotely and executes the get_result() method of the loaded plugin and then
# returns this data which will be sent back to the remote system
def get_data():
    fsm.enforce_state(States.plugin_loaded)

    result = currently_loaded_plugin.get_result()

    data = {
        'level': result.result_level.value,
        'message': result.message,
        'value': result.value
    }    

    fsm.transition_to_state(States.ready)
    return data
