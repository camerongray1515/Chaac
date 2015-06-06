import sys
import time
from  multiprocessing import Process, Queue

client_queues = {}

to_run = {
    'plugin1': ['client1', 'client2', 'client3'],
    'plugin2': ['client1', 'client4', 'client5'],
    'plugin3': ['client6'],
    'plugin4': ['client1', 'client2', 'client3', 'client4', 'client5'],
}

def worker(q, client):
    while not q.empty():
        plugin = q.get()
        print("Executing {0} on {1}".format(plugin, client))
        time.sleep(5)
        print("{0} ready".format(client))
    sys.exit(1)
  
def main():
    for plugin in to_run:
        for client in to_run[plugin]:
            execute(plugin, client)

def execute(plugin, client):
    if client not in client_queues:
        client_queues[client] = {
            'process': None,
            'queue': Queue()
        }

    client_queues[client]['queue'].put(plugin)

    if client_queues[client]['process'] == None or not client_queues[client]['process'].is_alive():
        print("spawning")
        client_queues[client]['process'] = Process(target=worker, args=(client_queues[client]['queue'], client))
        client_queues[client]['process'].start()

if __name__ == "__main__":
    main()
