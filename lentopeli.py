from geopy import distance
import mysql.connector

yhteys = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='flight_game',
    user='root',
    password='pass',
    autocommit=False
)

airports = []
km_total = 0
dist_by_type = {
    "closed": 0,
    "balloonport": 10,
    "heliport": 50,
    "small_airport": 100,
    "medium_airport": 200,
    "large_airport": 500,
    "seaplane_base": 100
}

def generate_random_location():
        sql = "SELECT ident, name, type, latitude_deg, longitude_deg " \
              "FROM airport WHERE NOT type='closed'" \
              " ORDER BY RAND() LIMIT 1;"
        print(sql)
        cursor = yhteys.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        ident, name, type, lat, long = result[0]

        parsed = {
            "ident": ident,
            "name": name,
            "type": type,
            "lat": lat,
            "long": long,
        }
        return parsed

def fetch_available_airports(curr_lat, curr_long, dest_lat, dest_long type):
  # Define flight radius based on airport type
  radius_km = None
  if type in dist_by_type:
    radius_km = dist_by_type[type]
  else:
    raise Exception(f"Airport type '{type}' is invalid.")

  # Select all airports within the reach of current location,
  # based on airport type, order by ones closest to destination
  # Distance = 3963.0 * arccos[(sin(lat1) * sin(lat2)) + cos(lat1) * cos(lat2) * cos(long2 – long1)] * 1.609344
  f"""SELECT ident, name, iso_country, latitude_deg, longitude_deg FROM airport
  WHERE 3963.0 * acos((sin(RADIANS({curr_lat})) * sin(RADIANS(latitude_deg))) +
  cos(RADIANS({curr_lat})) * cos(RADIANS(latitude_deg)) *
  cos(RADIANS(longitude_deg) - RADIANS({curr_long}))) * 1.609344 <= {radius_km}
  AND type != 'closed'
  ORDER by (3963.0 * acos((sin(RADIANS(latitude_deg)) * sin(RADIANS({dest_lat}))) +
  cos(RADIANS(latitude_deg)) * cos(RADIANS({dest_lat})) *
  cos(RADIANS({dest_long}) - RADIANS(longitude_deg))) * 1.609344) LIMIT 15;"""

def print_available_airports():
  print

def move(ident):
  print

def check_if_arrived():
    sql = "SELECT ident, name, type, latitude_deg, longitude_deg " \
          "FROM airport WHERE NOT type='closed'"\
          " ORDER BY RAND() LIMIT 1;"
    print(sql)
    cursor = yhteys.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    ident, name, type, lat, long = result[0]

    parsed = {
      "ident":ident,
      "name":name,
      "type":type,
      "lat":lat,
      "long":long,
    }
    return parsed



current = destination = generate_random_location()
while destination == current or \
    distance.distance([current["lat"], current["long"]],
                          [destination["lat"], destination["long"]]).km < 5000:
    destination = generate_random_location()

#change ident into country later
print(f"Aloitus paikkasi on {current['name']} maassa {current['ident']} ja päämääräsi on {destination['name']} maassa {destination['ident']}.")
input("Paina Enter printataksesi lähimmät lentokentät.")

airports = fetch_available_airports(current["lat"], current["long"], current["type"])
for airport in airports:
    print(airport)
