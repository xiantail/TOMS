from datetime import datetime
from time import sleep
import zmq
from train_status import TrainStatus as tc

class StatusDisplay():
    '''
    Display Status in Server side
    '''
    def __init__(self, host, port, interval=5):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.client = self.context.socket(zmq.REQ)
        self.client.connect("tcp://%s:%s" % (self.host, self.port))
        self.INTERVAL = interval
        self.status_dict = {}

    def get_status_dict(self):
        message = {}
        message['train_number'] = 'dummy'
        message['contents'] = {'dummy':'dummy'}
        message['msgtype'] = tc.msgSNAP
        self.status_dict = {}
        try:
            self.client.send_pyobj(message)
            response = self.client.recv_pyobj()
        except:
            print("Communication error occurred")
        else:
            self.status_dict = response['contents']

    def display_status(self):
        for entry in self.status_dict:
            print(entry, self.status_dict[entry])

    def process_cycle(self):
        print("Ctrl+C to stop...")
        while True:
            self.get_status_dict()
            self.display_status()
            sleep(self.INTERVAL)

if __name__ == '__main__':
    #only for test purpose
    sd = StatusDisplay('127.0.0.1', 9877)
    sd.process_cycle()
