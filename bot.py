from disnake.ext import commands
import disnake as discord
import asqlite


class Apollyon(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="..",
            test_guilds=[986817556901924915, 1039163489677226084],
            intents=discord.Intents.all(),
            status=discord.Status.idle,
            activity=discord.Game("Testing")
        )
        self.ranking = ["Rec", "E-1", "E-2", "E-3", "E-4", "E-5", "E-6", "E-7", "E-8", "E-9", "O-1", "O-2", "O-3", "O-4", "O-5", "O-6", "O-7", "O-8", "O-9", "O-10"]
        self.ranks = {
            "O-10" : {"insignia":"★ ★ ★ ★", "id":1024960227008860160, "name":"ADMIRAL / GENERAL"},
            "O-9" : {"insignia":"★ ★ ★", "id":1024960218699931729, "name":""},
            "O-8" : {"insignia":"★ ★", "id":1024753552851222658, "name":""},
            "O-7" : {"insignia":"★", "id":1004022597190697070, "name":""},
            "O-6" : {"insignia":"▰▰▰▰", "id":991333088246382672, "name":""},
            "O-5" : {"insignia":"▰▰▰", "id":986817556901924922, "name":""},
            "O-4" : {"insignia":"▰▰▱", "id":987053473830936596, "name":""},
            "O-3" : {"insignia":"▰▰", "id":986817556901924923, "name":""},
            "O-2" : {"insignia":"▰▱", "id":987053791117467648, "name":""},
            "O-1" : {"insignia":"▰", "id":986817557048754216, "name":""},
            "E-9" : {"insignia":"❱❱❱❱∴", "id":1020122448756211773, "name":""},
            "E-8" : {"insignia":"❱❱❱❱⋅⋅", "id":1020120620270374953, "name":""},
            "E-7" : {"insignia":"❱❱❱❱⋅", "id":1020120367517409330, "name":""},
            "E-6" : {"insignia":"❱❱❱❱", "id":1020119994442453014, "name":""},
            "E-5" : {"insignia":"❱❱❱", "id":1020117744781373440, "name":""},
            "E-4" : {"insignia":"(∕∕∕)", "id":1020117525490573354, "name":""},
            "E-3" : {"insignia":"(∕∕)", "id":1020117219788726272, "name":""},
            "E-2" : {"insignia":"(∕)", "id":1020116655843577947, "name":""},
            "E-1" : {"insignia":"()", "id":1020112626245709834, "name":""},
            "Rec" : {"insignia":"R-", "id":1021618895817285642, "name":""}
        }
        self.conn: asqlite.Connection = None
        

    async def register(self, guild_id, user_id, handle=False, new=False):
        async with self.conn.cursor() as cr:
            await cr.execute("CREATE TABLE IF NOT EXISTS registers(guild_id INT, user_id INT, rank TEXT, handle TEXT)")
            if not new:
                await cr.execute("INSERT INTO registers(guild_id, user_id, rank, handle) VALUES(?, ?, ?, ?)", (guild_id, user_id, "Rec", handle))
                await self.conn.commit()
            else:
                r = await self.get_user_registry(user_id, guild_id)
                rank = self.ranking[self.ranking.index(r[0]) + 1]
                await cr.execute("UPDATE registers SET rank=? WHERE user_id=? AND guild_id=?", (rank, user_id, guild_id))
                await self.conn.commit()
                return rank, r

    
    async def get_user_registry(self, user_id, guild_id):
        async with self.conn.cursor() as cr:
            await cr.execute("CREATE TABLE IF NOT EXISTS registers(guild_id INT, user_id INT, rank TEXT, handle TEXT)")
            await cr.execute("SELECT rank, handle FROM registers WHERE guild_id=? AND user_id=?", (guild_id, user_id))
            r = await cr.fetchone()
            return r


    async def set_guild_data(self, guild_id, modroles, curr, spectrum_id, reg1, reg2):
        async with self.conn.cursor() as cr:
            modrol = " ".join(str(r.id) for r in modroles)
            await cr.execute("CREATE TABLE IF NOT EXISTS guild_data(guild_id INT, modroles TEXT, spectrum_id TEXT, reg1, reg2)")
            await cr.execute("INSERT INTO guild_data(guild_id, modroles, spectrum_id, reg1, reg2) VALUES(?, ?, ?, ?, ?)", (guild_id, modrol, spectrum_id, reg1, reg2))
            try:
                c = [(guild_id, r, i) for r, i in curr.items()]
                print(c)
            except:
                c = [(guild_id, r.id, " ") for r in curr]
                print(c)
            print("here")
            await cr.execute("CREATE TABLE IF NOT EXISTS rank_data(guild_id INT, role INT, insignia TEXT)")
            await cr.executemany("INSERT INTO rank_data(guild_id, role, insignia) VALUES(?, ?, ?)", c)
            await self.conn.commit()


    async def get_guild_data(self, guild_id):
        async with self.conn.cursor() as cr:
            await cr.execute("SELECT * FROM guild_data WHERE guild_id=?", (guild_id))
            r = await cr.fetchone()
            return r


    async def get_guild_ranking(self, guild_id):
        async with self.conn.cursor() as cr:
            await cr.execute("SELECT * FROM rank_data WHERE guild_id=?", (guild_id))
            r = await cr.fetchall()
            dt = {}
            for l in r:
                dt[l[1]] = l[2]
            return dt