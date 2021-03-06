from multiprocessing import Queue, Process, Manager, Value
import time
import random
from worker import worker_task
from producer import producer_task
from buyer import buyer_task
from statistic import statistic_task
from parser_factory import ParserFactory
import queue as Queue

class Supervisor(object):

  def __init__(self):
    self.manager = Manager()
    self.queue = self.manager.Queue()
    self.statistics = self.manager.Queue()
    self.status = self.manager.Queue()
    self.availability = self.manager.Queue()
    self.terminator = self.manager.Queue()
    self.parser = ParserFactory().get_parser(self.config_changed, 'text')
    # self.NUMBER_OF_PROCESSES = cpu_count()

  def start(self):
    self.list_map = self.parser.get_list()
    self.spawn_workers()
    self.spawn_producer()
    self.spawn_buyer()
    self.spawn_statistic()

    try:
      while True:
        try:
          task = self.terminator.get(True, 1)
          print("The item has been purchased!")
          self.stop()
          exit(0)
        except Queue.Empty:
          pass
    except KeyboardInterrupt:
        self.stop()
  
  def spawn_workers(self):
    list_size = len(self.list_map)
    self.workers = [Process(target=worker_task, args=(self.queue, self.statistics, self.availability))
                    for i in range(list_size)]
    for worker in self.workers:
      worker.start()

  def spawn_producer(self):
    self.producer = [Process(target=producer_task, args=(self.status, self.list_map, self.queue))]
    for producer in self.producer:
      producer.start()

  def spawn_buyer(self):
    self.buyer = [Process(target=buyer_task, args=(self.availability, self.terminator))]
    for buyer in self.buyer:
      buyer.start()

  def spawn_statistic(self):
    self.statistic = [Process(target=statistic_task, args=(self.statistics, self.status))]
    for statistic in self.statistic:
      statistic.start()

  def stop(self):
    self.stop_workers()
    self.stop_producer()
    self.stop_buyer()
    self.stop_statistic()

  def stop_workers(self):
    for worker in self.workers:
      worker.terminate()
      worker.join()

  def stop_producer(self):
    for producer in self.producer:
      producer.terminate()
      producer.join()

  def stop_buyer(self):
    for buyer in self.buyer:
      buyer.terminate()
      buyer.join()

  def stop_statistic(self):
    for statistic in self.statistic:
      statistic.terminate()
      statistic.join()

  def config_changed(self, list_map):
      print(f'event type: {event.event_type}  path : {event.src_path}')
      self.list_map = list_map
      self.stop_producer()
      self.spawn_producer()

def main():
  manager = Supervisor()
  manager.start()
  

if __name__ == "__main__":
  main()