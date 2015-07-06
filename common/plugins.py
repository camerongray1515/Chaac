import tarfile
import io
import os
import base64
import configparser
import json

from common.exceptions import InvalidPluginError

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

# This method will take in a plugin name and return a base64 encoding of the gzip compresed
# tar archive of the plugin's contents.  This can then be sent over the SSH channel to the
# client which can then decode and decompress it back to the original files
def encode_plugin(plugin_name):
    # This appears like a file to tarfile but is in fact stored as a byte array in memory
    # this means that we can encode the file entirely in memory without needing to write
    # out to tempoary files on disk
    in_memory_file = io.BytesIO()
    tar = tarfile.open(fileobj=in_memory_file, mode="w:gz")
    # Change to the plugin_repo directory before adding files, this stops the plugin_repo
    # directory being added to the tar archive and then the files being extracted into it
    prev_dir = os.getcwd()
    os.chdir(config["Plugins"]["repo_directory"])
    # Add all files in the plugin to the archive
    num_files = 0
    for root, dirnames, filenames in os.walk(plugin_name):
        if "info.json" not in filenames or "__init__.py" not in filenames:
            raise InvalidPluginError

        for filename in filenames:
            file_path = os.path.join(root, filename)
            tar.add(file_path)
            num_files += 1

    if num_files == 0:
        raise InvalidPluginError

    tar.close()
    # Change back to the previous directory to prevent confusion
    os.chdir(prev_dir)

    # Get the byte array from the BytesIO object
    byte_array = in_memory_file.getvalue()

    # Return a base64 encoded representation of the byte array
    return base64.b64encode(byte_array)

# Returns a list with information about all plugins currently installed
def get_installed_plugins():
    """
    Returns:
        list: Contains an info dict for each installed plugin

    Raises:
        InvalidPluginError: If the plugin does not contain an info.json
                            file or if this file is invalid in some way
    """
    repo_directory = config["Plugins"]["repo_directory"]

    all_plugins = []

    for f in os.listdir(repo_directory):
        full_path = os.path.join(repo_directory, f)

        if os.path.isdir(full_path):
            try:
                with open(os.path.join(full_path,"info.json"))\
                                                        as info_file:
                    
                    plugin_info = json.load(info_file)
                
                    info_dict = {
                        "version": plugin_info["version"],
                        "class_name": plugin_info["class_name"],
                        "plugin_name": plugin_info["plugin_name"],
                        "description": plugin_info["description"]\
                                if "description" in plugin_info else ""
                    }

                    all_plugins.append(info_dict)
            except (KeyError, ValueError):
                raise InvalidPluginError(("Plugin '{0}' has an invalid "
                    "info.json file").format(f))
            except FileNotFoundError:
                raise InvalidPluginError(("Plugin '{0}' does not have "
                    "an info.json file").format(f))


    return all_plugins

if __name__ == "__main__":
    print(get_installed_plugins())
