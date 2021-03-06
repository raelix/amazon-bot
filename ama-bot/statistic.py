import queue as Queue

SAMPLES = 10
PERCENTAGE = 60

def statistic_task(statistics, status):
  main_map = {}
  while True:
    try:
      result = statistics.get(True, 1)
      # print(result)
      identifier = result['id']

      # Increase failure or success
      if result['failed']:
        increase_failure(main_map, identifier)
      else:
        increase_success(main_map, identifier)

      # If there are enough samples then check the failure percentage
      if total_samples(main_map, identifier) >= SAMPLES:

        if percentage_failures(main_map, identifier) > PERCENTAGE:
          # Too much failure let's ask to delete them
          print('Proxy ID:%s has %s%% of failures, asking to replace it.'% (identifier, percentage_failures(main_map, identifier)))
          status.put(delete_message(identifier))
          delete_item(main_map, identifier)

    except Queue.Empty:
      # print('statistic: waiting for a task.')
      pass
    except KeyboardInterrupt:
      print('Interrupted by keyboard')
      return 
    except Exception as e:
      print(e)

def create_item_structure(main_map, id):
  main_map[id] = {}
  main_map[id]['success'] = 0
  main_map[id]['failure'] = 0

def delete_item(main_map, id):
  del main_map[id]

def increase_failure(main_map, id):
  increase_counters(main_map, id, 'failure')

def increase_success(main_map, id):
  increase_counters(main_map, id, 'success')

def increase_counters(main_map, id, result_type):
  if id not in main_map:
    create_item_structure(main_map, id)
  if result_type == 'success':
    main_map[id]['success'] += 1
  if result_type == 'failure':
    main_map[id]['failure'] += 1

def total_samples(main_map, id):
  if id not in main_map:
    return 0
  else:
    return main_map[id]['success'] + main_map[id]['failure']

def percentage_failures(main_map, id):
  if id not in main_map:
    return None
  else:
    return main_map[id]['failure'] * 100 / total_samples(main_map, id)

def delete_message(id):
  return {
    'operation': 'delete',
    'id': id
  }