import disnake as discord

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        