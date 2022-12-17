from dotenv import load_dotenv
import requests
import json
import os
import re

load_dotenv()

#api to generate and read polls
strawPollAPI = "https://api.strawpoll.com/v3/polls"

#api to obtain coordinates from a provided address
coordinateQuery = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?"
coordinateMetadata = "&format=json&benchmark=2020&vintage=2010"

#api similar to google places api but free
restaurantQuery = "https://api.tomtom.com/search/2/poiSearch/"

tomtomAPIToken = os.environ.get("api-token")

def readJSONFile(fileName):
    with open(fileName, "r") as settingsFile:
        settings = json.load(settingsFile)
    return settings

def writeJSONFile(fileName, newSettings):
    with open(fileName, "w") as settingsFile:
        json.dump(newSettings, settingsFile)

def convertAddressToSearchStr(address):
    #replace all non-alphanumeric chunks in string with the + character
    #to make the string safe for url
    safeSearchStr = re.sub(r"[\W_]+", "+", address)
    return coordinateQuery + "address=" + safeSearchStr + coordinateMetadata

def getCoordinatesFromAddress(address):
    response = requests.get(convertAddressToSearchStr(address))
    try:
        relevantData = response.json()["result"]["addressMatches"][0]["geographies"]["Census Blocks"][0]
        return (relevantData["CENTLAT"], relevantData["CENTLON"])
    except IndexError:
        return False

def getNearbyRestaurantsByGenre(genre):
    settings = readJSONFile("settings.json")
    radius = settings["radius"]
    coordinates = getCoordinatesFromAddress(settings["address"])
    if coordinates:
        metadata = genre + f".json?key={tomtomAPIToken}&radius={radius}&lat={coordinates[0]}&lon={coordinates[1]}"
        response = requests.get(restaurantQuery + metadata)

        return [ result["poi"]["name"] for result in response.json()["results"] ]

    return []

def changeSetting(setting, newValue):
    if setting == "categories":
        #create lists to show user what changes occured in the settings
        addList = []
        removeList = []

        settings = readJSONFile("settings.json")
        categories = settings["categories"]

        #remove categories if they exist in settings
        #and add them if they do not exist
        for category in newValue.split():
            category = category.lower()
            if category in categories:
                removeList.append(category)
                categories.remove(category)
            else:
                addList.append(category)
                categories.append(category)

        writeJSONFile("settings.json", settings)

        return (addList, removeList)
    else:
        settings = readJSONFile("settings.json")
        settings[setting] = newValue
        writeJSONFile("settings.json", settings)

def generatePoll(prompt, options, pollType="category"):
    #removed duplication checking to allow for better testing
    data = {
        "title": prompt,
        "type": "multiple_choice",
        "poll_options": [ {"value": option} for option in options ],
        "poll_config": {"duplication_checking": "none"}
    }
    newPollData = requests.post(strawPollAPI, json=data)

    sessionData = readJSONFile("sessiondata.json")
    sessionData[f"last-{pollType}-poll"] = newPollData.json()["id"]
    writeJSONFile("sessiondata.json", sessionData)

    return newPollData.json()["embed_url"]

def getPollResults(pollTag):
    sessionData = readJSONFile("sessiondata.json")

    if not pollTag in sessionData:
        return "No such poll has taken place."

    pollResults = requests.get(strawPollAPI + "/" + sessionData[pollTag] + "/results").json()

    #iterate over poll options and find the current one with the most votes
    pollWinner = ""
    highestVoteCount = -1
    for option in pollResults["poll_options"]:
        if option["vote_count"] > highestVoteCount:
            highestVoteCount = option["vote_count"]
            pollWinner = option["value"]
            
    return pollWinner
        


