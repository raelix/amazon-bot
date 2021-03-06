from proxy_interface import ProxyInterface
import requests


class ProxyNone(ProxyInterface):

  def __init__(self):
    pass

  def get_map(self):
    return {}

  def get_new_map(self):
    return self.get_map()

  def get_source_ip(self):
    try:
      session = requests.session()
      session.proxies = self.get_map()
      source_ip = session.get("https://icanhazip.com/", timeout=3).text.strip()
      return source_ip
    except Exception as e:
      print("Cannot get remote IP")
    return 'Remote IP not available'

  def start(self):
    pass

  def stop(self):
    pass

  def get_unique_map(self, key):
    return self.get_map()
