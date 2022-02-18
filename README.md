# Team Fried Chicken Project Proposal


Team members: Ryan Doohan, Simon Friedland, Alan Diakov, Andrew Brusic

Project Idea
Discord Bot - “Secret Hitler” game clone (Secret Hitler - Wikipedia)

Secret Hitler sees players divided into two teams: the liberals and the fascists, the latter also including the Hitler role. The identity of Hitler is known to all other fascists, while the identities of the fascists are unknown to Hitler in games with at least seven players. The role distribution depends on the number of players in a game session.
-Wikipedia

Motivation
Secret Hitler is a 5-10 person game in which two teams are created. Discord servers are an excellent choice of environment for a game to be hosted, it is on the platform where the bot will be able to host a fun social game that can only be played either in person or on the “Secret Hitler” website. The goal of making this bot is to decrease the hassle of having to meet up in person or having to organize a game on an external website, and still provide users with the same fun experience said the game could provide, all from the comfort of a social media platform used by more than 300 million people.

Description of the proposed solution with the technology stacks to be used
We will be using the Discord Python API (API Reference) to code the functionality of the bot. We will register the bot through the Discord Developer Portal (Discord Developer Portal). To track information about the game (ie: roles, servers, users, etc.), we will be using a database. We will also use a server to host the bot.

End goals for the project (how will the demos look like?)
Our end goal for the project is to successfully run a full game of “Secret Hitler” via our bot. We hope to get some volunteers and/or judges to join the game with us, to help demonstrate to them how the game is played, and that our bot has successfully replicated the functionality of the game. We will have the main presentation focused on the channel in the discord server where the main game is taking place, and after the game is done we will go over some of the things that occurred from a user’s perspective.


Four major milestones to reach the end goals (in line with the Sprint cycles)
Create the discord bot and get it up and running within our group's discord server. The bot should form teams (liberals & fascists) and designate roles for all players.

Layout basic game functionality, add player voting (Ja or Nein), turns, president and chancellor elections, as well as some graphics the bot would post while the game is ongoing.


Finish game functionality, the winners of the game should be announced (whether liberals or fascists), all different policy cards should be implemented, and government powers.


Create a database to track role information and integrate it with the bot, this should also make it capable of being on multiple servers at once. Also, create the server to host the bot.
