from disnake.ext import commands
import disnake as discord
from db import Hanknyeon
from datetime import datetime

from views import Menu, ConfirmView


class Currency(commands.Cog):
    def __init__(self, bot: Hanknyeon) -> None:
        super().__init__()
        self.bot = bot
        self.prices = {
            1:3000, 2:4500, 3:6000, 4:8500, 5:10000
        }

    
    async def cog_slash_command_check(self, inter: discord.ApplicationCommandInteraction) -> bool:
        r = await self.bot.get_profile(inter.author.id)
        if not r:
            raise commands.CheckFailure("first")
        else:
            return True
            

    @commands.slash_command(description="Claim your daily petals!")
    async def daily(self, inter):
        r1 = await self.bot.get_profile(inter.author.id)
        r = [r1["daily_dt"], r1["daily_streak"], r1["coins"]] #type:ignore
        today = datetime.now().timestamp()
        if today - r[0] > 86400:
            print(r[1])
            if r[1] > 6 or today - r[0] > 2*86401:
                streak = 0 
            else:
                streak = r[1]
            cs = await self.bot.daily(inter.author.id, set=True, streak=streak)
            streak = r[1] + 1
            emb = discord.Embed(title="Daily Petals Claimed!", description=f"**<:HN_Gift:1034881304052899850> Petals Claimed: **{cs} {self.bot.petal}\n**<:HN_Butterfly2:1034884649912127619> Total Petals: **{format(r[2] + cs, ',')} {self.bot.petal}\n**<:HN_Butterfly:1034882795547394179> Daily Streak: **{streak}\n\nCome back tomorrow to claim more petals!", color=0xfcb8b8)
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            await inter.send(embed=emb)
        else:
            await inter.send(f"You need to wait {self.bot.sort_time(86400-(today-r[0]))} before claiming your daily petals!", ephemeral=True)


    @commands.slash_command(description="Shows the amount of petals a user owns.")
    async def balance(self, inter, user:discord.Member=None):  #type:ignore
        user = user if user else inter.author
        r = await self.bot.get_profile(user.id)
        c = await self.bot.get_inventory(user.id)
        coins = format(r["coins"], ",")  #type:ignore
        emb = discord.Embed(title=f"{user.display_name}'s blanace", description=f"**<:HN_Butterfly2:1034884649912127619> Petals: **{coins} {self.bot.petal}\n**<:HN_Butterfly:1034882795547394179>Cards: **{len(c)}", color=0xfcb8b8)
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=emb)


    @commands.slash_command(description="Hanknyeon's marketplace!")
    async def shop(self, inter, group=None, rarity:commands.Range[1, 5]=None): #type:ignore
        ids = []
        print(len(ids))
        if group:
            for id in self.bot.data.keys():
                print(self.bot.data[id]["group"], group)
                if self.bot.data[id]["group"] == group:
                    ids.append(id)
                    print(ids)
        if not group:
            for id in self.bot.data.keys():
                ids.append(id)
        if rarity:
            _ids = []
            for id in ids:
                if self.bot.data[id]["rarity"] == rarity:
                    _ids.append(id)
            ids = _ids
        embeds = []
        desc = "<a:HN_Boun:1035119052919685210> **__Here are the listed prices of the cards:__**. <a:HN_Boun:1035119052919685210>\n\n"
        for i in range(0, len(ids), 5):
            emb = discord.Embed(title="The Haknyeon Market", color=0xfcb8b8)
            nl = ids[i:i+5]
            for id in nl:
                data = self.bot.data[id] #type:ignore
                desc += f"{data['group']} **{data['name']}**\n**Card ID: **{id}\n**Rarity: **{self.bot.rare[data['rarity']]}\n**Price: **{format(self.prices[data['rarity']], ',')}\n\n" #type:ignore
            emb.description = desc
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            desc = "<a:HN_Boun:1035119052919685210> **__Here are the listed prices of the cards:__** <a:HN_Boun:1035119052919685210>.\n\n"
            embeds.append(emb)
        view = Menu(embeds)
        view.inter = inter  #type:ignore
        await inter.send(embed=embeds[0], view=view)


    @shop.autocomplete("group")
    async def shopgroup(self, inter, input):
        groups = []
        for id in self.bot.data.keys():
            if not self.bot.data[id]["group"] in groups:
                groups.append(self.bot.data[id]["group"])
        return [gr for gr in groups if input.lower() in gr.lower()]


    @commands.slash_command(description="Buy a card with your petals!")
    async def buy(self, inter, card_id):
        id = card_id
        v = ConfirmView()
        v.inter = inter #type:ignore
        dt = self.bot.data[id]
        price = self.prices[dt['rarity']]
        emb = discord.Embed(title="Are you sure you want to buy this card?", description=f"{dt['group']} **{dt['name']}**\n**Card ID: **{id}\n{self.bot.rare[dt['rarity']]}\n**Price: **{format(price, ',')}", color=0xfcb8b8)
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        emb.set_image(file=discord.File(f"pics/{id}.png", "image.png"))
        await inter.send(embed=emb, view=v)
        await v.wait()
        if v.value == False:
            await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this transaction!", color=0xfcb8b8), view=None, attachments=[])
        elif v.value == True:
            prf = await self.bot.get_profile(inter.author.id)
            coins = prf["coins"]  #type:ignore
            if coins < price:
                return await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You don't have enough coins to buy this card!", color=0xfcb8b8), view=None, attachments=[])
            await self.bot.remove_coins(inter.author.id, price)
            await self.bot.insert_card(inter.author.id, id)
            await inter.edit_original_message(embed=discord.Embed(description=f"<:HN_Checkmark:1035085306346606602> You successfully bought the card! (ID: {id})", color=0xfcb8b8), view=None, attachments=[])


    @buy.autocomplete("card_id")
    async def buyid(self, inter, input):
        return [id for id in self.bot.data.keys() if input.lower() in id.lower()]


    @commands.slash_command(description="Sell your cards for some petals!")
    async def sell(self, inter, card_id):
        id = card_id
        v = ConfirmView()
        v.inter = inter  #type:ignore
        dt = self.bot.data[id]
        price = int(str(self.prices[dt['rarity']])[:-1])
        emb = discord.Embed(title="Are you sure you want to sell this card?", description=f"{dt['group']} **{dt['name']}**\n**Card ID: **{id}\n{self.bot.rare[dt['rarity']]}\n**Selling Price: **{format(price, ',')}", color=0xfcb8b8)
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        emb.set_image(file=discord.File(f"pics/{id}.png", "image.png"))
        await inter.send(embed=emb, view=v)
        await v.wait()
        if v.value == False:
            await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this transaction!", color=0xfcb8b8), view=None, attachments=[])
        elif v.value == True:
            await self.bot.add_coins(inter.author.id, price)
            await self.bot.remove_cards(inter.author.id, id)
            await inter.edit_original_message(embed=discord.Embed(description=f"<:HN_Checkmark:1035085306346606602> You successfully sold the card! (ID: {id})", color=0xfcb8b8), view=None, attachments=[])


    @sell.autocomplete("card_id")
    async def getidfav(self, inter, input: str):
        r = await self.bot.get_inventory(inter.author.id)
        if not r:
           return [id for id in ["Nothing found"]]
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
            return [id for id in ids if input.lower() in id.lower()] 


def setup(bot):
    bot.add_cog(Currency(bot))