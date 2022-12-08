import os
import json
import shutil
import random
import interactions

from util import *
from os.path import exists
from dotenv import load_dotenv

def pluralize(list):
    return f"{'categories' if len(list) > 1 else 'category'} {', '.join(list)}"

# load tokens and IDs for bot
load_dotenv()
discordToken = os.getenv("discord-token")
guildID = int(str(os.getenv("guild-id")))

# initialize empty settings file if none exists
if not exists("./settings.json"):
    shutil.copyfile("default.json", "settings.json")
with open("sessiondata.json", "w") as sessionDataFile:
    json.dump({}, sessionDataFile)
    

bot = interactions.Client(token=str(discordToken))

@bot.command(
    name="configure",
    description="Change a setting.",
    scope=guildID,
    options=[
        interactions.Option(
            name="name",
            description="Setting to configure.",
            type=interactions.OptionType.STRING,
        ),
        interactions.Option(
            name="value",
            description="New value for the setting being configured.",
            type=interactions.OptionType.STRING
        ),
    ]
)
async def configure(ctx, name, value):
    if name == "categories":
        changeLists = changeSetting(name, value)
        await ctx.send(f"Added {pluralize(changeLists[0])} and removed {pluralize(changeLists[1])}!")
    else:
        changeSetting(name, value)
        await ctx.send(f"{name} set to {value} successfully!")

@bot.command(
    name="categorypoll",
    description="Create a strawpoll to select a category.",
    scope=guildID,
)
async def categorypoll(ctx):
    settings = readJSONFile("settings.json")
    pollUrl = generatePoll("Choose a category!", settings["categories"])
    await ctx.send(pollUrl)

@bot.command(
    name="restaurantpoll",
    description="Create a strawpoll to select a restaurant.",
    scope=guildID,
    options=[
        interactions.Option(
            name="unrandomized",
            description="Should results be based on most recent category poll? y/n",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ]
)
async def restaurantpoll(ctx, unrandomized="n"):
    randomize = unrandomized.lower()[0] != "y"
    category = None

    if randomize or "last-category-poll" not in readJSONFile("sessiondata.json"):
        category = random.choice(readJSONFile("settings.json")["categories"])
    else:
        category = getPollResults("last-category-poll")

    nearbyRestaurants = getNearbyRestaurantsByGenre(category)

    if len(nearbyRestaurants) < 1:
        await ctx.send(f"No {category} restaurants were found.")
        return

    pollUrl = generatePoll("Choose a restaurant!", nearbyRestaurants, "restaurant")
    await ctx.send(pollUrl)

@bot.command(
    name="showresults",
    description="Create a strawpoll to select restaurant.",
    scope=guildID,
    options=[
        interactions.Option(
            name="polltype",
            description="category or restarant?",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ]
)
async def showresults(ctx, polltype="category"):
    if polltype == "category":
       result = getPollResults("last-category-poll") 
    elif polltype == "restaurant":
        result = getPollResults("last-restaurant-poll")
    else:
        result = "Invalid polltype provided."
    await ctx.send(result)

@bot.command(
    name="pickrestaurant",
    description="Randomly pick a nearby restaurant.",
    scope=guildID,
    options=[
        interactions.Option(
            name="category",
            description="Optionally include category name or use last category poll result else random.",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ]
)
async def pickrestaurant(ctx, category=None):
    settings = readJSONFile("settings.json")
    sessionData = readJSONFile("sessiondata.json")

    if type(category) == str:
        restaurants = getNearbyRestaurantsByGenre(category)
    elif "last-category-poll" in sessionData: 
        restaurants = getNearbyRestaurantsByGenre(getPollResults("last-category-poll"))
    else:
        restaurants = getNearbyRestaurantsByGenre(random.choice(settings["categories"]))

    if (len(restaurants) > 0):
        await ctx.send(random.choice(restaurants))
    else:
        await ctx.send("Failed to generate a response in time.")

@bot.command(
    name="clearsession",
    description="Clear session data/cookies.",
    scope=guildID,
)
async def clearsession(ctx):
    writeJSONFile("sessiondata.json", {})
    await ctx.send("Successfully erased session data!")

bot.start()
