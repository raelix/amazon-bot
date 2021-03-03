import requests 
import json 
from time import sleep
from bs4 import BeautifulSoup
from price_parser import parse_price
from tld import get_tld
import random
import requests
from lxml.html import fromstring
from tor import get_tor_proxies
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


user_agent_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
]

def get_headers(locale='it'):
  if locale == 'fr':
    return {
      'Host': 'www.amazon.fr',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0',
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
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0',
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
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0',
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

      # 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)

def scrape(queue, url, callback, lock, browser, use_tor, need_to_wait, exit_flag, error_counter, proxies): 
    there_was_a_failure = False

    locale = get_tld(url.strip())
    
    my_headers=get_headers(locale)
    my_headers['User-Agent'] = random.choice(user_agent_list)

    # adapter = HTTPAdapter(max_retries=retry_strategy)
    # http = requests.Session()
    # http.mount("https://", adapter)
    # http.mount("http://", adapter)
    try:
      if use_tor:
        page = requests.get(url, headers=my_headers, proxies=get_tor_proxies(), timeout=3)
      else:
        page = requests.get(url, headers=my_headers, proxies=proxies, timeout=3)

      if page.status_code > 500 or 'images-amazon.com/captcha' in page.content.decode():
          
          there_was_a_failure = True
          # print("Page %s didn't work, the status code was %d" % (url,page.status_code))

    except Exception as e:
      there_was_a_failure = True
      # print("Page %s didn't work. It failed without status code, error: %s" % (url, e))

    if there_was_a_failure:
      with lock:
        error_counter.value = error_counter.value + 1
        queue.get()
      return 

    result = parse(url, page)
    callback(queue, result, browser, need_to_wait, exit_flag)



def parse(url, page):
  soup = BeautifulSoup(page.content, 'html.parser')
  result = dict()
  result['title'] = try_find(soup, 'span', {'id':'productTitle'})
  result['price'] = get_price(
                     try_find(soup, 'span', {'id':'newBuyBoxPrice'}) or 
                     try_find(soup, 'span', {'id':'price_inside_buybox'}) or 
                     try_find(soup, 'span', {'class':'offer-price'})
                     )

  result['is_new'] = (try_find(soup, 'span', {'id':'newBuyBoxPrice'}) or  
                      try_find(soup, 'span', {'id':'price_inside_buybox'})) is not None

  result['is_available'] = (try_find(soup, 'input', {'id':'add-to-cart-button-ubb'}) or 
                            try_find(soup, 'input', {'id':'add-to-cart-button'})) is not None

  result['buy_now_available'] = try_find(soup,'span',{'id':'submit.buy-now-announce'}) is not None
  result['url'] = url
  return result

def get_price(price):
  try:
    return parse_price(price).amount_float
  except Exception as e:
    print("Error parsing price")
    

def try_find(soup, element, object, to_text=True, strip=True):
  try:
    if to_text:
      if strip:
        return soup.find(element, object).text.strip()
      else:
        return soup.find(element, object).text
    else:
      return soup.find(element, object)
  except Exception as ex:
    pass
  return None
