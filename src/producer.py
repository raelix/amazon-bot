import queue as Queue
from proxy_factory import ProxyFactory
import time
import os
import uuid

standaloneProxy=os.getenv('STANDALONE_PROXY', 'true').lower() in ['true', '1']
proxyType=os.getenv('PROXY_TYPE', 'tor').lower()

def producer_task(status, list_map, queue):
  
  proxy = ProxyFactory().get_proxy(proxyType)
  
  if standaloneProxy:
    proxy.start()

  # proxy_map = proxy.get_map()
  source_ip = proxy.get_source_ip()
  list_size = len(list_map)
  item_index = 0
  proxy_list = produce_unique_proxy_list(list_size, proxy)
  
  while True:

    try:
      # Check if there is new status published then 
      # need to remove this proxy because it's not working well
      try:
          data = status.get(False)  
          if data['operation'] == 'delete':
            element_index = get_id_index_from_list(proxy_list, data['id'])
            if element_index != None:
              replace_proxy_item_from_list(proxy_list, proxy, element_index)
            else:
              print("producer: ERROR - proxy element not found")
      except Queue.Empty:
        pass

      while queue.qsize() > list_size:
        # print('Queue reach max length, waiting consumers.')
        time.sleep(0.1)

      # reset after completed loop
      if item_index == list_size:
        item_index = 0
      
      element = get_dict(list_map[item_index], proxy_list[item_index], source_ip)

      queue.put(element)
      
      # increase index for next element
      item_index += 1

    except KeyboardInterrupt:
      print('Interrupted by keyboard')
      try:
        if standaloneProxy:
          proxy.stop()
      except Exception as e:
        print(e)
      return 

def get_dict(url_and_price, proxy_map, source_ip):
  result = {}
  result['url']         = url_and_price['url']
  result['limit_price'] = url_and_price['price']
  result['source_ip']   = source_ip
  result['proxy']       = proxy_map['proxy']
  result['id']          = proxy_map['id']
  return result

def get_id_index_from_list(proxy_list, id):
  for index, item in enumerate(proxy_list):
    if item['id'] == id:
      return index

def replace_proxy_item_from_list(proxy_list, proxy, index):
  del proxy_list[index]
  proxy_list.append(produce_unique_proxy(proxy))


def produce_unique_proxy_list(list_size, proxy):
  unique_list = []
  for index in range(list_size):
    unique_list.append(produce_unique_proxy(proxy))
  return unique_list

def produce_unique_proxy(proxy):
  maps = {}
  maps['id'] = uuid.uuid4()
  maps['proxy'] = proxy.get_unique_map(maps['id'])
  return maps