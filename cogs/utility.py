from disnake.ext import commands
import disnake as discord
from datetime import datetime
from db import Hanknyeon
import time


class Utility(commands.Cog):
    def __init__(self, bot:Hanknyeon):
        self.bot = bot


    @commands.slash_command(description="Shows profile")
    async def profile(self, inter, user:discord.User=None):  #type:ignore
        use = user if user else inter.author
        r = await self.bot.get_profile(use.id)
        if not r:
            if not use:
                return await inter.send("You are using the bot for the first time! Try the command again to continue...", ephemeral=True)
            else:
                return await inter.send(f"{use.mention} does not have any profile yet!", ephemeral=True)
        emb=discord.Embed(title=f"{use.display_name}'s Profile...", color=0xfcb8b8)
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        emb.set_author(name=use.name, icon_url=use.avatar.url)  #type:ignore
        emb.add_field(name="Started Playing", value=discord.utils.format_dt(datetime.fromtimestamp(r["startdate"])))
        emb.add_field(name="Petals", value=format(r["coins"], ",")  + " " + self.bot.petal)
        emb.add_field(name="Daily Streak", value=str(r["daily_streak"]+1)+" days")
        c = await self.bot.get_inventory(use.id)
        emb.add_field(name="Total Cards", value=len(c))
        if r["fav_card"] != " ":
            emb.add_field(name="Favourite Card", value="\u200b", inline=False)
            emb.set_image(file=discord.File("pics/" + r["fav_card"]+ ".png", "image.png"))
        else:
            emb.add_field(name="Favourite Card", value="No favourite card has been set.", inline=False)
        await inter.send(embed=emb)


    @commands.slash_command()
    async def favourite(self, inter):
        pass


    @favourite.sub_command(description="Sets a favourite card in your profile")
    async def set(self, inter, card_id:str):
        await self.bot.insert_fav(inter.author.id, card_id)
        emb = discord.Embed(description=f"<:HN_Butterfly:1034882795547394179> Your favourite card has been successfully set! (ID: {card_id})", color=0xfcb8b8)
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=emb)


    @set.autocomplete("card_id")
    async def getidfav(self, inter, input: str):
        r = await self.bot.get_inventory(inter.author.id)
        if not r:
           return [id for id in ["Nothing found"]]
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
            return [id for id in ids if input.lower() in id.lower()] 
            

    @commands.slash_command(description="Shows bot's latency")
    async def ping(self, inter):
        start = time.perf_counter()
        await inter.send("Ping...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        await inter.edit_original_message(content='Pong! {:.2f}ms'.format(duration))

        
def setup(bot):
    bot.add_cog(Utility(bot))