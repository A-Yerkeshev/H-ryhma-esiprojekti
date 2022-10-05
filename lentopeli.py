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
    "balloonport": 50,
    "heliport": 100,
    "small_airport": 300,
    "medium_airport": 500,
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


def fetch_available_airports(curr_lat, curr_long, type):
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

    # Order airports by direction
    direction_groups = [[], [], [], [], [], [], [], []]

    for entry in result:
        airport = tuple_to_dict(entry)

        # Calculate in which direction airport is located
        x = math.cos(airport['lat']) * math.sin(airport['long'] - curr['long'])
        y = math.cos(curr['lat']) * math.sin(airport['lat']) - math.sin(curr['lat']) * math.cos(
        airport['lat']) * math.cos(airport['long'] - curr['long'])
        bearing = math.degrees(math.atan2(x, y))

        if bearing >= -22.5 and bearing < 22.5:
            airport['direction'] = 'North'
            direction_groups[0].append(airport)
        elif bearing >= 22.5 and bearing < 67.5:
            airport['direction'] = 'North-West'
            direction_groups[1].append(airport)
        elif bearing >= 67.5 and bearing < 112.5:
            airport['direction'] = 'West'
            direction_groups[2].append(airport)
        elif bearing >= 112.5 and bearing < 157.5:
            airport['direction'] = 'South-West'
            direction_groups[3].append(airport)
        elif bearing >= 157.5 or bearing < -157.5:
            airport['direction'] = 'South'
            direction_groups[4].append(airport)
        elif bearing >= -157.5 and bearing < -112.5:
            airport['direction'] = 'South-East'
            direction_groups[5].append(airport)
        elif bearing >= -112.5 and bearing < -67.5:
            airport['direction'] = 'East'
            direction_groups[6].append(airport)
        elif bearing >= -67.5 and bearing < -22.5:
            airport['direction'] = 'North-East'
            direction_groups[7].append(airport)
        else:
            airport['direction'] = 'Unknown direction'

    for group in direction_groups:
        for airport in group:
            airports.append(airport)


def print_available_airports():
    for i, airport in enumerate(airports):
        print(f"{str(i + 1)+':':<5} {airport['airport_name'][0:49]+',':<50} {airport['type']:<15} {'in ' + airport['country_name'][0:22]:<25} {str(round(get_distance(curr['lat'], curr['long'], airport['lat'], airport['long']), 2))+' km':<15} {'to the '+airport['direction']+'.'}")


# initialize start and end locations, calculate distance
check_if_arrived = False
curr = generate_random_location()
dest = generate_random_location()
dist = get_distance(curr["lat"], curr["long"], dest["lat"], dest["long"])

while dest == curr or (dist > 4000 or dist < 1500):
    dest = generate_random_location()
    dist = get_distance(curr["lat"], curr["long"], dest["lat"], dest["long"])

# Start the game
while curr['ident'] != dest['ident']:
    print(f"\nYour current location is '{curr['airport_name']}', {curr['type']} in {curr['country_name']}"
          f"\nYour destination is '{dest['airport_name']}' in {dest['country_name']}."
          f"\nThe destination is {dist:.0f} km away.")

    input("\nPress 'Enter' to fetch the nearest airports.")
    fetch_available_airports(curr["lat"], curr["long"], curr["type"])
    print_available_airports()

    index = int(input("\nEnter the index of the airport you want to fly to: ")) - 1

    while index >= len(airports) or index < 0:
        print(f"Your input is invalid. Please type a number between 1 and {len(airports)}")
        index = int(input("\nEnter the index of the airport you want to fly to: ")) - 1

    temp_dest = airports[index]
    flight = get_distance(curr['lat'], curr['long'], temp_dest['lat'], temp_dest['long'])
    flight_compare = get_distance(temp_dest['lat'], temp_dest['long'], dest['lat'], dest['long'])
    if dist > flight_compare:
        dist = dist - flight
        if dist < 0:
            dist = dist * -1
    else:
        dist = dist + flight
    turns_total = turns_total + 1
    km_total = km_total + flight
    curr = airports[index]
    print(f"\nYou fly {flight:.1f} km to {curr['airport_name']}.")
    print("\r>", end="")
    time.sleep(0.2)
    print("\r----->", end="")
    time.sleep(0.2)
    print("\r---------->", end="")
    time.sleep(0.2)
    print("\r      --------->", end="")
    time.sleep(0.2)
    print("\r               >", end="")
    time.sleep(0.3)
print(f"\nCongratulations! You made it to your destination, {dest['airport_name']}.\n"
      f"It took you {turns_total} turns and {km_total:.1f} km in total.")
