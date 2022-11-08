import disnake as discord
from .menu import Menu


class RoleMenu(discord.ui.RoleSelect):
    def __init__(self, n=False):
        super().__init__()
        self.n = n


    async def callback(self, inter: discord.MessageInteraction, /):
        if self.values[0] in self.view.m_roles or self.values[0] in self.view.roles:
            return await inter.send("You have already selected this role!", ephemeral=True)
        if not self.n:
            self.view.m_roles.append(self.values[0])
            await inter.response.edit_message(embed=discord.Embed(title="Moderator Roles", description="Select moderator roles that are able to promote, demote and send message to all members of a certain rank.\n\n**Selected Roles: **\n" + "\n".join(role.mention for role in self.view.m_roles), color=discord.Color.dark_blue()))
        else:
            self.view.roles.append(self.values[0])
            await inter.response.edit_message(embed=discord.Embed(title="Rank Roles Selection", description="Select roles for your ranking. Keep in mind that ranking heirarchy will be from top to bottom.\n\n**Selected Roles: **\n" + "\n".join(role.mention for role in self.view.roles), color=discord.Color.dark_blue()))
            


class SetupView(discord.ui.View):
    def __init__(self, org, mem, gid):
        super().__init__(timeout=None)
        self.clear_items()
        self.add_item(self.confirm)
        self.add_item(self.cancel)
        self.org = org
        self.mem = mem
        self.gid = gid
        self.r = False
        self.curr = None
        self.roles = []
        self.m_roles = []
        

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button, inter):
        if not inter.author.id == self.inter.author.id:
            await inter.send("You can't use that!", ephemeral=True)
        self.clear_items()
        self.add_item(self.next3)
        self.add_item(self.undo)
        self.add_item(self.cancel)
        self.add_item(RoleMenu())
        await inter.response.edit_message(embed=discord.Embed(title="Moderator Roles", description="Select moderator roles that are able to promote, demote and send message to all members of a certain rank.\n\n**Selected Roles: **\n", color=discord.Color.dark_blue()), view=self)


    @discord.ui.button(label="Cancel Setup", style=discord.ButtonStyle.red)
    async def cancel(self, button, inter):
        if not inter.author.id == self.inter.author.id:
            await inter.send("You can't use that!", ephemeral=True)
        await inter.response.edit_message("You cancelled the setup", view=None)


    @discord.ui.button(label="Next",style=discord.ButtonStyle.green)
    async def next3(self, b, inter: discord.MessageInteraction):
        if not self.m_roles:
            return await inter.send("You have not selected any role!", ephemeral=True)
        else:
            self.clear_items()
            self.add_item(self.next4)
            self.add_item(self.undo)
            self.add_item(self.cancel)
            self.add_item(RoleMenu(True))
            self.r = True
            await inter.response.edit_message(embed=discord.Embed(title="Rank Roles Selection", description="Select roles for your ranking. Keep in mind that ranking heirarchy will be from top to bottom.\n\n**Selected Roles: **\n", color=discord.Color.dark_blue()), view=self)


    @discord.ui.button(label="Next",style=discord.ButtonStyle.green)
    async def next4(self, b, inter: discord.MessageInteraction):
        if not self.roles:
            return await inter.send("You have not selected any role!", ephemeral=True)
        self.clear_items()
        self.add_item(self.yes2)
        self.add_item(self.no2)
        await inter.response.edit_message(embed=discord.Embed(title="Insignia Selection", description="Each rank role will be identified with its own insignia set up as the nick name of user. Do you want to set up an insignia?", color=discord.Color.dark_blue()), view=self)
        
    
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes2(self, b, inter):
        embeds = []
        ids = []
        for i in range(0, len(self.roles), 5):
            nl = self.roles[i:i+5]
            
            emb = discord.Embed(title="Insignia Selection", color=discord.Color.dark_blue())
            for r in nl:
                emb.add_field(name=r.name, value="Not Set", inline=False)
            ids.append(nl)
            embeds.append(emb)
        self.clear_items()
        v = Menu(embeds=embeds, ids=ids)
        v.inter = inter
        v.add_item(v.add_insig)
        v.add_item(v.next)
        v.bot = self.bot
        v.vie = self
        await inter.response.edit_message(embed=embeds[0], view=v)  
    

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no2(self, b, inter):
        self.clear_items()
        self.add_item(self.yes3)
        self.add_item(self.no3)
        self.add_item(self.cancel)
        await inter.response.edit_message(embed=discord.Embed(title="Registration messsage", description="Do you want to setup messages that are displayed at start or end of registration?\nClicking no will select the default ones.", color=discord.Color.dark_blue()), view=self)
        

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes3(self, b, inter):
        await inter.response.send_modal(
            title=f"Enter messages to send for registration.",
            custom_id="regis",
            components=[
                discord.ui.TextInput(
                    label="Registration start message",
                    placeholder="Type Here...",
                    custom_id="reg1",
                    value=f'''Hello! Let's get you registered! By continuing you are acknowledging the following agreement:

**{self.org.name} Pledge**
> I pledge to defend, protect, and benefit the interests of Task Force Talon. I will not divulge information about the org or its members to those outside of this org. I will notify command if I may have violated this pledge, whether intentionally or unintentionally. I will follow all orders and work in unison with my superiors and work in unison with those chosen to lead. I will notify command if I feel overburdened with my Org responsibilities. I will strive to take the initiative to the best of my ability and will notify command if I would like to take on greater responsibility and rank.

To continue please press the confirm button if you acknowledge the agreement!.''',
                    style=discord.TextInputStyle.paragraph,
                    min_length=5,
                    max_length=2048,
                ),
                discord.ui.TextInput(
                    label="Registration emd message",
                    placeholder="Type Here...",
                    custom_id="reg2",
                    value=f'''Your registration is complete. Welcome to {self.org.name}''',
                    style=discord.TextInputStyle.paragraph,
                    min_length=5,
                    max_length=2048,
                ),
            ],
        )
        modal_inter: discord.ModalInteraction = await self.bot.wait_for(
        "modal_submit",
        check=lambda i: i.custom_id == "regis" and i.author.id ==
        inter.author.id)
        await modal_inter.response.edit_message(embed=discord.Embed(title="Setup Comepleted!", description="Thanks for choosing us!", color=discord.Color.dark_blue()), view=None)

        print(self.curr)
        if not self.curr:
            self.curr = self.roles
        await self.bot.set_guild_data(self.gid, self.m_roles, self.curr, self.org.symbol, reg1=modal_inter.text_values["reg1"], reg2=modal_inter.text_values["reg2"])


    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no3(self, b, inter):
        await inter.response.edit_message(embed=discord.Embed(title="Setup Comepleted!", description="Thanks for choosing us!", color=discord.Color.dark_blue()), view=None)
        if not self.curr:
            self.curr = self.roles
        await self.bot.set_guild_data(self.gid, self.m_roles, self.curr, self.org.symbol, reg1=f'''Hello! Let's get you registered! By continuing you are acknowledging the following agreement:

**{self.org.name} Pledge**
> I pledge to defend, protect, and benefit the interests of Task Force Talon. I will not divulge information about the org or its members to those outside of this org. I will notify command if I may have violated this pledge, whether intentionally or unintentionally. I will follow all orders and work in unison with my superiors and work in unison with those chosen to lead. I will notify command if I feel overburdened with my Org responsibilities. I will strive to take the initiative to the best of my ability and will notify command if I would like to take on greater responsibility and rank.

To continue please press the confirm button if you acknowledge the agreement!.''', reg2=f'''Your registration is complete. Welcome to {self.org.name}''')
    
    
    @discord.ui.button(label="Undo Selection",style=discord.ButtonStyle.blurple)
    async def undo(self, b, inter):
        if not self.r:
            self.m_roles.pop()
            await inter.response.edit_message(embed=discord.Embed(title="Moderator Roles", description="Select moderator roles that are able to promote, demote and send message to all members of a certain rank.\n\n**Selected Roles: **\n" + "\n".join(role.mention for role in self.m_roles), color=discord.Color.dark_blue()))
        else:
            self.roles.pop()
            await inter.response.edit_message(embed=discord.Embed(title="Rank Roles Selection", description="Select roles for your ranking. Keep in mind that ranking heirarchy will be from top to bottom.\n\n**Selected Roles: **\n" + "\n".join(role.mention for role in self.roles), color=discord.Color.dark_blue()), view=self)
            