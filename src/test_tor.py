import itertools
from stem import process
import requests

session = requests.session()

def receive(password):
    proxies = {
        'http': 'socks5://user:{}@localhost:9050'.format(password),
        'https': 'socks5://user:{}@localhost:9050'.format(password)
    }
    return session.get("https://icanhazip.com/", proxies=proxies).text.strip()

print('== use 10 different circuits ==')
for response in map(receive, range(10)):
    print(response)
print()

print('== use 10 times same circuit (same password, same circuit) ==')
for response in map(receive, itertools.repeat('secret', 10)):
    print(response)

tor.terminate()