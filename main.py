from email import message
import discord
from discord.ext import commands
import random

intents = discord.Intents.default()  # Intents required to be declared for certain server perms
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='%', help_command=None, intents=intents)  # Creates instance of bots
round_counter = 0

game_started = False
policyCards = ['Fascist', 'Liberal'] # Array to hold the randomly chosen policy cards each round.

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
    global members, gameHand # gameHand is a global variable to hold the hand the president and chancellor have.

    members = [m for m in ctx.guild.members if role in m.roles] # Verify the inputted role exists within the servers roles.
    for m in members:
        try:
            await m.send(gameHand) # Send msg to all discord users within the server that have the inputted roles.
            await m.send("You're the Chancellor, chose which policy you would like to enact. 0 or 1.")
            message_response = await bot.wait_for('message', check=lambda m: m.author == ctx.author) # Get card to remove from user.
            cardToRemove = message_response.content

            if(cardToRemove == "0"):
                gameHand.pop(0) # Remove first card in hand, second card will be the enacted policy.
            if(cardToRemove == "1"):
                gameHand.pop(1) # Remove second card in hand, first card will be the enacted policy.

            print(gameHand) # Debugging statement to ensure task test passes.

            print(f":white_check_mark: Message sent to {m}")
        except:
            print(f":x: No DM could be sent to {m}")
    print("Done!")

    newPolicy = gameHand[0] # Define the new policy to be enacted and display to all players.
    await ctx.send("The Chancellor has chosen to enact a new " + newPolicy + " policy!")


@bot.command()
async def sendHand(ctx, role: discord.Role):
    global members, gameHand # gameHand is a global variable to hold the hand the president and chancellor have.
    
    gameHand = random.choices(policyCards, k = 3) # Send three random policy cards to server.
    members = [m for m in ctx.guild.members if role in m.roles] # Verify the inputted role exists within the servers roles.
    for m in members:
        try:
            await m.send(gameHand) # Send msg to all discord users within the server that have the inputted roles.
            await m.send('Choose a single card to remove from the list. Type 0, 1, or 2. This card will be removed.')
            message_response = await bot.wait_for('message', check=lambda m: m.author == ctx.author)  # Get card to remove from user.
            cardToRemove = message_response.content

            if(cardToRemove == "0"):
                gameHand.pop(0) # Remove first card from the hand.
            if(cardToRemove == "1"):
                gameHand.pop(1) # Remove second card from the hand.
            if(cardToRemove == "2"):
                gameHand.pop(2) # Remove third card from the hand.

            print(gameHand) # Debugging statement to ensure task test passes.

            print(f":white_check_mark: Message sent to {m}")
        except:
            print(f":x: No DM could be sent to {m}")
    print("Done!")

    await ctx.send("President has removed card. Chancellor should now run the <%choseCard Chancellor> command.") # Notify players the President has removed the first card.

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

@bot.command()
@commands.has_role("Voter")
async def ja(ctx):
    voter = discord.utils.get(ctx.guild.roles, name="Voter")

    # let the author know they voted
    await ctx.message.author.send("you voted ja!")

    # remove voter role to ensure user can only vote once
    await ctx.message.author.remove_roles(voter)

@bot.command()
@commands.has_role("Voter")
async def nein(ctx):
    voter = discord.utils.get(ctx.guild.roles, name="Voter")

    # let the author know they voted
    await ctx.message.author.send("you voted nein!")

    # remove voter role to ensure user can only vote once
    await ctx.message.author.remove_roles(voter)
    
@bot.command()
async def next_round(ctx):
    global round_counter
    round_counter += 1
    await ctx.send("Now initiating round {}!".format(round_counter))

bot.run(open("token.txt", "r").readline())  # Starts the bot
