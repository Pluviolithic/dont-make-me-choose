import os
import shutil
import interactions
from os.path import exists
from dotenv import load_dotenv
from util import changeSetting

# load tokens and IDs for bot
load_dotenv()
discordToken = os.getenv("discord-token")
guildID = int(str(os.getenv("guild-id")))

# initialize empty settings file if none exists
if not exists("./settings.json"):
    shutil.copyfile("default.json", "settings.json")

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
    changeSetting(name, value)
    await ctx.send(f"{name} set to {value} successfully!")

bot.start()
