import itertools
from stem import process
import requests
from headers import get_headers
from stem import process
session = requests.session()

def receive(password):
    proxies = {
        'http': 'socks5://user:{}@localhost:9050'.format(password),
        'https': 'socks5://user:{}@localhost:9050'.format(password)
    }
    return session.get("https://www.amazon.it/dp/B08HM4V2DH", proxies=proxies, headers=get_headers())

with process.launch_tor_with_config({'ControlPort': '3421', 'SocksPort': '9050'}) as tor:
    print('== use 10 different circuits ==')
    for response in map(receive, range(10)):
        print('images-amazon.com/captcha'  in response.content.decode())
    print()

    print('== use 10 times same circuit (same password, same circuit) ==')
    for response in map(receive, itertools.repeat('secret', 10)):
        print(response)

    tor.terminate()