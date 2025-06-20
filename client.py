import discord

class Client(discord.Client):
    games = []
    def __init__(self):
        super().__init__(intents=discord.Intents.all())

    async def getClient(self, uid):
        user = await self.fetch_user(uid)
        return user