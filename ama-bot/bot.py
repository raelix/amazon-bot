from selenium import webdriver
from pyvirtualdisplay import Display
from webdriver_manager.chrome import ChromeDriverManager
from re import sub
from decimal import Decimal
import re
import time
import threading 
import sys
import os
from tld import get_tld
import pathlib


def remove_file_if_exists(filename):
  if os.path.exists(filename):
    try:
      os.remove(filename)
    except Exception as e:
      print ("Error: %s." % e)
  else:  
    print("Sorry, I can not find %s file." % filename)

def download_new_proxies(browser, proxy_list_path):
  remove_file_if_exists(proxy_list_path)
  url = 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=1000&country=all&ssl=all&anonymity=all&simplified=true'
  browser.get(url)
  time.sleep(5)

def refresh_login(browser, portal, email, password):
  browser.get(portal)
  go_to_my_account(browser)
  go_to_my_orders(browser)
  type_email(browser, email)
  type_password(browser, password)
  # browser.save_screenshot('/data/login.png')

def go_to_my_account(browser):
  click_it(browser, "//a[@data-nav-role='signin']")

def go_to_my_orders(browser):
  click_it(browser, "//div[@data-card-identifier='YourOrders']")

def type_email(browser, email):
  write_input_and_submit(browser, "//input[@name='email']", email)

def type_password(browser, password):
  click_it(browser, "//input[@name='rememberMe']")
  write_input_and_submit(browser, "//input[@name='password']", password)

def click_it(browser, click):
  try:
    browser.find_element_by_xpath(click).click()
  except:
    pass

def write_input_and_submit(browser, input, key):
  try:
    input_element = browser.find_element_by_xpath(input)
    time.sleep(1)
    input_element.send_keys(key)
    time.sleep(1)
    input_element.submit()
    time.sleep(1)
  except:
    pass

def buy(browser, url, isTest=False):
  try:
    print('Trying on %s' % url)
    browser.get(url)
    tld_str = get_tld(url.strip())
    if tld_str == 'de':
      return try_to_buy_de(browser, isTest)
    if tld_str == 'fr' or tld_str == 'es':
      return try_to_buy_fr(browser, isTest)
    else:
      return try_to_buy(browser, isTest)
    # turbo-checkout-pyo-button
    # orderSummaryPrimaryActionBtn-announce
  except Exception as e:
    print(e)
    print('Buy not available for %s, go to the next one...' % url)

def try_to_buy_de(browser, isTest=False):
  try:
    print('Try buy now')
    browser.find_element_by_xpath("//input[@name='submit.buy-now']").click()
    skip_warranty(browser)
  except:
    try:
      print('Buy now not available, try add to cart')
      browser.find_element_by_xpath("//input[@name='submit.add-to-cart-ubb']").click()
      print('Added')
      skip_warranty(browser)
      print('Proceding to buy')
      browser.find_element_by_id('hlb-ptc-btn-native').click()
      browser.find_element_by_xpath("/html/body/div[5]/div[2]/div/div[1]/form/div/div[1]/div[2]/span/a").click()
      browser.find_element_by_xpath("/html/body/div[5]/div[1]/div/div[2]/div/div[1]/form/div[1]/div[2]/div/span[1]/span/input").click()
      browser.find_element_by_xpath("/html/body/div[5]/div[1]/div[2]/div[2]/div/div[2]/div[2]/form/div[2]/div/div/div/span/span/input").click()
      print('proceed successfully')
    except Exception as e:
      print(e)
      print("Can't proceed using cart as well")
      return
  try:
    print('buying...')
    if not isTest:
      try:
        browser.find_element_by_id('turbo-checkout-pyo-button').click()
      except:
        browser.find_element_by_xpath("//input[@name='placeYourOrder1']").click()
    print('bought!')
    time.sleep(3)
    return True
  except Exception as e:
    print(e)
    print('An error occurred while buying... :( ')


def try_to_buy_fr(browser, isTest=False):
  try:
    print('Try buy now')
    browser.find_element_by_xpath("//input[@name='submit.buy-now']").click()
    skip_warranty(browser)
  except:
    try:
      print('Buy now not available, try add to cart')
      browser.find_element_by_xpath("//input[@name='submit.add-to-cart']").click()
      print('Added')
      skip_warranty(browser)
      print('Proceding to buy')
      browser.find_element_by_id('hlb-ptc-btn-native').click()
      browser.find_element_by_class("a-button-input").click()
      print('proceed successfully')
    except Exception as e:
      print(e)
      print("Can't proceed using cart as well")
      return
  try:
    print('buying...')
    if not isTest:
      try:
        browser.find_element_by_id('turbo-checkout-pyo-button').click()
      except:
        browser.find_element_by_xpath("//input[@name='placeYourOrder1']").click()
    print('bought!')
    time.sleep(3)
    return True
  except Exception as e:
    print(e)
    print('An error occurred while buying... :( ')

def try_to_buy(browser, isTest=False):
  try:
    print('Try buy now')
    browser.find_element_by_xpath("//input[@name='submit.buy-now']").click()
    skip_warranty(browser)
  except:
    try:
      print('Buy now not available, try add to cart')
      browser.find_element_by_xpath("//input[@name='submit.add-to-cart-ubb']").click()
      print('Added')
      skip_warranty(browser)
      print('Proceding to buy')
      browser.find_element_by_id('hlb-ptc-btn-native').click()
      print('proceed successfully')
    except Exception as e:
      print(e)
      print("Can't proceed using cart as well")
      return
  try:
    print('buying...')
    if not isTest:
      try:
        browser.find_element_by_id('turbo-checkout-pyo-button').click()
      except:
        browser.find_element_by_xpath("//input[@name='placeYourOrder1']").click()
    print('bought!')
    time.sleep(3)
    return True
  except Exception as e:
    print(e)
    print('An error occurred while buying... :( ')

def skip_warranty(browser):
  try:
    browser.find_element_by_id('siNoCoverage').click()
  except:
    print('warranty has not been asked')  
  try:
    time.sleep(1)
    browser.find_element_by_id('siNoCoverage-announce').click()
    time.sleep(1)
  except:
    print('warranty has not been asked')  

def get_price(browser):
  try:
    return browser.find_element_by_id('price_inside_buybox').text
  except Exception as e:
    # print(e)
    print('product is from warehouse')
  try:
    return browser.find_element_by_class_name('offer-price').text
  except Exception as e:
    # print(e)
    print('Cant get price for warehouse as well')
  return None

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

