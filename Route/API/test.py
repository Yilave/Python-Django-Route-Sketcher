# import pip._vendor.requests as requests
# from functools import lru_cache


# @lru_cache(maxsize=None)
# def geocode(location):
#     return _geocode(location)

# def _geocode(location):
#     import geocoder
#     g = geocoder.osm(location)
#     return g.latlng

# geocode('San Diego')

# importing geopy library and Nominatim class
from geopy.geocoders import Nominatim

# calling the Nominatim tool and create Nominatim class
loc = Nominatim(user_agent="Geopy Library")

# entering the location name
getLoc = loc.geocode("175 5th Avenue NYC")
loc = (getLoc.latitude, getLoc.latitude)

# printing address
print(loc[0])

# printing latitude and longitude
# print("Latitude = ", getLoc.latitude, "\n")
# print("Longitude = ", getLoc.longitude)

# url = 'http://router.project-osrm.org/route/v1/driving/13.388860,52.517037;13.397634,52.529407;13.428555,52.523219?overview=false'
# response = requests.get(url)
# print(response.text)
