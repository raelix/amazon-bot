import requests 
from headers import get_headers
from price_parser import parse_price
from tld import get_tld

locale = get_tld('https://www.amazon.it/dp/B08HN4DSTC'.strip())
page = requests.get('https://www.amazon.it/dp/B08HN4DSTC', headers=get_headers(locale), timeout=10)

if page.status_code > 500:
    print('Status code 500 %s' % page.status_code) 
if 'images-amazon.com/captcha' in page.content.decode():
    print('Captcha %s' % page.status_code) 
print(page.content)