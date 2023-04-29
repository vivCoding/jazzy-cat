import discord
import os
from dotenv import load_dotenv
from vicuna.chatbot import JazzyChatbot

load_dotenv()


class JazzyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chatbot = JazzyChatbot()
        self.cmds = {
            "!jhelp": {
                "func": self.help_cmd,
                "desc": "Print all commands and info",
            },
            "!jclear": {
                "func": self.clear_cmd,
                "desc": "Clears the conversation history in channel where command was sent",
            },
        }

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

        msg = message.clean_content
        if msg in self.cmds:
            await self.cmds[msg]["func"](message)

        # await message.channel.send("i'm a wip, so i schleep now")
        async with message.channel.typing():
            convo_id = self.get_convo_id(message)

            resp = self.chatbot.respond_to_message(convo_id, msg)
            if resp is not None:
                # limit length to 2000
                await message.channel.send(resp[:2000])

    async def help_cmd(self, message: discord.Message):
        async with message.channel.typing():
            msg = "jazzy chat help\n"
            for cmd, val in self.cmds.items():
                msg += f"- {cmd}: {val['desc']}\n"
            await message.channel.send(msg)

    async def clear_cmd(self, message: discord.Message):
        async with message.channel.typing():
            convo_id = self.get_convo_id(message)
            self.chatbot.clear_convo(convo_id)
            await message.channel.send("ya boi is fresh now")

    def get_convo_id(self, message: discord.Message) -> str:
        return f"{message.guild.id}_{message.channel.id}"


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    client = JazzyClient(intents=intents)
    token = os.getenv("DISCORD_TOKEN")
    client.run(token)
