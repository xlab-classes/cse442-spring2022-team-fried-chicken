from email import message
import discord
from discord.ext import commands
import random

intents = discord.Intents.default()  # Intents required to be declared for certain server perms
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='%', help_command=None, intents=intents)  # Creates instance of bots

game_started = False
policyCards = ['Fascist', 'Liberal']

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
async def choseCard(ctx, role: discord.Role):
    global members
    global gameHand
    members = [m for m in ctx.guild.members if role in m.roles] # Verify the inputted role exists within the servers roles.
    for m in members:
        try:
            await m.send(gameHand) # Send msg to all discord users within the server that have the inputted roles.
            await m.send("You're the Chancellor, chose which policy you would like to enact. 0 or 1.")
            message_response = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
            cardToRemove = message_response.content

            if(cardToRemove == "0"):
                gameHand.pop(0)
            if(cardToRemove == "1"):
                gameHand.pop(1)

            print(gameHand)

            print(f":white_check_mark: Message sent to {m}")
        except:
            print(f":x: No DM could be sent to {m}")
    print("Done!")
    newPolicy = gameHand[0]
    await ctx.send("The Chancellor has chosen to enact a new " + newPolicy + " policy!")


@bot.command()
async def sendHand(ctx, role: discord.Role):
    global members

    global gameHand
    
    gameHand = random.choices(policyCards, k = 3) # Send three random policy cards to server.

    members = [m for m in ctx.guild.members if role in m.roles] # Verify the inputted role exists within the servers roles.
    for m in members:
        try:
            await m.send(gameHand) # Send msg to all discord users within the server that have the inputted roles.
            await m.send('Choose a single card to remove from the list. Type 0, 1, or 2. This card will be removed.')
            message_response = await bot.wait_for('message', check=lambda m: m.author == ctx.author)
            cardToRemove = message_response.content

            if(cardToRemove == "0"):
                gameHand.pop(0)
            if(cardToRemove == "1"):
                gameHand.pop(1)
            if(cardToRemove == "2"):
                gameHand.pop(2)

            print(f":white_check_mark: Message sent to {m}")
        except:
            print(f":x: No DM could be sent to {m}")
    print("Done!")
    print(gameHand)
    await ctx.send("President has removed card. Chancellor should now run the <%choseCard Chancellor> command.")



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

bot.run(open("token.txt", "r").readline())  # Starts the bot