import json
from importlib import import_module

# The methods specified here can be called by the server
permitted_methods = ["check_version", "update_client", "get_data"]

class PluginNotFoundException(Exception):
    pass

# Given the name and latest version (that the monitoring server has) of a plugin
# this function will return whether the client wants to be updated with the latest
# version of the plugin or not
def check_version(plugin_name, plugin_version):
    plugin_info = get_plugin_info(plugin_name)

    # Do we want to update the plugin or not?
    if plugin_version > plugin_info['version']:
        return {"want_update": True}
    else:
        return {"want_update": False}

# Called internally - For a given plugin name returns a dictionary containing
# the contents of the plugin's info.json file
def get_plugin_info(plugin_name):
    safe_plugin_name = plugin_name.strip('/').strip('\\')
    try:
        with open("plugins/{0}/info.json".format(safe_plugin_name), 'r') as f:
            plugin_info = json.load(f)
    except FileNotFoundError:
        raise PluginNotFoundException

    return plugin_info

# Called remotely - Receives the plugin as a binary payload, unpacks it and stores it
# on disk, replacing any plugins that already exist.
def update_client(plugin_name, payload):
    raise NotImplementedError


# Called remotely - Loads and instantiates the plugin and then calls the
# get_result() method of the instance. Then returns this data which will
# be sent back to the remote system
def get_data(plugin_name):
    plugin_info = get_plugin_info(plugin_name)

    # Attempt to import the plugin module and then instantiate its main class
    plugin = import_module("plugins.{0}".format(plugin_info["plugin_name"]))
    try:
        MainClass = getattr(plugin, plugin_info["classname"])
    except AttributeError:
        raise PluginNotFoundException

    plugin_instance = MainClass()

    # Execute the get_result() method of the plugin
    result = plugin_instance.get_result()

    data = {
        'level': result.result_level.value,
        'message': result.message,
        'value': result.value
    }    

    return data
