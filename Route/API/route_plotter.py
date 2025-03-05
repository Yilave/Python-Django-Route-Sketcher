# Import the needed Liabraries
import logging
import json
import polyline
import folium
from folium.plugins import MeasureControl
import geocoder

from functools import lru_cache
import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)
DEBUG = True

import pip._vendor.requests as requests
import xml.etree.ElementTree as ET
from tqdm import tqdm

# Plotting
import plotly.express as px

@lru_cache(maxsize=None)
def geocode(location):
    return _geocode(location)

def _geocode(location):
    import geocoder
    g = geocoder.osm(location)
    return g.latlng

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

route_nodes = routejson['routes'][0]['legs'][0]['annotation']['nodes']

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
        print("###############")
        print(myroot)
        for child in myroot:
            lat, long = child.attrib['lat'], child.attrib['lon']
        coordinates.append((lat, long))
    except:
        continue
print(coordinates[:10])


df_out = pd.DataFrame({'Node': np.arange(len(coordinates))})
df_out['coordinates'] = coordinates
df_out[['lat', 'long']] = pd.DataFrame(df_out['coordinates'].tolist(),)

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