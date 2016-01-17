
class TrainStatus():
    '''
    Define data exchange format with namedtuple and constants
    '''

    #namedtuple
    from collections import namedtuple
    trainstatus = namedtuple("TrainStatus", "location status direction speed senttime")
    trainstatus_full = namedtuple("TrainStatusFull", "train_number errstatus location status direction speed senttime recvtime recordtime")

    #Constants
    #msgtype for communication
    msgAPPR = 'Approval'
    msgSREP = 'Status Report'
    msgEND = 'End Service'
    msgSNAP = 'Get snapshot'
