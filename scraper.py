import requests 
import json
from bs4 import BeautifulSoup
from headers import get_headers
from price_parser import parse_price
from tld import get_tld
import requests
# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry


# retry_strategy = Retry(
#     total=3,
#     status_forcelist=[429, 500, 502, 503, 504],
#     method_whitelist=["HEAD", "GET", "OPTIONS"]
# )

def scrape(queue, url, callback, lock, browser, need_to_wait, exit_flag, error_counter, success_counter, proxy, my_ip): 
    there_was_a_failure = False

    locale = get_tld(url.strip())

    # adapter = HTTPAdapter(max_retries=retry_strategy)
    # http = requests.Session()
    # http.mount("https://", adapter)
    # http.mount("http://", adapter)
    try:
      page = requests.get(url, headers=get_headers(locale), proxies=proxy, timeout=3)

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
    else:
      with lock:
        success_counter.value = success_counter.value + 1
    result = parse(url, page, my_ip)
    callback(queue, result, browser, need_to_wait, exit_flag)



def parse(url, page, my_ip):
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
  result['source_ip'] = my_ip
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
