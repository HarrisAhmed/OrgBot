import disnake
from disnake.ext import commands, tasks
from datetime import date
import asqlite
from db import Hanknyeon
from token import TOKEN
import sys
import traceback
from pathlib import Path


intents = disnake.Intents.all()
bot = Hanknyeon()


@bot.event
async def on_ready():
    print("I'm Alive")
    bot.conn = await asqlite.connect("db/main.db")
    bot.curr = await asqlite.connect("db/currency.db")
    await bot.get_cards_data()
    print(len(bot.data.keys()))


@bot.event
async def on_slash_command_error(inter, error):
    if isinstance(error, commands.CheckFailure):
        if str(error) == "first":
            await bot.create_profile(inter.author.id)
            await inter.send(embed=disnake.Embed(description="This is your first time using me. Your adventure with Haknyeon starts now! Use the command again to continue.", color=0xfcb8b8), ephemeral=True)
        else:
            raise error
    elif isinstance(error, commands.CommandOnCooldown):
        time = error.cooldown.get_retry_after()
        embed = disnake.Embed(title="This command is on cooldown", description=f"Try using this command after {bot.sort_time(int(time))}.", color=disnake.Color.red())
        embed.set_author(name=inter.author.display_name, icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=embed)
    else:
        raise error


@tasks.loop(seconds=2)
async def check_limit():
    limited_cards = await bot.limited_cards()
    for r in limited_cards:
        card = r[0]
        dated = r[1]
        if str(date.today()) >= dated:
            await bot.delete_card(card, limit=True)
            print("done dana done")

        
for file in Path('cogs').glob('**/*.py'):
    *tree, _ = file.parts
    try:
        f = f"{'.'.join(tree)}.{file.stem}"
        print(f + " has been loaded!")
        bot.load_extension(f)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)


bot.load_extension("jishaku")
bot.run(TOKEN)
