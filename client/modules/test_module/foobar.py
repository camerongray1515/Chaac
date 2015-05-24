from module import Module, ResultLevel, ModuleResult

class TestModule(Module):
    def get_result(self):
        return ModuleResult(result_level=ResultLevel.ok, message="Foobar")
