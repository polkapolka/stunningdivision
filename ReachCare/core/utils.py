import logging

import requests

# http://api.geonames.org/findNearbyPostalCodes?postalcode=94611&country=USA&radius=10&username=reachcare
# Get an instance of a logger
logger = logging.getLogger(__name__)


class GeoNamesClient:
    url = "http://api.geonames.org/findNearbyPostalCodes"
    json_url = "http://api.geonames.org/findNearbyPostalCodesJSON"
    params = {}

    def __init__(self, username='reachcare', country="USA"):
        self.params['username'] = username
        self.params['country'] = country

    def find_nearby_postal_codes(self, zipcode, radius=10):
        if not zipcode:
            raise ValueError("Must provide zipcode")
        self.params['postalcode'] = zipcode
        self.params['radius'] = radius
        response_json = self.get(as_json=True)
        if 'postalCodes' not in response_json:
            logger.error(f"failed to get neerby postal codes for: {zipcode}, radius: {radius}")
        return response_json.get("postalCodes", [])

    def get(self, as_json=False):
        if as_json:
            response = requests.get(url=self.json_url, params=self.params)
            return response.json()
        else:
            response = requests.get(url=self.url, params=self.params)
            return response











