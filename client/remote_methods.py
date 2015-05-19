from fsm import FSM, States

fsm = FSM()

# The methods specified here can be called by the server
permitted_methods = ["fetch_init", "update_client", "get_data"]

def fetch_init(module_name, module_version):
    fsm.enforce_state(States.ready)

    fsm.transition_to_state(States.out_of_date)

def update_client(payload):
    fsm.enforce_state(States.out_of_date)

    fsm.transition_to_state(States.module_loaded)

def get_data():
    fsm.enforce_state(States.module_loaded)

    fsm.transition_to_state(States.ready)
