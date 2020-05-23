import requests
import json

# http://api.geonames.org/findNearbyPostalCodes?postalcode=94611&country=USA&radius=10&username=reachcare


class GeoNamesClient:
    url = "http://api.geonames.org/findNearbyPostalCodes"
    json_url = "http://api.geonames.org/findNearbyPostalCodesJSON"
    params = {}

    def __init__(self, username='reachcare', country="USA"):
        self.params['username']=username
        self.params['country']=country

    def find_nearby_postal_codes(self, zipcode, radius=10, as_json=False):
        if not zipcode:
            raise ValueError("Must provide zipcode")
        self.params['postalcode'] = zipcode
        self.params['radius'] = radius
        return self.get(as_json=as_json)['postalCodes']

    def get(self, as_json=False):
        if as_json:
            response = requests.get(url=self.json_url, params=self.params)
            return response.json()
        else:
            response = requests.get(url=self.url, params=self.params)
            return response











