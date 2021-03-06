from proxy_tor import ProxyTor
from proxy_none import ProxyNone
class ProxyFactory:
  
  def get_proxy(self, proxy_type='tor'):
    if proxy_type == 'tor':
      proxy = ProxyTor()
    if proxy_type == 'empty':
      proxy = ProxyNone()
    return proxy
          
