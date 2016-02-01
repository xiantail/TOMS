'''
Functional test for simulation mode
'''
import random
from simulator import Simulator as sim
from datetime import datetime, timedelta
from constants import TrainStatus as tc
import message_types as ms

opt_dest_OBA = ('TKU', 'HRI')
opt_dest_HRI = ('TKU', 'OBA')
opt_dest_TKU = ('OBA', 'HRI')
opt_continue = ('Garage', 'Continue', 'Continue', 'Continue')

if __name__ == '__main__':
    # Scenario :
    # B301F, B302F -> Start from GOBA at 6:00:00, 6:20:00
    # B303F, B304F, B305F, B306F -> start from GTKU at 6:10:00, 6:20:00, 6:30:00, 6:40:00
    # Destination to be deceided by random.choice / Idle time at station at least 00:04:00

    # Step 0: Start the server - separately started by server.py because of serve_forever()
    virtual_time = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
                            hour=6, minute=0, second=0)
    sim.set_virtualtime(virtual_time)
    sim.setup_communication()
    sim.set_servertime()

    # Step 1: Activate a UnitSet
    process_sets = []
    sim.load_unitsets()
    b301f = {'us':sim.unitset_dict['B301F'], 'start':virtual_time}
    process_sets.append(b301f)
    b302f = {'us':sim.unitset_dict['B302F'], 'start':virtual_time + timedelta(minutes=20)}
    process_sets.append(b302f)
    b303f = {'us':sim.unitset_dict['B303F'], 'start':virtual_time + timedelta(minutes=10)}
    process_sets.append(b303f)
    b304f = {'us':sim.unitset_dict['B304F'], 'start':virtual_time + timedelta(minutes=20)}
    process_sets.append(b304f)
    b305f = {'us':sim.unitset_dict['B305F'], 'start':virtual_time + timedelta(minutes=30)}
    process_sets.append(b305f)
    b306f = {'us':sim.unitset_dict['B306F'], 'start':virtual_time + timedelta(minutes=40)}
    process_sets.append(b306f)

    while len(process_sets) > 0:
        for i, entry in enumerate(process_sets):
            del_ent = []
            if entry.get('start') and entry['start'] >= virtual_time:

                entry['us'].mode = tc.stuACTV   #Active
                # request to move to lane
                if int(entry['us'].unitsetid[1:4]) % 2 == 1:
                    target = 'Lane1'
                else:
                    target = 'Lane2'
                # Move out from garage
                response = sim.move_garage_to_lane(unitset=entry['us'].unitsetid, target_lane=target)
                if response['contents']['result'] == True:
                    print('UnitSet %s is moving to %s' % (entry['us'].unitsetid, target))
                    entry.pop('start')
                    entry['us'].unitset_status = tc.stuMVOT
                    entry['move_end'] = virtual_time + timedelta(seconds=90)
                else:
                    print('UnitSet %s is rejected to move out, wait until %s' %
                          (entry['us'].unitsetid, response['contents']['retry_after']))
                    entry['start'] = response['contents']['retry_after']

            elif entry['move_end'] > virtual_time:
                response = sim.moving_into_lane(unitset=entry['us'].unitsetid)
            elif entry['move_end'] <= virtual_time:
                response = sim.arrived_at_lane(unitset=entry['us'].unitsetid, lane=None)

            #if....:
            #  del_ent.append(i)
        # move forward virtual time
        sim.move_forward_seconds(delta=1)
        virtual_time += timedelta(seconds=1)
        # Delete finished entry
        for elem in del_ent:
            process_sets.pop(elem)

    # Step 2 Move from garage to station lane (get dummy train number?)
    # Step 3: Get a new train number and departure time
    # Step 4:
    # Step 6:Update train diagram





