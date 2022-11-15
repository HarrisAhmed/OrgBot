import disnake as discord
from .menu import Menu
import copy


async def setupstart(inter, bot, org):
    emb = discord.Embed(title="Moderator Roles", description="Select moderator roles that are able to promote, demote and send message to all members of a certain rank.\n(If you do not see all roles, use the text field below to search for the desired role.)\n\n**Selected Roles: **\n", color=discord.Color.dark_blue())
    m_role_view = RoleSelect(emb, inter)
    await inter.response.edit_message(embed=emb, view=m_role_view)
    await m_role_view.wait()
    if m_role_view.value:
        m_roles = m_role_view.roles
        embed = discord.Embed(title="Rank Roles Selection", description="Add all roles that will serve as a rank for your org. The bot will use these to manage promotion/demotion commands, assign rank to those who finish registration, and use them as a reference for insignia's in a nickname. Hierarchy will be in the order you enter it from top to bottom (highest first to lowest last).\n\n**Selected Roles: **\n", color=discord.Color.dark_blue())
        r_role_view = RoleSelect(embed, inter)
        await m_role_view.inter.response.edit_message(embed=embed, view=r_role_view)
        await r_role_view.wait()
        if r_role_view.value:
            r_roles = r_role_view.roles
            confirm = Confirm2(inter)
            await r_role_view.inter.response.edit_message(embed=discord.Embed(title="Insignia Selection", description="Each rank role will be identified with its own insignia set up as the nick name of user. Do you want to set up an insignia?", color=discord.Color.dark_blue()), view=confirm)
            await confirm.wait()
            v = None
            curr = None
            if confirm.value:
                embeds = []
                ids = []
                for i in range(0, len(r_roles), 5):
                    nl = r_roles[i:i+5]
                    emb = discord.Embed(title="Insignia Selection", color=discord.Color.dark_blue())
                    for r in nl:
                        emb.add_field(name=r.name, value="Not Set", inline=False)
                    ids.append(nl)
                    embeds.append(emb)
                r = [r.id for r in r_roles]
                v = Menu(embeds=embeds, ids=ids, roles=r)
                v.inter = inter
                v.add_item(v.add_insig)
                v.add_item(v.next)
                v.bot = bot
                await confirm.inter.response.edit_message(embed=embeds[0], view=v)
                await v.wait()
                curr = v.curr
                if v.value:
                    pass
            if not confirm.value:
                curr = r_roles
                pass
            newinter = v.inter if v else confirm.inter
            reg_m_confirm = Confirm2(newinter)
            await newinter.response.edit_message(embed=discord.Embed(title="Registration messsage", description="Do you want to setup messages that are displayed at start or end of registration?\nClicking no will select the default ones.", color=discord.Color.dark_blue()), view=reg_m_confirm)
            await reg_m_confirm.wait()
            modal_inter = None
            if reg_m_confirm.value:
                await reg_m_confirm.inter.response.send_modal(
                    title=f"Enter messages to send for registration.",
                    custom_id="regis",
                    components=[
                        discord.ui.TextInput(
                            label="Registration start message",
                            placeholder="Type Here...",
                            custom_id="reg1",
                            value=f'''Hello! Let's get you registered! By continuing you are acknowledging the following agreement:

**{org.name} Pledge**
> I pledge to defend, protect, and benefit the interests of {org.name}. I will not divulge information about the org or its members to those outside of this org. I will notify command if I may have violated this pledge, whether intentionally or unintentionally. I will follow all orders and work in unison with my superiors and work in unison with those chosen to lead. I will notify command if I feel overburdened with my Org responsibilities. I will strive to take the initiative to the best of my ability and will notify command if I would like to take on greater responsibility and rank.

To continue please press the confirm button if you acknowledge the agreement!.''',
                            style=discord.TextInputStyle.paragraph,
                            min_length=5,
                            max_length=2048,
                        ),
                        discord.ui.TextInput(
                            label="Registration emd message",
                            placeholder="Type Here...",
                            custom_id="reg2",
                            value=f'''Your registration is complete. Welcome to {org.name}''',
                            style=discord.TextInputStyle.paragraph,
                            min_length=5,
                            max_length=2048,
                        ),
                    ],
                )
                modal_inter: discord.ModalInteraction = await bot.wait_for("modal_submit",check=lambda i: i.custom_id == "regis" and i.author.id ==inter.author.id)
                reg1 = modal_inter.text_values["reg1"]
                reg2 = modal_inter.text_values["reg2"]
            else:
                reg1 = f'''Hello! Let's get you registered! By continuing you are acknowledging the following agreement:

**{org.name} Pledge**
> I pledge to defend, protect, and benefit the interests of {org.name}. I will not divulge information about the org or its members to those outside of this org. I will notify command if I may have violated this pledge, whether intentionally or unintentionally. I will follow all orders and work in unison with my superiors and work in unison with those chosen to lead. I will notify command if I feel overburdened with my Org responsibilities. I will strive to take the initiative to the best of my ability and will notify command if I would like to take on greater responsibility and rank.

To continue please press the confirm button if you acknowledge the agreement!.'''
                reg2 = f'''Your registration is complete. Welcome to {org.name}'''
            new_inter = modal_inter if modal_inter else reg_m_confirm.inter
            emb = discord.Embed(title="Set registration logs channel", description="Information for registered users will be shown here.\n\n**Selected Channel: **\n", color=discord.Color.dark_blue())
            ch_view = RegChannel(emb, inter)
            await new_inter.response.edit_message(embed=emb, view=ch_view)
            await ch_view.wait()
            if ch_view.value:
                reg_ch = ch_view.ch.id
                await ch_view.inter.response.edit_message(embed=discord.Embed(title="Setup Comepleted!", description="Thanks for choosing us!", color=discord.Color.dark_blue()), view=None)
                await bot.set_guild_data(inter.guild.id, m_roles, curr, org.symbol, reg1=reg1, reg2=reg2, reg_ch=reg_ch)


class Confirm2(discord.ui.View):
    def __init__(self, inter):
        super().__init__(timeout=600)
        self.inter = inter
        self.value=None
        

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, b, inter):
        if self.inter.author != inter.author:
            return await inter.send("You can't use that!", ephemeral=True)
        self.inter = inter
        self.value = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, b, inter):
        if self.inter.author != inter.author:
            return await inter.send("You can't use that!", ephemeral=True)
        self.inter = inter
        self.value = False
        self.stop()


class RoleSelect(discord.ui.View):
    def __init__(self, embed:discord.Embed, inter):
        super().__init__(timeout=600)
        self.inter = inter
        self.value = None
        self.emb = embed
        self.roles = []

    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next(self, b, inter):
        if self.inter.author != inter.author:
            return await inter.send("You can't use that!", ephemeral=True)
        if not self.roles:
            return await inter.send("You have not selected any role!", ephemeral=True)
        self.value = True
        self.inter = inter
        self.stop()


    @discord.ui.button(label="Undo Selection", style=discord.ButtonStyle.blurple)
    async def undo(self, b, inter):
        if self.inter.author != inter.author:
            return await inter.send("You can't use that!", ephemeral=True)
        self.roles.pop()
        emb = copy.deepcopy(self.emb)
        emb.description += "\n".join(r.mention for r in self.roles)
        await inter.response.edit_message(embed=emb)

    @discord.ui.role_select()
    async def role_sel(self, r: discord.ui.RoleSelect, inter):
        if self.inter.author != inter.author:
            return await inter.send("You can't use that!", ephemeral=True)
        if r.values[0] in self.roles:
            return await inter.send("You have already selected this role!", ephemeral=True)
        self.roles.append(r.values[0])
        emb = copy.deepcopy(self.emb)
        emb.description += "\n".join(r.mention for r in self.roles)
        await inter.response.edit_message(embed=emb)


class RegChannel(discord.ui.View):
    def __init__(self, emb: discord.Embed, inter):
        super().__init__(timeout=600)
        self.inter = inter
        self.emb = emb
        self.value = None

    
    @discord.ui.channel_select()
    async def chan_sel(self, r, inter):
        if self.inter.author != inter.author:
            return await inter.send("You can't use that!", ephemeral=True)
        emb = copy.deepcopy(self.emb)
        self.ch = r.values[0]
        emb.description += r.values[0].mention
        await inter.response.edit_message(embed=emb)

    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next(self, b, inter):
        if self.inter.author != inter.author:
            return await inter.send("You can't use that!", ephemeral=True)
        self.inter = inter
        self.value = True
        self.stop()