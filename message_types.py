'''
This file defines message types which are used for communication between server and client
'''
from datetime import datetime, timedelta
from constants import TrainStatus as tc

class StatusMessage:
    def __init__(self, train_number=None, unitset=None, zone=None, position=None, direction=None,
                 track=None, location=None, speed=None, train_status=None, unitset_status=None,
                 target=None, request=None, senttime=None):
        self.train_number = train_number
        self.unitset = unitset
        self.zone = zone
        self.position = position
        self.track = track      #A/B/S
        self.location = location    #Lane, garage, track ...
        self.direction = direction
        self.speed = speed
        self.train_status = train_status
        if train_status:
            self.unitset_status = tc.stuASGN
        else:
            self.unitset_status = unitset_status
        self.target = target        #Lane
        self.request = request  #Dict
        self.senttime = datetime.now()

class StatusResponse:
    def __init__(self, recvtime, order, result, reason, target, distance):
        self.recvtime = recvtime
        self.order = order  #Dict
        self.result = result
        self.reason = reason
        self.target = target        #Next station
        self.distance = distance    #Distance to next station

def create_status_message(status_message):
    message = {'msgtype':tc.msgSREP, 'contents':status_message}
    return message

def create_response_message(status_response):
    response = {'msgtype':tc.msgSREP, 'contents':status_response}
    return response

def create_request(req_type, **kwargs):
    request = {}
    request['reqtype'] = req_type
    request['request'] = kwargs
    return request
