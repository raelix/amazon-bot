import abc
class ProxyInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_map(self):
        pass

    @abc.abstractmethod
    def get_unique_map(self, key):
        pass

    @abc.abstractmethod
    def get_new_map(self):
        pass

    @abc.abstractmethod
    def get_source_ip(self):
        pass

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

