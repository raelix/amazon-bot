def load_list_from_file(filepath):
  URLs=[]
  with open(filepath, 'r') as urllist:
      for url in urllist.readlines():
        URLs.append(url.rstrip("\n"))
  return URLs