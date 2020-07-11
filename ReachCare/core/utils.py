import logging
from geopy import Nominatim
import requests
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter



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




class GeoPyClient:
    def __init__(self, user_agent='reachcare'):
        self.geocode = RateLimiter(Nominatim(user_agent=user_agent).geocode, min_delay_seconds=1)

    def find_lat_long_from_zipcode(self, zipcode):
        loc = self.geocode(f"{zipcode}, US")
        if loc:
            return loc.latitude, loc.longitude

    def find_distance(self, loc1, loc2):
        return distance(loc1, loc2).miles





