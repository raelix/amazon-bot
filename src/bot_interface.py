import abc

class BotInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def login(self, browser, portal, email, password):
        pass

    @abc.abstractmethod
    def buy(self, browser, url, isTest):
        pass
