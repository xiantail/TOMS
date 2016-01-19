from time import sleep
from datetime import datetime, timedelta

class TrainStatus():
    '''
    Define data exchange format with namedtuple and constants
    '''

    #Constants
    #msgtype for communication
    msgAPPR = 'Approval'
    msgSREP = 'Status Report'
    msgEND = 'End Service'
    msgSNAP = 'Get snapshot'

    #Train Status
    staPREP = 'Preparation'         #Not approved yet
    staDOOR = 'Door Open'           #Embarkation / disembarkation
    staCLSE = 'Door Closed'         #Ready for departure
    staDEPT = 'Departing Station'   #Accelarating
    staNORM = 'Normal Operation'    #Constant speed
    staARRV = 'Arriving at Station' #Decelarating
    staSTOP = 'Completely Stopped'  #Stop at station
    staPASS = 'Passing Station'     #Pass the station
    staWAIT = 'Waiting for Order'   #Stand by for restart
    staEMER = 'Emergent Stop'       #Stop due to emergency
    staOSTP = 'Ordered Stop'        #Stop ordered by Server
    staFINS = 'Service Finished'    #Finished operation
    strFWRD = 'Forwarding'          #Not in service

class Station():
    '''
    Station class
    '''
    def __init__(self, code, name, **kwargs):
        self.code = code
        self.name = name
        #other attributes to be added later stage...

class StationZone(Station):
    '''
    Zone specific Station class
    '''
    def __init__(self, code, name, zone, center_position, station_range):
        super().__init__(code, name)
        self.zone = zone
        self.center_position = center_position
        self.station_range = station_range   #tuple(0.000, 0.400)

class OccupationHandling():
    def __init__(self):
        self.occupied = None
        self.release_time = None
        self.wait_time = 90

    def request_to_occupy(self, train_number):
        if self.occupied:
            return False
        else:
            self.occupied = train_number
            return True

    def request_to_release(self, train_number):
        if self.occupied == train_number:
            self.occupied = None
            return True
        else:
            return False

class Lane(OccupationHandling):
    '''
    Lane master in stations
    '''
    def __init__(self, stationzone, lane, offset, restriction, lane_range):
        super().__init__()
        self.stationzone = [stationzone]  #StationZone list
        self.lane = lane
        self.offset = offset
        self.restriction = restriction
        self.lane_range = lane_range
        self.connection = []

class Track(OccupationHandling):
    '''
    Track master
    '''
    def __init__(self, zone, name, speed, type, restriction):
        super().__init__()
        self.zone = zone
        self.name = name
        self.speed = speed
        self.type = type    #Double tracks or Single track
        self.restriction = restriction
        self.occupied = None

class Garage():
    '''
    Garage master
    '''
    def __init__(self, name, lanes):
        self.name = name
        self.lanes = lanes      #number of lanes in the garage
        self.locked = False    #if locked no further operations allowed
        self.connection = []

    def add_connection(self, lane):
        self.connection.append(lane)

# Unit testing
if __name__ == '__main__':
    import copy
    zone = 'S'
    station_list = []
    oba = StationZone('OBA', 'Obama', zone, 0.0, (-0.140, 0.180))
    station_list.append(oba)
    nob = StationZone('NOB', 'Kita Obama', zone, 2.423, (-0.100, 0.180))
    station_list.append(nob)
    hns = StationZone('HNS', 'Hinata Shimmachi', zone, 5.679, (-0.100, 0.100))
    station_list.append(hns)
    srt = StationZone('SRT', 'Shirato', zone, 8.132, (-0.100, 0.100))
    station_list.append(srt)
    hoz = StationZone('HOZ', 'Hozawa', zone, 11.416, (-0.100, 0.100))
    station_list.append(hoz)
    tai = StationZone('TAI', 'Takatsu Airport', zone, 14.693, (-0.160, 0.120))
    station_list.append(tai)
    mtu = StationZone('MTU', 'Minami Takatsu', zone, 16.910, (-0.090, 0.090))
    station_list.append(mtu)
    yan = StationZone('YAN', 'Takatsu Yanaicho', zone, 19.431, (-0.090, 0.090))
    station_list.append(yan)
    tku = StationZone('TKU', 'Takatsu', zone, 21.600, (-0.180, 0.160))
    station_list.append(tku)
    kta = StationZone('KTA', 'Kita Takatsu', zone, 23.774, (-0.100, 0.100))
    station_list.append(kta)
    ire = StationZone('IRE', 'Hase Irie', zone, 25.823, (-0.100, 0.100))
    station_list.append(ire)
    hse = StationZone('HSE', 'Hasecho', zone, 28.049, (-0.100, 0.100))
    station_list.append(hse)
    hys = StationZone('HYS', 'Hayashidacho', zone, 30.548, (-0.120, 0.140))
    station_list.append(hys)
    gom = StationZone('GOM', 'Nakagomicho', zone, 33.200, (-0.100, 0.100))
    station_list.append(gom)
    hri = StationZone('HRI', 'Hirai', zone, 35.789, (-0.100, 0.100))
    station_list.append(hri)
    print(len(station_list))

    gra = Garage('Takatsu Garage', 20)

    lane_list = []
    track_list = []
    prev_station = None
    for station in station_list:
        lane1 = Lane(station, 'Lane1', 0.040, 'A', (-0.080, 0.080))
        lane2 = Lane(station, 'Lane2', -0.040, 'B', (-0.080, 0.080))
        if station.code == "TKU":   #connect to garage
            lane1.connection.append(gra)
            lane2.connection.append(gra)
        lane_list.append(lane1)
        lane_list.append(lane2)
        if prev_station:
            name = prev_station.code + '-' + station.code
            track = Track('S', name, 70.0, 'S', (prev_station.center_position, station.center_position))
            track_list.append(track)
        prev_station = station
    print(len(lane_list))

    garage_list = []
    garage_list.append(gra)

    for track in track_list:
        if track.name in ('TAI-MTU', 'MTU-YAN', 'YAN-TKU', 'TKU-KTA'):
            track.type = 'M'

    for track in track_list:
        print(track.name, track.type, track.restriction)

    for lane in lane_list:
        print(lane.stationzone[0].name, lane.lane, lane.connection)
