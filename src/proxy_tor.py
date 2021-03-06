
from proxy_interface import ProxyInterface
import requests
from stem import process
import uuid
#https://stackoverflow.com/questions/30286293/make-requests-using-python-over-tor

DEFAULT_SOCK5_PORT   = 9050
DEFAULT_SOCK5_PORT   = 9050
DEFAULT_CONTROL_PORT = 9051


def get_new_hash():
  return uuid.uuid4().hex

class ProxyTor(ProxyInterface):

  def __init__(self):
    self.password = get_new_hash()

  def get_map(self):
    return self.__get_tor_proxies(self.password)

  def get_new_map(self):
    self.password = get_new_hash()
    return self.get_map()

  def get_unique_map(self, key):
    return self.__get_tor_proxies(key)

  def get_source_ip(self):
    try:
      session = requests.session()
      session.proxies = self.get_map()
      source_ip = session.get("https://icanhazip.com/", timeout=3).text.strip()
      return source_ip
    except Exception as e:
      print("Cannot get remote IP")
    return 'Remote IP not available'

  def __get_tor_proxies(self, password='random_password'):
    return {
      'http': 'socks5://user:{}@localhost:{}'.format(password, DEFAULT_SOCK5_PORT),
      'https': 'socks5://user:{}@localhost:{}'.format(password, DEFAULT_SOCK5_PORT)
    }


  def start(self):
    self.tor = process.launch_tor_with_config({'ControlPort': str(DEFAULT_CONTROL_PORT), 'SocksPort': str(DEFAULT_SOCK5_PORT)})

  def stop(self):
    self.tor.terminate()

