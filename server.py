import sys
import zmq
from datetime import datetime, timedelta
from constants import TrainStatus as tc
import configuration
from simulator import Simulator
import configparser
import multiprocessing as mp
from time import sleep

class TrainServer():
    ''' class for servers. Server should be triggered for each zone '''

    def __init__(self, zone, host, port, mode='S'):
        # General parameters
        self.mode = mode
        self.status_dict = {}
        self.zone = zone
        self.lastupdate = datetime.now()

        # Technical setting (communication)
        self.context = zmq.Context()
        self.host = host
        self.port = port
        self.server = self.context.socket(zmq.REP)

    def run_server(self):
        response = {}
        try:
            print('Server started at %s .... Ctrl+C to exit' % datetime.now())
            self.server.bind("tcp://%s:%s" % (self.host, self.port))
        except:
            print('Server error occurred at %s' % datetime.now())

        while True:
            message = self.server.recv_pyobj()
            # Standard format
            # {'train_number': train_number, 'contents':{contents}, 'msgtype':msg_type}
            train_number = message.get('train_number')
            contents = message.get('contents')
            msg_type = message.get('msgtype')
            # Exceptional case for getting snapshot
            if msg_type == tc.msgSNAP:
                train_number = 'dummy'
                contents = {'dummy':'dummy'}
            # Conditions for each message type
            if train_number and contents and msg_type:
                print('Got message from %s at %s' % (message['train_number'], datetime.now()))
                # Dispatching for process add conditions here in case new msgtype is added
                if msg_type == tc.msgAPPR:
                    contents = self.send_approval(train_number, contents)
                elif msg_type == tc.msgSREP:
                    contents = self.update_status(train_number, contents)
                elif msg_type == tc.msgEND:
                    contents = self.end_service(train_number, contents)
                elif msg_type == tc.msgSNAP:
                    contents = self.provide_status()
                else:
                    print('Invalid msgtype: %s' % message['msgtype'])
            else:   #message has invalid format
                print('Received message has wrong format(train_number, contents, msgtype): %s %s %s at %s'
                      % (train_number, contents, msg_type, datetime.now()))

            response['train_number'] = train_number
            response['contents'] = contents
            response['msgtype'] = msg_type
            #Any orders to client?
            #response['order'] = ...
            self.server.send_pyobj(response)

    def update_status(self, train_number, curstatus):
        self.status_dict[train_number] = curstatus
        print('status_dict has %s entries' % len(self.status_dict))
        curstatus = {}
        curstatus['recvtime'] = datetime.now()
        return curstatus

    def provide_status(self):
        contents={}
        contents['status_table'] = True
        contents['recvtime']=datetime.now()
        return self.status_dict

    def send_approval(self, train_number, contents):
        # return approval and return schedule (to be implemented)
        # 1. Check with schedule table
        # 2. If found entry in the table and close enough to departure time --> Approve
        # 3. If not met the requirements --> contents['approval'] = False, contents['reject_reason'] = 'xxxx'
        contents = {}
        contents['approval'] = True
        contents['recvtime'] = datetime.now()
        return contents

    def end_service(self, train_number, contents):
        self.status_dict.pop(train_number)
        contents = {}
        # Expected contents ['service_ended']['recvtime']
        contents['service_ended'] = True
        contents['recvtime'] = datetime.now()
        return contents

if __name__ == '__main__':
    #sys.args[1]->zone name, sys.args[2]->mode
    param = sys.args[1:]
    if not param.lower() == 'r':
        param[1] = 'S'
    else:
        param[1] = param[1].upper()   # must be "R"
    zone = sys.args[1].upper()
    config = configuration.read_config()
    if param[1] == 'S':
        host = config['sim_server']['host']
        port = config['sim_server']['port']
    else:
        host = config['server']['host']
        port = config['server']['port']

    ts = TrainServer(zone, host, port)

    # load master data

    # start server
    ts.run_server()