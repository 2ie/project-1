import os
import dotenv
import requests

dotenv.load_dotenv(dotenv.find_dotenv())

# zipcodeToLocation is a function that given a user's zipcode input, will return a formatted location string
def zipcode_to_location(zipcode):
    # The API used for this process is called Zipcodebase
    ZIPCODE_API_BASE_URL = "https://app.zipcodebase.com/api/v1/search"

    HEADERS = { 
    "apikey": os.getenv("ZIPCODE_API_KEY")}

    response_obj = requests.get(
        ZIPCODE_API_BASE_URL, headers=HEADERS, params={
            "codes": zipcode,
            "country": "US"
        },
    )

    response_info = response_obj.json()

    zipcode_obj = response_info["results"][zipcode][0]

    city = zipcode_obj["city"]
    state = zipcode_obj["state"]

    location_string = city + ", " + state + ", United States"

    return (location_string)