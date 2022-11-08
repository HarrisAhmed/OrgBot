from disnake.ext import commands
import disnake as discord
from db import Hanknyeon
from views import CardsView, Menu
import random
from PIL import Image
import time
from io import BytesIO
import os
from datetime import datetime


class Cards(commands.Cog):
    def __init__(self, bot: Hanknyeon) -> None:
        super().__init__()
        self.bot = bot
        
    
    async def cog_slash_command_check(self, inter: discord.ApplicationCommandInteraction) -> bool:
        r = await self.bot.get_profile(inter.author.id)
        if not r:
            raise commands.CheckFailure("first")
        else:
            return True


    async def cog_command_error(self, inter: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            time = error.cooldown.get_retry_after()
            embed = discord.Embed(title="This command is on cooldown", description=f"Try using this command after {self.bot.sort_time(int(time))}.", color=discord.Color.red())
            embed.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            await inter.send(embed=embed)
        else:
            raise error


    @commands.slash_command(description="Drops card")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def drop(self, inter: discord.ApplicationCommandInteraction):
        data = self.bot.data
        await inter.response.defer()
        piclis = []
        for _ids in self.bot.data.keys():
            if _ids not in self.bot.deleted:
                piclis.append(_ids)
            else:
                print(_ids)
        r1 = [id for id in piclis if data[id]["rarity"]==1]
        r2 = [id for id in piclis if data[id]["rarity"]==2]
        r3 = [id for id in piclis if data[id]["rarity"]==3]
        r4 = [id for id in piclis if data[id]["rarity"]==4]
        r5 = [id for id in piclis if data[id]["rarity"]==5]
        while True:
            q, w, e = random.sample(r1*60+r2*30+r3*15+r4*10+r5*5, 3)
            if q != w and w != e and e != q:
                break
        buff = await self.bot.loop.run_in_executor(None, self.create, q + ".png", w + ".png", e + ".png")
        q, w, e = q, w, e
        emb = discord.Embed(
            description=f"{inter.author.mention} is dropping a set of 3 cards!",
            color=0xfcb8b8)
        emb.set_image(file=discord.File(buff, filename="image.png"))
        rarities = []
        names = []
        for i in (q, w, e):
            rarities.append(data[i]["rarity"])
            names.append(f"{data[i]['group']} {data[i]['name']}")
        view = CardsView(rarities, names, (q, w, e))
        view.inter = inter #type:ignore
        view.bot = self.bot #type:ignore
        await inter.edit_original_message(
            embed=emb,
            view=view,
        )


    def create(self, q, w, e):
        i1 = Image.open(f"pics/{q}").convert("RGBA")
        i2 = Image.open(f"pics/{w}").convert("RGBA")
        i3 = Image.open(f"pics/{e}").convert("RGBA")
        img = Image.new("RGBA", (2460, 1100), (0, 0, 0, 0))
        img.paste(i1, (0, 0), i1)
        img.paste(i2, (820, 0), i2)
        img.paste(i3, (1640, 0), i3)
        buff = BytesIO()
        img.save(buff, "png")
        buff.seek(0)
        return buff


    @commands.slash_command(description="Shows Inventory")
    async def inventory(self, inter, user: discord.User = None): #type:ignore
        data = self.bot.data
        user = user if user else inter.author
        r = await self.bot.get_inventory(user.id)
        cards = r
        if not cards:
            await inter.send(embed=discord.Embed(description="Nothing found...", color=0xfcb8b8))
            return
        if len(cards) <= 5:
            emb = discord.Embed(title=f"{user.display_name}'s Inventory...",
                                color=0xfcb8b8)
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            num = 1
            desc = ""
            checked = []
            for card in cards:
                if not card[0] in checked:
                    sp = card[0].split(" ")
                    if len(sp) == 2:
                        card = sp[0]
                        q = sp[1]
                    else:
                        card = card[0]
                        q = 1
                    checked.append(card[0])
                    rari = self.bot.rare[data[card]["rarity"]]
                    desc += f"**{num}. {data[card]['name']}**\n**🌸 Group**: {data[card]['group']}\n🍃 **Copies**: {q}\n🌼 **Card ID**: {card}\n({rari})\n\n"
                    num += 1
            emb.description = desc
            emb.set_footer(text="Page 1 of 1")
            await inter.response.send_message(embed=emb)
        elif len(cards) > 5:
            await inter.response.defer()
            embeds = []
            num = 1
            total, left_over = divmod(len(cards), 5)
            pages = total + 1 if left_over else total
            desc = ""
            mnum = 0
            for page in range(pages):
                for card in cards:
                    sp = card[0].split(" ")
                    if len(sp) == 2:
                        card = sp[0]
                        q = sp[1]
                    else:
                        q = 1
                    emb = discord.Embed(
                        title=f"{user.display_name}'s Inventory...", color=0xfcb8b8)
                    emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
                    rari = self.bot.rare[data[card]["rarity"]]
                    desc += f"**{num}. {data[card]['name']}**\n**🌸 Group**: {data[card]['group']}\n🍃 **Copies**: {q}\n🌼 **Card ID**: {card}\n({rari})\n\n"
                    num += 1
                    mnum += 1
                    if num - 1 == len(cards):
                        emb.description = desc
                        embeds.append(emb)
                        mnum = -10000000000
                    if mnum == 5:
                        mnum = 0
                        emb.description = desc
                        desc = ""
                        embeds.append(emb)
            view = Menu(embeds)
            view.inter = inter #type:ignore
            await inter.edit_original_message(embed=embeds[0], view=view)


    @commands.slash_command()
    async def show(self, inter):
        pass


    @show.sub_command(description="Shows information about a card")
    async def card(self, inter, id: str):
        if id == "Nothing found":
            await inter.response.send_message("You don't have any card in your inventory.")
            return
        data = self.bot.data
        card = id
        rari = self.bot.rare[data[card]["rarity"]]
        emb = discord.Embed(
            title=f"{data[card]['name']}",
            description=
            f"🌸 **Group**: {data[card]['group']}\n🌼 **Card ID**: {card}\n🍃 **Owner**: {inter.author.mention}\n({rari})",
            color=0xfcb8b8)
        emb.set_image(file=discord.File(f"./pics/{id}.png", "image.png"))
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        await inter.send(embed=emb)


    @show.sub_command(description="Shows all cards in the database")
    async def all(self, inter):
        ids = self.bot.data.keys()
        data = self.bot.data
        embs = []
        files = []
        for card in ids:
            rari = self.bot.rare[data[card]["rarity"]]
            emb = discord.Embed(
                title=f"{data[card]['name']}",
                description=
                    f"🌸 **Group**: {data[card]['group']}\n🌼 **Card ID**: {card}\n🍃 **Owner**: {inter.author.mention}\n({rari})",
                color=0xfcb8b8)
            emb.set_image(file=discord.File(f"./pics/{card}.png", "image.png"))
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            embs.append(emb)
            files.append(card)
        v = Menu(embs, files=files)
        v.inter = inter #type:ignore
        await inter.send(embed=embs[0], view=v)

    @card.autocomplete("id")
    async def getids(self, inter, input: str):
        r = await self.bot.get_inventory(inter.author.id)
        if not r:
            return [id for id in ["Nothing found"]]
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
            return [id for id in ids if input.lower() in id.lower()] 
    

    @commands.slash_command(description="Gift a card to your friend")
    async def gift_card(self, inter, user: discord.User, card_id:str):
        if card_id == "Nothing found":
            await inter.send("You don't have any card in your inventory.", ephemeral=True)
            return
        await self.bot.remove_cards(inter.author.id, card_id)
        await self.bot.insert_card(user.id, card_id)
        r = await self.bot.get_inventory(inter.author.id)
        copies = 0
        for card in r:
            if card[0].split(" ")[0] == card_id:
                copies = card[0].split(" ")[1]
                break
        emb = discord.Embed(description=f"You've given {user.mention} a gift! <:HN_Gift:1034881304052899850>\n\n<:HN_Butterfly2:1034884649912127619> Given 1x {self.bot.data[card_id]['group']} **{self.bot.data[card_id]['name']}** | **{card_id}**\n{self.bot.rare[self.bot.data[card_id]['rarity']]}\n<:HN_Butterfly:1034882795547394179> **Copies left: **{copies}", color=0xfcb8b8)
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=emb)


    @gift_card.autocomplete("card_id")
    async def getid(self, inter, input: str):
        r = await self.bot.get_inventory(inter.author.id)
        if not r:
           return [id for id in ["Nothing found"]]
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
            return [id for id in ids if input.lower() in id.lower()]  
    

    @commands.slash_command(description="Search a card with its name and group!")
    async def search(self, inter, group:str, rarity:commands.Range[1, 5]=0):  #type: ignore
        ids = [id for id in self.bot.data.keys()]
        embeds = []
        files = []
        for id in ids:
            if self.bot.data[id]["group"] == group:
              if rarity == self.bot.data[id]["rarity"] or rarity==0:
                data = self.bot.data
                card = id
                rari = self.bot.rare[data[card]["rarity"]]
                emb = discord.Embed(
                    title=f"{data[id]['name']}",
                    description=
                    f"🌸 **Group**: {data[card]['group']}\n🌼 **Card ID**: {card}\n({rari})",
                    color=0xfcb8b8)
                emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
                file=discord.File(f"pics/{id}.png", "image.png")
                emb.set_image(url="attachment://image.png")
                files.append(id)
                embeds.append(emb)
        if len(embeds) == 0:
            return await inter.send("Nothing found...")
        m_v = Menu(embeds, files=files)
        m_v.inter = inter  #type:ignore
        await inter.send(embed=embeds[0], view=m_v, file=discord.File(f"pics/{files[0]}.png"))


    @search.autocomplete("group")
    async def group_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            if not self.bot.data[id]["group"] in groups:
                groups.append(self.bot.data[id]["group"])
        return [group for group in groups if input.lower() in group.lower()]


    @commands.slash_command(description="Shows your current cooldowns")
    async def cooldowns(self, inter):
        command: commands.InvokableApplicationCommand = self.bot.get_slash_command("drop") #type:ignore
        fake_msg = discord.Object(id=inter.author.id)
        fake_msg.author = inter.author #type:ignore
        cd_mapping = command._buckets
        cd = cd_mapping.get_bucket(fake_msg) #type:ignore
        dr_cd = cd.get_retry_after()
        drop_cd = self.bot.sort_time(int(dr_cd)) if dr_cd else "0 seconds"
        try:
            car_cd = time.time() - self.bot.card_cd[inter.author.id]
            card_cd = self.bot.sort_time(int(300-car_cd)) if car_cd > 0 else "0 seconds"
        except KeyError:
            card_cd = "0 seconds"
        r = await self.bot.daily(inter.author.id, get=True)
        dai_cd = datetime.now().timestamp() - r[0]  #type:ignore
        daily_cd = self.bot.sort_time(int(86400-dai_cd)) if 86400 > dai_cd > 0 else "0 seconds"
        emb = discord.Embed(title="COOLDOWNS", description=f"<:HN_DropCD:1033796159149453312> **Drop: **{drop_cd}\n<:HN_ClaimCD:1033796187985281034> **Claim: **{card_cd}\n<:HN_DailyCD:1033796206155022336> **Daily: **{daily_cd}", color=0xfcb8b8)
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=emb)


def setup(bot: Hanknyeon):
    bot.add_cog(Cards(bot))