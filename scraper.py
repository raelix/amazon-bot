import requests 
import json 
from time import sleep
from bs4 import BeautifulSoup
from price_parser import parse_price

def get_headers():
  return {
        'authority': 'www.amazon.it',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'it-IT,en;q=0.5',
    }

def scrape(url, callback, browser, need_to_wait, exit_flag):    
    page = requests.get(url, headers=get_headers())
    if page.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    result = parse(url, page)
    callback(result, browser, need_to_wait, exit_flag)
  

def parse(url, page):
  soup = BeautifulSoup(page.content, 'html.parser')
  result = dict()
  result['title'] = try_find(soup, 'span', {'id':'productTitle'})
  result['price'] = get_price( \
                     try_find(soup, 'span', {'id':'newBuyBoxPrice'}) or \
                     try_find(soup, 'span', {'id':'price_inside_buybox'}) or \
                     try_find(soup, 'span', {'class':'offer-price'})
                     )

  result['is_new'] = try_find(soup, 'span', {'id':'newBuyBoxPrice'}) is not None
  result['is_available'] = try_find(soup, 'input', {'id':'add-to-cart-button-ubb'}) is not None
  result['buy_now_available'] = try_find(soup,'span',{'id':'submit.buy-now-announce'}) is not None
  result['url'] = url
  return result

def get_price(price):
  try:
    return parse_price(price).amount_float
  except Exception as e:
    print("Error parsing price")
    

def try_find(soup, element, object, to_text=True, strip=True):
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
