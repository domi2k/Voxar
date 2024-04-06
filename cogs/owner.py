from typing import Literal, Optional

import discord
from discord.ext import commands


class Owner(commands.Cog, name="owner"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object],
                   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync(guild=ctx.guild)

            synced_to = 'globally' if spec is None else 'to the current guild.'
            embed = discord.Embed(title=f"Synced {len(synced)} commands {synced_to}",
                                  color=0x2b2d31)
            await ctx.send(embed=embed)
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        embed = discord.Embed(title=f"Synced the tree to {ret}/{len(guilds)}.",
                              color=0x2b2d31)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, cog: str) -> None:
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            embed = discord.Embed(title=f"Successfully loaded the `{cog}` cog.",
                                  color=0x2b2d31)
        except Exception as e:
            embed = discord.Embed(title=f'Could not load the `{cog}` cog.',
                                  description=e,
                                  color=0x2b2d31)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, cog: str) -> None:
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            embed = discord.Embed(title=f"Successfully unloaded the `{cog}` cog.",
                                  color=0x2b2d31)
        except Exception as e:
            embed = discord.Embed(title=f"Could not unload the `{cog}` cog.",
                                  description=e,
                                  color=0x2b2d31)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, cog: str) -> None:
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            embed = discord.Embed(title=f"Successfully reloaded the `{cog}` cog.",
                                  color=0x2b2d31)
        except Exception as e:
            embed = discord.Embed(title=f"Could not reload the `{cog}` cog.",
                                  description=e,
                                  color=0x2b2d31)
        await ctx.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Owner(bot))
