
import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


class DiscordInterface(object):
    def __init__(self, token):
        self.client = client
        client.app = self

    def run(self):
        client.run()


