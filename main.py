import asyncpg
import disnake as discord
from disnake.ext import commands
from tictactoe import TicTacToeView
from views import Confirm, setupstart, Confirm2
from bot import Apollyon
import asyncio
import os
import random
from rsi.org import OrgAPI
import time

bot = Apollyon()

async def run():
    credentials = {"user": "orgbot", "password": "orgbot", "database": "main", "host": "localhost"}
    db = await asyncpg.create_pool(**credentials, max_size=5, min_size=3)
    await db.execute("CREATE TABLE IF NOT EXISTS rank_data(guild_id bigint, role bigint, insignia TEXT, place INT)")
    await db.execute("CREATE TABLE IF NOT EXISTS registers(guild_id bigint, user_id bigint, rank INT, handle TEXT)")
    await db.execute("CREATE TABLE IF NOT EXISTS guild_data(guild_id bigint, modroles TEXT, spectrum_id TEXT, reg1 TEXT, reg2 TEXT, reg_ch bigint)")
    bot.db = db
    try:
        await bot.start(os.getenv("token"))
    except KeyboardInterrupt:
        await db.close()
        await bot.logout()


def regcheck():
    async def predicate(ctx):
        r = await bot.get_guild_data(ctx.guild.id)
        if not r:
            raise discord.DiscordException("No reg")
        else:
            return True
    return commands.check(predicate)


def mycheck():
    async def predicate(ctx):
        r = await bot.get_guild_data(ctx.guild.id)
        modroles = [r[1]] if len(r[1].split(" ")) < 2 else [i for i in r[1].split(" ")]
        ids = [r.id for r in ctx.author.roles]
        return any(int(i) in ids for i in modroles) or ctx.author.id == ctx.guild.owner_id
    return commands.check(predicate)


@bot.event
async def on_ready():
    print("I'm Ready!")


@bot.slash_command(description="Shows bot's latency")
async def ping(inter):
    start = time.perf_counter()
    await inter.send("Ping...")
    end = time.perf_counter()
    duration = (end - start) * 1000
    await inter.edit_original_message(content='Pong! {:.2f}ms'.format(duration)
                                      )


@bot.slash_command(
    description="Sends a message to all of the memebrs having a specific role")
@regcheck()
@mycheck()
async def msg(inter, role: discord.User):
    await inter.response.send_modal(
        title=f"Send Message to {role.name}",
        custom_id="create_tag_low",
        components=[
            discord.ui.TextInput(
                label="Content",
                placeholder="The message to send",
                custom_id="content",
                style=discord.TextInputStyle.paragraph,
                min_length=5,
                max_length=1024,
            ),
        ],
    )
    modal_inter = await bot.wait_for(
        "modal_submit",
        check=lambda i: i.custom_id == "create_tag_low" and i.author.id ==
        inter.author.id)
    tag_name = modal_inter.text_values["content"]
    await role.send(tag_name)
    await modal_inter.send("Message successfully sent!")


@bot.slash_command(description="Register yourself into the Org!")
@regcheck()
async def register(inter: discord.ApplicationCommandInteraction,
                   star_citizen_handle: str = commands.Param(description="To find this, go to your account settings on the website and review your Handle.")):
    if isinstance(inter.channel, discord.DMChannel):
        return await inter.send("This command can only be used in a server!", ephemeral=True)
    r = await bot.get_user_registry(inter.author.id, inter.guild.id)
    if r:
        return await inter.send("You are already registered to this Org!", ephemeral=True)
    await inter.send("Please Check your DMs", ephemeral=True)
    data = await bot.get_guild_data(inter.guild.id)
    rank = await bot.get_guild_ranking(inter.guild.id)
    v = Confirm()
    v.inter = inter
    m = await inter.author.send(data[3], view=v)
    await inter.author.send("Please watch the following video to complete this process properly: https://streamable.com/2zu0qk")
    await v.wait()
    if not v.value:
        await m.reply("You cancelled your agreement!")
    else:
        rnd = random.randint(1000000, 9999999)
        v2 = Confirm(str(rnd), star_citizen_handle)
        v2.inter = inter
        v2.bot = bot
        v2.rank = rank
        print(rank)
        v2.data = data
        v2.remove_item(v2.confirm)
        v2.remove_item(v2.cancel)
        v2.add_item(v2.next)
        await m.reply(
            f'''Got it! To continue, please follow the steps provided:
 
> Step One: Navigate to the RSI Website: https://robertsspaceindustries.com/ 
> Step Two: Navigate to your profile by logging in to your account and then clicking the account button, then your profile picture top right of the screen. 
> Step Three: Click Edit on your profile card. 
> Step Four: On the left hand side, click Overview, then edit your Community Moniker to the following ID Code for verification: `{rnd}` 
> Step Five: Once you have completed this step, press next''',
            view=v2)
        await v.wait()


@bot.slash_command(description="Promote a member to higher authority")
@regcheck()
@mycheck()
async def promote(inter:discord.ApplicationCommandInteraction, user:discord.Member):
    await inter.response.defer()
    reg = await bot.get_user_registry(user.id, inter.guild.id)
    if not reg:
        return await inter.send("This user is not registered to this Org!", ephemeral=True)
    r = await bot.get_guild_ranking(inter.guild.id)
    if reg[0] - 1 < 0:
        return await inter.send("This user is already at the highest rank!", ephemeral=True)
    role = inter.guild.get_role(r[reg[0] - 1]["id"])
    role2 = inter.guild.get_role(r[reg[0]]["id"])
    await user.add_roles(role)
    try:
        await user.remove_roles(role2)
    except:
        pass
    try:
        await user.edit(nick=f"{r[reg[0] - 1]['insignia']} {reg[1]}")
    except:
        pass
    await inter.followup.send(f"Successfully promoted {user.mention} to {role.name}")
    await bot.register(inter.guild.id, inter.author.id, new=True)


@bot.slash_command(description="Play a game of Tic Tac Toe!")
async def tictactoe(self, inter):
        ch = random.choice((0, 1))
        await inter.response.defer()
        if ch:
            view = TicTacToeView(inter.author)
            await inter.edit_original_message("Your turn.", view=view)
            view.m = await inter.original_message() #type:ignore
        else:
            view = TicTacToeView(inter.author)
            await view.next_ai_move()
            await inter.edit_original_message("Your turn.", view=view)
            view.m = await inter.original_message() #type:ignore


def is_guild_owner():
    async def predicate(ctx):
        return ctx.author.id == ctx.guild.owner_id
    return commands.check(predicate)


@bot.slash_command(description="Demote a user to lower authority")
@regcheck()
@mycheck()
async def demote(inter, user:discord.Member):
    await inter.response.defer()
    reg = await bot.get_user_registry(user.id, inter.guild.id)
    if not reg:
        return await inter.send("This user is not registered to this Org!", ephemeral=True)
    r = await bot.get_guild_ranking(inter.guild.id)
    if reg[0] + 1 >= len(r):
        return await inter.send("This user is already at the lowest rank!", ephemeral=True)
    role = inter.guild.get_role(r[reg[0] + 1]["id"])
    role2 = inter.guild.get_role(r[reg[0]]["id"])
    await user.add_roles(role)
    try:
        await user.remove_roles(role2)
    except:
        pass
    try:
        await user.edit(nick=f"{r[reg[0] + 1]['insignia']} {reg[1]}")
    except:
        pass
    await inter.followup.send(f"Successfully demoted {user.mention} to {role.name}")
    await bot.register(inter.guild.id, inter.author.id, new=True, demote=True)


@bot.slash_command(description="Setup Orgbot in your server!")
@is_guild_owner()
async def setup(inter, org_spectrum_id:str=commands.Param(description="Enter you Org's spectrum ID. Be sure this is same as shown on website")):
    await inter.response.defer()
    try:
        org = await bot.loop.run_in_executor(None, OrgAPI, org_spectrum_id)
    except:
        return await inter.send("Org spectrum ID not found", ephemeral=True)
    if "members" not in org._ttlcache:
            org._ttlcache["members"] = await bot.loop.run_in_executor(None, org._update_members, '')
    members = org._ttlcache["members"]
    v = Confirm2(inter)
    v.yes.label = "Confirm"
    emb = discord.Embed(title=org.name, description="Placeholder")
    emb.set_thumbnail(url=org.logo)
    await inter.edit_original_message(embed=emb, view=v)
    await v.wait()
    if v.value:
        await setupstart(v.inter, bot, org)


@bot.slash_command()
async def test(inter):
    v = discord.ui.View()
    await inter.send("hello", view=v)


@bot.slash_command()
@regcheck()
async def org_info(inter: discord.ApplicationCommandInteraction):
    r = await bot.get_guild_data(inter.guild_id)
    org = OrgAPI(r[2])
    emb = discord.Embed(title=org.name, description=org.join_us, color=discord.Color.dark_blue())
    emb.add_field(name="Spectrum ID", value=org.symbol)
    emb.add_field(name="Model", value=org.model)
    emb.add_field(name="Commitment", value=org.commitment)
    emb.add_field(name="Primary Focus", value=org.primary_focus)
    emb.add_field(name="Secondary Focus", value=org.secondary_focus)
    emb.set_image(url=org.banner)
    await inter.send(embed=emb)


bot.load_extension("jishaku")
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
