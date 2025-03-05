import logging
import pip._vendor.requests as requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import numpy as np
import pandas as pd
import json
# import polyline
# import folium
# from folium.plugins import MeasureControl
# import geocoder

from functools import lru_cache

logger = logging.getLogger(__name__)
DEBUG = True

@lru_cache(maxsize=None)
def geocode(location):
    return _geocode(location)

def _geocode(location):
    loc = Nominatim(user_agent="Geopy Library")
    getLoc = loc.geocode(location)
    loc = (getLoc.latitude, getLoc.latitude)
    
    # g = geocoder.osm(location)
    # return g.latlng

@lru_cache(maxsize=None)
def get_route(olat, olng, dlat, dlng):
    response = _get_route(olat, olng, dlat, dlng)
    return response

def _get_route(olat, olng, dlat, dlng):
    url = f'http://router.project-osrm.org/route/v1/driving/{olng},{olat};{dlng},{dlat}?alternatives=false&steps=false'
    # logger.debug(url)
    response = None

    try:
        logger.debug(f'====== OSRM: {url}')
        response = requests.get(url, verify=False)
    except Exception as ex:
        raise
    
    # logger.debug(response.text)
    if response and response.text:
        response_dict = json.loads(response.text)
        #possible = pd.DataFrame([{'Distance': (route['distance'] / 1000) *  0.621371 , route['weight_name']: route['weight']} for route in response_dict['routes']])
        return response_dict
    else:
        return None
@lru_cache(maxsize=None)
def distance(origin, dest):
    response = _distance(origin, dest)

    return response
def _distance(origin, dest):
    origin = geocode(origin)
    dest = geocode(dest)
    distance_ = geodesic(origin, dest)
    return distance_

def get_routing_map(origin, destination, zoom=None):
    orig_latlng = geocode(origin)
    dest_latlng = geocode(destination)

    print(_distance(orig_latlng, dest_latlng))

    resp = get_route(orig_latlng[0], orig_latlng[1], dest_latlng[0], dest_latlng[1])

    return resp

get_routing_map('Plymouth, MN', 'San Diego, CA', zoom=None)


    # decoded = polyline.decode(resp["routes"][0]['geometry'])
    # distance = resp["routes"][0]['distance'] * 0.000621371
    # duration = resp["routes"][0]['duration'] / 60

    # map2 = folium.Map(location=(orig_latlng[0], orig_latlng[1]), zoom_start=zoom,
    #                                 control_scale=True)
    # # map2.add_child(MeasureControl(
    # #     primary_length_unit='miles',
    # #     secondary_length_unit='meters',
    # #     primary_area_unit='acres',
    # #     secondary_area_unit='sqmeters')
    # # )

    # folium.PolyLine(locations=decoded, color="blue").add_to(map2)

    # print(f"{duration} minutes")
    # print(f"{distance} miles")

    # return map2