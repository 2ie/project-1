import requests
import os
import dotenv
from serpapi import GoogleSearch

dotenv.load_dotenv(dotenv.find_dotenv())

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

data = {
  "showtimes": [
    {
      "day": "Today",
      "date": "Nov 8",
      "theaters": [
        {
          "name": "Alamo Drafthouse Cinema South Lamar",
          "link": "https://www.google.com/search?q=alamo+drafthouse+cinema+south+lamar&stick=H4sIAAAAAAAAAOPgFeLSz9U3yElJK8_KkOLVT9c3NMwwrjCpMjQrThI2tDQzNjKzNLQwMjA2NTE3MjQx2MTEosVUWryIVTkxJzE3XyGlKDGtJCO_tDhVITkzLzU3UaE4v7QkQwEomVgEADpHpZ9fAAAA&sa=X&ved=2ahUKEwiYnMLe3Yj0AhWvgGoFHYilB7UQySZ6BAhOEAs",
          "distance": "1.5 mi",
          "address": "1120 South Lamar, Austin, TX 78704",
          "showing": [
            {
              "time": [
                "6:00pm",
                "7:00pm",
                "9:55pm",
                "10:10pm",
                "10:45pm"
              ],
              "type": "Standard"
            }
          ]
        },
        {
          "name": "Alamo Drafthouse Cinema Mueller",
          "link": "https://www.google.com/search?q=alamo+drafthouse+cinema+mueller&stick=H4sIAAAAAAAAAOPgFeLVT9c3NEw2yiu0yDXLkYJwM4wrTKoMzYqThM1MDM0NTcwNjC0sLUxNDI1NDY02MbFoMZUWL2KVT8xJzM1XSClKTCvJyC8tTlVIzsxLzU1UyC1NzclJLQIADHa9N14AAAA&sa=X&ved=2ahUKEwiYnMLe3Yj0AhWvgGoFHYilB7UQySZ6BAhOEBM",
          "distance": "3.2 mi",
          "address": "Suite 102, 1911 Aldrich Street, Austin, TX 78723",
          "showing": [
            {
              "time": [
                "2:40pm",
                "3:25pm",
                "6:35pm",
                "7:25pm"
              ],
              "type": "Standard"
            }
          ]
        },
        {
          "name": "AMC Barton Creek Square 14",
          "link": "https://www.google.com/search?q=amc+barton+creek+square+14&stick=H4sIAAAAAAAAAOPgFeLWT9c3LDc2MTdIt5TiBXEMM4wrTKoMzYqTRAwNzQ0MDIxMLUwNzAzNzI3MjI1NNjGxaDGVFi9ilUrMTVZISiwqyc9TSC5KTc1WKC4sTSxKVTA0AQAZeIHHWAAAAA&sa=X&ved=2ahUKEwiYnMLe3Yj0AhWvgGoFHYilB7UQySZ6BAhOEBo",
          "distance": "4.0 mi",
          "address": "2901 Capital Of Texas Hwy., Austin, TX 78746",
          "showing": [
            {
              "time": [
                "3:15pm",
                "6:45pm",
                "7:15pm",
                "8:15pm"
              ],
              "type": "Standard"
            },
            {
              "time": [
                "12:45pm",
                "4:15pm",
                "7:45pm"
              ],
              "type": "IMAX"
            },
            {
              "time": [
                "1:45pm",
                "5:15pm",
                "8:45pm"
              ],
              "type": "Dolby Cinema"
            }
          ]
        },
      ]
    },
  ]
}

# print(data["showtimes"][0]["theaters"])

def get_showtime_data(user_movie_query, user_location):
    user_movie_query = user_movie_query + "theater"

    params = {
      "q": user_movie_query,
      "location": user_location,
      "hl": "en",
      "gl": "us",
      "api_key": SERPAPI_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    theater_data = results["showtimes"][0]["theaters"]

    print(theater_data)
    return theater_data

# get_showtime_data("Super Mario Bros Movie", "Bastrop, Texas, United States")