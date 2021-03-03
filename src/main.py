from bot import buy, init_browser, refresh_login
from scraper import scrape
import secrets
from amazon_domains import get_unique_domains
import json 
import time
import os
from multiprocessing import Queue, Process, Manager, Value

from threading import Thread
from threading import Event
from threading import Lock
from tor import renew_connection, get_source_ip, get_tor_proxies
import random

session_key='dontforgetme'

## Configuration

percentage=int(os.getenv('PERCENTAGE', 60))
use_tor=os.getenv('USE_TOR', 'true').lower() in ['true', '1']
isTest=os.getenv('IS_TEST', 'false').lower() in ['true', '1']
is_running_in_container=os.getenv('IS_CONTAINERIZED', 'true').lower() in ['true', '1']
limit_price=int(os.getenv('LIMIT_PRICE', secrets.limit_price))
email=os.getenv('AMAZON_EMAIL', secrets.email)
password=os.getenv('AMAZON_PASSWORD', secrets.password)


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
  URLs = load_list_from_file('data/urls.txt')
  proxies = load_list_from_file('data/proxies.txt')
  domains_to_login = get_unique_domains(URLs)
  login_to_amazon(domains_to_login, browser, email, password)
  loop_login = 0
  loop_before_login = 10000
  queue = Queue()
  urls_index = 0
  with Manager() as manager:

    need_to_wait = manager.Event()
    exit_flag = manager.Event()
    lock = manager.Lock()
    my_ip = str()
    error_counter = Value('i', 0)
    success_counter = Value('i', 0)
    loop_request = Value('i', 0)
    if use_tor:
      proxy = get_tor_proxies()
      my_ip = get_source_ip(proxy)
    else:
      proxy = get_new_proxy(proxies)
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

      process = Process(target=scrape, args=(queue, url, callback, lock, browser, need_to_wait, exit_flag, error_counter, success_counter, proxy, my_ip))
      process.start()
      loop_request.value = loop_request.value + 1
      while queue.qsize() > 100:
        print("Reached queue processes...waiting previous to complete")
        time.sleep(1)
      
      with lock:
        # print('error:%s, success:%s, queue:%s, total:%s' % (error_counter.value,success_counter.value,queue.qsize(),loop_request.value))
        if error_counter.value * 100 / loop_request.value > percentage:
          print('Percentage of failures: %s' % (error_counter.value * 100 / loop_request.value))
          if use_tor:
            my_ip = renew_connection()
          else:
            proxy = get_new_proxy(proxies)
            my_ip = get_source_ip(proxy)
          loop_request.value = queue.qsize()
          error_counter.value = 0
          success_counter.value = 0

      urls_index += 1
      

def get_new_proxy(proxies):
  selected_proxy = random.choice(proxies)
  proxies_dict = {}
  proxies_dict['https'] = selected_proxy
  return proxies_dict

if __name__ == "__main__":
  main()


