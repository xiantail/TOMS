# This file will be renamed like "constants.py"
class TrainStatus():
    '''
    Define data exchange format with namedtuple and constants
    '''

    #Constants
    #msgtype for header level
    msgSREP = 'Status Report'
    msgSETT = 'Set server time'  #Only for simulation purpose
    msgSNAP = 'Get snapshot'

    #msgtype as request level
    msgAPPR = 'Approval'    # for new train number
    msgEND = 'End Service' # At the end of service with train number
    msgINIT = 'Initialize Unit set' # synchronize with server info
    msgMVOR = 'Request: Move-out from garage'
    msgMVIR = 'Request: Move-in to garage'
    msgNEXT = 'Request to move next station'
    msgSIM = 'Request to operate as simulation mode'
    msgREL = 'Request to release AFO'

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

    #Unit set status
    stuMVOT = 'Move-out'
    stuMVIN = 'Move-in'
    stuWAIT = 'Waiting'
    stuARRV = 'Arrived'
    stuACTV = 'Active'
    stuDEAC = 'Deactivated'
    stuOFF = 'Turned off'
    stuLAUN = 'Launching'
    stuASGN = 'Train number assigned'