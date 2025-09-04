import os
import discord
from discord.ext import commands
import json
import random
import asyncio
import datetime
import shutil
import time
from keep_alive import keep_alive

# ===============================
# TOKEN (ambil dari Secrets Replit)
# ===============================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Token bot tidak ditemukan! Pastikan sudah di-set di Environment Variables")

# ===============================
# Data penyimpanan dengan backup system
# ===============================
DATA_FILE = "data.json"
BACKUP_DIR = "backups"

# Buat directory backup jika belum ada
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def create_default_data():
    """Buat data default jika file tidak ada"""
    default_data = {
        "players": {},
        "last_backup": 0,
        "total_players": 0,
        "server_stats": {
            "total_pvp_battles": 0,
            "total_breakthroughs": 0,
            "last_update": datetime.datetime.now().isoformat()
        }
    }
    save_data(default_data)
    return default_data

def load_data():
    """Load data dengan error handling"""
    try:
        if not os.path.exists(DATA_FILE):
            return create_default_data()
        
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        # Validasi struktur data
        if "players" not in data:
            return create_default_data()
            
        return data
        
    except json.JSONDecodeError:
        print("❌ Error decoding JSON, restoring from backup...")
        return restore_from_backup()
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return create_default_data()

def save_data(data):
    """Save data dengan backup otomatis"""
    try:
        # Backup data lama sebelum menimpa
        if os.path.exists(DATA_FILE):
            backup_data()
        
        # Update timestamp
        data["server_stats"]["last_update"] = datetime.datetime.now().isoformat()
        
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print("💾 Data saved successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error saving data: {e}")
        return False

def backup_data():
    """Buat backup data"""
    try:
        if os.path.exists(DATA_FILE):
            timestamp = int(time.time())
            backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json")
            shutil.copy2(DATA_FILE, backup_path)
            
            # Hapus backup lama (simpan hanya 5 terbaru)
            backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_")])
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    os.remove(os.path.join(BACKUP_DIR, old_backup))
                    
            print(f"📦 Backup created: backup_{timestamp}.json")
            return True
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def restore_from_backup():
    """Restore data dari backup terbaru"""
    try:
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_")])
        if backups:
            latest_backup = os.path.join(BACKUP_DIR, backups[-1])
            shutil.copy2(latest_backup, DATA_FILE)
            print(f"🔧 Restored from backup: {latest_backup}")
            return load_data()
    except:
        pass
    
    print("⚠️  No backup found, creating new data...")
    return create_default_data()

# ===============================
# Realms dan stages
# ===============================
REALMS = {
    "Mortal Realm": [
        "Body Refining", "Qi Gathering", "Inner Pill", "Yuan Sea",
        "Becoming God", "Divine Bridge", "Nirvana", "Destiny",
        "Life and Death", "Ascended"
    ],
    "Immortal Realm": [
        "Half-Immortal", "Profound Immortal", "Golden Immortal",
        "Immortal Venerable", "Immortal King", "Immortal Emperor"
    ],
    "God Realm": [
        "True God", "God Sovereign", "God King"
    ]
}

REALM_ORDER = list(REALMS.keys())

# ===============================
# Helper functions untuk player data
# ===============================
def get_player(uid):
    """Dapatkan data player, buat baru jika belum ada"""
    data = load_data()
    uid_str = str(uid)
    
    if uid_str not in data["players"]:
        # Player baru
        data["players"][uid_str] = {
            "realm": "Mortal Realm",
            "stage": "Body Refining",
            "exp": 0,
            "qi": 0,
            "equipment": {},
            "power": 10,
            "pvp_wins": 0,
            "pvp_losses": 0,
            "last_pvp": "0",
            "created_at": datetime.datetime.now().isoformat(),
            "last_updated": datetime.datetime.now().isoformat()
        }
        data["total_players"] += 1
        save_data(data)
        
    return data["players"][uid_str]

def update_player(uid, pdata):
    """Update data player"""
    data = load_data()
    uid_str = str(uid)
    
    if uid_str in data["players"]:
        pdata["last_updated"] = datetime.datetime.now().isoformat()
        data["players"][uid_str] = pdata
        return save_data(data)
    
    return False

def get_all_players():
    """Dapatkan semua data players"""
    data = load_data()
    return data["players"]

# ===============================
# Bot setup
# ===============================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===============================
# Event handlers
# ===============================
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} telah online!')
    print(f'📊 Total players: {load_data()["total_players"]}')
    
    # Backup saat bot start
    backup_data()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Cooldown! Coba lagi dalam {error.retry_after:.1f} detik")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command tidak dikenali!")
    else:
        print(f"Error: {error}")

# ===============================
# Command: status
# ===============================
@bot.command()
async def status(ctx):
    p = get_player(ctx.author.id)
    equip_list = ", ".join([f"{k}(+{v})" for k, v in p["equipment"].items()]) or "None"
    
    embed = discord.Embed(
        title=f"📊 {ctx.author.name}'s Status",
        color=0x00ff00
    )
    embed.add_field(name="Realm", value=f"{p['realm']} - {p['stage']}", inline=True)
    embed.add_field(name="EXP", value=p["exp"], inline=True)
    embed.add_field(name="Qi", value=p["qi"], inline=True)
    embed.add_field(name="Power", value=p["power"], inline=True)
    embed.add_field(name="Equipment", value=equip_list, inline=False)
    embed.add_field(name="PvP Record", value=f"{p['pvp_wins']}W / {p['pvp_losses']}L", inline=True)
    embed.set_footer(text="Cultivate dengan !cultivate")
    
    await ctx.send(embed=embed)

# ===============================
# Command: cultivate (dengan cooldown)
# ===============================
@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def cultivate(ctx):
    p = get_player(ctx.author.id)
    gain = random.randint(5, 15)
    qi_gain = random.randint(1, 5)
    power_gain = random.randint(1, 3)
    
    p["exp"] += gain
    p["qi"] += qi_gain
    p["power"] += power_gain
    
    update_player(ctx.author.id, p)
    
    embed = discord.Embed(
        title="🧘 Cultivation Success",
        description=f"{ctx.author.mention} meditated and gained:",
        color=0x00ff00
    )
    embed.add_field(name="EXP", value=f"+{gain}", inline=True)
    embed.add_field(name="Qi", value=f"+{qi_gain}", inline=True)
    embed.add_field(name="Power", value=f"+{power_gain}", inline=True)
    
    await ctx.send(embed=embed)

# ===============================
# Command: breakthrough
# ===============================
@bot.command()
async def breakthrough(ctx):
    p = get_player(ctx.author.id)
    stages = REALMS[p["realm"]]
    idx = stages.index(p["stage"])

    needed = (idx + 1) * 100
    if p["exp"] < needed:
        return await ctx.send(f"❌ Not enough EXP. You need {needed} to breakthrough!")

    if idx + 1 < len(stages):
        p["stage"] = stages[idx + 1]
        p["exp"] = 0
        p["power"] += 20
        message = f"🔥 {ctx.author.mention} broke through to **{p['realm']} - {p['stage']}**!"
    else:
        r_idx = REALM_ORDER.index(p["realm"])
        if r_idx + 1 < len(REALM_ORDER):
            next_realm = REALM_ORDER[r_idx + 1]
            p["realm"] = next_realm
            p["stage"] = REALMS[next_realm][0]
            p["exp"] = 0
            p["power"] += 50
            message = f"🌟 {ctx.author.mention} ascended to **{p['realm']} - {p['stage']}**!"
        else:
            return await ctx.send("🎉 You already reached the peak realm!")

    update_player(ctx.author.id, p)
    
    # Update server stats
    data = load_data()
    data["server_stats"]["total_breakthroughs"] += 1
    save_data(data)
    
    await ctx.send(message)

# ===============================
# Command: pvp
# ===============================
@bot.command()
async def pvp(ctx, enemy: discord.Member):
    if enemy.id == ctx.author.id:
        return await ctx.send("❌ You can't PvP yourself!")

    attacker = get_player(ctx.author.id)
    defender = get_player(enemy.id)

    now = datetime.datetime.utcnow().timestamp()
    if float(attacker["last_pvp"]) + 300 > now:
        return await ctx.send("⏳ You must wait 5 minutes before PvP again!")
    
    attacker["last_pvp"] = str(now)

    atk_power = attacker["power"] + random.randint(0, 20)
    def_power = defender["power"] + random.randint(0, 20)

    if atk_power > def_power:
        attacker["exp"] += 50
        defender["exp"] = max(0, defender["exp"] - 20)
        attacker["pvp_wins"] += 1
        defender["pvp_losses"] += 1
        result = f"⚔️ {ctx.author.mention} defeated {enemy.mention}!"
    else:
        attacker["exp"] = max(0, attacker["exp"] - 20)
        defender["exp"] += 50
        attacker["pvp_losses"] += 1
        defender["pvp_wins"] += 1
        result = f"⚔️ {enemy.mention} defeated {ctx.author.mention}!"

    update_player(ctx.author.id, attacker)
    update_player(enemy.id, defender)
    
    # Update server stats
    data = load_data()
    data["server_stats"]["total_pvp_battles"] += 1
    save_data(data)
    
    await ctx.send(result)

@pvp.error
async def pvp_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!pvp @user`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ User tidak valid!")

# ===============================
# Command: pvp_rank
# ===============================
@bot.command()
async def pvp_rank(ctx):
    data = load_data()
    players = data["players"]
    
    ranking = sorted(
        players.items(),
        key=lambda x: x[1]["pvp_wins"],
        reverse=True
    )[:10]

    embed = discord.Embed(
        title="🏆 PvP Leaderboard",
        color=0xffd700
    )
    
    for i, (uid, pdata) in enumerate(ranking, 1):
        try:
            user = await bot.fetch_user(int(uid))
            name = user.name
        except:
            name = "Unknown User"
            
        embed.add_field(
            name=f"{i}. {name}",
            value=f"W: {pdata['pvp_wins']} | L: {pdata['pvp_losses']} | Power: {pdata['power']}",
            inline=False
        )

    await ctx.send(embed=embed)

# ===============================
# Command: backup (admin only)
# ===============================
@bot.command()
@commands.has_permissions(administrator=True)
async def backup(ctx):
    """Buat manual backup data"""
    if backup_data():
        await ctx.send("✅ Backup created successfully!")
    else:
        await ctx.send("❌ Failed to create backup!")

# ===============================
# Command: stats (server statistics)
# ===============================
@bot.command()
async def stats(ctx):
    """Show server statistics"""
    data = load_data()
    stats = data["server_stats"]
    
    embed = discord.Embed(
        title="📈 Server Statistics",
        color=0x7289da
    )
    embed.add_field(name="Total Players", value=data["total_players"], inline=True)
    embed.add_field(name="Total PvP Battles", value=stats["total_pvp_battles"], inline=True)
    embed.add_field(name="Total Breakthroughs", value=stats["total_breakthroughs"], inline=True)
    embed.add_field(name="Last Update", value=stats["last_update"][:19], inline=False)
    
    await ctx.send(embed=embed)

# ===============================
# Start bot
# ===============================
keep_alive()
bot.run(BOT_TOKEN)