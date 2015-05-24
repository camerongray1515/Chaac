from enum import Enum
from abc import ABCMeta, abstractmethod

class Plugin(metaclass=ABCMeta):
    @abstractmethod
    def get_result(self):
        pass


class ResultLevel(Enum):
    critical = 3
    major = 2
    minor = 1
    ok = 0
    unknown = -1


class PluginResult(object):
    def __init__(self, result_level, message="", value=0):
        self._result_level = result_level
        self._message = message
        self._value = value

    @property
    def result_level(self):
        return self._result_level
    @result_level.setter
    def result_level(self, value):
        self._result_level = value

    @property
    def message(self):
        return self._message
    @message.setter
    def message(self, value):
        self._message = value
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value

    def __repr__(self):
        return "<PluginResult level: {0}, message: '{1}', value: {2}>".format(self.result_level, self.message, self.value)
    
    
    
