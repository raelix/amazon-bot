from bot_interface import BotInterface
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
import pathlib

class BotAmazon(BotInterface):

  def login(self, browser, portal, username, password):
    browser.get(portal)
    self.go_to_my_account(browser)
    self.go_to_my_orders(browser)
    self.type_email(browser, username)
    self.type_password(browser, password)

  def buy(self, browser, url, isTest):
    try:
      print('Trying on %s' % url)
      browser.get(url)
      return self.try_to_buy(browser, isTest)
      # turbo-checkout-pyo-button
      # orderSummaryPrimaryActionBtn-announce
    except Exception as e:
      print(e)
      print('Buy not available for %s, go to the next one...' % url)

  def try_to_buy(self, browser, isTest=False):
    try:
      print('Try buy now')
      browser.find_element_by_xpath("//input[@name='submit.buy-now']").click()
      self.skip_warranty(browser)
    except:
      try:
        print('Buy now not available, try add to cart')
        browser.find_element_by_xpath("//input[@name='submit.add-to-cart-ubb']").click()
        print('Added')
        self.skip_warranty(browser)
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

  def skip_warranty(self, browser):
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
    
  def go_to_my_account(self, browser):
    self.click_it(browser, "//a[@data-nav-role='signin']")

  def go_to_my_orders(self, browser):
    self.click_it(browser, "//div[@data-card-identifier='YourOrders']")

  def type_email(self, browser, email):
    self.write_input_and_submit(browser, "//input[@name='email']", email)

  def type_password(self, browser, password):
    self.click_it(browser, "//input[@name='rememberMe']")
    self.write_input_and_submit(browser, "//input[@name='password']", password)

  def click_it(self, browser, click):
    try:
      browser.find_element_by_xpath(click).click()
    except:
      pass

  def write_input_and_submit(self, browser, input, key):
    try:
      input_element = browser.find_element_by_xpath(input)
      time.sleep(1)
      input_element.send_keys(key)
      time.sleep(1)
      input_element.submit()
      time.sleep(1)
    except:
      pass
