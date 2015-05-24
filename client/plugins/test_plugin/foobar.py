from plugin import Plugin, ResultLevel, PluginResult

class TestPlugin(Plugin):
    def get_result(self):
        return PluginResult(result_level=ResultLevel.ok, message="Foobar")
