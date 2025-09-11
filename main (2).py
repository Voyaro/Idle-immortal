import os
import discord
from discord.ext import commands
import json
import random
import asyncio
import datetime
import shutil
import time
import math
from keep_alive import keep_alive
from explore import start_exploration
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # wajib untuk bisa baca chat
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def explore(ctx):
    player = get_player(ctx.author.id)
    if not player:
        return await ctx.send("❌ Kamu belum register. Gunakan `!register` dulu.")

    await start_exploration(ctx, player, max_steps=10)
try:
    # Import functions saja, bukan *
    from boss import (
        list_bosses, 
        challenge_boss, 
        show_boss_info, 
        boss_status, 
        boss_cooldown,
        BOSSES
    )
    BOSS_SYSTEM_LOADED = True
    print("✅ Boss system loaded successfully!")
except ImportError as e:
    print(f"❌ Failed to load boss system: {e}")
    BOSS_SYSTEM_LOADED = False

# ===============================
# TOKEN (ambil dari Secrets Replit)
# ===============================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ Token bot tidak ditemukan! Pastikan sudah di-set di Environment Variables")
    BOT_TOKEN = "placeholder_token_untuk_development"

# ===============================
# Import dari utils instead of circular import
# ===============================
from utils import load_data, save_data, calculate_set_bonus

# ===============================
# Data penyimpanan dengan backup system
# ===============================
DATA_FILE = "data.json"
BACKUP_DIR = "backups"

# ===============================
# Global Variables untuk Active Systems
# ===============================
ACTIVE_CULTIVATIONS = {}
ACTIVE_BATTLES = {}
ACTIVE_DUNGEONS = {}
ACTIVE_QUESTS = {}
PENDING_REGISTRATIONS = {}

# ===============================
# Race System - BARU
# ===============================
RACES = {
    "human": {
        "name": "Human",
        "emoji": "👨",
        "bonuses": {"exp": 0.10, "qi": 0.15, "technique": 0.20},
        "description": "Versatile cultivators with balanced growth and technique mastery"
    },
    "demon": {
        "name": "Demon",
        "emoji": "😈", 
        "bonuses": {"power": 0.25, "attack": 0.20, "defense": -0.10},
        "description": "Powerful but reckless cultivators with immense combat prowess"
    },
    "half_demon": {
        "name": "Half-Demon",
        "emoji": "😠",
        "bonuses": {"power": 0.15, "exp": 0.10, "qi": 0.05},
        "description": "Balanced hybrid with both human versatility and demonic power"
    },
    "beast": {
        "name": "Beast Race",
        "emoji": "🐺",
        "bonuses": {"defense": 0.20, "health": 0.25, "speed": 0.15},
        "description": "Natural survivors with enhanced physical attributes and instincts"
    },
    "celestial": {
        "name": "Celestial",
        "emoji": "👼",
        "bonuses": {"qi": 0.30, "healing": 0.25, "exp": 0.10},
        "description": "Divine beings with exceptional Qi control and healing abilities",
        "hidden": True
    }
}

GENDERS = {
    "male": {"name": "Male", "emoji": "♂️"},
    "female": {"name": "Female", "emoji": "♀️"},
    "other": {"name": "Other", "emoji": "⚧️"}
}

# ===============================
# Realms, Stages, dan EXP Cap - SISTEM YANG LEBIH CHALLENGING
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
        "exp_multiplier": 1.0,
        "power_multiplier": 1.0,
        "spirit_stone_gain": 1,
        "color": 0x964B00,
        "discovery_chance": 0.3
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
        "exp_multiplier": 10.0,
        "power_multiplier": 5.0,
        "spirit_stone_gain": 5,
        "color": 0x00FF00,
        "discovery_chance": 0.5
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
        "exp_multiplier": 100.0,
        "power_multiplier": 25.0,
        "spirit_stone_gain": 25,
        "color": 0xFFD700,
        "discovery_chance": 0.7
    }
}

REALM_ORDER = list(REALMS.keys())

# ===============================
# Guild/Sect System - DIPERBAIKI
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
    "sword": {"name": "Sword Sect", "emoji": "⚔️", "specialty": "Sword Techniques", "bonus": {"attack": 0.1}},
    "elemental": {"name": "Elemental Sect", "emoji": "🔥", "specialty": "Element Control", "bonus": {"all": 0.05}},
    "body": {"name": "Body Sect", "emoji": "💪", "specialty": "Physical Cultivation", "bonus": {"defense": 0.1}},
    "soul": {"name": "Soul Sect", "emoji": "👻", "specialty": "Soul Attacks", "bonus": {"attack": 0.05, "support": 0.05}},
    "alchemy": {"name": "Alchemy Sect", "emoji": "🧪", "specialty": "Pill Refining", "bonus": {"healing": 0.1}},
    "array": {"name": "Array Sect", "emoji": "🔷", "specialty": "Formation Arrays", "bonus": {"defense": 0.05, "support": 0.05}},
    "beast": {"name": "Beast Taming Sect", "emoji": "🐉", "specialty": "Spirit Beasts", "bonus": {"movement": 0.1}},
    "dark": {"name": "Dark Moon Sect", "emoji": "🌙", "specialty": "Shadow Techniques", "bonus": {"attack": 0.07, "movement": 0.03}}
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
# Equipment System - DIPERLUAS
# ===============================
EQUIPMENT_SHOP = {
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

    # IMMORTAL REALM EQUIPMENT  
    "celestial_blade": {"name": "Celestial Blade", "power": 75, "cost": 2000, "type": "weapon", "emoji": "🌟", "realm": "Immortal Realm", "tier": "Celestial", "set": "celestial"},
    "celestial_robes": {"name": "Celestial Robes", "power": 60, "cost": 1800, "type": "armor", "emoji": "👘", "realm": "Immortal Realm", "tier": "Celestial", "set": "celestial"},
    "celestial_crown": {"name": "Celestial Crown", "power": 50, "cost": 1500, "type": "accessory", "emoji": "👑", "realm": "Immortal Realm", "tier": "Celestial", "set": "celestial"},

    "void_slasher": {"name": "Void Slasher", "power": 120, "cost": 4000, "type": "weapon", "emoji": "🌌", "realm": "Immortal Realm", "tier": "Void", "set": "void"},
    "void_mantle": {"name": "Void Mantle", "power": 100, "cost": 3500, "type": "armor", "emoji": "🌃", "realm": "Immortal Realm", "tier": "Void", "set": "void"},
    "void_orb": {"name": "Void Orb", "power": 80, "cost": 3000, "type": "accessory", "emoji": "🔮", "realm": "Immortal Realm", "tier": "Void", "set": "void"},

    "profound_saber": {"name": "Profound Saber", "power": 180, "cost": 7000, "type": "weapon", "emoji": "🗡️", "realm": "Immortal Realm", "tier": "Profound", "set": "profound"},
    "profound_vestments": {"name": "Profound Vestments", "power": 150, "cost": 6000, "type": "armor", "emoji": "🥻", "realm": "Immortal Realm", "tier": "Profound", "set": "profound"},
    "profound_talisman": {"name": "Profound Talisman", "power": 120, "cost": 5000, "type": "accessory", "emoji": "📿", "realm": "Immortal Realm", "tier": "Profound", "set": "profound"},

    "immortal_dao_sword": {"name": "Immortal Dao Sword", "power": 280, "cost": 12000, "type": "weapon", "emoji": "⚡", "realm": "Immortal Realm", "tier": "Immortal", "set": "immortal"},
    "immortal_phoenix_armor": {"name": "Immortal Phoenix Armor", "power": 240, "cost": 10000, "type": "armor", "emoji": "🔥", "realm": "Immortal Realm", "tier": "Immortal", "set": "immortal"},
    "immortal_lotus_seal": {"name": "Immortal Lotus Seal", "power": 200, "cost": 8000, "type": "accessory", "emoji": "🪷", "realm": "Immortal Realm", "tier": "Immortal", "set": "immortal"},

    # GOD REALM EQUIPMENT
    "divine_judgment": {"name": "Divine Judgment", "power": 400, "cost": 20000, "type": "weapon", "emoji": "⚖️", "realm": "God Realm", "tier": "Divine", "set": "divine"},
    "divine_sanctuary": {"name": "Divine Sanctuary", "power": 350, "cost": 18000, "type": "armor", "emoji": "🏛️", "realm": "God Realm", "tier": "Divine", "set": "divine"},
    "divine_halo": {"name": "Divine Halo", "power": 300, "cost": 15000, "type": "accessory", "emoji": "😇", "realm": "God Realm", "tier": "Divine", "set": "divine"},

    "sacred_annihilator": {"name": "Sacred Annihilator", "power": 600, "cost": 35000, "type": "weapon", "emoji": "💥", "realm": "God Realm", "tier": "Sacred", "set": "sacred"},
    "sacred_fortress": {"name": "Sacred Fortress", "power": 500, "cost": 30000, "type": "armor", "emoji": "🏰", "realm": "God Realm", "tier": "Sacred", "set": "sacred"},
    "sacred_eye": {"name": "Sacred Eye", "power": 450, "cost": 25000, "type": "accessory", "emoji": "👁️", "realm": "God Realm", "tier": "Sacred", "set": "sacred"},

    "primordial_chaos": {"name": "Primordial Chaos", "power": 850, "cost": 60000, "type": "weapon", "emoji": "🌀", "realm": "God Realm", "tier": "Primordial", "set": "primordial"},
    "primordial_genesis": {"name": "Primordial Genesis", "power": 750, "cost": 50000, "type": "armor", "emoji": "🌌", "realm": "God Realm", "tier": "Primordial", "set": "primordial"},
    "primordial_core": {"name": "Primordial Core", "power": 650, "cost": 45000, "type": "accessory", "emoji": "⭐", "realm": "God Realm", "tier": "Primordial", "set": "primordial"},

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
# Dungeon System - DIPERLUAS
# ===============================
DUNGEONS = {
    "forest": {
        "name": "Spirit Forest",
        "min_level": 1,
        "max_level": 10,
        "min_reward": 20,
        "max_reward": 50,
        "spirit_stone_reward": (1, 3),
        "emoji": "🌳",
        "difficulty": "Easy",
        "description": "A peaceful forest filled with low-level spirit beasts"
    },
    "cave": {
        "name": "Ancient Cave", 
        "min_level": 5,
        "max_level": 20,
        "min_reward": 40,
        "max_reward": 100,
        "spirit_stone_reward": (2, 5),
        "emoji": "🕳️",
        "difficulty": "Medium",
        "description": "Dark caves with ancient treasures and dangers"
    },
    "mountain": {
        "name": "Celestial Mountain",
        "min_level": 15,
        "max_level": 30,
        "min_reward": 80,
        "max_reward": 200,
        "spirit_stone_reward": (3, 8),
        "emoji": "⛰️",
        "difficulty": "Hard",
        "description": "A sacred mountain with powerful guardians"
    },
    "abyss": {
        "name": "Demon Abyss",
        "min_level": 25,
        "max_level": 50,
        "min_reward": 150,
        "max_reward": 400,
        "spirit_stone_reward": (5, 15),
        "emoji": "🔥",
        "difficulty": "Very Hard",
        "description": "A dangerous abyss filled with demonic creatures"
    },
    "palace": {
        "name": "Heavenly Palace",
        "min_level": 40,
        "max_level": 80,
        "min_reward": 300,
        "max_reward": 800,
        "spirit_stone_reward": (10, 25),
        "emoji": "🏯",
        "difficulty": "Extreme",
        "description": "The celestial palace of immortals"
    }
}

# ===============================
# Spirit Beast System - BARU
# ===============================
SPIRIT_BEASTS = {
    "common": [
        {"name": "Spirit Rabbit", "emoji": "🐇", "power": 5, "cost": 100, "bonus": {"exp": 0.05}},
        {"name": "Moon Fox", "emoji": "🦊", "power": 10, "cost": 250, "bonus": {"qi": 0.07}},
        {"name": "Wind Hawk", "emoji": "🦅", "power": 15, "cost": 500, "bonus": {"movement": 0.10}}
    ],
    "rare": [
        {"name": "Thunder Tiger", "emoji": "🐅", "power": 25, "cost": 1000, "bonus": {"attack": 0.08}},
        {"name": "Earth Bear", "emoji": "🐻", "power": 30, "cost": 1500, "bonus": {"defense": 0.10}},
        {"name": "Water Serpent", "emoji": "🐍", "power": 35, "cost": 2000, "bonus": {"healing": 0.09}}
    ],
    "epic": [
        {"name": "Phoenix", "emoji": "🔥", "power": 50, "cost": 5000, "bonus": {"all": 0.05}},
        {"name": "Azure Dragon", "emoji": "🐉", "power": 60, "cost": 7500, "bonus": {"attack": 0.12}},
        {"name": "White Tiger", "emoji": "🐯", "power": 70, "cost": 10000, "bonus": {"defense": 0.15}}
    ],
    "legendary": [
        {"name": "Golden Qilin", "emoji": "🦄", "power": 100, "cost": 20000, "bonus": {"all": 0.10}},
        {"name": "Vermilion Bird", "emoji": "🐦", "power": 120, "cost": 30000, "bonus": {"exp": 0.15, "qi": 0.15}},
        {"name": "Black Tortoise", "emoji": "🐢", "power": 150, "cost": 50000, "bonus": {"defense": 0.20, "healing": 0.10}}
    ]
}

# ===============================
# Alchemy System - BARU
# ===============================
PILL_RECIPES = {
    "qi_pill": {
        "name": "Qi Gathering Pill",
        "emoji": "💊",
        "effect": {"qi": 50},
        "ingredients": {"spirit_herb": 3, "spirit_water": 1},
        "cost": 100,
        "description": "Basic pill for Qi cultivation"
    },
    "exp_pill": {
        "name": "EXP Boost Pill",
        "emoji": "✨",
        "effect": {"exp": 100},
        "ingredients": {"spirit_herb": 5, "spirit_crystal": 2},
        "cost": 250,
        "description": "Increases cultivation EXP gain"
    },
    "power_pill": {
        "name": "Power Enhancement Pill",
        "emoji": "💪",
        "effect": {"power": 20},
        "ingredients": {"spirit_crystal": 3, "dragon_scale": 1},
        "cost": 500,
        "description": "Temporarily boosts combat power"
    },
    "breakthrough_pill": {
        "name": "Breakthrough Pill",
        "emoji": "🌟",
        "effect": {"breakthrough_chance": 0.2},
        "ingredients": {"phoenix_feather": 1, "dragon_heart": 1, "spirit_crystal": 10},
        "cost": 2000,
        "description": "Increases breakthrough success chance"
    }
}

ALCHEMY_INGREDIENTS = {
    "spirit_herb": {"name": "Spirit Herb", "emoji": "🌿", "rarity": "common", "base_cost": 10},
    "spirit_water": {"name": "Spirit Water", "emoji": "💧", "rarity": "common", "base_cost": 15},
    "spirit_crystal": {"name": "Spirit Crystal", "emoji": "🔮", "rarity": "uncommon", "base_cost": 30},
    "dragon_scale": {"name": "Dragon Scale", "emoji": "🐉", "rarity": "rare", "base_cost": 100},
    "phoenix_feather": {"name": "Phoenix Feather", "emoji": "🪶", "rarity": "epic", "base_cost": 500},
    "dragon_heart": {"name": "Dragon Heart", "emoji": "❤️", "rarity": "legendary", "base_cost": 2000}
}

# ===============================
# Achievement System - DIPERBAIKI
# ===============================
ACHIEVEMENTS = {
    "first_breakthrough": {
        "name": "First Breakthrough",
        "description": "Achieve your first cultivation breakthrough",
        "reward": {"spirit_stones": 100, "exp": 200},
        "emoji": "🌟",
        "condition": lambda p: p.get("breakthroughs", 0) >= 1
    },
    "dungeon_master": {
        "name": "Dungeon Master",
        "description": "Complete 10 dungeons",
        "reward": {"spirit_stones": 500, "qi": 300},
        "emoji": "🏆",
        "condition": lambda p: p.get("dungeons_completed", 0) >= 10
    },
    "pvp_champion": {
        "name": "PvP Champion",
        "description": "Win 10 PvP battles",
        "reward": {"spirit_stones": 300, "power": 50},
        "emoji": "⚔️",
        "condition": lambda p: p.get("pvp_wins", 0) >= 10
    },
    "technique_master": {
        "name": "Technique Master",
        "description": "Learn 5 techniques",
        "reward": {"spirit_stones": 400, "exp": 500},
        "emoji": "📜",
        "condition": lambda p: len(p.get("techniques", [])) >= 5
    },
    "realm_ascender": {
        "name": "Realm Ascender",
        "description": "Reach Immortal Realm",
        "reward": {"spirit_stones": 1000, "qi": 800},
        "emoji": "🌌",
        "condition": lambda p: p.get("realm") == "Immortal Realm"
    },
    "beast_tamer": {
        "name": "Beast Tamer",
        "description": "Tame 3 spirit beasts",
        "reward": {"spirit_stones": 400, "power": 30},
        "emoji": "🐉",
        "condition": lambda p: len(p.get("spirit_beasts", [])) >= 3
    },
    "alchemy_master": {
        "name": "Alchemy Master",
        "description": "Craft 10 pills",
        "reward": {"spirit_stones": 600, "qi": 400},
        "emoji": "🧪",
        "condition": lambda p: p.get("pills_crafted", 0) >= 10
    }
}

# ===============================
# Daily Quest System - DIPERBAIKI
# ===============================
DAILY_QUESTS = [
    {"id": "cultivate_5", "name": "Cultivate 5 times", "reward": {"exp": 100, "spirit_stones": 20}, "progress_needed": 5},
    {"id": "pvp_battle", "name": "Win 1 PvP battle", "reward": {"exp": 150, "qi": 50}, "progress_needed": 1},
    {"id": "complete_dungeon", "name": "Complete 2 dungeons", "reward": {"spirit_stones": 30, "qi": 100}, "progress_needed": 2},
    {"id": "learn_technique", "name": "Learn a new technique", "reward": {"exp": 200, "spirit_stones": 50}, "progress_needed": 1},
    {"id": "breakthrough", "name": "Achieve breakthrough", "reward": {"exp": 300, "spirit_stones": 100}, "progress_needed": 1},
    {"id": "find_treasure", "name": "Find 3 treasures", "reward": {"spirit_stones": 40, "qi": 80}, "progress_needed": 3},
    {"id": "defeat_monster", "name": "Defeat 5 monsters", "reward": {"exp": 120, "power": 25}, "progress_needed": 5}
]

# ===============================
# Helper functions - DIPERBAIKI
# ===============================
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
            "total_spirit_beasts": 0,
            "total_pills_crafted": 0,
            "last_update": datetime.datetime.now().isoformat()
        },
        "guilds": {},
        "market_items": [],
        "server_events": {},
        "daily_quests_reset": datetime.datetime.now().isoformat()
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

        # Update dengan field baru jika missing
        default_fields = {
            "guilds": {},
            "market_items": [],
            "server_events": {},
            "server_stats": {
                "total_pvp_battles": 0,
                "total_breakthroughs": 0,
                "total_dungeons": 0,
                "total_techniques_learned": 0,
                "total_spirit_beasts": 0,
                "total_pills_crafted": 0,
                "last_update": datetime.datetime.now().isoformat()
            },
            "daily_quests_reset": datetime.datetime.now().isoformat()
        }

        for field, default_value in default_fields.items():
            if field not in data:
                data[field] = default_value

        # Update player data dengan field baru
        for player_id, player_data in data["players"].items():
            new_fields = {
                "breakthroughs": player_data.get("breakthroughs", 0),
                "daily_quests": player_data.get("daily_quests", {}),
                "last_daily_claim": player_data.get("last_daily_claim", "0"),
                "discovered_techniques": player_data.get("discovered_techniques", []),
                "guild_contributions": player_data.get("guild_contributions", 0),
                "login_streak": player_data.get("login_streak", 0),
                "last_login": player_data.get("last_login", "0")
            }

            for field, default_value in new_fields.items():
                if field not in player_data:
                    player_data[field] = default_value

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

def get_player_level(p):
    """Hitung level player berdasarkan realm dan stage dengan race bonus"""
    realm_idx = REALM_ORDER.index(p["realm"])
    stage_idx = REALMS[p["realm"]]["stages"].index(p["stage"])

    base_level = (realm_idx * 100) + (stage_idx * 3) + 1

    # Apply race bonus jika ada
    race_data = RACES.get(p.get("race", "human"), RACES["human"])
    if "exp" in race_data["bonuses"]:
        base_level = int(base_level * (1 + race_data["bonuses"]["exp"]))

    return base_level

def get_exp_cap(p):
    """Dapatkan EXP cap untuk stage player saat ini dengan sistem yang lebih realistis"""
    realm_data = REALMS[p["realm"]]
    stage_idx = realm_data["stages"].index(p["stage"])

    # Base EXP untuk stage pertama di Mortal Realm
    base_exp = 1000

    # Exponential growth per stage: 1.5x per stage (bukan linear)
    stage_exp = base_exp * (1.5 ** stage_idx)

    # Realm multiplier 
    realm_multiplier = realm_data["exp_multiplier"]

    # Additional difficulty scaling
    difficulty_multiplier = 1 + (stage_idx * 0.1)

    exp_cap = int(stage_exp * realm_multiplier * difficulty_multiplier)

    return max(1000, exp_cap)

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
    """Dapatkan data player, return None jika belum terdaftar"""
    data = load_data()
    uid_str = str(uid)

    if uid_str not in data["players"]:
        return None

    player_data = data["players"][uid_str]

    # Update player lama dengan field baru jika perlu
    new_fields = {
        "spirit_stones": player_data.get("spirit_stones", 50),
        "techniques": player_data.get("techniques", []),
        "current_technique": player_data.get("current_technique", None),
        "sect": player_data.get("sect", None),
        "guild": player_data.get("guild", None),
        "guild_role": player_data.get("guild_role", None),
        "base_power": player_data.get("power", 10),
        "total_power": player_data.get("power", 10),
        "last_technique_find": player_data.get("last_technique_find", "0"),
        "last_daily_quest": player_data.get("last_daily_quest", "0"),
        "techniques_learned": player_data.get("techniques_learned", 0),
        "daily_streak": player_data.get("daily_streak", 0),
        "spirit_beasts": player_data.get("spirit_beasts", []),
        "current_beast": player_data.get("current_beast", None),
        "inventory": player_data.get("inventory", {
            "spirit_herb": 0, "spirit_water": 0, "spirit_crystal": 0,
            "dragon_scale": 0, "phoenix_feather": 0, "dragon_heart": 0
        }),
        "pills_crafted": player_data.get("pills_crafted", 0),
        "achievements": player_data.get("achievements", []),
        "race": player_data.get("race", "human"),
        "gender": player_data.get("gender", "other"),
        "display_name": player_data.get("display_name", ""),
        "created_at": player_data.get("created_at", datetime.datetime.now().isoformat()),
        "last_updated": datetime.datetime.now().isoformat(),
        "breakthroughs": player_data.get("breakthroughs", 0),
        "daily_quests": player_data.get("daily_quests", {}),
        "last_daily_claim": player_data.get("last_daily_claim", "0"),
        "discovered_techniques": player_data.get("discovered_techniques", []),
        "guild_contributions": player_data.get("guild_contributions", 0),
        "login_streak": player_data.get("login_streak", 0),
        "last_login": player_data.get("last_login", "0")
    }

    for field, default_value in new_fields.items():
        if field not in player_data:
            player_data[field] = default_value

    # Jika ada power lama, convert ke base_power
    if "power" in player_data and "base_power" not in player_data:
        player_data["base_power"] = player_data["power"]
        player_data["total_power"] = player_data["power"]

    # Check and update achievements
    check_achievements(uid_str, player_data)

    save_data(data)
    return player_data

def create_new_player(uid, race, gender, name):
    """Buat player baru dengan race dan gender"""
    data = load_data()
    uid_str = str(uid)

    race_data = RACES[race]
    gender_data = GENDERS[gender]

    # Base stats dengan bonus race
    base_power = 10
    base_qi = 50

    # Terapkan bonus race
    if "power" in race_data["bonuses"]:
        base_power = int(base_power * (1 + race_data["bonuses"]["power"]))
    if "qi" in race_data["bonuses"]:
        base_qi = int(base_qi * (1 + race_data["bonuses"]["qi"]))

    data["players"][uid_str] = {
        "realm": "Mortal Realm",
        "stage": "Body Refining [Entry]",
        "exp": 0,
        "qi": base_qi,
        "spirit_stones": 50,
        "equipment": {},
        "techniques": [],
        "current_technique": None,
        "sect": None,
        "guild": None,
        "guild_role": None,
        "base_power": base_power,
        "total_power": base_power,
        "pvp_wins": 0,
        "pvp_losses": 0,
        "last_pvp": "0",
        "last_dungeon": "0",
        "last_technique_find": "0",
        "last_daily_quest": "0",
        "dungeons_completed": 0,
        "techniques_learned": 0,
        "daily_streak": 0,
        "spirit_beasts": [],
        "current_beast": None,
        "inventory": {
            "spirit_herb": 0, "spirit_water": 0, "spirit_crystal": 0,
            "dragon_scale": 0, "phoenix_feather": 0, "dragon_heart": 0
        },
        "pills_crafted": 0,
        "achievements": [],
        "race": race,
        "gender": gender,
        "display_name": name,
        "created_at": datetime.datetime.now().isoformat(),
        "last_updated": datetime.datetime.now().isoformat(),
        "breakthroughs": 0,
        "daily_quests": {},
        "last_daily_claim": "0",
        "discovered_techniques": [],
        "guild_contributions": 0,
        "login_streak": 0,
        "last_login": str(time.time())
    }

    # Initialize daily quests
    for quest in DAILY_QUESTS:
        data["players"][uid_str]["daily_quests"][quest["id"]] = {
            "progress": 0,
            "completed": False,
            "claimed": False
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

def check_achievements(player_id, player_data):
    """Check and award achievements"""
    data = load_data()
    new_achievements = []

    for achievement_id, achievement_data in ACHIEVEMENTS.items():
        if (achievement_id not in player_data["achievements"] and 
            achievement_data["condition"](player_data)):

            # Award achievement
            player_data["achievements"].append(achievement_id)

            # Give rewards
            for reward_type, amount in achievement_data["reward"].items():
                if reward_type == "spirit_stones":
                    player_data["spirit_stones"] += amount
                elif reward_type == "exp":
                    player_data["exp"] = min(player_data["exp"] + amount, get_exp_cap(player_data))
                elif reward_type == "qi":
                    player_data["qi"] += amount
                elif reward_type == "power":
                    player_data["base_power"] += amount

            new_achievements.append(achievement_data)

    if new_achievements:
        update_player(player_id, player_data)

    return new_achievements

def reset_daily_quests():
    """Reset daily quests for all players"""
    data = load_data()
    now = datetime.datetime.now()
    last_reset = datetime.datetime.fromisoformat(data.get("daily_quests_reset", now.isoformat()))

    # Check if it's a new day
    if now.date() > last_reset.date():
        for player_id, player_data in data["players"].items():
            for quest in DAILY_QUESTS:
                player_data["daily_quests"][quest["id"]] = {
                    "progress": 0,
                    "completed": False,
                    "claimed": False
                }

        data["daily_quests_reset"] = now.isoformat()
        save_data(data)
        return True

    return False

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

    # Update daily quest progress
    winner["daily_quests"]["pvp_battle"]["progress"] += 1
    if winner["daily_quests"]["pvp_battle"]["progress"] >= winner["daily_quests"]["pvp_battle"].get("progress_needed", 1):
        winner["daily_quests"]["pvp_battle"]["completed"] = True

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
    exp_cap = get_exp_cap(player_data)

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
    exp_cap = get_exp_cap(p)

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
    embed.add_field(name="Final EXP", value=f"{p['exp']}/{exp_cap}", inline=True)

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
            exp_cap = get_exp_cap(p)

            # Cek jika sudah cap
            if p["exp"] >= exp_cap:
                break

            # Calculate gains - reduced EXP rate
            base_gain = random.randint(2, 6)
            gain = int(base_gain * realm_data["exp_multiplier"])
            qi_gain = random.randint(1, 5)
            power_gain = random.randint(1, 3)
            spirit_stones_gain = random.randint(1, realm_data["spirit_stone_gain"])

            # Apply race bonuses
            race_data = RACES.get(p.get("race", "human"), RACES["human"])
            if "exp" in race_data["bonuses"]:
                gain = int(gain * (1 + race_data["bonuses"]["exp"]))
            if "qi" in race_data["bonuses"]:
                qi_gain = int(qi_gain * (1 + race_data["bonuses"]["qi"]))

            # Adjust gain jika melebihi cap
            if p["exp"] + gain > exp_cap:
                gain = exp_cap - p["exp"]

            # Update player
            p["exp"] += gain
            p["qi"] += qi_gain
            p["base_power"] += power_gain
            p["spirit_stones"] += spirit_stones_gain

            # Update daily quest progress
            p["daily_quests"]["cultivate_5"]["progress"] += 1
            if p["daily_quests"]["cultivate_5"]["progress"] >= p["daily_quests"]["cultivate_5"].get("progress_needed", 5):
                p["daily_quests"]["cultivate_5"]["completed"] = True

            # Update power dengan teknik bonuses
            technique_bonus = 1 + sum(t['power_bonus'] for t in p["techniques"])
            set_bonus = calculate_set_bonus(p["equipment"])
            p["total_power"] = int(p["base_power"] * technique_bonus * (1 + set_bonus))

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
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===============================
# Event handlers
# ===============================
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} telah online!')
    print(f'🔑 Token valid: {bool(BOT_TOKEN)}')
    print(f'📊 Total players: {load_data()["total_players"]}')

    if BOT_TOKEN and BOT_TOKEN != "placeholder_token_untuk_development":
        print(f'🔒 Token length: {len(BOT_TOKEN)}')

    # Reset daily quests jika perlu
    reset_daily_quests()

    backup_data()
    print('🌟 Bot siap menerima command!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"📨 Received: {message.content} from {message.author}")

    # Cek jika user sudah terdaftar
    if not get_player(message.author.id):
        # Jika belum terdaftar dan bukan command registrasi, minta registrasi
        # HANYA di channel yang ditentukan
        if not message.content.startswith('!register') and message.channel.id == 1413513753726681220:
            await message.channel.send(
                f"👋 Welcome {message.author.mention}! You need to register first.\n"
                f"Use `!register` to start your cultivation journey!"
            )
            return

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Cooldown! Coba lagi dalam {error.retry_after:.1f} detik")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command tidak dikenali! Gunakan `!help` untuk melihat command yang tersedia.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Argument tidak lengkap! Gunakan `!help [command]` untuk info lengkap.")
    else:
        print(f"Error: {error}")
        await ctx.send("❌ Terjadi error! Silakan coba lagi atau hubungi admin.")

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
# Command: register - SISTEM REGISTRASI BARU
# ===============================
@bot.command()
async def register(ctx):
    """Registrasi player baru dengan pilihan race dan gender"""
    if get_player(ctx.author.id):
        return await ctx.send("❌ Anda sudah terdaftar! Gunakan `!status` untuk melihat profil Anda.")

    # Simpan data registrasi sementara
    PENDING_REGISTRATIONS[ctx.author.id] = {
        "step": "race",
        "data": {}
    }

    embed = discord.Embed(
        title="🎮 Registration - Choose Your Race",
        description="Pilih race untuk memulai perjalanan cultivation Anda:",
        color=0x7289da
    )

    for race_id, race_data in RACES.items():
        if not race_data.get("hidden", False):
            embed.add_field(
                name=f"{race_data['emoji']} {race_data['name']}",
                value=f"{race_data['description']}\n"
                      f"**Bonuses:** {', '.join([f'+{int(v*100)}% {k}' for k, v in race_data['bonuses'].items()])}",
                inline=False
            )

    embed.set_footer(text="Balas dengan nama race yang dipilih (contoh: human, demon, half_demon, beast)")
    await ctx.send(embed=embed)

    # Menunggu response race
    def check_race(m):
        return m.author == ctx.author and m.content.lower() in RACES.keys() and not RACES[m.content.lower()].get("hidden", False)

    try:
        race_msg = await bot.wait_for('message', timeout=60.0, check=check_race)
        race_choice = race_msg.content.lower()
        PENDING_REGISTRATIONS[ctx.author.id]["data"]["race"] = race_choice
        PENDING_REGISTRATIONS[ctx.author.id]["step"] = "gender"

        # Tampilkan pilihan gender
        embed = discord.Embed(
            title="🎮 Registration - Choose Your Gender",
            description="Pilih gender untuk karakter Anda:",
            color=0x7289da
        )

        for gender_id, gender_data in GENDERS.items():
            embed.add_field(
                name=f"{gender_data['emoji']} {gender_data['name']}",
                value=f"Pilih `{gender_id}` untuk {gender_data['name']}",
                inline=True
            )

        embed.set_footer(text="Balas dengan gender yang dipilih (contoh: male, female, other)")
        await ctx.send(embed=embed)

        # Menunggu response gender
        def check_gender(m):
            return m.author == ctx.author and m.content.lower() in GENDERS.keys()

        gender_msg = await bot.wait_for('message', timeout=60.0, check=check_gender)
        gender_choice = gender_msg.content.lower()
        PENDING_REGISTRATIONS[ctx.author.id]["data"]["gender"] = gender_choice
        PENDING_REGISTRATIONS[ctx.author.id]["step"] = "confirm"

        # Konfirmasi registrasi
        race_data = RACES[race_choice]
        gender_data = GENDERS[gender_choice]

        embed = discord.Embed(
            title="🎮 Registration - Confirmation",
            description="Konfirmasi pilihan Anda:",
            color=0x00ff00
        )
        embed.add_field(name="Race", value=f"{race_data['emoji']} {race_data['name']}", inline=True)
        embed.add_field(name="Gender", value=f"{gender_data['emoji']} {gender_data['name']}", inline=True)
        embed.add_field(name="Bonuses", value="\n".join([f"+{int(v*100)}% {k}" for k, v in race_data["bonuses"].items()]), inline=False)
        embed.set_footer(text="Balas 'confirm' untuk melanjutkan atau 'cancel' untuk membatalkan")

        await ctx.send(embed=embed)

        # Menunggu konfirmasi
        def check_confirm(m):
            return m.author == ctx.author and m.content.lower() in ['confirm', 'cancel']

        confirm_msg = await bot.wait_for('message', timeout=60.0, check=check_confirm)

        if confirm_msg.content.lower() == 'confirm':
            # Buat player baru
            player_data = create_new_player(
                ctx.author.id, 
                race_choice, 
                gender_choice,
                ctx.author.name
            )

            # Hapus dari pending registrations
            del PENDING_REGISTRATIONS[ctx.author.id]

            embed = discord.Embed(
                title="🎉 Registration Successful!",
                description=f"Selamat datang {ctx.author.mention} di dunia cultivation!",
                color=0x00ff00
            )
            embed.add_field(name="Race", value=f"{race_data['emoji']} {race_data['name']}", inline=True)
            embed.add_field(name="Gender", value=f"{gender_data['emoji']} {gender_data['name']}", inline=True)
            embed.add_field(name="Starting Power", value=player_data["base_power"], inline=True)
            embed.add_field(name="Starting Qi", value=player_data["qi"], inline=True)
            embed.add_field(name="Realm", value=player_data["realm"], inline=True)
            embed.add_field(name="Stage", value=player_data["stage"], inline=True)
            embed.set_footer(text="Gunakan !tutorial untuk panduan memulai atau !status untuk melihat profil")

            await ctx.send(embed=embed)
        else:
            del PENDING_REGISTRATIONS[ctx.author.id]
            await ctx.send("❌ Registrasi dibatalkan.")

    except asyncio.TimeoutError:
        if ctx.author.id in PENDING_REGISTRATIONS:
            del PENDING_REGISTRATIONS[ctx.author.id]
        await ctx.send("⏰ Waktu registrasi habis! Gunakan `!register` lagi untuk memulai.")

# ===============================
# Command: profile - TAMPILKAN PROFIL DENGAN RACE DAN GENDER
# ===============================
@bot.command()
async def profile(ctx, member: discord.Member = None):
    """Lihat profil player dengan detail race dan gender"""
    target = member or ctx.author
    p = get_player(target.id)

    if not p:
        if target == ctx.author:
            return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")
        else:
            return await ctx.send("❌ Player tersebut belum terdaftar!")

    race_data = RACES.get(p.get("race", "human"), RACES["human"])
    gender_data = GENDERS.get(p.get("gender", "other"), GENDERS["other"])
    exp_cap = get_exp_cap(p)

    embed = discord.Embed(
        title=f"📊 {p.get('display_name', target.name)}'s Profile",
        color=0x7289da
    )

    # Avatar dan info dasar
    embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
    embed.add_field(name="Race", value=f"{race_data['emoji']} {race_data['name']}", inline=True)
    embed.add_field(name="Gender", value=f"{gender_data['emoji']} {gender_data['name']}", inline=True)
    embed.add_field(name="Level", value=get_player_level(p), inline=True)

    # Race bonuses
    bonuses_text = "\n".join([f"+{int(v*100)}% {k}" for k, v in race_data["bonuses"].items()])
    embed.add_field(name="Race Bonuses", value=bonuses_text, inline=False)

    # Progress
    embed.add_field(name="Realm", value=p["realm"], inline=True)
    embed.add_field(name="Stage", value=p["stage"], inline=True)
    embed.add_field(name="EXP", value=f"{p['exp']}/{exp_cap}", inline=True)

    # Stats
    embed.add_field(name="Total Power", value=p["total_power"], inline=True)
    embed.add_field(name="Qi", value=p["qi"], inline=True)
    embed.add_field(name="Spirit Stones", value=p["spirit_stones"], inline=True)

    # Additional info
    embed.add_field(name="PvP Record", value=f"🏆 {p['pvp_wins']}W / 💀 {p['pvp_losses']}L", inline=True)
    embed.add_field(name="Dungeons", value=f"Completed: {p['dungeons_completed']}", inline=True)
    embed.add_field(name="Techniques", value=f"Learned: {p['techniques_learned']}", inline=True)

    # Join date
    join_date = datetime.datetime.fromisoformat(p["created_at"]).strftime("%Y-%m-%d")
    embed.set_footer(text=f"Registered on {join_date}")

    await ctx.send(embed=embed)

# ===============================
# Command: raceinfo - INFO TENTANG RACE
# ===============================
@bot.command()
async def raceinfo(ctx, race_name: str = None):
    """Lihat informasi detail tentang race"""
    if race_name and race_name.lower() in RACES:
        race_data = RACES[race_name.lower()]
        embed = discord.Embed(
            title=f"{race_data['emoji']} {race_data['name']}",
            description=race_data["description"],
            color=0x7289da
        )

        bonuses_text = "\n".join([f"+{int(v*100)}% {k}" for k, v in race_data["bonuses"].items()])
        embed.add_field(name="Bonuses", value=bonuses_text, inline=False)

        if race_data.get("hidden"):
            embed.set_footer(text="⭐ Hidden Race - Special availability")

        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="🏛️ Available Races",
            description="Pilih race untuk memulai perjalanan cultivation:",
            color=0x7289da
        )

        for race_id, race_data in RACES.items():
            if not race_data.get("hidden", False):
                bonuses_text = ", ".join([f"+{int(v*100)}% {k}" for k, v in race_data["bonuses"].items()])
                embed.add_field(
                    name=f"{race_data['emoji']} {race_data['name']}",
                    value=f"{race_data['description']}\n**Bonuses:** {bonuses_text}",
                    inline=False
                )

        embed.set_footer(text="Gunakan !raceinfo [race_name] untuk info detail tentang race tertentu")
        await ctx.send(embed=embed)

# ===============================
# Command: tutorial (NEW)
# ===============================
@bot.command()
async def tutorial(ctx):
    """Panduan memulai cultivation untuk pemula"""
    embed = discord.Embed(
        title="🎮 Tutorial - Memulai Perjalanan Cultivation",
        description="Selamat datang di dunia cultivation! Berikut panduan untuk memulai:",
        color=0x00ff00
    )

    embed.add_field(
        name="🚀 Langkah Pertama",
        value="1. `!register` - Registrasi dengan pilih race dan gender\n"
              "2. `!status` - Lihat status cultivationmu\n"
              "3. `!cultivate` - Lakukan cultivation manual\n"
              "4. `!raceinfo` - Lihat info tentang race yang tersedia",
        inline=False
    )

    embed.add_field(
        name="🎯 Memilih Race",
        value="• **Human**: Balanced, bonus EXP dan Qi\n"
              "• **Demon**: High power, bonus attack\n"
              "• **Half-Demon**: Balanced hybrid\n"
              "• **Beast Race**: High defense dan health\n"
              "• Gunakan `!raceinfo` untuk detail lengkap",
        inline=False
    )

    embed.add_field(
        name="📈 Naik Level",
        value="• Kumpulkan EXP dengan cultivation\n"
              "• Gunakan `!breakthrough` saat EXP cukup\n"
              "• Naik stage demi stage hingga realm tertinggi",
        inline=False
    )

    embed.add_field(
        name="💎 Resource Management",
        value="• **EXP**: Untuk naik level\n"
              "• **Qi**: Currency untuk beli equipment\n"
              "• **Spirit Stones**: Currency khusus teknik",
        inline=False
    )

    embed.add_field(
        name="⚔️ Fitur Lainnya",
        value="• `!shop` - Beli equipment\n"
              "• `!find_technique` - Cari teknik cultivation\n"
              "• `!pvp @user` - Battle dengan player lain\n"
              "• `!dungeons` - Jelajahi dungeon",
        inline=False
    )

    embed.set_footer(text="Gunakan !help untuk melihat semua command yang tersedia")
    await ctx.send(embed=embed)

# ===============================
# Command: realms
# ===============================
@bot.command()
async def realms(ctx):
    """Lihat semua realm dan stages dengan detail"""
    embed = discord.Embed(
        title="🌌 Cultivation Realms Hierarchy",
        description="Path to immortality and beyond\n*Each stage has its own EXP requirement for breakthrough*",
        color=0x7289da
    )

    for realm_name, realm_data in REALMS.items():
        stage_count = len(realm_data["stages"])
        first_stage_exp = int(100 * realm_data["exp_multiplier"])
        last_stage_exp = int(stage_count * 100 * realm_data["exp_multiplier"])

        # Create a compact stage list
        stages_list = " → ".join(realm_data["stages"])

        # Due to Discord character limits, we'll show first few stages and indicate total
        if len(stages_list) > 600:
            first_3_stages = " → ".join(realm_data["stages"][:3])
            stages_display = f"{first_3_stages} → ... ({len(realm_data['stages'])} total stages)"
        else:
            stages_display = stages_list

        embed.add_field(
            name=f"{realm_name} 🌟 ({stage_count} Stages)",
            value=f"**EXP Range:** {first_stage_exp:,} - {last_stage_exp:,} | **Power:** {realm_data['power_multiplier']}× | **Stones:** {realm_data['spirit_stone_gain']}/cultivate\n\n"
                  f"**Progression Path:**\n{stages_display}",
            inline=False
        )

    embed.set_footer(text="💡 EXP needed = Stage Position × 100 × Realm Multiplier")
    await ctx.send(embed=embed)

# ===============================
# Command: boss
# ===============================
@bot.command()
async def boss(ctx, action: str = None, boss_name: str = None):
    """Sistem boss - Lihat atau tantang boss dungeon"""
    if not BOSS_SYSTEM_LOADED:
        return await ctx.send("❌ Boss system sedang maintenance!")
    
    if action == "list":
        await list_bosses(ctx)
    elif action == "challenge" and boss_name:
        await challenge_boss(ctx, boss_name)
    elif action == "status":
        await boss_status(ctx)
    elif action == "cooldown":
        await boss_cooldown(ctx)
    else:
        await show_boss_info(ctx)

# ===============================
# Command: myrealm
# ===============================
@bot.command()
async def myrealm(ctx):
    """Lihat info detail tentang realm kamu sekarang"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    realm_data = REALMS[p["realm"]]
    current_stage_idx = realm_data["stages"].index(p["stage"])
    current_exp_cap = get_exp_cap(p)

    next_stage = None
    exp_needed = None
    if current_stage_idx + 1 < len(realm_data["stages"]):
        next_stage = realm_data["stages"][current_stage_idx + 1]
        exp_needed = int((current_stage_idx + 2) * 100 * realm_data["exp_multiplier"])
    else:
        realm_idx = REALM_ORDER.index(p["realm"])
        if realm_idx + 1 < len(REALM_ORDER):
            next_realm = REALM_ORDER[realm_idx + 1]
            next_stage = f"Ascend to {next_realm}"
            exp_needed = current_exp_cap

    embed = discord.Embed(
        title=f"🌠 {ctx.author.name}'s Realm Progress",
        color=realm_data["color"]
    )

    embed.add_field(
        name="Current Realm",
        value=f"**{p['realm']}**",
        inline=True
    )

    embed.add_field(
        name="Current Stage", 
        value=f"**{p['stage']}**\nStage {current_stage_idx + 1}/{len(realm_data['stages'])}",
        inline=True
    )

    embed.add_field(
        name="EXP Progress",
        value=f"{p['exp']}/{current_exp_cap}",
        inline=True
    )

    if next_stage and exp_needed:
        embed.add_field(
            name="Next Breakthrough",
            value=f"**{next_stage}**\nNeeded: {exp_needed} EXP",
            inline=False
        )

    progress_percentage = min(100, (p["exp"] / current_exp_cap) * 100)
    progress_bar = "█" * int(progress_percentage / 10) + "░" * (10 - int(progress_percentage / 10))

    embed.add_field(
        name="Current Stage Progress",
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
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    realm_data = REALMS[p["realm"]]
    current_stage_idx = realm_data["stages"].index(p["stage"])
    current_exp_cap = get_exp_cap(p)
    stage_progress = (p["exp"] / current_exp_cap) * 100

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

    embed.add_field(
        name="Current Stage Progress",
        value=f"EXP: {p['exp']}/{current_exp_cap} ({stage_progress:.1f}%)",
        inline=False
    )

    global_bar = "█" * int(global_progress / 10) + "░" * (10 - int(global_progress / 10))
    embed.add_field(
        name="Global Progress",
        value=f"```[{global_bar}] {global_progress:.1f}%```",
        inline=False
    )

    if p["realm"] != "God Realm" or p["stage"] != "Universe Creator [Peak]":
        next_milestone = ""
        next_exp_needed = 0
        if current_stage_idx + 1 < len(realm_data["stages"]):
            next_milestone = realm_data["stages"][current_stage_idx + 1]
            next_exp_needed = int((current_stage_idx + 2) * 100 * realm_data["exp_multiplier"])
        else:
            next_realm_idx = REALM_ORDER.index(p["realm"]) + 1
            if next_realm_idx < len(REALM_ORDER):
                next_milestone = REALM_ORDER[next_realm_idx]
                next_realm_data = REALMS[REALM_ORDER[next_realm_idx]]
                next_exp_needed = int(100 * next_realm_data["exp_multiplier"])

        embed.add_field(
            name="Next Milestone",
            value=f"**{next_milestone}**\nNeeded: {next_exp_needed} EXP",
            inline=True
        )

    embed.set_footer(text="Total stages: Mortal(30) + Immortal(36) + God(45) = 111 stages")
    await ctx.send(embed=embed)

# ===============================
# Command: cultivate (dengan cooldown dan race bonus)
# ===============================
@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def cultivate(ctx):
    """Cultivate manual sekali dengan race bonus"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    realm_data = REALMS[p["realm"]]
    exp_cap = get_exp_cap(p)
    race_data = RACES.get(p.get("race", "human"), RACES["human"])

    base_gain = random.randint(5, 15)
    gain = int(base_gain * realm_data["exp_multiplier"])

    # Apply race bonus
    if "exp" in race_data["bonuses"]:
        gain = int(gain * (1 + race_data["bonuses"]["exp"]))

    qi_gain = random.randint(1, 5)
    if "qi" in race_data["bonuses"]:
        qi_gain = int(qi_gain * (1 + race_data["bonuses"]["qi"]))

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

    # Update daily quest progress
    p["daily_quests"]["cultivate_5"]["progress"] += 1
    if p["daily_quests"]["cultivate_5"]["progress"] >= p["daily_quests"]["cultivate_5"].get("progress_needed", 5):
        p["daily_quests"]["cultivate_5"]["completed"] = True

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

    # Tampilkan race bonus jika ada
    if "exp" in race_data["bonuses"] or "qi" in race_data["bonuses"]:
        bonus_text = []
        if "exp" in race_data["bonuses"]:
            bonus_text.append(f"+{int(race_data['bonuses']['exp']*100)}% EXP")
        if "qi" in race_data["bonuses"]:
            bonus_text.append(f"+{int(race_data['bonuses']['qi']*100)}% Qi")
        embed.add_field(name="Race Bonus", value=", ".join(bonus_text), inline=False)

    await ctx.send(embed=embed)

# ===============================
# Command: start_cultivate (IDLE SYSTEM)
# ===============================
@bot.command()
async def start_cultivate(ctx):
    """Mulai cultivation idle secara otomatis"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    realm_data = REALMS[p["realm"]]
    exp_cap = get_exp_cap(p)

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

    exp_gain = int(hours * 200 * realm_data["exp_multiplier"])
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
    embed.add_field(name="Rate", value=f"{200 * realm_data['exp_multiplier']} EXP/hour", inline=True)

    await ctx.send(embed=embed)

# ===============================
# Command: breakthrough
# ===============================
@bot.command()
async def breakthrough(ctx):
    """Breakthrough ke stage berikutnya tanpa kehilangan EXP berlebih"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    realm_data = REALMS[p["realm"]]
    stages = realm_data["stages"]
    current_stage_idx = stages.index(p["stage"])
    
    # Current stage EXP cap adalah requirement breakthrough
    required_exp = get_exp_cap(p)

    if p["exp"] < required_exp:
        return await ctx.send(f"❌ Not enough EXP. You need {required_exp} EXP to breakthrough! (Current: {p['exp']}/{required_exp})")

    # Hitung kelebihan EXP setelah breakthrough
    excess_exp = p["exp"] - required_exp
    
    if current_stage_idx + 1 < len(stages):
        # Naik ke stage berikutnya di realm yang sama
        next_stage = stages[current_stage_idx + 1]
        p["stage"] = next_stage
        
        # ✅ PERBAIKAN: Simpan kelebihan EXP, jangan reset ke 0!
        p["exp"] = excess_exp  # Hanya kurangi dengan EXP yang dibutuhkan
        
        p["base_power"] += 15
        p["breakthroughs"] += 1
        
        # Update daily quest progress
        p["daily_quests"]["breakthrough"]["progress"] += 1
        if p["daily_quests"]["breakthrough"]["progress"] >= p["daily_quests"]["breakthrough"].get("progress_needed", 1):
            p["daily_quests"]["breakthrough"]["completed"] = True

        # Recalculate total power
        technique_bonus = 1 + sum(t['power_bonus'] for t in p["techniques"])
        set_bonus = calculate_set_bonus(p["equipment"])
        p["total_power"] = int(p["base_power"] * technique_bonus * (1 + set_bonus))
        
        message = f"🔥 {ctx.author.mention} broke through to **{next_stage}**! ({excess_exp} EXP carried over)"
        
    else:
        # Naik ke realm berikutnya
        realm_idx = REALM_ORDER.index(p["realm"])
        if realm_idx + 1 < len(REALM_ORDER):
            next_realm = REALM_ORDER[realm_idx + 1]
            p["realm"] = next_realm
            p["stage"] = REALMS[next_realm]["stages"][0]
            
            # ✅ PERBAIKAN: Simpan kelebihan EXP untuk realm baru
            p["exp"] = excess_exp
            
            p["base_power"] += 50
            p["breakthroughs"] += 1
            
            # Update daily quest progress
            p["daily_quests"]["breakthrough"]["progress"] += 1
            if p["daily_quests"]["breakthrough"]["progress"] >= p["daily_quests"]["breakthrough"].get("progress_needed", 1):
                p["daily_quests"]["breakthrough"]["completed"] = True

            # Recalculate total power
            technique_bonus = 1 + sum(t['power_bonus'] for t in p["techniques"])
            set_bonus = calculate_set_bonus(p["equipment"])
            p["total_power"] = int(p["base_power"] * technique_bonus * (1 + set_bonus))
            
            message = f"🌟 {ctx.author.mention} ascended to **{next_realm}**! ({excess_exp} EXP carried over)"
        else:
            return await ctx.send("🎉 You already reached the peak realm!")

    update_player(ctx.author.id, p)

    data = load_data()
    data["server_stats"]["total_breakthroughs"] += 1
    save_data(data)

    # Kirim embed yang informatif
    embed = discord.Embed(
        title="🚀 Breakthrough Successful!",
        description=message,
        color=0x00ff00
    )
    
    embed.add_field(name="New Stage", value=p["stage"], inline=True)
    embed.add_field(name="Current EXP", value=f"{p['exp']}/{get_exp_cap(p)}", inline=True)
    embed.add_field(name="Total Power", value=p["total_power"], inline=True)
    embed.add_field(name="EXPreserved", value=f"✅ {excess_exp} EXP carried over", inline=True)
    
    await ctx.send(embed=embed)

# ===============================
# Command: find_technique
# ===============================
@bot.command()
@commands.cooldown(1, 3600, commands.BucketType.user)
async def find_technique(ctx):
    """Mencari teknik cultivation baru secara random"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    now = time.time()
    last_find = float(p.get("last_technique_find", "0"))

    if last_find + 3600 > now:
        remaining = int(last_find + 3600 - now)
        return await ctx.send(f"⏳ Anda harus menunggu {remaining//60} menit sebelum mencari teknik lagi!")

    technique = generate_random_technique(p["realm"], p["stage"])

    p["last_technique_find"] = str(now)
    p["discovered_techniques"].append(technique)
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
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    # Find technique in discovered techniques
    technique = None
    for tech in p["discovered_techniques"]:
        if tech["id"] == technique_id:
            technique = tech
            break

    if not technique:
        return await ctx.send("❌ Teknik tidak ditemukan! Gunakan `!find_technique` untuk mencari teknik.")

    if p["spirit_stones"] < technique["cost"]:
        return await ctx.send(f"❌ Tidak cukup Spirit Stones! Butuh {technique['cost']}, kamu punya {p['spirit_stones']}")

    if any(t['id'] == technique_id for t in p["techniques"]):
        return await ctx.send("❌ Anda sudah menguasai teknik ini!")

    p["spirit_stones"] -= technique["cost"]
    p["techniques"].append(technique)
    p["techniques_learned"] += 1
    p["total_power"] = int(p["base_power"] * (1 + sum(t['power_bonus'] for t in p["techniques"])))

    # Remove from discovered techniques
    p["discovered_techniques"] = [tech for tech in p["discovered_techniques"] if tech["id"] != technique_id]

    # Update daily quest progress
    p["daily_quests"]["learn_technique"]["progress"] += 1
    if p["daily_quests"]["learn_technique"]["progress"] >= p["daily_quests"]["learn_technique"].get("progress_needed", 1):
        p["daily_quests"]["learn_technique"]["completed"] = True

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
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

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
# Command: discovered_techniques
# ===============================
@bot.command()
async def discovered_techniques(ctx):
    """Lihat teknik yang sudah ditemukan tapi belum dipelajari"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    if not p["discovered_techniques"]:
        return await ctx.send("❌ Anda belum menemukan teknik apapun! Gunakan `!find_technique` untuk mencari teknik.")

    embed = discord.Embed(
        title=f"📜 {ctx.author.name}'s Discovered Techniques",
        description="Teknik yang ditemukan tapi belum dipelajari:",
        color=0x7289da
    )

    for technique in p["discovered_techniques"]:
        embed.add_field(
            name=f"{technique['emoji']} {technique['element_emoji']} {technique['name']}",
            value=f"**Cost:** {technique['cost']} Spirit Stones\n"
                  f"**Bonus:** +{technique['power_bonus']*100}% Power\n"
                  f"**ID:** `{technique['id']}`",
            inline=True
        )

    embed.set_footer(text="Gunakan !learn_technique [id] untuk mempelajari teknik")
    await ctx.send(embed=embed)

# ===============================
# Command: status (IMPROVED dengan race dan gender)
# ===============================
@bot.command()
async def status(ctx):
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    realm_data = REALMS[p["realm"]]
    level = get_player_level(p)
    exp_cap = get_exp_cap(p)
    race_data = RACES.get(p.get("race", "human"), RACES["human"])
    gender_data = GENDERS.get(p.get("gender", "other"), GENDERS["other"])

    embed = discord.Embed(
        title=f"📊 {p.get('display_name', ctx.author.name)}'s Cultivation Status",
        color=realm_data["color"]
    )

    # Info race dan gender
    embed.add_field(
        name="🧬 Identity",
        value=f"**Race:** {race_data['emoji']} {race_data['name']}\n"
              f"**Gender:** {gender_data['emoji']} {gender_data['name']}",
        inline=False
    )

    # Realm dan stage
    embed.add_field(
        name="🌌 Realm & Stage",
        value=f"{p['realm']}\n**{p['stage']}** (Lv. {level})",
        inline=True
    )

    # Power stats
    technique_bonus = sum(t['power_bonus'] for t in p['techniques'])
    set_bonus = calculate_set_bonus(p['equipment'])
    total_bonus = technique_bonus + set_bonus

    embed.add_field(
        name="⭐ Power Stats",
        value=f"**Total:** {p['total_power']}\n**Base:** {p['base_power']}\n**Bonus:** +{total_bonus*100:.0f}%",
        inline=True
    )

    # Resources
    embed.add_field(
        name="💎 Resources",
        value=f"EXP: {p['exp']}/{exp_cap}\nQi: {p['qi']}\nSpirit Stones: {p['spirit_stones']}",
        inline=True
    )

    # Race bonuses
    bonuses_text = "\n".join([f"+{int(v*100)}% {k}" for k, v in race_data["bonuses"].items()])
    embed.add_field(
        name="🎯 Race Bonuses",
        value=bonuses_text,
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
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    player_realm = p["realm"]

    # Organize equipment by realm
    realms_equipment = {
        "Mortal Realm": [],
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
async def buy(ctx, item_id: str):
    """Beli equipment dari shop"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    if item_id not in EQUIPMENT_SHOP:
        return await ctx.send("❌ Item tidak ditemukan! Gunakan `!shop` untuk melihat item yang tersedia.")

    item_data = EQUIPMENT_SHOP[item_id]

    # Check if player can access this realm's equipment
    if not can_access_equipment(p["realm"], item_data["realm"]):
        return await ctx.send(f"❌ Realm Anda ({p['realm']}) terlalu rendah untuk membeli equipment {item_data['realm']}!")

    if p["qi"] < item_data["cost"]:
        return await ctx.send(f"❌ Qi tidak cukup! Butuh {item_data['cost']} Qi, Anda memiliki {p['qi']} Qi.")

    # Check if already have this item type equipped
    current_equipment = p.get("equipment", {})
    for equipped_item in current_equipment.keys():
        if EQUIPMENT_SHOP.get(equipped_item, {}).get("type") == item_data["type"]:
            return await ctx.send(f"❌ Anda sudah memiliki {item_data['type']} equipment! Jual yang lama dulu.")

    # Purchase item
    p["qi"] -= item_data["cost"]
    if "equipment" not in p:
        p["equipment"] = {}
    p["equipment"][item_id] = item_data["power"]

    # Recalculate total power
    technique_bonus = 1 + sum(t['power_bonus'] for t in p["techniques"])
    set_bonus = calculate_set_bonus(p["equipment"])
    p["total_power"] = int((p["base_power"] + sum(p["equipment"].values())) * technique_bonus * (1 + set_bonus))

    update_player(ctx.author.id, p)

    embed = discord.Embed(
        title="🛒 Purchase Successful!",
        description=f"{ctx.author.mention} membeli {item_data['emoji']} {item_data['name']}",
        color=0x00ff00
    )
    embed.add_field(name="Power", value=f"+{item_data['power']}", inline=True)
    embed.add_field(name="Cost", value=f"{item_data['cost']} Qi", inline=True)
    embed.add_field(name="Remaining Qi", value=f"{p['qi']}", inline=True)
    embed.add_field(name="Total Power", value=f"{p['total_power']}", inline=True)

    await ctx.send(embed=embed)

# ===============================
# Command: inventory
# ===============================
@bot.command()
async def inventory(ctx):
    """Lihat inventory dan equipment yang dimiliki"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    embed = discord.Embed(
        title=f"🎒 {ctx.author.name}'s Inventory",
        color=0x7289da
    )

    # Equipment section
    if p.get("equipment"):
        equip_text = ""
        total_equip_power = 0
        set_counts = {}

        for item_id, power in p["equipment"].items():
            item_data = EQUIPMENT_SHOP.get(item_id, {"name": item_id.replace("_", " ").title(), "emoji": "⚙️"})
            equip_text += f"{item_data['emoji']} {item_data['name']} (+{power})\n"
            total_equip_power += power

            # Count set items
            if "set" in item_data:
                set_name = item_data["set"]
                set_counts[set_name] = set_counts.get(set_name, 0) + 1

        embed.add_field(
            name="⚔️ Equipment",
            value=equip_text or "No equipment",
            inline=False
        )
        embed.add_field(
            name="Total Equipment Power",
            value=f"+{total_equip_power}",
            inline=True
        )

        # Show set bonuses
        if set_counts:
            set_bonus_text = ""
            for set_name, count in set_counts.items():
                if set_name in SET_BONUSES:
                    bonus = 0
                    if count >= 3 and "3_piece" in SET_BONUSES[set_name]:
                        bonus = SET_BONUSES[set_name]["3_piece"]
                    elif count >= 2 and "2_piece" in SET_BONUSES[set_name]:
                        bonus = SET_BONUSES[set_name]["2_piece"]

                    if bonus > 0:
                        set_bonus_text += f"{set_name.title()} Set ({count}/3): +{bonus*100:.0f}% Power\n"

            if set_bonus_text:
                embed.add_field(
                    name="✨ Set Bonuses",
                    value=set_bonus_text,
                    inline=False
                )
    else:
        embed.add_field(
            name="⚔️ Equipment",
            value="No equipment equipped",
            inline=False
        )

    # Inventory items
    if any(count > 0 for count in p["inventory"].values()):
        inventory_text = ""
        for item, count in p["inventory"].items():
            if count > 0:
                item_data = ALCHEMY_INGREDIENTS.get(item, {"name": item.replace("_", " ").title(), "emoji": "📦"})
                inventory_text += f"{item_data['emoji']} {item_data['name']}: {count}\n"

        embed.add_field(
            name="📦 Inventory Items",
            value=inventory_text or "No items",
            inline=False
        )
    else:
        embed.add_field(
            name="📦 Inventory",
            value="No items in inventory",
            inline=False
        )

    # Spirit Beasts
    if p.get("spirit_beasts"):
        beasts_text = ""
        for beast in p["spirit_beasts"]:
            beasts_text += f"{beast['emoji']} {beast['name']} (+{beast['power']} power)\n"

        embed.add_field(
            name="🐉 Spirit Beasts",
            value=beasts_text or "No spirit beasts",
            inline=False
        )
    else:
        embed.add_field(
            name="🐉 Spirit Beasts",
            value="No spirit beasts tamed",
            inline=False
        )

    await ctx.send(embed=embed)

# ===============================
# Command: sell
# ===============================
@bot.command()
async def sell(ctx, item_id: str):
    """Jual equipment yang dimiliki"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    if "equipment" not in p or item_id not in p["equipment"]:
        return await ctx.send("❌ Anda tidak memiliki equipment tersebut!")

    item_data = EQUIPMENT_SHOP.get(item_id, {})
    sell_price = int(item_data.get("cost", 0) * 0.6)  # 60% of original price

    # Remove item and give refund
    del p["equipment"][item_id]
    p["qi"] += sell_price

    # Recalculate power
    technique_bonus = 1 + sum(t['power_bonus'] for t in p["techniques"])
    set_bonus = calculate_set_bonus(p["equipment"])
    p["total_power"] = int((p["base_power"] + sum(p["equipment"].values())) * technique_bonus * (1 + set_bonus))

    update_player(ctx.author.id, p)

    embed = discord.Embed(
        title="💰 Sale Successful!",
        description=f"{ctx.author.mention} menjual {item_data.get('emoji', '⚙️')} {item_data.get('name', item_id)}",
        color=0xffd700
    )
    embed.add_field(name="Sale Price", value=f"{sell_price} Qi", inline=True)
    embed.add_field(name="New Qi Total", value=f"{p['qi']}", inline=True)
    embed.add_field(name="Total Power", value=f"{p['total_power']}", inline=True)

    await ctx.send(embed=embed)

# ===============================
# Command: pvp
# ===============================
@bot.command()
@commands.cooldown(1, 300, commands.BucketType.user)  # 5 minute cooldown
async def pvp(ctx, member: discord.Member):
    """Challenge another player to a battle"""
    if member.id == ctx.author.id:
        return await ctx.send("❌ Anda tidak bisa battle dengan diri sendiri!")

    if member.bot:
        return await ctx.send("❌ Anda tidak bisa battle dengan bot!")

    attacker = get_player(ctx.author.id)
    defender = get_player(member.id)

    if not attacker or not defender:
        return await ctx.send("❌ Salah satu player belum terdaftar! Gunakan `!register` untuk memulai.")

    # Check if defender is available for battle
    if defender["total_power"] < 10:
        return await ctx.send("❌ Player tersebut terlalu lemah untuk battle!")

    embed = discord.Embed(
        title="⚔️ Battle Challenge",
        description=f"{ctx.author.mention} menantang {member.mention} untuk battle!",
        color=0xff0000
    )
    embed.add_field(name="Attacker Power", value=attacker["total_power"], inline=True)
    embed.add_field(name="Defender Power", value=defender["total_power"], inline=True)
    embed.add_field(name="Cooldown", value="5 menit", inline=True)

    message = await ctx.send(embed=embed)

    # Add reaction for acceptance
    await message.add_reaction('✅')
    await message.add_reaction('❌')

    def check(reaction, user):
        return user == member and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == message.id

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

        if str(reaction.emoji) == '✅':
            await ctx.send(f"🎉 {member.mention} menerima tantangan! Memulai battle...")
            await start_battle(ctx.author.id, member.id, ctx)
        else:
            await ctx.send(f"❌ {member.mention} menolak tantangan battle.")

    except asyncio.TimeoutError:
        await ctx.send("⏰ Waktu penerimaan battle habis!")

# ===============================
# Command: leaderboard
# ===============================
@bot.command()
async def leaderboard(ctx, page: int = 1):
    """Lihat ranking cultivator"""
    players = get_all_players()

    if not players:
        return await ctx.send("❌ Belum ada player yang terdaftar!")

    # Sort players by total power
    sorted_players = sorted(
        [(uid, data) for uid, data in players.items()],
        key=lambda x: x[1]["total_power"],
        reverse=True
    )

    items_per_page = 10
    total_pages = (len(sorted_players) + items_per_page - 1) // items_per_page

    if page < 1 or page > total_pages:
        return await ctx.send(f"❌ Halaman {page} tidak valid! Total halaman: {total_pages}")

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_players = sorted_players[start_idx:end_idx]

    embed = discord.Embed(
        title="🏆 Cultivation Leaderboard",
        description=f"Top cultivators by power (Page {page}/{total_pages})",
        color=0xffd700
    )

    for i, (uid, player) in enumerate(page_players, start=start_idx + 1):
        try:
            user = await bot.fetch_user(int(uid))
            username = user.name
        except:
            username = f"Unknown User ({uid})"

        embed.add_field(
            name=f"{i}. {username}",
            value=f"**Power:** {player['total_power']} | **Realm:** {player['realm']}\n**Stage:** {player['stage']} | **Wins:** {player['pvp_wins']}",
            inline=False
        )

    embed.set_footer(text=f"Total players: {len(sorted_players)} | Use !leaderboard [page] untuk halaman lain")
    await ctx.send(embed=embed)

# ===============================
# Command: myrank
# ===============================
@bot.command()
async def myrank(ctx):
    """Lihat ranking Anda"""
    players = get_all_players()
    player_id = str(ctx.author.id)

    if player_id not in players:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    # Sort players by total power
    sorted_players = sorted(
        [(uid, data) for uid, data in players.items()],
        key=lambda x: x[1]["total_power"],
        reverse=True
    )

    # Find player's rank
    player_rank = None
    for rank, (uid, _) in enumerate(sorted_players, start=1):
        if uid == player_id:
            player_rank = rank
            break

    if player_rank is None:
        return await ctx.send("❌ Ranking tidak ditemukan!")

    player_data = players[player_id]
    total_players = len(sorted_players)
    percentile = (player_rank / total_players) * 100

    embed = discord.Embed(
        title=f"🏅 Your Ranking - #{player_rank}",
        description=f"{ctx.author.name}'s cultivation progress",
        color=0xffd700
    )

    embed.add_field(name="Total Power", value=player_data["total_power"], inline=True)
    embed.add_field(name="Realm", value=player_data["realm"], inline=True)
    embed.add_field(name="Stage", value=player_data["stage"], inline=True)
    embed.add_field(name="PvP Record", value=f"{player_data['pvp_wins']}W/{player_data['pvp_losses']}L", inline=True)
    embed.add_field(name="Total Players", value=total_players, inline=True)
    embed.add_field(name="Percentile", value=f"Top {percentile:.1f}%", inline=True)

    # Progress to next rank
    if player_rank > 1:
        next_player_power = sorted_players[player_rank-2][1]["total_power"]
        power_needed = next_player_power - player_data["total_power"] + 1
        embed.add_field(
            name="Next Rank",
            value=f"Need +{power_needed} power to reach rank #{player_rank-1}",
            inline=False
        )

    await ctx.send(embed=embed)

# ===============================
# Command: pvp_rank
# ===============================
@bot.command()
async def pvp_rank(ctx, page: int = 1):
    """Lihat ranking PvP"""
    players = get_all_players()

    if not players:
        return await ctx.send("❌ Belum ada player yang terdaftar!")

    # Sort players by PvP wins
    sorted_players = sorted(
        [(uid, data) for uid, data in players.items()],
        key=lambda x: (x[1]["pvp_wins"], -x[1]["pvp_losses"]),
        reverse=True
    )

    items_per_page = 10
    total_pages = (len(sorted_players) + items_per_page - 1) // items_per_page

    if page < 1 or page > total_pages:
        return await ctx.send(f"❌ Halaman {page} tidak valid! Total halaman: {total_pages}")

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_players = sorted_players[start_idx:end_idx]

    embed = discord.Embed(
        title="⚔️ PvP Leaderboard",
        description=f"Top PvP fighters (Page {page}/{total_pages})",
        color=0xff0000
    )

    for i, (uid, player) in enumerate(page_players, start=start_idx + 1):
        try:
            user = await bot.fetch_user(int(uid))
            username = user.name
        except:
            username = f"Unknown User ({uid})"

        win_rate = player["pvp_wins"] / max(1, player["pvp_wins"] + player["pvp_losses"]) * 100

        embed.add_field(
            name=f"{i}. {username}",
            value=f"**Wins:** {player['pvp_wins']} | **Losses:** {player['pvp_losses']}\n**Win Rate:** {win_rate:.1f}% | **Power:** {player['total_power']}",
            inline=False
        )

    embed.set_footer(text=f"Total players: {len(sorted_players)} | Use !pvp_rank [page] untuk halaman lain")
    await ctx.send(embed=embed)

# ===============================
# Command: top
# ===============================
@bot.command()
async def top(ctx, count: int = 5):
    """Lihat top cultivators"""
    if count < 1 or count > 20:
        return await ctx.send("❌ Jumlah harus antara 1-20!")

    players = get_all_players()

    if not players:
        return await ctx.send("❌ Belum ada player yang terdaftar!")

    # Sort players by total power
    sorted_players = sorted(
        [(uid, data) for uid, data in players.items()],
        key=lambda x: x[1]["total_power"],
        reverse=True
    )[:count]

    embed = discord.Embed(
        title=f"🏆 Top {count} Cultivators",
        description="Most powerful cultivators in the realm",
        color=0xffd700
    )

    for i, (uid, player) in enumerate(sorted_players, start=1):
        try:
            user = await bot.fetch_user(int(uid))
            username = user.name
        except:
            username = f"Unknown User ({uid})"

        embed.add_field(
            name=f"{i}. {username}",
            value=f"**Power:** {player['total_power']} | **Realm:** {player['realm']}\n**Stage:** {player['stage']} | **Wins:** {player['pvp_wins']}",
            inline=False
        )

    await ctx.send(embed=embed)

# ===============================
# Command: dungeons
# ===============================
@bot.command()
async def dungeons(ctx):
    """Lihat semua dungeon yang tersedia"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    player_level = get_player_level(p)

    embed = discord.Embed(
        title="🏰 Available Dungeons",
        description="Jelajahi dungeon untuk mendapatkan reward!",
        color=0x7289da
    )

    for dungeon_id, dungeon_data in DUNGEONS.items():
        accessible = dungeon_data["min_level"] <= player_level <= dungeon_data["max_level"]
        status_emoji = "✅" if accessible else "❌"

        embed.add_field(
            name=f"{status_emoji} {dungeon_data['emoji']} {dungeon_data['name']}",
            value=f"**Level:** {dungeon_data['min_level']}-{dungeon_data['max_level']}\n"
                  f"**Difficulty:** {dungeon_data['difficulty']}\n"
                  f"**Reward:** {dungeon_data['min_reward']}-{dungeon_data['max_reward']} EXP\n"
                  f"**Spirit Stones:** {dungeon_data['spirit_stone_reward'][0]}-{dungeon_data['spirit_stone_reward'][1]}\n"
                  f"**Description:** {dungeon_data['description']}",
            inline=False
        )

    embed.set_footer(text="Gunakan !enter [dungeon_name] untuk memasuki dungeon")
    await ctx.send(embed=embed)

# ===============================
# Command: enter
# ===============================
@bot.command()
@commands.cooldown(1, 300, commands.BucketType.user)  # 5 minute cooldown
async def enter(ctx, dungeon_name: str):
    """Memasuki dungeon untuk mencari reward"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    player_level = get_player_level(p)

    dungeon_id = dungeon_name.lower()
    if dungeon_id not in DUNGEONS:
        return await ctx.send("❌ Dungeon tidak ditemukan! Gunakan `!dungeons` untuk melihat dungeon yang tersedia.")

    dungeon_data = DUNGEONS[dungeon_id]

    # Check level requirements
    if player_level < dungeon_data["min_level"]:
        return await ctx.send(f"❌ Level Anda ({player_level}) terlalu rendah! Butuh level {dungeon_data['min_level']}+.")

    if player_level > dungeon_data["max_level"]:
        return await ctx.send(f"❌ Level Anda ({player_level}) terlalu tinggi! Maksimal level {dungeon_data['max_level']}.")

    # Calculate success chance based on power
    success_chance = min(90, 50 + (p["total_power"] // 10))
    success = random.randint(1, 100) <= success_chance

    if success:
        # Successful dungeon run
        exp_reward = random.randint(dungeon_data["min_reward"], dungeon_data["max_reward"])
        spirit_stones_reward = random.randint(*dungeon_data["spirit_stone_reward"])
        qi_reward = random.randint(10, 30)

        p["exp"] = min(p["exp"] + exp_reward, get_exp_cap(p))
        p["spirit_stones"] += spirit_stones_reward
        p["qi"] += qi_reward
        p["dungeons_completed"] += 1

        # Update daily quest progress
        p["daily_quests"]["complete_dungeon"]["progress"] += 1
        if p["daily_quests"]["complete_dungeon"]["progress"] >= p["daily_quests"]["complete_dungeon"].get("progress_needed", 2):
            p["daily_quests"]["complete_dungeon"]["completed"] = True

        # Chance to find ingredients
        found_items = {}
        if random.random() < 0.3:
            ingredient = random.choice(list(ALCHEMY_INGREDIENTS.keys()))
            quantity = random.randint(1, 3)
            p["inventory"][ingredient] = p["inventory"].get(ingredient, 0) + quantity
            found_items[ingredient] = quantity

        update_player(ctx.author.id, p)

        # Update server stats
        data = load_data()
        data["server_stats"]["total_dungeons"] += 1
        save_data(data)

        # PERBAIKAN: Embed harus berada di dalam blok if success
        embed = discord.Embed(
            title="🎉 Dungeon Completed!",
            description=f"{ctx.author.mention} berhasil menyelesaikan {dungeon_data['emoji']} {dungeon_data['name']}",
            color=0x00ff00
        )
        embed.add_field(name="EXP Reward", value=f"+{exp_reward}", inline=True)
        embed.add_field(name="Spirit Stones", value=f"+{spirit_stones_reward}", inline=True)
        embed.add_field(name="Qi Reward", value=f"+{qi_reward}", inline=True)
        embed.add_field(name="Total Dungeons", value=p["dungeons_completed"], inline=True)

        if found_items:
            items_text = ""
            for item, quantity in found_items.items():
                item_data = ALCHEMY_INGREDIENTS.get(item, {"name": item.replace("_", " ").title(), "emoji": "📦"})
                items_text += f"{item_data['emoji']} {item_data['name']} x{quantity}\n"
            embed.add_field(name="Items Found", value=items_text, inline=False)

        await ctx.send(embed=embed)

    else:
        # Failed dungeon run
        embed = discord.Embed(
            title="💀 Dungeon Failed!",
            description=f"{ctx.author.mention} gagal menyelesaikan {dungeon_data['emoji']} {dungeon_data['name']}",
            color=0xff0000
        )
        embed.add_field(name="Success Chance", value=f"{success_chance}%", inline=True)
        embed.add_field(name="Result", value="Anda dikalahkan oleh guardian dungeon!", inline=True)
        await ctx.send(embed=embed)

# ===============================
# SPIRIT BEAST SYSTEM - NEW
# ===============================r
SPIRIT_BEASTS = {
    "common": [
        {"name": "Spirit Rabbit", "emoji": "🐇", "power": 5, "cost": 100, "bonus": {"exp": 0.05}},
        {"name": "Moon Fox", "emoji": "🦊", "power": 10, "cost": 250, "bonus": {"qi": 0.07}},
        {"name": "Wind Hawk", "emoji": "🦅", "power": 15, "cost": 500, "bonus": {"movement": 0.10}}
    ],
    "rare": [
        {"name": "Thunder Tiger", "emoji": "🐅", "power": 25, "cost": 1000, "bonus": {"attack": 0.08}},
        {"name": "Earth Bear", "emoji": "🐻", "power": 30, "cost": 1500, "bonus": {"defense": 0.10}},
        {"name": "Water Serpent", "emoji": "🐍", "power": 35, "cost": 2000, "bonus": {"healing": 0.09}}
    ],
    "epic": [
        {"name": "Phoenix", "emoji": "🔥", "power": 50, "cost": 5000, "bonus": {"all": 0.05}},
        {"name": "Azure Dragon", "emoji": "🐉", "power": 60, "cost": 7500, "bonus": {"attack": 0.12}},
        {"name": "White Tiger", "emoji": "🐯", "power": 70, "cost": 10000, "bonus": {"defense": 0.15}}
    ],
    "legendary": [
        {"name": "Golden Qilin", "emoji": "🦄", "power": 100, "cost": 20000, "bonus": {"all": 0.10}},
        {"name": "Vermilion Bird", "emoji": "🐦", "power": 120, "cost": 30000, "bonus": {"exp": 0.15, "qi": 0.15}},
        {"name": "Black Tortoise", "emoji": "🐢", "power": 150, "cost": 50000, "bonus": {"defense": 0.20, "healing": 0.10}}
    ]
}

def apply_beast_bonuses(player_data, base_gain, qi_gain, power_gain):
    """Terapkan bonus dari spirit beasts"""
    total_exp_bonus = 1.0
    total_qi_bonus = 1.0
    total_power_bonus = 1.0
    
    for beast in player_data.get("spirit_beasts", []):
        for bonus_type, bonus_value in beast["bonus"].items():
            if bonus_type == "exp":
                total_exp_bonus += bonus_value
            elif bonus_type == "qi":
                total_qi_bonus += bonus_value
            elif bonus_type == "power":
                total_power_bonus += bonus_value
            elif bonus_type == "all":
                total_exp_bonus += bonus_value
                total_qi_bonus += bonus_value
                total_power_bonus += bonus_value
    
    return (
        int(base_gain * total_exp_bonus),
        int(qi_gain * total_qi_bonus),
        int(power_gain * total_power_bonus)
    )


# ===============================
# Command: spirit_beasts (BARU - TAMBAHKAN DI SINI)
# ===============================
@bot.command()
async def spirit_beasts(ctx):
    """Lihat spirit beasts yang tersedia untuk dijinakkan"""
    embed = discord.Embed(
        title="🐉 Spirit Beast Sanctuary",
        description="Jinakkan spirit beasts untuk mendapatkan bonus permanen!",
        color=0x00ff00
    )

    for rarity, beasts in SPIRIT_BEASTS.items():
        rarity_text = f"**{rarity.title()} Beasts**\n"
        for beast in beasts:
            bonus_text = ", ".join([f"+{int(v*100)}% {k}" for k, v in beast["bonus"].items()])
            rarity_text += f"{beast['emoji']} **{beast['name']}** - {beast['cost']} Spirit Stones\n"
            rarity_text += f"   Power: +{beast['power']} | Bonus: {bonus_text}\n\n"
        
        embed.add_field(name=f"🌟 {rarity.title()} Tier", value=rarity_text, inline=False)

    embed.set_footer(text="Gunakan !tame [beast_name] untuk menjinakkan spirit beast")
    await ctx.send(embed=embed)

# ===============================
# Command: tame (BARU - TAMBAHKAN DI SINI)
# ===============================
@bot.command()
async def tame(ctx, beast_name: str):
    """Jinakkan spirit beast dengan Spirit Stones"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    # Cari beast berdasarkan nama
    found_beast = None
    beast_rarity = None
    
    for rarity, beasts in SPIRIT_BEASTS.items():
        for beast in beasts:
            if beast["name"].lower() == beast_name.lower():
                found_beast = beast
                beast_rarity = rarity
                break
        if found_beast:
            break

    if not found_beast:
        return await ctx.send("❌ Spirit beast tidak ditemukan! Gunakan `!spirit_beasts` untuk melihat yang tersedia.")

    # Cek apakah sudah memiliki beast ini
    if any(beast["name"].lower() == beast_name.lower() for beast in p.get("spirit_beasts", [])):
        return await ctx.send("❌ Anda sudah memiliki spirit beast ini!")

    # Cek Spirit Stones
    if p["spirit_stones"] < found_beast["cost"]:
        return await ctx.send(f"❌ Tidak cukup Spirit Stones! Butuh {found_beast['cost']}, Anda memiliki {p['spirit_stones']}.")

    # Jinakkan beast
    p["spirit_stones"] -= found_beast["cost"]
    
    if "spirit_beasts" not in p:
        p["spirit_beasts"] = []
    
    p["spirit_beasts"].append(found_beast)
    
    # Update server stats
    data = load_data()
    data["server_stats"]["total_spirit_beasts"] = data["server_stats"].get("total_spirit_beasts", 0) + 1
    save_data(data)

    update_player(ctx.author.id, p)

    bonus_text = ", ".join([f"+{int(v*100)}% {k}" for k, v in found_beast["bonus"].items()])
    
    embed = discord.Embed(
        title="🎉 Spirit Beast Tamed!",
        description=f"{ctx.author.mention} berhasil menjinakkan {found_beast['emoji']} {found_beast['name']}!",
        color=0x00ff00
    )
    embed.add_field(name="Cost", value=f"{found_beast['cost']} Spirit Stones", inline=True)
    embed.add_field(name="Power Bonus", value=f"+{found_beast['power']}", inline=True)
    embed.add_field(name="Special Bonuses", value=bonus_text, inline=True)
    embed.add_field(name="Rarity", value=beast_rarity.title(), inline=True)
    embed.add_field(name="Total Spirit Beasts", value=len(p["spirit_beasts"]), inline=True)
    embed.add_field(name="Remaining Stones", value=p["spirit_stones"], inline=True)

    embed.set_footer(text="Gunakan !set_beast untuk mengaktifkan spirit beast ini")
    await ctx.send(embed=embed)


# ===============================
# Command: set_beast
# ===============================
@bot.command()
async def set_beast(ctx, beast_name: str = None):
    """Set spirit beast aktif atau lihat beast yang dimiliki"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    if not beast_name:
        # Show current beast and list of owned beasts
        if not p.get("spirit_beasts"):
            return await ctx.send("❌ Anda belum menjinakkan spirit beast apapun!")

        embed = discord.Embed(
            title=f"🐉 {ctx.author.name}'s Spirit Beasts",
            description="Spirit beasts yang telah dijinakkan:",
            color=0x00ff00
        )

        for i, beast in enumerate(p["spirit_beasts"]):
            status = "✅" if p.get("current_beast") == beast["name"] else "❌"
            bonus_text = ", ".join([f"+{int(v*100)}% {k}" for k, v in beast["bonus"].items()])
            
            embed.add_field(
                name=f"{status} {beast['emoji']} {beast['name']}",
                value=f"**Power:** +{beast['power']} | **Bonus:** {bonus_text}",
                inline=False
            )

        embed.set_footer(text="Gunakan !set_beast \"nama_beast\" untuk mengaktifkan beast")
        await ctx.send(embed=embed)
        return  # PERBAIKAN: Pastikan return di sini

    # Set active beast
    found_beast = None
    for beast in p.get("spirit_beasts", []):
        if beast["name"].lower() == beast_name.lower():
            found_beast = beast
            break

    if not found_beast:
        return await ctx.send("❌ Spirit beast tidak ditemukan! Pastikan Anda sudah menjinakkannya.")

    p["current_beast"] = found_beast["name"]
    update_player(ctx.author.id, p)

    bonus_text = ", ".join([f"+{int(v*100)}% {k}" for k, v in found_beast["bonus"].items()])
    
    embed = discord.Embed(
        title="🎯 Active Spirit Beast Set!",
        description=f"{ctx.author.mention} mengaktifkan {found_beast['emoji']} {found_beast['name']}",
        color=0x00ff00
    )
    embed.add_field(name="Power Bonus", value=f"+{found_beast['power']}", inline=True)
    embed.add_field(name="Special Bonuses", value=bonus_text, inline=True)
    embed.add_field(name="Note", value="Bonus akan diterapkan secara otomatis dalam cultivation dan battle", inline=False)

    await ctx.send(embed=embed)


# ===============================
# ALCHEMY SYSTEM - NEW
# ===============================
@bot.command()
async def alchemy(ctx):
    """Lihat resep alchemy yang tersedia"""
    embed = discord.Embed(
        title="🧪 Alchemy Laboratory",
        description="Craft pills untuk meningkatkan cultivation!",
        color=0x800080
    )

    for pill_id, pill_data in PILL_RECIPES.items():
        ingredients_text = ""
        for ingredient, quantity in pill_data["ingredients"].items():
            ing_data = ALCHEMY_INGREDIENTS.get(ingredient, {"name": ingredient.replace("_", " ").title(), "emoji": "📦"})
            ingredients_text += f"{ing_data['emoji']} {ing_data['name']} x{quantity}\n"

        effects_text = ", ".join([f"+{amount} {effect}" for effect, amount in pill_data["effect"].items()])

        embed.add_field(
            name=f"{pill_data['emoji']} {pill_data['name']}",
            value=f"**Effects:** {effects_text}\n"
                  f"**Ingredients:**\n{ingredients_text}"
                  f"**Description:** {pill_data['description']}",
            inline=False
        )

    embed.set_footer(text="Gunakan !craft [pill_name] untuk membuat pill")
    await ctx.send(embed=embed)

@bot.command()
async def craft(ctx, pill_name: str):
    """Craft alchemy pill"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    # Find pill recipe
    found_pill = None
    for pill_id, pill_data in PILL_RECIPES.items():
        if pill_data["name"].lower() == pill_name.lower():
            found_pill = pill_data
            break

    if not found_pill:
        return await ctx.send("❌ Resep pill tidak ditemukan! Gunakan `!alchemy` untuk melihat resep.")

    # Check ingredients
    missing_ingredients = []
    for ingredient, quantity in found_pill["ingredients"].items():
        if p["inventory"].get(ingredient, 0) < quantity:
            missing_ingredients.append(f"{ingredient} x{quantity}")

    if missing_ingredients:
        return await ctx.send(f"❌ Bahan tidak cukup! Kurang: {', '.join(missing_ingredients)}")

    # Craft pill
    for ingredient, quantity in found_pill["ingredients"].items():
        p["inventory"][ingredient] -= quantity

    # Apply pill effects
    results = []
    for effect, amount in found_pill["effect"].items():
        if effect == "exp":
            p["exp"] = min(p["exp"] + amount, get_exp_cap(p))
            results.append(f"+{amount} EXP")
        elif effect == "qi":
            p["qi"] += amount
            results.append(f"+{amount} Qi")
        elif effect == "power":
            p["base_power"] += amount
            results.append(f"+{amount} Base Power")
        elif effect == "breakthrough_chance":
            results.append(f"+{int(amount*100)}% breakthrough chance")

    p["pills_crafted"] += 1

    # Update daily quest progress for find_treasure
    p["daily_quests"]["find_treasure"]["progress"] += 1
    if p["daily_quests"]["find_treasure"]["progress"] >= p["daily_quests"]["find_treasure"].get("progress_needed", 3):
        p["daily_quests"]["find_treasure"]["completed"] = True

    # Recalculate total power
    technique_bonus = 1 + sum(t['power_bonus'] for t in p["techniques"])
    set_bonus = calculate_set_bonus(p["equipment"])
    p["total_power"] = int((p["base_power"] + sum(p["equipment"].values())) * technique_bonus * (1 + set_bonus))

    update_player(ctx.author.id, p)

    # Update server stats
    data = load_data()
    data["server_stats"]["total_pills_crafted"] = data["server_stats"].get("total_pills_crafted", 0) + 1
    save_data(data)

    embed = discord.Embed(
        title="🎉 Pill Crafting Successful!",
        description=f"{ctx.author.mention} berhasil membuat {found_pill['emoji']} {found_pill['name']}",
        color=0x800080
    )
    embed.add_field(name="Effects", value="\n".join(results), inline=False)
    embed.add_field(name="Total Pills Crafted", value=p["pills_crafted"], inline=True)

    await ctx.send(embed=embed)

# ===============================
# ACHIEVEMENT SYSTEM - DIPERBAIKI
# ===============================
@bot.command()
async def achievements(ctx):
    """Lihat achievements yang tersedia"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    embed = discord.Embed(
        title="🏆 Achievement System",
        description="Selesaikan achievement untuk mendapatkan reward!",
        color=0xffd700
    )

    completed = 0
    for achievement_id, achievement_data in ACHIEVEMENTS.items():
        completed_status = achievement_id in p.get("achievements", [])
        status_emoji = "✅" if completed_status else "⚪"

        if completed_status:
            completed += 1

        reward_text = ", ".join([f"{amount} {resource}" for resource, amount in achievement_data["reward"].items()])

        embed.add_field(
            name=f"{status_emoji} {achievement_data['emoji']} {achievement_data['name']}",
            value=f"{achievement_data['description']}\n**Reward:** {reward_text}",
            inline=False
        )

    embed.set_footer(text=f"Total completed: {completed}/{len(ACHIEVEMENTS)}")
    await ctx.send(embed=embed)

ACHIEVEMENTS = {
    # ... achievement lainnya yang sudah ada,
    
    "dragon_slayer": {
        "name": "Dragon Slayer",
        "description": "Kalahkan Ancient Dragon",
        "reward": {"spirit_stones": 500, "power": 30},
        "emoji": "🐉",
        "condition": lambda p: "Ancient Dragon" in p.get("bosses_defeated", [])
    },
    "phoenix_hunter": {
        "name": "Phoenix Hunter", 
        "description": "Kalahkan Celestial Phoenix",
        "reward": {"spirit_stones": 800, "qi": 200},
        "emoji": "🔥",
        "condition": lambda p: "Celestial Phoenix" in p.get("bosses_defeated", [])
    },
    "kraken_killer": {
        "name": "Kraken Killer",
        "description": "Kalahkan Abyssal Kraken", 
        "reward": {"spirit_stones": 1200, "exp": 500},
        "emoji": "🐙",
        "condition": lambda p: "Abyssal Kraken" in p.get("bosses_defeated", [])
    },
    "boss_master": {
        "name": "Boss Master",
        "description": "Kalahkan semua boss",
        "reward": {"spirit_stones": 2000, "exp": 1000, "qi": 500},
        "emoji": "🏆",
        "condition": lambda p: len(p.get("bosses_defeated", [])) >= 3
    }
}

# ===============================
# GUILD SYSTEM - DITAMBAHKAN
# ===============================
@bot.command()
async def create_guild(ctx, guild_name: str):
    """Buat guild baru"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    if p["guild"]:
        return await ctx.send("❌ Anda sudah berada dalam guild! Keluar dulu untuk membuat guild baru.")

    if p["spirit_stones"] < GUILD_COSTS["create"]:
        return await ctx.send(f"❌ Tidak cukup Spirit Stones! Butuh {GUILD_COSTS['create']}, Anda memiliki {p['spirit_stones']}.")

    data = load_data()

    # Check if guild name already exists
    if guild_name in data["guilds"]:
        return await ctx.send("❌ Nama guild sudah digunakan!")

    # Create guild
    p["spirit_stones"] -= GUILD_COSTS["create"]
    p["guild"] = guild_name
    p["guild_role"] = "Leader"

    data["guilds"][guild_name] = {
        "name": guild_name,
        "leader": ctx.author.id,
        "members": [ctx.author.id],
        "level": 1,
        "treasury": 0,
        "created_at": datetime.datetime.now().isoformat(),
        "description": f"Guild yang dipimpin oleh {ctx.author.name}"
    }

    update_player(ctx.author.id, p)
    save_data(data)

    embed = discord.Embed(
        title="🏰 Guild Created!",
        description=f"{ctx.author.mention} telah membuat guild **{guild_name}**!",
        color=0x00ff00
    )
    embed.add_field(name="Cost", value=f"{GUILD_COSTS['create']} Spirit Stones", inline=True)
    embed.add_field(name="Role", value="Leader", inline=True)
    embed.add_field(name="Members", value="1", inline=True)
    embed.add_field(name="Guild Benefits", value="+15% EXP, +10% Qi, +20% Spirit Stones, -25% Technique costs", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def join_guild(ctx, guild_name: str):
    """Bergabung dengan guild yang ada"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    if p["guild"]:
        return await ctx.send("❌ Anda sudah berada dalam guild! Keluar dulu untuk bergabung dengan guild lain.")

    if p["spirit_stones"] < GUILD_COSTS["join"]:
        return await ctx.send(f"❌ Tidak cukup Spirit Stones! Butuh {GUILD_COSTS['join']}, Anda memiliki {p['spirit_stones']}.")

    data = load_data()

    if guild_name not in data["guilds"]:
        return await ctx.send("❌ Guild tidak ditemukan!")

    guild = data["guilds"][guild_name]

    if ctx.author.id in guild["members"]:
        return await ctx.send("❌ Anda sudah menjadi member guild ini!")

    # Join guild
    p["spirit_stones"] -= GUILD_COSTS["join"]
    p["guild"] = guild_name
    p["guild_role"] = "Member"

    guild["members"].append(ctx.author.id)

    update_player(ctx.author.id, p)
    save_data(data)

    embed = discord.Embed(
        title="🏰 Joined Guild!",
        description=f"{ctx.author.mention} telah bergabung dengan guild **{guild_name}**!",
        color=0x00ff00
    )
    embed.add_field(name="Cost", value=f"{GUILD_COSTS['join']} Spirit Stones", inline=True)
    embed.add_field(name="Role", value="Member", inline=True)
    embed.add_field(name="Total Members", value=f"{len(guild['members'])}", inline=True)
    embed.add_field(name="Leader", value=f"<@{guild['leader']}>", inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def leave_guild(ctx):
    """Keluar dari guild"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    if not p["guild"]:
        return await ctx.send("❌ Anda tidak berada dalam guild manapun!")

    data = load_data()
    guild_name = p["guild"]

    if guild_name not in data["guilds"]:
        p["guild"] = None
        p["guild_role"] = None
        update_player(ctx.author.id, p)
        return await ctx.send("❌ Guild tidak ditemukan! Anda telah dikeluarkan.")

    guild = data["guilds"][guild_name]

    if ctx.author.id == guild["leader"]:
        return await ctx.send("❌ Leader tidak bisa keluar guild! Transfer kepemimpinan dulu atau bubarkan guild.")

    # Leave guild
    guild["members"].remove(ctx.author.id)
    p["guild"] = None
    p["guild_role"] = None

    update_player(ctx.author.id, p)
    save_data(data)

    await ctx.send(f"🏰 Anda telah keluar dari guild **{guild_name}**!")

@bot.command()
async def guild_info(ctx, guild_name: str = None):
    """Lihat info guild"""
    data = load_data()

    if not guild_name:
        p = get_player(ctx.author.id)
        if not p or not p["guild"]:
            return await ctx.send("❌ Anda tidak berada dalam guild! Gunakan `!guild_info [nama_guild]`")
        guild_name = p["guild"]

    if guild_name not in data["guilds"]:
        return await ctx.send("❌ Guild tidak ditemukan!")

    guild = data["guilds"][guild_name]

    embed = discord.Embed(
        title=f"🏰 Guild {guild_name}",
        description=guild.get("description", "No description"),
        color=0x7289da
    )

    try:
        leader = await bot.fetch_user(guild["leader"])
        leader_name = leader.name
    except:
        leader_name = f"Unknown User ({guild['leader']})"

    embed.add_field(name="Leader", value=leader_name, inline=True)
    embed.add_field(name="Level", value=guild["level"], inline=True)
    embed.add_field(name="Members", value=f"{len(guild['members'])}", inline=True)
    embed.add_field(name="Treasury", value=f"{guild['treasury']} Spirit Stones", inline=True)
    embed.add_field(name="Created", value=datetime.datetime.fromisoformat(guild["created_at"]).strftime("%Y-%m-%d"), inline=True)

    # Show member list (first 10)
    members_text = ""
    for i, member_id in enumerate(guild["members"][:10]):
        try:
            member = await bot.fetch_user(member_id)
            role = "👑" if member_id == guild["leader"] else "👤"
            members_text += f"{role} {member.name}\n"
        except:
            members_text += f"👤 Unknown User ({member_id})\n"

    if len(guild["members"]) > 10:
        members_text += f"... and {len(guild['members']) - 10} more members"

    embed.add_field(name="Members", value=members_text or "No members", inline=False)
    embed.add_field(name="Guild Benefits", value="+15% EXP, +10% Qi, +20% Spirit Stones, -25% Technique costs", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def guilds(ctx):
    """Lihat semua guild yang tersedia"""
    data = load_data()

    if not data["guilds"]:
        return await ctx.send("❌ Belum ada guild yang terdaftar!")

    embed = discord.Embed(
        title="🏰 Available Guilds",
        description="Daftar guild yang dapat Anda ikuti:",
        color=0x7289da
    )

    for guild_name, guild_data in data["guilds"].items():
        try:
            leader = await bot.fetch_user(guild_data["leader"])
            leader_name = leader.name
        except:
            leader_name = f"Unknown User ({guild_data['leader']})"

        embed.add_field(
            name=f"{guild_name} (Level {guild_data['level']})",
            value=f"**Leader:** {leader_name}\n**Members:** {len(guild_data['members'])}\n**Treasury:** {guild_data['treasury']} Spirit Stones",
            inline=False
        )

    embed.set_footer(text="Gunakan !join_guild [nama_guild] untuk bergabung")
    await ctx.send(embed=embed)

@bot.command()
async def guild_donate(ctx, amount: int):
    """Donasikan Spirit Stones ke guild treasury"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    if not p["guild"]:
        return await ctx.send("❌ Anda tidak berada dalam guild!")

    if amount <= 0:
        return await ctx.send("❌ Jumlah donasi harus positif!")

    if p["spirit_stones"] < amount:
        return await ctx.send(f"❌ Tidak cukup Spirit Stones! Anda memiliki {p['spirit_stones']}.")

    data = load_data()
    guild_name = p["guild"]

    if guild_name not in data["guilds"]:
        return await ctx.send("❌ Guild tidak ditemukan!")

    guild = data["guilds"][guild_name]

    # Donate to guild
    p["spirit_stones"] -= amount
    p["guild_contributions"] += amount
    guild["treasury"] += amount

    update_player(ctx.author.id, p)
    save_data(data)

    embed = discord.Embed(
        title="💰 Guild Donation!",
        description=f"{ctx.author.mention} mendonasikan {amount} Spirit Stones ke guild **{guild_name}**!",
        color=0x00ff00
    )
    embed.add_field(name="Amount", value=f"{amount} Spirit Stones", inline=True)
    embed.add_field(name="New Treasury", value=f"{guild['treasury']} Spirit Stones", inline=True)
    embed.add_field(name="Your Contributions", value=f"{p['guild_contributions']} Spirit Stones", inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def guild_benefits(ctx):
    """Lihat benefits guild"""
    embed = discord.Embed(
        title="🏰 Guild Benefits",
        description="Keuntungan bergabung dengan guild:",
        color=0x00ff00
    )

    benefits_text = ""
    for benefit, value in GUILD_BENEFITS.items():
        benefit_name = benefit.replace("_", " ").title()
        benefits_text += f"• **{benefit_name}**: +{int(value*100)}%\n"

    embed.add_field(name="Benefits", value=benefits_text, inline=False)
    embed.add_field(name="Costs", value=f"**Buat Guild**: {GUILD_COSTS['create']} Spirit Stones\n**Join Guild**: {GUILD_COSTS['join']} Spirit Stones", inline=False)
    embed.add_field(name="Note", value="Benefits berlaku untuk semua member guild secara otomatis", inline=False)

    await ctx.send(embed=embed)

# ===============================
# DAILY QUEST SYSTEM - DITAMBAHKAN
# ===============================
@bot.command()
async def daily_quests(ctx):
    """Lihat daily quests yang tersedia"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    # Reset daily quests jika perlu
    reset_daily_quests()

    embed = discord.Embed(
        title="📋 Daily Quests",
        description="Selesaikan quest harian untuk mendapatkan reward!",
        color=0xffd700
    )

    completed_count = 0
    for quest in DAILY_QUESTS:
        quest_data = p["daily_quests"][quest["id"]]
        status_emoji = "✅" if quest_data["claimed"] else "🟢" if quest_data["completed"] else "⚪"

        if quest_data["claimed"]:
            completed_count += 1

        progress = f"{quest_data['progress']}/{quest.get('progress_needed', 1)}"
        reward_text = ", ".join([f"{amount} {resource}" for resource, amount in quest["reward"].items()])

        embed.add_field(
            name=f"{status_emoji} {quest['name']}",
            value=f"**Progress:** {progress}\n**Reward:** {reward_text}",
            inline=False
        )

    embed.set_footer(text=f"Completed: {completed_count}/{len(DAILY_QUESTS)} | Reset setiap hari")
    await ctx.send(embed=embed)

@bot.command()
async def claim_daily(ctx):
    """Klaim reward daily quest yang sudah completed"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    # Reset daily quests jika perlu
    reset_daily_quests()

    claimed_quests = []
    total_rewards = {"exp": 0, "qi": 0, "spirit_stones": 0, "power": 0}

    for quest in DAILY_QUESTS:
        quest_data = p["daily_quests"][quest["id"]]

        if quest_data["completed"] and not quest_data["claimed"]:
            # Give rewards
            for reward_type, amount in quest["reward"].items():
                if reward_type == "exp":
                    p["exp"] = min(p["exp"] + amount, get_exp_cap(p))
                    total_rewards["exp"] += amount
                elif reward_type == "qi":
                    p["qi"] += amount
                    total_rewards["qi"] += amount
                elif reward_type == "spirit_stones":
                    p["spirit_stones"] += amount
                    total_rewards["spirit_stones"] += amount
                elif reward_type == "power":
                    p["base_power"] += amount
                    total_rewards["power"] += amount

            quest_data["claimed"] = True
            claimed_quests.append(quest["name"])

    if not claimed_quests:
        return await ctx.send("❌ Tidak ada quest yang bisa di-claim! Selesaikan quest harian terlebih dahulu.")

    # Update login streak
    now = time.time()
    last_claim = float(p.get("last_daily_claim", "0"))

    if now - last_claim > 172800:  # 2 days in seconds
        p["login_streak"] = 1
    else:
        p["login_streak"] += 1

    p["last_daily_claim"] = str(now)

    # Add streak bonus
    streak_bonus = min(0.5, p["login_streak"] * 0.05)  # Max 50% bonus
    if streak_bonus > 0:
        for reward_type in total_rewards:
            if total_rewards[reward_type] > 0:
                bonus_amount = int(total_rewards[reward_type] * streak_bonus)
                total_rewards[reward_type] += bonus_amount

                if reward_type == "exp":
                    p["exp"] = min(p["exp"] + bonus_amount, get_exp_cap(p))
                elif reward_type == "qi":
                    p["qi"] += bonus_amount
                elif reward_type == "spirit_stones":
                    p["spirit_stones"] += bonus_amount
                elif reward_type == "power":
                    p["base_power"] += bonus_amount

    update_player(ctx.author.id, p)

    # Recalculate total power
    technique_bonus = 1 + sum(t['power_bonus'] for t in p["techniques"])
    set_bonus = calculate_set_bonus(p["equipment"])
    p["total_power"] = int((p["base_power"] + sum(p["equipment"].values())) * technique_bonus * (1 + set_bonus))

    embed = discord.Embed(
        title="🎉 Daily Rewards Claimed!",
        description=f"{ctx.author.mention} mengklaim reward quest harian:",
        color=0x00ff00
    )

    rewards_text = ""
    for reward_type, amount in total_rewards.items():
        if amount > 0:
            rewards_text += f"**{reward_type.title()}**: +{amount}\n"

    embed.add_field(name="Quests Completed", value="\n".join(claimed_quests), inline=False)
    embed.add_field(name="Rewards", value=rewards_text, inline=False)
    embed.add_field(name="Login Streak", value=f"{p['login_streak']} days (+{int(streak_bonus*100)}% bonus)", inline=True)
    embed.add_field(name="Total Power", value=p["total_power"], inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def daily_streak(ctx):
    """Lihat login streak Anda"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    streak = p.get("login_streak", 0)
    bonus = min(50, streak * 5)  # 5% per day, max 50%

    embed = discord.Embed(
        title="📅 Login Streak",
        description=f"{ctx.author.name}'s daily login streak",
        color=0xffd700
    )
    embed.add_field(name="Current Streak", value=f"{streak} days", inline=True)
    embed.add_field(name="Bonus Reward", value=f"+{bonus}%", inline=True)
    embed.add_field(name="Next Bonus", value=f"+{min(50, (streak + 1) * 5)}% at {streak + 1} days", inline=True)

    if streak > 0:
        last_claim = datetime.datetime.fromtimestamp(float(p.get("last_daily_claim", "0")))
        next_claim = last_claim + datetime.timedelta(days=1)
        embed.add_field(name="Last Claim", value=last_claim.strftime("%Y-%m-%d %H:%M"), inline=True)
        embed.add_field(name="Next Claim Available", value=next_claim.strftime("%Y-%m-%d %H:%M"), inline=True)

    embed.set_footer(text="Klaim quest harian setiap hari untuk mempertahankan streak!")
    await ctx.send(embed=embed)

# ===============================
# Command: reroll - GANTI RACE (UNTUK COST)
# ===============================
@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)  # 1 day cooldown
async def reroll(ctx):
    """Ganti race Anda (biaya 1000 Spirit Stones)"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    if p["spirit_stones"] < 1000:
        return await ctx.send(f"❌ Butuh 1000 Spirit Stones! Anda memiliki {p['spirit_stones']}.")

    # Tampilkan pilihan race
    embed = discord.Embed(
        title="🔄 Race Reroll",
        description="Pilih race baru (biaya 1000 Spirit Stones):",
        color=0xffd700
    )

    for race_id, race_data in RACES.items():
        if not race_data.get("hidden", False):
            embed.add_field(
                name=f"{race_data['emoji']} {race_data['name']}",
                value=f"{race_data['description']}",
                inline=False
            )

    embed.set_footer(text="Balas dengan nama race yang dipilih atau 'cancel' untuk membatalkan")
    await ctx.send(embed=embed)

    def check_race(m):
        return m.author == ctx.author and (m.content.lower() in RACES.keys() or m.content.lower() == 'cancel')

    try:
        race_msg = await bot.wait_for('message', timeout=60.0, check=check_race)
        if race_msg.content.lower() == 'cancel':
            return await ctx.send("❌ Reroll dibatalkan.")

        new_race = race_msg.content.lower()
        old_race = p.get("race", "human")

        # Bayar cost
        p["spirit_stones"] -= 1000
        p["race"] = new_race

        # Recalculate stats dengan bonus baru
        race_data = RACES[new_race]
        old_race_data = RACES[old_race]

        # Remove old bonuses
        if "power" in old_race_data["bonuses"]:
            p["base_power"] = int(p["base_power"] / (1 + old_race_data["bonuses"]["power"]))
        if "qi" in old_race_data["bonuses"]:
            p["qi"] = int(p["qi"] / (1 + old_race_data["bonuses"]["qi"]))

        # Apply new bonuses
        if "power" in race_data["bonuses"]:
            p["base_power"] = int(p["base_power"] * (1 + race_data["bonuses"]["power"]))
        if "qi" in race_data["bonuses"]:
            p["qi"] = int(p["qi"] * (1 + race_data["bonuses"]["qi"]))

        # Recalculate total power
        technique_bonus = 1 + sum(t['power_bonus'] for t in p["techniques"])
        set_bonus = calculate_set_bonus(p["equipment"])
        p["total_power"] = int(p["base_power"] * technique_bonus * (1 + set_bonus))

        update_player(ctx.author.id, p)

        embed = discord.Embed(
            title="🔄 Race Changed!",
            description=f"{ctx.author.mention} telah mengganti race!",
            color=0x00ff00
        )
        embed.add_field(name="New Race", value=f"{race_data['emoji']} {race_data['name']}", inline=True)
        embed.add_field(name="Cost", value="1000 Spirit Stones", inline=True)
        embed.add_field(name="Remaining Stones", value=p["spirit_stones"], inline=True)
        embed.add_field(name="New Bonuses", value="\n".join([f"+{int(v*100)}% {k}" for k, v in race_data["bonuses"].items()]), inline=False)

        await ctx.send(embed=embed)

    except asyncio.TimeoutError:
        await ctx.send("⏰ Waktu habis! Reroll dibatalkan.")

# ===============================
# Command: stats
# ===============================
@bot.command()
async def stats(ctx):
    """Lihat statistik server"""
    data = load_data()
    server_stats = data["server_stats"]

    embed = discord.Embed(
        title="📊 Server Statistics",
        description="Statistik global cultivation server",
        color=0x7289da
    )

    embed.add_field(name="Total Players", value=data["total_players"], inline=True)
    embed.add_field(name="Total PvP Battles", value=server_stats["total_pvp_battles"], inline=True)
    embed.add_field(name="Total Breakthroughs", value=server_stats["total_breakthroughs"], inline=True)
    embed.add_field(name="Total Dungeons", value=server_stats["total_dungeons"], inline=True)
    embed.add_field(name="Total Techniques Learned", value=server_stats["total_techniques_learned"], inline=True)
    embed.add_field(name="Total Spirit Beasts", value=server_stats.get("total_spirit_beasts", 0), inline=True)
    embed.add_field(name="Total Pills Crafted", value=server_stats.get("total_pills_crafted", 0), inline=True)
    embed.add_field(name="Total Guilds", value=len(data["guilds"]), inline=True)
    embed.add_field(name="Last Update", value=server_stats["last_update"][:10], inline=True)

    await ctx.send(embed=embed)

# ===============================
# ADMIN COMMANDS - DITAMBAHKAN
# ===============================
@bot.command()
@commands.is_owner()
async def backup(ctx):
    """Buat backup manual data (Owner only)"""
    if backup_data():
        await ctx.send("✅ Backup berhasil dibuat!")
    else:
        await ctx.send("❌ Gagal membuat backup!")

@bot.command()
@commands.is_owner()
async def add_currency(ctx, member: discord.Member, currency_type: str, amount: int):
    """Tambahkan currency ke player (Owner only)"""
    if currency_type not in ["spirit_stones", "qi", "exp"]:
        return await ctx.send("❌ Tipe currency tidak valid! Gunakan: spirit_stones, qi, exp")

    p = get_player(member.id)
    if not p:
        return await ctx.send("❌ Player tidak ditemukan!")

    if currency_type == "exp":
        p["exp"] = min(p["exp"] + amount, get_exp_cap(p))
    else:
        p[currency_type] += amount

    update_player(member.id, p)

    await ctx.send(f"✅ Menambahkan {amount} {currency_type} ke {member.mention}")

@bot.command()
@commands.is_owner()
async def reset_cooldown(ctx, member: discord.Member):
    """Reset cooldown player (Owner only)"""
    p = get_player(member.id)
    if not p:
        return await ctx.send("❌ Player tidak ditemukan!")

    # Reset various cooldowns
    p["last_technique_find"] = "0"
    p["last_pvp"] = "0"
    p["last_dungeon"] = "0"

    update_player(member.id, p)

    await ctx.send(f"✅ Cooldown {member.mention} telah direset!")

# ===============================
# Command: help (COMPREHENSIVE) - UPDATED dengan fitur baru
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
            description="A comprehensive cultivation RPG bot dengan idle mechanics, real-time battles, dan progression systems!",
            color=0x7289da
        )

        embed.add_field(
            name="📚 Command Categories",
            value="Gunakan `!help <category>` untuk command detail:\n\n"
                  "🎮 **registration** - Registrasi dan character creation\n"
                  "🧘 **cultivation** - Core cultivation & progression\n"
                  "🏛️ **races** - Race system dan bonuses\n"
                  "⚔️ **combat** - PvP battles dan dungeons\n"
                  "🛒 **economy** - Shop, equipment, dan trading\n"
                  "🐉 **beasts** - Spirit beast system\n"
                  "🧪 **alchemy** - Pill crafting system\n"
                  "🏆 **achievements** - Achievement system\n"
                  "🏰 **guild** - Guild system dan teamwork\n"
                  "📋 **daily** - Daily quests dan events\n"
                  "📊 **info** - Stats, progress, dan information\n"
                  "🏆 **ranking** - Leaderboards dan competition\n"
                  "🔧 **system** - Bot utilities dan admin\n",
            inline=False
        )

        embed.add_field(
            name="🚀 Quick Start",
            value="`!register` - Registrasi character baru\n"
                  "`!tutorial` - Panduan lengkap pemula\n"
                  "`!raceinfo` - Info tentang race yang tersedia\n"
                  "`!status` - Lihat status cultivation",
            inline=False
        )

        embed.set_footer(text="🌟 Start your journey to immortality today! Use !help <category> untuk specific commands.")

    elif category.lower() == "registration":
        embed = discord.Embed(
            title="🎮 Registration Commands",
            description="Buat character dan mulai perjalanan cultivation!",
            color=0x00ff00
        )

        embed.add_field(
            name="Character Creation",
            value="`!register` - Registrasi character baru\n"
                  "`!reroll` - Ganti race (1000 Spirit Stones)\n"
                  "`!profile` - Lihat profil character",
            inline=False
        )

        embed.add_field(
            name="Available Races",
            value="• **Human**: Balanced growth\n"
                  "• **Demon**: High power, low defense\n"
                  "• **Half-Demon**: Balanced hybrid\n"
                  "• **Beast Race**: High defense\n"
                  "• **Celestial**: Hidden race (Qi specialist)",
            inline=False
        )

        embed.set_footer(text="🎯 Pilih race sesuai style bermain Anda!")

    elif category.lower() == "races":
        embed = discord.Embed(
            title="🏛️ Race System",
            description="Setiap race memiliki bonus dan keunikan berbeda!",
            color=0x7289da
        )

        for race_id, race_data in RACES.items():
            if not race_data.get("hidden", False):
                bonuses_text = ", ".join([f"+{int(v*100)}% {k}" for k, v in race_data["bonuses"].items()])
                embed.add_field(
                    name=f"{race_data['emoji']} {race_data['name']}",
                    value=f"{race_data['description']}\n**Bonuses:** {bonuses_text}",
                    inline=False
                )

        embed.set_footer(text="Gunakan !raceinfo [race_name] untuk info detail")

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
                  "`!my_techniques` - View learned techniques\n"
                  "`!discovered_techniques` - View discovered techniques",
            inline=False
        )

        embed.set_footer(text="💫 Idle cultivation gains: ~200 EXP/hour, 405+ Qi/hour, 400+ Spirit Stones/hour!")

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
                  "`!sell <item_name>` - Sell equipment for Qi",
            inline=False
        )

        embed.add_field(
            name="🎒 Inventory",
            value="`!inventory` - View your equipment and items",
            inline=False
        )

        embed.set_footer(text="💰 Earn Qi through cultivation and spend it wisely!")

    elif category.lower() == "beasts":
        embed = discord.Embed(
            title="🐉 Spirit Beast Commands",
            description="Tame spirit beasts for permanent bonuses!",
            color=0x00ff00
        )

        embed.add_field(
            name="🐾 Beast Management",
            value="`!spirit_beasts` - View available spirit beasts\n"
                  "`!tame <beast_name>` - Tame a spirit beast\n"
                  "`!set_beast` - Set active spirit beast\n"
                  "`!inventory` - View your tamed beasts",
            inline=False
        )

        embed.add_field(
            name="🌟 Beast Benefits",
            value="• Permanent power bonuses\n"
                  "• Special ability boosts\n"
                  "• Stat increases\n"
                  "• Unique combat advantages",
            inline=False
        )

        embed.set_footer(text="🐉 Spirit beasts provide permanent bonuses to your cultivation!")

    elif category.lower() == "alchemy":
        embed = discord.Embed(
            title="🧪 Alchemy Commands",
            description="Craft powerful pills to enhance your cultivation!",
            color=0x800080
        )

        embed.add_field(
            name="⚗️ Alchemy System",
            value="`!alchemy` - View available pill recipes\n"
                  "`!craft <pill_name>` - Craft a pill\n"
                  "`!inventory` - View your ingredients",
            inline=False
        )

        embed.add_field(
            name="💊 Pill Effects",
            value="• Instant EXP boosts\n"
                  "• Qi regeneration\n"
                  "• Power increases\n"
                  "• Breakthrough chance bonuses",
            inline=False
        )

        embed.set_footer(text="🧪 Collect ingredients from dungeons to craft powerful pills!")

    elif category.lower() == "achievements":
        embed = discord.Embed(
            title="🏆 Achievement Commands",
            description="Complete achievements for special rewards!",
            color=0xffd700
        )

        embed.add_field(
            name="🎯 Achievement System",
            value="`!achievements` - View all achievements\n"
                  "`!status` - See your progress",
            inline=False
        )

        embed.add_field(
            name="🎁 Achievement Rewards",
            value="• Spirit Stones\n"
                  "• EXP bonuses\n"
                  "• Qi rewards\n"
                  "• Special items",
            inline=False
        )

        embed.set_footer(text="🏆 Complete achievements to show off your cultivation prowess!")

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
                  "• `guild` - Guild system and teamwork\n"
                  "• `beasts` - Spirit beast system\n"
                  "• `alchemy` - Pill crafting system\n"
                  "• `achievements` - Achievement system\n"
                  "• `daily` - Daily quests and events\n"
                  "• `info` - Statistics and information\n"
                  "• `ranking` - Leaderboards and competition\n"
                  "• `system` - Bot utilities",
            inline=False
        )

    await ctx.send(embed=embed)

# ===============================
# DEV COMMANDS - Untuk monitoring dan debugging
# ===============================
@bot.command()
@commands.is_owner()
async def dev_stats(ctx):
    """Lihat statistik internal bot (Owner only)"""
    # Data cultivation aktif
    active_cultivations = len(ACTIVE_CULTIVATIONS)
    cultivation_users = list(ACTIVE_CULTIVATIONS.keys())

    # Data battle aktif
    active_battles = len(ACTIVE_BATTLES)
    battle_info = []
    for battle_id, battle_data in ACTIVE_BATTLES.items():
        battle_info.append(f"{battle_id} (Round {battle_data['round']})")

    # Data pending registrations
    pending_registrations = len(PENDING_REGISTRATIONS)

    # Server stats
    data = load_data()
    server_stats = data["server_stats"]

    embed = discord.Embed(
        title="📊 Dev Statistics - Internal Bot Status",
        description="Statistik internal dan monitoring bot",
        color=0x7289da
    )

    embed.add_field(name="Active Cultivations", value=f"{active_cultivations} users", inline=True)
    embed.add_field(name="Active Battles", value=f"{active_battles} battles", inline=True)
    embed.add_field(name="Pending Registrations", value=f"{pending_registrations} users", inline=True)

    if cultivation_users:
        embed.add_field(name="Cultivating Users", value="\n".join([f"<@{uid}>" for uid in cultivation_users[:5]]), inline=False)

    if battle_info:
        embed.add_field(name="Active Battles Info", value="\n".join(battle_info[:3]), inline=False)

    embed.add_field(name="Total Players", value=data["total_players"], inline=True)
    embed.add_field(name="Total Guilds", value=len(data["guilds"]), inline=True)
    embed.add_field(name="Memory Usage", value=f"{len(str(data)) // 1024} KB", inline=True)

    embed.add_field(
        name="Server Stats", 
        value=f"PvP Battles: {server_stats['total_pvp_battles']}\n"
              f"Breakthroughs: {server_stats['total_breakthroughs']}\n"
              f"Dungeons: {server_stats['total_dungeons']}\n"
              f"Techniques: {server_stats['total_techniques_learned']}",
        inline=False
    )

    embed.set_footer(text=f"Bot Latency: {round(bot.latency * 1000)}ms")
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def dev_cleanup(ctx):
    """Bersihkan data aktivitas yang stuck (Owner only)"""
    # Cleanup stuck cultivations
    cleaned_cultivations = 0
    current_time = time.time()
    for user_id, cult_data in list(ACTIVE_CULTIVATIONS.items()):
        if current_time - cult_data.get("start_time", 0) > 86400:  # 24 jam
            del ACTIVE_CULTIVATIONS[user_id]
            cleaned_cultivations += 1

    # Cleanup stuck battles
    cleaned_battles = 0
    for battle_id, battle_data in list(ACTIVE_BATTLES.items()):
        if not battle_data.get("active", True):
            del ACTIVE_BATTLES[battle_id]
            cleaned_battles += 1

    # Cleanup old pending registrations
    cleaned_registrations = 0
    for user_id, reg_data in list(PENDING_REGISTRATIONS.items()):
        if current_time - float(reg_data.get("start_time", current_time)) > 3600:  # 1 jam
            del PENDING_REGISTRATIONS[user_id]
            cleaned_registrations += 1

    embed = discord.Embed(
        title="🧹 Cleanup Completed",
        description="Pembersihan data internal yang stuck",
        color=0x00ff00
    )

    embed.add_field(name="Cleaned Cultivations", value=cleaned_cultivations, inline=True)
    embed.add_field(name="Cleaned Battles", value=cleaned_battles, inline=True)
    embed.add_field(name="Cleaned Registrations", value=cleaned_registrations, inline=True)
    embed.add_field(name="Active Cultivations", value=len(ACTIVE_CULTIVATIONS), inline=True)
    embed.add_field(name="Active Battles", value=len(ACTIVE_BATTLES), inline=True)
    embed.add_field(name="Pending Registrations", value=len(PENDING_REGISTRATIONS), inline=True)

    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def dev_playerinfo(ctx, member: discord.Member):
    """Lihat info detail player (Owner only)"""
    p = get_player(member.id)
    if not p:
        return await ctx.send("❌ Player tidak ditemukan!")

    # Format created_at time
    created_at = datetime.datetime.fromisoformat(p["created_at"]).strftime("%Y-%m-%d %H:%M")
    last_updated = datetime.datetime.fromisoformat(p["last_updated"]).strftime("%Y-%m-%d %H:%M")

    embed = discord.Embed(
        title=f"👤 Dev Player Info - {member.name}",
        description="Informasi detail player untuk debugging",
        color=0x7289da
    )

    embed.add_field(name="Player ID", value=member.id, inline=True)
    embed.add_field(name="Race", value=p.get("race", "human"), inline=True)
    embed.add_field(name="Gender", value=p.get("gender", "other"), inline=True)

    embed.add_field(name="Realm", value=p["realm"], inline=True)
    embed.add_field(name="Stage", value=p["stage"], inline=True)
    embed.add_field(name="Level", value=get_player_level(p), inline=True)

    embed.add_field(name="EXP", value=f"{p['exp']}/{get_exp_cap(p)}", inline=True)
    embed.add_field(name="Qi", value=p["qi"], inline=True)
    embed.add_field(name="Spirit Stones", value=p["spirit_stones"], inline=True)

    embed.add_field(name="Base Power", value=p["base_power"], inline=True)
    embed.add_field(name="Total Power", value=p["total_power"], inline=True)
    embed.add_field(name="PvP Record", value=f"{p['pvp_wins']}W/{p['pvp_losses']}L", inline=True)

    embed.add_field(name="Techniques Learned", value=len(p["techniques"]), inline=True)
    embed.add_field(name="Spirit Beasts", value=len(p.get("spirit_beasts", [])), inline=True)
    embed.add_field(name="Dungeons Completed", value=p["dungeons_completed"], inline=True)

    embed.add_field(name="Created At", value=created_at, inline=True)
    embed.add_field(name="Last Updated", value=last_updated, inline=True)
    embed.add_field(name="Login Streak", value=p.get("login_streak", 0), inline=True)

    # Equipment info
    if p.get("equipment"):
        equip_power = sum(p["equipment"].values())
        embed.add_field(name="Equipment Power", value=equip_power, inline=True)
        embed.add_field(name="Equipment Items", value=len(p["equipment"]), inline=True)

    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def dev_broadcast(ctx, *, message: str):
    """Broadcast message ke semua player (Owner only)"""
    players = get_all_players()
    notified = 0
    failed = 0

    for player_id in players.keys():
        try:
            user = await bot.fetch_user(int(player_id))
            await user.send(f"📢 **Broadcast dari Developer:**\n{message}")
            notified += 1
        except:
            failed += 1
        await asyncio.sleep(0.5)  # Rate limiting

    await ctx.send(f"✅ Broadcast selesai! Terkirim: {notified}, Gagal: {failed}")

@bot.command()
@commands.is_owner()
async def dev_reload(ctx):
    """Reload data dari file (Owner only)"""
    global players
    players = load_data()
    await ctx.send("✅ Data reloaded dari file!")

@bot.command()
@commands.is_owner()
async def dev_eval(ctx, *, code: str):
    """Jalankan kode Python (Owner only) - HATI-HATI!"""
    try:
        # Restricted environment for safety
        local_vars = {
            'bot': bot,
            'ctx': ctx,
            'get_player': get_player,
            'load_data': load_data,
            'save_data': save_data
        }

        # Remove dangerous built-ins
        restricted_globals = {k: v for k, v in globals().items() if not k.startswith('__')}
        restricted_globals.update(local_vars)

        result = eval(code, restricted_globals, local_vars)
        await ctx.send(f"✅ Eval result:\n```py\n{result}\n```")
    except Exception as e:
        await ctx.send(f"❌ Eval error:\n```{e}```")

@bot.command()
@commands.is_owner()
async def dev_activity(ctx):
    """Cek aktivitas terkini bot (Owner only)"""
    # Get recent player activity
    data = load_data()
    recent_players = []

    for player_id, player_data in data["players"].items():
        try:
            last_updated = datetime.datetime.fromisoformat(player_data["last_updated"])
            if (datetime.datetime.now() - last_updated).days < 7:  # Aktif dalam 7 hari
                recent_players.append((player_id, last_updated, player_data["total_power"]))
        except:
            continue

    # Sort by most recent
    recent_players.sort(key=lambda x: x[1], reverse=True)

    embed = discord.Embed(
        title="📈 Recent Player Activity",
        description="Player yang aktif dalam 7 hari terakhir",
        color=0x00ff00
    )

    active_count = len(recent_players)
    total_count = len(data["players"])

    embed.add_field(name="Active Players", value=f"{active_count}/{total_count} ({active_count/total_count*100:.1f}%)", inline=False)

    # Top 5 most recent players
    if recent_players:
        recent_text = ""
        for i, (player_id, last_updated, power) in enumerate(recent_players[:5]):
            recent_text += f"{i+1}. <@{player_id}> - {power} power ({last_updated.strftime('%Y-%m-%d %H:%M')})\n"
        embed.add_field(name="Most Recent", value=recent_text, inline=False)

    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def reset_boss_cooldown(ctx, member: discord.Member):
    """Reset cooldown boss khusus (Owner only)"""
    p = get_player(member.id)
    if not p:
        return await ctx.send("❌ Player tidak ditemukan!")

    # Reset boss-related cooldowns
    boss_fields = ["last_boss", "boss_cooldown", "last_boss_fight", "boss_challenge_time"]
    
    reset_count = 0
    for field in boss_fields:
        if field in p:
            p[field] = "0"
            reset_count += 1

    update_player(member.id, p)

    # Coba reset di system boss jika ada
    try:
        if BOSS_SYSTEM_LOADED:
            if 'reset_player_boss_cooldown' in globals():
                reset_player_boss_cooldown(member.id)
    except Exception as e:
        print(f"Error resetting boss system cooldown: {e}")

    await ctx.send(f"✅ {reset_count} boss cooldown {member.mention} telah direset!")

# ===============================
# Start bot
# ===============================
keep_alive()

try:
    bot.run(BOT_TOKEN)
except Exception as e:
    print(f"❌ Error running bot: {e}")
    print(f"🔑 Token: {BOT_TOKEN}")