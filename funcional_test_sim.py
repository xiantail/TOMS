'''
Functional test for simulation mode
'''
import random
from simulator import Simulator as sim
from datetime import datetime, timedelta

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
    b301f = (sim.unitset_dict['B301F'], virtual_time)
    process_sets.append(b301f)
    b302f = (sim.unitset_dict['B302F'], virtual_time + timedelta(minutes=20))
    process_sets.append(b302f)
    b303f = (sim.unitset_dict['B303F'], virtual_time + timedelta(minutes=10))
    process_sets.append(b303f)
    b304f = (sim.unitset_dict['B304F'], virtual_time + timedelta(minutes=20))
    process_sets.append(b304f)
    b305f = (sim.unitset_dict['B305F'], virtual_time + timedelta(minutes=30))
    process_sets.append(b305f)
    b306f = (sim.unitset_dict['B306F'], virtual_time + timedelta(minutes=40))
    process_sets.append(b306f)

    while len(process_sets) > 0:
        for i, entry in enumerate(process_sets):
            del_ent = []
            if entry[1] >= virtual_time:
            #send status
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





