import logging
import traceback
from typing import Optional, Union
import torch
from chatbot import JazzyChatbot
import discord
import os
from dotenv import load_dotenv
from config import Config

load_dotenv()


class JazzyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chatbot = JazzyChatbot()
        self.cmds = {
            "!jhelp": {
                "func": self.help_cmd,
                "desc": "Prints all commands and info",
            },
            "!jreset": {
                "func": self.reset_cmd,
                "desc": "Clears the conversation history in channel where command was sent, and sets jazzy cat back to his silly self.",
            },
            "!jcurrent": {
                "func": self.get_curr_context_cmd,
                "desc": "Returns current context that the jazzy cat is following.",
            },
            "!jserious": {
                "func": self.serious_mode_cmd,
                "desc": "Makes the jazzy cat be more serious in his answers (e.g. change context to assistant prompt). Clears the conversation history",
            },
            "!jchange": {
                "func": self.change_context_cmd,
                "desc": "Manipulates the jazzy cat into talking as something else (e.g. change the context). Usage: `!jchange <new_context>`",
            },
            "!jlogs": {
                "func": self.get_logs_cmd,
                "desc": "Get debug logs",
            },
        }
        self.has_greeted = False

    async def on_ready(self):
        if self.has_greeted:
            return
        self.has_greeted = True
        print(f"{self.user} has connected to the discord bois")
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
            msg = message.clean_content
            # parse messages for any commands
            for cmd in self.cmds:
                if msg.startswith(cmd):
                    await self.cmds[cmd]["func"](message)
                    return

            convo_id = self.get_convo_id(message)
            try:
                # add message, then generate response based on entire convo so far
                self.chatbot.add_message_to_convo(
                    convo_id, msg, message.author.global_name
                )
                # resp = "i am wip, i go to sleep"
                resp = self.chatbot.respond_to_convo(convo_id)
                if resp is not None:
                    # ensure sent messages are not over 2000 (discord limit)
                    while len(resp) > 0:
                        await message.channel.send(resp[:2000])
                        resp = resp[2000:]
            except Exception as e:
                await message.channel.send("i'm feelin a lil sick, imma go afk now")
                raise e

    async def help_cmd(self, message: discord.Message):
        await message.channel.send(embed=self.create_help_embed(message.author))

    async def reset_cmd(self, message: discord.Message):
        convo_id = self.get_convo_id(message)
        self.chatbot.clear_convo(convo_id)
        curr_context = self.chatbot.get_convo_context(convo_id)
        await message.channel.send(
            embed=self.create_embed(
                title="Resetted the jazzy cat",
                description=f"ya boi is fresh now",
                author=message.author,
            )
        )

    async def get_curr_context_cmd(self, message: discord.Message):
        convo_id = self.get_convo_id(message)
        curr_context = self.chatbot.get_convo_context(convo_id)
        await message.channel.send(
            embed=self.create_embed(
                title="Current context",
                description=curr_context,
                author=message.author,
            )
        )

    async def serious_mode_cmd(self, message: discord.Message):
        convo_id = self.get_convo_id(message)
        self.chatbot.clear_convo(convo_id)

        self.chatbot.create_new_convo(convo_id, context=Config.serious_context)
        await message.channel.send(
            "the jazzy cat is serious now",
            embed=self.create_embed(
                title="Serious mode activated",
                description=f"he is now a certified AI assistant",
                author=message.author,
            ),
        )

    async def change_context_cmd(self, message: discord.Message):
        convo_id = self.get_convo_id(message)
        msg = message.clean_content
        context = msg[msg.find("!jchange") + len("!jchange") :].strip()

        self.chatbot.clear_convo(convo_id)
        self.chatbot.create_new_convo(convo_id, context=context)
        await message.channel.send(
            embed=self.create_embed(
                title="Changed jazzy cat's context",
                description=f"{context}",
                author=message.author,
            )
        )

    def get_convo_id(self, message: discord.Message) -> str:
        return f"{message.guild.id}_{message.channel.id}"

    async def get_logs_cmd(self, message: discord.Message):
        if os.path.isfile(Config.log_file):
            with open(Config.log_file, "r") as f:
                await message.channel.send(
                    embed=self.create_embed(
                        title="jazzy cat's logs",
                        description="attached as a file",
                        author=message.author,
                    ),
                    file=discord.File(f),
                )
                return
        await message.channel.send(
            embed=self.create_embed(
                title="jazzy cat's logs",
                description=f"lmao nonexistent",
                author=message.author,
            )
        )

    async def send_cmd_error(self, message: discord.Message, cmd: str):
        await message.channel.send(
            embed=self.create_embed(
                title="Invalid usage",
                description=self.cmds[cmd]["description"],
                author=message.author,
            )
        )

    def create_help_embed(
        self, author: Optional[Union[discord.User, discord.Member]] = None
    ):
        return self.create_embed(
            title="All Commands",
            description="\n".join(
                [f"⦁ `{cmd}`: {val['desc']}" for cmd, val in self.cmds.items()]
            ),
            author=author if author else self.user,
        )

    def create_embed(
        self,
        title: str,
        description: str,
        author: Optional[Union[discord.User, discord.Member]] = None,
    ):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.light_embed(),
        )
        if author:
            embed.set_author(name=author.display_name, icon_url=author.avatar.url)
        return embed


if __name__ == "__main__":
    print("we startin")
    print("has cuda", torch.cuda.is_available())
    print("cuda version", torch.version.cuda)
    print("example tensor", torch.tensor([1, 2, 3]).cuda())

    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    client = JazzyClient(intents=intents)
    token = os.getenv("DISCORD_TOKEN")
    handler = logging.FileHandler(filename=Config.log_file, encoding="utf-8", mode="w")

    client.run(token, log_handler=handler, log_level=logging.DEBUG, root_logger=True)
