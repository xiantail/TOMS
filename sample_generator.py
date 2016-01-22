import csv

def create_sample_csv():
    '''
    Create sample csv files
    '''
    # Stations
    station_list = []
    station_list.append({'code':'OBA', 'name':'Obama'})
    station_list.append({'code':'NOB', 'name':'Kita Obama'})
    station_list.append({'code':'HNS', 'name':'Hinata Shimmachi'})
    station_list.append({'code':'SRT', 'name':'Shirato'})
    station_list.append({'code':'HOZ', 'name':'Hozawa'})
    station_list.append({'code':'TAI', 'name':'Takatsu Airport'})
    station_list.append({'code':'MTU', 'name':'Minami Takatsu'})
    station_list.append({'code':'YAN', 'name':'Takatsu Yanaicho'})
    station_list.append({'code':'TKU', 'name':'Takatsu'})
    station_list.append({'code':'KTA', 'name':'Kita Takatsu'})
    station_list.append({'code':'IRE', 'name':'Hase Irie'})
    station_list.append({'code':'HSE', 'name':'Hasecho'})
    station_list.append({'code':'HYS', 'name':'Hayashidacho'})
    station_list.append({'code':'GOM', 'name':'Nakagomicho'})
    station_list.append({'code':'HIR', 'name':'Hirai'})
    station_list.append({'code':'GTKU', 'name':'Takatsu Garage'})
    station_list.append({'code':'GOBA', 'name':'Obama Garage'})

    with open('station_list.csv', 'wt') as csvfile:
        fieldnames = ['code', 'name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in station_list:
            writer.writerow(row)
    print('%s stations are written' % len(station_list))

    # Zone specific station information
    zone = 'S'
    station_zone_list = []
    station_zone_list.append({'code':'OBA', 'zone':zone, 'center_position':0.000, 'station_range':(-0.140, 0.180)})
    station_zone_list.append({'code':'NOB', 'zone':zone, 'center_position':2.423, 'station_range':(-0.100, 0.180)})
    station_zone_list.append({'code':'HNS', 'zone':zone, 'center_position':5.679, 'station_range':(-0.100, 0.100)})
    station_zone_list.append({'code':'SRT', 'zone':zone, 'center_position':8.132, 'station_range':(-0.100, 0.100)})
    station_zone_list.append({'code':'HOZ', 'zone':zone, 'center_position':11.416, 'station_range':(-0.100, 0.100)})
    station_zone_list.append({'code':'TAI', 'zone':zone, 'center_position':14.693, 'station_range':(-0.160, 0.120)})
    station_zone_list.append({'code':'MTU', 'zone':zone, 'center_position':16.910, 'station_range':(-0.090, 0.090)})
    station_zone_list.append({'code':'YAN', 'zone':zone, 'center_position':19.431, 'station_range':(-0.090, 0.090)})
    station_zone_list.append({'code':'TKU', 'zone':zone, 'center_position':21.600, 'station_range':(-0.180, 0.160)})
    station_zone_list.append({'code':'KTA', 'zone':zone, 'center_position':23.774, 'station_range':(-0.100, 0.100)})
    station_zone_list.append({'code':'IRE', 'zone':zone, 'center_position':25.823, 'station_range':(-0.100, 0.100)})
    station_zone_list.append({'code':'HSE', 'zone':zone, 'center_position':28.049, 'station_range':(-0.100, 0.100)})
    station_zone_list.append({'code':'HYS', 'zone':zone, 'center_position':30.548, 'station_range':(-0.120, 0.140)})
    station_zone_list.append({'code':'GOM', 'zone':zone, 'center_position':33.200, 'station_range':(-0.100, 0.100)})
    station_zone_list.append({'code':'HIR', 'zone':zone, 'center_position':35.789, 'station_range':(-0.100, 0.100)})

    with open('station_zone.csv', 'wt') as csvfile:
        fieldnames = ['code', 'zone', 'center_position', 'station_range']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in station_zone_list:
            writer.writerow(row)
    print('%s zone specific station information are written' % len(station_zone_list))

    # Tracks
    track_list = []
    prev_station = None
    for station in station_zone_list:
        if prev_station:
            if prev_station['code'] + '-' + station['code'] in ('TAI-MTU', 'MTU-YAN', 'YAN-TKU', 'TKU-KTA'):
                category = 'M'
            else:
                category = 'S'

            track_list.append({'name':prev_station['code'] + '-' + station['code'], 'zone':zone,
                               'speed':70, 'category':category,
                               'track_range':(prev_station['center_position'], station['center_position'])})
        prev_station = station

    with open('track_list.csv', 'wt') as csvfile:
        fieldnames = ['name', 'zone', 'speed', 'category', 'track_range']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in track_list:
            writer.writerow(row)
    print('%s tracks are written' % len(track_list))

    # Garages
    garage_list = []
    garage_list.append({'code':'GOBA', 'lanes':2})
    garage_list.append({'code':'GTKU', 'lanes':16})

    with open('garage_list.csv', 'wt') as csvfile:
        fieldnames = ['code', 'lanes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in garage_list:
            writer.writerow(row)
    print('%s garages are written' % len(garage_list))

    # Lanes - assumption : each station has 2 lanes except start and end station (1 lane)
    lane_list = []
    for counter, station in enumerate(station_zone_list):
        connection = []
        # add tracks for connection
        if counter > 0:
            connection.append(track_list[counter-1]['name'])
        if counter < len(track_list):
            connection.append(track_list[counter]['name'])
        # add garages for connection
        if station['code'] in ('OBA', 'TKU'):
            connection.append('G' + station['code'])
        # create lanes
        if station['code'] not in ('OBA', 'HRI'):
            lane_list.append({'code':station['code'], 'zone':zone, 'name':'Lane2',
                              'priority':'B', 'offset':-0.040, 'lane_range':(-0.080, 0.080),
                              'connection':connection})
        lane_list.append({'code':station['code'], 'zone':zone, 'name':'Lane1',
                          'priority':'A', 'offset':0.040, 'lane_range':(-0.080, 0.080),
                          'connection':connection})

    with open('lane_list.csv', 'wt') as csvfile:
        fieldnames = ['code', 'zone', 'name', 'priority', 'offset', 'lane_range', 'connection']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in lane_list:
            writer.writerow(row)
    print('%s lanes are written' % len(lane_list))

if __name__ == '__main__':

    # create csv file anyway
    create_sample_csv()
