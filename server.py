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

        # master data / equipments
        self.station_name_dict = {}
        self.station_list = []
        self.station_dict = {}
        self.track_list = []
        self.track_dict = {}
        self.garage_list = []
        self.garage_dict = {}
        self.lane_list = []
        self.lane_dict = {}

        # Technical setting (communication)
        self.context = zmq.Context()
        self.host = host
        self.port = port
        self.server = self.context.socket(zmq.REP)

        self.servertime = datetime.now()
        if mode == 'S':
            self.servertime = datetime(year=datetime.now().year, month=datetime.now().month,
                                       day=datetime.now().day, hour=3, minute=0, second=0)

    def upload_master_data(self, station_list, station_zone, track_list, garage_list, lane_list):
        # Step.1 load station name
        station_name_dict = {}
        with open(station_list, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # List is not required as this only be used to get name text
                self.station_name_dict[row['code']] = row['name']

        # Step.2 load zone specific station data
        with open(station_zone, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['name'] = self.station_name_dict[row['code']]
                #convert fake tuple (stored as str in csv) into real tuple for range
                lrange = row['station_range'].strip("()").split(", ")
                station_range = tuple([float(x) for x in lrange])
                #code, name, zone, center_position, station_range
                sz = SZ(code=row['code'], name=row['name'], zone=row['zone'],
                        center_position=row['center_position'], station_range=station_range)
                self.station_dict[row['code']]=sz
                self.station_list.append(sz)

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
                self.track_dict[row['name']]=tr
                self.track_list.append(tr)

        # Step.4 load garages
        with open(garage_list, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #code, lanes
                gr = GR(code=row['code'], lanes=row['lanes'])
                self.garage_dict[row['code']]=gr
                self.garage_list.append(gr)

        # Step.5 load lanes
        with open(lane_list, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                connection = []
                #[stationzone], name, offset, lane_range, connection
                stationzone = self.station_dict[row['code']]
                #Convert str to list otherwise sliced per character
                lclist = row['connection'].strip("[]'").split("', '")
                for elem in lclist:
                    if len(elem) == 4 and elem.startswith('G'): # garages
                        connection.append(self.garage_dict[elem])
                    else:
                        connection.append(self.track_dict[elem])
                # convert str fake tuple into real tuple
                lrange = row['lane_range'].strip("()").split(", ")
                lane_range = tuple([float(x) for x in lrange])
                ln = LN(stationzone=stationzone, name=row['name'], offset=row['offset'],
                        lane_range=lane_range, connection=connection)
                self.station_dict[row['code']].assign_lane([ln])
                self.lane_list.append(ln)

        # Step.6 load train unit set (cars) --> to be removed this block as unit_set should be loaded in client side


    def run_server(self):
        response = {}
        try:
            print('Server started at %s .... Ctrl+C to exit' % datetime.now())
            self.server.bind("tcp://%s:%s" % (self.host, self.port))
        except:
            print('Server error occurred at %s' % datetime.now())

        while True:
            # Step 1. Get message and split into elements
            message = self.server.recv_pyobj()
            # Standard format
            # New format{'msgtype':msg_type, 'contents':{.....}}
            # Key - train_number or unitsetid should be in contents
            #train_number: message['contents'].get('train_number')
            #unitset_id: message['contents'].get('unitsetid')
            contents = message.get('contents')
            msg_type = message.get('msgtype')

            # Step 2. Dispatch the message to right option (method)
            # Step 2.1 Set server time for simulation mode
            if msg_type == tc.msgSETT:   #Set server time for simulation mode
                # Expected messsage: {'msgtype':'Set server time', 'contents':datetime()}
                contents = self.set_servertime(contents)
            # Step 2.2 Provide snapshot
            elif msg_type == tc.msgSNAP:
                contents = self.provide_status(contents)
            # Step 2.3 Initialize Unit Set in garage
            elif msg_type == tc.msgINIT:
                # Expected message {'msgtype':msgINIT, 'contents':{'unitsetid':xxxxx, 'destination': GTKU(garage)}
                contents = self.initialize_unit_set(contents)
            # Step 2.4 Move-out from garage to station lane
            elif msg_type == tc.msgMVOR:
                contents = self.handle_moveout_request(contents)
            # Step 2.5 Move-in from station lane to garage
            elif msg_type == tc.msgMVIR:
                contents = self.handle_movein_request(contents)
            # Step 2.5

            # Step 2.99 : Incorrect message type
            else:
                print('Incorrect message type: %s' % msg_type)
                contents['result'] = 'Incorrect message type'

            '''
            #---------------
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
            else:   #message has invalid format
                print('Received message has wrong format(train_number, contents, msgtype): %s %s %s at %s'
                      % (train_number, contents, msg_type, datetime.now()))
            '''

            response['contents'] = contents
            response['msgtype'] = msg_type
            self.server.send_pyobj(response)

    def set_servertime(self,contents):
        '''
        Expected message : {'msgtype':msgSETT, 'contents':{'server_time':'2016-01-27 11:24:25'}}
        '''
        try:
            newtime = contents.get('servertime')[:19]
            self.servertime = datetime.strptime(newtime,'%Y-%m-%d %H:%M:%S')
        except:
            contents['result'] = 'Time format error!'
        else:
            print('Server time is now set to %s' % self.servertime)
            contents['result'] = str(newtime)
        return contents

    def initialize_unit_set(self, contents):
        # Load an Unit set in the garage
        # Expected message {'msgtype':msgINIT, 'contents':{'unitsetid':xxxxx, 'destination': 'GTKU'(garage)}
        unitsetid = contents.get('unitsetid')
        if unitsetid:
            garage = self.garage_dict[contents.get('destination')]
            availability =  garage.lanes - len(garage.unitsets)
            if availability > 0:
                garage.unitsets.append(unitsetid)
                contents['result'] = True
                connected_lanes = []
                for lane in garage.connection:
                    connected_lanes.append(lane.name)
                contents['connection'] = connected_lanes
            else:
                contents['result'] = False
                contents['reason'] = 'All slots are occupied in garage'
        else:
            contents['result'] = False
            contents['reason'] = 'Unit Set is not specified in the message'
        if self.mode == 'S':
            contents['resptime'] = self.servertime
        else:
            contents['resptime'] = datetime.now()
        return contents

    def handle_moveout_request(self, contents):
        # Expected contents {'unitset', 'location', 'target'}
        unitset = contents.get('unitset')
        location = contents.get('location')
        target = contents.get('target')
        contents = {}

        #check availability of lane
        try:
            zstation = self.station_dict[location[1:]]
        except:
            contents['result'] = False
            contents['reason'] = 'Wrong location provided (zone specific station not found)'
            return contents

        lane_availability = False
        for lane in zstation.assigned_lane:
            if lane.name == target and lane.occupied == [] and lane.booked == []:
                lane_availability = True
        if lane_availability == False:
            contents['result'] = False
            contents['reason'] = 'Target lane is not available at this moment'
            contents['retry_after'] = self.servertime + timedelta(seconds=10)
            return contents

        #check availability of garage itself
        try:
            garage = self.garage_dict[location]
        except:
            contents['result'] = False
            contents['reason'] = 'Wrong location provided (garage not found)'
            return contents
        garage_availability = False
        if garage.occupied == [] and garage.booked == []:
            garage_availability = True
        else:
            contents['result'] = False
            contents['reason'] = 'Cannot outgoing from garage at this moment'
            contents['retry_after'] = self.servertime + timedelta(seconds=10)
            return contents

        # Provide AFO of lane and garage
        for lane in zstation.assigned_lane:
            if lane.name == target:
                lane.occupied = unitset
                break
        garage.occupied = unitset
        contents['result'] = True
        return contents

    def handle_movein_request(self, contents):
        # Expected contents {'unitsetid':unit set id, 'destination':(station lane)}
        pass


    def update_status(self, train_number, curstatus):
        self.status_dict[train_number] = curstatus
        print('status_dict has %s entries' % len(self.status_dict))
        curstatus = {}
        curstatus['recvtime'] = datetime.now()
        return curstatus

    def provide_status(self, contents):
        contents={}
        contents['status_table'] = True
        if self.mode == 'S':
            contents['recvtime'] = self.servertime
        else:
            contents['recvtime'] = datetime.now()
        contents['status_list'] = self.status_dict
        return contents

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
        if self.mode == 'S':
            contents['recvtime'] = self.servertime
        else:
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
                          track_list = config['datafile']['track_list'])

    # start server
    ts.run_server()