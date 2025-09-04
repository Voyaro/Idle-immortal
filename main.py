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
            "total_dungeons": 0,
            "total_techniques_learned": 0,
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
        
        # FIX: Tambahkan field baru jika missing
        if "total_dungeons" not in data["server_stats"]:
            data["server_stats"]["total_dungeons"] = 0
        if "total_techniques_learned" not in data["server_stats"]:
            data["server_stats"]["total_techniques_learned"] = 0
            
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
        if not os.path.exists(BACKUP_DIR):
            print("⚠️ No backup directory found")
            return create_default_data()
            
        backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_") and f.endswith(".json")]
        if not backups:
            print("⚠️ No backup files found")
            return create_default_data()
            
        backups.sort(reverse=True)
        latest_backup = os.path.join(BACKUP_DIR, backups[0])
        
        print(f"🔧 Restoring from backup: {latest_backup}")
        shutil.copy2(latest_backup, DATA_FILE)
        return load_data()
        
    except Exception as e:
        print(f"❌ Error restoring backup: {e}")
        return create_default_data()

# ===============================
# Realms, Stages, dan EXP Cap - SUPER BUFFED
# ===============================
REALMS = {
    "Mortal Realm": {
        "stages": [
            "Body Refining [Entry]", "Body Refining [Middle]", "Body Refining [Peak]",
            "Qi Gathering [Entry]", "Qi Gathering [Middle]", "Qi Gathering [Peak]", 
            "Inner Pill [Entry]", "Inner Pill [Middle]", "Inner Pill [Peak]",
            "Yuan Sea [Entry]", "Yuan Sea [Middle]", "Yuan Sea [Peak]",
            "Becoming God [Entry]", "Becoming God [Middle]", "Becoming God [Peak]",
            "Divine Bridge [Entry]", "Divine Bridge [Middle]", "Divine Bridge [Peak]",
            "Nirvana [Entry]", "Nirvana [Middle]", "Nirvana [Peak]",
            "Destiny [Entry]", "Destiny [Middle]", "Destiny [Peak]",
            "Life and Death [Entry]", "Life and Death [Middle]", "Life and Death [Peak]",
            "Ascended [Entry]", "Ascended [Middle]", "Ascended [Peak]"
        ],
        "exp_cap": 10000,
        "exp_multiplier": 1.0,
        "power_multiplier": 1.0,
        "spirit_stone_gain": 1,
        "color": 0x964B00
    },
    "Immortal Realm": {
        "stages": [
            "Half-Immortal [Entry]", "Half-Immortal [Middle]", "Half-Immortal [Peak]",
            "Profound Immortal [Entry]", "Profound Immortal [Middle]", "Profound Immortal [Peak]",
            "Golden Immortal [Entry]", "Golden Immortal [Middle]", "Golden Immortal [Peak]",
            "Immortal Venerable [Entry]", "Immortal Venerable [Middle]", "Immortal Venerable [Peak]",
            "Immortal King [Entry]", "Immortal King [Middle]", "Immortal King [Peak]",
            "Immortal Emperor [Entry]", "Immortal Emperor [Middle]", "Immortal Emperor [Peak]"
        ],
        "exp_cap": 100000,
        "exp_multiplier": 3.0,
        "power_multiplier": 5.0,
        "spirit_stone_gain": 5,
        "color": 0x00FF00
    },
    "God Realm": {
        "stages": [
            "True God [Entry]", "True God [Middle]", "True God [Peak]",
            "God Sovereign [Entry]", "God Sovereign [Middle]", "God Sovereign [Peak]", 
            "God King [Entry]", "God King [Middle]", "God King [Peak]"
        ],
        "exp_cap": 500000,
        "exp_multiplier": 10.0,
        "power_multiplier": 25.0,
        "spirit_stone_gain": 25,
        "color": 0xFFD700
    }
}

REALM_ORDER = list(REALMS.keys())

# ===============================
# Cultivation Sects & Random Techniques
# ===============================
CULTIVATION_SECTS = {
    "sword": {"name": "Sword Sect", "emoji": "⚔️", "specialty": "Sword Techniques"},
    "elemental": {"name": "Elemental Sect", "emoji": "🔥", "specialty": "Element Control"},
    "body": {"name": "Body Sect", "emoji": "💪", "specialty": "Physical Cultivation"},
    "soul": {"name": "Soul Sect", "emoji": "👻", "specialty": "Soul Attacks"},
    "alchemy": {"name": "Alchemy Sect", "emoji": "🧪", "specialty": "Pill Refining"},
    "array": {"name": "Array Sect", "emoji": "🔷", "specialty": "Formation Arrays"},
    "beast": {"name": "Beast Taming Sect", "emoji": "🐉", "specialty": "Spirit Beasts"},
    "dark": {"name": "Dark Moon Sect", "emoji": "🌙", "specialty": "Shadow Techniques"}
}

TECHNIQUE_TYPES = {
    "attack": {"name": "Attack Technique", "emoji": "⚡", "power_bonus": (0.15, 0.25)},
    "defense": {"name": "Defense Technique", "emoji": "🛡️", "power_bonus": (0.10, 0.20)},
    "support": {"name": "Support Technique", "emoji": "💫", "power_bonus": (0.08, 0.18)},
    "healing": {"name": "Healing Technique", "emoji": "❤️", "power_bonus": (0.05, 0.15)},
    "movement": {"name": "Movement Technique", "emoji": "💨", "power_bonus": (0.07, 0.17)}
}

ELEMENT_TYPES = {
    "fire": "🔥", "water": "💧", "earth": "🌍", "wind": "💨", 
    "lightning": "⚡", "ice": "❄️", "light": "✨", "dark": "🌙"
}

# ===============================
# Equipment System
# ===============================
EQUIPMENT_SHOP = {
    "wooden_sword": {"name": "Wooden Sword", "power": 5, "cost": 50, "type": "weapon", "emoji": "⚔️"},
    "iron_sword": {"name": "Iron Sword", "power": 10, "cost": 100, "type": "weapon", "emoji": "⚔️"},
    "steel_sword": {"name": "Steel Sword", "power": 15, "cost": 200, "type": "weapon", "emoji": "⚔️"},
    "dragon_sword": {"name": "Dragon Sword", "power": 30, "cost": 500, "type": "weapon", "emoji": "🐉"},
    "leather_armor": {"name": "Leather Armor", "power": 3, "cost": 80, "type": "armor", "emoji": "🛡️"},
    "iron_armor": {"name": "Iron Armor", "power": 7, "cost": 150, "type": "armor", "emoji": "🛡️"},
    "steel_armor": {"name": "Steel Armor", "power": 12, "cost": 300, "type": "armor", "emoji": "🛡️"},
    "dragon_armor": {"name": "Dragon Armor", "power": 25, "cost": 600, "type": "armor", "emoji": "🐉"},
    "qi_ring": {"name": "Qi Ring", "power": 8, "cost": 250, "type": "accessory", "emoji": "💍"},
    "spirit_amulet": {"name": "Spirit Amulet", "power": 15, "cost": 500, "type": "accessory", "emoji": "🔮"},
    "divine_pendant": {"name": "Divine Pendant", "power": 25, "cost": 1000, "type": "accessory", "emoji": "✨"}
}

# ===============================
# Dungeon System
# ===============================
DUNGEONS = {
    "forest": {
        "name": "Spirit Forest",
        "min_level": 1,
        "max_level": 10,
        "min_reward": 20,
        "max_reward": 50,
        "spirit_stone_reward": (1, 3),
        "emoji": "🌳"
    },
    "cave": {
        "name": "Ancient Cave", 
        "min_level": 5,
        "max_level": 20,
        "min_reward": 40,
        "max_reward": 100,
        "spirit_stone_reward": (2, 5),
        "emoji": "🕳️"
    },
    "mountain": {
        "name": "Celestial Mountain",
        "min_level": 15,
        "max_level": 30,
        "min_reward": 80,
        "max_reward": 200,
        "spirit_stone_reward": (3, 8),
        "emoji": "⛰️"
    },
    "abyss": {
        "name": "Demon Abyss",
        "min_level": 25,
        "max_level": 50,
        "min_reward": 150,
        "max_reward": 400,
        "spirit_stone_reward": (5, 15),
        "emoji": "🔥"
    }
}

# ===============================
# Helper functions
# ===============================
def get_player_level(p):
    """Hitung level player berdasarkan realm dan stage"""
    realm_idx = REALM_ORDER.index(p["realm"])
    stage_idx = REALMS[p["realm"]]["stages"].index(p["stage"])
    return (realm_idx * 100) + (stage_idx * 3) + 1

def get_exp_cap(p):
    """Dapatkan EXP cap untuk realm player"""
    return REALMS[p["realm"]]["exp_cap"]

def generate_random_technique(player_realm, player_stage):
    """Generate random cultivation technique dengan AI"""
    sect = random.choice(list(CULTIVATION_SECTS.keys()))
    technique_type = random.choice(list(TECHNIQUE_TYPES.keys()))
    element = random.choice(list(ELEMENT_TYPES.keys()))
    
    # Determine power based on realm
    realm_idx = REALM_ORDER.index(player_realm)
    stage_idx = REALMS[player_realm]["stages"].index(player_stage)
    base_power = (realm_idx * 0.1) + (stage_idx * 0.02)
    
    # Power bonus range
    min_bonus, max_bonus = TECHNIQUE_TYPES[technique_type]["power_bonus"]
    power_bonus = round(random.uniform(min_bonus + base_power, max_bonus + base_power), 2)
    
    # Technique names pool
    prefix = ["Heavenly", "Divine", "Ancient", "Celestial", "Primordial", "Mystic", "Supreme"]
    middle = ["Dragon", "Phoenix", "Star", "Moon", "Sun", "Cloud", "Mountain", "Ocean"]
    suffix = ["Slash", "Palm", "Fist", "Step", "Breath", "Gaze", "Shield", "Domain"]
    
    technique_name = f"{random.choice(prefix)} {random.choice(middle)} {random.choice(suffix)}"
    
    # Description generator
    descriptions = {
        "attack": [f"Unleashes devastating {element} energy", "Cuts through space itself", "Summons celestial wrath"],
        "defense": [f"Creates impenetrable {element} barrier", "Absorbs enemy attacks", "Reflects damage back"],
        "support": [f"Amplifies {element} cultivation speed", "Enhances spiritual sense", "Boosts Qi recovery"],
        "healing": [f"Regenerates body with {element} energy", "Purifies toxins", "Revives damaged meridians"],
        "movement": [f"Teleports through {element} space", "Moves at lightning speed", "Phases through objects"]
    }
    
    description = random.choice(descriptions[technique_type])
    
    # Cost based on power
    cost = int(power_bonus * 1000 * (realm_idx + 1))
    
    return {
        "id": f"{technique_type}_{element}_{random.randint(1000,9999)}",
        "name": technique_name,
        "sect": sect,
        "type": technique_type,
        "element": element,
        "power_bonus": power_bonus,
        "description": description,
        "cost": cost,
        "emoji": TECHNIQUE_TYPES[technique_type]["emoji"],
        "element_emoji": ELEMENT_TYPES[element],
        "requirements": {
            "realm": player_realm,
            "stage": player_stage
        }
    }

def get_player(uid):
    """Dapatkan data player, buat baru jika belum ada"""
    data = load_data()
    uid_str = str(uid)
    
    if uid_str not in data["players"]:
        # Player baru dengan data lengkap
        data["players"][uid_str] = {
            "realm": "Mortal Realm",
            "stage": "Body Refining [Entry]",
            "exp": 0,
            "qi": 0,
            "spirit_stones": 50,
            "equipment": {},
            "techniques": [],
            "current_technique": None,
            "sect": None,
            "base_power": 10,
            "total_power": 10,
            "pvp_wins": 0,
            "pvp_losses": 0,
            "last_pvp": "0",
            "last_dungeon": "0",
            "last_technique_find": "0",
            "dungeons_completed": 0,
            "techniques_learned": 0,
            "created_at": datetime.datetime.now().isoformat(),
            "last_updated": datetime.datetime.now().isoformat()
        }
        data["total_players"] += 1
        save_data(data)
    else:
        # Update player lama dengan field baru
        player_data = data["players"][uid_str]
        new_fields = {
            "spirit_stones": 50,
            "techniques": [],
            "current_technique": None,
            "sect": None,
            "base_power": player_data.get("power", 10),
            "total_power": player_data.get("power", 10),
            "last_technique_find": "0",
            "techniques_learned": 0,
            "created_at": datetime.datetime.now().isoformat(),
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        for field, default_value in new_fields.items():
            if field not in player_data:
                player_data[field] = default_value
        
        # Jika ada power lama, convert ke base_power
        if "power" in player_data and "base_power" not in player_data:
            player_data["base_power"] = player_data["power"]
            player_data["total_power"] = player_data["power"]
        
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
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===============================
# Event handlers
# ===============================
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} telah online!')
    print(f'🔑 Token valid: {bool(BOT_TOKEN)}')
    print(f'📊 Total players: {load_data()["total_players"]}')
    
    if BOT_TOKEN:
        print(f'🔒 Token length: {len(BOT_TOKEN)}')
    
    backup_data()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    print(f"📨 Received: {message.content} from {message.author}")
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Cooldown! Coba lagi dalam {error.retry_after:.1f} detik")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command tidak dikenali!")
    else:
        print(f"Error: {error}")

# ===============================
# TEST COMMAND: ping
# ===============================
@bot.command()
async def ping(ctx):
    """Test jika bot merespon"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! {latency}ms")
    print(f"✅ Ping command executed by {ctx.author}")

# ===============================
# Command: realms
# ===============================
@bot.command()
async def realms(ctx):
    """Lihat semua realm dan stages dengan detail"""
    embed = discord.Embed(
        title="🌌 Cultivation Realms Hierarchy",
        description="Path to immortality and beyond",
        color=0x7289da
    )
    
    for realm_name, realm_data in REALMS.items():
        stages_info = ""
        for i, stage in enumerate(realm_data["stages"]):
            exp_needed = int((i + 1) * 100 * realm_data["exp_multiplier"])
            power_level = int(10 * (i + 1) * realm_data["power_multiplier"])
            
            stages_info += f"**{i+1}. {stage}**\n"
            stages_info += f"→ EXP: {exp_needed} | Power: ~{power_level}\n"
        
        embed.add_field(
            name=f"{realm_name} 🌟",
            value=f"**EXP Cap:** {realm_data['exp_cap']:,}\n"
                  f"**Power Multiplier:** {realm_data['power_multiplier']}×\n"
                  f"**Spirit Stones:** {realm_data['spirit_stone_gain']}/cultivate\n"
                  f"**Stages:** {len(realm_data['stages'])}",
            inline=False
        )
    
    await ctx.send(embed=embed)

# ===============================
# Command: myrealm
# ===============================
@bot.command()
async def myrealm(ctx):
    """Lihat info detail tentang realm kamu sekarang"""
    p = get_player(ctx.author.id)
    realm_data = REALMS[p["realm"]]
    current_stage_idx = realm_data["stages"].index(p["stage"])
    
    next_stage = None
    if current_stage_idx + 1 < len(realm_data["stages"]):
        next_stage = realm_data["stages"][current_stage_idx + 1]
        exp_needed = int((current_stage_idx + 2) * 100 * realm_data["exp_multiplier"])
    else:
        realm_idx = REALM_ORDER.index(p["realm"])
        if realm_idx + 1 < len(REALM_ORDER):
            next_realm = REALM_ORDER[realm_idx + 1]
            next_stage = f"Ascend to {next_realm}"
            exp_needed = 1000
    
    embed = discord.Embed(
        title=f"🌠 {ctx.author.name}'s Realm Progress",
        color=realm_data["color"]
    )
    
    embed.add_field(
        name="Current Realm",
        value=f"**{p['realm']}**\nEXP Cap: {realm_data['exp_cap']:,}",
        inline=True
    )
    
    embed.add_field(
        name="Current Stage", 
        value=f"**{p['stage']}**\nStage {current_stage_idx + 1}/{len(realm_data['stages'])}",
        inline=True
    )
    
    embed.add_field(
        name="EXP Progress",
        value=f"{p['exp']}/{realm_data['exp_cap']}",
        inline=True
    )
    
    if next_stage:
        embed.add_field(
            name="Next Breakthrough",
            value=f"**{next_stage}**\nButuh: {exp_needed if 'exp_needed' in locals() else 'N/A'} EXP",
            inline=False
        )
    
    progress_percentage = min(100, (p["exp"] / realm_data["exp_cap"]) * 100)
    progress_bar = "█" * int(progress_percentage / 10) + "░" * (10 - int(progress_percentage / 10))
    
    embed.add_field(
        name="Overall Progress",
        value=f"```[{progress_bar}] {progress_percentage:.1f}%```",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ===============================
# Command: progress
# ===============================
@bot.command()
async def progress(ctx):
    """Lihat progress cultivation secara keseluruhan"""
    p = get_player(ctx.author.id)
    
    realm_data = REALMS[p["realm"]]
    current_stage_idx = realm_data["stages"].index(p["stage"])
    stage_progress = (current_stage_idx + 1) / len(realm_data["stages"]) * 100
    
    total_stages = sum(len(REALMS[realm]["stages"]) for realm in REALMS)
    current_global_stage = 0
    
    for realm in REALM_ORDER:
        if realm == p["realm"]:
            current_global_stage += current_stage_idx + 1
            break
        else:
            current_global_stage += len(REALMS[realm]["stages"])
    
    global_progress = (current_global_stage / total_stages) * 100
    
    embed = discord.Embed(
        title="📊 Overall Cultivation Progress",
        description=f"{ctx.author.name}'s journey to immortality",
        color=0x00ff00
    )
    
    embed.add_field(
        name="Current Position",
        value=f"**{p['realm']}** - {p['stage']}\nStage {current_global_stage}/{total_stages}",
        inline=False
    )
    
    global_bar = "█" * int(global_progress / 10) + "░" * (10 - int(global_progress / 10))
    embed.add_field(
        name="Global Progress",
        value=f"```[{global_bar}] {global_progress:.1f}%```",
        inline=False
    )
    
    if p["realm"] != "God Realm" or p["stage"] != "God King [Peak]":
        next_milestone = ""
        if current_stage_idx + 1 < len(realm_data["stages"]):
            next_milestone = realm_data["stages"][current_stage_idx + 1]
        else:
            next_realm_idx = REALM_ORDER.index(p["realm"]) + 1
            next_milestone = REALM_ORDER[next_realm_idx]
        
        embed.add_field(
            name="Next Milestone",
            value=f"**{next_milestone}**",
            inline=True
        )
    
    embed.set_footer(text="Total stages: Mortal(30) + Immortal(18) + God(9) = 57 stages")
    await ctx.send(embed=embed)

# ===============================
# Command: cultivate (dengan cooldown)
# ===============================
@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def cultivate(ctx):
    p = get_player(ctx.author.id)
    realm_data = REALMS[p["realm"]]
    exp_cap = realm_data["exp_cap"]
    
    base_gain = random.randint(5, 15)
    gain = int(base_gain * realm_data["exp_multiplier"])
    qi_gain = random.randint(1, 5)
    power_gain = random.randint(1, 3)
    spirit_stones_gain = random.randint(1, realm_data["spirit_stone_gain"])
    
    if p["exp"] + gain > exp_cap:
        gain = max(0, exp_cap - p["exp"])
        if gain == 0:
            return await ctx.send(f"❌ EXP sudah mencapai batas maksimum untuk realm ini! ({exp_cap} EXP)")
    
    p["exp"] += gain
    p["qi"] += qi_gain
    p["base_power"] += power_gain
    p["spirit_stones"] += spirit_stones_gain
    
    technique_bonus = 1 + sum(t['power_bonus'] for t in p["techniques"])
    p["total_power"] = int(p["base_power"] * technique_bonus)
    
    update_player(ctx.author.id, p)
    
    embed = discord.Embed(
        title="🧘 Cultivation Success",
        description=f"{ctx.author.mention} meditated and gained:",
        color=0x00ff00
    )
    embed.add_field(name="EXP", value=f"+{gain}", inline=True)
    embed.add_field(name="Qi", value=f"+{qi_gain}", inline=True)
    embed.add_field(name="Base Power", value=f"+{power_gain}", inline=True)
    embed.add_field(name="Spirit Stones", value=f"+{spirit_stones_gain}", inline=True)
    embed.add_field(name="Total EXP", value=f"{p['exp']}/{exp_cap}", inline=True)
    embed.add_field(name="Total Power", value=p["total_power"], inline=True)
    
    await ctx.send(embed=embed)

# ===============================
# Command: breakthrough
# ===============================
@bot.command()
async def breakthrough(ctx):
    p = get_player(ctx.author.id)
    realm_data = REALMS[p["realm"]]
    stages = realm_data["stages"]
    idx = stages.index(p["stage"])

    base_exp = (idx + 1) * 100
    exp_needed = int(base_exp * realm_data["exp_multiplier"])
    
    if p["exp"] < exp_needed:
        return await ctx.send(f"❌ Not enough EXP. You need {exp_needed} to breakthrough!")

    if idx + 1 < len(stages):
        p["stage"] = stages[idx + 1]
        p["exp"] = 0
        p["base_power"] += 15
        p["total_power"] = int(p["base_power"] * (1 + sum(t['power_bonus'] for t in p["techniques"])))
        message = f"🔥 {ctx.author.mention} broke through to **{p['stage']}**!"
    else:
        r_idx = REALM_ORDER.index(p["realm"])
        if r_idx + 1 < len(REALM_ORDER):
            next_realm = REALM_ORDER[r_idx + 1]
            p["realm"] = next_realm
            p["stage"] = REALMS[next_realm]["stages"][0]
            p["exp"] = 0
            p["base_power"] += 50
            p["total_power"] = int(p["base_power"] * (1 + sum(t['power_bonus'] for t in p["techniques"])))
            message = f"🌟 {ctx.author.mention} ascended to **{p['realm']}**!"
        else:
            return await ctx.send("🎉 You already reached the peak realm!")

    update_player(ctx.author.id, p)
    
    data = load_data()
    data["server_stats"]["total_breakthroughs"] += 1
    save_data(data)
    
    await ctx.send(message)

# ===============================
# Command: find_technique
# ===============================
@bot.command()
@commands.cooldown(1, 3600, commands.BucketType.user)
async def find_technique(ctx):
    """Mencari teknik cultivation baru secara random"""
    p = get_player(ctx.author.id)
    
    now = time.time()
    last_find = float(p.get("last_technique_find", "0"))
    
    if last_find + 3600 > now:
        remaining = int(last_find + 3600 - now)
        return await ctx.send(f"⏳ Anda harus menunggu {remaining//60} menit sebelum mencari teknik lagi!")
    
    technique = generate_random_technique(p["realm"], p["stage"])
    
    p["last_technique_find"] = str(now)
    update_player(ctx.author.id, p)
    
    embed = discord.Embed(
        title="📜 Technique Discovery!",
        description=f"{ctx.author.mention} menemukan teknik cultivation kuno!",
        color=0x00ff00
    )
    
    embed.add_field(
        name=f"{technique['emoji']} {technique['element_emoji']} {technique['name']}",
        value=f"**Sect:** {CULTIVATION_SECTS[technique['sect']]['emoji']} {CULTIVATION_SECTS[technique['sect']]['name']}\n"
              f"**Type:** {TECHNIQUE_TYPES[technique['type']]['name']}\n"
              f"**Power Bonus:** +{technique['power_bonus']*100}%\n"
              f"**Cost:** {technique['cost']} Spirit Stones\n"
              f"**Description:** {technique['description']}",
        inline=False
    )
    
    embed.set_footer(text="Gunakan !learn_technique [id] untuk mempelajari teknik ini")
    await ctx.send(embed=embed)

# ===============================
# Command: learn_technique
# ===============================
@bot.command()
async def learn_technique(ctx, technique_id: str):
    """Mempelajari teknik cultivation yang ditemukan"""
    p = get_player(ctx.author.id)
    
    # Simulate technique discovery
    technique = generate_random_technique(p["realm"], p["stage"])
    technique["id"] = technique_id
    
    if p["spirit_stones"] < technique["cost"]:
        return await ctx.send(f"❌ Tidak cukup Spirit Stones! Butuh {technique['cost']}, kamu punya {p['spirit_stones']}")
    
    if any(t['id'] == technique_id for t in p["techniques"]):
        return await ctx.send("❌ Anda sudah menguasai teknik ini!")
    
    p["spirit_stones"] -= technique["cost"]
    p["techniques"].append(technique)
    p["techniques_learned"] += 1
    p["total_power"] = int(p["base_power"] * (1 + sum(t['power_bonus'] for t in p["techniques"])))
    
    update_player(ctx.author.id, p)
    
    data = load_data()
    data["server_stats"]["total_techniques_learned"] += 1
    save_data(data)
    
    embed = discord.Embed(
        title="🎓 Technique Learned!",
        description=f"{ctx.author.mention} berhasil mempelajari teknik baru!",
        color=0x00ff00
    )
    
    embed.add_field(
        name=f"{technique['emoji']} {technique['name']}",
        value=f"**Power Bonus:** +{technique['power_bonus']*100}%\n"
              f"**Total Power:** {p['total_power']} (+{int(technique['power_bonus']*p['base_power'])})",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ===============================
# Command: my_techniques
# ===============================
@bot.command()
async def my_techniques(ctx):
    """Lihat semua teknik yang sudah dipelajari"""
    p = get_player(ctx.author.id)
    
    if not p["techniques"]:
        return await ctx.send("❌ Anda belum mempelajari teknik apapun! Gunakan `!find_technique` untuk mencari teknik.")
    
    total_bonus = sum(t['power_bonus'] for t in p["techniques"])
    
    embed = discord.Embed(
        title=f"📚 {ctx.author.name}'s Cultivation Techniques",
        description=f"Total Power Bonus: +{total_bonus*100}%",
        color=0x7289da
    )
    
    for technique in p["techniques"]:
        embed.add_field(
            name=f"{technique['emoji']} {technique['element_emoji']} {technique['name']}",
            value=f"**Sect:** {CULTIVATION_SECTS[technique['sect']]['name']}\n"
                  f"**Type:** {technique['type'].title()}\n"
                  f"**Bonus:** +{technique['power_bonus']*100}% Power\n"
                  f"**Element:** {technique['element'].title()}",
            inline=True
        )
    
    embed.add_field(
        name="Power Summary",
        value=f"**Base Power:** {p['base_power']}\n"
              f"**Total Bonus:** +{total_bonus*100}%\n"
              f"**Total Power:** {p['total_power']}",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ===============================
# Command: status (IMPROVED)
# ===============================
@bot.command()
async def status(ctx):
    p = get_player(ctx.author.id)
    realm_data = REALMS[p["realm"]]
    level = get_player_level(p)
    exp_cap = get_exp_cap(p)
    
    equip_list = []
    for item_id, power in p["equipment"].items():
        item_data = EQUIPMENT_SHOP.get(item_id, {"name": item_id.replace("_", " ").title(), "emoji": "⚙️"})
        equip_list.append(f"{item_data['emoji']} {item_data['name']}(+{power})")
    
    equip_text = "\n".join(equip_list) if equip_list else "None"
    
    exp_percentage = min(100, (p["exp"] / exp_cap) * 100)
    progress_bar = "█" * int(exp_percentage / 10) + "░" * (10 - int(exp_percentage / 10))
    
    embed = discord.Embed(
        title=f"📊 {ctx.author.name}'s Cultivation Status",
        color=realm_data["color"]
    )
    
    embed.add_field(
        name="🌌 Realm & Stage",
        value=f"{p['realm']}\n**{p['stage']}** (Lv. {level})",
        inline=True
    )
    
    embed.add_field(
        name="⭐ Power Stats",
        value=f"**Total:** {p['total_power']}\n**Base:** {p['base_power']}\n**Bonus:** +{sum(t['power_bonus'] for t in p['techniques'])*100}%",
        inline=True
    )
    
    embed.add_field(
        name="💎 Resources",
        value=f"EXP: {p['exp']}/{exp_cap}\nQi: {p['qi']}\nSpirit Stones: {p['spirit_stones']}",
        inline=True
    )
    
    embed.add_field(
        name="📈 EXP Progress",
        value=f"```[{progress_bar}] {exp_percentage:.1f}%```",
        inline=False
    )
    
    embed.add_field(
        name="⚔️ PvP Record",
        value=f"🏆 {p['pvp_wins']}W / 💀 {p['pvp_losses']}L",
        inline=True
    )
    
    embed.add_field(
        name="🏰 Dungeons",
        value=f"Completed: {p['dungeons_completed']}",
        inline=True
    )
    
    embed.add_field(
        name="📚 Techniques",
        value=f"Learned: {p['techniques_learned']}",
        inline=True
    )
    
    embed.add_field(
        name="🎒 Equipment",
        value=equip_text,
        inline=False
    )
    
    await ctx.send(embed=embed)

# ===============================
# Command: shop
# ===============================
@bot.command()
async def shop(ctx):
    """Lihat item yang tersedia di shop"""
    embed = discord.Embed(
        title="🏪 Cultivation Shop",
        description="Gunakan `!buy <item_name>` untuk membeli\nContoh: `!buy iron_sword`",
        color=0xffd700
    )
    
    for item_id, item_data in EQUIPMENT_SHOP.items():
        embed.add_field(
            name=f"{item_data['emoji']} {item_data['name']} - {item_data['cost']} Qi",
            value=f"Power: +{item_data['power']} | Type: {item_data['type']}\nID: `{item_id}`",
            inline=False
        )
    
    embed.set_footer(text="Gunakan !inventory untuk melihat equipment Anda")
    await ctx.send(embed=embed)

# ===============================
# Command: buy
# ===============================
@bot.command()
async def buy(ctx, *, item_name: str):
    """Beli equipment dari shop"""
    item_name = item_name.lower().replace(" ", "_")
    
    if item_name not in EQUIPMENT_SHOP:
        return await ctx.send("❌ Item tidak ditemukan! Gunakan `!shop` untuk melihat list item.")
    
    item_data = EQUIPMENT_SHOP[item_name]
    p = get_player(ctx.author.id)
    
    if p["qi"] < item_data["cost"]:
        return await ctx.send(f"❌ Qi tidak cukup! Butuh {item_data['cost']} Qi, Anda punya {p['qi']} Qi.")
    
    current_equipment = p["equipment"]
    for eq_id, eq_power in current_equipment.items():
        if EQUIPMENT_SHOP.get(eq_id, {}).get("type") == item_data["type"]:
            p["base_power"] -= eq_power
            break
    
    p["qi"] -= item_data["cost"]
    p["equipment"][item_name] = item_data["power"]
    p["base_power"] += item_data["power"]
    p["total_power"] = int(p["base_power"] * (1 + sum(t['power_bonus'] for t in p["techniques"])))
    
    update_player(ctx.author.id, p)
    
    embed = discord.Embed(
        title="🛍️ Purchase Successful!",
        description=f"{ctx.author.mention} membeli {item_data['emoji']} {item_data['name']}",
        color=0x00ff00
    )
    embed.add_field(name="Power", value=f"+{item_data['power']}", inline=True)
    embed.add_field(name="Cost", value=f"{item_data['cost']} Qi", inline=True)
    embed.add_field(name="Remaining Qi", value=f"{p['qi']} Qi", inline=True)
    
    await ctx.send(embed=embed)

# ===============================
# Command: inventory
# ===============================
@bot.command()
async def inventory(ctx):
    """Lihat inventory equipment"""
    p = get_player(ctx.author.id)
    
    if not p["equipment"]:
        return await ctx.send("🎒 Inventory kosong! Gunakan `!shop` untuk melihat item yang bisa dibeli.")
    
    total_equip_power = sum(p["equipment"].values())
    
    embed = discord.Embed(
        title=f"🎒 {ctx.author.name}'s Inventory",
        description=f"Total Equipment Power: +{total_equip_power}",
        color=0x7289da
    )
    
    for item_id, power in p["equipment"].items():
        item_data = EQUIPMENT_SHOP.get(item_id, {"name": item_id.replace("_", " ").title(), "type": "unknown", "emoji": "⚙️"})
        embed.add_field(
            name=f"{item_data['emoji']} {item_data['name']}",
            value=f"Power: +{power} | Type: {item_data['type']}",
            inline=False
        )
    
    embed.add_field(name="Total Qi", value=f"{p['qi']} Qi", inline=True)
    embed.add_field(name="Total Power", value=p["total_power"], inline=True)
    
    await ctx.send(embed=embed)

# ===============================
# Command: sell
# ===============================
@bot.command()
async def sell(ctx, *, item_name: str):
    """Jual equipment"""
    item_name = item_name.lower().replace(" ", "_")
    
    p = get_player(ctx.author.id)
    
    if item_name not in p["equipment"]:
        return await ctx.send("❌ Item tidak ditemukan di inventory!")
    
    item_data = EQUIPMENT_SHOP.get(item_name, {"name": item_name.replace("_", " ").title(), "cost": 50})
    sell_price = max(10, item_data["cost"] // 2)
    
    p["base_power"] -= p["equipment"][item_name]
    del p["equipment"][item_name]
    p["qi"] += sell_price
    p["total_power"] = int(p["base_power"] * (1 + sum(t['power_bonus'] for t in p["techniques"])))
    
    update_player(ctx.author.id, p)
    
    await ctx.send(f"💰 {ctx.author.mention} menjual {item_data['name']} dan mendapatkan {sell_price} Qi!")

# ===============================
# Command: dungeons
# ===============================
@bot.command()
async def dungeons(ctx):
    """Lihat semua dungeon yang tersedia"""
    embed = discord.Embed(
        title="🏰 Available Dungeons",
        description="Gunakan `!enter <dungeon_name>` untuk memasuki dungeon\nContoh: `!enter forest`",
        color=0x8B4513
    )
    
    for dungeon_id, dungeon_data in DUNGEONS.items():
        embed.add_field(
            name=f"{dungeon_data['emoji']} {dungeon_data['name']}",
            value=f"Level: {dungeon_data['min_level']}-{dungeon_data['max_level']}\nReward: {dungeon_data['min_reward']}-{dungeon_data['max_reward']} EXP\nSpirit Stones: {dungeon_data['spirit_stone_reward'][0]}-{dungeon_data['spirit_stone_reward'][1]}\nID: `{dungeon_id}`",
            inline=False
        )
    
    await ctx.send(embed=embed)

# ===============================
# Command: enter (dungeon)
# ===============================
@bot.command()
@commands.cooldown(1, 300, commands.BucketType.user)
async def enter(ctx, *, dungeon_name: str):
    """Masuk ke dungeon"""
    dungeon_name = dungeon_name.lower()
    
    if dungeon_name not in DUNGEONS:
        return await ctx.send("❌ Dungeon tidak ditemukan! Gunakan `!dungeons` untuk melihat list dungeon.")
    
    dungeon_data = DUNGEONS[dungeon_name]
    p = get_player(ctx.author.id)
    player_level = get_player_level(p)
    exp_cap = get_exp_cap(p)
    
    if player_level < dungeon_data["min_level"]:
        return await ctx.send(f"❌ Level Anda ({player_level}) terlalu rendah untuk dungeon ini! (Min: {dungeon_data['min_level']})")
    
    if player_level > dungeon_data["max_level"]:
        return await ctx.send(f"❌ Level Anda ({player_level}) terlalu tinggi untuk dungeon ini! (Max: {dungeon_data['max_level']})")
    
    now = time.time()
    last_dungeon = float(p.get("last_dungeon", "0"))
    if last_dungeon + 300 > now:
        remaining = int(last_dungeon + 300 - now)
        return await ctx.send(f"⏳ Anda harus menunggu {remaining} detik sebelum masuk dungeon lagi!")
    
    p["last_dungeon"] = str(now)
    
    level_diff = min(dungeon_data["max_level"] - player_level, 10)
    exp_reward = random.randint(
        dungeon_data["min_reward"], 
        dungeon_data["max_reward"] + level_diff * 5
    )
    qi_reward = random.randint(5, 15)
    spirit_stones_reward = random.randint(dungeon_data["spirit_stone_reward"][0], dungeon_data["spirit_stone_reward"][1])
    
    if p["exp"] + exp_reward > exp_cap:
        exp_reward = max(0, exp_cap - p["exp"])
        if exp_reward == 0:
            return await ctx.send(f"❌ EXP sudah mencapai batas maksimum untuk realm ini! ({exp_cap} EXP)")
    
    success_chance = min(90, 50 + (p["total_power"] // 5))
    success = random.randint(1, 100) <= success_chance
    
    if success:
        p["exp"] += exp_reward
        p["qi"] += qi_reward
        p["spirit_stones"] += spirit_stones_reward
        p["base_power"] += random.randint(1, 3)
        p["total_power"] = int(p["base_power"] * (1 + sum(t['power_bonus'] for t in p["techniques"])))
        p["dungeons_completed"] += 1
        
        data = load_data()
        data["server_stats"]["total_dungeons"] += 1
        save_data(data)
        
        embed = discord.Embed(
            title=f"🎉 {dungeon_data['emoji']} Dungeon Cleared!",
            description=f"{ctx.author.mention} berhasil menyelesaikan {dungeon_data['name']}!",
            color=0x00ff00
        )
        embed.add_field(name="EXP Reward", value=f"+{exp_reward}", inline=True)
        embed.add_field(name="Qi Reward", value=f"+{qi_reward}", inline=True)
        embed.add_field(name="Spirit Stones", value=f"+{spirit_stones_reward}", inline=True)
        embed.add_field(name="Success Chance", value=f"{success_chance}%", inline=True)
        embed.add_field(name="Total EXP", value=f"{p['exp']}/{exp_cap}", inline=False)
        
    else:
        embed = discord.Embed(
            title=f"💀 {dungeon_data['emoji']} Dungeon Failed!",
            description=f"{ctx.author.mention} gagal menyelesaikan {dungeon_data['name']}...",
            color=0xff0000
        )
        embed.add_field(name="Success Chance", value=f"{success_chance}%", inline=True)
        embed.add_field(name="Tip", value="Tingkatkan power Anda untuk meningkatkan success chance!", inline=False)
    
    update_player(ctx.author.id, p)
    await ctx.send(embed=embed)

# ===============================
# Command: pvp
# ===============================
@bot.command()
async def pvp(ctx, enemy: discord.Member):
    if enemy.id == ctx.author.id:
        return await ctx.send("❌ You can't PvP yourself!")

    attacker = get_player(ctx.author.id)
    defender = get_player(enemy.id)

    now = time.time()
    last_pvp = float(attacker["last_pvp"])
    if last_pvp + 300 > now:
        return await ctx.send("⏳ You must wait 5 minutes before PvP again!")
    
    attacker["last_pvp"] = str(now)

    atk_power = attacker["total_power"] + random.randint(0, 20)
    def_power = defender["total_power"] + random.randint(0, 20)

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
            value=f"W: {pdata['pvp_wins']} | L: {pdata['pvp_losses']} | Power: {pdata['total_power']}",
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
    embed.add_field(name="Total Dungeons", value=stats["total_dungeons"], inline=True)
    embed.add_field(name="Total Techniques Learned", value=stats["total_techniques_learned"], inline=True)
    embed.add_field(name="Last Update", value=stats["last_update"][:19], inline=False)
    
    await ctx.send(embed=embed)

# ===============================
# Start bot
# ===============================
keep_alive()

try:
    bot.run(BOT_TOKEN)
except Exception as e:
    print(f"❌ Error running bot: {e}")
    print(f"🔑 Token: {BOT_TOKEN}")