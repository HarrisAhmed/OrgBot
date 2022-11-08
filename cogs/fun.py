from disnake.ext import commands
import disnake as discord
from db import Hanknyeon
from views.tictactoe import TicTacToeView
import random
from views.rps import RPS
from views.minesweeper import MineView


class Fun(commands.Cog):
    def __init__(self, bot:Hanknyeon) -> None:
        self.bot = bot


    @commands.slash_command(description="Play a game of Tic Tace Toe!")
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

    
    @commands.slash_command(description="Play a minesweeper game!")
    async def minesweeper(self, inter):
        await inter.response.defer()
        v = MineView(inter.author)
        await inter.edit_original_message(f"{inter.author.display_name}'s minesweeper game...", view=v)


    @commands.slash_command(description="PLay a round of Rock Paper and scissors with the bot!")
    async def rps(self, inter):
        embed = discord.Embed(title="An intense game of Rock, Paper and Scissors!", description="Select an option from below!", color=0xfcb8b8)
        await inter.send(embed=embed, view=RPS())


def setup(bot: Hanknyeon):
    bot.add_cog(Fun(bot))