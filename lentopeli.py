import math
import mysql.connector

airports = []
km_total = 0
dist_by_type = {
  closed: 0,
  balloonport: 10,
  heliport: 50,
  small_airport: 100,
  medium_airport: 200,
  large_airport: 500,
  seaplane_base: 100
}

def generate_random_location():
def fetch_available_airports(curr_lat, curr_long, type):
  # Define flight radius based on airport type
  radius_km = None
  if type in dist_by_type:
    radius_km = dist_by_type[type]
  else:
    raise Exception(f"Airport type '{type}' is invalid.")

  # Select all airports within the reach of current location
  # ((delta x)_to_km)^2 + ((delta y)_to_km)^2 <= R^2
  # Latitude: 1 deg = 110.574 km
  # Longitude: 1 deg = 111.320*cos(latitude) km
  f"""SELECT ident, name, iso_country, latitude_deg, longitude_deg FROM airport
  WHERE POWER(({curr_lat} + latitude_deg)*110.574, 2) +
  POWER(({curr_long} + longitude_deg)*111.320*cos(latitude_deg), 2) <= POWER({radius_km}, 2)
  AND type != 'closed'
  OR POWER(({curr_lat} + latitude_deg)*110.574, 2) +
  POWER(({curr_long} - longitude_deg)*111.320*cos(latitude_deg), 2) <= POWER({radius_km}, 2)
  AND type != 'closed'
  OR POWER(({curr_lat} - latitude_deg)*110.574, 2) +
  POWER(({curr_long} + longitude_deg)*111.320*cos(latitude_deg), 2) <= POWER({radius_km}, 2)
  AND type != 'closed'
  OR POWER(({curr_lat} - latitude_deg)*110.574, 2) +
  POWER(({curr_long} - longitude_deg)*111.320*cos(latitude_deg), 2) <= POWER({radius_km}, 2)
  AND type != 'closed'
  ORDER by (latitude_deg + longitude_deg) LIMIT 50;"""
def print_available_airports():
def move(ident):
def check_if_arrived():
