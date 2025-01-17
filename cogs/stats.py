from discord.ext import commands

from utils.player import Player, PlayerException
from utils.request import Request, RequestError
from classes.converters import Hero, Platform


class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["rank", "sr"])
    @commands.cooldown(1, 5.0, commands.BucketType.member)
    async def rating(self, ctx, platform: Platform, *, username):
        """Returns player ranks.

        `<platform>` - The platform of the player to get ranks for.
        `<username>` - The username of the player to get ranks for.

        Platforms
        - pc (bnet)
        - playstation (ps, psn, play)
        - xbox (xbl)
        - nintendo-switch (nsw, switch)

        Username formatting
        - pc: BattleTag (format: name#0000)
        - playstation: Online ID
        - xbox: Gamertag
        - nintendo-switch: Nintendo Switch ID (format: name-code)

        BattleTag example: Timmy#22340
        Nintendo Switch ID example: name-7alf327e36d5d1d8f507e765u5a2ech7
        """
        try:
            message = await ctx.send(embed=self.bot.loading_embed())
            data = await Request(platform=platform, username=username).get()
        except RequestError as e:
            await self.bot.cleanup(message)
            return await ctx.send(e)

        profile = Player(data, platform=platform, username=username)
        if profile.is_private:
            embed = profile.private()
        else:
            embed = await profile.get_ratings(ctx)
        await message.edit(embed=embed)

    @commands.command(aliases=["stats"])
    @commands.cooldown(1, 5.0, commands.BucketType.member)
    async def statistics(self, ctx, platform: Platform, *, username):
        """Returns player both quick play and competitive statistics.

        `<platform>` - The platform of the player to get stats for.
        `<username>` - The username of the player to get stats for.

        Platforms
        - pc (bnet)
        - playstation (ps, psn, play)
        - xbox (xbl)
        - nintendo-switch (nsw, switch)

        Username formatting
        - pc: BattleTag (format: name#0000)
        - playstation: Online ID
        - xbox: Gamertag
        - nintendo-switch: Nintendo Switch ID (format: name-code)

        BattleTag example: Timmy#22340
        Nintendo Switch ID example: name-7alf327e36d5d1d8f507e765u5a2ech7
        """
        try:
            message = await ctx.send(embed=self.bot.loading_embed())
            data = await Request(platform=platform, username=username).get()
        except RequestError as e:
            await self.bot.cleanup(message)
            return await ctx.send(e)

        profile = Player(data, platform=platform, username=username)
        if profile.is_private:
            embed = profile.private()
        else:
            try:
                embed = profile.get_statistics(ctx)
            except PlayerException as e:
                await self.bot.cleanup(message)
                return await ctx.send(e)

        await self.bot.cleanup(message)
        await self.bot.paginator.Paginator(pages=embed).start(ctx)

    @commands.command()
    @commands.cooldown(1, 5.0, commands.BucketType.member)
    async def hero(
        self,
        ctx,
        hero: Hero,
        platform: Platform,
        *,
        username,
    ):
        """Returns player both quick play and competitive statistics for a given hero.

        `<hero>` - The name of the hero you want to see stats for.
        `<platform>` - The platform of the player to get stats for.
        `<username>` - The username of the player to get stats for.

        Platforms
        - pc (bnet)
        - playstation (ps, psn, play)
        - xbox (xbl)
        - nintendo-switch (nsw, switch)

        Username formatting
        - pc: BattleTag (format: name#0000)
        - playstation: Online ID
        - xbox: Gamertag
        - nintendo-switch: Nintendo Switch ID (format: name-code)

        BattleTag example: Timmy#22340
        Nintendo Switch ID example: name-7alf327e36d5d1d8f507e765u5a2ech7
        """
        try:
            message = await ctx.send(embed=self.bot.loading_embed())
            data = await Request(platform=platform, username=username).get()
        except RequestError as e:
            await self.bot.cleanup(message)
            return await ctx.send(e)

        profile = Player(data, platform=platform, username=username)
        if profile.is_private:
            embed = profile.private()
        else:
            try:
                embed = profile.get_hero(ctx, hero)
            except PlayerException as e:
                await self.bot.cleanup(message)
                return await ctx.send(e)

        await self.bot.cleanup(message)
        await self.bot.paginator.Paginator(pages=embed).start(ctx)


def setup(bot):
    bot.add_cog(Statistics(bot))
