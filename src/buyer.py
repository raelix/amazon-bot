import os, time
import queue as Queue
from selenium import webdriver
from pyvirtualdisplay import Display
from webdriver_manager.chrome import ChromeDriverManager
import pathlib
from bot_factory import BotFactory

is_running_in_container=os.getenv('IS_CONTAINERIZED', 'false').lower() in ['true', '1']
isTest=os.getenv('IS_TEST', 'true').lower() in ['true', '1']
wait_before_login=int(os.getenv('WAIT_BEFORE_LOGIN', '1800'))

session_key='chrome-session'

def buyer_task(configuration, availability, terminator):
  if is_running_in_container:
    browser = init_browser(session_key, skip_display=True, visible=False)
  else:
    browser = init_browser(session_key, skip_display=False, visible=True)
  providers = populate_providers(configuration)
  login_all(browser, providers)
  while True:
    try: 
      task = availability.get(True, wait_before_login)
      success = providers[task['buyer']]['instance'].buy(browser, task['url'], isTest)
      if success:
        time.sleep(5)
        terminator.put('END')
        exit(0)
    except Queue.Empty:
      print('buyer: waiting message to buy :) let me verify the login in the meantime')
      login_all(browser, providers)
    except KeyboardInterrupt:
      print('Interrupted by keyboard')
      return 

def populate_providers(configuration):
  providers = {}
  for scraper in configuration['scrapers']:
    providers[scraper['buyer']] = {}
    providers[scraper['buyer']]['instance'] = BotFactory().get_bot(scraper['buyer'])
    providers[scraper['buyer']]['username'] = scraper['username']
    providers[scraper['buyer']]['password'] = scraper['password']
    providers[scraper['buyer']]['portal'] = scraper['portal']
  return providers
    
def login_all(browser, providers):
  for provider in providers:
    providers[provider]['instance'].login(browser, providers[provider]['portal'], providers[provider]['username'], providers[provider]['password'])

def init_browser(session_key, skip_display=False, visible=False):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir=." + session_key)
    prefs = {"download.default_directory" : pathlib.Path().absolute().as_posix() + '/data'}
    chrome_options.add_experimental_option("prefs",prefs)
    if skip_display:
      display = Display(visible=0 if not visible else 1, size=(1024, 768))
      display.start()
      print('Initialized virtual display..')
      chrome_options.add_argument('--no-sandbox')
      chrome_options.add_argument("start-maximized")
      chrome_options.add_experimental_option('prefs', {'download.default_directory': os.getcwd(), 'download.prompt_for_download': False})
      browser = webdriver.Chrome(options=chrome_options)
    else:
      browser  = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    return browser