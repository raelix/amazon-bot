import abc
class ScraperInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_valid(self, page):
        pass

    @abc.abstractmethod
    def parse(self, page):
        pass

    @abc.abstractmethod
    def verify_matching(self, result, task):
        pass