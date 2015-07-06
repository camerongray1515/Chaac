import tarfile
import io
import os
import base64
import configparser

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
