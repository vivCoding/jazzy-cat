import discord
import os
from dotenv import load_dotenv

load_dotenv()


class JazzyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f"{self.user} has connected to da discord bois")
        # get all text channels it has access to
        channels = [
            channel
            for channel in self.get_all_channels()
            if channel.type == discord.ChannelType.text
            and channel.permissions_for(channel.guild.me).send_messages
        ]
        # sort by visual position
        channels.sort(key=lambda c: c.position)
        # send message to first channel it has access to
        await channels[0].send("the jazzy cat is here bois")

    async def on_message(self, message: discord.Message):
        # don't respond to itself
        if message.author == self.user:
            return
        await message.channel.send("im a wip, so i schleep")


if __name__ == "__main__":
    intents = discord.Intents.default()
    client = JazzyBot(intents=intents)
    token = os.getenv("DISCORD_TOKEN")
    client.run(token)
