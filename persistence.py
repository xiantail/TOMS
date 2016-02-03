import configuration
import sqlite3
import csv
import pickle

config = configuration.read_config()
file = config['database']['file']

def migrage_station_name():
    conn = sqlite3.connect('toms.sqlite')
    cursor = conn.cursor()

    station_name_dict = {}
    values_to_insert = []
    with open('station_list.csv', 'rt') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # List is not required as this only be used to get name text
            station_name_dict[row['code']] = row['name']

    values_to_insert = []
    for entry in station_name_dict.items():
        values_to_insert.append(entry)
    cursor.executemany("""INSERT INTO station_name ('code', 'name') VALUES (?, ?)""", values_to_insert)
    conn.commit()
    conn.close()

def migrate_zone_specific_station():
    conn = sqlite3.connect('toms.sqlite')
    cursor = conn.cursor()

    values_to_insert = []
    with open('station_zone.csv', 'rt') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lrange = row['station_range'].strip("()").split(", ")
            station_range = tuple([float(x) for x in lrange])
            values_to_insert.append((row['code'], row['zone'], float(row['center_position']),
                                     float(station_range[0]), float(station_range[1])))
    cursor.executemany("""INSERT INTO zstaion ('code', 'zone', 'center_pos', 'range_from',
    'range_to') VALUES (?, ?, ?, ?, ?)""", values_to_insert)
    conn.commit()
    conn.close()

def migrate_tracks():
    conn = sqlite3.connect('toms.sqlite')
    cursor = conn.cursor()

    values_to_insert = []
    with open('track_list.csv', 'rt') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lrange = row['track_range'].strip("()").split(", ")
            track_range = tuple([float(x) for x in lrange])
            track_id = row['zone'] + row['name']
            category = row['category']
            if category == 'M':
                category = 'A'
            values_to_insert.append((track_id, category, row['zone'], float(row['speed']),
                                     float(track_range[0]), float(track_range[1])))
            if category == 'A':
                category = 'B'
                values_to_insert.append((track_id, category, row['zone'], float(row['speed']),
                                         float(track_range[0]), float(track_range[1])))
    cursor.executemany("""INSERT INTO tracks ('track_id', 'category', 'zone', 'speed', 'range_from',
    'range_to') VALUES (?, ?, ?, ?, ?, ?)""", values_to_insert)
    conn.commit()
    conn.close()

def migrate_garages():
    conn = sqlite3.connect('toms.sqlite')
    cursor = conn.cursor()

    values_to_insert = []
    with open('garage_list.csv', 'rt') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            values_to_insert.append((row['code'], 'Garage', row['code'][1:], row['lanes']))
    cursor.executemany("""INSERT INTO garages ('gid', 'name', 'station', 'lanes')
    VALUES (?, ?, ?, ?)""", values_to_insert)
    conn.commit()
    conn.close()

def migrate_station_lanes():
    conn = sqlite3.connect('toms.sqlite')
    cursor = conn.cursor()

    values_to_insert = []
    with open('lane_list.csv', 'rt') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lane_id = '{c}{n:0>2}'.format(c=row['code'],n=int(row['name'][-1]))
            offset = float(row['offset'])
            name = row['name']
            priority = row['priority']
            lrange = row['lane_range'].strip("()").split(", ")
            lane_range = tuple([float(x) for x in lrange])
            range_from = lane_range[0]
            range_to = lane_range[1]
            lclist = row['connection'].strip("[]'").split("', '")
            connection = pickle.dumps(lclist)

            values_to_insert.append((lane_id, name, offset, range_from, range_to, priority, connection))
    cursor.executemany("""INSERT INTO lanes ('lane_id', 'name', 'offset', 'range_from', 'range_to',
    'priority', 'connections') VALUES (?, ?, ?, ?, ?, ?, ?)""", values_to_insert)
    conn.commit()
    conn.close()