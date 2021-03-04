import requests
from stem import Signal
from stem.control import Controller
import time
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

def get_tor_proxies(password='testit'):
    return {
        'http': 'socks5://user:{}@localhost:9050'.format(password),
        'https': 'socks5://user:{}@localhost:9050'.format(password)
    }


def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        old_ip = get_source_ip(get_tor_proxies())
        controller.authenticate(password='scrapeit')
        controller.signal(Signal.NEWNYM)
        seg = 0
        new_ip = get_source_ip(get_tor_proxies())
        if new_ip != None:
            while new_ip == old_ip:
                new_ip = get_source_ip(get_tor_proxies())
                time.sleep(1)
                seg += 1
                print ("Waiting to obtain new IP: %s Seconds" % seg) 
            return new_ip

def get_source_ip(proxy):
    try:
        session = requests.session()
        session.proxies = proxy
        source_ip = session.get("https://icanhazip.com/", timeout=3).text.strip()
        # print(source_ip)
        return source_ip
    except Exception as e:
        print("Cannot get remote IP")