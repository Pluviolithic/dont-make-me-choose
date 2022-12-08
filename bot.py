import os
import json
import shutil
import strawpoll
import interactions
from os.path import exists
from dotenv import load_dotenv
from util import changeSetting

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
    pass

@bot.command(
    name="restaurantpoll",
    description="Create a strawpoll to select a restaurant.",
    scope=guildID,
    options=[
        interactions.Option(
            name="unrandomized",
            description="Should results be based on previous poll? y/n",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ]
)
async def restaurantpoll(ctx, unrandomized="n"):
    randomize = unrandomized.lower()[0] != "y"
    pass

@bot.command(
    name="showresults",
    description="Create a strawpoll to select restaurant.",
    scope=guildID,
    options=[
        interactions.Option(
            name="polltype",
            description="categorypoll or restarantpoll?",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ]
)
async def showresults(ctx, polltype):
    pass

@bot.command(
    name="pickrestaurant",
    description="Randomly pick a nearby restaurant.",
    scope=guildID,
    options=[
        interactions.Option(
            name="category",
            description="Optionally include category name or use last category poll result.",
            type=interactions.OptionType.STRING,
            required=False,
        ),
    ]
)
async def pickrestaurant(ctx, category):
    pass

bot.start()
