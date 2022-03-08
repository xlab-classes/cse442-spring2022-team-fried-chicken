import discord
from discord.ext import commands
import random

intents = discord.Intents.default()  # Intents required to be declared for certain server perms
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='%', help_command=None, intents=intents)  # Creates instance of bots

policyCards = ['Separatist', 'Loyalist']

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="stonks"))


@bot.command()
async def hello(ctx, num: int):
    await ctx.send("hello {}".format(num + 1))


@bot.command()
async def JOHNCENA(ctx):
    await ctx.send("YOU CAN'T SEE ME")

@bot.command()
async def pullCards(ctx):
    await ctx.send(random.choices(policyCards, k = 3)) # send three random policy cards to server.

@bot.command()
async def assign_roles(ctx):
    players = []  # list of players
    for member in ctx.guild.members:  # gets all members in the server
        if not member.bot:  # that aren't bots
            players.append(member)
    palpatine = players.pop(random.randrange(len(players)))  # removes one person from list to make palpatine
    separatist = players.pop(random.randrange(len(players)))  # removes one person from the list to make a separatist - need to change later so 30% of players are seperatists
    palpatine_dm = await palpatine.create_dm()  # creates dm channel for palpatine
    await palpatine_dm.send("You are palpatine!")  # sends palpatine the message
    separatist_dm = await separatist.create_dm()  # creates dm channel for seperatists
    await separatist_dm.send("You are a seperatist!")  # sends separatist the message
    for loyalist in players:  # remainder of players are loyalists
        loyalist_dm = await loyalist.create_dm()  # creates loyalist dms
        await loyalist_dm.send("You are a loyalist!")  # sends loyalists msgs


bot.run(open("token.txt", "r").readline())  # Starts the bot
