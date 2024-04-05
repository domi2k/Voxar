import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime
from pytube import YouTube, Search, Playlist
from pytube.exceptions import VideoUnavailable
import validators


class PlayingButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.repeat_value = False

    @discord.ui.button(label="Repeat", style=discord.ButtonStyle.gray, emoji="<:repeat:1223780536393404486>")
    async def repeat_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.repeat_value = not self.repeat_value
        button.style = discord.ButtonStyle.grey if self.repeat_value is False else discord.ButtonStyle.blurple
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray, emoji="<:back:1223780528759636090>")
    async def back_button(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.gray, emoji="<:pause:1223780532991688737>")
    async def pause_button(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.gray, emoji="<:next:1223780531792252938>")
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Menu", style=discord.ButtonStyle.gray, emoji="<:menu:1223780530252677183>")
    async def menu_button(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(view=self)


def create_progress_bar(current_length: int, total_length: int) -> str:
    progress_ratio = current_length / total_length

    filled_icons = round(progress_ratio * 16)

    beginning_empty, beginning_filled = "<:b1:1225580868702306404>", "<:b2:1225580870266781706>"
    middle_empty, middle_filled = "<:m1:1225580874708549744>", "<:m3:1225580877740773517>"
    middle_half_filled = "<:m2:1225580876050726934>"
    end_empty, end_filled = "<:e1:1225580871797706842>", "<:e2:1225580873336754206>"

    progress_bar = ""
    progress_bar += beginning_filled if filled_icons > 0 else beginning_empty
    filled_icons -= 1

    for _ in range(1, 15):
        if filled_icons > 1:
            progress_bar += middle_filled
            filled_icons -= 1
        elif filled_icons == 1:
            progress_bar += middle_half_filled
            filled_icons -= 1
        else:
            progress_bar += middle_empty

    progress_bar += end_filled if filled_icons == 1 else end_empty

    return progress_bar


def playing_embed(interaction: discord.Interaction, yt) -> discord.embeds.Embed:
    username = interaction.user.display_name
    avatar_url = interaction.user.display_avatar.url

    embed = discord.Embed(title=yt.title,
                          colour=0x2b2d31,
                          timestamp=datetime.now())

    embed.add_field(name="",
                    value="00:00",
                    inline=True)
    embed.add_field(name="",
                    value=create_progress_bar(15, 16),
                    inline=True)
    embed.add_field(name="",
                    value="18:54",
                    inline=True)

    embed.set_thumbnail(url=yt.thumbnail_url)
    embed.set_footer(text=f"Added by {username}", icon_url=avatar_url)

    return embed


class Music(commands.Cog, name="music"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name="play", description="Plays music from a link or using search.")
    @app_commands.describe(search='Put a name or paste a link')
    async def play(self, interaction: discord.Interaction, search: str):
        if validators.url(search.strip()):
            try:
                yt = YouTube(search)
            except VideoUnavailable as e:
                error_embed = discord.Embed(title="Video unavailable.", description=e)
                await interaction.response.send_message(embed=error_embed)
            else:
                embed = playing_embed(interaction, yt)
                await interaction.response.send_message(embed=embed, view=PlayingButtons())
        else:



            await interaction.response.send_message(content="To nie link")


async def setup(bot):
    await bot.add_cog(Music(bot))
