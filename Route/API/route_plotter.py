# Import the needed Liabraries
import os
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pip._vendor.requests as requests
import xml.etree.ElementTree as ET
from tqdm import tqdm
from multiprocessing import Process
import time


# Plotting
import plotly.express as px

import logging
import json
from functools import lru_cache

FILE = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(FILE)

logger = logging.getLogger(__name__)
DEBUG = True

@lru_cache(maxsize=None)
def geocode(location):
    return _geocode(location)

def _geocode(location):
    loc = Nominatim(user_agent="Geopy Library")
    getLoc = loc.geocode(location)
    loc = (getLoc.longitude, getLoc.latitude) 
    return loc


@lru_cache(maxsize=None)
def distance(origin, dest):
    response = _distance(origin, dest)
    return response

def _distance(origin, dest):
    distance_ = geodesic((geocode(origin)[1], geocode(origin)[0]), (geocode(dest)[1], geocode(dest)[0])).miles
    return distance_

@lru_cache(maxsize=None)
def get_route(origin, destination):

    start_time = time.time()


    #source = (-83.920699, 35.96061) # Knoxville 
    #dest  = (-73.973846, 40.71742)  # New York City

    start = "{},{}".format(geocode(origin)[0], geocode(origin)[1])
    end = "{},{}".format(geocode(destination)[0], geocode(destination)[1])
    # Service - 'route', mode of transportation - 'driving', without alternatives
    url = 'http://router.project-osrm.org/route/v1/driving/{};{}?alternatives=false&annotations=nodes'.format(start, end)


    headers = { 'Content-type': 'application/json'}
    r = requests.get(url, headers = headers)
    print("Calling API ...:", r.status_code) # Status Code 200 is success


    routejson = r.json()
    print(routejson)
    route_nodes = routejson['routes'][0]['legs'][0]['annotation']['nodes']

    # print("Nodes number before: ", len(route_nodes))

    # print(route_nodes)
    distance_traveled =  distance(origin, destination)

    ### keeping every third element in the node list to optimise time
    # Note: the distance between each node on the rout is 100 metres apart
    route_list = []
    for i in range(0, len(route_nodes)):
        if i % 300 == 1:
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
    print(r.text)

    df_out = pd.DataFrame({'Node': np.arange(len(coordinates))})
    # df_out['nodes'] = final_nodes
    df_out['coordinates'] = coordinates
    df_out[['lat', 'long']] = pd.DataFrame(df_out['coordinates'].tolist())

    # Converting Latitude and Longitude into float
    df_out['lat'] = df_out['lat'].astype(float)
    df_out['long'] = df_out['long'].astype(float)

    df_lat = df_out['lat'].to_list()
    df_long = df_out['long'].to_list()
    lon_lat = zip(df_long, df_lat)


    # Get the average price data in the csv and compute the 
    # price_data = pd.read_csv('C:/Users/ISAAC/Desktop/ASSIGNMENT/Django Developer/Route/fuel-prices-for-be-assessment.csv')
    price_data = pd.read_csv(BASE_DIR + "/fuel-prices-for-be-assessment.csv")

    average_price = price_data['Retail Price'].mean() 
    # print(f"Average Price === {average_price}")
    gallons = distance_traveled / 10

    total_fuel_cost = gallons * average_price
        
    data = {
        "data": df_out, 
        "lon_lat": lon_lat,
        "lat": df_lat,
        "lon": df_long,
        "distance": f"{abs(distance_traveled)} Miles", 
        "gallons": gallons, 
        "average_price": abs(average_price), 
        "total_cost": f"${abs(total_fuel_cost)}", 
        # "nodes": final_nodes, 
        "length": len(route_list)
        }
    # end_time = time.time()
    # execution_time = end_time - start_time
    # print(execution_time)

    return data

if __name__ == '__main__':
    p = Process(target=get_route, args=('bob',))
    p.start()
    p.join()

   

# get_route('Brooklyn, NY', 'Philadelphia, Pennsylvania')

