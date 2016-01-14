import xmlrpc.client
from datetime import datetime
from time import sleep

class StatusDisplay():
    '''
    Display Status in Server side
    '''
    def __init__(self, host, port, interval=5):
        self.host = 'http://' + host + ':' + str(port) + '/'
        self.proxy = xmlrpc.client.ServerProxy(self.host)
        self.status_dict = {}
        self.INTERVAL = interval

    def get_status_dict(self):
        try:
            self.status_dict = self.proxy.provide_status()
        except:
            print("Communication error occurred")

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
    sd = StatusDisplay('localhost', 9877, 5)
    sd.process_cycle()
