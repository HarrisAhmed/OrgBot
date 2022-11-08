import disnake as discord


class Menu(discord.ui.View):
    def __init__(self, embeds, ids=None):
        super().__init__(timeout=None)
        self.files=None
        self.embeds = embeds
        self.remove_item(self.add_insig)
        self.remove_item(self.next)
        self.index = 0
        self.ids = ids
        self.curr = {}
        self.remove.label = f"Page 1/{len(self.embeds)}"
        self._update_state()


    async def interaction_check(self, inter):
        if self.inter.author.id != inter.author.id:  #type:ignore
            return False
        else:
            return True

    
    async def on_error(self, error, item, inter) -> None:
        if self.inter.author.id != inter.author.id:  #type:ignore
            return await inter.send("You can't use that!")
        else:
            raise error


    def _update_state(self) -> None:
        self.first_page.disabled = self.prev_page.disabled = self.index == 0
        self.last_page.disabled = self.next_page.disabled = self.index == len(self.embeds) - 1
        self.remove.label = f"Page {self.index + 1}/{len(self.embeds)}"


    @discord.ui.button(emoji="<:HN_Rewind:1035179518400405605>", style=discord.ButtonStyle.gray)
    async def first_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index = 0
        self._update_state()
        if not self.files:
            await inter.response.edit_message(embed=self.embeds[self.index], view=self,)
        else:
            self.embeds[self.index]._files.clear()
            file = discord.File(f"pics/{self.files[self.index]}.png", "image.png")
            await inter.response.edit_message(embed=self.embeds[self.index], view=self, files=[file])

    @discord.ui.button(emoji="<:HN_ArrowLeft:1035177424947773541>", style=discord.ButtonStyle.gray)
    async def prev_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index -= 1
        self._update_state()
        if not self.files:
            await inter.response.edit_message(embed=self.embeds[self.index], view=self,)
        else:
            self.embeds[self.index]._files.clear()
            file = discord.File(f"pics/{self.files[self.index]}.png", "image.png")
            await inter.response.edit_message(embed=self.embeds[self.index], view=self, files=[file])

    @discord.ui.button(label="Page 1", style=discord.ButtonStyle.grey, disabled=True)
    async def remove(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        pass

    @discord.ui.button(emoji="<:HN_ArrowRight:1035177472179830875>", style=discord.ButtonStyle.gray)
    async def next_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index += 1
        self._update_state()
        if not self.files:
            await inter.response.edit_message(embed=self.embeds[self.index], view=self,)
        else:
            file = discord.File(f"pics/{self.files[self.index]}.png", "image.png")
            self.embeds[self.index]._files.clear()
            await inter.response.edit_message(embed=self.embeds[self.index], view=self, files=[file])

    @discord.ui.button(emoji="<:HN_FastForward:1035179433004371999>", style=discord.ButtonStyle.gray)
    async def last_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index = len(self.embeds) - 1
        self._update_state()
        if not self.files:
            await inter.response.edit_message(embed=self.embeds[self.index], view=self,)
        else:
            self.embeds[self.index]._files.clear()
            file = discord.File(f"pics/{self.files[self.index]}.png", "image.png")
            await inter.response.edit_message(embed=self.embeds[self.index], view=self, files=[file])

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True  #type:ignore
        await self.inter.edit_original_message(view=self)  #type:ignore


    @discord.ui.button(label="Set Insignia", style=discord.ButtonStyle.blurple)
    async def add_insig(self, b, inter):
        await inter.response.send_modal(
            title=f"Enter insignia for each rank",
            custom_id="role_insig",
            components=[
                discord.ui.TextInput(
                    label=r.name,
                    placeholder="Type Here...",
                    custom_id=r.id,
                    style=discord.TextInputStyle.paragraph,
                    min_length=1,
                    max_length=8,
                    required=False
                ) for r in self.ids[self.index]
            ],
        )
        modal_inter: discord.ModalInteraction = await self.bot.wait_for(
        "modal_submit",
        check=lambda i: i.custom_id == "role_insig" and i.author.id ==
        inter.author.id)
        for r, v in modal_inter.text_values.items():
            self.curr[int(r)] = v
        emb = self.embeds[self.index]
        emb.clear_fields()
        for l in self.ids[self.index]:
            emb.add_field(name=l.name, value=self.curr[l.id], inline=False)
        await modal_inter.response.edit_message(embed=emb)


    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next(self, b, inter):
        self.vie.clear_items()
        self.vie.add_item(self.vie.yes3)
        self.vie.add_item(self.vie.no3)
        self.vie.add_item(self.vie.cancel)
        self.vie.curr = self.curr
        await inter.response.edit_message(embed=discord.Embed(title="Registration messsage", description="Do you want to setup messages that are displayed at start or end of registration?\nClicking no will select the default ones.", color=discord.Color.dark_blue()), view=self.vie)


class MenuSelect(discord.ui.Select):
    def __init__(self, ids):
        self.ids = ids
        options = []
        for id in ids:
            options.append(discord.SelectOption(
                label = id
            ))
        super().__init__(
            placeholder="Select the cards to add into your folder...",
            min_values=1,
            max_values=len(ids),
            options=options
        )

    async def callback(self, inter):
        print(self.values)
        self.view.ids.clear()
        for v in self.values:
            self.view.ids.append(v)
        await inter.response.edit_message(embed=discord.Embed(title="Select cards from dropdown menu", description=f"**Folder Name: **{self.view.fdn}\n\n**Selected Cards: **\n-" + "\n-".join(id for id in self.view.ids), color=0xfcb8b8))


class SelectPages(discord.ui.View):
    def __init__(self, ids, fdn):
        super().__init__(timeout=60)
        self.ids = ids
        self.index = 0
        self.selected_ids = []
        self.fdn = fdn
        self.selects = []
        for id in range(0, len(ids), 25):
            nl = ids[id:id+25]
            self.selects.append(MenuSelect(nl))
        self.add_item(self.selects[0])
        self._update_state()


    async def interaction_check(self, inter):
        if self.inter.author.id != inter.author.id:  #type:ignore
            return False
        else:
            return True

    
    async def on_error(self, error, item, inter) -> None:
        if self.inter.author.id != inter.author.id:  #type:ignore
            return await inter.send("You can't use that!")
        else:
            raise error


    def _update_state(self) -> None:
        self.prev_page.disabled = self.index == 0
        self.next_page.disabled = self.index == len(self.selects) - 1
        self.remove.label = f"Page {self.index + 1}/{len(self.selects)}"


    def remove_select(self):
        for child in self.children:
            if isinstance(child, MenuSelect):
                self.remove_item(child)
                break   
        self.add_item(self.selects[self.index])

    
    @discord.ui.button(emoji="<:HN_ArrowLeft:1035177424947773541>", style=discord.ButtonStyle.gray)
    async def prev_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index -= 1
        self._update_state()
        self.remove_select()
        await inter.response.edit_message(view=self)

    
    @discord.ui.button(label="Page 1", style=discord.ButtonStyle.grey, disabled=True)
    async def remove(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        pass

    
    @discord.ui.button(emoji="<:HN_ArrowRight:1035177472179830875>", style=discord.ButtonStyle.gray)
    async def next_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index += 1
        self._update_state()
        self.remove_select()
        await inter.response.edit_message(view=self)

    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True  #type:ignore
        await self.inter.edit_original_message(view=self)  #type:ignore


    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button, inter):
        await inter.response.edit_message(embed=discord.Embed(title="Task Successfully completed!", description=f"**Folder Name: **{self.fdn}\n\n**Selected Cards: **\n-" + "\n-".join(id for id in self.ids), color=0xfcb8b8), view=None)
        self.value = True
        self.stop()


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button, inter):
        await inter.response.edit_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this your folder creation!", color=0xfcb8b8), view=None)
        self.value = False
        self.stop()



    