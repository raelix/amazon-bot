
import random
from user_agent import generate_user_agent

def get_headers(locale='it'):
  custom_headers = __get_headers(locale)
  custom_headers['User-Agent'] = generate_user_agent()
  return custom_headers

def __get_headers(locale='it'):
  if locale == 'fr':
    return {
      'Host': 'www.amazon.fr',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-GPC': '1',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache'
      }
  elif locale == 'es':
    return {
      'Host': 'www.amazon.es',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-GPC': '1',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache'
    }
  elif locale == 'de':
    return {
      'Host': 'www.amazon.de',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-GPC': '1',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache'
    }
  else:
    return {
      'Host': 'www.amazon.it',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Cache-Control': 'max-age=0',
    }