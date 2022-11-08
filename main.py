import asqlite
import disnake as discord
from disnake.ext import commands
from tictactoe import TicTacToeView
from views import Confirm, SetupView
from bot import Apollyon
import random
from rsi.org import OrgAPI
import time

org = OrgAPI('TFTTALON')

bot = Apollyon()


@bot.event
async def on_ready():
    bot.conn = await asqlite.connect("main.db")
    print("I'm Ready!")


@bot.slash_command(description="Shows bot's latency")
async def ping(inter):
    start = time.perf_counter()
    await inter.send("Ping...")
    end = time.perf_counter()
    duration = (end - start) * 1000
    await inter.edit_original_message(content='Pong! {:.2f}ms'.format(duration)
                                      )


@commands.has_role(1005250279505154078)
@bot.slash_command(
    description="Sends a message to all of the memebrs having a specific role")
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
async def promote(inter:discord.ApplicationCommandInteraction, user:discord.Member):
    r = await bot.register(inter.guild.id, user.id, new=True)
    await inter.send("Successfully promoted the member!")
    await user.edit(nick=bot.ranks[r[0]]["insignia"] + " " + r[1][1])
    role1 = inter.guild.get_role(bot.ranks[r[0]]["id"])
    role2 = inter.guild.get_role(bot.ranks[r[1][0]]["id"])
    await inter.author.remove_roles(role2)
    await inter.author.add_roles(role1)


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


@bot.slash_command(description="Setup Orgbot in your server!")
async def setup(inter, org_spectrum_id:str=commands.Param(description="Enter you Org's spectrum ID. Be sure this is same as shown on website")):
    org = await bot.loop.run_in_executor(None, OrgAPI, org_spectrum_id)
    if "members" not in org._ttlcache:
            org._ttlcache["members"] = await bot.loop.run_in_executor(None, org._update_members, '')
    members = org._ttlcache["members"]
    mem = [m['handle'] for m in members]
    v = SetupView(org, mem, inter.guild.id)
    v.bot = bot
    v.inter = inter
    emb = discord.Embed(title=org.name, description="Placeholder")
    emb.set_thumbnail(url=org.logo)
    await inter.send(embed=emb, view=v)


@bot.slash_command()
async def test(inter):
    v = discord.ui.View()
    await inter.send("hello", view=v)

bot.load_extension("jishaku")
bot.run(
    "ODE4ODMyNDYxMTA2NjQzMDI1.G0zyWZ.RrIO3NQnPSZgAvWjhKQcaijKMLJJnujYJCZfbs")
