from disnake.ext import commands
import asqlite
import disnake
from datetime import date, datetime , timedelta
import os


class Hanknyeon(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="..",
            intents=disnake.Intents.all(),
            test_guilds=[1024399481782927511],
            status=disnake.Status.idle,
            activity=disnake.Game("with JoyStick"),
        ) 
        self.conn: asqlite.Connection = None   #type:ignore
        self.curr: asqlite.Connection = None   #type:ignore
        self.card_cd = {}
        self.petal = "<:HN_Petals:1033787290708889611>"
        self.data = {}
        self.deleted = []
        self.rare = {
    1:"✿❀❀❀❀",
    2:"✿✿❀❀❀",
    3:"✿✿✿❀❀",
    4:"✿✿✿✿❀",
    5:"✿✿✿✿✿"
}
        
    async def get_inventory(self, user_id):
            async with self.conn.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS CARDS(user_id INT, cards TEXT)")
                await cursor.execute("SELECT cards from CARDS WHERE user_id=?", (user_id,))
                r = await cursor.fetchall()
                await self.conn.commit()
                return r
                
            
    async def insert_card(self, user_id, card):
            async with self.conn.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS CARDS(user_id INT, cards TEXT)")
                await cursor.execute("SELECT cards from CARDS WHERE user_id=?", (user_id,))
                r = await cursor.fetchall()
                if r:
                    for cards in r:
                        c = cards[0][:8]
                        if c == card:
                            card = f"{card} {int(cards[0][9:])+1}"
                            await cursor.execute("UPDATE CARDS SET cards=? WHERE user_id=? AND cards=?", (card, user_id, cards[0]))
                            await self.conn.commit()
                            return
                card = card + " 1"
                await cursor.execute("INSERT INTO CARDS(user_id, cards) VALUES(?,?)", (user_id, card))
                await self.conn.commit()

    async def add_card_data(self, name, grop, rarity, id, limit):
            async with self.conn.cursor() as cursor:
                if limit:
                    EndDate = date.today()
                    await cursor.execute("CREATE TABLE IF NOT EXISTS LIMITED(card TEXT, date DATE)")
                    await cursor.execute("INSERT INTO LIMITED(card, date) VALUES(?, ?)", (id, EndDate))
                await cursor.execute("CREATE TABLE IF NOT EXISTS CARDS_DATA(name, grop, rarity INT,ID)")
                await cursor.execute("INSERT INTO CARDS_DATA(name, grop, rarity, ID) VALUES(?, ?, ?, ?)", (name, grop, rarity, id))
                await self.conn.commit()
                self.data[id] = {"name":name, "group":grop, "rarity":rarity}

    def sort_time(self, s:int):
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        w, d = divmod(d, 7)
        time_dict = {int(w):" week", int(d):" day", int(h):" hour", int(m):" minute", int(s):" second"}
        for item in time_dict.keys():
            if int(item) > 1:
                time_dict[item] = time_dict[item] + "s"
        return " ".join(str(i) + k for i, k in time_dict.items() if i!=0)
    
    async def get_cards_data(self):
            async with self.conn.cursor() as cursor:
                await cursor.execute("CREATE TABLE IF NOT EXISTS CARDS_DATA(name, grop, rarity INT,ID)")
                await cursor.execute("SELECT * from CARDS_DATA")
                r = await cursor.fetchall()
                await cursor.execute("CREATE TABLE IF NOT EXISTS deleted(id TEXT)")
                await cursor.execute("SELECT * FROM deleted")
                r2 = await cursor.fetchall()
                for cards in r:
                    self.data[cards[3]] = {"name":cards[0], "rarity":cards[2], "group":cards[1]}
                for de in r2:
                    if r2:
                        self.deleted.append(de[0])
                await self.conn.commit()

    async def delete_card(self, id, limit=False, from_existance=False):
            async with self.conn.cursor() as cursor:
                if limit:
                    await cursor.execute("DELETE FROM LIMITED WHERE card=?", (id))
                    await cursor.execute("CREATE TABLE IF NOT EXISTS deleted(id TEXT)")
                    await cursor.execute("INSERT INTO deleted(id) VALUES(?)", (id))
                    await self.conn.commit()
                    return
                if from_existance:
                    await cursor.execute("DELETE FROM CARDS_DATA WHERE id=?", (id))
                    os.remove(f"pics/{id}.png")
                self.data.pop(id)
                await self.conn.commit()

    async def limited_cards(self):
        async with self.conn.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS LIMITED(card TEXT, date DATE)")
            await cursor.execute("SELECT * FROM LIMITED")
            r = await cursor.fetchall()
            return r
    
    async def remove_cards(self, user_id, card, num=1):
            async with self.conn.cursor() as cursor:
                await cursor.execute("SELECT cards from CARDS WHERE user_id=?", (user_id,))
                r = await cursor.fetchall()
                for c in r:
                    if c[0].startswith(card):
                        n = int(c[0].split(" ")[1])
                        if n-num == 0:
                            await cursor.execute("DELETE FROM CARDS WHERE user_id=? AND cards=?", (user_id, c[0],))
                            await self.conn.commit()
                        else:
                            card = c[0].split(" ")[0] + " " + str(n-num)
                            await cursor.execute("UPDATE CARDS SET cards=? WHERE user_id=? AND cards=?", (card, user_id, c[0]))
                            await self.conn.commit()

    
    async def insert_fav(self, user_id, fav=" "):
        async with self.curr.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS profile(user_id INT, startdate TIMESTAMP, fav_card TEXT, coins INT, daily_dt TIMESTAMP, daily_streak INT)")
            await cursor.execute("SELECT fav_card FROM profile WHERE user_id=?", (user_id))
            r = await cursor.fetchone()
            if r[0]:
                await cursor.execute("UPDATE profile SET fav_card=? WHERE user_id=?", (fav, user_id))
            await self.curr.commit()

    
    async def get_profile(self, user_id):
        async with self.curr.cursor() as cr:
            await cr.execute("CREATE TABLE IF NOT EXISTS profile(user_id INT, startdate TIMESTAMP, fav_card TEXT, coins INT, daily_dt TIMESTAMP, daily_streak INT)")
            await cr.execute("SELECT * FROM profile WHERE user_id=?", (user_id))
            r = await cr.fetchone()
            await self.curr.commit()
            if r:
                dc = {"user_id":r[0], "startdate":r[1], "fav_card":r[2], "coins":r[3], "daily_dt":r[4], "daily_streak":r[5]}
                return dc
            else:
                return None
                
    async def create_profile(self, user_id):
        async with self.curr.cursor() as cr:
            new_d = datetime.now() - timedelta(2)
            new_dt = new_d.timestamp()
            tmstmp = datetime.now().timestamp()
            await cr.execute("CREATE TABLE IF NOT EXISTS profile(user_id INT, startdate TIMESTAMP, fav_card TEXT, coins INT, daily_dt TIMESTAMP, daily_streak INT)")
            await cr.execute("INSERT INTO profile(user_id, startdate, fav_card, coins, daily_dt, daily_streak) VALUES(?, ?, ?, ?, ?, ?)", (user_id, tmstmp, " ", 0, new_dt, 0))
            await self.curr.commit()
    
    async def add_coins(self, user_id, coins:int, remove=False):
        async with self.curr.cursor() as cr:
            await cr.execute("CREATE TABLE IF NOT EXISTS profile(user_id INT, startdate TIMESTAMP, fav_card TEXT, coins INT, daily_dt TIMESTAMP, daily_streak INT)")
            await cr.execute("SELECT coins FROM profile WHERE user_id=?", (user_id))
            r = await cr.fetchone()
            coin = coins + r[0]
            await cr.execute("UPDATE profile SET coins=? WHERE user_id=?", (coin, user_id))
            await self.curr.commit()
    
    async def remove_coins(self, user_id, coins:int, remove=False):
        async with self.curr.cursor() as cr:
            await cr.execute("CREATE TABLE IF NOT EXISTS profile(user_id INT, startdate TIMESTAMP, fav_card TEXT, coins INT, daily_dt TIMESTAMP, daily_streak INT)")
            await cr.execute("SELECT coins FROM profile WHERE user_id=?", (user_id))
            r = await cr.fetchone()
            coin = r[0] - coins
            await cr.execute("UPDATE profile SET coins=? WHERE user_id=?", (coin, user_id))
            await self.curr.commit()

    async def daily(self, user_id, get=False, set=False, streak:int=0):
        async with self.curr.cursor() as cr:
            await cr.execute("CREATE TABLE IF NOT EXISTS profile(user_id INT, startdate TIMESTAMP, fav_card TEXT, coins INT, daily_dt TIMESTAMP, daily_streak INT)")
            await cr.execute("SELECT daily_dt, daily_streak, coins FROM profile WHERE user_id=?", (user_id))
            r = await cr.fetchone()
            if get:
                return r
            if set:
                streak_lis = [125, 250, 375, 500, 625, 850]
                tmstmp = datetime.now().timestamp()
                await cr.execute("UPDATE profile SET coins=?, daily_streak=?, daily_dt=? WHERE user_id=?", (streak_lis[streak]+r["coins"], streak + 1, tmstmp, user_id))
                await self.curr.commit()
                return streak_lis[streak]


    async def folder(self, user_id, name=None, get=False, add=False, ids=None, delete=False):
        async with self.conn.cursor() as cr:
            await cr.execute("CREATE TABLE IF NOT EXISTS folder(user_id INT, name, id)")
            if get:
                await cr.execute("SELECT * FROM folder WHERE user_id=?", (user_id))
                r = await cr.fetchall()
                if r:
                    names = []
                    dc = {}
                    for i in r:
                        if i[1] not in names:
                            names.append(i[1])
                    for j in names:
                        dc[j] = []
                        for k in r:
                            dc[j].append(k[2])
                    print(dc)
                    return dc
            if add:
                values = [(user_id, name, id ) for id in ids]
                await cr.executemany("INSERT INTO folder(user_id, name, id) VALUES(?, ?, ?)", values)
                await self.conn.commit()
            if delete:
                if not ids:
                    await cr.execute("DELETE FROM folder WHERE user_id=? AND name=?", (user_id, name,))
                else:
                    params = [(user_id, name, id) for id in ids]
                    await cr.executemany("DELETE FROM folder WHERE user_id=? AND name=? AND id=?", params)