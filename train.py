from datetime import datetime
from time import sleep
import re
from train_status import TrainStatus as tc
import zmq

class Train():
    '''
    For instances of trains
    '''

    def __init__(self, train_number, host, port):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.client = self.context.socket(zmq.REQ)

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
        # Set date at this timing since operations might be beyond 24:00:00
        self.dep_date = datetime.now().strftime("%Y%m%d")
        # Take logs into local file every x records
        self.LOG_INTERVAL = 100

    def connect_to_server(self):
        try:
            self.client.connect("tcp://%s:%s" % (self.host, self.port))
        except:
            print('Connection to server failed at %s' % datetime.now())

    def get_approval(self, location, status, direction, senttime):
        self.location = location
        self.status = status    #Must be 'REQA'
        self.direction = direction
        self.senttime = senttime
        response = self.send_status(msg_type=tc.msgAPPR)
        if response['contents']['approval']:
            self.status = 'RDEP'
            print('Departure on schedule is approved for %s at %s' % (self.train_number, response['contents']['recvtime']))
        else:
            print('Not approved due to reason: %s' % response['contents']['reject_reason'])

    def set_status(self, location, status, speed, senttime):
        self.location = location
        self.status = status
        self.speed = speed
        self.senttime = senttime

    def send_status(self, msg_type=tc.msgSREP):
        self.senttime = datetime.now()
        # Prepare data for sending
        message = {}
        message['train_number'] = self.train_number
        message['msgtype'] = msg_type
        message['contents'] = self.curstatus[self.train_number] = {'location':self.location, 'status':self.status,
                                                                   'direction':self.direction, 'speed':self.speed,
                                                                   'senttime':self.senttime}
        # Send it!
        try:
            self.client.send_pyobj(message)
            response = self.client.recv_pyobj()
            self.recvtime = response['contents']['recvtime']
        except:
            errstatus = 'Error'
            print('Communcation error occured at %s %s' % (self.train_number, datetime.now()))
        else:
            errstatus = 'OK'
        self.store_status(errstatus)
        return response

    def store_status(self, errstatus):
        # For historical data recording
        self.curstatusfull = {'train_number': self.train_number, 'location': self.location,
                              'status': self.status, 'direction': self.direction,
                              'speed': self.speed, 'senttime': self.senttime, 'recvtime': self.recvtime,
                              'recordtime': datetime.now(), 'errstatus':errstatus}
        self.historydata.append(self.curstatusfull)
        if len(self.historydata) >= self.LOG_INTERVAL or self.status == 'FINS':
            self.save_locally(self.historydata)
            self.historydata = []
        # Clear already stored data
        self.curstatusfull = None
        self.curstatus = {}

    def save_locally(self, hist_data):
        import csv
        import threading

        def save_into_file():
            filename = str(self.train_number) + self.dep_date
            with open(filename, 'at') as logfile:
                fieldname = ['train_number', 'location', 'status', 'direction', 'speed', 'senttime', 'recvtime',
                             'recordtime', 'errstatus']
                log = csv.DictWriter(logfile, fieldnames=fieldname)
                log.writerows(hist_data)
            print('Log saved for %s at %s' % (self.train_number, datetime.now()))

        p = threading.Thread(target=save_into_file)
        p.start()
        # At the end of the service, wait log to save
        if self.status == 'FINS':
            p.join()

def train_client(train, host, port):
    '''
    Temporary version to test
    :param train_number: Train number to identify
    :param stops: How many stops to be tested
    :return:
    '''
    train_number, stops = train
    atrain = Train(train_number, host, port)
    atrain.connect_to_server()
    # Judge direction
    number = int(re.match(r'\d*', train_number).group())
    if number % 2 == 1:
        atrain.direction = 'O'  #Outbound / Outer circle
        location = ('S', 0.0, 'S')
    else:
        atrain.direction = 'I'  #Inbound / Inner circle
        location = ('S', 77.1, 'S')
    atrain.get_approval(location, 'REQA', atrain.direction, datetime.now())
    timer = 0
    station_count = 0
    while True:
        if atrain.direction == 'O':
            factor = 1
        else:
            factor = -1
        sleep(1)
        zone = atrain.location[0]
        point = atrain.location[1]
        cline = atrain.location[2]
        status = atrain.status
        speed = atrain.speed
        senttime = datetime.now()
        msg_type = None
        # Only for test, simple logic
        if atrain.status == 'RDEP':
            status = 'ACCL'
            speed = 0.0
        elif atrain.status == 'ACCL':
            orig_speed = speed
            speed += 3.0
            point = round((point + (orig_speed + speed) / 2 / 3600 * factor),3)
            if speed > 70.0:
                speed = 70.0
                status = 'CONS'
        elif atrain.status == 'CONS':
            timer += 1
            point = round((point + 70.0 / 3600 * factor), 3)
            if timer >= 60:
                status = 'DECL'
                timer = 0
        elif atrain.status == 'DECL':
            orig_speed = speed
            speed -= 3.0
            point = round((point + (orig_speed + speed) / 2 / 3600 * factor),3)
            if speed < 0.0:
                speed = 0.0
                status = 'STOP'
        elif atrain.status == 'STOP':
            timer += 1
            if station_count == stops:
                status = 'FINS'
                msg_type = tc.msgEND
            elif timer >= 30:
                status = 'ACCL'
                timer = 0
                station_count += 1

        location = (zone, point, cline)
        atrain.set_status(location, status, speed, senttime)
        if not msg_type:
            msg_type = tc.msgSREP
        atrain.send_status(msg_type)
        if status == 'FINS':
            break

    print('Operation %s is finished at %s.' % (atrain.train_number, datetime.now()))

if __name__ == '__main__':
    # For unit test
    atrain = Train('6001S', '127.0.0.1', 9877)
    location = ('S', 0.0, 'S')
    #connect to server
    atrain.connect_to_server()
    atrain.get_approval(location, 'REQA', 'O', datetime.now())
    atrain.LOG_INTERVAL = 10    #Default value is too long for unit test
    # Only for Unit test purpose
    timer = 0
    station_count = 0
    while True:
        sleep(1)
        zone = atrain.location[0]
        point = atrain.location[1]
        cline = atrain.location[2]
        status = atrain.status
        speed = atrain.speed
        senttime = datetime.now()
        # Only for test, simple logic
        if atrain.status == 'RDEP':
            status = 'ACCL'
            speed = 0.0
        elif atrain.status == 'ACCL':
            orig_speed = speed
            speed += 3.0
            point = round((point + (orig_speed + speed) / 2 / 3600),3)
            if speed > 70.0:
                speed = 70.0
                status = 'CONS'
        elif atrain.status == 'CONS':
            timer += 1
            point = round((point + 70.0 / 3600), 3)
            if timer >= 60:
                status = 'DECL'
                timer = 0
        elif atrain.status == 'DECL':
            orig_speed = speed
            speed -= 3.0
            point = round((point + (orig_speed + speed) / 2 / 3600),3)
            if speed < 0.0:
                speed = 0.0
                status = 'STOP'
        elif atrain.status == 'STOP':
            timer += 1
            if station_count == 2:
                status = 'FINS'
            elif timer >= 30:
                status = 'ACCL'
                timer = 0
                station_count += 1

        location = (zone, point, cline)
        atrain.set_status(location, status, speed, senttime)
        atrain.send_status()
        if status == 'FINS':
            break

    print('Operation %s is finished at %s.' % (atrain.train_number, datetime.now()))