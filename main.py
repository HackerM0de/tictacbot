from games.tictactoe import TicTacToe
from games.reversi import Reversi
from games.game import Game
from client import Client
from dotenv import dotenv_values

TOKEN = dotenv_values()["TOKEN"]

client = Client()

@client.event
async def on_ready():

    print(f'''{client.user} connected to {[g.name for g in client.guilds]}
          (id: {[g.id for g in client.guilds]})''')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.name != 'gayms':
        return
    if not message.content:
        return
    parts = message.content.split()
    sender = message.author
    if parts[0].lower() == 'duel':
        receiver = await client.getClient(parts[1][2:len(parts[1])-1])
        if receiver.bot:
            await message.channel.send("You can't duel bots!")
            return
        for game in client.games:
            if sender in game.players:
                await message.channel.send('You are already in a game!')
                return
            if receiver.mention in game.players:
                await message.channel.send(f'{receiver.mention} is already in a game!')
                return
        game: Game = Reversi((sender, receiver))
        await message.channel.send(game.displayInfo())
        client.games.append(game)
    else:
        for game in client.games:
            if sender in game.players:
                output = game.commands(sender, message.content)
                if output:
                    await message.channel.send(output)
                if game.gameOver:
                    client.games.remove(game)

client.run(TOKEN)