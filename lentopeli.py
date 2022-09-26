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

# def fetch_available_airports(curr_lat, curr_long):


# def print_available_airports():


# def move(ident):


# def check_if_arrived():

current = destination = generate_random_location()
print(current)
while destination == current or \
    distance.distance([current["lat"], current["long"]],
                          [destination["lat"], destination["long"]]).km < 5000:
    destination = generate_random_location()