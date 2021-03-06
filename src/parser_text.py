from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils import load_list_from_file
from parser_interface import ConfigParser

URLS_FILEPATH='./urls.txt'
DEFAULT_MAX_PRICE=300

class ParserText(FileSystemEventHandler, ConfigParser):

  def __init__(self):
    self.observer = Observer()

  def start(self, callback):
    self.observer.schedule(self, path=URLS_FILEPATH, recursive=False)
    self.observer.start()
    self.callback = callback

  def get_list(self):
      URLs = load_list_from_file(URLS_FILEPATH)
      return self.__create_list(URLs)

  def stop(self):
    self.observer.stop()
    self.observer.join()

  def on_modified(self, event):
      print(f'event type: {event.event_type}  path : {event.src_path}')
      self.callback(self.get_list())

  def __create_list(self, URLs):
    urls_list = []
    for url in URLs:
      url_and_price = url.split(',')
      url_map = {
        'url': url_and_price[0],
        'price': url_and_price[1] if len(url_and_price) > 1 else DEFAULT_MAX_PRICE
      }
      urls_list.append(url_map)
    return urls_list
