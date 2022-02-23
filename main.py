import discord
from discord.ext import commands
import random

intents = discord.Intents.default()  # Intents required to be declared for certain server perms
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='%', help_command=None, intents=intents)  # Creates instance of bots


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
async def assign_roles(ctx):
    players = []
    for member in ctx.guild.members:
        if not member.bot:
            players.append(member)
    hitler = random.sample(players, 1)[0]
    fascist = random.sample(players, 1)[0]
    hitler_dm = await hitler.create_dm()
    await hitler_dm.send("You are hitler!")
    fascist_dm = await fascist.create_dm()
    await fascist_dm.send("You are fascist!")
    for liberal in players:
        liberal_dm = await liberal.create_dm()
        await liberal_dm.send("You are liberal!")


bot.run(open("token.txt", "r").readline())  # Starts the bot

