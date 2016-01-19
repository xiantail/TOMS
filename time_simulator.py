from datetime import datetime, timedelta
from time import sleep

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
