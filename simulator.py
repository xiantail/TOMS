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
