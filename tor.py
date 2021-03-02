import requests
from secrets import tor_secret
from stem import Signal
from stem.control import Controller
#https://stackoverflow.com/questions/30286293/make-requests-using-python-over-tor
# TORRC conf
#ControlPort 9051
## If you enable the controlport, be sure to enable one of these
## authentication methods, to prevent attackers from accessing it.
#HashedControlPassword 16:05834BCEDD478D1060F1D7E2CE98E9C13075E8D3061D702F63BCD674DE
#
# Please note that the HashedControlPassword above is for the password "password". 
# If you want to set a different password, replace the HashedControlPassword in the torrc 
# by noting the output from tor --hash-password "<new_password>" where <new_password> is 
# the password that you want to set.

def get_tor_proxies():
    return {"http": 'socks5://127.0.0.1:9050', "https": 'socks5://127.0.0.1:9050'}

def get_tor_session():
    session = requests.session()
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session

def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password=tor_secret)
        controller.signal(Signal.NEWNYM)
    session = get_tor_session()
    print(session.get("http://httpbin.org/ip").text)
    
# session = get_tor_session()
# print(session.get("http://httpbin.org/ip").text)