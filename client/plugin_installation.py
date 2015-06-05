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

    # We should now verify that the top level direcotry in the archive is the
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

if __name__ == "__main__":
    unpack_plugin("test_plugin", "H4sIAOn4cVUC/+3UQUvDMBgG4J77K0JPG5SaZOsKg109eRDxHupMS7VNRpIORPzvZs2mVREvs6C8zyU0SRuSfm+ctE7s2r5u1IUQjWqcENnuKTon6q2Wy0PLipwOzyw8B4siYjxf8ILygvOIslVOaURoNIHeutIQEm3LThqt6u/nSWN/2KT31v4RldEdySqt7/wpNN1OG0dufU1cDyURR/C/uVH+QxWcO/0/55+v8s/552yJ/E+W//D/T/EP0U/JjbR9667kXrbpsTN0xfG2La0d3ROz0MzXMfHuZUVq6YQZZs+sbKvjyIGRrjfqwwdnYaZoD2ttRutm+jElnbS2rOUmuRzqM5njVvqd/Deq0tmD1Wri/LMF/ZJ/WiD/U3gecpmEChDKH0KyJsmoKpI0zNj77Tda+VGW0WPfcA2c3nm/DZL4BREFAAAAAAAAAAAAAAAAAJjYK/pnt6gAKAAA")
    # unpack_plugin("test_plugin", "H4sIALz7cVUC/+3UQWuDMBgGYM/+iuCpBXFJWhUKve60wxi7i2ujuGlSklgYY/99qWk3tzF6WYWN97kEYzREv/ezwthi1/Z1I6+2ye45uADqZMvlYWR5Sodr5q+9RR4wni54TnnOeUBZyrJlQGgwgd7YUhMSbMpOaCXrn9cJbc4c0nkf/4hKq44klVIP7is03U5pS+5dTdwOJREG8L/ZUf59Ffx+EziXf56lX/KfcYb8T5d///9P8ffRj8mdMH1rb8RetPFx0k+F4aYtjRn1iZkf5quQOFtRkVrYQg+rZ0a01fHOgRa21/LTC2d+ZdEe9lqP9k3UU0w6YUxZi3V0PdRnNEdXukz+G1mp5NEoOXH+2YJ+yz/Nkf8pvAy5jHwFFNJ9hGhFolFVRLFfsXfHb5R0d1lCj3NDGzg989ENovAVEQUAAAAAAAAAAAAAAAAAmNgbcynDVwAoAAA=")
