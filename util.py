from dotenv import load_dotenv
import requests
import json
import os
import re

load_dotenv()

coordinateQuery = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?"
restaurantQuery = "https://api.tomtom.com/search/2/poiSearch/"

coordinateMetadata = "&format=json&benchmark=2020&vintage=2010"

tomtomAPIToken = os.environ.get("api-token")

def convertAddressToSearchStr(address):
    safeSearchStr = re.sub(r"[\W_]+", "+", address)
    return coordinateQuery + "address=" + safeSearchStr + coordinateMetadata

def getCoordinatesFromAddress(address):
    response = requests.get(convertAddressToSearchStr(address))
    # maybe throw error indicating invalid addresses?
    relevantData = response.json()["result"]["addressMatches"][0]["geographies"]["Census Blocks"][0]
    return (relevantData["CENTLAT"], relevantData["CENTLON"])

def getNearbyRestaurantsByGenre(genre):
    # if settings don't contain address, throw error? 
    with open("settings.json", "r") as settingsFile:
        settings = json.load(settingsFile)
    if ("address" not in settings):
        raise Exception("User has not configured address in settings.")    
    if ("radius" in settings):
        radius = settings["radius"]
    else:
        radius = 1500

    coordinates = getCoordinatesFromAddress(settings["address"])
    metadata = genre + f".json?key={tomtomAPIToken}&radius={radius}&lat={coordinates[0]}&lon={coordinates[1]}"
    response = requests.get(restaurantQuery + metadata)

    return [ result["poi"]["name"] for result in response.json()["results"] ]

def changeSetting(setting, newValue):
    with open("settings.json", "r") as settingsFile:
        settings = json.load(settingsFile)
    settings[setting] = newValue
    with open("settings.json", "w") as settingsFile:
        json.dump(settings, settingsFile)

        
