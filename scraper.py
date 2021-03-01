import requests 
import json 
from time import sleep
from bs4 import BeautifulSoup
from price_parser import parse_price
from tld import get_tld

def get_headers(locale='it'):
  if locale == 'fr':
    return {
      'Host': 'www.amazon.fr',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-GPC': '1',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache'
      }
  elif locale == 'es':
    return {
      'Host': 'www.amazon.es',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-GPC': '1',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache'
    }
  elif locale == 'de':
    return {
      'Host': 'www.amazon.de',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-GPC': '1',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache'
    }
  else:
    return {
      'Host': 'www.amazon.it',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-GPC': '1',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache'
    }

def scrape(url, callback, browser, need_to_wait, exit_flag): 
    locale = get_tld(url.strip())
    page = requests.get(url, headers=get_headers(locale))
    if page.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in page.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,page.status_code))
        return None
    result = parse(url, page)
    callback(result, browser, need_to_wait, exit_flag)
  

def parse(url, page):
  soup = BeautifulSoup(page.content, 'html.parser')
  result = dict()
  result['title'] = try_find(soup, 'span', {'id':'productTitle'})
  result['price'] = get_price(
                     try_find(soup, 'span', {'id':'newBuyBoxPrice'}) or 
                     try_find(soup, 'span', {'id':'price_inside_buybox'}) or 
                     try_find(soup, 'span', {'class':'offer-price'})
                     )

  result['is_new'] = (try_find(soup, 'span', {'id':'newBuyBoxPrice'}) or  
                      try_find(soup, 'span', {'id':'price_inside_buybox'})) is not None

  result['is_available'] = (try_find(soup, 'input', {'id':'add-to-cart-button-ubb'}) or 
                            try_find(soup, 'input', {'id':'add-to-cart-button'})) is not None

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
