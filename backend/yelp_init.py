import os
import requests

yelp_api_key = os.getenv("YELP_API_KEY")

def search_yelp(term, location, price_level=None):
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {yelp_api_key}"}
    params = {
        "term": term,
        "location": location,
        "limit": 5
    }
    if price_level:
        params["price"] = price_level

    response = requests.get(url, headers=headers, params=params)
    return response.json()

