import discord
from games.tictactoe import TicTacToe
from games.reversi import Reversi
from games.game import Game

from duelbutton import DuelButton

from typing import Literal

class Client(discord.Client):

    def __init__(self, channelName):
        super().__init__(intents=discord.Intents.all())
        self.games: list[Game] = []
        self.duels = []
        self.channelName = channelName
        self.tree = discord.app_commands.CommandTree(self)
        self.addEvents()

    async def getClient(self, uid: int) -> discord.User:
        user = await self.fetch_user(uid)
        return user
    
    async def addGame(self,
                g: Literal["tictactoe", "reversi"],
                users: tuple[discord.User],
                channel: discord.TextChannel) -> None:
        if g == "tictactoe":
            game: Game = TicTacToe(users)
        elif g == "reversi":
            game: Game = Reversi(users)
        await channel.send(game.displayInfo())
        self.games.append(game)
    
    def addEvents(self):
        @self.tree.command(
            name="duel",
            description="Initiate a duel against another user."
        )
        async def duel(interaction: discord.Interaction,
                       receiver: discord.Member,
                       game: Literal["tictactoe", "reversi"]) -> None:
            """Initiate a duel against another user.

            Parameters
            -----------
            receiver: discord.Member
                The member you want to duel.
            game:
                The game you want to play.
            """

            if receiver.bot:
                await interaction.response.send_message("You can't duel bots!", ephemeral=True)
                return
            if receiver == interaction.user:
                await interaction.response.send_message("You can't duel yourself!", ephemeral=True)
                return
            for game in self.games:
                if interaction.user in game.players:
                    await interaction.response.send_message("You are already in a game!", ephemeral=True)
                    return
                if receiver in game.players:
                    await interaction.response.send_message(f"{receiver.mention} is already in a game!", ephemeral=True)
                    return
            view = DuelButton(self, receiver, interaction.user, game)
            await interaction.response.send_message(
                f"{interaction.user.mention} challenged {receiver.mention} to a duel in {game}!"
               + "\nThey have 3 minutes to accept!", view=view)
            view.message = await interaction.original_response()

        @self.event
        async def on_ready():
            await self.tree.sync()
            print(f"""{self.user} connected to {[g.name for g in self.guilds]}""")

        @self.event    
        async def on_message(message: discord.Message) -> None:
            sender = message.author
            if sender == self.user:
                return
            if message.channel.name != self.channelName:
                return
            if not message.content:
                return
            for game in self.games:
                if sender in game.players:
                    output = game.commands(sender, message.content)
                    if game.gameOver:
                        self.games.remove(game)
                    if output:
                        await message.channel.send(output)