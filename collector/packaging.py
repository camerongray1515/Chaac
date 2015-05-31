import tarfile
import io
import os
import base64

# TODO: Currently the tar archive extracts to include the "plugin_repo" directory, fix this
# TODO: so that it only extracts the directory containing the plugin itself

# This method will take in a plugin name and return a base64 encoding of the gzip compresed
# tar archive of the plugin's contents.  This can then be sent over the SSH channel to the
# client which can then decode and decompress it back to the original files
def encode_plugin(plugin_name):
    # This appears like a file to tarfile but is in fact stored as a byte array in memory
    # this means that we can encode the file entirely in memory without needing to write
    # out to tempoary files on disk
    in_memory_file = io.BytesIO()
    tar = tarfile.open(fileobj=in_memory_file, mode="w:gz")
    # Add all files in the plugin to the archive
    for root, dirnames, filenames in os.walk(os.path.join("plugin_repo", plugin_name)):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            tar.add(file_path)
    tar.close()

    # Get the byte array from the BytesIO object
    byte_array = in_memory_file.getvalue()

    # Return a base64 encoded representation of the byte array
    return base64.b64encode(byte_array)

if __name__ == "__main__":
    print(encode_plugin("test_plugin"))
