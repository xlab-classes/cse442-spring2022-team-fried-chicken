import discord
from discord.ext import commands
import random

intents = discord.Intents.default()  # Intents required to be declared for certain server perms
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='%', help_command=None, intents=intents)  # Creates instance of bots

game_started = False

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
async def start_game(ctx):
    global game_started
    game_started = True
    await ctx.send("Game initialized!")

@bot.command()
async def end_game(ctx):
    global game_started
    game_started = False
    await ctx.send("Game terminated!")


@bot.command()
@commands.has_permissions(administrator=True)
async def assign_roles(ctx):
    if game_started:
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
    else:
        await ctx.send("Start the game first with **%start_game**")

# @commands.has_role("President"): used when creating commands for only a specific role to use
# ctx.message.author: use to get the member variable for the message's original author

@bot.command()
async def assign(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)

@bot.command()
async def remove(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)

bot.run(open("token.txt", "r").readline())  # Starts the bot
