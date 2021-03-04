from bot import buy, init_browser, refresh_login, download_new_proxies
from scraper import scrape
import secrets
from amazon_domains import get_unique_domains
import json 
import time
import os
from multiprocessing import Queue, Process, Manager, Value
from threading import Thread, Event, Lock
from tor import renew_connection, get_source_ip, get_tor_proxies
import random
import uuid

session_key='dontforgetme'

## Configuration

percentage=int(os.getenv('PERCENTAGE', 85))
use_tor=os.getenv('USE_TOR', 'true').lower() in ['true', '1']
isTest=os.getenv('IS_TEST', 'false').lower() in ['true', '1']
is_running_in_container=os.getenv('IS_CONTAINERIZED', 'true').lower() in ['true', '1']
limit_price=int(os.getenv('LIMIT_PRICE', secrets.limit_price))
email=os.getenv('AMAZON_EMAIL', secrets.email)
password=os.getenv('AMAZON_PASSWORD', secrets.password)

proxy_list_path = 'data/http_proxies.txt'
url_list_path = 'data/urls.txt'

def callback(queue, result, browser, need_to_wait, exit_flag):
  if need_to_wait.is_set():
    queue.get()
    return
  print("")
  print(json.dumps(result, indent=4, sort_keys=True))
  if result['is_available']:
    price = result['price']
    print('Price is %s' % price)
    if price > limit_price:
      print('Price is too high, currently: %s euro.' % price)
      print('Limit: %s' % limit_price)
    else:
      print('Price is good %s!' % price)
      need_to_wait.set()
      was_a_success = buy(browser, result['url'], isTest)
      if was_a_success is True:
        exit_flag.set()
      need_to_wait.clear()
  queue.get()

def login_to_amazon(URLs, browser, email, password):
  for portal in URLs:
    refresh_login(browser, portal, email, password)

def load_list_from_file(filepath):
  URLs=[]
  with open(filepath, 'r') as urllist:
      for url in urllist.readlines():
        URLs.append(url.rstrip("\n"))
  return URLs

def main():
  print("Configuration:")
  print("  use TOR: %s" % use_tor)
  print("  is a test: %s" % isTest)
  print("  is containerized: %s" % is_running_in_container)
  print("  limit price: %s" % limit_price)
  print("  email: %s" % email)
  print("")
  if is_running_in_container:
    browser = init_browser(session_key, skip_display=True, visible=False)
  else:
    browser = init_browser(session_key, skip_display=False, visible=True)

  download_new_proxies(browser, proxy_list_path)
  URLs = load_list_from_file(url_list_path)
  proxy_list = load_list_from_file(proxy_list_path)

  domains_to_login = get_unique_domains(URLs)
  login_to_amazon(domains_to_login, browser, email, password)
  loop_login = 0
  loop_before_login = 10000
  urls_index = 0
  with Manager() as manager:

    my_ip = str()
    need_to_wait = manager.Event()
    exit_flag = manager.Event()
    lock = manager.Lock()
    queue = manager.Queue()
    proxy_index = manager.Value('i', 0)
    current_hash = get_unique_hash()
    counters = manager.dict()
    counters = init_structure(manager, counters, current_hash)
    if use_tor:
      proxy = get_tor_proxies()
      my_ip = get_source_ip(proxy)
    else:
      proxy_list, proxy = get_next_proxy(proxy_list, proxy_index, browser)
      my_ip = get_source_ip(proxy)
    while True:
      # Someone lock the iteraction, probably we found a good match
      while need_to_wait.is_set():
        time.sleep(3)
        print("Wait, probably I bought it...!")
      
      if exit_flag.is_set():
        exit(0)

      # Refresh login after $loop_before_login loops
      if loop_login < loop_before_login:
        loop_login +=1
      else:
        loop_login = 0
        login_to_amazon(domains_to_login, browser, email, password)

      if urls_index == len(URLs):
        urls_index = 0
      
      url = URLs[urls_index]

      queue.put(urls_index) 
      
      process = Process(target=scrape, args=(queue, url, callback, lock, browser, need_to_wait, exit_flag, counters, current_hash, proxy, my_ip))
      process.start()

      with lock:
        counters[current_hash]['total'] = counters[current_hash]['total'] + 1
        print('errors:%s, success:%s, total:%s - IP:%s' % (counters[current_hash]['errors'], counters[current_hash]['success'], counters[current_hash]['total'], my_ip))
        
        if counters[current_hash]['errors'] + counters[current_hash]['success'] > 100:
          percentage = counters[current_hash]['errors'] * 100 / (counters[current_hash]['errors'] + counters[current_hash]['success'] )
          if int(percentage) > 97:
            print('Percentage of failures: %s%%' % int(percentage))

            current_hash = get_unique_hash()

            if use_tor:
              proxy = get_tor_proxies(current_hash)
              my_ip = get_source_ip(proxy)
            else:
              proxy_list, proxy = get_next_proxy(proxy_list, proxy_index, browser)
              my_ip = get_source_ip(proxy)
            
          counters = init_structure(manager, counters, current_hash)
      
      while queue.qsize() > 100:
        print("Reached max queue length, waiting previous tasks to complete...")
        time.sleep(0.1)
      

      # with lock:
      #   if error_counter.value * 100 / loop_request.value > percentage:
      #     print('Percentage of failures: %s%%' % int((error_counter.value * 100 / loop_request.value)))
      #     if use_tor:
      #       my_ip = renew_connection()
      #     else:
      #       proxy_list, proxy = get_next_proxy(proxy_list, proxy_index, browser)
      #       my_ip = get_source_ip(proxy)
      #     loop_request.value = queue.qsize()
      #     error_counter.value = 0
      #     success_counter.value = 0

      urls_index += 1

def get_unique_hash():
  return uuid.uuid4().hex

def init_structure(manager, counters, current_hash):
    counters[current_hash] = manager.dict()
    counters[current_hash]['total'] = 0
    counters[current_hash]['success'] = 0
    counters[current_hash]['errors'] = 0
    return counters

def get_next_proxy(proxy_list, proxy_index, browser):
  if proxy_index.value == len(proxy_list):
    proxy_index.value = 0
    download_new_proxies(browser, proxy_list_path)
    proxy_list = load_list_from_file(proxy_list_path)
  selected_proxy = proxy_list[proxy_index.value]
  proxies_dict = {}
  proxies_dict['https'] = selected_proxy
  proxy_index.value = proxy_index.value + 1
  return proxy_list, proxies_dict

if __name__ == "__main__":
  main()


