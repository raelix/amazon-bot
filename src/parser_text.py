from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser_interface import ConfigParser
import json 

URLS_FILEPATH='./configuration.json'

class ParserText(FileSystemEventHandler, ConfigParser):

  def __init__(self):
    self.observer = Observer()
    self.configuration = None

  def start(self, callback):
    self.observer.schedule(self, path=URLS_FILEPATH, recursive=False)
    self.observer.start()
    self.callback = callback
    self.configuration = self.get_configuration()

  def get_configuration(self):
    if self.configuration != None:
      return self.configuration
    else:
      with open(URLS_FILEPATH) as json_file: 
        self.configuration = json.load(json_file) 
        return self.configuration

  def stop(self):
    self.observer.stop()
    self.observer.join()

  def on_modified(self, event):
      print(f'event type: {event.event_type}  path : {event.src_path}')
      self.configuration = None
      self.callback(self.get_configuration())

  def get_list_URLs(self):
    result_list = []
    for scrape in self.get_configuration()['scrapers']:
      for url_map in scrape['URLs']:
        url_map['consumer'] = scrape['consumer']
        url_map['buyer'] = scrape['buyer']
        result_list.append(url_map)
    return result_list