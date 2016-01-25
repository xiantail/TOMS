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

    def assign_lane(self, lanes):
        for lane in lanes:
            if type(lane)=='':
                self.assigned_lane.append(lane)
                print('%s is assigned to station %s' % (lane.name, self.name))

    def get_absrange(self):
        range_low = self.station_range[0] + float(self.center_position)
        range_high = self.station_range[1] + float(self.center_position)
        return (range_low, range_high)


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
    'code', 'zone', 'name', 'priority', 'offset', 'lane_range', 'connection'
    '''
    def __init__(self, stationzone, name, offset, lane_range, connection):
        super().__init__()
        self.stationzone = [stationzone]  #StationZone list
        self.name = name
        self.offset = float(offset)
        self.lane_range = lane_range
        self.connection = connection

    def get_absrange(self):
        range_low = self.lane_range[0] + float(self.stationzone[0].center_position)
        range_high = self.lane_range[1] + float(self.stationzone[0].center_position)
        return (range_low, range_high)

    def get_absposition(self):
        return self.offset + float(self.stationzone[0].center_position)

class Track(OccupationHandling):
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
        self.occupied = None

    def get_absrange(self):
        return self.track_range

class Garage():
    '''
    Garage master
    '''
    def __init__(self, code, lanes):
        self.code = code
        self.lanes = lanes      #number of lanes in the garage
        self.locked = False    #if locked no further operations allowed
        self.connection = []
        self.availability = lanes

    def add_connection(self, lane):
        self.connection.append(lane)

'''
    def movein_garage(self):
        if self.availability > 0:
            self.locked = True
            self.availability -= 1
            print('Slot available')
            return True
        else:
            print('No available slot in the garage')
            return False

    def moveout_garage(self):
        if self.locked == False:
            self.locked = True
            self.availability += 1

    def lock_garage(self):
        self.locked = True

    def release_garage(self):
        self.locked = False
'''