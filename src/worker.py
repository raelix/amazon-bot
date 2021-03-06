import queue as Queue
from bs4 import BeautifulSoup
from headers import get_headers
from price_parser import parse_price
from tld import get_tld
import random, time, json, urllib3, requests, os

request_timeout=int(os.getenv('REQUEST_TIMEOUT', '5').lower())
wait_random=os.getenv('WAIT_RANDOM', 'false').lower() in ['true', '1']

def worker_task(queue, statistics, availability):
  while True:
    try:
      task = queue.get(True, 1)

      locale = get_tld(task['url'].strip())
      if wait_random:
        time.sleep(random.uniform(0,2))
      
      page = requests.get(task['url'], headers=get_headers(locale), proxies=task['proxy'], timeout=request_timeout)
      
      if page.status_code > 500:
        # print('Status code 500 %s' % page.status_code) 
        send_statistics(True, task, statistics)
        continue
      if 'images-amazon.com/captcha' in page.content.decode():
        # print('Captcha %s' % page.status_code) 
        send_statistics(True, task, statistics)
        continue

      send_statistics(False, task, statistics)
      result = parse(page)

      print(json.dumps(result, indent=4, sort_keys=True))

      if verify_matching(result, task):
        availability.put(task)

    except Queue.Empty:
      pass
      # print('worker: waiting for a task.')
    except KeyboardInterrupt:
      print('Interrupted by keyboard')
      return 
    except Exception as e:
      print(e)
      # print('Request timeout')
      send_statistics(True, task, statistics)

def send_statistics(failed, task, statistics):
  try:
    statistic = {}
    statistic['id'] = task['id'] 
    statistic['failed'] = failed 
    statistics.put(statistic)
  except KeyboardInterrupt:
    print('Interrupted by keyboard')
    return 

def verify_matching(result, task):
  if result['is_available'] and result['is_amazon']:
    price = result['price']
    print('Price is %s' % price)
    if price > int(task['limit_price']):
      print('Price is too high, currently: %s euro.' % price)
      print('Limit: %s' % task['limit_price'])
    else:
      print('Price is good %s!' % price)
      return True
  return False

def parse(page):
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
  merchant_info = try_find(soup,'div',{'id':'merchant-info'}) 
  seller_info = try_find(soup,'a',{'id':'sellerProfileTriggerId'}) 
  is_amazon = True if (merchant_info is not None and 'amazon' in merchant_info.lower()) or (seller_info is not None and 'amazon' in seller_info.lower()) else False
  result['is_amazon'] = is_amazon
  
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
