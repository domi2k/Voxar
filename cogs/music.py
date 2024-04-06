import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime
import validators

from typing import cast
import wavelink


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


# def create_progress_bar(current_length: int, total_length: int) -> str:
#     progress_ratio = current_length / total_length
#
#     filled_icons = round(progress_ratio * 16)
#
#     beginning_empty, beginning_filled = "<:b1:1225944746573303879>", "<:b2:1225944748121133117>"
#     middle_empty, middle_filled = "<:m1:1225944752395124828>", "<:m3:1225944755981258875>"
#     middle_half_filled = "<:m2:1225944753816862812>"
#     end_empty, end_filled = "<:e1:1225944749672890428>", "<:e2:1225944750771671123>"
#
#     progress_bar = ""
#     progress_bar += beginning_filled if filled_icons > 0 else beginning_empty
#     filled_icons -= 1
#
#     for _ in range(1, 15):
#         if filled_icons > 1:
#             progress_bar += middle_filled
#             filled_icons -= 1
#         elif filled_icons == 1:
#             progress_bar += middle_half_filled
#             filled_icons -= 1
#         else:
#             progress_bar += middle_empty
#
#     progress_bar += end_filled if filled_icons == 1 else end_empty
#
#     return progress_bar


# def playing_embed(interaction: discord.Interaction, yt) -> discord.embeds.Embed:
#     username = interaction.user.display_name
#     avatar_url = interaction.user.display_avatar.url
#
#     current_time = "00:00"
#     progress_bar = create_progress_bar(3, 16)
#     total_time = "18:54"
#
#     embed = discord.Embed(title=yt.title,
#                           description=f"{current_time}{progress_bar}{total_time}",
#                           colour=0x2b2d31,
#                           timestamp=datetime.now())
#
#     embed.set_thumbnail(url=yt.thumbnail_url)
#     embed.set_footer(text=f"Added by {username}", icon_url=avatar_url)
#
#     return embed


class Music(commands.Cog, name="music"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            # Handle edge cases...
            return

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track

        embed: discord.Embed = discord.Embed(title="Now Playing")
        embed.description = f"**{track.title}** by `{track.author}`"

        if track.artwork:
            embed.set_image(url=track.artwork)

        if original and original.recommended:
            embed.description += f"\n\n`This track was recommended via {track.source}`"

        if track.album.name:
            embed.add_field(name="Album", value=track.album.name)

        embed.add_field(name="Source", value=track.source)
        embed.add_field(name="Link", value=track.uri)
        if track.preview_url:
            embed.add_field(name="Preview_url", value=track.preview_url)

        payload.player.channel = self.bot.get_channel(track.extras.channel_id)
        await payload.player.channel.send(embed=embed)

    @app_commands.guild_only()
    @app_commands.command(name="play", description="Plays music from a link or using search.")
    @app_commands.describe(search='Put a name or paste a link')
    async def play(self, interaction: discord.Interaction, search: str):
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
        tracks[0].extras = {"channel_id": interaction.channel_id}

        # if not player.playing:
        await player.play(tracks[0])

        # await interaction.response.send_message(embed=embed, view=PlayingButtons())

    @commands.command(aliases=["dc"])
    async def disconnect(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.disconnect()
        await ctx.message.add_reaction("\u2705")


async def setup(bot):
    await bot.add_cog(Music(bot))
