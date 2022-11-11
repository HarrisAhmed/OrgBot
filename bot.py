from disnake.ext import commands
import disnake as discord
import asyncpg


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
        self.db: asyncpg.Connection = None
        

    async def register(self, guild_id, user_id, handle=False, new=False, demote=False):
        if not new and not demote:
            conn = await self.db.acquire()
            ranking = await self.get_guild_ranking(guild_id)
            async with conn.transaction():
                await self.db.execute("INSERT INTO registers(guild_id, user_id, rank, handle) VALUES($1, $2, $3, $4)", guild_id, user_id, len(ranking)-1, handle)
            await self.db.release(conn)
        if new:
            r = await self.get_user_registry(user_id, guild_id)
            conn = await self.db.acquire()
            ranking = await self.get_guild_ranking(guild_id)
            rank = r[0] - 1 if not demote else r[0] + 1
            async with conn.transaction():
                await self.db.execute("UPDATE registers SET rank=$1 WHERE user_id=$2 AND guild_id=$3", rank, user_id, guild_id)
            await self.db.release(conn)
            return rank, r

    
    async def get_user_registry(self, user_id, guild_id):
        r = await self.db.fetchrow("SELECT * FROM registers WHERE guild_id=$1 AND user_id=$2", guild_id, user_id)
        try:
            return r["rank"], r["handle"]
        except:
            return None


    async def set_guild_data(self, guild_id, modroles, curr, spectrum_id, reg1, reg2):
        modrol = " ".join(str(r.id) for r in modroles)
        try:
            c = [(guild_id, int(curr[r]["id"]), curr[r]["insignia"], r) for r in curr.keys()]
        except:
            c = [(guild_id, int(r.id), " ", curr.index(r)) for r in curr]
        conn = await self.db.acquire()
        async with conn.transaction():
            await self.db.execute("INSERT INTO guild_data(guild_id, modroles, spectrum_id, reg1, reg2) VALUES($1, $2, $3, $4, $5)", guild_id, modrol, spectrum_id, reg1, reg2)
            await self.db.executemany("INSERT INTO rank_data(guild_id, role, insignia, place) VALUES($1, $2, $3, $4)", c)
        await self.db.release(conn)


    async def get_guild_data(self, guild_id):
        r = await self.db.fetchrow("SELECT * FROM guild_data WHERE guild_id=$1", guild_id)
        try:
            return r["guild_id"], r["modroles"], r["spectrum_id"], r["reg1"], r["reg2"]
        except:
            return None


    async def get_guild_ranking(self, guild_id):
        r = await self.db.fetch("SELECT * FROM rank_data WHERE guild_id=$1", guild_id)
        dt = {}
        for l in r:
            dt[l["place"]] = {"id":l["role"], "insignia":l["insignia"]}
        return dt