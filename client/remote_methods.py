import json
from importlib import import_module
from fsm import FSM, States

fsm = FSM()

# The methods specified here can be called by the server
permitted_methods = ["init_plugin", "update_client", "get_data"]

currently_loaded_plugin = None

class PluginNotFoundException(Exception):
    pass

def init_plugin(plugin_name, plugin_version):
    global currently_loaded_plugin

    fsm.enforce_state(States.ready)

    # Read in the plugin's information file and decode the JSON
    safe_plugin_name = plugin_name.strip('/').strip('\\')
    try:
        with open("plugins/{0}/info.json".format(safe_plugin_name), 'r') as f:
            plugin_info = json.load(f)
    except FileNotFoundError:
        raise PluginNotFoundException

    # Now import the plugin and instantiate its main class
    plugin = import_module("plugins.{0}".format(plugin_info["plugin_name"]))
    try:
        MainClass = getattr(plugin, plugin_info["classname"])
    except AttributeError:
        raise PluginNotFoundException

    currently_loaded_plugin = MainClass()

    # TODO: Check plugin version and transition to appropriate state, also return appropraite result
    fsm.transition_to_state(States.out_of_date)

def update_client(payload):
    fsm.enforce_state(States.out_of_date)

    fsm.transition_to_state(States.up_to_date)

def load_plugin():
    fsm.enforce_state(States.up_to_date)

    fsm.transition_to_state(States.plugin_loaded)

def get_data():
    fsm.enforce_state(States.plugin_loaded)

    fsm.transition_to_state(States.ready)
