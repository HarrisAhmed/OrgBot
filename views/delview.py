import disnake as discord

class DeleteView(discord.ui.View):
    def __init__(self, user_id, cards):
        super().__init__(timeout=60)
        self.remove_item(self.more)
        self.remove_item(self.one)
        self.add_item(DeleteSelect(cards))
        self.user = user_id
        self.card = None
        self.q = None


    @discord.ui.button(label="Take Single", style=discord.ButtonStyle.green)
    async def one(self, button, inter):
        if self.inter.author.id != inter.author.id:  #type:ignore
            return await inter.send("You can't use that!")
        await self.bot.remove_cards(self.user, self.card)  #type:ignore
        self.clear_items()
        await inter.response.edit_message(f"Deleted a single duplicate of selected card ({self.card}) from user's inventory.", view=self)

    
    @discord.ui.button(label="Take all", style=discord.ButtonStyle.red)
    async def more(self, button, inter):
        if self.inter.author.id != inter.author.id:  #type:ignore
            return await inter.send("You can't use that!")
        await self.bot.remove_cards(self.user, self.card, self.q)  #type:ignore
        self.clear_items()
        await inter.response.edit_message(f"Deleted all duplicates of selected card ({self.card}) from user's inventory.", view=self)


class DeleteSelect(discord.ui.Select):
    def __init__(self, cards):
        self.cards = cards
        options = []
        for c in cards:
            options.append(discord.SelectOption(
                label = c[0].split(" ")[0]
            ))
        super().__init__(
            placeholder="Select the card to remove...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, inter):
        if self.view.inter.author.id != inter.author.id:  #type:ignore
            return await inter.send("You can't use that!")
        for c in self.cards:
            if c[0].split(" ")[0] == self.values[0]:
                self.view.q = int(c[0].split(" ")[1])  #type:ignore
                print(self.view.q)  #type:ignore
        self.view.card = self.values[0]  #type:ignore
        self.view.add_item(self.view.one)  #type:ignore
        self.view.add_item(self.view.more)  #type:ignore
        self.view.remove_item(self)  #type:ignore
        await inter.response.edit_message("Do you want to take all duplicates of selected card or single one?", view=self.view)
            

