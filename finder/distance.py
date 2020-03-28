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


def get_coords(address):
    try:
        gmaps = googlemaps.Client(key=read_google_key())
        coords = gmaps.geocode(address)[0]['geometry']['location']
        lat = coords['lat']
        long = coords['lng']
        return lat, long
    except:
        raise Exception("invalid input")

#calculates the distance between a set of coordinates (the coordinates of the business, stored in the database) and
#another location
def calculate_distance(location1_lat, location1_long, location2):
    gmaps = googlemaps.Client(key=read_google_key())
    try:
        location2_coords = gmaps.geocode(location2)[0]['geometry']['location']
        location2_lat = location2_coords['lat']
        location2_long = location2_coords['lng']
    except:
        raise ValueError("invalid input")

    #formula from https: // www.w3resource.com / python - exercises / math / python - math - exercise - 27.php

    lat1 = radians(location1_lat)
    lat2 = radians(location2_lat)
    long1 = radians(location1_long)
    long2 = radians(location2_long)

    #radius of the earth
    r = 6371.01

    dist = r * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(long1 - long2))
    return dist