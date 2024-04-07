import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime
from typing import cast
import wavelink


class PlayingButtons(discord.ui.View):
    def __init__(self, message=None):
        super().__init__(timeout=None)
        self.repeat_value = False
        self.paused = False
        self.message = message

    @discord.ui.button(label="Repeat", style=discord.ButtonStyle.gray, emoji="<:repeat:1223780536393404486>")
    async def repeat_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.repeat_value = not self.repeat_value
        button.style = discord.ButtonStyle.grey if self.repeat_value is False else discord.ButtonStyle.blurple
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray, emoji="<:back:1223780528759636090>")
    async def back_button(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.gray, emoji="<:pause:1223780532991688737>")
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return

        self.paused = not self.paused

        button.label = "Pause" if self.paused is False else "Resume"
        button.emoji = "<:pause:1223780532991688737>" if self.paused is False else "<:play:1223780534837182557>"
        button.style = discord.ButtonStyle.grey if self.paused is False else discord.ButtonStyle.red

        await player.pause(not player.paused)

        if self.message and self.paused:
            new_embed = create_main_embed(player.current, player)
            await self.message.edit(embed=new_embed, view=self)

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

    beginning_empty, beginning_filled = "<:b1:1225944746573303879>", "<:b2:1225944748121133117>"
    middle_empty, middle_filled = "<:m1:1225944752395124828>", "<:m3:1225944755981258875>"
    middle_half_filled = "<:m2:1225944753816862812>"
    end_empty, end_filled = "<:e1:1225944749672890428>", "<:e2:1225944750771671123>"

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


def create_main_embed(track: wavelink.Playable, player: wavelink.player) -> discord.Embed:
    username = track.extras.username
    avatar_url = track.extras.avatar

    current_time = f"{player.position // 60000}:{(player.position // 1000) % 60:02d}"
    total_time = f"{track.length // 60000}:{(track.length // 1000) % 60:02d}"
    progress_bar = create_progress_bar(player.position, track.length)

    embed = discord.Embed(title=track.title,
                          description=f"{current_time} {progress_bar} {total_time}",
                          colour=0x2b2d31,
                          timestamp=datetime.now())
    embed.set_author(name=f"♪ Now Playing │ {track.author}",
                     url=track.uri)
    embed.set_thumbnail(url=track.artwork)
    embed.set_footer(text=f"Added by {username}", icon_url=avatar_url)

    return embed


class Music(commands.Cog, name="music"):
    def __init__(self, bot) -> None:
        self.bot = bot


    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        if not payload.player:
            return

        track = payload.track
        embed = create_main_embed(track, payload.player)

        payload.player.channel = self.bot.get_channel(track.extras.channel_id)
        message = await payload.player.channel.send(embed=embed, view=PlayingButtons())

        view = PlayingButtons(message=message)
        await message.edit(view=view)

    @app_commands.guild_only()
    @app_commands.command(name="play", description="Plays music from a link or using search.")
    @app_commands.describe(search='Put a name or paste a link')
    async def play(self, interaction: discord.Interaction, search: str) -> None:
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("Please join a voice channel first before using this command.",
                                                    ephemeral=True)
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            try:
                player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
            except AttributeError:
                await interaction.response.send_message("Failed to connect to the voice channel.",
                                                        ephemeral=True)
                return

        tracks: wavelink.Search = await wavelink.Playable.search(search, source="ytsearch")
        if not tracks:
            await interaction.response.send_message("Could not find any tracks with that query. Please try again.",
                                                    ephemeral=True)
            return

        tracks[0].extras = {
            "channel_id": interaction.channel_id,
            "username": interaction.user.display_name,
            "avatar": interaction.user.display_avatar.url
        }

        # if not player.playing:
        await player.play(tracks[0])

        if player.paused:
            await player.pause(False)

        embed = discord.Embed(description=f"Added **{tracks[0].title}** along with `0` in the queue",
                              colour=0x2b2d31)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Music(bot))
