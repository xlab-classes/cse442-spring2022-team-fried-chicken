import discord
from discord.ext import commands

intents = discord.Intents.default()  # Intents required to be declared for certain server perms
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='%', help_command=None, intents=intents)  # Creates instance of bots

bot.run('TOKEN_HERE', bot=True)  # Starts the bot
