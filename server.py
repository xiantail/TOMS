from xmlrpc.server import SimpleXMLRPCServer
from datetime import datetime, timedelta
import multiprocessing as mp
from time import sleep

class TrainServer():
    ''' class for servers. Server should be triggered for each zone '''

    def __init__(self, zone, host, port, interval):
        self.status_dict = {}
        self.zone = zone
        self.host = (host, port)
        self.INTERVAL = interval
        self.lastupdate = datetime.now()

        self.server = SimpleXMLRPCServer((self.host))
        self.server.register_function(self.provide_status, "provide_status")
        self.server.register_function(self.update_status, "update_status")

    def start_server(self):
        try:
            print('Server starting.... Ctrl+C to exit')
            self.server.serve_forever()
        except KeyboardInterrupt:
            print('Server stopped at %s' % datetime.now())

    def update_status(self, curstatus):
        for train_number in curstatus.keys():
            self.status_dict[train_number] = curstatus[train_number]
            print('status_dict has %s entries' % len(self.status_dict))
        return datetime.now()

    def provide_status(self):
        return self.status_dict


if __name__ == '__main__':
    ts = TrainServer('S', 'localhost', 9877, 5)
    ts.start_server()