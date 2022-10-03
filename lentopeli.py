from geopy import distance
import mysql.connector
import math
import time


yhteys = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='flight_game',
    user='root',
    password='toast',
    autocommit=False
)

airports = []
flight_compare = ""
temp_dest = ""
turns_total = 0
km_total = 0
dist_by_type = {
    "closed": 0,
    "balloonport": 10,
    "heliport": 50,
    "small_airport": 200,
    "medium_airport": 400,
    "large_airport": 1000,
    "seaplane_base": 100
}


def get_distance(curr_lat, curr_long, dest_lat, dest_long):
    distance_result = distance.distance([curr_lat, curr_long],
                                        [dest_lat, dest_long]).km
    return distance_result

def generate_random_location():
    sql = "SELECT ident, airport.name as airport_name," \
          "country.name as country_name, type, latitude_deg, longitude_deg " \
          "FROM airport, country WHERE NOT type='closed' " \
          "and airport.iso_country = country.iso_country" \
          " ORDER BY RAND() LIMIT 1;"
    cursor = yhteys.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    return tuple_to_dict(result[0])

def tuple_to_dict(tuple):
    ident, airport_name, country_name, type, lat, long = tuple

    return {
        "ident": ident,
        "airport_name": airport_name,
        "country_name": country_name,
        "type": type,
        "lat": lat,
        "long": long,
    }

def fetch_available_airports(curr_lat, curr_long, dest_lat, dest_long, type):
    # Define flight radius based on airport type
    radius_km = None
    if type in dist_by_type:
      radius_km = dist_by_type[type]
    else:
      raise Exception(f"Airport type '{type}' is invalid.")

    # Select all airports within the reach of current location,
    # based on airport type, order by ones closest to destination
    # Distance = 3963.0 * arccos[(sin(lat1) * sin(lat2)) + cos(lat1) * cos(lat2) * cos(long2 – long1)] * 1.609344
    sql = f"""SELECT ident, airport.name, country.name, type, latitude_deg, longitude_deg FROM airport, country
    WHERE 3963.0 * acos((sin(RADIANS({curr_lat})) * sin(RADIANS(latitude_deg))) +
    cos(RADIANS({curr_lat})) * cos(RADIANS(latitude_deg)) *
    cos(RADIANS(longitude_deg) - RADIANS({curr_long}))) * 1.609344 <= {radius_km}
    AND type != 'closed'
    AND ident != '{curr["ident"]}'
    AND country.iso_country = airport.iso_country;"""
    cursor = yhteys.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    airports.clear()
    for entry in result:
        airports.append(entry)

def print_available_airports():
    # Order airports by direction
    direction_groups = [[], [], [], [], [], [], [], []]

    for i, airport in enumerate(airports):
        airport = tuple_to_dict(airport)

        # Calculate in which direction airport is located
        x = math.cos(airport['lat'])*math.sin(airport['long']-curr['long'])
        y = math.cos(curr['lat'])*math.sin(airport['lat'])-math.sin(curr['lat'])*math.cos(airport['lat'])*math.cos(airport['long']-curr['long'])
        bearing = math.degrees(math.atan2(x,y))

        if bearing >= -22.5 and bearing < 22.5:
            direction = 'North'
            direction_groups[0].append(airport)
        elif bearing >= 22.5 and bearing < 67.5:
            direction = 'North-West'
            direction_groups[1].append(airport)
        elif bearing >= 67.5 and bearing < 112.5:
            direction = 'West'
            direction_groups[2].append(airport)
        elif bearing >= 112.5 and bearing < 157.5:
            direction = 'South-West'
            direction_groups[3].append(airport)
        elif bearing >= 157.5 or bearing < -157.5:
            direction = 'South'
            direction_groups[4].append(airport)
        elif bearing >= -157.5 and bearing < -112.5:
            direction = 'South-East'
            direction_groups[5].append(airport)
        elif bearing >= -112.5 and bearing < -67.5:
            direction = 'East'
            direction_groups[6].append(airport)
        elif bearing >= -67.5 and bearing < -22.5:
            direction = 'North-East'
            direction_groups[7].append(airport)
        else:
            direction = 'Unknown direction'

    sorted = []
    for group in direction_groups:
        for airport in group:
            sorted.append(airport)

    # Print available airports
    for i, airport in enumerate(sorted):
        print(f"{str(i + 1)}: {airport['airport_name']}, in {airport['country_name']} - "
              f"{get_distance(curr['lat'], curr['long'], airport['lat'], airport['long']):.1f} km away"
              f" in {direction} direction.")


def move(index):
    global curr
    curr = tuple_to_dict(airports[index])
    airport = tuple_to_dict(airport)
    print(f"{str(i + 1)}: {airport['airport_name']}, {airport['country_name']} - "
            f"{get_distance(curr['lat'], curr['long'], airport['lat'], airport['long']):.1f} km away")

# initialize start and end locations, calculate distance
check_if_arrived = False
curr = generate_random_location()
dest = generate_random_location()
dist = get_distance(curr["lat"], curr["long"], dest["lat"], dest["long"])

while dest == curr or (dist > 6000 or dist < 3000):
    dest = generate_random_location()
    dist = get_distance(curr["lat"], curr["long"], dest["lat"], dest["long"])

# Start the game
while curr['ident'] != dest['ident']:
    print(f"\nYour current location is '{curr['airport_name']}', {curr['type']} in {curr['country_name']}"
    f"\nYour destination is '{dest['airport_name']}' in {dest['country_name']}."
    f"\nThe destination is {dist:.0f} km away.")

    input("\nPress 'Enter' to fetch the nearest airports.")
    fetch_available_airports(curr["lat"], curr["long"], dest["lat"], dest["long"], curr["type"])
    print_available_airports()

    index = int(input("\nEnter the index of the airport you want to go to: ")) - 1

    while index >= len(airports) or index < 0:
        print(f"Your input is invalid. Please, type number between 0 and {len(airports)}")
        index = int(input("\nEnter the index of the airport you want to go to: ")) - 1

    temp_dest = tuple_to_dict(airports[index])
    flight = get_distance(curr['lat'], curr['long'], temp_dest['lat'], temp_dest['long'])
    flight_compare = get_distance(temp_dest['lat'], temp_dest['long'], dest['lat'], dest['long'])
    if dist > flight_compare:
        dist = dist - flight
    else:
        dist = dist + flight
    turns_total = turns_total + 1
    km_total = km_total + flight
    curr = tuple_to_dict(airports[index])
    print(f"\nYou fly {flight:.1f} km to {curr['airport_name']}.")
    print("\r>", end="")
    time.sleep(0.3)
    print("\r----->", end="")
    time.sleep(0.3)
    print("\r---------->", end="")
    time.sleep(0.3)
    print("\r      --------->", end="")
    time.sleep(0.3)
    print("\r               >", end="")
    time.sleep(0.3)