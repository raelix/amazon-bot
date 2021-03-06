from bot import init_browser, refresh_login, buy
import os, time
import queue as Queue

is_running_in_container=os.getenv('IS_CONTAINERIZED', 'false').lower() in ['true', '1']
isTest=os.getenv('IS_TEST', 'true').lower() in ['true', '1']
email=os.getenv('AMAZON_EMAIL', 'raelix@hotmail.it')
password=os.getenv('AMAZON_PASSWORD', '!Enrico5252')
wait_before_login=int(os.getenv('WAIT_BEFORE_LOGIN', '1800'))
portal=os.getenv('PORTAL', 'https://www.amazon.it')

session_key='chrome-session'

def buyer_task(availability, terminator):
  if is_running_in_container:
    browser = init_browser(session_key, skip_display=True, visible=False)
  else:
    browser = init_browser(session_key, skip_display=False, visible=True)
  refresh_login(browser, portal, email, password)  
  while True:
    try: 
      task = availability.get(True, wait_before_login)
      success = buy(browser, task['url'], isTest)
      if success:
        time.sleep(5)
        terminator.put('END')
        exit(0)
    except Queue.Empty:
      print('buyer: waiting message to buy :) let me verify the login in the meantime')
      refresh_login(browser, portal, email, password)  
    except KeyboardInterrupt:
      print('Interrupted by keyboard')
      return 

