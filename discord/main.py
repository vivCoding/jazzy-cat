import discord
import os
from dotenv import load_dotenv
from config import Config
from vicuna.chatbot import JazzyChatbot

load_dotenv()


class JazzyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chatbot = JazzyChatbot()

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
        channel = message.channel
        async with channel.typing():
            convo_id = f"{message.guild.id}_{message.channel.id}_{message.channel.name}"
            msg = message.clean_content

            res = self.chatbot.respond_to_message(convo_id, msg)
            if res is not None:
                while len(res) > 0:
                    await message.channel.send(res[:2000])
                    res = res[2000:]
        # await message.channel.send("i'm a wip, so i schleep now")


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    client = JazzyClient(intents=intents)
    token = os.getenv("DISCORD_TOKEN")
    client.run(token)
