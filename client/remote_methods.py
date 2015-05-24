import json
from importlib import import_module
from fsm import FSM, States

fsm = FSM()

# The methods specified here can be called by the server
permitted_methods = ["init_module", "update_client", "get_data"]

currently_loaded_module = None

class ModuleNotFoundException(Exception):
    pass

def init_module(module_name, module_version):
    global currently_loaded_module

    fsm.enforce_state(States.ready)

    # Read in the module's information file and decode the JSON
    safe_module_name = module_name.strip('/').strip('\\')
    try:
        with open("modules/{0}/info.json".format(safe_module_name), 'r') as f:
            module_info = json.load(f)
    except FileNotFoundError:
        raise ModuleNotFoundException

    # Now import the module and instantiate its main class
    module = import_module("modules.{0}".format(module_info["module_name"]))
    try:
        MainClass = getattr(module, module_info["classname"])
    except AttributeError:
        raise ModuleNotFoundException

    currently_loaded_module = MainClass()

    # TODO: Check module version and transition to appropriate state, also return appropraite result
    fsm.transition_to_state(States.out_of_date)

def update_client(payload):
    fsm.enforce_state(States.out_of_date)

    fsm.transition_to_state(States.up_to_date)

def load_module():
    fsm.enforce_state(States.up_to_date)

    fsm.transition_to_state(States.module_loaded)

def get_data():
    fsm.enforce_state(States.module_loaded)

    fsm.transition_to_state(States.ready)
