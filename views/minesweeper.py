import disnake as discord
import random

class MineButton(discord.ui.Button):
    def __init__(self, label, x, y):
        super().__init__(style = discord.ButtonStyle.blurple, label=" ", row=x)
        self.x = x
        self.y = y
        self.r = label
        self.clicked = False

    async def callback(self, inter: discord.MessageInteraction):
        v : MineView = self.view # type: ignore
        if inter.author != v.user:
            return await inter.send("This isn't your game!", ephemeral=True)
        v.board[self.x][self.y] = self.r
        self.label = self.r if self.r else " "
        self.disabled = True
        self.clicked = True
        if not self.r:
            v.clear()
        if self.r == "💥":
            v.open_all(True)
            return await inter.response.edit_message("Kaboom! 💥", view=v)
        for i, _ in enumerate(v.board):
            for j, __ in enumerate(_):
                if __ != "💥" and not v[i,j].clicked:  #type:ignore
                    print(i, j, v[i,j].label)  #type:ignore
                    return await inter.response.edit_message(view=v)
        v.open_all()
        return await inter.response.edit_message("You Won!", view=v)
                    


class MineView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user
        self.board = [[0 for i in range(5)] for j in range(5)]
        mines = random.sample(range(25), k=3)
        print(mines)
        self.min_coords = []
        for m in mines:
            x, y = divmod(m, 5)
            self.board[x][y] = "💥"  # type: ignore
            self.min_coords.append((x, y))
        self.add_mines()
        for x in range(5):
            for y in range(5):
                self.add_item(MineButton(self.board[x][y], x, y))

    def clear(self):
        for x, _x in enumerate(self.board):
            for y, _y in enumerate(_x):
                if _y==0 and self[x, y].clicked:   # type: ignore
                    neigh = self.neighbors(x, y)
                    for bx, by in neigh:
                        self.board[x][y] = " "  #type:ignore
                        butt : MineButton = self[bx, by] # type: ignore
                        butt.label = str(self.board[bx][by]) if butt.r else " "
                        butt.disabled = True
                        butt.clicked = True
                        self.clear()

    def neighbors(self, x, y):
        l = [-1, 0, 1]
        nums = [(x+i, y+j) for i in l for j in l]
        nums.remove((x,y))
        rnum = []
        for _x, _y in nums:
            if 0 <= _x < 5 and 0 <= _y < 5 and self.board[_x][_y] != "💥":
                rnum.append((_x,_y))
        return rnum

    def add_mines(self):
        for x, y in self.min_coords:
            nums = self.neighbors(x, y)
            for _x, _y in nums:
                self.board[_x][_y] = self.board[_x][_y] + 1
        print(self.board)

    def __getitem__(self, key):
        for child in self.children:
            if child.x == key[0] and child.y == key[1]: # type: ignore
                return child

    def open_all(self , error=False):
        for child in self.children:  # type: ignore 
            child : MineButton 
            child.disabled  = True  
            child.label = child.r
            if child.r == 0:       
                child.label = " "  
            if child.r == "💥":
                child.style = discord.ButtonStyle.red if error else discord.ButtonStyle.green



    
