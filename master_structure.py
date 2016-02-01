# master data structure classes
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
        self.center_position = float(center_position)
        self.station_range = station_range   #tuple(0.000, 0.400)
        self.assigned_lane = []
        self.assigned_garage = []

    def assign_lane(self, lanes):
        for lane in lanes:
            if isinstance(lane, Lane):
                self.assigned_lane.append(lane)
                print('%s is assigned to station %s' % (lane.name, self.name))

    def get_absrange(self):
        range_low = self.station_range[0] + float(self.center_position)
        range_high = self.station_range[1] + float(self.center_position)
        return (range_low, range_high)


class OccupancyHandling():
    def __init__(self):
        self.occupied =[]
        self.booked = []

    def request_to_occupy(self, train):
        # Basically FIFO style unless no problems found
        if not (self.occupied and self.booked):
            self.occupied.append(train)
            print('Approval for Occupancy to train %s' % train.train_number)
            return 0
        elif not self.occupied and self.booked:
            self.occupied.append(self.booked.pop(0))
            self.booked.append(train)
            print('Request by %s is in waiting queue: Position %s' % (train.train_number, len(self.booked)))
            return len(self.booked)
        elif self.occupied:
            self.booked.append(train)
            print('Request by %s is in waiting queue: Position %s' % (train.train_number, len(self.booked)))
            return len(self.booked)

    def request_to_release(self, train):
        if not self.occupied:
            print('%s is not in the position to send release request' % train.train_number)
            return False
        elif train in self.occupied[0]:
            self.occupied.pop(0)
            print('Occupancy of %s is released' % train.train_number)
            return True
        else:
            print('%s is not in the position to send release request' % train.train_number)
            return False

class Lane(OccupancyHandling):
    '''
    Lane master in stations
    'code', 'zone', 'name', 'priority', 'offset', 'lane_range', 'connection'
    '''
    def __init__(self, stationzone, name, offset, lane_range, connection):
        super().__init__()
        self.stationzone = [stationzone]  #StationZone list
        self.name = name
        self.offset = float(offset)
        self.lane_range = lane_range
        self.connection = connection
        self.occupied = []
        self.booked = []

    def get_absrange(self):
        range_low = self.lane_range[0] + float(self.stationzone[0].center_position)
        range_high = self.lane_range[1] + float(self.stationzone[0].center_position)
        return (range_low, range_high)

    def get_absposition(self):
        return self.offset + float(self.stationzone[0].center_position)

class Track(OccupancyHandling):
    '''
    Track master
    'name', 'zone', 'speed', 'category', 'track_range'
    '''
    def __init__(self, name, zone, speed, category, track_range):
        super().__init__()
        self.zone = zone
        self.name = name
        self.speed = speed
        self.category = category    #Double tracks or Single track
        self.track_range = track_range
        self.occupied = []
        self.booked = []

    def get_absrange(self):
        return self.track_range

class Garage():
    '''
    Garage master
    -----
    Basic rules:
    Garage must be connected to station lanes directly. No train number required to park in garage or move between
    station lane and garage. Only unit set information is necessary. If train needs to be forwarded from station to
    another station, train number is required.
    '''
    def __init__(self, code, lanes):
        self.code = code
        self.lanes = lanes      #number of lanes in the garage
        self.occupied = []
        self.unitsets = []
        self.booked = []
        self.connection = []
        self.assigned_slots = []

    def add_connection(self, lane):
        self.connection.append(lane)

    def load_unitset(self, unitset):
        if self.lanes - len(self.unitsets) > 0:
            print('Unit set %s loaded' % unitset.unitsetid)
            self.unitsets.append(unitset)
            return True
        else:
            print('No open slot for Unit Set %s' % unitset.unitsetid)
            return False

    def movein_garage(self, unitset):
        # 1. Unit Set in the connected lane?
        found = False
        for lane in self.connection:
            if lane.occupied == unitset:    #OK
                found = True
                break
        if found == False:
            print('Unit Set %s is not located in connected lane' % unitset.unitsetid)
            return False

        # 2. Any available slots in the garage?
        if self.lanes - len(self.unitsets) <= 0:
            print('No available slots for %s in the garage', unitset.unitsetid)
            return False

        # 3. Any other operations ongoing?
        if self.occupied:
            print('Other operation is ongoing')
            return False

        # 4. Everything fine -> return True
        return True

    def moveout_garage(self, target_unitset, target_lane):
        # 1. Unit Set in the garage?
        found = False
        for unitset in self.unitsets:
            if unitset == target_unitset:
                found = True
                break
        if found == False:
            print('Unit Set %s is not located in the garage' % target_unitset.unitsetid)
            return False

        # 2. Target station lane is available?
        if target_lane.occupied:
            print('Target Station lane is not available')
            return False

        # 3. Any other operations ongoing?
        if self.occupied:
            print('Other operation is ongoing')
            return False

        # 4. Everything fine -> return True
        return True
