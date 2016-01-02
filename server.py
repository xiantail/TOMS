from xmlrpc.server import SimpleXMLRPCServer
from train_status import TrainStatus as ts
from datetime import datetime
from time import sleep

status_dict = {}

def update_status(**kwargs):
    train_number, status = kwargs
    status_dict[train_number] = status
    return datetime.now()

def display_status():
    for train_number, status in status_dict:
        print(train_number, status)


if __name__ == '__main__':
    server = SimpleXMLRPCServer(('localhost', 9877))
    server.register_function(update_status, "update_status")
    server.serve_forever()
    while True:
        sleep(5)
        display_status()
