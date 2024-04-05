import os
import platform
import settings

import discord
from discord import app_commands
from discord.ext import commands

import wavelink


class Voxar(commands.Bot):
    def __init__(self) -> None:
        logger = settings.setup_logger()
        intents = discord.Intents.all()

        super().__init__(command_prefix=".", intents=intents)
        self.logger = logger

    async def on_ready(self) -> None:
        await self.change_status()

    async def setup_hook(self) -> None:
        self.logger.info(f"OS: {platform.system()} {platform.release()}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Discord.py version: {discord.__version__}")
        self.logger.info(f"Name: {self.user.name}")
        self.logger.info(f"ID: {self.user.id}")
        self.logger.info("-----------------------------------------------")
        self.logger.info("Loading cogs...")
        await self.load_cogs()
        self.logger.info("-----------------------------------------------")
        self.logger.info("Loading wavelink...")
        nodes = [wavelink.Node(uri="http://127.0.0.1:2333", password=settings.WAVELINK_PASSWORD)]
        await wavelink.Pool.connect(nodes=nodes, client=self)
        self.logger.info("------------------ BOT READY ------------------")

    @staticmethod
    async def change_status() -> None:
        activity = discord.Activity(type=discord.ActivityType.listening, name="Void's Whisper")
        await bot.change_presence(activity=activity)

    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        self.logger.info(f"Wavelink Node connected: {payload.node!r} | Resumed: {payload.resumed}")

    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command) -> None:
        self.logger.info(f"User {interaction.user} used command {command.name} in guild {interaction.guild_id}")

    async def load_cogs(self) -> None:
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                cog_name = file[:-3]
                try:
                    await self.load_extension(f"cogs.{cog_name}")
                    self.logger.info(f"Loaded cog '{cog_name}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(f"Failed to load cog {cog_name}\n{exception}")


bot = Voxar()
bot.run(settings.DISCORD_TOKEN, log_handler=None)
