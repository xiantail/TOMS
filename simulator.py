from datetime import datetime, timedelta
from time import sleep
import math
from master_structure import *
from master_structure import StationZone as SZ
from master_structure import Track as TR
from master_structure import Garage as GR
from master_structure import Lane as LN

from train_cars import UnitSet

from datetime import date, datetime

import csv

class Simulator():
    '''
    Sample data can be generated with function create_sample_csv in constants.py
    '''
    # master data / equipments
    station_name_dict = {}
    station_list = []
    station_dict = {}
    track_list = []
    track_dict = {}
    garage_list = []
    garage_dict = {}
    lane_list = []
    lane_dict = {}

    # master data / train cars
    unitset_dict = {}
    unitset_list = []

    # date / time
    virtual_datetime = datetime(year=date.today().year, month=date.today().month, day=date.today().day,
                                hour=4, minute=0, second=0)

    @classmethod
    def load_data(cls):
        # Step.1 load station name
        station_name_dict = {}
        with open('station_list.csv', 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # List is not required as this only be used to get name text
                Simulator.station_name_dict[row['code']] = row['name']

        # Step.2 load zone specific station data
        with open('station_zone.csv', 'rt') as csvfile:
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
        with open('track_list.csv', 'rt') as csvfile:
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
        with open('garage_list.csv', 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #code, lanes
                gr = GR(code=row['code'], lanes=row['lanes'])
                Simulator.garage_dict[row['code']]=gr
                Simulator.garage_list.append(gr)

        # Step.5 load lanes
        with open('lane_list.csv', 'rt') as csvfile:
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
        with open('unit_set.csv', 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                us = UnitSet(unitsetid=row['unitsetid'], cars=int(row['cars']), max_speed=float(row['max_speed']))
                Simulator.unitset_list.append(us)
                Simulator.unitset_dict[us.unitsetid] = us


    @classmethod
    def calc_duration(cls, distance, speed=(0.0, 70.0, 0.0), acceleration=3.0, decceleration=3.0, rounding=10, debug=False):
        '''
        :param distance: distance between stations in Kilometer
        :param speed: (start speed, max speed, end speed)
        :param acceleration: km/h/sec
        :param decceleration: km/h/sec
        :param rounding: 10,15,30,60
        :return: duration time in seconds
        '''
        start_speed = speed[0]
        max_speed = speed[1]
        end_speed = speed[2]
        # time to reach max_speed in sec.
        ttrm = math.ceil((max_speed - start_speed) / acceleration)
        # distance to reach max_speed in km
        dtrm = round((max_speed - start_speed) / 2 * ttrm / 3600, 3)
        # time to reach end_speed in sec.
        ttre = math.ceil((max_speed - end_speed) / decceleration)
        # distance to reach end_speed in km
        dtre = round((max_speed - end_speed) / 2 * ttre / 3600, 3)
        # distance with max_speed
        dwms = distance - dtrm - dtre
        if debug:
            print('ttrm: %s' % ttrm)
            print('dtrm: %s' % dtrm)
            print('ttre: %s' % ttre)
            print('dtre: %s' % dtre)
            print('dwms: %s' % dwms)
        if dwms > 0:
            # time with max_speed
            twms = math.ceil(dwms / max_speed * 3600)
            if debug:
                print('twms: %s' % twms)
        else:   #distance is too short to reach max_speed
            print('Max speed is too high in this section')
            return 0
        # rounding
        if rounding not in (10, 15, 30, 60):
            rounding = 10
        duration = ttrm + twms + ttre
        duration += (rounding - duration % rounding)
        return duration


if __name__ == '__main__':
    # set basedate
    base_time = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
                         hour=0, minute=0, second=0)
    # fastest mode
    start_timestamp = datetime.now()
    for i in range(86400):
        simtime=base_time+timedelta(seconds=i)
        print(simtime, "\r", end="")
    end_timestamp = datetime.now()
    delta_timestamp = end_timestamp - start_timestamp
    print('Now it is %s, took %s for process' % (simtime, delta_timestamp))
