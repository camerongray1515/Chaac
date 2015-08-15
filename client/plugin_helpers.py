import json
from exceptions import PluginNotFoundError

def get_plugin_info(plugin_name):
    safe_plugin_name = plugin_name.strip('/').strip('\\')
    try:
        with open("plugins/{0}/info.json".format(safe_plugin_name), 'r') as f:
            plugin_info = json.load(f)
    except FileNotFoundError:
        raise PluginNotFoundError

    return plugin_info
