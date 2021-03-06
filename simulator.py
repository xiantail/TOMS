from datetime import datetime, timedelta
from time import sleep
import math
import configuration
from train_cars import UnitSet
from train_cars import CarUnit
from constants import TrainStatus as tc
from datetime import date, datetime
import message_types as mt
import zmq
import csv

class Simulator():
    '''
    Sample data can be generated with function create_sample_csv in constants.py
    '''

    # master data / train cars
    unitset_dict = {}
    unitset_list = []
    carunit_dict = {}
    carunit_list = []

    # constants
    MIN_PREP = timedelta(seconds=240)
    MIN_STOP = timedelta(seconds=30)
    MIN_PCHANGE = timedelta(seconds=90)


    # date / time
    _virtual_datetime = datetime(year=date.today().year, month=date.today().month, day=date.today().day,
                                hour=4, minute=0, second=0)

    # Communication specific
    host = None
    port = None
    context = zmq.Context()
    client = context.socket(zmq.REQ)


    @classmethod
    def setup_communication(cls):
        config = configuration.read_config()
        print('Simulation mode')
        Simulator.host = config['sim_server']['host_sim']
        Simulator.port = config['sim_server']['port_sim']
        try:
            Simulator.client.connect("tcp://%s:%s" % (Simulator.host, Simulator.port))
        except:
            print('Connection to server failed at %s' % datetime.now())

    @classmethod
    def load_unitsets(cls):
        config = configuration.read_config()
        car_unit = config['datafile']['car_unit']
        unit_set = config['datafile']['unit_set']

        # read car unit information from csv file
        with open(car_unit, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cn = CarUnit(unitid=row['unitid'], cars=int(row['cars']), max_speed=float(row['max_speed']),
                             acceleration=float(row['acceleration']), deceleration=float(row['deceleration']),
                                                emergency_factor=float(row['emergency_factor']))
                Simulator.carunit_list.append(cn)
                Simulator.carunit_dict[cn.unitid] = cn

        # read unit set information from csv file
        with open(unit_set, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # convert str to list for assigned units
                lrange = row['assigned_unit'].strip("[']").split("', '")
                assigned_unit = list([Simulator.carunit_dict[x] for x in lrange])
                us = UnitSet(unitsetid=row['unitsetid'], location=str(row['location']), assigned_unit=assigned_unit)
                Simulator.unitset_list.append(us)
                Simulator.unitset_dict[us.unitsetid] = us

    @classmethod
    def set_virtualtime(cls, virtualtime):
        Simulator._virtual_datetime = virtualtime

    @classmethod
    def set_servertime(cls):
        servertime = str(Simulator._virtual_datetime)
        message = {}
        message['msgtype'] = tc.msgSETT
        message['contents'] = {'servertime':servertime}
        Simulator.client.send_pyobj(message)
        response = Simulator.client.recv_pyobj()
        return response

    @classmethod
    def move_forward_seconds(cls, delta=1):
        Simulator._virtual_datetime += timedelta(seconds=delta)
        response = Simulator.set_servertime()
        return response

    @classmethod
    def move_garage_to_lane(cls, unitset, target_lane):
        request = mt.create_request(tc.msgMVOR, unitset=unitset.unitsetid, location=unitset.location,
                                    target=target_lane)
        message = mt.create_status_message(unitset=unitset.unitsetid, request=request, unitset_status=tc.stuWAIT)
        Simulator.client.send_pyobj(message)
        response = Simulator.client.recv_pyobj()
        return response

    @classmethod
    def moving_into_lane(cls, unitset):
        request = None  #Not necessary until arrive at the station lane
        message = mt.create_status_message(unitset=unitset.unitsetid, request=request, unitset_status=tc.stuMVOT)
        Simulator.client.send_pyobj(message)
        response = Simulator.client.recv_pyobj()
        return response

    @classmethod
    def arrived_at_lane(cls, unitset, lane):
        request = {'reqtype':tc.msgREL, 'target':lane}
        message = mt.create_status_message(unitset=unitset.unitsetid, request=request, unitset_status=tc.stuARRV)
        Simulator.client.send_pyobj(message)
        response = Simulator.client.recv_pyobj()
        return response

    @classmethod
    def move_lane_to_garage(cls, unitset, target_slot=None):
        message = {}
        message['msgtype'] = tc.msgMVIR
        message['contents'] = {'unitset':unitset.unitsetid, 'location':unitset.location, 'target':target_slot}
        Simulator.client.send_pyobj(message)
        response = Simulator.client.recv_pyobj()
        return response

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
