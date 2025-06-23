import discord
from typing import Literal, TYPE_CHECKING
if TYPE_CHECKING:
    from client import Client

class DuelButton(discord.ui.View):
    
    def __init__(self,
                 client: "Client",
                 receiver: discord.User,
                 sender: discord.User,
                 game: Literal["tictactoe", "reversi"]) -> None:
        super().__init__(timeout=120)
        self.client = client
        self.receiver = receiver
        self.sender = sender
        self.game = game
        self.message = None

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(content="Duel expired.", view=None)
            self.client.duelRequests.discard(self.receiver)
            self.client.duelRequests.discard(self.sender)

    @discord.ui.button(label="Accept Duel", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.receiver.id:
            await interaction.response.send_message("You're not the challenged user!", ephemeral=True)
            return
        
        self.stop()
        self.client.duelRequests.discard(self.receiver)
        self.client.duelRequests.discard(self.sender)
        await interaction.response.edit_message(content=f"{self.receiver.mention} accepted!", view=None)
        await self.client.addGame(self.game, (self.sender, self.receiver), interaction.channel)

    @discord.ui.button(label="Cancel Duel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user not in (self.receiver, self.sender):
            await interaction.response.send_message("This isn't your duel!", ephemeral=True)
            return
        self.stop()
        self.client.duelRequests.discard(self.receiver)
        self.client.duelRequests.discard(self.sender)
        await interaction.response.edit_message(content="Duel cancelled.", view=None)