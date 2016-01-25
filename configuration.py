import configparser

def read_config():
    config = configparser.ConfigParser()
    if not config.read('config.ini'):
        reset_config()
        config.read('config.ini')
    # Now file must be available
    return config

def reset_config():
    config = configparser.ConfigParser()
    config['server'] = {'host':'127.0.0.1',
                        'port':9877}
    config['sim_server'] ={'host_sim':'127.0.0.1',
                           'port_sim':9878}
    config['datafile'] = {'station_list':'station_list.py',
                              'station_zone':'station_zone.csv',
                              'track_list':'track_list.csv',
                              'garage_list':'garage_list.csv',
                              'lane_list': 'lane_list.csv',
                              'unit_set': 'unit_set.csv'}
    with open('config.ini', 'wt') as configfile:
        config.write(configfile)
