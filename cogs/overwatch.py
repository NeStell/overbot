import secrets

import discord
from discord.ext import commands

from utils.scrape import get_overwatch_news, get_overwatch_status
from classes.converters import MemeCategory


class Overwatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def format_overwatch_status(status):
        if status.lower() == "no problems at overwatch":
            return (f"<:online:648186001361076243> {status}", discord.Color.green())
        return (f"<:dnd:648185968209428490> {status}", discord.Color.red())

    async def get_meme(self, category):
        url = f"https://www.reddit.com/r/Overwatch_Memes/{category}.json"
        async with self.bot.session.get(url) as r:
            memes = await r.json()
        # excluding .mp4 and files from other domains
        memes = [
            meme
            for meme in memes["data"]["children"]
            if not meme["data"]["secure_media"]
            or not meme["data"]["is_reddit_media_domain"]
        ]
        return secrets.choice(memes)

    def embed_meme(self, ctx, meme):
        embed = discord.Embed(color=0xFF5700)
        embed.title = meme["data"]["title"]
        embed.url = f'https://reddit.com/{meme["data"]["permalink"]}'
        embed.set_image(url=meme["data"]["url"])
        embed.set_footer(
            text=meme["data"]["subreddit_name_prefixed"],
            icon_url=self.bot.config.reddit_logo,
        )
        return embed

    @commands.command()
    @commands.cooldown(1, 60.0, commands.BucketType.member)
    async def status(self, ctx):
        """Returns the current Overwatch servers status."""
        embed = discord.Embed()
        embed.title = "Status"
        embed.url = self.bot.config.overwatch["status"]
        embed.timestamp = self.bot.timestamp
        embed.set_footer(text="downdetector.com")

        try:
            overwatch = await get_overwatch_status()
        except Exception:
            embed.description = (
                f"[Overwatch Servers Status]({self.bot.config.overwatch['status']})"
            )

        status, color = self.format_overwatch_status(str(overwatch).strip())
        embed.color = color
        embed.add_field(name="Overwatch", value=status)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 30.0, commands.BucketType.member)
    async def news(self, ctx, amount: int = None):
        """Returns the latest Overwatch news.

        `[amount]` - The amount of news to return. Defaults to 4.

        You can use this command once every 30 seconds.
        """
        async with ctx.typing():
            pages = []
            amount = amount or 4

            try:
                titles, links, imgs, dates = await get_overwatch_news(abs(amount))
            except Exception:
                embed = discord.Embed(color=self.bot.color)
                embed.title = "Latest Overwatch News"
                embed.description = f"[Click here]({self.bot.config.overwatch['news']})"
                await ctx.send(embed=embed)

            for i, (title, link, img, date) in enumerate(
                zip(titles, links, imgs, dates), start=1
            ):
                embed = discord.Embed()
                embed.title = title
                embed.url = link
                embed.set_author(name="Blizzard Entertainment")
                embed.set_image(url=f"https:{img}")
                embed.set_footer(text=f"News {i}/{len(titles)} • {date}")
                pages.append(embed)

            await self.bot.paginator.Paginator(pages=pages).start(ctx)

    @commands.command()
    @commands.cooldown(1, 5.0, commands.BucketType.member)
    async def patch(self, ctx):
        """Returns patch notes links."""
        embed = discord.Embed(color=self.bot.color)
        embed.title = "Overwatch Patch Notes"
        embed.add_field(
            name="Live",
            value="[Click here to view **live** patch notes]"
            f"({self.bot.config.overwatch['patch'].format('live')})",
            inline=False,
        )
        embed.add_field(
            name="Ptr",
            value="[Click here to view **ptr** patch notes]"
            f"({self.bot.config.overwatch['patch'].format('ptr')})",
            inline=False,
        )
        embed.add_field(
            name="Experimental",
            value="[Click here to view **experimental** patch notes]"
            f"({self.bot.config.overwatch['patch'].format('experimental')})",
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3.0, commands.BucketType.member)
    async def meme(self, ctx, category: MemeCategory = "hot"):
        """Returns a random Overwatch meme.

        `[category]` - The category to get a random meme from.

        Categories
        - Hot
        - New
        - Top
        - Rising

        Defaults to `Hot`.

        All memes are taken from the subreddit r/Overwatch_Memes.
        """
        try:
            meme = await self.get_meme(category)
            embed = self.embed_meme(ctx, meme)
        except Exception as e:
            await ctx.send(embed=self.bot.embed_exception(e))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Overwatch(bot))
