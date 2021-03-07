import queue as Queue
from headers import get_headers
from tld import get_tld
import random, time, json, urllib3, requests, os
from scraper_factory import ScraperFactory

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
      
      if not ScraperFactory.get_scraper(task['provider']).is_valid(page):
        # print('Captcha %s' % page.status_code) 
        send_statistics(True, task, statistics)
        continue

      send_statistics(False, task, statistics)
      result = ScraperFactory.get_scraper(task['provider']).parse(page)

      print(json.dumps(result, indent=4, sort_keys=True))

      if ScraperFactory.get_scraper(task['provider']).verify_matching(result, task):
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
