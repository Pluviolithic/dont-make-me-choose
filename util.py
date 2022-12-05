import requests
import re

coordinateQuery = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?"
metadata = "&format=json&benchmark=2020&vintage=2010"

def convertAddressToSearchStr(address):
    safeSearchStr = re.sub(r"[\W_]+", "+", address)
    return coordinateQuery + "address=" + safeSearchStr + metadata

def getCoordinatesFromAddress(address):
    response = requests.get(convertAddressToSearchStr(address))
    relevantData = response.json()["result"]["addressMatches"][0]["geographies"]["Census Blocks"][0]
    return (relevantData["CENTLAT"], relevantData["CENTLON"])

