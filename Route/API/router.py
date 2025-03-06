import logging
import pip._vendor.requests as requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import xml.etree.ElementTree as ET
import plotly.express as px
from tqdm import tqdm
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

    print(f"Distance === {distance(orig_latlng, dest_latlng)}")

    resp = get_route(orig_latlng[0], orig_latlng[1], dest_latlng[0], dest_latlng[1])
    print(f"Response === {resp}")
    
    route_nodes = resp['routes'][0]['legs'][0]['annotation']['nodes']

    print(f"Route Nodes === {route_nodes}")


    headers = { 'Content-type': 'application/json'}

    ### keeping every third element in the node list to optimise time
    route_list = []
    for i in range(0, len(route_nodes)):
        if i % 3==1:
            route_list.append(route_nodes[i])

    coordinates = []

    for node in tqdm(route_list):
        try:
            url = 'https://api.openstreetmap.org/api/0.6/node/' + str(node)
            r = requests.get(url, headers = headers)
            myroot = ET.fromstring(r.text)
            for child in myroot:
                lat, long = child.attrib['lat'], child.attrib['lon']
            coordinates.append((lat, long))
        except:
            continue
    print(coordinates[:10])

    df_out = pd.DataFrame({'Node': np.arange(len(coordinates))})
    df_out['coordinates'] = coordinates
    df_out[['lat', 'long']] = pd.DataFrame(df_out['coordinates'].tolist())

    # Converting Latitude and Longitude into float
    df_out['lat'] = df_out['lat'].astype(float)
    df_out['long'] = df_out['long'].astype(float)

    # Plotting the coordinates on map
    color_scale = [(0, 'red'), (1,'green')]
    fig = px.scatter_mapbox(df_out, 
                            lat="lat", 
                            lon="long", 
                            zoom=8, 
                            height=600,
                            width=900)


    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()

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