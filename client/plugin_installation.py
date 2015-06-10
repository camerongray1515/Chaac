import tarfile
import base64
import os
import io
import shutil

from exceptions import InvalidPluginError

# This method takes in a base64 encoded string (that is received from the server)
# decodes it and then decompresses and extracts the resulting tar.gz archive to
# put the plugin on the server
def unpack_plugin(plugin_name, base64_encoded_plugin):
    # Decode the base64 string into a byte array and then create a ByteIO object
    # from it.  This object appears to the tarfile module as though it is a
    # regular file on disk and can therefore be extracted from memory.
    byte_array = base64.b64decode(base64_encoded_plugin)
    in_memory_file = io.BytesIO(byte_array)

    # Extract all files in the archive to the plugins directory
    tar = tarfile.open(fileobj=in_memory_file, mode="r:gz")

    # We should now verify that the top level directory in the archive is the
    # plugin's name and that the required files exist in the archive before we
    # extract it.
    plugin_files = tar.getnames()
    archive_directory_name = os.path.commonprefix(plugin_files).replace("/", "")

    if archive_directory_name.strip() == "":
        raise InvalidPluginError
    
    if plugin_name != archive_directory_name:
        raise InvalidPluginError

    # Plugin must always contain a info.json file and an __init__.py file
    if (archive_directory_name+"/info.json" not in plugin_files 
        or archive_directory_name+"/__init__.py" not in plugin_files):
        raise InvalidPluginError

    # We are now happy to install the plugin so delete the plugin from disk if it
    # already exists.  We don't care if we can't find the directory, it just means
    # that the machine does not already have the plugin we are installing
    try:
        shutil.rmtree(os.path.join("plugins", archive_directory_name))
    except FileNotFoundError:
        pass

    # Finally extract the archive to the plugins directory therefore installing it
    tar.extractall(path="plugins")    
