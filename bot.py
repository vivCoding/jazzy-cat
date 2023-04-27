import discord
import os
from dotenv import load_dotenv

load_dotenv()

class JazzyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f'{self.user} has connected to discord bois')
        # send msg to first text channel
        for guild in self.guilds:
            for channel in guild.channels:
                if channel.type == discord.ChannelType.text:
                    await channel.send('the jazzy cat is here bois')
                    break

    async def on_message(self, message: discord.Message):
        if message.author == self.user: return
        await message.channel.send("im a wip, so i schleep")

if __name__ == "__main__":
    intents = discord.Intents.default()
    client = JazzyBot(intents=intents)
    token = os.getenv("DISCORD_TOKEN")
    client.run(token)