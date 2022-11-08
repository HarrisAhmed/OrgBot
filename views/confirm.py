import disnake as discord
from rsi.citizen import fetch_citizen
from bot import Apollyon


class Confirm(discord.ui.View):
    def __init__(self, check=None, hn=None):
        super().__init__(timeout=600)
        self.value = None
        self.check = check
        self.hn = hn
        self.remove_item(self.done)
        self.remove_item(self.next)

    @discord.ui.button(label="I acknowledge!", style=discord.ButtonStyle.green)
    async def confirm(self, button, inter):
        if not inter.author.id == self.inter.author.id:
            await inter.send("You can't use that!", ephemeral=True)
        self.value = True
        await inter.response.defer()
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button, inter):
        if not inter.author.id == self.inter.author.id:
            await inter.send("You can't use that!", ephemeral=True)
        self.value = False
        await inter.response.defer()
        self.stop()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next(self, button, inter: discord.ApplicationCommandInteraction):
        us = await self.bot.loop.run_in_executor(None, fetch_citizen, self.hn)
        print(us)
        if not us or us["handle"] == "None":
            return await inter.send(
                "We did not find your account! Perhaps you entered the wrong handle! Please return to the server and redo the </register:1038367728110682122> command. Please follow the video that was provided to you above."
            )
        if self.check != us["username"]:
            return await inter.send(
                "We've checked and found that your moniker id has not been changed to what we provided. Please proceed as directed and press next again!"
            )
        else:
            self.add_item(self.done)
            self.remove_item(self.next)
            self.bot: Apollyon
            print(self.rank)

            print(list(self.rank.keys())[-1])
            role = self.inter.guild.get_role(list(self.rank.keys())[-1])
            await self.inter.author.add_roles(role)
            try:
                await self.inter.author.edit(nick=f"{self.rank[list(self.rank.keys())[-1]]} {us['handle']}")
            except:
                pass
            await inter.send(
                '''**Thank you, Please be sure to change your moniker back to your desired display name!**
                Press done to finish setup!'''
            )


    @discord.ui.button(label="Done!", style=discord.ButtonStyle.green)
    async def done(self, b, inter):
        await inter.send(self.data[4], view=None)
        await self.bot.register(self.inter.guild.id, self.inter.author.id,
                                    self.hn)