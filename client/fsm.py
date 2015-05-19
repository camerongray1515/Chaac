from enum import Enum

class InvalidStateException(Exception):
    pass

class States(Enum):
    ready = 0
    out_of_date = 1
    module_loaded = 2
    running = 3


class FSM(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self._current_state = States.ready

    def enforce_state(self, state):
        if self._current_state != state:
            self.reset()
            raise InvalidStateException("An invalid command was received. Client has been reset")
        return True

    def transition_to_state(self, state):
        self._current_state = state
