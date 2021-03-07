import abc
class ConfigParser(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def start(self, callback):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def get_configuration(self):
        pass

    @abc.abstractmethod
    def get_list_URLs(self):
        pass


