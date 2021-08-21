from scraper_interface import ScraperInterface
import requests
from bs4 import BeautifulSoup
from price_parser import parse_price

class ScraperAmazon(ScraperInterface):

  def __init__(self):
    pass

  def is_valid(self, page):
    return 'images-amazon.com/captcha' not in page.content.decode()

  def verify_matching(self, result, task):
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

  def parse(self, page):
    soup = BeautifulSoup(page.content, 'html.parser')
    result = dict()
    result['title'] = self.try_find(soup, 'span', {'id':'productTitle'})
    result['price'] = self.get_price(
                      self.try_find(soup, 'span', {'id':'newBuyBoxPrice'}) or 
                      self.try_find(soup, 'span', {'id':'price_inside_buybox'}) or 
                      self.try_find(soup, 'span', {'class':'offer-price'})
                      )

    result['is_new'] = (self.try_find(soup, 'span', {'id':'newBuyBoxPrice'}) or  
                        self.try_find(soup, 'span', {'id':'price_inside_buybox'})) is not None

    result['is_available'] = (self.try_find(soup, 'input', {'id':'add-to-cart-button-ubb'}) or 
                              self.try_find(soup, 'input', {'id':'add-to-cart-button'})) is not None

    result['buy_now_available'] = self.try_find(soup,'span',{'id':'submit.buy-now-announce'}) is not None
    merchant_info = self.try_find(soup,'div',{'id':'merchant-info'}) 
    seller_info = self.try_find(soup,'a',{'id':'sellerProfileTriggerId'}) 
    is_amazon = True if (merchant_info is not None and 'amazon' in merchant_info.lower()) or (seller_info is not None and 'amazon' in seller_info.lower()) else False
    result['is_amazon'] = is_amazon
    
    return result

  def get_price(self, price):
    try:
      return parse_price(price).amount_float
    except Exception as e:
      print("Error parsing price")
      

  def try_find(self, soup, element, object, to_text=True, strip=True):
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