import random
import json

from os import path
from discord import Game
from discord.ext import commands as c

VERSION = "1.1.0"

# Grab the config variables
with open("config.json") as cfg:
    config = json.load(cfg)

# Grab the databases
with open("db.json") as dtb:
    db = json.load(dtb)

with open("nsfw.json") as nsfwf:
    nsfw = json.load(nsfwf)

# Helper command to update the database
def update_db(database, filename):
    with open(filename, "w") as dtb:
        json.dump(database, dtb, indent=4)

description="""
Basic quote bot.
"""
bot = c.Bot(c.when_mentioned_or(config["prefix"]), description=description)

# Check for if the user running a command is the bot's owner.
def is_owner():
    return c.check(lambda ctx: ctx.message.author.id == config["owner"])

# Change avatar and username
async def update_profile(name, picture):
    if path.isfile(picture):
        with open(picture, "rb") as avatar:
            await bot.edit_profile(avatar=avatar.read())
            print("Bot avatar set.")
        await bot.edit_profile(username=name)
        print("Bot name set.")

# Events
@bot.event
async def on_ready():
    print("Attempting to set username and avatar.")
    try:
        await update_profile(config["bot_name"], config["avatar"])
    except Exception as err:
        print(f"Error setting name or avatar: {err}")

    print("============READY")
    print(f"QuoteBot v{VERSION}")
    print(f"Logged in as: {bot.user.name} ({bot.user.id})")
    print("============READY")

@bot.event
async def on_command_error(err, ctx):
    channel = ctx.message.channel
    if isinstance(err, c.CheckFailure):
        await bot.send_message(channel, "You don't have permission to do that.")
    elif isinstance(err, c.MissingRequiredArgument):
        await bot.send_message(channel, "Missing argument(s).")

# Commands
@bot.command(name="quit")
@is_owner()
async def bot_quit():
    """Shut the bot down."""
    await bot.say("Shutting down...")
    await bot.logout()

@bot.command(name="status")
@is_owner()
async def bot_status(*, status: str = None):
    """Change the bot's 'playing' status.

    Running this command without any arguments will turn the 'playing' status off'
    """
    game = Game(name=status)
    await bot.change_status(game=game)

@bot.command(name="info")
async def bot_info():
    """Display info about the bot."""
    await bot.say(f"QuoteBot v{VERSION}")

@bot.group(aliases=["quotes"], pass_context=True)
async def quote(ctx):
    """Quotes!

    Running the command without any arguments will display a random quote.
    """
    if ctx.invoked_subcommand is None:
        try:
            quote_body = random.choice(db["quotes"])
        except IndexError:
            await bot.say("There are no quotes.")
            return
        await bot.say(quote_body)

@quote.command(name="add", aliases=["new", "create"])
async def quote_new(name, *, body: str):
    """Add a new quote."""
    quote_body = f"<{name}> {body}"
    if quote_body not in db["quotes"]:
        db["quotes"].append(quote_body)
        update_db(db, "db.json")
        await bot.say("Quote added.")
    else:
        await bot.say("That quote already exists.")

@quote.command(name="remove", aliases=["del", "destroy"])
async def quote_remove(*, body: str):
    """Remove a quote.

    Copy/Paste the entire line of a quote to remove it.
    """
    if body in db["quotes"]:
        db["quotes"].remove(body)
        update_db(db, "db.json")
        await bot.say("Quote removed.")
    else:
        await bot.say("Quote doesn't exist.")

@bot.group(name="nsfw", pass_context=True)
async def nsfw_c(ctx):
    """Not safe for work quotes!

    Running the command without any arguments will display a random NSFW quote.
    """
    if ctx.invoked_subcommand is None:
        try:
            nsfw_body = random.choice(nsfw["quotes"])
        except IndexError:
            await bot.say("There are no NSFW quotes.")
            return
        await bot.say(nsfw_body)

@nsfw_c.command(name="add", aliases=["new", "create"])
async def nsfw_new(name, *, body: str):
    """Add a new NSFW quote."""
    nsfw_body = f"<{name}> {body}"
    if nsfw_body not in nsfw["quotes"]:
        nsfw["quotes"].append(nsfw_body)
        update_db(nsfw, "nsfw.json")
        await bot.say("NSFW quote added.")
    else:
        await bot.say("That NSFW quote already exists.")

@nsfw_c.command(name="remove", aliases=["del", "destroy"])
async def nsfw_remove(*, body: str):
    """Remove an NSFW quote.

    Copy/Paste the entire line of an NSFW quote to remove it.
    """
    if body in nsfw["quotes"]:
        nsfw["quotes"].remove(body)
        update_db(nsfw, "nsfw.json")
        await bot.say("NSFW quote removed.")
    else:
      	await bot.say("NSFW quote doesn't exist.")

bot.run(config["token"])
