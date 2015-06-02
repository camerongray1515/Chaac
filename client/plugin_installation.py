import tarfile
import base64
import os
import io

# TODO: If the plugin already exists, delete it before extracting.  Otherwise we
# TODO: we run the risk of leaving files in the plugin directory from the old
# TODO: version that were removed from the new version.

# This method takes in a base64 encoded string (that is received from the server)
# decodes it and then decompresses and extracts the resulting tar.gz archive to
# put the plugin on the server
def unpack_plugin(base64_encoded_plugin):
    # Decode the base64 string into a byte array and then create a ByteIO object
    # from it.  This object appears to the tarfile module as though it is a
    # regular file on disk and can therefore be extracted from memory.
    byte_array = base64.b64decode(base64_encoded_plugin)
    in_memory_file = io.BytesIO(byte_array)

    # Extract all files in the archive to the plugins directory
    tar = tarfile.open(fileobj=in_memory_file, mode="r:gz")
    tar.extractall(path="plugins")    
