
import discord

import threading
import asyncio

# asyncio.run_coroutine_threadsafe(coro, loop)

client = discord.Client()

@client.event
async def on_ready():
    print('discord - logged in as {0.user}'.format(client))
    client.app.post_init()

class DiscordInterface(object):
    def __init__(self, token):
        self.client = client
        client.app = self
        self.token = token

        self.thread = threading.Thread(target=self.run_threaded)
        self.thread.daemon = True

        self.channel_ids = { "clip": 784896658408341584}

    def post_init(self):
        pass

    def send_clip(self, message):
        coro = self.send_message_async("clip", message, 2.0)
        asyncio.run_coroutine_threadsafe(coro, client.loop)       

    def send_message(self, target, message):
        coro = self.send_message_async(target, message)
        asyncio.run_coroutine_threadsafe(coro, client.loop)

    def run_threaded(self):
        client.run( self.token )

    def run(self):
        self.thread.start()

    async def send_message_async(self, target, message, delay=0):

        if delay != 0:
            print("discord - send_message_async - delay {}".format(delay) )
            await asyncio.sleep(delay)
        channel = self.client.get_channel( self.channel_ids[target] )
        if channel is None:
            print("discord - send_message_async - cannot resolve channel")

        await channel.send(message)




