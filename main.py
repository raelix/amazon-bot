from bot import buy, init_browser, refresh_login
from scraper import scrape
from secrets import limit_price, email, password
from amazon_domains import get_unique_domains
import json 
import time
from threading import Thread
from threading import Event


session_key='dontforgetme'

isTest=True

need_to_wait = Event()
exit_flag = Event()

def main():
  browser = init_browser(session_key, skip_display=False, visible=True)
  URLs = get_scrape_URLs()
  domains_to_login = get_unique_domains(URLs)
  login_to_amazon(domains_to_login, browser, email, password)
  threads = []
  loop_time = 0
  loop_refresh = 100
  while True:

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
      single_thread = Thread(target=scrape, args=(url, callback, browser, need_to_wait, exit_flag))
      threads.append(single_thread)
    for thread in threads:
      thread.start()
      time.sleep(0.2)
    for thread in threads:
      thread.join()

    # Erase list
    threads = []
    time.sleep(1)

def callback(result, browser, need_to_wait, exit_flag):
  if need_to_wait.isSet():
    return
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
        URLs.append(url)
  return URLs


if __name__ == "__main__":
  main()