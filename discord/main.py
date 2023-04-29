from typing import Optional
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
        # send greeting msg to every connected server
        for guild in self.guilds:
            # get all text channels it has access to in server
            channels = [
                channel
                for channel in guild.channels
                if channel.type == discord.ChannelType.text
                and channel.permissions_for(channel.guild.me).send_messages
            ]
            # sort by visual position
            channels.sort(key=lambda c: c.position)
            # send message to first channel it has access to
            await channels[0].send(
                "the jazzy cat is here bois", embed=self.create_help_embed()
            )

    async def on_message(self, message: discord.Message):
        # don't respond to itself
        if message.author == self.user:
            return

        async with message.channel.typing():
            # await message.channel.send("i'm a wip, so i schleep now")
            msg = message.clean_content
            if msg in self.cmds:
                await self.cmds[msg]["func"](message)
                return

            convo_id = self.get_convo_id(message)

            try:
                resp = self.chatbot.respond_to_message(convo_id, msg)
                if resp is not None:
                    # ensure sent messages are not over 2000 (discord limit)
                    while len(resp) > 0:
                        await message.channel.send(resp[:2000])
                        resp = resp[2000:]
            except:
                await message.channel.send("i'm feelin a lil sick, imma go afk now")

    async def help_cmd(self, message: discord.Message):
        await message.channel.send(embed=self.create_help_embed())

    async def clear_cmd(self, message: discord.Message):
        # await message.channel.send("that's a wip, so i schleep now")
        convo_id = self.get_convo_id(message)
        self.chatbot.clear_convo(convo_id)
        await message.channel.send(
            embed=self.create_embed(
                title="Conversation cleared",
                description="ya boi is fresh now",
                author=message.author,
            )
        )

    def get_convo_id(self, message: discord.Message) -> str:
        return f"{message.guild.id}_{message.channel.id}"

    def create_help_embed(self):
        return self.create_embed(
            title="All Commands",
            description="\n".join(
                [f"⦁ {cmd}: {val['desc']}" for cmd, val in self.cmds.items()]
            ),
            author=self.user,
        )

    def create_embed(
        self,
        title: str,
        description: str,
        author: Optional[discord.Message.author] = None,
    ):
        return discord.Embed(
            title=title,
            description=description,
            color=discord.Color.light_embed(),
            author=author,
        )


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    client = JazzyClient(intents=intents)
    token = os.getenv("DISCORD_TOKEN")
    client.run(token)
