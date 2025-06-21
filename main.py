from client import Client
from dotenv import dotenv_values

TOKEN = dotenv_values()["TOKEN"]
CHANNEL_NAME = dotenv_values()["CHANNEL"]
client = Client(channelName=CHANNEL_NAME)
client.run(TOKEN)