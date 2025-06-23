
# Tictacbot Discord Bot

A turn based game Discord bot made entirely in Python. Object oriented setup makes it easy to add more games. Optionally it is possible to connect it to MongoDB to store player ELO.

# Basic Setup

1. Create a Discord bot on the Discord developer page.
2. Add a `.env` file to the project root.
3. Paste the bot token into the file like this: `TOKEN=your-token-here` (see an example of a `.env` file below).
4. Run the `main.py` file.
5. Use the /duel command to duel another user
6. Once in game, use chat commands to make moves in the game. Use the /help command with the name of the game to get more info.

# Commands

### Basic bot commands

- /help [topic]: gives a help message about the bot or the selected topic.
- /duel player game: sends a duel request to another player with that specific game

### Commands with database

- /elo [player]: fetches the ELO of a player or the command sender
- /leaderboard game: fetches the top 10 players in a game based on ELO

# Connecting a Database
1. Make sure you have correctly installed MongoDB.
2. Add the entry `MONGO_URI` to your `.env` file with the MongoDB URI leading to your server.
3. Add the entry `DB_NAME` to your `.env` file with the name of the database you want to access on MongoDB.
4. Play a game with another person, and the entries should show up in a collection called `users`.

# All `.env` Values

- TOKEN: stores the Discord bot token
- GUILD: the name of the guild where the bot listens for commands. If not provided, the bot will listen in all guilds.
- CHANNEL: the name of the channel where the bot listens for commands. If not provided, the bot will listen in all channels.
- MONGO_URI: the link to your MongoDB server. If not provided the ELO system will be disabled.
- DB_NAME: the name of the MongoDB database where data will be stored. If not provided the ELO system will be disabled.

### Example `.env` Config

```
TOKEN=your-token-here
GUILD=My Games Group
CHANNEL=games
MONGO_URI=mongodb://localhost:27017/
DB_NAME=players
```

# Included Games

- tictactoe: the classic game with no changes. This game is never ranked, as it is a solved game and is just for fun.
- reversi: a game played on an 8x8 board with flipping tiles. The person with the more tiles in the end wins. If a database is added, this game is ranked.
- snaketactoe: a twist on the classic game. Each piece may only last for 3 rounds max. After another piece is played, the oldest piece will disappear. The age of the pieces is shown on the top right. If a database is added, this game is ranked.

# Adding New Games

TBA