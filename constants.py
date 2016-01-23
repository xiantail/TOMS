# This file will be renamed like "constants.py"
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

