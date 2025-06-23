import discord
from games.tictactoe import TicTacToe
from games.reversi import Reversi
from games.snaketactoe import SnakeTacToe
from games.game import Game

from duelbutton import DuelButton

from typing import Literal, TYPE_CHECKING
if TYPE_CHECKING:
    from database import DataBase

class Client(discord.Client):

    def __init__(self, channelName: str, db: "DataBase"=None):
        super().__init__(intents=discord.Intents.all())
        self.games: list[Game] = []
        self.ratedGames = {"reversi", "snaketactoe"}
        self.duelRequests = set()
        self.channelName = channelName
        self.db = db
        self.tree = discord.app_commands.CommandTree(self)
        self.addEvents()

    async def getClient(self, uid: int) -> discord.User:
        user = await self.fetch_user(uid)
        return user
    
    async def addGame(self,
                g: Literal["tictactoe", "reversi", "snaketactoe"],
                users: tuple[discord.User],
                channel: discord.TextChannel) -> None:
        if g == "tictactoe":
            game: Game = TicTacToe(users)
        elif g == "reversi":
            game: Game = Reversi(users, self.db)
        elif g == "snaketactoe":
            game: Game = SnakeTacToe(users, self.db)
        await channel.send(game.displayInfo())
        self.games.append(game)
    
    def addEvents(self):
        @self.tree.command(
            name="duel",
            description="Initiate a duel against another user."
        )
        async def duel(interaction: discord.Interaction,
                       receiver: discord.Member,
                       game: Literal["tictactoe", "reversi", "snaketactoe"]) -> None:
            """Initiate a duel against another user.

            Parameters
            -----------
            receiver: discord.Member
                The member you want to duel.
            game:
                The game you want to play.
            """

            sender = interaction.user
            if receiver.bot:
                await interaction.response.send_message("You can't duel bots!", ephemeral=True)
                return
            if receiver == sender:
                await interaction.response.send_message("You can't duel yourself!", ephemeral=True)
                return
            if sender in self.duelRequests:
                await interaction.response.send_message("You have a pending duel!", ephemeral=True)
                return
            if receiver in self.duelRequests:
                await interaction.response.send_message(f"{receiver.mention} has a pending duel!", ephemeral=True)
                return
            for game in self.games:
                if sender in game.players:
                    await interaction.response.send_message("You are already in a game!", ephemeral=True)
                    return
                if receiver in game.players:
                    await interaction.response.send_message(f"{receiver.mention} is already in a game!", ephemeral=True)
                    return
                
            if self.db is not None and game in self.ratedGames:
                self.db.initializeUserGame(sender.id, game)
                self.db.initializeUserGame(receiver.id, game)

            view = DuelButton(self, receiver, sender, game)

            if self.db is not None and game in self.ratedGames:
                senderElo = self.db.getUserElo(sender.id, game) or "N/A"
                receiverElo = self.db.getUserElo(receiver.id, game) or "N/A"

                messageContent = (
                    f"{sender.mention} ({senderElo}) challenged "
                    f"{receiver.mention} ({receiverElo}) to a duel in {game}!\n"
                    "They have 2 minutes to accept!"
                )
            else:
                messageContent = (
                    f"{sender.mention} challenged {receiver.mention} to a duel in {game}!\n"
                    "They have 2 minutes to accept!"
                )
            await interaction.response.send_message(messageContent, view=view)
            view.message = await interaction.original_response()
            self.duelRequests.add(sender)
            self.duelRequests.add(receiver)

        @self.tree.command(
                name="elo",
                description="Get the ELO of yourself or a specific player."
        )
        async def elo(interaction: discord.Interaction, player: discord.User=None):
            player = player or interaction.user

            if self.db is None:
                await interaction.response.send_message("Database is not enabled.", ephemeral=True)
                return
            
            ratings = self.db.getUserRatings(player.id)

            if not ratings:
                await interaction.response.send_message(f"{player.display_name} has no Elo ratings yet.", ephemeral=True)
                return
            
            lines = []
            for game, data in ratings.items():
                rating = round(data["rating"])
                lines.append(f"**{game.capitalize()}**: `{rating}`")

            await interaction.response.send_message(
                f"**{player.display_name}**'s Elo Ratings:\n" + "\n".join(lines)
            )

        @self.tree.command(
            name="leaderboard",
            description="Gets the top 10 players in a game."
        )
        async def leaderboard(interaction: discord.Interaction, game: Literal["reversi", "snaketactoe"]):
            if self.db is None:
                await interaction.response.send_message("Database is not enabled.", ephemeral=True)
                return
            
            board = self.db.getLeaderboard(game)

            if not board:
                await interaction.response.send_message(f"No one has played {game} yet.", ephemeral=True)
            
            lines = [f"**Top {len(board)} Players in {game}**"]
            for i, entry in enumerate(board, start=1):
                user = await self.getClient(entry[0])
                rating = entry[1]
                lines.append(f"`#{i:>2}` {user.display_name} — **{rating}**")

            await interaction.response.send_message("\n".join(lines))

        @self.tree.command(
                name="help",
                description="Provides general info or specific info about a topic."
        )
        async def help(interaction: discord.Interaction, topic: Literal["how-to-play", "commands"] | None=None):
            helpMessages = {
                None: f"{self.user.mention} is a Discord Bot for turn based gaming.\n"
                + "It lets users duel each other in various games.\n"
                + "Use this help command to find out more about different topics.",

                "how-to-play": "Guide to starting a match:\n"
                + "```1. Send a duel request with /duel\n"
                + "2. If you got a duel request, accept it.\n"
                + "3. The game board will appear and show who goes first.\n"
                + "4. Type in the game command (not / command) into the chat.\n"
                + "5. If you don't know game commands, refer to the help menu.```",

                "commands": "Bot commands:\n"
                + "```Legend:\n"
                + "/example param: Command \"example\" with required parameter \"param\"\n"
                + "/example [param]: Command \"example\" with optional parameter \"param\"\n\n"
                + "/help [topic]: Provides general info or specific info about a topic.\n"
                + "/duel user game: Send a duel request to that user using that game.\n"
                + "/elo [user]: Get the elo of the user, or you if there's no user.\n"
                + "/leaderboard game: Get the top 10 players for a game.\n\n"

                + "Game specific commands are in the game's help menu.\n```"
            }

            await interaction.response.send_message(helpMessages[topic])

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