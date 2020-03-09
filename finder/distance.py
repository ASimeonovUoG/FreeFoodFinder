import googlemaps
from math import radians, sin, cos, acos

def read_google_key():
    google_api_key = None
    try:
        with open('google.key', 'r') as f:
            google_api_key = f.readline().strip()
    except:
        try:
            with open('../google.key') as f:
                google_api_key = f.readline().strip()

        except:
            raise IOError('Google API key file not found')

    return google_api_key


def calculate_distance(location1, location2):
    gmaps = googlemaps.Client(key=read_google_key())
    try:
        location1_coords = gmaps.geocode(location1)[0]['geometry']['location']
        location1_lat = location1_coords['lat']
        location1_long = location1_coords['lng']

        location2_coords = gmaps.geocode(location2)[0]['geometry']['location']
        location2_lat = location2_coords['lat']
        location2_long = location2_coords['lng']
    except:
        raise Exception("invalid input")

    #formula from https: // www.w3resource.com / python - exercises / math / python - math - exercise - 27.php

    lat1 = radians(location1_lat)
    lat2 = radians(location2_lat)
    long1 = radians(location1_long)
    long2 = radians(location2_long)

    #radius of the earth
    r = 6371.01

    dist = r * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(long1 - long2))
    return dist
