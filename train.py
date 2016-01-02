from train_status import TrainStatus as ts
from datetime import datetime
from time import sleep

import xmlrpc.client

class Train():
    '''
    For instances of trains
    '''

    def __init__(self, train_number):
        self.proxy = xmlrpc.client.SeverProxy("http://localhost:9877/")
        self.train_number = train_number
        self.location = ()
        self.status = ''
        self.direction = ''
        self.speed = 0
        self.senttime = None
        self.recvtime = None
        self.curstatus = {}
        self.curstatusfull = None
        self.historydata = []

    def get_approval(self):
        pass

    def set_status(self):
        pass

    def send_status(self):
        sleep(1)
        self.senttime = datetime.now()
        # Prepare data for sending
        self.curstatus[self.train_number] = ts.trainstatus(location = self.location, status = self.status,
                                                           direction = self.direction, speed = self.speed,
                                                           senttime = self.senttime)
        # Send it!
        self.recvtime = self.proxy.update_status(self.curstatus)

        # Everything successful, store the data
        errstatus = 'OK'
        self.store_status(errstatus)

    def store_status(self, errstatus):
        # For historical data recording
        self.curstatusfull = ts.trainstatus_full(train_number = self.train_number, location = self.location,
                                                 status = self.status, direction = self.direction,
                                                 speed = self.speed, senttime = self.senttime,
                                                 recvtime = self.recvtime, recordtime = datetime.now())
        self.historydata.append(self.custatusfull)
        # Clear already stored data
        self.curstatusfull = None
        self.curstatus = {}
