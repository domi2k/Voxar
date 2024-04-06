import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog, name="general"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name="botinfo", description="Information about the bot")
    async def botinfo(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(description="",
                              color=0x2b2d31)
        embed.set_thumbnail(url="")
        embed.set_author(name="Voxar")
        embed.add_field(name="Developer:", value="domi2k", inline=True)
        embed.add_field(name="Last Updated:", value="", inline=True)
        await interaction.response.send_message(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(General(bot))
