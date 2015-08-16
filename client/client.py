import json
import configparser
import sys
import argparse

from flask import Flask, jsonify, request
from plugin_helpers import get_plugin_info
from exceptions import PluginNotFoundError
from importlib import import_module
from client_setup import start_setup_wizard

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

parser = argparse.ArgumentParser()
parser.add_argument("--setup", help="Run the setup wizard",
        action="store_true")
args = parser.parse_args()

client = Flask(__name__)
client.secret_key = "changemetemp7qWYsGtL5fDHFMhG"

@client.route("/check_plugin_version/", methods=["GET"])
def check_plugin_version():
    if not("name" in request.args and "version" in request.args):
        return jsonify(success=True, message="Must specify a plugin "
                "name and version to check")
    
    plugin_name = request.args.get("name")

    try:
        plugin_version = float(request.args.get("version"))
    except ValueError:
        return jsonify(success=False, message="Version must be a float")


    try:
        plugin_info = get_plugin_info(plugin_name)
    except PluginNotFoundError:
        # If the plugin is not found, say we want an update to request the plugin to
        # be installed onto this client
        return jsonify(success=True, want_update=True)

    # Do we want to update the plugin or not?
    if plugin_version > plugin_info['version']:
        return jsonify(success=True, want_update=True)
    else:
        return jsonify(success=True, want_update=False)

@client.route("/execute_plugin/", methods=["GET"])
def execute_plugin():
    if "name" not in request.args:
        return jsonify(success=False, message="Must specify plugin name")
    

    plugin_name = request.args.get("name")

    try:
        plugin_info = get_plugin_info(plugin_name)
    except PluginNotFoundError:
        return jsonify(success=False, message="Plugin not found")

    # Attempt to import the plugin module and then instantiate its main class
    plugin = import_module("plugins.{0}".format(plugin_info["plugin_name"]))
    MainClass = getattr(plugin, plugin_info["classname"])

    plugin_instance = MainClass()

    # Execute the get_result() method of the plugin
    result = plugin_instance.get_result()

    data = {
        'level': result.result_level.value,
        'message': result.message,
        'value': result.value
    }    

    return jsonify(data)

if __name__ == "__main__":
    if args.setup:
        start_server = start_setup_wizard()
        if not start_server:
            sys.exit()

    config = configparser.ConfigParser()
    config.read("config.ini")
    
    if not config.sections():
        print("No config file found, you must start the client giving the "
                "--setup command line argument to run the setup wizard")
        sys.exit()

    client.config["CONFIG"] = config

    http_server = HTTPServer(WSGIContainer(client))
    http_server.listen(config["Server"]["port"])
    IOLoop.instance().start()
