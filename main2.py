from typing import Optional, Union
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
        self.cmds = {
            "!jhelp": {
                "func": self.help_cmd,
                "desc": "Print all commands and info",
            },
            "!jreset": {
                "func": self.reset_cmd,
                "desc": "Clears the conversation history in channel where command was sent, and sets jazzy cat back to his silly self.",
            },
            "!jhistory": {
                "func": self.get_history_cmd,
                "desc": "Return conversation history (may take a long time to send)",
            },
            "!jserious": {
                "func": self.serious_mode_cmd,
                "desc": "Make the jazzy cat be more serious in his answers. Clears the conversation history",
            },
            "!jchange": {
                "func": self.change_prompt_cmd,
                "desc": "Manipulate the jazzy cat into roleplaying as something else. Usage: `!jchange -r <rolename> -p <initial_prompt>`",
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
            for cmd in self.cmds:
                if msg.startswith(cmd):
                    await self.cmds[msg]["func"](message)
                    return

            convo_id = self.get_convo_id(message)

            try:
                resp = self.chatbot.respond_to_message(
                    convo_id=convo_id, message=msg, author=message.author.display_name
                )
                if resp is not None:
                    # ensure sent messages are not over 2000 (discord limit)
                    while len(resp) > 0:
                        await message.channel.send(resp[:2000])
                        resp = resp[2000:]
            except:
                await message.channel.send("i'm feelin a lil sick, imma go afk now")

    async def help_cmd(self, message: discord.Message):
        await message.channel.send(embed=self.create_help_embed(message.author))

    async def reset_cmd(self, message: discord.Message):
        convo_id = self.get_convo_id(message)
        self.chatbot.clear_convo(convo_id)
        role = Config.convo_template.roles[-1]
        prompt = Config.convo_template.system
        await message.channel.send(
            embed=self.create_embed(
                title="Resetted the jazzy cat",
                description=f"ya boi is fresh now\n⦁ Role: {role}\n⦁ Prompt: {prompt}",
                author=message.author,
            )
        )

    async def get_history_cmd(self, message: discord.Message):
        convo_id = self.get_convo_id(message)
        resp = self.chatbot.get_convo_str(convo_id)
        # ensure sent messages are not over 2000 (discord limit)
        while len(resp) > 0:
            await message.channel.send(resp[:2000])
            resp = resp[2000:]

    async def serious_mode_cmd(self, message: discord.Message):
        convo_id = self.get_convo_id(message)
        self.chatbot.clear_convo(convo_id)
        role = Config.default_convo_template.roles[-1]
        prompt = Config.default_convo_template.system
        self.chatbot.create_new_convo(
            convo_id,
            prompt=prompt,
            chatbot_role=role,
        )
        await message.send(
            "the jazzy cat is serious now",
            embed=self.create_embed(
                title="Serious mode activated",
                description=f"he is now an AI assistant\n⦁ Role: {role}\n⦁ Prompt: {prompt}",
                author=message.author,
            ),
        )

    async def change_prompt_cmd(self, message: discord.Message):
        convo_id = self.get_convo_id(message)
        msg = message.clean_content
        try:
            msg = msg[msg.find("!jchange") + 8 :].strip()
            if not msg.startswith("-r"):
                self.send_cmd_error(message, "!jchange")
            msg = msg[msg.find("-r") + 2].strip()
            role = msg[: msg.find(" ")]
            msg = msg[msg.find(" ") + 1 :].strip()
            if not msg.startswith("-p"):
                self.send_cmd_error(message, "!jchange")
            msg = msg[msg.find("-p") + 2].strip()
            prompt = msg.strip()
            self.chatbot.clear_convo(convo_id)
            self.chatbot.create_new_convo(convo_id, prompt=prompt, chatbot_role=role)
            await message.channel.send(
                embed=self.create_embed(
                    title="Changed jazzy cat role and prompt",
                    description=f"⦁ Role: {role}\n⦁ Prompt: {prompt}",
                    author=message.author,
                )
            )
        except Exception as e:
            await self.send_cmd_error(message, "!jchange")

    async def send_cmd_error(self, message: discord.Message, cmd: str):
        await message.channel.send(
            embed=self.create_embed(
                title="Invalid usage",
                description=self.cmds[cmd]["description"],
                author=message.author,
            )
        )

    def get_convo_id(self, message: discord.Message) -> str:
        return f"{message.guild.id}_{message.channel.id}"

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
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    client = JazzyClient(intents=intents)
    token = os.getenv("DISCORD_TOKEN")
    client.run(token)
