from bot import buy, init_browser, refresh_login
from scraper import scrape
import secrets
from amazon_domains import get_unique_domains
import json 
import time
import os
from threading import Thread
from threading import Event
from threading import Lock
from tor import renew_connection
from ThreadSafeCounter import ThreadSafeCounter

session_key='dontforgetme'

## Configuration

use_tor=os.getenv('USE_TOR', 'true').lower() in ['true', '1']
isTest=os.getenv('IS_TEST', 'false').lower() in ['true', '1']
is_running_in_container=os.getenv('IS_CONTAINERIZED', 'true').lower() in ['true', '1']
limit_price=os.getenv('LIMIT_PRICE', secrets.limit_price)
email=os.getenv('AMAZON_EMAIL', secrets.email)
password=os.getenv('AMAZON_PASSWORD', secrets.password)


need_to_wait = Event()
exit_flag = Event()
lock = Lock()

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
  URLs = get_scrape_URLs()
  domains_to_login = get_unique_domains(URLs)
  login_to_amazon(domains_to_login, browser, email, password)
  threadSafeCounter = ThreadSafeCounter()
  threads = []
  loop_time = 0
  loop_refresh = 100
  while True:
    print("Start loop!")
    # Someone lock the iteraction, probably we found a good match
    while need_to_wait.isSet():
      time.sleep(3)
      print("Wait, probably I bought it...!")
    
    if exit_flag.is_set():
      exit(0)

    # Refresh login after $loop_refresh loops
    if loop_time < loop_refresh:
      loop_time +=1
    else:
      loop_time = 0
      login_to_amazon(domains_to_login, browser, email, password)

    # Spawn one thread for each request trying to speed up the results
    for url in URLs:
      single_thread = Thread(target=scrape, args=(url, callback, lock, browser, use_tor, need_to_wait, exit_flag, threadSafeCounter))
      threads.append(single_thread)
    for thread in threads:
      thread.start()
      time.sleep(0.5)
    for thread in threads:
      thread.join()
    with lock:
      print('Failures: %s' % threadSafeCounter.get())
      if threadSafeCounter.get() > (len(threads) / 1.2):
        threadSafeCounter.reset()
        if use_tor:
          print('Renewal IP')
          renew_connection()
    # Erase list
    threads = []
    # time.sleep(0.5)

def callback(result, browser, need_to_wait, exit_flag):
  if need_to_wait.isSet():
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

def login_to_amazon(URLs, browser, email, password):
  for portal in URLs:
    refresh_login(browser, portal, email, password)

def get_scrape_URLs(file="urls.txt"):
  URLs=[]
  with open(file, 'r') as urllist:
      for url in urllist.readlines():
        URLs.append(url.rstrip("\n"))
  return URLs

if __name__ == "__main__":
  main()
  
