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

# ===============================
# Global Variables untuk Active Systems
# ===============================
ACTIVE_CULTIVATIONS = {}
ACTIVE_BATTLES = {}

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
            "True Immortal [Entry]", "True Immortal [Middle]", "True Immortal [Peak]",
            "Profound Immortal [Entry]", "Profound Immortal [Middle]", "Profound Immortal [Peak]",
            "Golden Immortal [Entry]", "Golden Immortal [Middle]", "Golden Immortal [Peak]",
            "Mystic Immortal [Entry]", "Mystic Immortal [Middle]", "Mystic Immortal [Peak]",
            "Supreme Immortal [Entry]", "Supreme Immortal [Middle]", "Supreme Immortal [Peak]",
            "Immortal Lord [Entry]", "Immortal Lord [Middle]", "Immortal Lord [Peak]",
            "Immortal Saint [Entry]", "Immortal Saint [Middle]", "Immortal Saint [Peak]",
            "Immortal Ancestor [Entry]", "Immortal Ancestor [Middle]", "Immortal Ancestor [Peak]",
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
            "Lesser God [Entry]", "Lesser God [Middle]", "Lesser God [Peak]",
            "True God [Entry]", "True God [Middle]", "True God [Peak]",
            "Elder God [Entry]", "Elder God [Middle]", "Elder God [Peak]",
            "High God [Entry]", "High God [Middle]", "High God [Peak]",
            "Ancient God [Entry]", "Ancient God [Middle]", "Ancient God [Peak]",
            "Primordial God [Entry]", "Primordial God [Middle]", "Primordial God [Peak]",
            "Supreme God [Entry]", "Supreme God [Middle]", "Supreme God [Peak]",
            "Divine Lord [Entry]", "Divine Lord [Middle]", "Divine Lord [Peak]",
            "Divine Saint [Entry]", "Divine Saint [Middle]", "Divine Saint [Peak]",
            "Divine Ancestor [Entry]", "Divine Ancestor [Middle]", "Divine Ancestor [Peak]",
            "God Sovereign [Entry]", "God Sovereign [Middle]", "God Sovereign [Peak]",
            "God Emperor [Entry]", "God Emperor [Middle]", "God Emperor [Peak]", 
            "God King [Entry]", "God King [Middle]", "God King [Peak]",
            "Celestial Overlord [Entry]", "Celestial Overlord [Middle]", "Celestial Overlord [Peak]",
            "Universe Creator [Entry]", "Universe Creator [Middle]", "Universe Creator [Peak]"
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
# Guild/Sect System
# ===============================
GUILD_BENEFITS = {
    "exp_bonus": 0.15,      # 15% bonus EXP for guild members
    "qi_bonus": 0.10,       # 10% bonus Qi generation
    "spirit_stone_bonus": 0.20,  # 20% bonus Spirit Stones
    "technique_discount": 0.25,   # 25% discount on technique learning
}

GUILD_COSTS = {
    "create": 5000,         # Cost to create a guild
    "join": 500,            # Cost to join a guild
    "upgrade": 10000,       # Cost to upgrade guild level
}

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
    # ===============================
    # MORTAL REALM EQUIPMENT
    # ===============================
    # Tier 1 - Basic (Wood/Cloth)
    "wooden_sword": {"name": "Wooden Sword", "power": 8, "cost": 50, "type": "weapon", "emoji": "⚔️", "realm": "Mortal Realm", "tier": "Basic", "set": "wooden"},
    "cloth_armor": {"name": "Cloth Armor", "power": 5, "cost": 40, "type": "armor", "emoji": "🛡️", "realm": "Mortal Realm", "tier": "Basic", "set": "cloth"},
    "copper_ring": {"name": "Copper Ring", "power": 3, "cost": 30, "type": "accessory", "emoji": "💍", "realm": "Mortal Realm", "tier": "Basic", "set": "copper"},

    # Tier 2 - Common (Iron/Leather)  
    "iron_sword": {"name": "Iron Sword", "power": 15, "cost": 120, "type": "weapon", "emoji": "⚔️", "realm": "Mortal Realm", "tier": "Common", "set": "iron"},
    "leather_armor": {"name": "Leather Armor", "power": 12, "cost": 100, "type": "armor", "emoji": "🛡️", "realm": "Mortal Realm", "tier": "Common", "set": "leather"},
    "iron_ring": {"name": "Iron Ring", "power": 8, "cost": 80, "type": "accessory", "emoji": "💍", "realm": "Mortal Realm", "tier": "Common", "set": "iron"},

    # Tier 3 - Rare (Steel)
    "steel_sword": {"name": "Steel Sword", "power": 25, "cost": 250, "type": "weapon", "emoji": "⚔️", "realm": "Mortal Realm", "tier": "Rare", "set": "steel"},
    "steel_armor": {"name": "Steel Armor", "power": 20, "cost": 200, "type": "armor", "emoji": "🛡️", "realm": "Mortal Realm", "tier": "Rare", "set": "steel"},
    "steel_amulet": {"name": "Steel Amulet", "power": 15, "cost": 180, "type": "accessory", "emoji": "🔮", "realm": "Mortal Realm", "tier": "Rare", "set": "steel"},

    # Tier 4 - Epic (Spirit)
    "spirit_sword": {"name": "Spirit Sword", "power": 40, "cost": 500, "type": "weapon", "emoji": "🗡️", "realm": "Mortal Realm", "tier": "Epic", "set": "spirit"},
    "spirit_armor": {"name": "Spirit Armor", "power": 35, "cost": 450, "type": "armor", "emoji": "🛡️", "realm": "Mortal Realm", "tier": "Epic", "set": "spirit"},
    "spirit_pendant": {"name": "Spirit Pendant", "power": 30, "cost": 400, "type": "accessory", "emoji": "✨", "realm": "Mortal Realm", "tier": "Epic", "set": "spirit"},

    # ===============================
    # IMMORTAL REALM EQUIPMENT  
    # ===============================
    # Tier 1 - Celestial
    "celestial_blade": {"name": "Celestial Blade", "power": 75, "cost": 2000, "type": "weapon", "emoji": "🌟", "realm": "Immortal Realm", "tier": "Celestial", "set": "celestial"},
    "celestial_robes": {"name": "Celestial Robes", "power": 60, "cost": 1800, "type": "armor", "emoji": "👘", "realm": "Immortal Realm", "tier": "Celestial", "set": "celestial"},
    "celestial_crown": {"name": "Celestial Crown", "power": 50, "cost": 1500, "type": "accessory", "emoji": "👑", "realm": "Immortal Realm", "tier": "Celestial", "set": "celestial"},

    # Tier 2 - Void  
    "void_slasher": {"name": "Void Slasher", "power": 120, "cost": 4000, "type": "weapon", "emoji": "🌌", "realm": "Immortal Realm", "tier": "Void", "set": "void"},
    "void_mantle": {"name": "Void Mantle", "power": 100, "cost": 3500, "type": "armor", "emoji": "🌃", "realm": "Immortal Realm", "tier": "Void", "set": "void"},
    "void_orb": {"name": "Void Orb", "power": 80, "cost": 3000, "type": "accessory", "emoji": "🔮", "realm": "Immortal Realm", "tier": "Void", "set": "void"},

    # Tier 3 - Profound
    "profound_saber": {"name": "Profound Saber", "power": 180, "cost": 7000, "type": "weapon", "emoji": "🗡️", "realm": "Immortal Realm", "tier": "Profound", "set": "profound"},
    "profound_vestments": {"name": "Profound Vestments", "power": 150, "cost": 6000, "type": "armor", "emoji": "🥻", "realm": "Immortal Realm", "tier": "Profound", "set": "profound"},
    "profound_talisman": {"name": "Profound Talisman", "power": 120, "cost": 5000, "type": "accessory", "emoji": "📿", "realm": "Immortal Realm", "tier": "Profound", "set": "profound"},

    # Tier 4 - Immortal
    "immortal_dao_sword": {"name": "Immortal Dao Sword", "power": 280, "cost": 12000, "type": "weapon", "emoji": "⚡", "realm": "Immortal Realm", "tier": "Immortal", "set": "immortal"},
    "immortal_phoenix_armor": {"name": "Immortal Phoenix Armor", "power": 240, "cost": 10000, "type": "armor", "emoji": "🔥", "realm": "Immortal Realm", "tier": "Immortal", "set": "immortal"},
    "immortal_lotus_seal": {"name": "Immortal Lotus Seal", "power": 200, "cost": 8000, "type": "accessory", "emoji": "🪷", "realm": "Immortal Realm", "tier": "Immortal", "set": "immortal"},

    # ===============================
    # GOD REALM EQUIPMENT
    # ===============================
    # Tier 1 - Divine
    "divine_judgment": {"name": "Divine Judgment", "power": 400, "cost": 20000, "type": "weapon", "emoji": "⚖️", "realm": "God Realm", "tier": "Divine", "set": "divine"},
    "divine_sanctuary": {"name": "Divine Sanctuary", "power": 350, "cost": 18000, "type": "armor", "emoji": "🏛️", "realm": "God Realm", "tier": "Divine", "set": "divine"},
    "divine_halo": {"name": "Divine Halo", "power": 300, "cost": 15000, "type": "accessory", "emoji": "😇", "realm": "God Realm", "tier": "Divine", "set": "divine"},

    # Tier 2 - Sacred
    "sacred_annihilator": {"name": "Sacred Annihilator", "power": 600, "cost": 35000, "type": "weapon", "emoji": "💥", "realm": "God Realm", "tier": "Sacred", "set": "sacred"},
    "sacred_fortress": {"name": "Sacred Fortress", "power": 500, "cost": 30000, "type": "armor", "emoji": "🏰", "realm": "God Realm", "tier": "Sacred", "set": "sacred"},
    "sacred_eye": {"name": "Sacred Eye", "power": 450, "cost": 25000, "type": "accessory", "emoji": "👁️", "realm": "God Realm", "tier": "Sacred", "set": "sacred"},

    # Tier 3 - Primordial  
    "primordial_chaos": {"name": "Primordial Chaos", "power": 850, "cost": 60000, "type": "weapon", "emoji": "🌀", "realm": "God Realm", "tier": "Primordial", "set": "primordial"},
    "primordial_genesis": {"name": "Primordial Genesis", "power": 750, "cost": 50000, "type": "armor", "emoji": "🌌", "realm": "God Realm", "tier": "Primordial", "set": "primordial"},
    "primordial_core": {"name": "Primordial Core", "power": 650, "cost": 45000, "type": "accessory", "emoji": "⭐", "realm": "God Realm", "tier": "Primordial", "set": "primordial"},

    # Tier 4 - Universe (ENDGAME)
    "universe_creator": {"name": "Universe Creator", "power": 1200, "cost": 100000, "type": "weapon", "emoji": "🌍", "realm": "God Realm", "tier": "Universe", "set": "universe"},
    "universe_mantle": {"name": "Universe Mantle", "power": 1000, "cost": 80000, "type": "armor", "emoji": "🌌", "realm": "God Realm", "tier": "Universe", "set": "universe"},
    "universe_heart": {"name": "Universe Heart", "power": 900, "cost": 70000, "type": "accessory", "emoji": "💫", "realm": "God Realm", "tier": "Universe", "set": "universe"}
}

# Set bonuses for wearing multiple pieces of same set
SET_BONUSES = {
    "wooden": {"2_piece": 0.10, "3_piece": 0.25},
    "cloth": {"2_piece": 0.10, "3_piece": 0.25}, 
    "copper": {"2_piece": 0.10, "3_piece": 0.25},
    "iron": {"2_piece": 0.15, "3_piece": 0.35},
    "leather": {"2_piece": 0.15, "3_piece": 0.35},
    "steel": {"2_piece": 0.20, "3_piece": 0.45},
    "spirit": {"2_piece": 0.25, "3_piece": 0.55},
    "celestial": {"2_piece": 0.30, "3_piece": 0.65},
    "void": {"2_piece": 0.35, "3_piece": 0.75},
    "profound": {"2_piece": 0.40, "3_piece": 0.85},
    "immortal": {"2_piece": 0.50, "3_piece": 1.00},
    "divine": {"2_piece": 0.60, "3_piece": 1.20},
    "sacred": {"2_piece": 0.75, "3_piece": 1.50},
    "primordial": {"2_piece": 1.00, "3_piece": 2.00},
    "universe": {"2_piece": 1.50, "3_piece": 3.00}
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
            "guild": None,           # Guild membership
            "guild_role": None,      # Role in guild
            "base_power": 10,
            "total_power": 10,
            "pvp_wins": 0,
            "pvp_losses": 0,
            "last_pvp": "0",
            "last_dungeon": "0",
            "last_technique_find": "0",
            "last_daily_quest": "0",  # Daily quest system
            "dungeons_completed": 0,
            "techniques_learned": 0,
            "daily_streak": 0,       # Daily login streak
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
            "guild": None,
            "guild_role": None,
            "base_power": player_data.get("power", 10),
            "total_power": player_data.get("power", 10),
            "last_technique_find": "0",
            "last_daily_quest": "0",
            "techniques_learned": 0,
            "daily_streak": 0,
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

def calculate_set_bonus(equipment_dict):
    """Calculate set bonuses from equipment"""
    set_counts = {}
    total_bonus = 0

    # Count items per set
    for item_id in equipment_dict.keys():
        item_data = EQUIPMENT_SHOP.get(item_id, {})
        if "set" in item_data:
            set_name = item_data["set"]
            set_counts[set_name] = set_counts.get(set_name, 0) + 1

    # Calculate bonuses
    for set_name, count in set_counts.items():
        if set_name in SET_BONUSES:
            if count >= 3 and "3_piece" in SET_BONUSES[set_name]:
                total_bonus += SET_BONUSES[set_name]["3_piece"]
            elif count >= 2 and "2_piece" in SET_BONUSES[set_name]:
                total_bonus += SET_BONUSES[set_name]["2_piece"]

    return total_bonus

def get_realm_order_index(realm_name):
    """Get realm order for equipment access checks"""
    realm_order = ["Mortal Realm", "Immortal Realm", "God Realm"]
    return realm_order.index(realm_name) if realm_name in realm_order else 0

def can_access_equipment(player_realm, equipment_realm):
    """Check if player can access equipment from specific realm"""
    player_index = get_realm_order_index(player_realm)
    equipment_index = get_realm_order_index(equipment_realm)
    return player_index >= equipment_index

def create_progress_bar(current, maximum, length=10, filled_char="█", empty_char="░"):
    """Create visual progress bar"""
    if maximum == 0:
        return empty_char * length
    
    progress = min(1.0, current / maximum)
    filled_length = int(length * progress)
    bar = filled_char * filled_length + empty_char * (length - filled_length)
    return f"[{bar}] {progress*100:.1f}%"

def get_all_players():
    """Dapatkan semua data players"""
    data = load_data()
    return data["players"]

# ===============================
# Battle System Functions
# ===============================
async def start_battle(attacker_id, defender_id, ctx):
    """Mulai real-time battle"""
    battle_id = f"{attacker_id}_{defender_id}"

    if battle_id in ACTIVE_BATTLES:
        return await ctx.send("⏳ Battle sedang berlangsung!")

    attacker = get_player(attacker_id)
    defender = get_player(defender_id)

    # Setup battle data
    ACTIVE_BATTLES[battle_id] = {
        "attacker": attacker_id,
        "defender": defender_id,
        "attacker_hp": 100,
        "defender_hp": 100,
        "attacker_power": attacker["total_power"],
        "defender_power": defender["total_power"],
        "round": 0,
        "message": None,
        "active": True,
        "channel_id": ctx.channel.id
    }

    # Kirim battle message
    embed = discord.Embed(
        title="⚔️ Battle Started!",
        description=f"<@{attacker_id}> vs <@{defender_id}>",
        color=0xff0000
    )
    embed.add_field(name="Attacker Power", value=attacker["total_power"], inline=True)
    embed.add_field(name="Defender Power", value=defender["total_power"], inline=True)
    embed.add_field(name="HP", value="❤️ 100% | ❤️ 100%", inline=False)
    embed.set_footer(text="Battle dimulai dalam 3...")

    message = await ctx.send(embed=embed)
    ACTIVE_BATTLES[battle_id]["message"] = message

    # Start battle task
    asyncio.create_task(battle_task(battle_id, ctx))

async def battle_task(battle_id, ctx):
    """Background task untuk battle"""
    try:
        battle_data = ACTIVE_BATTLES[battle_id]

        # Countdown
        for i in range(3, 0, -1):
            if not battle_data["active"]:
                return
            embed = battle_data["message"].embeds[0]
            embed.set_footer(text=f"Battle dimulai dalam {i}...")
            await battle_data["message"].edit(embed=embed)
            await asyncio.sleep(1)

        # Battle rounds
        while (battle_data["attacker_hp"] > 0 and battle_data["defender_hp"] > 0 and 
               battle_data["active"] and battle_data["round"] < 10):

            battle_data["round"] += 1
            await battle_round(battle_id, ctx)
            await asyncio.sleep(2)

        # Battle finished
        await finish_battle(battle_id, ctx)

    except Exception as e:
        print(f"Error in battle task: {e}")
    finally:
        if battle_id in ACTIVE_BATTLES:
            del ACTIVE_BATTLES[battle_id]

async def battle_round(battle_id, ctx):
    """Satu round battle"""
    battle_data = ACTIVE_BATTLES[battle_id]

    # Calculate damage
    att_dmg = max(5, random.randint(10, 20) * battle_data["attacker_power"] // 100)
    def_dmg = max(5, random.randint(10, 20) * battle_data["defender_power"] // 100)

    # Apply damage
    battle_data["defender_hp"] = max(0, battle_data["defender_hp"] - att_dmg)
    battle_data["attacker_hp"] = max(0, battle_data["attacker_hp"] - def_dmg)

    # Update message
    embed = discord.Embed(
        title=f"⚔️ Round {battle_data['round']}",
        description=f"<@{battle_data['attacker']}> vs <@{battle_data['defender']}>",
        color=0xff0000
    )

    embed.add_field(
        name="Action", 
        value=f"<@{battle_data['attacker']}> deals **{att_dmg} damage**!\n<@{battle_data['defender']}> deals **{def_dmg} damage**!",
        inline=False
    )

    # HP bars
    att_hp_bar = "❤️" * (battle_data["attacker_hp"] // 10) + "♡" * (10 - battle_data["attacker_hp"] // 10)
    def_hp_bar = "❤️" * (battle_data["defender_hp"] // 10) + "♡" * (10 - battle_data["defender_hp"] // 10)

    embed.add_field(
        name="HP Status",
        value=f"**Attacker:** {att_hp_bar} {battle_data['attacker_hp']}%\n**Defender:** {def_hp_bar} {battle_data['defender_hp']}%",
        inline=False
    )

    try:
        await battle_data["message"].edit(embed=embed)
    except:
        pass

async def finish_battle(battle_id, ctx):
    """Selesaikan battle dan berikan rewards"""
    battle_data = ACTIVE_BATTLES[battle_id]
    attacker = get_player(battle_data["attacker"])
    defender = get_player(battle_data["defender"])

    # Determine winner
    if battle_data["attacker_hp"] <= 0 or battle_data["defender_hp"] > battle_data["attacker_hp"]:
        winner_id = battle_data["defender"]
        loser_id = battle_data["attacker"]
        result = f"<@{winner_id}> wins!"
    else:
        winner_id = battle_data["attacker"]
        loser_id = battle_data["defender"]
        result = f"<@{winner_id}> wins!"

    # Update player stats
    winner = get_player(winner_id)
    loser = get_player(loser_id)

    winner["pvp_wins"] += 1
    loser["pvp_losses"] += 1

    exp_reward = 50
    spirit_stone_reward = 10

    winner["exp"] = min(winner["exp"] + exp_reward, get_exp_cap(winner))
    winner["spirit_stones"] += spirit_stone_reward
    loser["exp"] = max(0, loser["exp"] - 20)

    update_player(winner_id, winner)
    update_player(loser_id, loser)

    # Update server stats
    data = load_data()
    data["server_stats"]["total_pvp_battles"] += 1
    save_data(data)

    # Final message
    embed = discord.Embed(
        title="🎉 Battle Finished!",
        description=result,
        color=0x00ff00
    )

    embed.add_field(
        name="Rewards",
        value=f"<@{winner_id}>: +{exp_reward} EXP, +{spirit_stone_reward} Spirit Stones\n<@{loser_id}>: -20 EXP",
        inline=False
    )

    embed.add_field(
        name="Record",
        value=f"<@{winner_id}>: {winner['pvp_wins']}W/{winner['pvp_losses']}L\n<@{loser_id}>: {loser['pvp_wins']}W/{loser['pvp_losses']}L",
        inline=True
    )

    try:
        await battle_data["message"].edit(embed=embed)
    except:
        pass

# ===============================
# Idle Cultivation System Functions
# ===============================
async def update_cultivation_message(user_id, player_data, realm_data):
    """Update cultivation status message"""
    if user_id not in ACTIVE_CULTIVATIONS:
        return

    cultivation_data = ACTIVE_CULTIVATIONS[user_id]
    exp_cap = realm_data["exp_cap"]

    # Calculate progress
    progress_percentage = min(100, (player_data["exp"] / exp_cap) * 100)
    progress_bar = "█" * int(progress_percentage / 10) + "░" * (10 - int(progress_percentage / 10))

    # Calculate time elapsed
    time_elapsed = int(time.time() - cultivation_data["start_time"])
    hours, remainder = divmod(time_elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(
        title="🧘 Idle Cultivation Progress",
        description=f"<@{user_id}> sedang meditation...",
        color=0x00ff00
    )

    embed.add_field(name="Status", value="🟢 **ACTIVE** - Cultivating otomatis", inline=True)
    embed.add_field(name="Time Elapsed", value=f"{hours}h {minutes}m {seconds}s", inline=True)
    embed.add_field(name="Total Gained", value=f"{cultivation_data['total_gained']} EXP", inline=True)

    embed.add_field(name="Current EXP", value=f"{player_data['exp']}/{exp_cap}", inline=True)
    embed.add_field(name="Current Qi", value=f"{player_data['qi']}", inline=True)
    embed.add_field(name="Spirit Stones", value=f"{player_data['spirit_stones']}", inline=True)

    embed.add_field(
        name="Progress", 
        value=f"```[{progress_bar}] {progress_percentage:.1f}%```", 
        inline=False
    )

    embed.set_footer(text="Bot akan otomatis berhenti saat EXP cap tercapai")

    try:
        await cultivation_data["message"].edit(embed=embed)
    except:
        pass

async def stop_cultivation(user_id, reason="manual"):
    """Hentikan cultivation dan update message"""
    if user_id not in ACTIVE_CULTIVATIONS:
        return

    cultivation_data = ACTIVE_CULTIVATIONS[user_id]
    cultivation_data["active"] = False

    p = get_player(user_id)
    realm_data = REALMS[p["realm"]]

    # Final message
    time_elapsed = int(time.time() - cultivation_data["start_time"])
    hours, remainder = divmod(time_elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(
        title="🧘 Idle Cultivation Finished",
        color=0xffd700 if reason == "completed" else 0xff0000
    )

    if reason == "completed":
        embed.description = f"<@{user_id}> telah mencapai EXP cap!"
    else:
        embed.description = f"<@{user_id}> menghentikan cultivation."

    embed.add_field(name="Duration", value=f"{hours}h {minutes}m {seconds}s", inline=True)
    embed.add_field(name="Total EXP Gained", value=f"{cultivation_data['total_gained']}", inline=True)
    embed.add_field(name="Final EXP", value=f"{p['exp']}/{realm_data['exp_cap']}", inline=True)

    embed.add_field(name="Qi Gained", value=f"+{p['qi']}", inline=True)
    embed.add_field(name="Spirit Stones Gained", value=f"+{p['spirit_stones']}", inline=True)
    embed.add_field(name="Power Increased", value=f"+{p['base_power'] - 10}", inline=True)

    try:
        await cultivation_data["message"].edit(embed=embed)
    except:
        pass

    # Remove from active cultivations
    if user_id in ACTIVE_CULTIVATIONS:
        del ACTIVE_CULTIVATIONS[user_id]

async def idle_cultivation_task(user_id, player_data, realm_data):
    """Background task untuk idle cultivation"""
    try:
        while user_id in ACTIVE_CULTIVATIONS and ACTIVE_CULTIVATIONS[user_id]["active"]:
            p = get_player(user_id)
            exp_cap = realm_data["exp_cap"]

            # Cek jika sudah cap
            if p["exp"] >= exp_cap:
                break

            # Calculate gains
            base_gain = random.randint(5, 15)
            gain = int(base_gain * realm_data["exp_multiplier"])
            qi_gain = random.randint(1, 5)
            power_gain = random.randint(1, 3)
            spirit_stones_gain = random.randint(1, realm_data["spirit_stone_gain"])

            # Adjust gain jika melebihi cap
            if p["exp"] + gain > exp_cap:
                gain = exp_cap - p["exp"]

            # Update player
            p["exp"] += gain
            p["qi"] += qi_gain
            p["base_power"] += power_gain
            p["spirit_stones"] += spirit_stones_gain

            # Update power dengan teknik bonuses
            technique_bonus = 1 + sum(t['power_bonus'] for t in p["techniques"])
            p["total_power"] = int(p["base_power"] * technique_bonus)

            update_player(user_id, p)

            # Update cultivation data
            ACTIVE_CULTIVATIONS[user_id]["total_gained"] += gain

            # Update message setiap 30 detik
            if time.time() - ACTIVE_CULTIVATIONS[user_id].get("last_update", 0) >= 30:
                await update_cultivation_message(user_id, p, realm_data)
                ACTIVE_CULTIVATIONS[user_id]["last_update"] = time.time()

            # Wait 1 menit antara cultivation
            await asyncio.sleep(60)

    except Exception as e:
        print(f"Error in cultivation task: {e}")
    finally:
        # Cleanup
        if user_id in ACTIVE_CULTIVATIONS:
            await stop_cultivation(user_id, "completed")

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
        # Create a compact stage list
        stages_list = " → ".join(realm_data["stages"])

        # Due to Discord character limits, we'll show first few stages and indicate total
        if len(stages_list) > 800:  # Keep within Discord embed field limits
            first_5_stages = " → ".join(realm_data["stages"][:5])
            stages_display = f"{first_5_stages} → ... ({len(realm_data['stages'])} total stages)"
        else:
            stages_display = stages_list

        embed.add_field(
            name=f"{realm_name} 🌟 ({len(realm_data['stages'])} Stages)",
            value=f"**EXP Cap:** {realm_data['exp_cap']:,} | **Power:** {realm_data['power_multiplier']}× | **Stones:** {realm_data['spirit_stone_gain']}/cultivate\n\n"
                  f"**Progression Path:**\n{stages_display}",
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
            value=f"**{next_stage}**\nButuh: {exp_needed} EXP",
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

    embed.set_footer(text="Total stages: Mortal(30) + Immortal(36) + God(45) = 111 stages")
    await ctx.send(embed=embed)

# ===============================
# Command: cultivate (dengan cooldown)
# ===============================
@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def cultivate(ctx):
    """Cultivate manual sekali"""
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
# Command: start_cultivate (IDLE SYSTEM)
# ===============================
@bot.command()
async def start_cultivate(ctx):
    """Mulai cultivation idle secara otomatis"""
    p = get_player(ctx.author.id)
    realm_data = REALMS[p["realm"]]
    exp_cap = realm_data["exp_cap"]

    # Cek jika sudah mencapai cap
    if p["exp"] >= exp_cap:
        return await ctx.send(f"❌ EXP sudah mencapai batas maksimum! ({exp_cap} EXP)")

    # Cek jika sudah cultivating
    if ctx.author.id in ACTIVE_CULTIVATIONS:
        return await ctx.send("⏳ Anda sudah sedang cultivating! Gunakan `!stop_cultivate` untuk berhenti.")

    embed = discord.Embed(
        title="🧘 Starting Idle Cultivation",
        description=f"{ctx.author.mention} mulai meditation...",
        color=0x00ff00
    )
    embed.add_field(name="Status", value="🟢 **ACTIVE** - Cultivating otomatis", inline=True)
    embed.add_field(name="EXP Cap", value=f"{exp_cap}", inline=True)
    embed.add_field(name="Current EXP", value=f"{p['exp']}", inline=True)
    embed.set_footer(text="Bot akan otomatis berhenti saat EXP cap tercapai")

    message = await ctx.send(embed=embed)

    # Start idle cultivation
    ACTIVE_CULTIVATIONS[ctx.author.id] = {
        "message": message,
        "start_time": time.time(),
        "total_gained": 0,
        "active": True,
        "last_update": 0
    }

    # Start background task
    asyncio.create_task(idle_cultivation_task(ctx.author.id, p, realm_data))

# ===============================
# Command: stop_cultivate
# ===============================
@bot.command()
async def stop_cultivate(ctx):
    """Hentikan cultivation idle"""
    if ctx.author.id not in ACTIVE_CULTIVATIONS:
        return await ctx.send("❌ Anda tidak sedang cultivating!")

    await stop_cultivation(ctx.author.id, "manual")
    await ctx.send("✅ Idle cultivation dihentikan!")

# ===============================
# Command: cultivate_status
# ===============================
@bot.command()
async def cultivate_status(ctx):
    """Cek status cultivation idle"""
    if ctx.author.id not in ACTIVE_CULTIVATIONS:
        return await ctx.send("❌ Anda tidak sedang cultivation! Gunakan `!start_cultivate` untuk mulai.")

    cultivation_data = ACTIVE_CULTIVATIONS[ctx.author.id]
    duration = time.time() - cultivation_data["start_time"]
    hours = duration / 3600

    p = get_player(ctx.author.id)
    realm_data = REALMS[p["realm"]]

    exp_gain = int(hours * 410 * realm_data["exp_multiplier"])
    qi_gain = int(hours * 405)
    spirit_stones_gain = int(hours * (realm_data["spirit_stone_gain"] + 400))

    embed = discord.Embed(
        title="🧘 Cultivation Status",
        description=f"{ctx.author.mention}'s idle cultivation progress",
        color=0x00ff00
    )
    embed.add_field(name="Duration", value=f"{hours:.1f} hours", inline=True)
    embed.add_field(name="EXP Gained", value=f"+{exp_gain}", inline=True)
    embed.add_field(name="Qi Gained", value=f"+{qi_gain}", inline=True)
    embed.add_field(name="Spirit Stones", value=f"+{spirit_stones_gain}", inline=True)
    embed.add_field(name="Rate", value=f"{410 * realm_data['exp_multiplier']} EXP/hour", inline=True)

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

    # Calculate bonuses for display
    technique_bonus = sum(t['power_bonus'] for t in p['techniques'])
    set_bonus = calculate_set_bonus(p['equipment'])
    total_bonus = technique_bonus + set_bonus

    embed.add_field(
        name="⭐ Power Stats",
        value=f"**Total:** {p['total_power']}\n**Base:** {p['base_power']}\n**Technique Bonus:** +{technique_bonus*100:.0f}%\n**Set Bonus:** +{set_bonus*100:.0f}%",
        inline=True
    )

    embed.add_field(
        name="💎 Resources",
        value=f"EXP: {p['exp']}/{exp_cap}\nQi: {p['qi']}\nSpirit Stones: {p['spirit_stones']}",
        inline=True
    )

    embed.add_field(
        name="📈 EXP Progress",
        value=f"```{create_progress_bar(p['exp'], exp_cap, 15)}```",
        inline=False
    )
    
    # Guild info if member
    if p.get("guild"):
        data = load_data()
        if "guilds" in data and p["guild"] in data["guilds"]:
            guild_data = data["guilds"][p["guild"]]
            embed.add_field(
                name="🏰 Guild",
                value=f"{guild_data['name']} (Level {guild_data['level']})\nRole: {p['guild_role']}",
                inline=True
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
async def shop(ctx, realm: str = None):
    """Lihat item yang tersedia di shop - gunakan !shop [realm] untuk filter"""
    p = get_player(ctx.author.id)
    player_realm = p["realm"]

    # Organize equipment by realm
    realms_equipment = {
        "Mortal Realm": [],


# ===============================
# Guild System Commands
# ===============================
@bot.command()
async def create_guild(ctx, *, guild_name: str):
    """Create a cultivation guild"""
    p = get_player(ctx.author.id)
    data = load_data()
    
    if p["guild"]:
        return await ctx.send("❌ You're already in a guild! Leave first with `!leave_guild`")
    
    if p["spirit_stones"] < GUILD_COSTS["create"]:
        return await ctx.send(f"❌ Need {GUILD_COSTS['create']} Spirit Stones to create a guild!")
    
    # Initialize guilds if not exists
    if "guilds" not in data:
        data["guilds"] = {}
    
    guild_id = guild_name.lower().replace(" ", "_")
    if guild_id in data["guilds"]:
        return await ctx.send("❌ Guild name already exists!")
    
    # Create guild
    data["guilds"][guild_id] = {
        "name": guild_name,
        "leader": str(ctx.author.id),
        "members": {str(ctx.author.id): "Leader"},
        "level": 1,
        "exp": 0,
        "treasury": 0,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    # Update player
    p["spirit_stones"] -= GUILD_COSTS["create"]
    p["guild"] = guild_id
    p["guild_role"] = "Leader"
    
    update_player(ctx.author.id, p)
    save_data(data)
    
    embed = discord.Embed(
        title="🏰 Guild Created!",
        description=f"{ctx.author.mention} created guild **{guild_name}**!",
        color=0x00ff00
    )
    embed.add_field(name="Guild Level", value="1", inline=True)
    embed.add_field(name="Members", value="1", inline=True)
    embed.add_field(name="Cost", value=f"{GUILD_COSTS['create']} Spirit Stones", inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def join_guild(ctx, *, guild_name: str):
    """Join an existing guild"""
    p = get_player(ctx.author.id)
    data = load_data()
    
    if p["guild"]:
        return await ctx.send("❌ You're already in a guild!")
    
    if p["spirit_stones"] < GUILD_COSTS["join"]:
        return await ctx.send(f"❌ Need {GUILD_COSTS['join']} Spirit Stones to join a guild!")
    
    if "guilds" not in data:
        return await ctx.send("❌ No guilds exist yet!")
    
    guild_id = guild_name.lower().replace(" ", "_")
    if guild_id not in data["guilds"]:
        return await ctx.send("❌ Guild not found!")
    
    guild_data = data["guilds"][guild_id]
    if len(guild_data["members"]) >= 20:  # Max 20 members
        return await ctx.send("❌ Guild is full! (Max 20 members)")
    
    # Join guild
    guild_data["members"][str(ctx.author.id)] = "Member"
    p["spirit_stones"] -= GUILD_COSTS["join"]
    p["guild"] = guild_id
    p["guild_role"] = "Member"
    
    update_player(ctx.author.id, p)
    save_data(data)
    
    await ctx.send(f"✅ {ctx.author.mention} joined guild **{guild_data['name']}**!")

@bot.command()
async def guild_info(ctx, *, guild_name: str = None):
    """View guild information"""
    data = load_data()
    p = get_player(ctx.author.id)
    
    if "guilds" not in data:
        return await ctx.send("❌ No guilds exist yet!")
    
    # Use player's guild if no name specified
    if not guild_name:
        if not p["guild"]:
            return await ctx.send("❌ You're not in a guild! Specify a guild name.")
        guild_id = p["guild"]
    else:
        guild_id = guild_name.lower().replace(" ", "_")
    
    if guild_id not in data["guilds"]:
        return await ctx.send("❌ Guild not found!")
    
    guild_data = data["guilds"][guild_id]
    
    # Get member list
    member_list = []
    for member_id, role in guild_data["members"].items():
        try:
            user = await bot.fetch_user(int(member_id))
            member_list.append(f"{role}: {user.name}")
        except:
            member_list.append(f"{role}: Unknown User")
    
    embed = discord.Embed(
        title=f"🏰 Guild: {guild_data['name']}",
        color=0x7289da
    )
    embed.add_field(name="Level", value=guild_data["level"], inline=True)
    embed.add_field(name="Members", value=f"{len(guild_data['members'])}/20", inline=True)
    embed.add_field(name="Treasury", value=f"{guild_data['treasury']} Spirit Stones", inline=True)
    embed.add_field(name="Members List", value="\n".join(member_list), inline=False)
    embed.add_field(name="Created", value=guild_data["created_at"][:10], inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def guilds(ctx):
    """List all guilds"""
    data = load_data()
    
    if "guilds" not in data or not data["guilds"]:
        return await ctx.send("❌ No guilds exist yet! Create one with `!create_guild <name>`")
    
    embed = discord.Embed(
        title="🏰 All Guilds",
        description="Use `!guild_info <name>` for details",
        color=0x7289da
    )
    
    for guild_id, guild_data in data["guilds"].items():
        member_count = len(guild_data["members"])
        embed.add_field(
            name=f"{guild_data['name']} (Level {guild_data['level']})",
            value=f"Members: {member_count}/20\nTreasury: {guild_data['treasury']} Stones",
            inline=True
        )
    
    await ctx.send(embed=embed)

# ===============================
# Daily Quest System
# ===============================
DAILY_QUESTS = [
    {"id": "cultivate_5", "name": "Cultivate 5 times", "reward": {"exp": 100, "spirit_stones": 20}, "progress_needed": 5},
    {"id": "pvp_battle", "name": "Win 1 PvP battle", "reward": {"exp": 150, "qi": 50}, "progress_needed": 1},
    {"id": "complete_dungeon", "name": "Complete 2 dungeons", "reward": {"spirit_stones": 30, "qi": 100}, "progress_needed": 2},
    {"id": "learn_technique", "name": "Learn a new technique", "reward": {"exp": 200, "spirit_stones": 50}, "progress_needed": 1},
    {"id": "breakthrough", "name": "Achieve breakthrough", "reward": {"exp": 300, "spirit_stones": 100}, "progress_needed": 1}
]

@bot.command()
async def daily_quests(ctx):
    """View today's daily quests"""
    p = get_player(ctx.author.id)
    
    # Initialize daily quest data
    if "daily_quests" not in p:
        p["daily_quests"] = {}
        p["last_daily_reset"] = datetime.date.today().isoformat()
    
    # Check if daily reset needed
    today = datetime.date.today().isoformat()
    if p.get("last_daily_reset", "") != today:
        p["daily_quests"] = {}
        p["last_daily_reset"] = today
        p["daily_streak"] += 1
    
    embed = discord.Embed(
        title="📋 Daily Quests",
        description=f"Daily Streak: {p['daily_streak']} days",
        color=0xffd700
    )
    
    # Generate daily quests (3 random quests)
    import random
    available_quests = random.sample(DAILY_QUESTS, 3)
    
    for quest in available_quests:
        quest_progress = p["daily_quests"].get(quest["id"], 0)
        completed = quest_progress >= quest["progress_needed"]
        
        status_emoji = "✅" if completed else "⏳"
        progress_text = f"{quest_progress}/{quest['progress_needed']}"
        
        reward_text = ", ".join([f"{amount} {resource.replace('_', ' ').title()}" 
                               for resource, amount in quest["reward"].items()])
        
        embed.add_field(
            name=f"{status_emoji} {quest['name']}",
            value=f"Progress: {progress_text}\nReward: {reward_text}",
            inline=False
        )
    
    update_player(ctx.author.id, p)
    await ctx.send(embed=embed)

@bot.command()
async def claim_daily(ctx):
    """Claim completed daily quest rewards"""
    p = get_player(ctx.author.id)
    
    if "daily_quests" not in p:
        return await ctx.send("❌ No daily quests data! Use `!daily_quests` first.")
    
    # Check for completed quests
    completed_quests = []
    total_rewards = {"exp": 0, "qi": 0, "spirit_stones": 0}
    
    import random
    available_quests = random.sample(DAILY_QUESTS, 3)
    
    for quest in available_quests:
        quest_progress = p["daily_quests"].get(quest["id"], 0)
        if quest_progress >= quest["progress_needed"]:
            completed_quests.append(quest["name"])
            for resource, amount in quest["reward"].items():
                total_rewards[resource] += amount
            # Mark as claimed
            p["daily_quests"][quest["id"]] = -1
    
    if not completed_quests:
        return await ctx.send("❌ No completed quests to claim!")
    
    # Apply rewards
    exp_cap = get_exp_cap(p)
    if total_rewards["exp"] > 0:
        p["exp"] = min(p["exp"] + total_rewards["exp"], exp_cap)
    
    p["qi"] += total_rewards["qi"]
    p["spirit_stones"] += total_rewards["spirit_stones"]
    
    update_player(ctx.author.id, p)
    
    embed = discord.Embed(
        title="🎉 Daily Rewards Claimed!",
        color=0x00ff00
    )
    embed.add_field(name="Completed Quests", value="\n".join(completed_quests), inline=False)
    embed.add_field(name="Rewards", value=f"EXP: +{total_rewards['exp']}\nQi: +{total_rewards['qi']}\nSpirit Stones: +{total_rewards['spirit_stones']}", inline=True)
    
    await ctx.send(embed=embed)

# ===============================
# Seasonal Events
# ===============================
@bot.command()
async def seasonal_event(ctx):
    """Check current seasonal event"""
    import calendar
    
    now = datetime.datetime.now()
    month = now.month
    
    events = {
        1: {"name": "New Year Blessing", "bonus": "Double EXP from cultivation", "emoji": "🎊"},
        2: {"name": "Lunar Festival", "bonus": "25% discount on techniques", "emoji": "🏮"},
        3: {"name": "Spring Awakening", "bonus": "Extra Qi from all activities", "emoji": "🌸"},
        6: {"name": "Summer Solstice", "bonus": "Dungeon rewards increased", "emoji": "☀️"},
        10: {"name": "Autumn Harvest", "bonus": "Spirit Stone gain doubled", "emoji": "🍂"},
        12: {"name": "Winter Meditation", "bonus": "Breakthrough costs reduced", "emoji": "❄️"}
    }
    
    if month in events:
        event = events[month]
        embed = discord.Embed(
            title=f"{event['emoji']} Current Event: {event['name']}",
            description=f"**Special Bonus:** {event['bonus']}",
            color=0xff6b9d
        )
        embed.add_field(name="Duration", value=f"All of {calendar.month_name[month]}", inline=True)
    else:
        embed = discord.Embed(

    elif category.lower() == "guild":
        embed = discord.Embed(
            title="🏰 Guild Commands",
            description="Join forces with other cultivators and grow stronger together!",
            color=0x7289da
        )

        embed.add_field(
            name="🏰 Guild Management",
            value="`!create_guild <name>` - Create a new guild (5000 Spirit Stones)\n"
                  "`!join_guild <name>` - Join an existing guild (500 Spirit Stones)\n"
                  "`!leave_guild` - Leave your current guild\n"
                  "`!guild_info [name]` - View guild information",
            inline=False
        )

        embed.add_field(
            name="📋 Guild Features",
            value="`!guilds` - List all available guilds\n"
                  "`!guild_donate <amount>` - Donate to guild treasury\n"
                  "`!guild_benefits` - View guild member benefits",
            inline=False
        )

        embed.set_footer(text="🌟 Guild Benefits: +15% EXP, +10% Qi, +20% Spirit Stones, -25% Technique costs!")

    elif category.lower() == "daily":
        embed = discord.Embed(
            title="📋 Daily & Events Commands",
            description="Complete daily quests and participate in seasonal events!",
            color=0xffd700
        )

        embed.add_field(
            name="📋 Daily Quests",
            value="`!daily_quests` - View today's daily quests\n"
                  "`!claim_daily` - Claim completed quest rewards\n"
                  "`!daily_streak` - View your login streak",
            inline=False
        )

        embed.add_field(
            name="🎉 Events",
            value="`!seasonal_event` - Check current seasonal event\n"
                  "`!event_rewards` - View available event rewards",
            inline=False
        )

        embed.set_footer(text="🎯 Daily quests reset every 24 hours! Keep your streak going!")


            title="🌟 No Active Event",
            description="Check back next month for seasonal bonuses!",
            color=0x888888
        )
    
    await ctx.send(embed=embed)


        "Immortal Realm": [],
        "God Realm": []
    }

    for item_id, item_data in EQUIPMENT_SHOP.items():
        realm_name = item_data["realm"]
        if realm_name in realms_equipment:
            realms_equipment[realm_name].append((item_id, item_data))

    # If specific realm requested, show only that realm
    if realm and realm.lower().replace(" ", "_") in ["mortal", "mortal_realm", "immortal", "immortal_realm", "god", "god_realm"]:
        if realm.lower() in ["mortal", "mortal_realm"]:
            target_realm = "Mortal Realm"
        elif realm.lower() in ["immortal", "immortal_realm"]:
            target_realm = "Immortal Realm"
        elif realm.lower() in ["god", "god_realm"]:
            target_realm = "God Realm"

        embed = discord.Embed(
            title=f"🏪 {target_realm} Equipment Shop",
            description=f"Equipment for **{target_realm}** cultivators\nUse `!buy <item_name>` to purchase",
            color=0xffd700
        )

        can_access = can_access_equipment(player_realm, target_realm)
        access_status = "✅ Accessible" if can_access else "❌ Realm Too Low"
        embed.add_field(name="Access Status", value=access_status, inline=False)

        for item_id, item_data in realms_equipment[target_realm]:
            embed.add_field(
                name=f"{item_data['emoji']} {item_data['name']} - {item_data['cost']:,} Qi",
                value=f"**Power:** +{item_data['power']} | **Type:** {item_data['type']}\n**Tier:** {item_data['tier']} | **Set:** {item_data['set']}\nID: `{item_id}`",
                inline=False
            )

    else:
        # Show overview of all realms
        embed = discord.Embed(
            title="🏪 Cultivation Equipment Shop",
            description=f"**Your Realm:** {player_realm}\nUse `!shop [realm]` for detailed view\nExample: `!shop mortal`, `!shop immortal`, `!shop god`",
            color=0xffd700
        )

        for realm_name, items in realms_equipment.items():
            if not items:
                continue

            can_access = can_access_equipment(player_realm, realm_name)
            access_emoji = "✅" if can_access else "🔒"

            # Show first few items as preview
            preview_items = items[:3]
            preview_text = ""
            for item_id, item_data in preview_items:
                preview_text += f"{item_data['emoji']} {item_data['name']} ({item_data['cost']:,} Qi)\n"

            if len(items) > 3:
                preview_text += f"... and {len(items)-3} more items"

            embed.add_field(
                name=f"{access_emoji} {realm_name} ({len(items)} items)",
                value=preview_text or "No items",
                inline=False
            )

    embed.set_footer(text="💡 Tip: Higher realms unlock more powerful equipment!")
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

    # Check realm requirement
    if not can_access_equipment(p["realm"], item_data["realm"]):
        required_realm = item_data["realm"]
        return await ctx.send(f"❌ Realm tidak cukup tinggi! Item ini membutuhkan **{required_realm}** atau lebih tinggi. Anda masih di **{p['realm']}**.")

    if p["qi"] < item_data["cost"]:
        return await ctx.send(f"❌ Qi tidak cukup! Butuh {item_data['cost']} Qi, Anda punya {p['qi']} Qi.")

    # Remove old equipment of same type
    old_equipment_power = 0
    current_equipment = p["equipment"]
    for eq_id, eq_power in current_equipment.items():
        if EQUIPMENT_SHOP.get(eq_id, {}).get("type") == item_data["type"]:
            old_equipment_power = eq_power
            p["base_power"] -= eq_power
            break

    # Add new equipment
    p["qi"] -= item_data["cost"]
    p["equipment"][item_name] = item_data["power"]
    p["base_power"] += item_data["power"]

    # Calculate set bonus
    set_bonus = calculate_set_bonus(p["equipment"])
    technique_bonus = sum(t['power_bonus'] for t in p["techniques"])

    # Update total power with set bonuses
    p["total_power"] = int(p["base_power"] * (1 + technique_bonus + set_bonus))

    update_player(ctx.author.id, p)

    # Create enhanced purchase message
    embed = discord.Embed(
        title="🛍️ Purchase Successful!",
        description=f"{ctx.author.mention} membeli {item_data['emoji']} {item_data['name']}",
        color=0x00ff00
    )
    embed.add_field(name="Power", value=f"+{item_data['power']}", inline=True)
    embed.add_field(name="Tier", value=f"{item_data['tier']} ({item_data['realm']})", inline=True)
    embed.add_field(name="Cost", value=f"{item_data['cost']} Qi", inline=True)

    if set_bonus > 0:
        embed.add_field(name="Set Bonus", value=f"+{set_bonus*100:.0f}% Total Power", inline=True)

    embed.add_field(name="Total Power", value=f"{p['total_power']}", inline=True)
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
    set_bonus = calculate_set_bonus(p["equipment"])

    embed = discord.Embed(
        title=f"🎒 {ctx.author.name}'s Inventory",
        description=f"Total Equipment Power: +{total_equip_power}\nSet Bonus: +{set_bonus*100:.0f}% Total Power",
        color=0x7289da
    )

    for item_id, power in p["equipment"].items():
        item_data = EQUIPMENT_SHOP.get(item_id, {"name": item_id.replace("_", " ").title(), "type": "unknown", "emoji": "⚙️"})

        # Check enchantment level
        enchant_level = p.get("enchanted", {}).get(item_id, 0)
        enchant_text = f" +{enchant_level}" if enchant_level > 0 else ""
        tier_text = f" ({item_data.get('tier', 'Unknown')})" if 'tier' in item_data else ""

        embed.add_field(
            name=f"{item_data['emoji']} {item_data['name']}{enchant_text}",
            value=f"**Power:** +{power} | **Type:** {item_data['type']}{tier_text}\n**Set:** {item_data.get('set', 'None')}",
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

    # Recalculate total power with updated set bonuses
    set_bonus = calculate_set_bonus(p["equipment"])
    technique_bonus = sum(t['power_bonus'] for t in p["techniques"])
    p["total_power"] = int(p["base_power"] * (1 + technique_bonus + set_bonus))

    update_player(ctx.author.id, p)

    await ctx.send(f"💰 {ctx.author.mention} menjual {item_data['name']} dan mendapatkan {sell_price} Qi!")

# ===============================
# Command: enchant (Equipment Enhancement)
# ===============================
@bot.command()
async def enchant(ctx, *, item_name: str):
    """Upgrade equipment dengan Spirit Stones"""
    item_name = item_name.lower().replace(" ", "_")

    p = get_player(ctx.author.id)

    if item_name not in p["equipment"]:
        return await ctx.send("❌ Item tidak ditemukan di inventory! Gunakan `!inventory` untuk melihat equipment Anda.")

    if "enchanted" not in p:
        p["enchanted"] = {}

    current_enchant = p["enchanted"].get(item_name, 0)
    max_enchant = 10  # Maximum +10 enchantment

    if current_enchant >= max_enchant:
        return await ctx.send(f"❌ {EQUIPMENT_SHOP.get(item_name, {}).get('name', item_name)} sudah mencapai enchantment maksimum (+{max_enchant})!")

    # Calculate cost based on current enchant level
    base_cost = 50
    enchant_cost = base_cost * (current_enchant + 1) * (current_enchant + 1)  # Exponential cost

    if p["spirit_stones"] < enchant_cost:
        return await ctx.send(f"❌ Spirit Stones tidak cukup! Butuh {enchant_cost} Spirit Stones, Anda punya {p['spirit_stones']}.")

    # Calculate success rate (decreases with higher enchant levels)
    success_rate = max(20, 100 - (current_enchant * 8))  # 100% -> 92% -> 84% ... -> 20%

    import random
    success = random.randint(1, 100) <= success_rate

    p["spirit_stones"] -= enchant_cost

    if success:
        # Success! Increase enchantment
        p["enchanted"][item_name] = current_enchant + 1
        new_enchant = current_enchant + 1

        # Increase base power of the item
        power_increase = 5 + (new_enchant * 2)  # +5, +7, +9, +11, etc.
        p["equipment"][item_name] += power_increase
        p["base_power"] += power_increase

        # Recalculate total power with bonuses
        set_bonus = calculate_set_bonus(p["equipment"])
        technique_bonus = sum(t['power_bonus'] for t in p["techniques"])
        p["total_power"] = int(p["base_power"] * (1 + technique_bonus + set_bonus))

        update_player(ctx.author.id, p)

        item_display_name = EQUIPMENT_SHOP.get(item_name, {}).get('name', item_name.replace('_', ' ').title())

        embed = discord.Embed(
            title="✨ Enchantment Successful!",
            description=f"{ctx.author.mention} berhasil meng-enchant {item_display_name}!",
            color=0x00ff00
        )
        embed.add_field(name="New Level", value=f"+{new_enchant} Enhancement", inline=True)
        embed.add_field(name="Power Boost", value=f"+{power_increase} Power", inline=True)
        embed.add_field(name="Cost", value=f"{enchant_cost} Spirit Stones", inline=True)
        embed.add_field(name="Total Power", value=f"{p['total_power']}", inline=True)
        embed.add_field(name="Success Rate", value=f"{success_rate}%", inline=True)
        embed.add_field(name="Remaining Stones", value=f"{p['spirit_stones']}", inline=True)

        await ctx.send(embed=embed)

    else:
        # Failed! No enchantment increase, just consume stones
        update_player(ctx.author.id, p)

        item_display_name = EQUIPMENT_SHOP.get(item_name, {}).get('name', item_name.replace('_', ' ').title())

        embed = discord.Embed(
            title="💥 Enchantment Failed!",
            description=f"{ctx.author.mention} gagal meng-enchant {item_display_name}...",
            color=0xff0000
        )
        embed.add_field(name="Current Level", value=f"+{current_enchant} Enhancement", inline=True)
        embed.add_field(name="Success Rate", value=f"{success_rate}%", inline=True)
        embed.add_field(name="Cost", value=f"{enchant_cost} Spirit Stones", inline=True)
        embed.add_field(name="Remaining Stones", value=f"{p['spirit_stones']}", inline=True)
        embed.set_footer(text="💡 Tip: Higher enhancement levels have lower success rates!")

        await ctx.send(embed=embed)

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
# Command: pvp (REAL-TIME BATTLE)
# ===============================
@bot.command()
async def pvp(ctx, enemy: discord.Member):
    """Battle real-time melawan player lain"""
    if enemy.id == ctx.author.id:
        return await ctx.send("❌ You can't PvP yourself!")

    attacker = get_player(ctx.author.id)
    defender = get_player(enemy.id)

    now = time.time()
    last_pvp = float(attacker["last_pvp"])
    if last_pvp + 300 > now:
        return await ctx.send("⏳ You must wait 5 minutes before PvP again!")

    attacker["last_pvp"] = str(now)
    update_player(ctx.author.id, attacker)

    # Start real-time battle
    await start_battle(ctx.author.id, enemy.id, ctx)

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
# Command: leaderboard
# ===============================
@bot.command()
async def leaderboard(ctx, page: int = 1):
    """Leaderboard cultivation berdasarkan stage tertinggi"""
    data = load_data()
    players = data["players"]

    # Filter hanya players yang memiliki data lengkap
    valid_players = []
    for uid, pdata in players.items():
        if all(key in pdata for key in ["realm", "stage", "total_power"]):
            valid_players.append((uid, pdata))

    if not valid_players:
        return await ctx.send("❌ No players found for leaderboard!")

    # Calculate cultivation score (realm + stage)
    def calculate_cultivation_score(player_data):
        realm = player_data["realm"]
        stage = player_data["stage"]

        # Realm weight (semakin tinggi realm, score lebih tinggi)
        realm_weights = {"Mortal Realm": 0, "Immortal Realm": 1000, "God Realm": 2000}
        realm_score = realm_weights.get(realm, 0)

        # Stage progress within realm
        if realm in REALMS and stage in REALMS[realm]["stages"]:
            stage_index = REALMS[realm]["stages"].index(stage)
            total_stages = len(REALMS[realm]["stages"])
            stage_score = (stage_index / total_stages) * 1000  # Normalize to 0-1000
        else:
            stage_score = 0

        return realm_score + stage_score

    # Sort by cultivation score
    ranked_players = []
    for uid, pdata in valid_players:
        try:
            user = await bot.fetch_user(int(uid))
            username = user.name
        except:
            username = f"Unknown User ({uid})"

        score = calculate_cultivation_score(pdata)
        ranked_players.append({
            "username": username,
            "realm": pdata["realm"],
            "stage": pdata["stage"],
            "power": pdata["total_power"],
            "score": score,
            "user_id": uid
        })

    # Sort by score descending
    ranked_players.sort(key=lambda x: x["score"], reverse=True)

    # Pagination
    items_per_page = 10
    total_pages = (len(ranked_players) + items_per_page - 1) // items_per_page
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_players = ranked_players[start_idx:end_idx]

    # Create embed
    embed = discord.Embed(
        title="🏆 Cultivation Leaderboard",
        description="Ranking berdasarkan realm dan stage tertinggi",
        color=0xFFD700
    )

    # Add ranking entries
    for i, player in enumerate(page_players, start=start_idx + 1):
        realm_emoji = "🌍" if player["realm"] == "Mortal Realm" else "🌟" if player["realm"] == "Immortal Realm" else "✨"

        embed.add_field(
            name=f"#{i} {realm_emoji} {player['username']}",
            value=f"**{player['realm']}** - {player['stage']}\n"
                  f"⚡ Power: {player['power']} | 📊 Score: {player['score']:.1f}",
            inline=False
        )

    # Add footer with pagination info
    embed.set_footer(text=f"Page {page}/{total_pages} • Total players: {len(ranked_players)}")

    await ctx.send(embed=embed)

# ===============================
# Command: top
# ===============================
@bot.command()
async def top(ctx, count: int = 5):
    """Top cultivation players (default: top 5)"""
    count = max(1, min(count, 20))  # Limit to 20 players

    data = load_data()
    players = data["players"]

    # Get top players by realm progression
    top_players = []
    for uid, pdata in players.items():
        if all(key in pdata for key in ["realm", "stage", "total_power"]):
            # Calculate progression index
            realm_order = list(REALMS.keys())
            if pdata["realm"] in realm_order and pdata["stage"] in REALMS[pdata["realm"]]["stages"]:
                realm_idx = realm_order.index(pdata["realm"])
                stage_idx = REALMS[pdata["realm"]]["stages"].index(pdata["stage"])
                progression = (realm_idx * 100) + stage_idx
                top_players.append((uid, pdata, progression))

    if not top_players:
        return await ctx.send("❌ No players found!")

    # Sort by progression
    top_players.sort(key=lambda x: x[2], reverse=True)
    top_players = top_players[:count]

    embed = discord.Embed(
        title=f"👑 Top {count} Cultivators",
        color=0xFFD700
    )

    for i, (uid, pdata, progression) in enumerate(top_players, 1):
        try:
            user = await bot.fetch_user(int(uid))
            username = user.name
        except:
            username = f"Unknown User ({uid})"

        realm_emoji = "🌍" if pdata["realm"] == "Mortal Realm" else "🌟" if pdata["realm"] == "Immortal Realm" else "✨"

        embed.add_field(
            name=f"{i}. {realm_emoji} {username}",
            value=f"**{pdata['realm']}** - {pdata['stage']}\n"
                  f"⚡ Power: {pdata['total_power']}",
            inline=False
        )

    await ctx.send(embed=embed)

# ===============================
# Command: myrank
# ===============================
@bot.command()
async def myrank(ctx):
    """Lihat ranking cultivation Anda"""
    data = load_data()
    players = data["players"]
    current_player = get_player(ctx.author.id)

    # Calculate all players' scores
    def calculate_score(pdata):
        realm_weights = {"Mortal Realm": 0, "Immortal Realm": 1000, "God Realm": 2000}
        realm_score = realm_weights.get(pdata["realm"], 0)

        if pdata["realm"] in REALMS and pdata["stage"] in REALMS[pdata["realm"]]["stages"]:
            stage_index = REALMS[pdata["realm"]]["stages"].index(pdata["stage"])
            total_stages = len(REALMS[pdata["realm"]]["stages"])
            stage_score = (stage_index / total_stages) * 1000
        else:
            stage_score = 0

        return realm_score + stage_score

    # Get all scores
    all_scores = []
    for uid, pdata in players.items():
        if all(key in pdata for key in ["realm", "stage"]):
            score = calculate_score(pdata)
            all_scores.append((uid, score))

    # Sort and find rank
    all_scores.sort(key=lambda x: x[1], reverse=True)

    player_rank = None
    for rank, (uid, score) in enumerate(all_scores, 1):
        if uid == str(ctx.author.id):
            player_rank = rank
            player_score = score
            break

    if player_rank is None:
        return await ctx.send("❌ Rank not found!")

    total_players = len(all_scores)
    percentile = (total_players - player_rank + 1) / total_players * 100

    embed = discord.Embed(
        title=f"📊 Your Cultivation Rank",
        description=f"{ctx.author.name}'s position in the cultivation world",
        color=0x7289DA
    )

    realm_emoji = "🌍" if current_player["realm"] == "Mortal Realm" else "🌟" if current_player["realm"] == "Immortal Realm" else "✨"

    embed.add_field(name="Rank", value=f"#{player_rank} / {total_players}", inline=True)
    embed.add_field(name="Percentile", value=f"Top {percentile:.1f}%", inline=True)
    embed.add_field(name="Score", value=f"{player_score:.1f}", inline=True)
    embed.add_field(name="Realm", value=f"{realm_emoji} {current_player['realm']}", inline=True)
    embed.add_field(name="Stage", value=current_player["stage"], inline=True)
    embed.add_field(name="Power", value=current_player["total_power"], inline=True)

    # Progress to next rank
    if player_rank > 1:
        next_rank_score = all_scores[player_rank - 2][1]  # Score of player above
        score_needed = next_rank_score - player_score
        embed.add_field(
            name="Next Rank Progress", 
            value=f"Need {score_needed:.1f} score to reach rank #{player_rank-1}",
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
# DEV COMMANDS (Developer Only)
# ===============================
# List of developer user IDs (ganti dengan ID Discord Anda)
DEVELOPER_IDS = ["877390433519562842"]

def is_developer():
    """Check if user is a developer"""
    async def predicate(ctx):
        if str(ctx.author.id) not in DEVELOPER_IDS:
            await ctx.send("❌ This command is for developers only!")
            return False
        return True
    return commands.check(predicate)

@bot.command()
@is_developer()
async def dev_stats(ctx):
    """Detailed server statistics for developers"""
    data = load_data()
    stats = data["server_stats"]
    players = data["players"]

    # Calculate various metrics
    total_power = sum(p["total_power"] for p in players.values())
    avg_power = total_power / len(players) if players else 0
    max_power = max((p["total_power"] for p in players.values()), default=0)

    # Count players by realm
    realm_counts = {}
    for p in players.values():
        realm = p["realm"]
        realm_counts[realm] = realm_counts.get(realm, 0) + 1

    # Count equipment usage
    equipment_counts = {}
    for p in players.values():
        for item_id in p["equipment"]:
            equipment_counts[item_id] = equipment_counts.get(item_id, 0) + 1

    embed = discord.Embed(
        title="🔧 Developer Statistics",
        color=0x9932cc
    )

    embed.add_field(name="Total Players", value=data["total_players"], inline=True)
    embed.add_field(name="Active Players", value=len(players), inline=True)
    embed.add_field(name="Average Power", value=f"{avg_power:.1f}", inline=True)
    embed.add_field(name="Max Power", value=max_power, inline=True)
    embed.add_field(name="Total PvP Battles", value=stats["total_pvp_battles"], inline=True)
    embed.add_field(name="Total Breakthroughs", value=stats["total_breakthroughs"], inline=True)

    # Realm distribution
    realm_text = "\n".join([f"{realm}: {count}" for realm, count in realm_counts.items()])
    embed.add_field(name="Realm Distribution", value=realm_text, inline=False)

    # File size info
    file_size = os.path.getsize(DATA_FILE) if os.path.exists(DATA_FILE) else 0
    embed.add_field(name="Data File Size", value=f"{file_size/1024:.1f} KB", inline=True)

    # Backup count
    backup_count = len([f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_")]) if os.path.exists(BACKUP_DIR) else 0
    embed.add_field(name="Backup Count", value=backup_count, inline=True)

    await ctx.send(embed=embed)

@bot.command()
@is_developer()
async def dev_player(ctx, user: discord.Member = None):
    """View detailed player data (developer only)"""
    target_user = user or ctx.author
    p = get_player(target_user.id)

    embed = discord.Embed(
        title=f"🔍 Player Data: {target_user.name}",
        color=0x9932cc
    )

    embed.add_field(name="User ID", value=target_user.id, inline=True)
    embed.add_field(name="Realm", value=p["realm"], inline=True)
    embed.add_field(name="Stage", value=p["stage"], inline=True)
    embed.add_field(name="EXP", value=f"{p['exp']}/{get_exp_cap(p)}", inline=True)
    embed.add_field(name="Qi", value=p["qi"], inline=True)
    embed.add_field(name="Spirit Stones", value=p["spirit_stones"], inline=True)
    embed.add_field(name="Base Power", value=p["base_power"], inline=True)
    embed.add_field(name="Total Power", value=p["total_power"], inline=True)
    embed.add_field(name="PvP Record", value=f"{p['pvp_wins']}W/{p['pvp_losses']}L", inline=True)
    embed.add_field(name="Dungeons Completed", value=p["dungeons_completed"], inline=True)
    embed.add_field(name="Techniques Learned", value=p["techniques_learned"], inline=True)
    embed.add_field(name="Created At", value=p["created_at"][:10], inline=True)

    # Equipment list
    if p["equipment"]:
        equip_text = "\n".join([f"{item_id}: +{power}" for item_id, power in p["equipment"].items()])
        embed.add_field(name="Equipment", value=equip_text, inline=False)

    await ctx.send(embed=embed)

@bot.command()
@is_developer()
async def dev_give(ctx, user: discord.Member, resource: str, amount: int):
    """Give resources to a player (developer only)"""
    valid_resources = ["exp", "qi", "spirit_stones", "power"]

    if resource not in valid_resources:
        return await ctx.send(f"❌ Invalid resource! Available: {', '.join(valid_resources)}")

    p = get_player(user.id)

    if resource == "exp":
        p["exp"] = min(p["exp"] + amount, get_exp_cap(p))
    elif resource == "qi":
        p["qi"] += amount
    elif resource == "spirit_stones":
        p["spirit_stones"] += amount
    elif resource == "power":
        p["base_power"] += amount
        p["total_power"] = int(p["base_power"] * (1 + sum(t['power_bonus'] for t in p["techniques"])))

    update_player(user.id, p)

    await ctx.send(f"✅ Gave {amount} {resource} to {user.mention}")

@bot.command()
@is_developer()
async def dev_set_realm(ctx, user: discord.Member, realm: str, stage: str = None):
    """Set player's realm and stage (developer only)"""
    if realm not in REALMS:
        return await ctx.send(f"❌ Invalid realm! Available: {', '.join(REALMS.keys())}")

    p = get_player(user.id)

    if stage and stage not in REALMS[realm]["stages"]:
        return await ctx.send(f"❌ Invalid stage for {realm}!")

    p["realm"] = realm
    if stage:
        p["stage"] = stage
    else:
        p["stage"] = REALMS[realm]["stages"][0]

    p["exp"] = 0
    update_player(user.id, p)

    await ctx.send(f"✅ Set {user.mention} to {realm} - {p['stage']}")

@bot.command()
@is_developer()
async def dev_reset_player(ctx, user: discord.Member):
    """Reset player data (developer only)"""
    data = load_data()
    uid_str = str(user.id)

    if uid_str in data["players"]:
        del data["players"][uid_str]
        data["total_players"] = max(0, data["total_players"] - 1)
        save_data(data)
        await ctx.send(f"✅ Reset player data for {user.mention}")
    else:
        await ctx.send(f"❌ Player {user.mention} not found!")

@bot.command()
@is_developer()
async def dev_reload_data(ctx):
    """Reload data from file (developer only)"""
    global data
    data = load_data()
    await ctx.send("✅ Data reloaded from file!")

@bot.command()
@is_developer()
async def dev_force_backup(ctx):
    """Force immediate backup (developer only)"""
    if backup_data():
        await ctx.send("✅ Backup created successfully!")
    else:
        await ctx.send("❌ Failed to create backup!")

@bot.command()
@is_developer()
async def dev_list_backups(ctx):
    """List all backups (developer only)"""
    if not os.path.exists(BACKUP_DIR):
        return await ctx.send("❌ No backup directory found!")

    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_") and f.endswith(".json")]
    backups.sort(reverse=True)

    if not backups:
        return await ctx.send("❌ No backups found!")

    embed = discord.Embed(
        title="📦 Backup Files",
        color=0x9932cc
    )

    for backup in backups[:10]:  # Show last 10 backups
        backup_path = os.path.join(BACKUP_DIR, backup)
        size = os.path.getsize(backup_path)
        timestamp = backup.replace("backup_", "").replace(".json", "")
        date_str = datetime.datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M")

        embed.add_field(
            name=backup,
            value=f"Size: {size/1024:.1f} KB\nCreated: {date_str}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
@is_developer()
async def dev_restore_backup(ctx, backup_name: str):
    """Restore from specific backup (developer only)"""
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    if not os.path.exists(backup_path):
        return await ctx.send("❌ Backup file not found!")

    try:
        # Create backup of current data first
        backup_data()

        # Restore from specified backup
        shutil.copy2(backup_path, DATA_FILE)

        # Reload data
        global data
        data = load_data()

        await ctx.send(f"✅ Successfully restored from {backup_name}")
    except Exception as e:
        await ctx.send(f"❌ Error restoring backup: {e}")

@bot.command()
@is_developer()
async def dev_broadcast(ctx, *, message: str):
    """Broadcast message to all players (developer only)"""
    # This would typically send a message to all users who have interacted with the bot
    # For now, just confirm the command
    await ctx.send(f"📢 Broadcast message prepared:\n{message}\n\n*(This would be sent to all players in a real implementation)*")

@bot.command()
@is_developer()
async def dev_help(ctx):
    """Show developer commands help (developer only)"""
    embed = discord.Embed(
        title="🔧 Developer Commands Help",
        color=0x9932cc
    )

    commands_list = [
        ("!dev_stats", "Detailed server statistics"),
        ("!dev_player [@user]", "View detailed player data"),
        ("!dev_give @user resource amount", "Give resources to player (exp/qi/spirit_stones/power)"),
        ("!dev_set_realm @user realm [stage]", "Set player's realm and stage"),
        ("!dev_reset_player @user", "Reset player data"),
        ("!dev_reload_data", "Reload data from file"),
        ("!dev_force_backup", "Force immediate backup"),
        ("!dev_list_backups", "List all backup files"),
        ("!dev_restore_backup filename", "Restore from specific backup"),
        ("!dev_broadcast message", "Broadcast message to all players"),
        ("!dev_help", "This help message")
    ]

    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)

    await ctx.send(embed=embed)

# ===============================
# Command: help (COMPREHENSIVE) - UPDATED
# ===============================
# Remove default help command first
bot.remove_command('help')

@bot.command(name='help')
async def help_command(ctx, category: str = None):
    """Comprehensive help system with categories"""

    if category is None:
        # Main help menu
        embed = discord.Embed(
            title="🏮 Idle Immortal Bot - Command Guide",
            description="A comprehensive cultivation RPG bot with idle mechanics, real-time battles, and progression systems!",
            color=0x7289da
        )

        embed.add_field(
            name="📚 Command Categories",
            value="Use `!help <category>` for detailed commands:\n\n"
                  "🧘 **cultivation** - Core cultivation & progression\n"
                  "⚔️ **combat** - PvP battles and dungeons\n"
                  "🛒 **economy** - Shop, equipment, and trading\n"
                  "🏰 **guild** - Guild system and teamwork\n"
                  "📋 **daily** - Daily quests and events\n"
                  "📊 **info** - Stats, progress, and information\n"
                  "🏆 **ranking** - Leaderboards and competition\n"
                  "🔧 **system** - Bot utilities and admin\n",
            inline=False
        )

        embed.add_field(
            name="🚀 Quick Start",
            value="`!status` - Check your cultivation status\n"
                  "`!cultivate` - Manual cultivation session\n"
                  "`!start_cultivate` - Start idle cultivation\n"
                  "`!realms` - View cultivation realms\n"
                  "`!leaderboard` - See cultivation rankings",
            inline=False
        )

        embed.add_field(
            name="💡 Pro Tips",
            value="• Use idle cultivation for passive EXP gain (410+ EXP/hour!)\n"
                  "• Complete dungeons for bonus rewards\n"
                  "• Learn techniques to boost your power\n"
                  "• Challenge other players in PvP battles\n"
                  "• Check your rank with `!myrank`",
            inline=False
        )

        embed.set_footer(text="🌟 Start your journey to immortality today! Use !help <category> for specific commands.")

    elif category.lower() == "cultivation":
        embed = discord.Embed(
            title="🧘 Cultivation Commands",
            description="Master the path of cultivation and ascend through the realms!",
            color=0x00ff00
        )

        embed.add_field(
            name="📈 Progress & Info",
            value="`!status` - Your comprehensive stats\n"
                  "`!realms` - View all cultivation realms\n"
                  "`!myrealm` - Your current realm details\n"
                  "`!progress` - Overall cultivation progress\n"
                  "`!breakthrough` - Advance to next stage/realm",
            inline=False
        )

        embed.add_field(
            name="🧘 Cultivation Methods",
            value="`!cultivate` - Manual cultivation (1min cooldown)\n"
                  "`!start_cultivate` - **Start idle cultivation**\n"
                  "`!stop_cultivate` - Stop idle cultivation\n"
                  "`!cultivate_status` - Check idle progress",
            inline=False
        )

        embed.add_field(
            name="📜 Techniques",
            value="`!find_technique` - Discover techniques (1hr cooldown)\n"
                  "`!learn_technique <id>` - Learn discovered techniques\n"
                  "`!my_techniques` - View learned techniques",
            inline=False
        )

        embed.set_footer(text="💫 Idle cultivation gains: 410+ EXP/hour, 405+ Qi/hour, 400+ Spirit Stones/hour!")

    elif category.lower() == "combat":
        embed = discord.Embed(
            title="⚔️ Combat Commands",
            description="Engage in battles and prove your cultivation prowess!",
            color=0xff0000
        )

        embed.add_field(
            name="🥊 Player vs Player",
            value="`!pvp @user` - Challenge player to battle (5min cooldown)\n"
                  "`!pvp_rank` - View PvP leaderboard",
            inline=False
        )

        embed.add_field(
            name="🏰 Dungeons",
            value="`!dungeons` - List available dungeons\n"
                  "`!enter <dungeon_name>` - Enter dungeon (5min cooldown)",
            inline=False
        )

        embed.set_footer(text="⚡ Higher power increases success chance in combat!")

    elif category.lower() == "economy":
        embed = discord.Embed(
            title="🛒 Economy Commands",
            description="Manage your resources and equipment!",
            color=0xffd700
        )

        embed.add_field(
            name="🏪 Shopping",
            value="`!shop` - Browse available equipment\n"
                  "`!buy <item_name>` - Purchase equipment with Qi\n"
                  "Example: `!buy iron_sword`",
            inline=False
        )

        embed.add_field(
            name="🎒 Inventory",
            value="`!inventory` - View your equipment\n"
                  "`!sell <item_name>` - Sell equipment for Qi\n"
                  "`!enchant <item_name>` - Enhance equipment",
            inline=False
        )

        embed.set_footer(text="💰 Earn Qi through cultivation and spend it wisely!")

    elif category.lower() == "info":
        embed = discord.Embed(
            title="📊 Information Commands",
            description="Get detailed information about your progress and the server!",
            color=0x7289da
        )

        embed.add_field(
            name="📈 Statistics",
            value="`!status` - Your complete cultivation status\n"
                  "`!stats` - Server-wide statistics\n"
                  "`!ping` - Check bot response time",
            inline=False
        )

        embed.set_footer(text="📋 Stay informed about your cultivation journey!")

    elif category.lower() == "ranking":
        embed = discord.Embed(
            title="🏆 Ranking Commands",
            description="Compete with other cultivators and see your progress!",
            color=0xFFD700
        )

        embed.add_field(
            name="📊 Leaderboards",
            value="`!leaderboard` - Full cultivation leaderboard\n"
                  "`!leaderboard 2` - Page 2 of leaderboard\n"
                  "`!top` - Top 5 cultivators\n"
                  "`!top 10` - Top 10 cultivators\n"
                  "`!myrank` - Your current rank and stats\n"
                  "`!pvp_rank` - PvP leaderboard",
            inline=False
        )

        embed.set_footer(text="👑 Climb the ranks to become the ultimate cultivator!")

    elif category.lower() == "system":
        embed = discord.Embed(
            title="🔧 System Commands",
            description="Bot utilities and administrative functions!",
            color=0x9932cc
        )

        embed.add_field(
            name="🔧 Utilities",
            value="`!ping` - Check bot latency\n"
                  "`!backup` - Create manual backup (Admin only)",
            inline=False
        )

        embed.set_footer(text="⚙️ System commands help maintain the bot!")

    else:
        embed = discord.Embed(
            title="❌ Unknown Category",
            description=f"Category '{category}' not found!",
            color=0xff0000
        )

        embed.add_field(
            name="Available Categories:",
            value="• `cultivation` - Core cultivation commands\n"
                  "• `combat` - PvP and dungeons\n"
                  "• `economy` - Shop and inventory\n"
                  "• `info` - Statistics and information\n"
                  "• `ranking` - Leaderboards and competition\n"
                  "• `system` - Bot utilities",
            inline=False
        )

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