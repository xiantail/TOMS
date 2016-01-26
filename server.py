import sys
import zmq
from datetime import datetime, timedelta
from constants import TrainStatus as tc
import configuration
from simulator import Simulator
import csv

# Master data
from master_structure import StationZone as SZ
from master_structure import Track as TR
from master_structure import Garage as GR
from master_structure import Lane as LN
from train_cars import UnitSet

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

        self.servertime = datetime.now()
        if mode == 'S':
            self.servertime = datetime(year=datetime.now().year, month=datetime.now().month,
                                       day=datetime.now().day, hour=3, minute=0, second=0)

    def upload_master_data(self, station_list, station_zone, track_list, garage_list, lane_list, unit_set):
        # Step.1 load station name
        station_name_dict = {}
        with open(station_list, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # List is not required as this only be used to get name text
                Simulator.station_name_dict[row['code']] = row['name']

        # Step.2 load zone specific station data
        with open(station_zone, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['name'] = Simulator.station_name_dict[row['code']]
                #convert fake tuple (stored as str in csv) into real tuple for range
                lrange = row['station_range'].strip("()").split(", ")
                station_range = tuple([float(x) for x in lrange])
                #code, name, zone, center_position, station_range
                sz = SZ(code=row['code'], name=row['name'], zone=row['zone'],
                        center_position=row['center_position'], station_range=station_range)
                Simulator.station_dict[row['code']]=sz
                Simulator.station_list.append(sz)

        # Step.3 load tracks
        with open(track_list, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #convert str fake tuple into real tuple
                lrange = row['track_range'].strip("()").split(", ")
                track_range = tuple([float(x) for x in lrange])
                #name, zone, speed, category, track_range
                tr = TR(name=row['name'], zone=row['zone'], speed=row['speed'], category=row['category'],
                        track_range=track_range)
                Simulator.track_dict[row['name']]=tr
                Simulator.track_list.append(tr)

        # Step.4 load garages
        with open(garage_list, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #code, lanes
                gr = GR(code=row['code'], lanes=row['lanes'])
                Simulator.garage_dict[row['code']]=gr
                Simulator.garage_list.append(gr)

        # Step.5 load lanes
        with open(lane_list, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                connection = []
                #[stationzone], name, offset, lane_range, connection
                stationzone = Simulator.station_dict[row['code']]
                #Convert str to list otherwise sliced per character
                lclist = row['connection'].strip("[]'").split("', '")
                for elem in lclist:
                    if len(elem) == 4 and elem.startswith('G'): # garages
                        connection.append(Simulator.garage_dict[elem])
                    else:
                        connection.append(Simulator.track_dict[elem])
                # convert str fake tuple into real tuple
                lrange = row['lane_range'].strip("()").split(", ")
                lane_range = tuple([float(x) for x in lrange])
                ln = LN(stationzone=stationzone, name=row['name'], offset=row['offset'],
                        lane_range=lane_range, connection=connection)
                Simulator.station_dict[row['code']].assign_lane([ln])
                Simulator.lane_list.append(ln)

        # Step.6 load train unit set (cars)
        with open(unit_set, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                us = UnitSet(unitsetid=row['unitsetid'], cars=int(row['cars']), max_speed=float(row['max_speed']))
                Simulator.unitset_list.append(us)
                Simulator.unitset_dict[us.unitsetid] = us

    def set_servertime(self):
        pass

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
            # Obsolete:{'train_number': train_number, 'contents':{contents}, 'msgtype':msg_type}
            # New format{'target':{'train_number'|'unit_set': '6001S'|'20'}, 'contents':{.....}, 'msgtype':msg_type}
            # --- methods should be split into several blocks per msg_type, for example
            train_number = message.get('train_number')  #Obsolete
            target = message.get('target')
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
            response['target'] = target
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
    param = sys.argv[1:]
    print(param)
    if not param[1].lower() == 'r':
        param[1] = 'S'
    else:
        param[1] = param[1].upper()   # must be "R"
    zone = param[0].upper()
    print('Zone name: %s' % zone)
    print('Mode: %s' % param[1])
    config = configuration.read_config()
    if param[1] == 'S':
        print('Simulation mode')
        host = config['sim_server']['host_sim']
        port = config['sim_server']['port_sim']
    else:
        print('Realtime mode')
        host = config['server']['host']
        port = config['server']['port']

    ts = TrainServer(zone, host, port)

    # load master data
    ts.upload_master_data(station_list = config['datafile']['station_list'],
                          station_zone = config['datafile']['station_zone'],
                          garage_list = config['datafile']['garage_list'],
                          lane_list = config['datafile']['lane_list'],
                          track_list = config['datafile']['track_list'],
                          unit_set = config['datafile']['unit_set'])

    # start server
    ts.run_server()