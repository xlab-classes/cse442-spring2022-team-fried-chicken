from sys import flags
import discord
from discord.ext import commands
import random
import asyncio
from config import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from rsa import verify

intents = discord.Intents.all()  # Intents required to be declared for certain server perms
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='%', help_command=None, intents=intents)  # Creates instance of bots
cred = credentials.Certificate(firebase_config)
databaseApp = firebase_admin.initialize_app(cred, {
    "databaseURL": DatabaseURL
})

game_started = False
roles_assigned = False
presidentHasChosen = False  # Bool flag to ensure choseCard command is not run before the sendHand command.
chancellor_elected = False
round_ended = False
round_counter = 0
players = []
palpatine = []
separatist = []
loyalist = []
policyCards = ['Separatist', 'Loyalist']  # Array to hold the randomly chosen policy cards each round.

enactedPolicies = []  # Array to track currently enacted policy cards.
election_tracker = 0

@bot.command()
async def get_instructions(ctx):
    user = ctx.message.author
    instructions = "**Game Setup:**\n"
    instructions += "- Game must start with **%start_game**\n"
    instructions += "- All players must join with **%join_game**\n"
    instructions += "- Once all players have joined, the administrator must call **%assign_roles**\n"
    instructions += "- When the roles are being assigned, all players are messaged their private role\n"
    instructions += "--- Roles are either Loyalist, Palpatine, or Separatist"
    await user.send(instructions)
    instructions = "**Game Play:**\n"
    instructions += "- A random player is given the Public role of __President__\n"
    instructions += "- __President__ must select any player to be given the role of __Chancellor__ using the **%elect** command\n"
    instructions += "- Once a chancellor has been elected, the players must vote A(Yes) or B(No)\n"
    instructions += "--- If the majority vote is NO or if the vote is equal, then the round ends here and the next player is given the __President__ role\n"
    instructions += "- If the majority vote is YES, then the __President__ must dray three policy cards by calling the **%sendHand President** command and discard a card, sending the remaining two cards over to the __Chancellor__\n"
    instructions += "- The __Chancellor__ must discard one of the remaining two cards, allowing the remaining card to be enacted\n"
    instructions += "- The round then ends and the next player is given the role of __President__"
    await user.send(instructions)
    instructions = "**Object of the Game:**\n"
    instructions += "If you are one of the **Loyalists**:\n"
    instructions += "- Five Loyalist cards need to be enacted\n"
    instructions += "If you are **Palpatine** or one of the **Separatists**, one of these conditions needs to me met:\n"
    instructions += "- Six Separatist policies need to be enacted\n"
    instructions += "- At least three Separatist policies need to enacted and Palpatine is elected __Chancellor__"
    await user.send(instructions)



@bot.command(pass_context=True)
async def write(ctx):
    # color = input("Pick a color")
    user = ctx.message.author
    ref = db.reference(f"/")
    ref.update({
        "Color": "blue"
    })


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
    if not game_started:
        game_started = True
        await ctx.send("Game initialized!")
    else:
        await ctx.send("Game already started!")


@bot.command()
async def end_game(ctx):
    global game_started, roles_assigned, chancellor_elected, round_ended, round_counter, players
    game_started = False
    roles_assigned = False
    chancellor_elected = False
    round_ended = False
    round_counter = 0
    players = []
    await ctx.send("Game terminated!")


@bot.command()
async def join_game(ctx):
    user = ctx.message.author.name
    ref = db.reference(f"/")
    score = ref.get(user)
    if user not in score[0]:
        ref.update({
            user: {
                "Wins": 0,
                "Games": 0
            }
        })
    if not game_started:  # Game needs to be started first
        await ctx.send("Start the game first with **%start_game**")
    elif roles_assigned:  # Roles should not yet be assigned
        await ctx.send("Too late to join the game!")
    elif len(players) >= 10:  # The lobby can not have more than 10 players
        await ctx.send("Lobby is full")
    elif ctx.author in players:  # A player can not join twice
        await ctx.send("You have already joined the lobby!")
    else:
        players.append(ctx.author)
        await ctx.send('{0} has joined the lobby!'.format(ctx.author))


@bot.command()
async def scoreboard(ctx):
    user = ctx.message.author.name
    ref = db.reference(f"/")
    score = ref.get(user)
    for use in score[0]:
        await ctx.send('{0} has {1} wins out of {2} games.'.format(use, score[0][use]["Wins"], score[0][use]["Games"]))


@bot.command()
async def update_score(ctx, s: int):
    if type(s) == int:
        user = ctx.message.author.name
        ref = db.reference(f"/")
        ref.update({
            user: {
                "Score": s
            }
        })
    else:
        await ctx.send('Try again but with an int')


@bot.command()
async def get_score(ctx):
    user = ctx.message.author.name
    ref = db.reference(f"/")
    score = ref.get(user)
    await ctx.send('{0}s score is {1}.'.format(user, score[0][user]["Score"]))


@bot.command()
async def chooseCard(ctx, role: discord.Role):
    global members, gameHand, presidentHasChosen, round_ended  # members is a list that holds each user in the discord server.
    # gameHand holds the hand the president and chancellor have.
    global members, gameHand, presidentHasChosen  # members is a list that holds each user in the discord server.
    global enactedPolicies  # gameHand holds the hand the president and chancellor have.
    # presidentHasChosen is a bool flag which ensures the choseCard command isn't run before sendHand.
    if (presidentHasChosen):
        members = [m for m in ctx.guild.members if
                   role in m.roles]  # Verify the inputted role exists within the servers roles.
        for m in members:
            try:
                await m.send(gameHand)  # Send msg to all discord users within the server that have the inputted roles.
                for card in gameHand:
                    if card == "Separatist":
                        await m.send(file=discord.File('graphics/separatist_article.png'))
                    else:
                        await m.send(file=discord.File('graphics/loyalist_article.png'))
                await m.send(
                    "You're the Chancellor, chose which policy you would like to remove, the remaining policy will be enacted! (0 or 1)")
                message_response = await bot.wait_for('message', check=lambda
                    m: m.author == ctx.author)  # Get card to remove from user.
                cardToRemove = message_response.content

                if cardToRemove == "0":
                    gameHand.pop(0)  # Remove first card in hand, second card will be the enacted policy.
                elif cardToRemove == "1":
                    gameHand.pop(1)  # Remove second card in hand, first card will be the enacted policy.
                else:  # If the user entered an invalid character.
                    await m.send('Invalid input! Run the <%chooseCard Chancellor> command again.')
                    return

                print(gameHand)  # Debugging statement to ensure task test passes.

                print(f":white_check_mark: Message sent to {m}")
            except:
                print(f":x: No DM could be sent to {m}")
        print("Done!")

        # round can end now
        await ctx.send("The round is over. President must end the round with **%next_round**")
        round_ended = True

        newPolicy = gameHand[0]  # Define the new policy to be enacted and display to all players.
        presidentHasChosen = False  # Update presidentHasChosen flag.
        enactedPolicies.append(
            newPolicy)  # Push the newly enacted policy to the enactedPolicies array to keep track of policies.
        verifyWin = checkPolicies(enactedPolicies, '')  # Ensure no policy counts have reached 5.

        await m.send('You succesfully removed card #' + cardToRemove + ' from the hand!')
        await ctx.send("The Chancellor has chosen to enact a new " + newPolicy + " policy!")
        await ctx.send(generatePolicyString(enactedPolicies))
        president_role = discord.utils.find(lambda p: p.name == "President", ctx.guild.roles)
        president = discord.utils.find(lambda p: president_role in p.roles, ctx.guild.members)
        president_dm = await president.create_dm()
        print("President is {}".format(president.name))

        if newPolicy == "Separatist":
            policy_count = enactedPolicies.count('Separatist')
            print(policy_count)
            if 1 < policy_count <= 3:  # President can discover a member's party membership
                await president_dm.send("You may now reveal a player's party membership to yourself. Type the the index of the player to have their identity revealed.")
                await president_dm.send("Indexes start from 0 from the first player listed. **{}**".format(", ".join([player.name for player in players])))
                await ctx.send("The President may now discover a player's party membership for themself.")
                message_response = await bot.wait_for('message', check=lambda
                    x: x.author == president and int(x.content) < len(players))
                index = int(message_response.content)
                if players[index] in loyalist:
                    await president_dm.send("{}'s party membership is **{}**!".format(players[index], "Loyalist"))
                else:
                    await president_dm.send("{}'s party membership is **{}**!".format(players[index], "Separatist"))
            elif 3 < policy_count < 6:  # President kills a player
                await president_dm.send(
                    "You may now kill a player that is currently not Chancellor or President. Type the the index of the player to kill.")
                await president_dm.send("Indexes start from 0 from the first player listed. {}".format(", ".join([player.name for player in players])))
                await ctx.send("The President may now kill a player.")
                message_response = await bot.wait_for('message', check=lambda
                    x: x.author == president and int(x.content) < len(players) and players[int(x.content)] != president and players[int(x.content)] != ctx.author)
                index = int(message_response.content)
                await ctx.send(
                    "{}'s has killed **{}**!".format(president.name, (players[index]).name))
                killed_player = players.pop(index)
                killed_dm = await killed_player.create_dm()
                await killed_dm.send("You have been killed, you may no longer participate in the game.")

        if (verifyWin == 1):
            await ctx.send("The Loyalists have succesfully enacted 5 policies! They are the winners!")
            await ctx.send("Loyalist Members: " + generateWinnerList(ctx, "Loyalist"))
            await end_game(ctx)
        elif (verifyWin == 2):
            await ctx.send("The Separatists have succesfully enacted 5 policies! They are the winners!")
            await ctx.send("Separatist Members: " + generateWinnerList(ctx, "Separatist"))
            await end_game(ctx)
    else:
        await ctx.send('The choseHand command cannot be run until after the sendHand command.')


@bot.command()
async def sendHand(ctx, role: discord.Role):
    global members, gameHand, presidentHasChosen, round_ended  # members is a list that holds each user in the discord server.
    # gameHand holds the hand the president and chancellor have.
    # presidentHasChosen is a bool flag which ensures the choseCard command isn't run before sendHand.
    gameHand = random.choices(policyCards, k=3)  # Send three random policy cards to server.
    members = [m for m in ctx.guild.members if
               role in m.roles]  # Verify the inputted role exists within the servers roles.
    # This command can only be called after the chancellor has been elected
    if not chancellor_elected:
        await ctx.send("A chancellor was not yet elected")
        return

    if round_ended:
        await ctx.send("The round is over. President must end the round with **%next_round**")
        return

    if round_ended:
        await ctx.send("The round is over. President must end the round with **%next_round**")
        return

    gameHand = random.choices(policyCards, k=3)  # Send three random policy cards to server.
    members = [m for m in ctx.guild.members if
               role in m.roles]  # Verify the inputted role exists within the servers roles.
    for m in members:
        try:
            await m.send(gameHand)  # Send msg to all discord users within the server that have the inputted roles.
            for card in gameHand:
                if card == "Separatist":
                    await m.send(file=discord.File('graphics/separatist_article.png'))
                else:
                    await m.send(file=discord.File('graphics/loyalist_article.png'))
            await m.send('Choose a single card to remove from the list. Type 0, 1, or 2. This card will be removed.')
            message_response = await bot.wait_for('message', check=lambda
                m: m.author == ctx.author)  # Get card to remove from user.
            cardToRemove = message_response.content

            if (cardToRemove == "0"):
                gameHand.pop(0)  # Remove first card from the hand.
            elif (cardToRemove == "1"):
                gameHand.pop(1)  # Remove second card from the hand.
            elif (cardToRemove == "2"):
                gameHand.pop(2)  # Remove third card from the hand.
            else:  # If the user entered an invalid character.
                await m.send('Invalid input! Run the <%sendHand President> command again.')
                return

            print(gameHand)  # Debugging statement to ensure task test passes.

            print(f":white_check_mark: Message sent to {m}")
        except:
            print(f":x: No DM could be sent to {m}")
    print("Done!")

    presidentHasChosen = True  # Update presidentHasChosen flag.
    await m.send('You succesfully removed card #' + cardToRemove + ' from the hand!')
    await ctx.send(
        "President has removed card. Chancellor should now run the <%chooseCard Chancellor> command.")  # Notify players the President has removed the first card.


@bot.command()
@commands.has_permissions(administrator=True)
async def assign_roles(ctx):
    if game_started:
        global players, roles_assigned, palpatine, separatist, loyalist, round_counter, election_tracker
        copy = players.copy()

        if roles_assigned:
            ctx.send("roles are already assigned")
            return

        num_separtist = 1
        if len(players) > 8:
            num_separtist = 3
        elif len(players) > 6:
            num_separtist = 2

        palpatine = players.pop(random.randrange(len(players)))  # removes one person from list to make palpatine

        for i in range(num_separtist):
            separatist.append(
                players.pop(random.randrange(len(players))))  # is fine, never gonna test for more than 6 players
        loyalist = players  # Remaining players are loyalist

        # TODO for Andrew --------------------------------
        palpatine_dm = await palpatine.create_dm()  # creates dm channel for palpatine
        await palpatine_dm.send("You are palpatine!")  # sends palpatine the message
        await palpatine_dm.send(file=discord.File('graphics/palpatine_role.png'))

        for sep in separatist:
            separatist_dm = await sep.create_dm()  # creates dm channel for seperatists
            await separatist_dm.send("You are a seperatist!")  # sends separatist the message
            await separatist_dm.send(file=discord.File('graphics/separatist_role.png'))
            for other in separatist:
                if other != sep:
                    await separatist_dm.send("{} is a Separatist".format(other.name))
            await separatist_dm.send("{} is Palpatine".format(palpatine.name))

        for loyalist in players:  # remainder of players are loyalists
            loyalist_dm = await loyalist.create_dm()  # creates loyalist dms
            await loyalist_dm.send("You are a loyalist!")  # sends loyalists msgs
            await loyalist_dm.send(file=discord.File('graphics/loyalist_role.png'))
        roles_assigned = True
        players = copy

        # start the first round and elect the first president
        round_counter = 1
        president = discord.utils.get(ctx.guild.roles, name="President")
        first_pres = random.choice(players)
        await first_pres.add_roles(president)
        await ctx.send("The game has started!")
        await ctx.send("{} is now the president".format(first_pres.name))
        await ctx.send("President must now elect the chancellor by calling **%elect [@user]**")

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
@commands.has_role("President")
async def next_round(ctx):
    global round_ended, chancellor_elected

    if not game_started:
        await ctx.send("Start the game first with **%start_game**")
        return
    if not roles_assigned:
        await ctx.send("roles have not been assigned yet")
        return
    if not round_ended:
        await ctx.send("Round has not ended yet")
        return

    global round_counter
    round_counter += 1
    await ctx.send("Now initiating round {}!".format(round_counter))

    # remove all players of president, chancellor, and voter role just in case
    president = discord.utils.get(ctx.guild.roles, name="President")
    chancellor = discord.utils.get(ctx.guild.roles, name="Chancellor")
    voter = discord.utils.get(ctx.guild.roles, name="Voter")
    for user in players:
        if president in user.roles:
            await user.remove_roles(president)
        if chancellor in user.roles:
            await user.remove_roles(chancellor)
        if voter in user.roles:
            await user.remove_roles(voter)

    # reset Flags
    chancellor_elected = False
    round_ended = False

    # go to next president
    curr_idx = players.index(ctx.author)
    max_idx = len(players) - 1
    if curr_idx == max_idx:
        curr_idx = 0
    else:
        curr_idx += 1
    next_president = players[curr_idx]
    await next_president.add_roles(president)
    await ctx.send("{} is the next president".format(next_president.name))
    await ctx.send("President must now elect the chancellor by calling **%elect [@user]**")


@bot.command()
async def elect(ctx, member: discord.Member):
    global chancellor_elected, round_ended, players, enactedPolicies, election_tracker

    chancellor = discord.utils.find(lambda x: x.name == 'Chancellor', ctx.message.guild.roles)
    president = discord.utils.find(lambda x: x.name == 'President', ctx.message.guild.roles)

    if not roles_assigned:
        await ctx.send("roles have not been assigned yet")
        return
    if round_ended:
        await ctx.send("The round is over. President must end the round with **%next_round**")
        return

    # Do one quick loop to check that a chancellor has not been elected yet
    for user in ctx.guild.members:
        if not user.bot:
            if chancellor in user.roles:
                await ctx.send("A Chancellor has already been elected")
                return

    await member.add_roles(chancellor)

    await ctx.send("{} has been nominated as chancellor".format(member.name))

    msg = await ctx.send(
        "Vote A or B! You have 10 seconds! \n If you put more than 1 reaction, your left-most reaction will be taken.")
    await msg.add_reaction('\U0001F170')  # A emote
    await msg.add_reaction('\U0001F171')  # B emote
    await asyncio.sleep(10)
    a = 0
    b = 0

    react_msg = discord.utils.get(bot.cached_messages, id=msg.id)
    reacted = []
    for r in react_msg.reactions:
        if r.emoji == '\U0001F170':  # if it is the A reaction emote
            a += r.count  # increment amount of reactions of A emote
        elif r.emoji == '\U0001F171':  # if it is the B reaction emote
            b += r.count  # increment amount of reactions of B emote
        async for user in r.users():
            reacted.append(user)
            if reacted.count(user) > 1 or user.bot:
                if r.emoji == '\U0001F170':
                    a -= 1
                elif r.emoji == '\U0001F171':
                    b -= 1
    if a < 0:
        a = 0
    if b < 0:
        b = 0
    if a > b:
        await ctx.send("A wins with {} votes, B had {} votes.".format(a, b))
        await ctx.send("President must now call **%sendHand President** to draw cards")
        election_tracker += 1
        await ctx.send("Election Success Tracker is now **{}**!".format(election_tracker))
        chancellor_elected = True
        if election_tracker == 3:
            new_policy = random.choice(policyCards)
            print(new_policy)
            enactedPolicies.append(new_policy)
            await ctx.send("The election tracker has hit 3, the top policy will now be enacted!")
            election_tracker = 0
            policy_str = generatePolicyString(enactedPolicies)
            await ctx.send(policy_str)
    elif b > a:
        await ctx.send("B wins with {} votes, A had {} votes.".format(b, a))
        await ctx.send("The round is over. President must end the round with **%next_round**")
        round_ended = True
        election_tracker = 0
    elif a == b:
        await ctx.send("There is a tie with both A and B receiving {} votes.".format(a))
        await ctx.send("The round is over. President must end the round with **%next_round**")
        round_ended = True
        election_tracker = 0


def checkPalpatine(member):  # Function to detect if a given player is the Palpatine or not.
    # Will return true if the player passed into the function is the Palpatine and false if not.

    global palpatine  # Holds whoever the Palpatine was each game. Assigned in the assign_roles() function.

    if (palpatine == member):  # Determine if the Discord user passed into checkPalpatine() is the game's Palpatine.
        return True
    else:
        return False


def generatePolicyString(array_policies):  # Compute the number of each policy and generate output string.
    loyalistCount = str(array_policies.count('Loyalist'))
    separatistCount = str(array_policies.count('Separatist'))

    policyString = 'Currently enacted Loyalist policies: ' + loyalistCount + '   |   Currently enacted Separatist policies: ' + separatistCount

    return policyString


def checkPolicies(array_policies, member):
    loyalistCount = array_policies.count('Loyalist')
    separatistCount = array_policies.count('Separatist')

    if (separatistCount > 2 and checkPalpatine(
            member) == True):  # When the Separatist policy count is 3 or greater and the Palpatine is the chancellor, they have won the game.
        return 0
    elif (loyalistCount == 5):  # When the Loyalist policies hit 5, they have won the game.
        return 1
    elif (separatistCount == 5):  # When the Separatist policies hit 5, they have won the game.
        return 2
    else:
        return -1


def generatePolicyString(array_policies):  # Compute the number of each policy and generate output string.
    loyalistCount = str(array_policies.count('Loyalist'))
    separatistCount = str(array_policies.count('Separatist'))

    policyString = 'Currently enacted Loyalist policies: ' + loyalistCount + '   |   Currently enacted Separatist policies: ' + separatistCount

    return policyString


def generateWinnerList(ctx, winningRole):
    winners = ''

    user = ctx.message.author.name
    ref = db.reference(f"/")
    score = ref.get(user)
    global palpatine, separatist, loyalist
    victors = [palpatine] + separatist
    if winningRole == "Loyalist":
        victors = loyalist

    for m in victors:
        winners += (m.name + ', ')

    for player in players:
        if player in victors:
            ref.update({
                player.name: {
                    "Games": score[0][player.name]["Games"] + 1,
                    "Wins": score[0][player.name]["Wins"] + 1
                }
            })
        else:
            ref.update({
                player.name: {
                    "Games": score[0][player.name]["Games"] + 1,
                    "Wins": score[0][player.name]["Wins"]
                }
            })
    return winners


bot.run(open("token.txt", "r").readline())  # Starts the bot
