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
try:
    from ai_exploration import AIExploration
    AI_EXPLORATION_LOADED = True
except Exception as e:
    print(f"❌ AI Exploration failed to load: {e}")
    AI_EXPLORATION_LOADED = False

# NPC System Import
try:
    from npc_system import NPCS, get_npc_data, update_npc_affection, query_ai_for_npc_dialogue, save_npc_data
    NPC_SYSTEM_LOADED = True
    print("✅ NPC system loaded successfully!")
except Exception as e:
    print(f"❌ NPC system failed to load: {e}")
    NPC_SYSTEM_LOADED = False

# This block is duplicate - AI_EXPLORATION_LOADED is already set above
try:
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
try:
    from world_boss_system import (
        WORLD_BOSSES,
        ACTIVE_WORLD_BOSSES,
        WORLD_BOSS_PARTIES,
        PLAYER_PARTIES,
        create_party,
        invite_party,
        join_party,
        leave_party,
        party_info,
        challenge_world_boss,
        world_boss_status,
        start_world_boss_tasks
    )
    WORLD_BOSS_SYSTEM_LOADED = True
    print("✅ World Boss system loaded successfully!")
except ImportError as e:
    print(f"❌ Failed to load world boss system: {e}")
    WORLD_BOSS_SYSTEM_LOADED = False

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
# ===============================
# COMPREHENSIVE SECT SYSTEM - 3 REALMS
# ===============================

CULTIVATION_SECTS = {
    # MORTAL REALM SECTS
    "azure_sword": {
        "name": "Azure Sword Sect", 
        "emoji": "⚔️", 
        "realm": "Mortal Realm",
        "specialty": "Sword Mastery", 
        "bonus": {"attack": 0.15, "critical_chance": 0.10},
        "description": "Masters of the Azure Sword techniques, focusing on precise and deadly strikes.",
        "entrance_requirement": "Mortal Realm Stage 3",
        "techniques": ["Azure Slash", "Sword Rain", "Blade Whirlwind", "Azure Strike"]
    },
    "flame_lotus": {
        "name": "Flame Lotus Sect", 
        "emoji": "🔥", 
        "realm": "Mortal Realm",
        "specialty": "Fire Cultivation", 
        "bonus": {"attack": 0.12, "fire_resistance": 0.20},
        "description": "Cultivators who harness the power of flame and lotus energy.",
        "entrance_requirement": "Mortal Realm Stage 5", 
        "techniques": ["Lotus Fire Burst", "Flame Shield", "Phoenix Dance", "Burning Soul"]
    },
    "iron_body": {
        "name": "Iron Body Sect", 
        "emoji": "💪", 
        "realm": "Mortal Realm",
        "specialty": "Physical Cultivation", 
        "bonus": {"defense": 0.20, "health": 0.15},
        "description": "Focuses on strengthening the physical body to unbreakable levels.",
        "entrance_requirement": "Mortal Realm Stage 2",
        "techniques": ["Iron Skin", "Titan Strength", "Unbreakable Will", "Steel Fist"]
    },
    "spirit_herb": {
        "name": "Spirit Herb Sect", 
        "emoji": "🌿", 
        "realm": "Mortal Realm",
        "specialty": "Alchemy & Healing", 
        "bonus": {"healing": 0.25, "pill_efficacy": 0.30},
        "description": "Masters of spiritual herbs and alchemical arts.",
        "entrance_requirement": "Mortal Realm Stage 4",
        "techniques": ["Healing Mist", "Poison Resistance", "Herb Knowledge", "Life Drain"]
    },
    "shadow_moon": {
        "name": "Shadow Moon Sect", 
        "emoji": "🌙", 
        "realm": "Mortal Realm",
        "specialty": "Stealth & Assassination", 
        "bonus": {"movement": 0.18, "stealth": 0.25},
        "description": "Silent assassins who strike from the shadows under moonlight.",
        "entrance_requirement": "Mortal Realm Stage 6",
        "techniques": ["Shadow Step", "Moon Blade", "Invisibility", "Silent Kill"]
    },

    # IMMORTAL REALM SECTS  
    "celestial_sword": {
        "name": "Celestial Sword Palace", 
        "emoji": "🌟", 
        "realm": "Immortal Realm",
        "specialty": "Divine Sword Arts", 
        "bonus": {"attack": 0.25, "divine_power": 0.20},
        "description": "Elite immortal sword cultivators wielding celestial blades.",
        "entrance_requirement": "Immortal Realm Stage 1",
        "techniques": ["Celestial Slash", "Star Sword Rain", "Divine Blade", "Heavenly Cut"]
    },
    "void_abyss": {
        "name": "Void Abyss Sect", 
        "emoji": "🌌", 
        "realm": "Immortal Realm",
        "specialty": "Void Manipulation", 
        "bonus": {"void_power": 0.30, "space_control": 0.25},
        "description": "Masters of void energy and spatial manipulation.",
        "entrance_requirement": "Immortal Realm Stage 3",
        "techniques": ["Void Tear", "Space Lock", "Dimensional Step", "Abyss Call"]
    },
    "phoenix_flame": {
        "name": "Eternal Phoenix Sect", 
        "emoji": "🔥", 
        "realm": "Immortal Realm",
        "specialty": "Phoenix Fire Arts", 
        "bonus": {"fire_mastery": 0.35, "regeneration": 0.20},
        "description": "Immortal fire cultivators who embody the phoenix spirit.",
        "entrance_requirement": "Immortal Realm Stage 2",
        "techniques": ["Phoenix Rebirth", "Eternal Flame", "Fire Storm", "Phoenix Wings"]
    },
    "thunder_emperor": {
        "name": "Thunder Emperor Sect", 
        "emoji": "⚡", 
        "realm": "Immortal Realm",
        "specialty": "Lightning Mastery", 
        "bonus": {"lightning_power": 0.40, "speed": 0.25},
        "description": "Controllers of thunder and lightning, blessed by the Thunder Emperor.",
        "entrance_requirement": "Immortal Realm Stage 4",
        "techniques": ["Thunder Strike", "Lightning Body", "Storm Call", "Emperor's Wrath"]
    },
    "jade_palace": {
        "name": "Jade Immortal Palace", 
        "emoji": "💎", 
        "realm": "Immortal Realm",
        "specialty": "Jade Cultivation", 
        "bonus": {"defense": 0.30, "jade_power": 0.25},
        "description": "Noble immortals who cultivate with pure jade energy.",
        "entrance_requirement": "Immortal Realm Stage 5",
        "techniques": ["Jade Shield", "Crystal Armor", "Jade Beam", "Immortal Protection"]
    },

    # GOD REALM SECTS
    "primordial_dao": {
        "name": "Primordial Dao Temple", 
        "emoji": "☯️", 
        "realm": "God Realm",
        "specialty": "Dao Mastery", 
        "bonus": {"dao_power": 0.50, "cosmic_insight": 0.40},
        "description": "Ancient gods who comprehend the fundamental laws of existence.",
        "entrance_requirement": "God Realm Stage 1",
        "techniques": ["Dao Strike", "Law Manipulation", "Reality Bend", "Cosmic Truth"]
    },
    "universe_creator": {
        "name": "Universe Creator Sect", 
        "emoji": "🌍", 
        "realm": "God Realm",
        "specialty": "Creation Powers", 
        "bonus": {"creation_power": 0.60, "universe_control": 0.45},
        "description": "Gods who possess the power to create and destroy universes.",
        "entrance_requirement": "God Realm Stage 3",
        "techniques": ["Universe Genesis", "World Destroyer", "Star Creation", "Galaxy Forge"]
    },
    "time_space": {
        "name": "Time-Space Dominion", 
        "emoji": "⏰", 
        "realm": "God Realm",
        "specialty": "Time & Space Control", 
        "bonus": {"time_mastery": 0.55, "space_mastery": 0.50},
        "description": "Divine beings who control the flow of time and fabric of space.",
        "entrance_requirement": "God Realm Stage 2",
        "techniques": ["Time Stop", "Space Warp", "Temporal Slash", "Dimensional Prison"]
    },
    "chaos_order": {
        "name": "Chaos-Order Balance", 
        "emoji": "⚖️", 
        "realm": "God Realm",
        "specialty": "Balance Mastery", 
        "bonus": {"chaos_power": 0.35, "order_power": 0.35, "balance": 0.40},
        "description": "Gods who maintain the eternal balance between chaos and order.",
        "entrance_requirement": "God Realm Stage 4",
        "techniques": ["Chaos Storm", "Order Lock", "Balance Strike", "Duality Mastery"]
    },
    "infinite_void": {
        "name": "Infinite Void Sect", 
        "emoji": "🌌", 
        "realm": "God Realm",
        "specialty": "Void Transcendence", 
        "bonus": {"void_transcendence": 0.70, "infinite_power": 0.60},
        "description": "The ultimate sect for gods who transcend existence itself.",
        "entrance_requirement": "God Realm Stage 5",
        "techniques": ["Void Transcendence", "Infinite Strike", "Existence Erase", "Beyond Reality"]
    }
}

# Expanded Technique System
TECHNIQUE_TYPES = {
    "attack": {"name": "Attack Technique", "emoji": "⚡", "power_bonus": (0.15, 0.25)},
    "defense": {"name": "Defense Technique", "emoji": "🛡️", "power_bonus": (0.10, 0.20)},
    "support": {"name": "Support Technique", "emoji": "💫", "power_bonus": (0.08, 0.18)},
    "healing": {"name": "Healing Technique", "emoji": "❤️", "power_bonus": (0.05, 0.15)},
    "movement": {"name": "Movement Technique", "emoji": "💨", "power_bonus": (0.07, 0.17)},
    "special": {"name": "Special Technique", "emoji": "✨", "power_bonus": (0.20, 0.35)},
    "ultimate": {"name": "Ultimate Technique", "emoji": "💥", "power_bonus": (0.40, 0.60)}
}

# Sect Helper Functions
def get_player_sect(player_id):
    """Get player's current sect"""
    p = get_player(player_id)
    if p is None:
        return None
    return p.get("sect", None)

def can_join_sect(player_data, sect_id):
    """Check if player meets sect requirements"""
    sect = CULTIVATION_SECTS[sect_id]
    player_realm = player_data["realm"]
    player_stage = player_data["stage"]
    
    # Check realm requirement
    required_realm = sect["realm"]
    if player_realm != required_realm:
        return False, f"Must be in {required_realm}"
    
    # Check stage requirement
    requirement = sect["entrance_requirement"]
    if "Stage" in requirement:
        required_stage = int(requirement.split("Stage ")[1])
        if player_stage < required_stage:
            return False, f"Must reach {requirement}"
    
    return True, ""

def get_sect_techniques(sect_id):
    """Get all techniques available to a sect"""
    if sect_id in CULTIVATION_SECTS:
        return CULTIVATION_SECTS[sect_id]["techniques"]
    return []

def apply_sect_bonuses(player_data, sect_id):
    """Apply sect bonuses to player stats"""
    if sect_id not in CULTIVATION_SECTS:
        return player_data["total_power"]
    
    sect = CULTIVATION_SECTS[sect_id]
    bonuses = sect["bonus"]
    base_power = player_data["total_power"]
    
    # Apply all sect bonuses
    total_bonus = 0
    for bonus_type, bonus_value in bonuses.items():
        total_bonus += bonus_value
    
    return int(base_power * (1 + total_bonus))

ELEMENT_TYPES = {
    "fire": "🔥", "water": "💧", "earth": "🌍", "wind": "💨", 
    "lightning": "⚡", "ice": "❄️", "light": "✨", "dark": "🌙"
}

# ===============================
# EXCITING NEW GAME SYSTEMS
# ===============================

# ARTIFACT SYSTEM - Powerful special items
ARTIFACTS = {
    # Mortal Realm Artifacts
    "jade_phoenix_pendant": {
        "name": "Jade Phoenix Pendant",
        "rarity": "legendary",
        "emoji": "🟢",
        "realm": "Mortal Realm",
        "power_bonus": 1000,
        "special_effect": "Phoenix Rebirth - 10% chance to survive fatal attacks",
        "description": "A jade pendant containing the essence of a phoenix spirit",
        "activation_cost": 50,
        "cooldown": 3600  # 1 hour
    },
    "lightning_essence_orb": {
        "name": "Lightning Essence Orb",
        "rarity": "epic",
        "emoji": "⚡",
        "realm": "Mortal Realm", 
        "power_bonus": 800,
        "special_effect": "Lightning Strike - Deal 50% extra damage in next battle",
        "description": "Crystallized lightning essence that crackles with power",
        "activation_cost": 30,
        "cooldown": 1800  # 30 minutes
    },
    "earth_spirit_crown": {
        "name": "Earth Spirit Crown",
        "rarity": "rare",
        "emoji": "👑",
        "realm": "Mortal Realm",
        "power_bonus": 600,
        "special_effect": "Stone Skin - Reduce damage taken by 25% for 1 hour",
        "description": "Crown blessed by earth spirits for protection",
        "activation_cost": 40,
        "cooldown": 2400  # 40 minutes
    },

    # Immortal Realm Artifacts
    "celestial_star_map": {
        "name": "Celestial Star Map",
        "rarity": "mythic",
        "emoji": "🗺️",
        "realm": "Immortal Realm",
        "power_bonus": 2500,
        "special_effect": "Star Navigation - Increase exploration success by 75%",
        "description": "Ancient map showing the positions of celestial bodies",
        "activation_cost": 100,
        "cooldown": 7200  # 2 hours
    },
    "void_shatter_gauntlets": {
        "name": "Void Shatter Gauntlets",
        "rarity": "legendary",
        "emoji": "🥊",
        "realm": "Immortal Realm",
        "power_bonus": 2000,
        "special_effect": "Void Strike - Ignore all defenses in next attack",
        "description": "Gauntlets that can tear through the fabric of space",
        "activation_cost": 80,
        "cooldown": 5400  # 1.5 hours
    },
    "immortal_healing_lotus": {
        "name": "Immortal Healing Lotus",
        "rarity": "epic",
        "emoji": "🪷",
        "realm": "Immortal Realm",
        "power_bonus": 1500,
        "special_effect": "Lotus Regeneration - Fully heal and remove all debuffs",
        "description": "Sacred lotus that blooms only in immortal gardens",
        "activation_cost": 60,
        "cooldown": 3600  # 1 hour
    },

    # God Realm Artifacts
    "creation_genesis_stone": {
        "name": "Creation Genesis Stone",
        "rarity": "transcendent",
        "emoji": "💎",
        "realm": "God Realm",
        "power_bonus": 5000,
        "special_effect": "Genesis Creation - Create a temporary pocket dimension",
        "description": "The original stone used to create the first universe",
        "activation_cost": 200,
        "cooldown": 14400  # 4 hours
    },
    "time_control_hourglass": {
        "name": "Time Control Hourglass",
        "rarity": "mythic",
        "emoji": "⏳",
        "realm": "God Realm",
        "power_bonus": 4000,
        "special_effect": "Time Manipulation - Reset all cooldowns instantly",
        "description": "Hourglass containing the sands of time itself",
        "activation_cost": 150,
        "cooldown": 10800  # 3 hours
    },
    "infinity_chaos_orb": {
        "name": "Infinity Chaos Orb",
        "rarity": "legendary",
        "emoji": "🌌",
        "realm": "God Realm",
        "power_bonus": 3500,
        "special_effect": "Chaos Burst - Random powerful effect activated",
        "description": "Orb containing the raw chaos of infinite possibilities",
        "activation_cost": 120,
        "cooldown": 7200  # 2 hours
    }
}

# CULTIVATION FORMATIONS - Group cultivation system
FORMATIONS = {
    "seven_star_formation": {
        "name": "Seven Star Formation",
        "emoji": "✨",
        "min_participants": 3,
        "max_participants": 7,
        "duration": 3600,  # 1 hour
        "power_multiplier": 1.5,
        "qi_bonus": 2.0,
        "cost_per_person": 100,
        "description": "Ancient formation that channels star power for cultivation"
    },
    "dragon_ascension_circle": {
        "name": "Dragon Ascension Circle",
        "emoji": "🐲",
        "min_participants": 5,
        "max_participants": 10,
        "duration": 7200,  # 2 hours
        "power_multiplier": 2.0,
        "qi_bonus": 3.0,
        "cost_per_person": 250,
        "description": "Formation that mimics the ascension path of ancient dragons"
    },
    "phoenix_rebirth_array": {
        "name": "Phoenix Rebirth Array",
        "emoji": "🔥",
        "min_participants": 2,
        "max_participants": 5,
        "duration": 5400,  # 1.5 hours
        "power_multiplier": 1.8,
        "qi_bonus": 2.5,
        "cost_per_person": 180,
        "description": "Formation focused on rebirth and transformation energies"
    }
}

# ENLIGHTENMENT EVENTS - Random spiritual awakenings
ENLIGHTENMENT_EVENTS = {
    "dao_comprehension": {
        "name": "Dao Comprehension",
        "emoji": "☯️",
        "rarity": "rare",
        "power_boost": (500, 1500),
        "qi_boost": (200, 800),
        "chance": 0.05,  # 5% chance
        "description": "You suddenly comprehend a fragment of the universal Dao",
        "message": "💫 **Enlightenment!** The mysteries of the Dao become clearer to you!"
    },
    "elemental_awakening": {
        "name": "Elemental Awakening",
        "emoji": "🌟",
        "rarity": "uncommon",
        "power_boost": (300, 800),
        "qi_boost": (100, 400),
        "chance": 0.08,  # 8% chance
        "description": "Your understanding of elemental forces deepens dramatically",
        "message": "⚡ **Elemental Awakening!** You feel one with the elements!"
    },
    "cosmic_revelation": {
        "name": "Cosmic Revelation",
        "emoji": "🌌",
        "rarity": "legendary",
        "power_boost": (1000, 3000),
        "qi_boost": (500, 1500),
        "chance": 0.02,  # 2% chance
        "description": "The secrets of the cosmos are revealed to your inner eye",
        "message": "🌟 **COSMIC REVELATION!** The universe speaks directly to your soul!"
    },
    "inner_demon_defeat": {
        "name": "Inner Demon Defeat",
        "emoji": "😈",
        "rarity": "epic",
        "power_boost": (800, 2000),
        "qi_boost": (300, 1000),
        "chance": 0.03,  # 3% chance
        "description": "You overcome a major inner demon and achieve spiritual clarity",
        "message": "👹 **Inner Demon Defeated!** Your mind is clearer than ever before!"
    }
}

# TREASURE HUNT LOCATIONS - Exploration system
TREASURE_LOCATIONS = {
    "ancient_ruins": {
        "name": "Ancient Ruins",
        "emoji": "🏛️",
        "difficulty": "medium",
        "exploration_time": 1800,  # 30 minutes
        "cost": 50,
        "success_chance": 0.6,
        "rewards": {
            "spirit_stones": (100, 500),
            "artifacts": ["lightning_essence_orb", "earth_spirit_crown"],
            "power_gain": (200, 600)
        },
        "description": "Mysterious ruins left by ancient cultivators"
    },
    "mystic_cave": {
        "name": "Mystic Cave",
        "emoji": "🕳️",
        "difficulty": "easy",
        "exploration_time": 900,  # 15 minutes
        "cost": 25,
        "success_chance": 0.8,
        "rewards": {
            "spirit_stones": (50, 200),
            "qi_gain": (100, 300),
            "power_gain": (100, 300)
        },
        "description": "A cave filled with natural qi formations"
    },
    "celestial_peak": {
        "name": "Celestial Peak",
        "emoji": "⛰️",
        "difficulty": "hard",
        "exploration_time": 3600,  # 1 hour
        "cost": 150,
        "success_chance": 0.4,
        "rewards": {
            "spirit_stones": (300, 1000),
            "artifacts": ["celestial_star_map", "void_shatter_gauntlets"],
            "power_gain": (500, 1200),
            "enlightenment_chance": 0.1
        },
        "description": "Sacred peak where immortals once meditated"
    },
    "void_dimension": {
        "name": "Void Dimension",
        "emoji": "🌌",
        "difficulty": "extreme",
        "exploration_time": 7200,  # 2 hours
        "cost": 500,
        "success_chance": 0.2,
        "rewards": {
            "spirit_stones": (1000, 3000),
            "artifacts": ["creation_genesis_stone", "time_control_hourglass"],
            "power_gain": (1000, 2500),
            "enlightenment_chance": 0.25
        },
        "description": "Dangerous dimension where reality bends and breaks"
    }
}

# Global tracking for formations and treasure hunts
active_formations = {}
active_explorations = {}
player_artifacts = {}  # player_id: [artifact_ids]
artifact_cooldowns = {}  # player_id: {artifact_id: timestamp}

# ===============================
# NPC Combat Assistance System
# ===============================

NPC_COMBAT_BONUSES = {
    # Combat assistance bonuses based on NPC specialty
    "sword_master": {"damage": 0.25, "defense": 0.10, "special": "Critical Strike (30% chance for 2x damage)"},
    "alchemist": {"healing": 0.20, "damage": 0.05, "special": "Auto-heal 10% HP every 3 rounds"},
    "demon_slayer": {"damage": 0.30, "defense": 0.05, "special": "Demon Bane (50% more damage vs dark enemies)"},
    "formation_expert": {"defense": 0.25, "damage": 0.10, "special": "Barrier Formation (blocks 1 fatal blow)"},
    "beast_tamer": {"damage": 0.15, "defense": 0.15, "special": "Spirit Beast summon (extra 100 damage per turn)"},
    "lightning_cultivator": {"damage": 0.35, "special": "Lightning Storm (AOE attack in group battles)"},
    "assassin": {"damage": 0.20, "special": "Shadow Strike (bypass 50% enemy defense)"},
    "illusionist": {"defense": 0.20, "special": "Illusion Shield (50% chance to dodge attacks)"},
    "fire_cultivator": {"damage": 0.30, "special": "Burning Soul (additional fire damage over time)"},
    "dao_sage": {"damage": 0.15, "defense": 0.15, "special": "Dao Enlightenment (all bonuses +10%)"},
    "ice_empress": {"damage": 0.25, "defense": 0.15, "special": "Frozen Domain (slow enemy attacks)"},
    "healer": {"healing": 0.30, "defense": 0.10, "special": "Divine Healing (restore 20% HP instantly)"},
    "moon_goddess": {"damage": 0.20, "defense": 0.20, "special": "Moonlight Blessing (regenerate 5% HP per turn)"},
    "sword_maiden": {"damage": 0.25, "defense": 0.15, "special": "Sword Dance (multiple strikes)"},
    "flower_spirit": {"healing": 0.25, "defense": 0.10, "special": "Petal Shield (absorb damage)"},
    "wind_cultivator": {"damage": 0.20, "defense": 0.10, "special": "Wind Acceleration (+50% speed)"},
    "mystic_seer": {"damage": 0.15, "defense": 0.25, "special": "Future Sight (predict enemy attacks)"},
    "sound_cultivator": {"damage": 0.25, "special": "Sonic Wave (ignore defense)"},
    "genius_alchemist": {"healing": 0.35, "damage": 0.10, "special": "Perfect Pill (full heal once per battle)"},
    "jade_empress": {"damage": 0.30, "defense": 0.30, "special": "Jade Immortality (immune to status effects)"}
}

def get_player_combat_assistant(player_id):
    """Get player's selected combat assistant NPC"""
    p = get_player(player_id)
    return p.get("combat_assistant", None)

def can_use_npc_assistant(player_id, npc_id):
    """Check if player can use this NPC as combat assistant (60%+ affection)"""
    try:
        from npc_system import get_npc_data
        npc_data = get_npc_data(player_id, npc_id)
        return npc_data["affection_level"] >= 60
    except:
        return False

def check_exclusive_relationship_limit(player_id, target_npc_id, new_affection):
    """Check if exclusive relationship rules allow this affection increase"""
    try:
        from npc_system import get_npc_data, NPCS
        
        # If trying to go above 80%, check for existing 100% relationships
        if new_affection > 80:
            for npc_id in NPCS.keys():
                if npc_id != target_npc_id:
                    npc_data = get_npc_data(player_id, npc_id)
                    if npc_data["affection_level"] >= 100:
                        # Someone else is already at 100%, block this increase
                        return False, npc_data["name"]
        
        # If trying to reach 100%, block all other NPCs at 80%
        if new_affection >= 100:
            for npc_id in NPCS.keys():
                if npc_id != target_npc_id:
                    npc_data = get_npc_data(player_id, npc_id)
                    if npc_data["affection_level"] > 80:
                        # Force other NPCs down to 80% maximum
                        npc_data["affection_level"] = 80
                        # Update their relationship status
                        for threshold, status in reversed(list(AFFECTION_THRESHOLDS.items())):
                            if 80 >= threshold:
                                npc_data["relationship_status"] = status
                                break
        
        return True, None
        
    except:
        return True, None  # Allow increase if there's an error

# Import affection thresholds here for use in the function above
try:
    from npc_system import AFFECTION_THRESHOLDS
except:
    AFFECTION_THRESHOLDS = {
        0: "stranger",
        10: "acquaintance", 
        25: "friend",
        50: "close_friend",
        75: "beloved",
        90: "soulmate"
    }

def get_npc_combat_bonus(npc_specialty, bonus_type):
    """Get NPC combat bonus by specialty and type"""
    if npc_specialty in NPC_COMBAT_BONUSES:
        return NPC_COMBAT_BONUSES[npc_specialty].get(bonus_type, 0)
    return 0

def apply_npc_combat_assistance(player_data, npc_specialty):
    """Apply NPC combat bonuses to player stats"""
    bonuses = NPC_COMBAT_BONUSES.get(npc_specialty, {})
    
    # Apply damage bonus
    damage_bonus = bonuses.get("damage", 0)
    enhanced_power = int(player_data["total_power"] * (1 + damage_bonus))
    
    # Apply defense bonus (reduces incoming damage)
    defense_bonus = bonuses.get("defense", 0)
    
    # Apply healing bonus (increases healing effects)
    healing_bonus = bonuses.get("healing", 0)
    
    return {
        "enhanced_power": enhanced_power,
        "defense_bonus": defense_bonus,
        "healing_bonus": healing_bonus,
        "special_ability": bonuses.get("special", "")
    }

# ===============================
# Equipment System - DIPERLUAS
# ===============================
EQUIPMENT_SHOP = {
    # MORTAL REALM EQUIPMENT - EXPANDED
    
    # Tier 1 - Basic (Wood/Cloth/Copper)
    "wooden_sword": {"name": "Wooden Sword", "power": 8, "cost": 50, "type": "weapon", "emoji": "⚔️", "realm": "Mortal Realm", "tier": "Basic", "set": "wooden"},
    "cloth_armor": {"name": "Cloth Armor", "power": 5, "cost": 40, "type": "armor", "emoji": "🛡️", "realm": "Mortal Realm", "tier": "Basic", "set": "cloth"},
    "cloth_hat": {"name": "Cloth Hat", "power": 4, "cost": 35, "type": "helmet", "emoji": "🎩", "realm": "Mortal Realm", "tier": "Basic", "set": "cloth"},
    "copper_ring": {"name": "Copper Ring", "power": 3, "cost": 30, "type": "accessory", "emoji": "💍", "realm": "Mortal Realm", "tier": "Basic", "set": "copper"},

    # Tier 2 - Common (Iron/Leather)  
    "iron_sword": {"name": "Iron Sword", "power": 15, "cost": 120, "type": "weapon", "emoji": "⚔️", "realm": "Mortal Realm", "tier": "Common", "set": "iron"},
    "leather_armor": {"name": "Leather Armor", "power": 12, "cost": 100, "type": "armor", "emoji": "🛡️", "realm": "Mortal Realm", "tier": "Common", "set": "leather"},
    "leather_helmet": {"name": "Leather Helmet", "power": 10, "cost": 90, "type": "helmet", "emoji": "⛑️", "realm": "Mortal Realm", "tier": "Common", "set": "leather"},
    "iron_ring": {"name": "Iron Ring", "power": 8, "cost": 80, "type": "accessory", "emoji": "💍", "realm": "Mortal Realm", "tier": "Common", "set": "iron"},

    # Tier 3 - Rare (Steel)
    "steel_sword": {"name": "Steel Sword", "power": 25, "cost": 250, "type": "weapon", "emoji": "⚔️", "realm": "Mortal Realm", "tier": "Rare", "set": "steel"},
    "steel_armor": {"name": "Steel Armor", "power": 20, "cost": 200, "type": "armor", "emoji": "🛡️", "realm": "Mortal Realm", "tier": "Rare", "set": "steel"},
    "steel_helm": {"name": "Steel Helm", "power": 18, "cost": 180, "type": "helmet", "emoji": "🪖", "realm": "Mortal Realm", "tier": "Rare", "set": "steel"},
    "steel_amulet": {"name": "Steel Amulet", "power": 15, "cost": 180, "type": "accessory", "emoji": "🔮", "realm": "Mortal Realm", "tier": "Rare", "set": "steel"},

    # Tier 4 - Epic (Spirit)
    "spirit_sword": {"name": "Spirit Sword", "power": 40, "cost": 500, "type": "weapon", "emoji": "🗡️", "realm": "Mortal Realm", "tier": "Epic", "set": "spirit"},
    "spirit_armor": {"name": "Spirit Armor", "power": 35, "cost": 450, "type": "armor", "emoji": "🛡️", "realm": "Mortal Realm", "tier": "Epic", "set": "spirit"},
    "spirit_crown": {"name": "Spirit Crown", "power": 32, "cost": 420, "type": "helmet", "emoji": "👑", "realm": "Mortal Realm", "tier": "Epic", "set": "spirit"},
    "spirit_pendant": {"name": "Spirit Pendant", "power": 30, "cost": 400, "type": "accessory", "emoji": "✨", "realm": "Mortal Realm", "tier": "Epic", "set": "spirit"},

    # Tier 5 - Legendary (Crystal)
    "crystal_blade": {"name": "Crystal Blade", "power": 65, "cost": 800, "type": "weapon", "emoji": "💎", "realm": "Mortal Realm", "tier": "Legendary", "set": "crystal"},
    "crystal_mail": {"name": "Crystal Mail", "power": 55, "cost": 700, "type": "armor", "emoji": "💠", "realm": "Mortal Realm", "tier": "Legendary", "set": "crystal"},
    "crystal_circlet": {"name": "Crystal Circlet", "power": 50, "cost": 650, "type": "helmet", "emoji": "💎", "realm": "Mortal Realm", "tier": "Legendary", "set": "crystal"},
    "crystal_orb": {"name": "Crystal Orb", "power": 45, "cost": 600, "type": "accessory", "emoji": "🔮", "realm": "Mortal Realm", "tier": "Legendary", "set": "crystal"},

    # Tier 6 - Mythic (Jade) 
    "jade_saber": {"name": "Jade Saber", "power": 90, "cost": 1200, "type": "weapon", "emoji": "🗡️", "realm": "Mortal Realm", "tier": "Mythic", "set": "jade"},
    "jade_robes": {"name": "Jade Robes", "power": 80, "cost": 1100, "type": "armor", "emoji": "👘", "realm": "Mortal Realm", "tier": "Mythic", "set": "jade"},
    "jade_diadem": {"name": "Jade Diadem", "power": 75, "cost": 1000, "type": "helmet", "emoji": "👑", "realm": "Mortal Realm", "tier": "Mythic", "set": "jade"},
    "jade_bracelet": {"name": "Jade Bracelet", "power": 70, "cost": 950, "type": "accessory", "emoji": "📿", "realm": "Mortal Realm", "tier": "Mythic", "set": "jade"},

    # Tier 7 - Phoenix (Phoenix)
    "phoenix_talon": {"name": "Phoenix Talon", "power": 120, "cost": 1800, "type": "weapon", "emoji": "🔥", "realm": "Mortal Realm", "tier": "Phoenix", "set": "phoenix"},
    "phoenix_feather_armor": {"name": "Phoenix Feather Armor", "power": 110, "cost": 1700, "type": "armor", "emoji": "🪶", "realm": "Mortal Realm", "tier": "Phoenix", "set": "phoenix"},
    "phoenix_crest": {"name": "Phoenix Crest", "power": 100, "cost": 1600, "type": "helmet", "emoji": "🔥", "realm": "Mortal Realm", "tier": "Phoenix", "set": "phoenix"},
    "phoenix_heart": {"name": "Phoenix Heart", "power": 95, "cost": 1500, "type": "accessory", "emoji": "❤️‍🔥", "realm": "Mortal Realm", "tier": "Phoenix", "set": "phoenix"},

    # Tier 8 - Dragon (Dragon)
    "dragon_fang": {"name": "Dragon Fang", "power": 160, "cost": 2500, "type": "weapon", "emoji": "🐲", "realm": "Mortal Realm", "tier": "Dragon", "set": "dragon"},
    "dragon_scale_armor": {"name": "Dragon Scale Armor", "power": 140, "cost": 2300, "type": "armor", "emoji": "🐉", "realm": "Mortal Realm", "tier": "Dragon", "set": "dragon"},
    "dragon_horn_helm": {"name": "Dragon Horn Helm", "power": 130, "cost": 2200, "type": "helmet", "emoji": "🐲", "realm": "Mortal Realm", "tier": "Dragon", "set": "dragon"},
    "dragon_pearl": {"name": "Dragon Pearl", "power": 120, "cost": 2000, "type": "accessory", "emoji": "🔮", "realm": "Mortal Realm", "tier": "Dragon", "set": "dragon"},

    # IMMORTAL REALM EQUIPMENT - EXPANDED
    
    # Tier 1 - Celestial 
    "celestial_blade": {"name": "Celestial Blade", "power": 200, "cost": 3000, "type": "weapon", "emoji": "🌟", "realm": "Immortal Realm", "tier": "Celestial", "set": "celestial"},
    "celestial_robes": {"name": "Celestial Robes", "power": 180, "cost": 2800, "type": "armor", "emoji": "👘", "realm": "Immortal Realm", "tier": "Celestial", "set": "celestial"},
    "celestial_crown": {"name": "Celestial Crown", "power": 170, "cost": 2600, "type": "helmet", "emoji": "👑", "realm": "Immortal Realm", "tier": "Celestial", "set": "celestial"},
    "celestial_ring": {"name": "Celestial Ring", "power": 160, "cost": 2500, "type": "accessory", "emoji": "💍", "realm": "Immortal Realm", "tier": "Celestial", "set": "celestial"},

    # Tier 2 - Void
    "void_slasher": {"name": "Void Slasher", "power": 300, "cost": 5000, "type": "weapon", "emoji": "🌌", "realm": "Immortal Realm", "tier": "Void", "set": "void"},
    "void_mantle": {"name": "Void Mantle", "power": 280, "cost": 4800, "type": "armor", "emoji": "🌃", "realm": "Immortal Realm", "tier": "Void", "set": "void"},
    "void_mask": {"name": "Void Mask", "power": 270, "cost": 4600, "type": "helmet", "emoji": "🎭", "realm": "Immortal Realm", "tier": "Void", "set": "void"},
    "void_orb": {"name": "Void Orb", "power": 260, "cost": 4500, "type": "accessory", "emoji": "🔮", "realm": "Immortal Realm", "tier": "Void", "set": "void"},

    # Tier 3 - Profound
    "profound_saber": {"name": "Profound Saber", "power": 450, "cost": 8000, "type": "weapon", "emoji": "🗡️", "realm": "Immortal Realm", "tier": "Profound", "set": "profound"},
    "profound_vestments": {"name": "Profound Vestments", "power": 420, "cost": 7500, "type": "armor", "emoji": "🥻", "realm": "Immortal Realm", "tier": "Profound", "set": "profound"},
    "profound_helm": {"name": "Profound Helm", "power": 400, "cost": 7200, "type": "helmet", "emoji": "⛑️", "realm": "Immortal Realm", "tier": "Profound", "set": "profound"},
    "profound_talisman": {"name": "Profound Talisman", "power": 380, "cost": 7000, "type": "accessory", "emoji": "📿", "realm": "Immortal Realm", "tier": "Profound", "set": "profound"},

    # Tier 4 - Stellar
    "stellar_destroyer": {"name": "Stellar Destroyer", "power": 650, "cost": 12000, "type": "weapon", "emoji": "💫", "realm": "Immortal Realm", "tier": "Stellar", "set": "stellar"},
    "stellar_guardianship": {"name": "Stellar Guardianship", "power": 600, "cost": 11000, "type": "armor", "emoji": "🌌", "realm": "Immortal Realm", "tier": "Stellar", "set": "stellar"},
    "stellar_circlet": {"name": "Stellar Circlet", "power": 580, "cost": 10500, "type": "helmet", "emoji": "⭐", "realm": "Immortal Realm", "tier": "Stellar", "set": "stellar"},
    "stellar_prism": {"name": "Stellar Prism", "power": 550, "cost": 10000, "type": "accessory", "emoji": "🔷", "realm": "Immortal Realm", "tier": "Stellar", "set": "stellar"},

    # Tier 5 - Cosmic
    "cosmic_obliterator": {"name": "Cosmic Obliterator", "power": 900, "cost": 18000, "type": "weapon", "emoji": "🌠", "realm": "Immortal Realm", "tier": "Cosmic", "set": "cosmic"},
    "cosmic_aegis": {"name": "Cosmic Aegis", "power": 850, "cost": 17000, "type": "armor", "emoji": "🛡️", "realm": "Immortal Realm", "tier": "Cosmic", "set": "cosmic"},
    "cosmic_diadem": {"name": "Cosmic Diadem", "power": 820, "cost": 16500, "type": "helmet", "emoji": "💎", "realm": "Immortal Realm", "tier": "Cosmic", "set": "cosmic"},
    "cosmic_nucleus": {"name": "Cosmic Nucleus", "power": 800, "cost": 16000, "type": "accessory", "emoji": "🌌", "realm": "Immortal Realm", "tier": "Cosmic", "set": "cosmic"},

    # Tier 6 - Eternal
    "eternal_judgment": {"name": "Eternal Judgment", "power": 1300, "cost": 25000, "type": "weapon", "emoji": "⚖️", "realm": "Immortal Realm", "tier": "Eternal", "set": "eternal"},
    "eternal_bastion": {"name": "Eternal Bastion", "power": 1200, "cost": 23000, "type": "armor", "emoji": "🏰", "realm": "Immortal Realm", "tier": "Eternal", "set": "eternal"},
    "eternal_crown": {"name": "Eternal Crown", "power": 1150, "cost": 22000, "type": "helmet", "emoji": "👑", "realm": "Immortal Realm", "tier": "Eternal", "set": "eternal"},
    "eternal_heart": {"name": "Eternal Heart", "power": 1100, "cost": 21000, "type": "accessory", "emoji": "💖", "realm": "Immortal Realm", "tier": "Eternal", "set": "eternal"},

    # Tier 7 - Transcendent
    "transcendent_apocalypse": {"name": "Transcendent Apocalypse", "power": 1800, "cost": 35000, "type": "weapon", "emoji": "💥", "realm": "Immortal Realm", "tier": "Transcendent", "set": "transcendent"},
    "transcendent_sanctuary": {"name": "Transcendent Sanctuary", "power": 1700, "cost": 33000, "type": "armor", "emoji": "🏛️", "realm": "Immortal Realm", "tier": "Transcendent", "set": "transcendent"},
    "transcendent_aureole": {"name": "Transcendent Aureole", "power": 1650, "cost": 32000, "type": "helmet", "emoji": "😇", "realm": "Immortal Realm", "tier": "Transcendent", "set": "transcendent"},
    "transcendent_essence": {"name": "Transcendent Essence", "power": 1600, "cost": 31000, "type": "accessory", "emoji": "✨", "realm": "Immortal Realm", "tier": "Transcendent", "set": "transcendent"},

    # Tier 8 - Immortal (Ultimate Immortal Tier)
    "immortal_dao_sword": {"name": "Immortal Dao Sword", "power": 2500, "cost": 50000, "type": "weapon", "emoji": "⚡", "realm": "Immortal Realm", "tier": "Immortal", "set": "immortal"},
    "immortal_phoenix_armor": {"name": "Immortal Phoenix Armor", "power": 2300, "cost": 45000, "type": "armor", "emoji": "🔥", "realm": "Immortal Realm", "tier": "Immortal", "set": "immortal"},
    "immortal_dragon_helm": {"name": "Immortal Dragon Helm", "power": 2200, "cost": 43000, "type": "helmet", "emoji": "🐲", "realm": "Immortal Realm", "tier": "Immortal", "set": "immortal"},
    "immortal_lotus_seal": {"name": "Immortal Lotus Seal", "power": 2100, "cost": 40000, "type": "accessory", "emoji": "🪷", "realm": "Immortal Realm", "tier": "Immortal", "set": "immortal"},

    # GOD REALM EQUIPMENT - EXPANDED
    
    # Tier 1 - Divine
    "divine_judgment": {"name": "Divine Judgment", "power": 3000, "cost": 60000, "type": "weapon", "emoji": "⚖️", "realm": "God Realm", "tier": "Divine", "set": "divine"},
    "divine_sanctuary": {"name": "Divine Sanctuary", "power": 2800, "cost": 55000, "type": "armor", "emoji": "🏛️", "realm": "God Realm", "tier": "Divine", "set": "divine"},
    "divine_aureole": {"name": "Divine Aureole", "power": 2700, "cost": 53000, "type": "helmet", "emoji": "😇", "realm": "God Realm", "tier": "Divine", "set": "divine"},
    "divine_halo": {"name": "Divine Halo", "power": 2600, "cost": 50000, "type": "accessory", "emoji": "✨", "realm": "God Realm", "tier": "Divine", "set": "divine"},

    # Tier 2 - Sacred
    "sacred_annihilator": {"name": "Sacred Annihilator", "power": 4500, "cost": 90000, "type": "weapon", "emoji": "💥", "realm": "God Realm", "tier": "Sacred", "set": "sacred"},
    "sacred_fortress": {"name": "Sacred Fortress", "power": 4200, "cost": 85000, "type": "armor", "emoji": "🏰", "realm": "God Realm", "tier": "Sacred", "set": "sacred"},
    "sacred_crown": {"name": "Sacred Crown", "power": 4000, "cost": 80000, "type": "helmet", "emoji": "👑", "realm": "God Realm", "tier": "Sacred", "set": "sacred"},
    "sacred_eye": {"name": "Sacred Eye", "power": 3800, "cost": 75000, "type": "accessory", "emoji": "👁️", "realm": "God Realm", "tier": "Sacred", "set": "sacred"},

    # Tier 3 - Omnipotent
    "omnipotent_obliterator": {"name": "Omnipotent Obliterator", "power": 6500, "cost": 130000, "type": "weapon", "emoji": "🌠", "realm": "God Realm", "tier": "Omnipotent", "set": "omnipotent"},
    "omnipotent_aegis": {"name": "Omnipotent Aegis", "power": 6000, "cost": 120000, "type": "armor", "emoji": "🛡️", "realm": "God Realm", "tier": "Omnipotent", "set": "omnipotent"},
    "omnipotent_circlet": {"name": "Omnipotent Circlet", "power": 5800, "cost": 115000, "type": "helmet", "emoji": "💎", "realm": "God Realm", "tier": "Omnipotent", "set": "omnipotent"},
    "omnipotent_essence": {"name": "Omnipotent Essence", "power": 5500, "cost": 110000, "type": "accessory", "emoji": "🌟", "realm": "God Realm", "tier": "Omnipotent", "set": "omnipotent"},

    # Tier 4 - Infinite
    "infinite_destroyer": {"name": "Infinite Destroyer", "power": 9000, "cost": 180000, "type": "weapon", "emoji": "♾️", "realm": "God Realm", "tier": "Infinite", "set": "infinite"},
    "infinite_guardian": {"name": "Infinite Guardian", "power": 8500, "cost": 170000, "type": "armor", "emoji": "🔒", "realm": "God Realm", "tier": "Infinite", "set": "infinite"},
    "infinite_diadem": {"name": "Infinite Diadem", "power": 8200, "cost": 165000, "type": "helmet", "emoji": "♾️", "realm": "God Realm", "tier": "Infinite", "set": "infinite"},
    "infinite_core": {"name": "Infinite Core", "power": 8000, "cost": 160000, "type": "accessory", "emoji": "🌌", "realm": "God Realm", "tier": "Infinite", "set": "infinite"},

    # Tier 5 - Absolute
    "absolute_devastator": {"name": "Absolute Devastator", "power": 12000, "cost": 240000, "type": "weapon", "emoji": "💀", "realm": "God Realm", "tier": "Absolute", "set": "absolute"},
    "absolute_bastion": {"name": "Absolute Bastion", "power": 11500, "cost": 230000, "type": "armor", "emoji": "🏯", "realm": "God Realm", "tier": "Absolute", "set": "absolute"},
    "absolute_crown": {"name": "Absolute Crown", "power": 11200, "cost": 225000, "type": "helmet", "emoji": "👑", "realm": "God Realm", "tier": "Absolute", "set": "absolute"},
    "absolute_nucleus": {"name": "Absolute Nucleus", "power": 11000, "cost": 220000, "type": "accessory", "emoji": "⚡", "realm": "God Realm", "tier": "Absolute", "set": "absolute"},

    # Tier 6 - Primordial
    "primordial_chaos": {"name": "Primordial Chaos", "power": 16000, "cost": 320000, "type": "weapon", "emoji": "🌀", "realm": "God Realm", "tier": "Primordial", "set": "primordial"},
    "primordial_genesis": {"name": "Primordial Genesis", "power": 15000, "cost": 300000, "type": "armor", "emoji": "🌌", "realm": "God Realm", "tier": "Primordial", "set": "primordial"},
    "primordial_helm": {"name": "Primordial Helm", "power": 14500, "cost": 290000, "type": "helmet", "emoji": "⭐", "realm": "God Realm", "tier": "Primordial", "set": "primordial"},
    "primordial_core": {"name": "Primordial Core", "power": 14000, "cost": 280000, "type": "accessory", "emoji": "🔮", "realm": "God Realm", "tier": "Primordial", "set": "primordial"},

    # Tier 7 - Creation
    "creation_architect": {"name": "Creation Architect", "power": 22000, "cost": 440000, "type": "weapon", "emoji": "🏗️", "realm": "God Realm", "tier": "Creation", "set": "creation"},
    "creation_sanctuary": {"name": "Creation Sanctuary", "power": 20000, "cost": 400000, "type": "armor", "emoji": "🏛️", "realm": "God Realm", "tier": "Creation", "set": "creation"},
    "creation_aureole": {"name": "Creation Aureole", "power": 19500, "cost": 390000, "type": "helmet", "emoji": "🌟", "realm": "God Realm", "tier": "Creation", "set": "creation"},
    "creation_nexus": {"name": "Creation Nexus", "power": 19000, "cost": 380000, "type": "accessory", "emoji": "🌌", "realm": "God Realm", "tier": "Creation", "set": "creation"},

    # Tier 8 - Universe (Ultimate God Tier)
    "universe_creator": {"name": "Universe Creator", "power": 30000, "cost": 600000, "type": "weapon", "emoji": "🌍", "realm": "God Realm", "tier": "Universe", "set": "universe"},
    "universe_mantle": {"name": "Universe Mantle", "power": 28000, "cost": 560000, "type": "armor", "emoji": "🌌", "realm": "God Realm", "tier": "Universe", "set": "universe"},
    "universe_crown": {"name": "Universe Crown", "power": 27000, "cost": 540000, "type": "helmet", "emoji": "👑", "realm": "God Realm", "tier": "Universe", "set": "universe"},
    "universe_heart": {"name": "Universe Heart", "power": 26000, "cost": 520000, "type": "accessory", "emoji": "💫", "realm": "God Realm", "tier": "Universe", "set": "universe"}
}

# Set bonuses for wearing multiple pieces of same set (now includes 4-piece sets with helmets)
SET_BONUSES = {
    # MORTAL REALM SETS
    "wooden": {"2_piece": 0.10, "3_piece": 0.25, "4_piece": 0.50},
    "cloth": {"2_piece": 0.10, "3_piece": 0.25, "4_piece": 0.50}, 
    "copper": {"2_piece": 0.10, "3_piece": 0.25, "4_piece": 0.50},
    "iron": {"2_piece": 0.15, "3_piece": 0.35, "4_piece": 0.70},
    "leather": {"2_piece": 0.15, "3_piece": 0.35, "4_piece": 0.70},
    "steel": {"2_piece": 0.20, "3_piece": 0.45, "4_piece": 0.90},
    "spirit": {"2_piece": 0.25, "3_piece": 0.55, "4_piece": 1.10},
    "crystal": {"2_piece": 0.30, "3_piece": 0.65, "4_piece": 1.30},
    "jade": {"2_piece": 0.35, "3_piece": 0.75, "4_piece": 1.50},
    "phoenix": {"2_piece": 0.40, "3_piece": 0.85, "4_piece": 1.70},
    "dragon": {"2_piece": 0.50, "3_piece": 1.00, "4_piece": 2.00},
    
    # IMMORTAL REALM SETS
    "celestial": {"2_piece": 0.60, "3_piece": 1.20, "4_piece": 2.40},
    "void": {"2_piece": 0.70, "3_piece": 1.40, "4_piece": 2.80},
    "profound": {"2_piece": 0.80, "3_piece": 1.60, "4_piece": 3.20},
    "stellar": {"2_piece": 0.90, "3_piece": 1.80, "4_piece": 3.60},
    "cosmic": {"2_piece": 1.00, "3_piece": 2.00, "4_piece": 4.00},
    "eternal": {"2_piece": 1.20, "3_piece": 2.40, "4_piece": 4.80},
    "transcendent": {"2_piece": 1.40, "3_piece": 2.80, "4_piece": 5.60},
    "immortal": {"2_piece": 1.60, "3_piece": 3.20, "4_piece": 6.40},
    
    # GOD REALM SETS
    "divine": {"2_piece": 2.00, "3_piece": 4.00, "4_piece": 8.00},
    "sacred": {"2_piece": 2.50, "3_piece": 5.00, "4_piece": 10.00},
    "omnipotent": {"2_piece": 3.00, "3_piece": 6.00, "4_piece": 12.00},
    "infinite": {"2_piece": 3.50, "3_piece": 7.00, "4_piece": 14.00},
    "absolute": {"2_piece": 4.00, "3_piece": 8.00, "4_piece": 16.00},
    "primordial": {"2_piece": 5.00, "3_piece": 10.00, "4_piece": 20.00},
    "creation": {"2_piece": 6.00, "3_piece": 12.00, "4_piece": 24.00},
    "universe": {"2_piece": 8.00, "3_piece": 16.00, "4_piece": 32.00}
}

# ===============================
# Dungeon System - DIPERLUAS
# ===============================
DUNGEONS = {
    "forest": {
        "name": "Spirit Forest",
        "min_level": 1,
        "max_level": 10,
        "min_reward": 8000,  # 10x from 800
        "max_reward": 15000,  # 10x from 1500
        "spirit_stone_reward": (1, 3),
        "emoji": "🌳",
        "difficulty": "Easy",
        "description": "A peaceful forest filled with low-level spirit beasts"
    },
    "cave": {
        "name": "Ancient Cave", 
        "min_level": 5,
        "max_level": 20,
        "min_reward": 25000,  # 10x from 2500
        "max_reward": 40000,  # 10x from 4000
        "spirit_stone_reward": (2, 5),
        "emoji": "🕳️",
        "difficulty": "Medium",
        "description": "Dark caves with ancient treasures and dangers"
    },
    "mountain": {
        "name": "Celestial Mountain",
        "min_level": 15,
        "max_level": 30,
        "min_reward": 80000,  # 10x from 8000
        "max_reward": 120000,  # 10x from 12000
        "spirit_stone_reward": (3, 8),
        "emoji": "⛰️",
        "difficulty": "Hard",
        "description": "A sacred mountain with powerful guardians"
    },
    "abyss": {
        "name": "Demon Abyss",
        "min_level": 25,
        "max_level": 50,
        "min_reward": 150000,  # 10x from 15000
        "max_reward": 200000,  # 10x from 20000
        "spirit_stone_reward": (5, 15),
        "emoji": "🔥",
        "difficulty": "Very Hard",
        "description": "A dangerous abyss filled with demonic creatures"
    },
    "palace": {
        "name": "Heavenly Palace",
        "min_level": 40,
        "max_level": 80,
        "min_reward": 250000,  # 10x from 25000
        "max_reward": 300000,  # 10x from 30000
        "spirit_stone_reward": (10, 25),
        "emoji": "🏯",
        "difficulty": "Extreme",
        "description": "The celestial palace of immortals"
    },
    "forbidden_realm": {
        "name": "Forbidden Realm",
        "min_level": 60,
        "max_level": 100,
        "min_reward": 400000,
        "max_reward": 600000,
        "spirit_stone_reward": (20, 40),
        "emoji": "🚫",
        "difficulty": "Nightmare",
        "description": "Forbidden realm where ancient evils slumber"
    },
    "void_dimension": {
        "name": "Void Dimension",
        "min_level": 80,
        "max_level": 120,
        "min_reward": 700000,
        "max_reward": 1000000,
        "spirit_stone_reward": (30, 60),
        "emoji": "🌌",
        "difficulty": "Impossible",
        "description": "Dimension of nothingness where reality breaks down"
    },
    "cosmic_labyrinth": {
        "name": "Cosmic Labyrinth",
        "min_level": 100,
        "max_level": 150,
        "min_reward": 1200000,
        "max_reward": 1800000,
        "spirit_stone_reward": (50, 100),
        "emoji": "🌠",
        "difficulty": "Transcendent",
        "description": "Infinite labyrinth that spans across galaxies"
    },
    "primordial_depths": {
        "name": "Primordial Depths",
        "min_level": 120,
        "max_level": 200,
        "min_reward": 2000000,
        "max_reward": 3000000,
        "spirit_stone_reward": (80, 150),
        "emoji": "⚫",
        "difficulty": "Primordial",
        "description": "The deepest depths where creation itself began"
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

    # Apply NPC combat assistance if available
    attacker_power = attacker["total_power"]
    defender_power = defender["total_power"]
    
    attacker_assistant = None
    defender_assistant = None
    
    if NPC_SYSTEM_LOADED:
        # Check for combat assistants
        attacker_assistant_id = get_player_combat_assistant(attacker_id)
        defender_assistant_id = get_player_combat_assistant(defender_id)
        
        if attacker_assistant_id and can_use_npc_assistant(attacker_id, attacker_assistant_id):
            from npc_system import get_npc_data
            attacker_npc_data = get_npc_data(str(attacker_id), attacker_assistant_id)
            attacker_bonuses = apply_npc_combat_assistance(attacker, attacker_npc_data['specialty'])
            attacker_power = attacker_bonuses['enhanced_power']
            attacker_assistant = attacker_npc_data['name']
        
        if defender_assistant_id and can_use_npc_assistant(defender_id, defender_assistant_id):
            from npc_system import get_npc_data
            defender_npc_data = get_npc_data(str(defender_id), defender_assistant_id)
            defender_bonuses = apply_npc_combat_assistance(defender, defender_npc_data['specialty'])
            defender_power = defender_bonuses['enhanced_power']
            defender_assistant = defender_npc_data['name']

    # Setup battle data
    ACTIVE_BATTLES[battle_id] = {
        "attacker": attacker_id,
        "defender": defender_id,
        "attacker_hp": 100,
        "defender_hp": 100,
        "attacker_power": attacker_power,
        "defender_power": defender_power,
        "attacker_assistant": attacker_assistant,
        "defender_assistant": defender_assistant,
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
    
    attacker_power_text = f"{attacker_power:,}"
    if attacker_assistant:
        attacker_power_text += f"\n🤝 **Assistant:** {attacker_assistant}"
    
    defender_power_text = f"{defender_power:,}"
    if defender_assistant:
        defender_power_text += f"\n🤝 **Assistant:** {defender_assistant}"
    
    embed.add_field(name="Attacker Power", value=attacker_power_text, inline=True)
    embed.add_field(name="Defender Power", value=defender_power_text, inline=True)
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
    if user_id not in ACTIVE_CULTIVATIONS or player_data is None:
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
    if p is None:
        if user_id in ACTIVE_CULTIVATIONS:
            del ACTIVE_CULTIVATIONS[user_id]
        return

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
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)  # Disable built-in help

# ===============================
# Event handlers
# ===============================
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} telah online!')
    print(f'🔑 Token valid: {bool(BOT_TOKEN)}')
    
    # Safe data loading
    try:
        data = load_data()
        total_players = data.get("total_players", 0) if data else 0
        print(f'📊 Total players: {total_players}')
    except:
        print(f'📊 Total players: 0 (data loading error)')

    if BOT_TOKEN and BOT_TOKEN != "placeholder_token_untuk_development":
        print(f'🔒 Token length: {len(BOT_TOKEN)}')

    # Reset daily quests jika perlu
    try:
        reset_daily_quests()
    except Exception as e:
        print(f"Warning: Daily quest reset failed: {e}")

    try:
        backup_data()
    except Exception as e:
        print(f"Warning: Backup failed: {e}")
    
    # Start world boss tasks jika system loaded
    if WORLD_BOSS_SYSTEM_LOADED:
        try:
            asyncio.create_task(start_world_boss_tasks())
            print("🌍 World Boss tasks started!")
        except Exception as e:
            print(f"Warning: World Boss tasks failed: {e}")
    
    print('✅ AI Exploration system loaded successfully!')
    print('✅ Boss system loaded successfully!')
    print('✅ World Boss system loaded successfully!')
    print('🌟 Bot siap menerima command!')

#================================
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
# AI-DRIVEN EXPLORATION SYSTEM - FULLY DYNAMIC
# ===============================

import aiohttp
import json
import re

# Hugging Face API Setup
HF_TOKEN = os.environ.get("HUGGING_FACE_TOKEN", "")
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"

async def query_huggingface_api(prompt, max_length=200):
    """Query Hugging Face API for text generation (non-blocking)"""
    if not HF_TOKEN:
        return "AI is currently unavailable."
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": max_length,
            "temperature": 0.9,
            "do_sample": True,
            "top_p": 0.9
        }
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(HF_API_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated = result[0].get("generated_text", "")
                        return generated.replace(prompt, "").strip()
                return f"API Error: {response.status}"
    except asyncio.TimeoutError:
        return "AI timeout - generating fallback scenario..."
    except Exception as e:
        return f"AI Error: {str(e)[:50]}..."

def parse_ai_response(response):
    """Parse AI response to extract scenario and choices"""
    try:
        # Extract scenario description
        scenario_match = re.search(r"SCENARIO:(.*?)CHOICES:", response, re.DOTALL)
        scenario = scenario_match.group(1).strip() if scenario_match else response[:200]
        
        # Extract choices
        choices_match = re.search(r"CHOICES:(.*)", response, re.DOTALL)
        choices_text = choices_match.group(1) if choices_match else ""
        
        choices = []
        for i, line in enumerate(choices_text.split('\n')[:3], 1):
            if line.strip():
                choices.append({
                    "number": i,
                    "text": line.strip()[:100],  # Limit choice length
                    "emoji": ["🗡️", "🛡️", "🏃‍♂️"][i-1]
                })
        
        # Ensure we have at least 3 choices
        while len(choices) < 3:
            defaults = [
                {"number": 1, "text": "Attack with full power", "emoji": "🗡️"},
                {"number": 2, "text": "Defend and observe", "emoji": "🛡️"},
                {"number": 3, "text": "Retreat carefully", "emoji": "🏃‍♂️"}
            ]
            choices.append(defaults[len(choices)])
        
        return scenario, choices[:3]
    except:
        # Fallback if parsing fails
        return response[:200], [
            {"number": 1, "text": "Face the challenge head-on", "emoji": "🗡️"},
            {"number": 2, "text": "Proceed with caution", "emoji": "🛡️"}, 
            {"number": 3, "text": "Look for alternative path", "emoji": "🏃‍♂️"}
        ]

def calculate_exploration_outcome(choice_num, player_power, scenario_difficulty):
    """Calculate outcome based on AI choice and player stats"""
    import random
    
    # Base success rate depends on player power vs scenario difficulty
    base_success = min(85, 30 + (player_power // 100))
    
    # Choice modifiers
    choice_modifiers = {1: -10, 2: 0, 3: 5}  # Aggressive, Balanced, Cautious
    success_rate = base_success + choice_modifiers.get(choice_num, 0)
    
    success = random.randint(1, 100) <= success_rate
    
    # Calculate rewards/penalties
    if success:
        exp_base = random.randint(10000, 50000) * (scenario_difficulty // 10)
        qi_base = random.randint(100, 500) * (scenario_difficulty // 10)
        stones_base = random.randint(5, 25) * (scenario_difficulty // 10)
        health_change = random.randint(-5, 10)
        
        return {
            "success": True,
            "exp": exp_base,
            "qi": qi_base,
            "spirit_stones": stones_base,
            "health_change": health_change,
            "continue": True
        }
    else:
        # Failure - potential damage/loss
        health_loss = random.randint(10, 30)
        exp_loss = random.randint(1000, 5000)
        
        return {
            "success": False,
            "exp": -exp_loss,
            "qi": 0,
            "spirit_stones": 0,
            "health_change": -health_loss,
            "continue": True
        }

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)  # 1 minute cooldown
async def explore(ctx):
    """Start an AI-driven cultivation adventure that continues until death or stop!"""
    user_id = ctx.author.id
    p = get_player(user_id)
    
    if user_id in ACTIVE_EXPLORATIONS:
        return await ctx.send("⏳ You're already on an adventure! Use `!stop_explore` to end it.")
    
    if not HF_TOKEN:
        return await ctx.send("❌ AI exploration system is unavailable. Missing API token.")
    
    # Initialize exploration health if not exists
    if p is None:
        return await ctx.send("❌ Player not found! Use `!register` first.")
    if "exploration_health" not in p or p["exploration_health"] is None:
        p["exploration_health"] = 100
    
    player_level = get_player_level(p)
    player_realm = p["realm"]
    player_power = p["total_power"]
    
    # Start AI-driven exploration
    initial_prompt = f"""You are creating a cultivation adventure for a {player_realm} realm cultivator at level {player_level} with {player_power} power. 

Create an unpredictable, dangerous scenario in a cultivation world. Include mystical elements, potential treasures, spirit beasts, or ancient ruins. Make it immersive and atmospheric.

SCENARIO: [Describe the situation in 1-2 sentences]
CHOICES:
1. [Aggressive/risky action]
2. [Balanced/careful action] 
3. [Defensive/retreat action]

Keep responses under 150 words total."""

    await ctx.send("🧠 The AI is weaving your destiny...")
    
    try:
        ai_response = await query_huggingface_api(initial_prompt, max_length=200)
        scenario_text, choices = parse_ai_response(ai_response)
        
        # Calculate scenario difficulty based on player level
        scenario_difficulty = random.randint(max(1, player_level - 5), player_level + 10)
        
        # Create initial exploration embed
        embed = discord.Embed(
            title="🌌 AI-Driven Cultivation Adventure",
            description=f"**Health:** {p['exploration_health']}/100 ❤️\n\n{scenario_text}",
            color=0x00ff00
        )
        
        choice_text = ""
        for choice in choices:
            choice_text += f"{choice['number']}️⃣ {choice['emoji']} {choice['text']}\n"
        
        embed.add_field(name="Your Options:", value=choice_text, inline=False)
        embed.set_footer(text="React with 1️⃣2️⃣3️⃣ to choose or ❌ to stop exploring")
        
        message = await ctx.send(embed=embed)
        
        # Add reactions
        emojis = ['1️⃣', '2️⃣', '3️⃣', '❌']
        for emoji in emojis:
            await message.add_reaction(emoji)
        
        # Store exploration state
        ACTIVE_EXPLORATIONS[user_id] = {
            "message": message,
            "scenario": scenario_text,
            "choices": choices,
            "difficulty": scenario_difficulty,
            "turn": 1,
            "active": True,
            "start_time": time.time(),
            "story_context": [scenario_text]  # Track story for continuity
        }
        
        # Start the exploration loop
        await continue_exploration(ctx, user_id)
        
    except Exception as e:
        await ctx.send(f"❌ Error starting AI adventure: {str(e)}")

async def continue_exploration(ctx, user_id):
    """Continue the AI-driven exploration based on player choice"""
    if user_id not in ACTIVE_EXPLORATIONS:
        return
    
    exploration = ACTIVE_EXPLORATIONS[user_id]
    message = exploration["message"]
    
    def check(reaction, user):
        return (user.id == user_id and 
                str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '❌'] and 
                reaction.message.id == message.id)
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=300.0, check=check)
        
        if str(reaction.emoji) == '❌':
            # Player chooses to stop
            del ACTIVE_EXPLORATIONS[user_id]
            embed = discord.Embed(
                title="🏠 Adventure Ended",
                description="You decide to return safely from your exploration.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            return
        
        # Get player choice
        choice_map = {'1️⃣': 1, '2️⃣': 2, '3️⃣': 3}
        choice_num = choice_map.get(str(reaction.emoji))
        
        if choice_num:
            p = get_player(user_id)
            if p is None:
                del ACTIVE_EXPLORATIONS[user_id]
                return
            
            # Calculate outcome
            outcome = calculate_exploration_outcome(choice_num, p["total_power"], exploration["difficulty"])
            
            # Apply health change
            p["exploration_health"] = max(0, min(100, p["exploration_health"] + outcome["health_change"]))
            
            # Check for death
            if p["exploration_health"] <= 0:
                # DEATH - End exploration
                del ACTIVE_EXPLORATIONS[user_id]
                p["exploration_health"] = 100  # Reset for next time
                
                embed = discord.Embed(
                    title="💀 Death in the Wilderness",
                    description=f"Your cultivation journey ends here. You died during exploration but will be revived.\n\n"
                               f"**Final Stats:**\nTurns Survived: {exploration['turn']}\nDifficulty: {exploration['difficulty']}",
                    color=0xff0000
                )
                update_player(user_id, p)
                await ctx.send(embed=embed)
                return
            
            # Apply rewards/penalties
            if outcome["success"]:
                p["exp"] = min(p["exp"] + outcome["exp"], get_exp_cap(p))
                p["qi"] += outcome["qi"]
                p["spirit_stones"] += outcome["spirit_stones"]
            else:
                p["exp"] = max(0, p["exp"] + outcome["exp"])  # EXP can be negative
            
            update_player(user_id, p)
            
            # Generate next scenario using AI
            selected_choice = exploration["choices"][choice_num - 1]
            story_context = " ".join(exploration["story_context"][-2:])  # Last 2 story beats
            
            next_prompt = f"""Continue this cultivation adventure story:
Previous context: {story_context}
Player chose: {selected_choice['text']}
Result: {'Success' if outcome['success'] else 'Failure/Danger'}
Current health: {p['exploration_health']}/100

Create the next unpredictable scenario. The adventure continues to escalate. Include new dangers, discoveries, or mysterious encounters.

SCENARIO: [What happens next in 1-2 sentences]
CHOICES:
1. [New aggressive action]
2. [New careful action]
3. [New defensive action]

Keep under 150 words."""

            await ctx.send("🎲 The AI is determining your fate...")
            
            ai_response = await query_huggingface_api(next_prompt, max_length=200)
            
            # Fallback if AI fails
            if "Error" in ai_response or "timeout" in ai_response.lower():
                fallback_scenarios = [
                    f"You continue deeper into the mystical realm. Strange energies pulse around you as you encounter a {['ancient shrine', 'spiritual vortex', 'hidden treasure'][random.randint(0,2)]}.",
                    f"The cultivation world reveals new challenges. A {['powerful spirit beast', 'mysterious cultivator', 'dangerous formation'][random.randint(0,2)]} appears before you.",
                    f"Your journey leads to a crossroads. The path ahead splits toward {['danger and glory', 'mystery and power', 'wisdom and peril'][random.randint(0,2)]}."
                ]
                ai_response = f"SCENARIO: {random.choice(fallback_scenarios)} CHOICES:\n1. Face it with determination\n2. Approach with caution\n3. Seek alternative route"
            
            next_scenario, next_choices = parse_ai_response(ai_response)
            
            # Create result embed
            result_color = 0x00ff00 if outcome["success"] else 0xff6600
            result_title = "✅ Success!" if outcome["success"] else "⚠️ Danger!"
            
            result_embed = discord.Embed(
                title=result_title,
                description=f"**Choice:** {selected_choice['text']}\n\n"
                           f"**Health:** {p['exploration_health']}/100 ❤️\n"
                           f"**EXP:** {outcome['exp']:+,} | **Qi:** {outcome['qi']:+,} | **Stones:** {outcome['spirit_stones']:+,}",
                color=result_color
            )
            await ctx.send(embed=result_embed)
            
            # Continue with next scenario
            next_embed = discord.Embed(
                title=f"🌌 Adventure Continues - Turn {exploration['turn'] + 1}",
                description=f"**Health:** {p['exploration_health']}/100 ❤️\n\n{next_scenario}",
                color=0x00ff00
            )
            
            next_choice_text = ""
            for choice in next_choices:
                next_choice_text += f"{choice['number']}️⃣ {choice['emoji']} {choice['text']}\n"
            
            next_embed.add_field(name="Your Options:", value=next_choice_text, inline=False)
            next_embed.set_footer(text="React with 1️⃣2️⃣3️⃣ to choose or ❌ to stop")
            
            next_message = await ctx.send(embed=next_embed)
            
            # Add reactions to new message
            for emoji in ['1️⃣', '2️⃣', '3️⃣', '❌']:
                await next_message.add_reaction(emoji)
            
            # Update exploration state
            exploration["message"] = next_message
            exploration["scenario"] = next_scenario
            exploration["choices"] = next_choices
            exploration["turn"] += 1
            exploration["difficulty"] += random.randint(1, 3)  # Escalating difficulty
            exploration["story_context"].append(next_scenario)
            
            # Keep story context manageable
            if len(exploration["story_context"]) > 5:
                exploration["story_context"] = exploration["story_context"][-3:]
            
            # Continue the loop
            await continue_exploration(ctx, user_id)
        
    except asyncio.TimeoutError:
        # Timeout - end exploration
        if user_id in ACTIVE_EXPLORATIONS:
            del ACTIVE_EXPLORATIONS[user_id]
        await ctx.send("⏰ Your adventure times out. You return safely from the wilderness.")

@bot.command()
async def stop_explore(ctx):
    """Stop your current AI-driven exploration"""
    user_id = ctx.author.id
    
    if user_id in ACTIVE_EXPLORATIONS:
        turns = ACTIVE_EXPLORATIONS[user_id].get("turn", 1)
        del ACTIVE_EXPLORATIONS[user_id]
        
        embed = discord.Embed(
            title="🏠 Exploration Ended",
            description=f"You safely return from your AI-driven adventure.\n**Turns Survived:** {turns}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ You're not currently exploring!")

# Global exploration tracking
ACTIVE_EXPLORATIONS = {}
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
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk mulai.")
        
    cultivation_data = ACTIVE_CULTIVATIONS[ctx.author.id]
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
    if p is None:
        return await ctx.send("❌ Anda belum terdaftar!")
        
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
# WORLD BOSS COMMANDS
# ===============================
if WORLD_BOSS_SYSTEM_LOADED:

    @bot.command(name="world")
    async def world_cmd(ctx):
        """Lihat status semua World Boss"""
        await world_boss_status(ctx)

    @bot.command(name="createparty")
    async def create_party_cmd(ctx, *, party_name: str):
        """Buat party untuk lawan World Boss"""
        await create_party(ctx, party_name)

    @bot.command(name="inviteparty")
    async def invite_party_cmd(ctx, member: discord.Member):
        """Invite member ke party"""
        await invite_party(ctx, member)

    @bot.command(name="joinparty")
    async def join_party_cmd(ctx, *, party_name: str):
        """Join party yang sudah ada"""
        await join_party(ctx, party_name)

    @bot.command(name="leaveparty")
    async def leave_party_cmd(ctx):
        """Keluar dari party"""
        await leave_party(ctx)

    @bot.command(name="partyinfo")
    async def party_info_cmd(ctx):
        """Lihat info party"""
        await party_info(ctx)

    @bot.command(name="challengeboss")
    async def challenge_boss_cmd(ctx, *, boss_name: str):
        """Tantang World Boss (hanya leader yang bisa)"""
        await challenge_world_boss(ctx, boss_name)

# ================================
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
        [(uid, data) for uid, data in players.items() if data is not None],
        key=lambda x: x[1].get("total_power", 0),
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
        [(uid, data) for uid, data in players.items() if data is not None],
        key=lambda x: x[1].get("total_power", 0),
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
        [(uid, data) for uid, data in players.items() if data is not None],
        key=lambda x: (x[1].get("pvp_wins", 0), -x[1].get("pvp_losses", 0)),
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
        [(uid, data) for uid, data in players.items() if data is not None],
        key=lambda x: x[1].get("total_power", 0),
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
# Command: my_beasts (MISSING COMMAND)
# ===============================
@bot.command()
async def my_beasts(ctx):
    """View all your tamed spirit beasts"""
    p = get_player(ctx.author.id)
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` untuk memulai.")

    if not p.get("spirit_beasts"):
        return await ctx.send("❌ Anda belum menjinakkan spirit beast apapun! Gunakan `!spirit_beasts` untuk melihat yang tersedia.")

    embed = discord.Embed(
        title=f"🐉 {ctx.author.name}'s Spirit Beast Collection",
        description="All your tamed spirit beasts:",
        color=0x00ff00
    )

    current_beast = p.get("current_beast")
    total_power_bonus = 0

    for beast in p["spirit_beasts"]:
        status = "✅ **ACTIVE**" if current_beast == beast["name"] else "💤 Inactive"
        bonus_text = ", ".join([f"+{int(v*100)}% {k}" for k, v in beast["bonus"].items()])
        total_power_bonus += beast["power"]

        embed.add_field(
            name=f"{beast['emoji']} {beast['name']} ({status})",
            value=f"**Power:** +{beast['power']} | **Bonus:** {bonus_text}",
            inline=False
        )

    embed.add_field(
        name="📊 Collection Stats",
        value=f"**Total Beasts:** {len(p['spirit_beasts'])}\n**Total Power Bonus:** +{total_power_bonus}\n**Active Beast:** {current_beast or 'None'}",
        inline=False
    )

    embed.set_footer(text="Use !set_beast \"beast_name\" to change active beast")
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
# COMPREHENSIVE HELP SYSTEM - FULLY UPDATED
# ===============================
# Remove default help command first
bot.remove_command('help')

@bot.command(name='help')
async def help_command(ctx, category: str = None):
    """Show comprehensive help for the Cultivation RPG Bot"""

    if category is None:
        # Main help menu
        embed = discord.Embed(
            title="🌟 Cultivation RPG Bot - Complete Guide",
            description="🎊 **MASSIVE UPDATE!** Master the way of cultivation with 50 NPCs, 15 sects, artifacts, formations, and treasure hunts!\n\n🚀 **From mortal to god - build your empire of power!**",
            color=0x7289da
        )
        
        embed.add_field(
            name="🎯 **Core Cultivation**",
            value="`!help core` - Registration, cultivation, breakthrough, profiles",
            inline=False
        )
        
        embed.add_field(
            name="⚔️ **Combat & PvP**",
            value="`!help combat` - Battle, PvP, world bosses, NPC combat assistants",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Equipment & Items**",
            value="`!help equipment` - 96 items across all realms, weapons, armor, helmets",
            inline=False
        )
        
        embed.add_field(
            name="🌸 **NPCs & Relationships**", 
            value="`!help npcs` - 50 unique NPCs, affection system, combat assistance at 60%+",
            inline=False
        )
        
        embed.add_field(
            name="🏛️ **Sects & Techniques**",
            value="`!help sects` - 15 sects with unique techniques, realm-based progression",
            inline=False
        )
        
        embed.add_field(
            name="🏺 **Advanced Systems**",
            value="`!help advanced` - Artifacts, formations, treasure hunts, enlightenment events",
            inline=False
        )
        
        embed.add_field(
            name="📚 **All Commands**",
            value="`!help commands` - Complete command reference (50+ commands!)",
            inline=False
        )
        
        embed.add_field(
            name="🌟 **Quick Start Guide**",
            value="1️⃣ `!register` - Begin your journey\n2️⃣ `!cultivate` - Build power\n3️⃣ `!shop` - Get equipment\n4️⃣ `!npc_list` - Meet NPCs\n5️⃣ `!sect_list` - Join a sect\n6️⃣ `!treasure_hunt` - Find artifacts!",
            inline=False
        )
        
        embed.set_footer(text="🎮 Use !help <category> to see detailed information | 🎊 Featuring 50 NPCs, 15 sects, 96 items, and epic adventures!")

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

    elif category.lower() == "core":
        embed = discord.Embed(
            title="🎯 Core Cultivation Commands",
            description="Essential commands for your cultivation journey from Mortal to God Realm",
            color=0x00ff00
        )
        
        embed.add_field(
            name="🌱 **Getting Started**",
            value="`!register` - Start your cultivation journey\n`!profile` - View your cultivation status and power\n`!leaderboard` - See top cultivators across all realms",
            inline=False
        )
        
        embed.add_field(
            name="⚡ **Cultivation & Advancement**",
            value="`!cultivate` - Improve your power and qi (chance for enlightenment!)\n`!breakthrough` - Advance to next cultivation stage\n`!daily` - Claim daily rewards and bonuses",
            inline=False
        )
        
        embed.add_field(
            name="💰 **Economy & Resources**",
            value="`!work` - Earn spirit stones through various jobs\n`!shop [realm]` - Browse equipment by realm\n`!inventory` - View your items and equipment",
            inline=False
        )

    elif category.lower() == "combat":
        embed = discord.Embed(
            title="⚔️ Combat & PvP Commands", 
            description="Advanced battle systems with NPC assistance and epic boss fights",
            color=0xff0000
        )
        
        embed.add_field(
            name="🥊 **Player vs Player**",
            value="`!duel @user` - Challenge another cultivator to battle\n`!accept` - Accept a duel invitation\n`!decline` - Decline a duel invitation",
            inline=False
        )
        
        embed.add_field(
            name="🐉 **Epic Boss Battles**",
            value="`!boss` - Fight the current world boss for massive rewards\n`!boss_info` - View boss details, health, and loot table",
            inline=False
        )
        
        embed.add_field(
            name="🤝 **NPC Combat Assistance**",
            value="`!set_assistant <npc>` - Set NPC as combat assistant (60% affection required)\n`!assistant_info` - View current assistant and their bonuses\n`!available_assistants` - See all eligible NPC assistants\n`!remove_assistant` - Remove current combat assistant",
            inline=False
        )

    elif category.lower() == "npcs":
        embed = discord.Embed(
            title="🌸 NPCs & Relationship System",
            description="50 unique NPCs with complex personalities and exclusive soulmate mechanics",
            color=0xff69b4
        )
        
        embed.add_field(
            name="💕 **Building Relationships**",
            value="`!talk <npc>` - Have AI-driven conversations with NPCs\n`!gift <npc> <item>` - Give gifts to increase affection\n`!npc_info <npc>` - View detailed NPC information and preferences",
            inline=False
        )
        
        embed.add_field(
            name="👥 **NPC Discovery & Management**",
            value="`!npc_list [realm]` - Browse NPCs by cultivation realm\n`!npcs` - View all 50 available NPCs\n`!my_relationships` - See all your affection levels and statuses",
            inline=False
        )
        
        embed.add_field(
            name="💖 **Exclusive Soulmate System**",
            value="**🔒 EXCLUSIVE RELATIONSHIPS**: Only ONE NPC can reach 100% affection (soulmate status)\n**⚖️ Affection Cap**: When you have a soulmate, all others are capped at 80%\n**💔 Strategic Choice**: Choose your soulmate wisely - it affects all other relationships!",
            inline=False
        )

    elif category.lower() == "sects":
        embed = discord.Embed(
            title="🏛️ Sects & Technique System",
            description="15 comprehensive sects across 3 realms with unique techniques and progression",
            color=0x9400d3
        )
        
        embed.add_field(
            name="🌟 **Sect Management**",
            value="`!sect_list [realm]` - Browse sects by realm (5 per realm)\n`!join_sect <name>` - Join a cultivation sect\n`!my_sect` - View your sect status, techniques, and bonuses",
            inline=False
        )
        
        embed.add_field(
            name="📚 **Technique Mastery**",
            value="`!learn_sect_technique <name>` - Master sect techniques with spirit stones\n`!sect_info <name>` - View detailed sect information and requirements\n`!leave_sect` - Leave current sect (⚠️ loses all techniques!)",
            inline=False
        )

    elif category.lower() == "advanced":
        embed = discord.Embed(
            title="🏺 Advanced Game Systems",
            description="4 exciting endgame systems for solo and group activities",
            color=0xffd700
        )
        
        embed.add_field(
            name="🏺 **Artifact System**",
            value="`!artifacts` - View your artifact collection and available artifacts\n`!activate_artifact <name>` - Use special artifact powers with cooldowns\n**9 Legendary Artifacts**: Powerful items with unique abilities across all realms",
            inline=False
        )
        
        embed.add_field(
            name="🗺️ **Treasure Hunt Expeditions**",
            value="`!treasure_hunt [location]` - Explore 4 dangerous locations\n`!check_hunt` - Monitor expedition progress and collect rewards\n**Risk vs Reward**: Higher difficulty = better artifacts and enlightenment chances",
            inline=False
        )
        
        embed.add_field(
            name="✨ **Cultivation Formations**",
            value="`!formations` - View formation types and requirements\n`!create_formation <name>` - Start group cultivation sessions\n`!join_formation <name>` - Join active formations\n`!active_formations` - See all recruiting and active formations",
            inline=False
        )

    elif category.lower() == "commands":
        embed = discord.Embed(
            title="📚 Complete Command Reference",
            description="All 50+ commands organized by category for easy reference",
            color=0x7289da
        )
        
        embed.add_field(
            name="🎯 **Core Cultivation (12 commands)**",
            value="`!register`, `!profile`, `!cultivate`, `!breakthrough`, `!daily`, `!work`, `!shop`, `!buy`, `!sell`, `!inventory`, `!stats`, `!leaderboard`",
            inline=False
        )
        
        embed.add_field(
            name="⚔️ **Combat Systems (8 commands)**", 
            value="`!duel`, `!accept`, `!decline`, `!boss`, `!boss_info`, `!set_assistant`, `!assistant_info`, `!available_assistants`, `!remove_assistant`",
            inline=False
        )
        
        embed.add_field(
            name="🌸 **NPC Relationships (10 commands)**",
            value="`!talk`, `!gift`, `!npc_info`, `!npc_list`, `!npcs`, `!my_relationships`, `!set_assistant`, `!remove_assistant`, `!assistant_info`, `!available_assistants`",
            inline=False
        )
        
        embed.add_field(
            name="🏛️ **Sect Management (6 commands)**",
            value="`!sect_list`, `!join_sect`, `!leave_sect`, `!my_sect`, `!learn_sect_technique`, `!sect_info`",
            inline=False
        )
        
        embed.add_field(
            name="🏺 **Advanced Systems (10 commands)**",
            value="`!artifacts`, `!activate_artifact`, `!treasure_hunt`, `!check_hunt`, `!formations`, `!create_formation`, `!join_formation`, `!active_formations`",
            inline=False
        )

    else:
        embed = discord.Embed(
            title="❌ Unknown Help Category",
            description="**Available categories:**\n`core`, `combat`, `npcs`, `sects`, `advanced`, `commands`\n\nUse `!help` to see the main help menu.",
            color=0xff0000
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
# NPC INTERACTION COMMANDS - AI-DRIVEN
# ===============================

@bot.command(name="npcs")
async def npcs_command(ctx):
    """Alias for npc_list - shows all NPCs"""
    await npc_list(ctx)

@bot.command(name="my_relationships")
async def my_relationships(ctx):
    """View all your NPC relationships"""
    if not NPC_SYSTEM_LOADED:
        return await ctx.send("❌ NPC system is not available!")
    
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    embed = discord.Embed(
        title=f"💕 {ctx.author.name}'s NPC Relationships",
        description="Your relationships with all NPCs you've interacted with:",
        color=0xff69b4
    )
    
    # Get all NPCs the player has interacted with
    from npc_system import NPC_INTERACTIONS, get_npc_data
    
    if player_id not in NPC_INTERACTIONS or not NPC_INTERACTIONS[player_id]:
        return await ctx.send("❌ You haven't interacted with any NPCs yet! Use `!npc_list` to see available NPCs.")
    
    relationships = []
    combat_assistants = []
    soulmates = []
    
    for npc_id in NPC_INTERACTIONS[player_id]:
        npc_data = get_npc_data(player_id, npc_id)
        affection = npc_data['affection_level']
        
        # Categorize relationships
        if affection >= 100:
            soulmates.append(npc_data)
        elif affection >= 60:
            combat_assistants.append(npc_data)
        
        hearts = "💖" * (affection // 20)
        empty_hearts = "🤍" * (5 - (affection // 20))
        affection_bar = hearts + empty_hearts
        
        relationships.append((affection, f"{npc_data['emoji']} **{npc_data['name']}** - {affection_bar} {affection}/100 ({npc_data['relationship_status']})"))
    
    # Sort by affection level (highest first)
    relationships.sort(key=lambda x: x[0], reverse=True)
    
    # Show top relationships
    if relationships:
        relationship_text = "\n".join([rel[1] for rel in relationships[:15]])  # Show top 15
        embed.add_field(
            name="📊 All Relationships",
            value=relationship_text,
            inline=False
        )
    
    # Show special categories
    if soulmates:
        embed.add_field(
            name="💖 Soulmates (100%)",
            value=f"{soulmates[0]['emoji']} **{soulmates[0]['name']}** - Exclusive bond!",
            inline=True
        )
    
    if combat_assistants:
        assistant_list = "\n".join([f"{npc['emoji']} {npc['name']}" for npc in combat_assistants[:5]])
        embed.add_field(
            name="⚔️ Combat Assistants Available (60%+)",
            value=assistant_list,
            inline=True
        )
    
    # Current assistant
    current_assistant = get_player_combat_assistant(player_id)
    if current_assistant and current_assistant in NPCS:
        embed.add_field(
            name="🤝 Current Combat Assistant",
            value=f"{NPCS[current_assistant]['emoji']} **{NPCS[current_assistant]['name']}**",
            inline=True
        )
    
    stats_text = f"**Total NPCs Met:** {len(relationships)}\n**Combat Ready:** {len(combat_assistants)}\n**Soulmates:** {len(soulmates)}"
    embed.add_field(name="📈 Relationship Stats", value=stats_text, inline=False)
    
    await ctx.send(embed=embed)
@bot.command(name="npc_list")
async def npc_list(ctx):
    """List all available NPCs"""
    if not NPC_SYSTEM_LOADED:
        return await ctx.send("❌ NPC system is not available!")
    
    embed = discord.Embed(
        title="🧑‍🤝‍🧑 Available NPCs", 
        description="Interact with these AI-driven cultivator NPCs!",
        color=0x9932cc
    )
    
    male_npcs = []
    female_npcs = []
    
    for npc_id, npc in NPCS.items():
        npc_info = f"{npc['emoji']} **{npc['name']}** - {npc['realm']} ({npc['specialty']})"
        if npc['gender'] == 'male':
            male_npcs.append(npc_info)
        else:
            female_npcs.append(npc_info)
    
    embed.add_field(name="👨 Male NPCs", value="\n".join(male_npcs[:10]), inline=True)
    embed.add_field(name="👩 Female NPCs", value="\n".join(female_npcs[:10]), inline=True)
    embed.add_field(name="💬 Usage", value="`!talk <npc_name>` - Chat with NPC\n`!gift <npc_name> <item>` - Give gift\n`!npc_info <npc_name>` - View NPC details", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="talk")
async def talk_npc(ctx, *, npc_name=None):
    """Talk to an NPC - AI-driven conversations!"""
    if not NPC_SYSTEM_LOADED:
        return await ctx.send("❌ NPC system is not available!")
    
    if not npc_name:
        return await ctx.send("❌ Please specify an NPC name! Use `!npc_list` to see available NPCs.")
    
    # Find NPC by name
    npc_id = None
    for id, npc in NPCS.items():
        if npc['name'].lower() == npc_name.lower():
            npc_id = id
            break
    
    if not npc_id:
        return await ctx.send(f"❌ NPC '{npc_name}' not found! Use `!npc_list` to see available NPCs.")
    
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    # Get player-specific NPC data
    npc_data = get_npc_data(player_id, npc_id)
    
    # Send typing indicator for immersion
    async with ctx.typing():
        # Generate AI-driven dialogue
        dialogue = await query_ai_for_npc_dialogue(npc_data, player, "casual_conversation")
        
        # Calculate affection change from talking
        result = update_npc_affection(player_id, npc_id, random.randint(1, 3))
        old_affection, new_affection = result[0], result[1]
        exclusive_message = result[2] if len(result) > 2 else ""
        affection_change = new_affection - old_affection
        
        # Create response embed
        embed = discord.Embed(
            title=f"💬 Conversation with {npc_data['name']} {npc_data['emoji']}",
            description=f"*{dialogue}*",
            color=0x4169e1
        )
        
        # Add affection info
        hearts = "💖" * (new_affection // 20)
        empty_hearts = "🤍" * (5 - (new_affection // 20))
        affection_bar = hearts + empty_hearts
        
        embed.add_field(
            name="💕 Affection", 
            value=f"{affection_bar} {new_affection}/100 (+{affection_change})",
            inline=True
        )
        embed.add_field(
            name="🤝 Relationship", 
            value=npc_data['relationship_status'].title(),
            inline=True
        )
        
        embed.set_footer(text=f"Cultivation: {npc_data['realm']} | Specialty: {npc_data['specialty']}")
        
        await ctx.send(embed=embed)
        
        # Send exclusive relationship message if any
        if exclusive_message:
            await ctx.send(exclusive_message)
        
        save_npc_data()

@bot.command(name="gift")
async def gift_npc(ctx, npc_name=None, *, item=None):
    """Give a gift to an NPC to increase affection"""
    if not NPC_SYSTEM_LOADED:
        return await ctx.send("❌ NPC system is not available!")
    
    if not npc_name or not item:
        return await ctx.send("❌ Usage: `!gift <npc_name> <item>`\nExample: `!gift Chen Wei spirit_sword`")
    
    # Find NPC
    npc_id = None
    for id, npc in NPCS.items():
        if npc['name'].lower() == npc_name.lower():
            npc_id = id
            break
    
    if not npc_id:
        return await ctx.send(f"❌ NPC '{npc_name}' not found!")
    
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    # Check if player has enough spirit stones for gift
    gift_cost = 100  # Basic gift cost
    if player.get("spirit_stones", 0) < gift_cost:
        return await ctx.send(f"❌ You need {gift_cost} spirit stones to buy a gift!")
    
    # Deduct cost
    player["spirit_stones"] -= gift_cost
    update_player(player_id, player)
    
    # Get NPC data and calculate affection change
    npc_data = get_npc_data(player_id, npc_id)
    
    # Calculate affection change based on gift type
    from npc_system import calculate_affection_change
    affection_change = calculate_affection_change(npc_data, "gift", item.lower())
    result = update_npc_affection(player_id, npc_id, affection_change)
    old_affection, new_affection = result[0], result[1]
    exclusive_message = result[2] if len(result) > 2 else ""
    
    # Generate AI response to gift
    async with ctx.typing():
        dialogue = await query_ai_for_npc_dialogue(npc_data, player, f"received_gift:{item}")
        
        # Determine gift reception
        if item.lower() in [gift.lower() for gift in npc_data.get("gifts_loved", [])]:
            reaction = "😍 *absolutely loves it*"
        elif item.lower() in [gift.lower() for gift in npc_data.get("gifts_hated", [])]:
            reaction = "😤 *dislikes it*"
        else:
            reaction = "😊 *appreciates it*"
        
        embed = discord.Embed(
            title=f"🎁 Gift to {npc_data['name']} {npc_data['emoji']}",
            description=f"You gave **{item}** to {npc_data['name']}!\n\n*{dialogue}*\n\n{npc_data['name']} {reaction}",
            color=0xff69b4
        )
        
        hearts = "💖" * (new_affection // 20)
        empty_hearts = "🤍" * (5 - (new_affection // 20))
        affection_bar = hearts + empty_hearts
        
        embed.add_field(
            name="💕 Affection Change", 
            value=f"{affection_bar} {new_affection}/100 ({affection_change:+d})",
            inline=True
        )
        embed.add_field(
            name="💰 Cost", 
            value=f"-{gift_cost} Spirit Stones",
            inline=True
        )
        
        await ctx.send(embed=embed)
        
        # Send exclusive relationship message if any
        if exclusive_message:
            await ctx.send(exclusive_message)
        
        save_npc_data()

@bot.command(name="npc_info")
async def npc_info(ctx, *, npc_name=None):
    """View detailed information about an NPC"""
    if not NPC_SYSTEM_LOADED:
        return await ctx.send("❌ NPC system is not available!")
    
    if not npc_name:
        return await ctx.send("❌ Please specify an NPC name!")
    
    # Find NPC
    npc_id = None
    for id, npc in NPCS.items():
        if npc['name'].lower() == npc_name.lower():
            npc_id = id
            break
    
    if not npc_id:
        return await ctx.send(f"❌ NPC '{npc_name}' not found!")
    
    player_id = str(ctx.author.id)
    npc_data = get_npc_data(player_id, npc_id)
    
    embed = discord.Embed(
        title=f"{npc_data['emoji']} {npc_data['name']}",
        description=npc_data['backstory'],
        color=0x9932cc
    )
    
    # Basic Info
    embed.add_field(name="🏮 Cultivation", value=f"Level {npc_data['cultivation_level']}\n{npc_data['realm']}", inline=True)
    embed.add_field(name="⚡ Specialty", value=npc_data['specialty'], inline=True)
    embed.add_field(name="👤 Personality", value=npc_data['personality'].replace('_', ' ').title(), inline=True)
    
    # Relationship Info
    hearts = "💖" * (npc_data['affection_level'] // 20)
    empty_hearts = "🤍" * (5 - (npc_data['affection_level'] // 20))
    affection_bar = hearts + empty_hearts
    
    embed.add_field(name="💕 Your Relationship", value=f"{affection_bar}\n{npc_data['affection_level']}/100 - {npc_data['relationship_status'].title()}", inline=False)
    
    # Preferences
    loved_gifts = ", ".join(npc_data.get('gifts_loved', [])[:3])
    hated_gifts = ", ".join(npc_data.get('gifts_hated', [])[:3])
    
    embed.add_field(name="💝 Loves", value=loved_gifts if loved_gifts else "Unknown", inline=True)
    embed.add_field(name="💔 Hates", value=hated_gifts if hated_gifts else "Unknown", inline=True)
    
    # Show combat assistance eligibility
    if npc_data['affection_level'] >= 60:
        embed.add_field(
            name="⚔️ Combat Assistance", 
            value="✅ **Available** - This NPC can assist you in battles!\nUse `!set_assistant " + npc_data['name'] + "` to make them your combat partner.",
            inline=False
        )
    else:
        needed_affection = 60 - npc_data['affection_level'] 
        embed.add_field(
            name="⚔️ Combat Assistance", 
            value=f"🔒 **Locked** - Need {needed_affection} more affection points to unlock combat assistance.",
            inline=False
        )
    
    await ctx.send(embed=embed)

# ===============================
# NPC Combat Assistant Commands  
# ===============================

@bot.command(name="set_assistant")
async def set_combat_assistant(ctx, *, npc_name=None):
    """Set an NPC as your combat assistant (requires 60%+ affection)"""
    if not NPC_SYSTEM_LOADED:
        return await ctx.send("❌ NPC system is not available!")
    
    if not npc_name:
        return await ctx.send("❌ Please specify an NPC name! Use `!available_assistants` to see eligible NPCs.")
    
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    # Find NPC by name
    npc_id = None
    for id, npc in NPCS.items():
        if npc['name'].lower() == npc_name.lower():
            npc_id = id
            break
    
    if not npc_id:
        return await ctx.send(f"❌ NPC '{npc_name}' not found! Use `!npc_list` to see available NPCs.")
    
    # Check affection requirement
    if not can_use_npc_assistant(player_id, npc_id):
        npc_data = get_npc_data(player_id, npc_id)
        needed_affection = 60 - npc_data['affection_level']
        return await ctx.send(f"❌ You need {needed_affection} more affection points with {npc_data['name']} to use them as a combat assistant!")
    
    # Set the combat assistant
    player["combat_assistant"] = npc_id
    update_player(player_id, player)
    
    npc_data = get_npc_data(player_id, npc_id)
    bonuses = apply_npc_combat_assistance(player, npc_data['specialty'])
    
    embed = discord.Embed(
        title="⚔️ Combat Assistant Set!",
        description=f"**{npc_data['name']} {npc_data['emoji']}** is now your combat assistant!",
        color=0x00ff00
    )
    
    embed.add_field(
        name="💪 Combat Bonuses",
        value=f"**Enhanced Power:** {bonuses['enhanced_power']:,} (+{int((bonuses['enhanced_power']/player['total_power'] - 1) * 100)}%)\n**Defense Bonus:** {int(bonuses['defense_bonus']*100)}%\n**Healing Bonus:** {int(bonuses['healing_bonus']*100)}%",
        inline=True
    )
    
    embed.add_field(
        name="✨ Special Ability",
        value=bonuses['special_ability'],
        inline=False
    )
    
    embed.add_field(
        name="🔔 Combat Usage",
        value="Your assistant will automatically help in:\n• PvP Battles (`!pvp`)\n• Boss Fights (`!boss_challenge`)\n• World Boss Raids (`!wb_challenge`)",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="remove_assistant")
async def remove_combat_assistant(ctx):
    """Remove your current combat assistant"""
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    if "combat_assistant" not in player or not player["combat_assistant"]:
        return await ctx.send("❌ You don't have a combat assistant set!")
    
    assistant_id = player["combat_assistant"]
    assistant_name = NPCS[assistant_id]['name'] if assistant_id in NPCS else "Unknown"
    
    player["combat_assistant"] = None
    update_player(player_id, player)
    
    embed = discord.Embed(
        title="💔 Combat Assistant Removed",
        description=f"**{assistant_name}** is no longer your combat assistant.",
        color=0xff6b6b
    )
    embed.add_field(
        name="🔄 Set New Assistant",
        value="Use `!available_assistants` to see eligible NPCs\nUse `!set_assistant <npc_name>` to set a new one",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="assistant_info")
async def combat_assistant_info(ctx):
    """View your current combat assistant details"""
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    assistant_id = get_player_combat_assistant(player_id)
    if not assistant_id or assistant_id not in NPCS:
        return await ctx.send("❌ You don't have a combat assistant set! Use `!available_assistants` to see eligible NPCs.")
    
    npc_data = get_npc_data(player_id, assistant_id)
    bonuses = apply_npc_combat_assistance(player, npc_data['specialty'])
    
    embed = discord.Embed(
        title=f"⚔️ Combat Assistant: {npc_data['name']} {npc_data['emoji']}",
        description=f"**{npc_data['personality']}** {npc_data['gender']} from {npc_data['realm']}",
        color=0x4169e1
    )
    
    # Affection display
    hearts = "💖" * (npc_data['affection_level'] // 20)
    empty_hearts = "🤍" * (5 - (npc_data['affection_level'] // 20))
    affection_bar = hearts + empty_hearts
    
    embed.add_field(
        name="💕 Relationship Status",
        value=f"{affection_bar} {npc_data['affection_level']}/100\n**Status:** {npc_data['relationship_status'].title()}",
        inline=True
    )
    
    embed.add_field(
        name="💪 Combat Bonuses",
        value=f"**Power:** {player['total_power']:,} → {bonuses['enhanced_power']:,}\n**Defense Bonus:** {int(bonuses['defense_bonus']*100)}%\n**Healing Bonus:** {int(bonuses['healing_bonus']*100)}%",
        inline=True
    )
    
    embed.add_field(
        name="✨ Special Ability",
        value=bonuses['special_ability'],
        inline=False
    )
    
    embed.add_field(
        name="🏮 Specialty",
        value=npc_data['specialty'],
        inline=True
    )
    
    embed.add_field(
        name="🔄 Management",
        value="`!remove_assistant` - Remove assistant\n`!available_assistants` - See other options",
        inline=True
    )
    
    await ctx.send(embed=embed)

@bot.command(name="available_assistants")
async def available_assistants(ctx):
    """View NPCs available for combat assistance (60%+ affection)"""
    if not NPC_SYSTEM_LOADED:
        return await ctx.send("❌ NPC system is not available!")
    
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    available_npcs = []
    locked_npcs = []
    
    for npc_id, npc in NPCS.items():
        npc_data = get_npc_data(player_id, npc_id)
        if npc_data['affection_level'] >= 60:
            bonuses = NPC_COMBAT_BONUSES.get(npc_data['specialty'], {})
            damage_bonus = int(bonuses.get('damage', 0) * 100)
            defense_bonus = int(bonuses.get('defense', 0) * 100)
            healing_bonus = int(bonuses.get('healing', 0) * 100)
            
            bonus_text = []
            if damage_bonus > 0:
                bonus_text.append(f"⚔️ +{damage_bonus}% DMG")
            if defense_bonus > 0:
                bonus_text.append(f"🛡️ +{defense_bonus}% DEF")
            if healing_bonus > 0:
                bonus_text.append(f"❤️ +{healing_bonus}% HEAL")
            
            available_npcs.append(f"{npc['emoji']} **{npc['name']}** ({npc_data['affection_level']}/100)\n{' | '.join(bonus_text)}")
        else:
            locked_npcs.append(f"{npc['emoji']} {npc['name']} - Need {60 - npc_data['affection_level']} more affection")
    
    embed = discord.Embed(
        title="⚔️ Combat Assistant Availability",
        description="NPCs with 60%+ affection can assist you in battles!",
        color=0x9932cc
    )
    
    current_assistant = get_player_combat_assistant(player_id)
    if current_assistant and current_assistant in NPCS:
        embed.add_field(
            name="👑 Current Assistant",
            value=f"{NPCS[current_assistant]['emoji']} **{NPCS[current_assistant]['name']}**",
            inline=False
        )
    
    if available_npcs:
        embed.add_field(
            name="✅ Available for Combat (60%+ Affection)",
            value="\n\n".join(available_npcs[:8]),  # Limit to prevent embed overflow
            inline=False
        )
    
    if locked_npcs[:5]:  # Show first 5 locked NPCs
        embed.add_field(
            name="🔒 Need More Affection",
            value="\n".join(locked_npcs[:5]),
            inline=False
        )
    
    embed.add_field(
        name="📖 Usage",
        value="`!set_assistant <npc_name>` - Set combat assistant\n`!assistant_info` - View current assistant\n`!talk <npc_name>` / `!gift <npc_name> <item>` - Build affection",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ===============================
# COMPREHENSIVE SECT SYSTEM COMMANDS
# ===============================

@bot.command(name="sect_list")
async def sect_list(ctx, realm=None):
    """View all available sects, optionally filtered by realm"""
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    embed = discord.Embed(
        title="🏛️ Cultivation Sects",
        description="Join a sect to learn unique techniques and gain powerful bonuses!",
        color=0x9400d3
    )
    
    # Filter sects by realm if specified
    if realm:
        if realm.lower() == "mortal":
            target_realm = "Mortal Realm"
        elif realm.lower() == "immortal":
            target_realm = "Immortal Realm"
        elif realm.lower() == "god":
            target_realm = "God Realm"
        else:
            return await ctx.send("❌ Invalid realm! Use: `mortal`, `immortal`, or `god`")
        
        filtered_sects = {k: v for k, v in CULTIVATION_SECTS.items() if v["realm"] == target_realm}
        embed.title = f"🏛️ {target_realm} Sects"
    else:
        filtered_sects = CULTIVATION_SECTS
    
    # Group sects by realm
    realms = {"Mortal Realm": [], "Immortal Realm": [], "God Realm": []}
    
    for sect_id, sect in filtered_sects.items():
        can_join, requirement = can_join_sect(player, sect_id)
        status = "✅" if can_join else "🔒"
        
        sect_info = f"{sect['emoji']} **{sect['name']}**\n{sect['specialty']}\n*{sect['entrance_requirement']}*"
        realms[sect['realm']].append(sect_info)
    
    for realm_name, sect_list in realms.items():
        if sect_list:
            embed.add_field(
                name=f"🌟 {realm_name}",
                value="\n\n".join(sect_list[:3]),  # Limit to prevent overflow
                inline=True
            )
    
    embed.add_field(
        name="📖 Commands",
        value="`!join_sect <sect_name>` - Join a sect\n`!sect_info <sect_name>` - View sect details\n`!my_sect` - View your current sect",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="join_sect")
async def join_sect(ctx, *, sect_name=None):
    """Join a cultivation sect"""
    if not sect_name:
        return await ctx.send("❌ Please specify a sect name! Use `!sect_list` to see available sects.")
    
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    # Find sect by name
    sect_id = None
    for id, sect in CULTIVATION_SECTS.items():
        if sect['name'].lower() == sect_name.lower():
            sect_id = id
            break
    
    if not sect_id:
        return await ctx.send(f"❌ Sect '{sect_name}' not found! Use `!sect_list` to see available sects.")
    
    sect = CULTIVATION_SECTS[sect_id]
    
    # Check if already in a sect
    current_sect = get_player_sect(player_id)
    if current_sect:
        current_sect_name = CULTIVATION_SECTS[current_sect]['name']
        return await ctx.send(f"❌ You're already a member of {current_sect_name}! Use `!leave_sect` first.")
    
    # Check requirements
    can_join, requirement = can_join_sect(player, sect_id)
    if not can_join:
        return await ctx.send(f"❌ You cannot join {sect['name']}! Requirement: {requirement}")
    
    # Join the sect
    player["sect"] = sect_id
    player["sect_techniques"] = []  # Initialize techniques list
    update_player(player_id, player)
    
    # Create welcome embed
    embed = discord.Embed(
        title=f"🎉 Welcome to {sect['name']}! {sect['emoji']}",
        description=f"You have successfully joined the {sect['name']}!\n\n*{sect['description']}*",
        color=0x00ff00
    )
    
    # Show bonuses
    bonus_text = []
    for bonus_type, bonus_value in sect['bonus'].items():
        bonus_text.append(f"**{bonus_type.replace('_', ' ').title()}:** +{int(bonus_value*100)}%")
    
    embed.add_field(
        name="💪 Sect Bonuses",
        value="\n".join(bonus_text),
        inline=True
    )
    
    # Show available techniques
    techniques = sect['techniques']
    embed.add_field(
        name="📚 Available Techniques",
        value="\n".join([f"• {tech}" for tech in techniques[:4]]),
        inline=True
    )
    
    embed.add_field(
        name="🎓 Next Steps",
        value="`!learn_technique <technique_name>` - Learn sect techniques\n`!my_sect` - View your sect status",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="leave_sect")
async def leave_sect(ctx):
    """Leave your current sect"""
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    current_sect = get_player_sect(player_id)
    if not current_sect:
        return await ctx.send("❌ You're not a member of any sect!")
    
    sect_name = CULTIVATION_SECTS[current_sect]['name']
    
    # Remove sect and techniques
    player["sect"] = None
    player["sect_techniques"] = []
    update_player(player_id, player)
    
    embed = discord.Embed(
        title="💔 Left Sect",
        description=f"You have left the {sect_name}.\n\n⚠️ **Warning:** All sect techniques have been lost!",
        color=0xff6b6b
    )
    
    embed.add_field(
        name="🔄 Join New Sect",
        value="`!sect_list` - View available sects\n`!join_sect <sect_name>` - Join a new sect",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="my_sect")
async def my_sect(ctx):
    """View your current sect status and techniques"""
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    current_sect = get_player_sect(player_id)
    if not current_sect:
        return await ctx.send("❌ You're not a member of any sect! Use `!sect_list` to see available sects.")
    
    sect = CULTIVATION_SECTS[current_sect]
    learned_techniques = player.get("sect_techniques", [])
    
    embed = discord.Embed(
        title=f"{sect['emoji']} {sect['name']}",
        description=f"**Specialty:** {sect['specialty']}\n*{sect['description']}*",
        color=0x4169e1
    )
    
    # Show bonuses
    bonus_text = []
    for bonus_type, bonus_value in sect['bonus'].items():
        bonus_text.append(f"**{bonus_type.replace('_', ' ').title()}:** +{int(bonus_value*100)}%")
    
    embed.add_field(
        name="💪 Your Bonuses",
        value="\n".join(bonus_text),
        inline=True
    )
    
    # Show power with bonuses
    base_power = player["total_power"]
    sect_power = apply_sect_bonuses(player, current_sect)
    embed.add_field(
        name="⚡ Power Boost",
        value=f"**Base:** {base_power:,}\n**With Sect:** {sect_power:,}\n**Bonus:** +{sect_power-base_power:,}",
        inline=True
    )
    
    # Show learned techniques
    if learned_techniques:
        embed.add_field(
            name="📚 Learned Techniques",
            value="\n".join([f"✅ {tech}" for tech in learned_techniques]),
            inline=False
        )
    
    # Show available techniques
    available_techniques = [tech for tech in sect['techniques'] if tech not in learned_techniques]
    if available_techniques:
        embed.add_field(
            name="📖 Available to Learn",
            value="\n".join([f"📝 {tech}" for tech in available_techniques]),
            inline=False
        )
    
    embed.add_field(
        name="🎓 Commands",
        value="`!learn_technique <technique_name>` - Learn new technique\n`!sect_techniques` - View all sect techniques",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="learn_sect_technique")
async def learn_sect_technique(ctx, *, technique_name=None):
    """Learn a technique from your sect"""
    if not technique_name:
        return await ctx.send("❌ Please specify a technique name! Use `!my_sect` to see available techniques.")
    
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    current_sect = get_player_sect(player_id)
    if not current_sect:
        return await ctx.send("❌ You're not a member of any sect! Use `!join_sect` first.")
    
    sect = CULTIVATION_SECTS[current_sect]
    available_techniques = sect['techniques']
    learned_techniques = player.get("sect_techniques", [])
    
    # Check if technique exists in sect
    if technique_name not in available_techniques:
        return await ctx.send(f"❌ '{technique_name}' is not available in {sect['name']}!")
    
    # Check if already learned
    if technique_name in learned_techniques:
        return await ctx.send(f"❌ You have already learned '{technique_name}'!")
    
    # Calculate cost based on technique power
    technique_cost = 500 * (len(learned_techniques) + 1)  # Increases with each technique
    
    if player["spirit_stones"] < technique_cost:
        return await ctx.send(f"❌ You need {technique_cost} spirit stones to learn '{technique_name}'! You have {player['spirit_stones']}.")
    
    # Learn the technique
    player["spirit_stones"] -= technique_cost
    if "sect_techniques" not in player:
        player["sect_techniques"] = []
    player["sect_techniques"].append(technique_name)
    
    # Add small power bonus for learning technique
    power_bonus = random.randint(100, 300)
    player["total_power"] += power_bonus
    
    update_player(player_id, player)
    
    embed = discord.Embed(
        title="🎓 Technique Learned!",
        description=f"You have successfully learned **{technique_name}**!",
        color=0x00ff00
    )
    
    embed.add_field(
        name="💰 Cost",
        value=f"-{technique_cost} Spirit Stones",
        inline=True
    )
    
    embed.add_field(
        name="⚡ Power Gained",
        value=f"+{power_bonus} Power",
        inline=True
    )
    
    embed.add_field(
        name="📚 Progress",
        value=f"Learned {len(player['sect_techniques'])}/{len(available_techniques)} sect techniques",
        inline=False
    )
    
    # Check if all techniques learned
    if len(player["sect_techniques"]) == len(available_techniques):
        embed.add_field(
            name="🏆 Master Achievement",
            value=f"**Congratulations!** You have mastered all techniques of {sect['name']}!",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name="sect_info")
async def sect_info(ctx, *, sect_name=None):
    """View detailed information about a specific sect"""
    if not sect_name:
        return await ctx.send("❌ Please specify a sect name! Use `!sect_list` to see available sects.")
    
    # Find sect by name
    sect_id = None
    for id, sect in CULTIVATION_SECTS.items():
        if sect['name'].lower() == sect_name.lower():
            sect_id = id
            break
    
    if not sect_id:
        return await ctx.send(f"❌ Sect '{sect_name}' not found! Use `!sect_list` to see available sects.")
    
    sect = CULTIVATION_SECTS[sect_id]
    
    embed = discord.Embed(
        title=f"{sect['emoji']} {sect['name']}",
        description=sect['description'],
        color=0x9400d3
    )
    
    embed.add_field(
        name="🌍 Realm",
        value=sect['realm'],
        inline=True
    )
    
    embed.add_field(
        name="🎯 Specialty",
        value=sect['specialty'],
        inline=True
    )
    
    embed.add_field(
        name="📋 Requirements",
        value=sect['entrance_requirement'],
        inline=True
    )
    
    # Show bonuses
    bonus_text = []
    for bonus_type, bonus_value in sect['bonus'].items():
        bonus_text.append(f"**{bonus_type.replace('_', ' ').title()}:** +{int(bonus_value*100)}%")
    
    embed.add_field(
        name="💪 Bonuses",
        value="\n".join(bonus_text),
        inline=False
    )
    
    # Show techniques
    techniques = sect['techniques']
    embed.add_field(
        name="📚 Techniques",
        value="\n".join([f"• {tech}" for tech in techniques]),
        inline=False
    )
    
    embed.add_field(
        name="🚪 Join",
        value=f"`!join_sect {sect['name']}`",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ===============================
# NEW GAME SYSTEMS COMMANDS
# ===============================

@bot.command(name="artifacts")
async def artifacts(ctx):
    """View all available artifacts and your collection"""
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    player_artifacts_list = player_artifacts.get(player_id, [])
    
    embed = discord.Embed(
        title="🏺 Artifact Collection",
        description="Powerful items that grant special abilities and massive power boosts!",
        color=0xffd700
    )
    
    # Group artifacts by realm
    realms = {"Mortal Realm": [], "Immortal Realm": [], "God Realm": []}
    
    for artifact_id, artifact in ARTIFACTS.items():
        owned = "✅" if artifact_id in player_artifacts_list else "🔒"
        rarity_color = {"rare": "🟦", "epic": "🟪", "legendary": "🟨", "mythic": "🟧", "transcendent": "🔴"}
        rarity_emoji = rarity_color.get(artifact["rarity"], "⚪")
        
        artifact_info = f"{owned} {artifact['emoji']} **{artifact['name']}** {rarity_emoji}\n*{artifact['description']}*\n**Power:** +{artifact['power_bonus']}\n**Effect:** {artifact['special_effect']}"
        realms[artifact["realm"]].append(artifact_info)
    
    for realm_name, artifact_list in realms.items():
        if artifact_list:
            embed.add_field(
                name=f"🌟 {realm_name}",
                value="\n\n".join(artifact_list[:2]),  # Limit to prevent overflow
                inline=False
            )
    
    embed.add_field(
        name="📖 Commands",
        value="`!activate_artifact <name>` - Use artifact power\n`!treasure_hunt` - Explore to find artifacts",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="activate_artifact")
async def activate_artifact(ctx, *, artifact_name=None):
    """Activate an artifact's special power"""
    if not artifact_name:
        return await ctx.send("❌ Please specify an artifact name! Use `!artifacts` to see your collection.")
    
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    # Find artifact
    artifact_id = None
    for id, artifact in ARTIFACTS.items():
        if artifact['name'].lower() == artifact_name.lower():
            artifact_id = id
            break
    
    if not artifact_id:
        return await ctx.send(f"❌ Artifact '{artifact_name}' not found!")
    
    # Check if player owns it
    player_artifacts_list = player_artifacts.get(player_id, [])
    if artifact_id not in player_artifacts_list:
        return await ctx.send(f"❌ You don't own the {ARTIFACTS[artifact_id]['name']}!")
    
    # Check cooldown
    now = time.time()
    if player_id in artifact_cooldowns and artifact_id in artifact_cooldowns[player_id]:
        cooldown_end = artifact_cooldowns[player_id][artifact_id]
        if now < cooldown_end:
            remaining = int(cooldown_end - now)
            return await ctx.send(f"❌ Artifact is on cooldown! {remaining} seconds remaining.")
    
    artifact = ARTIFACTS[artifact_id]
    
    # Check activation cost
    if player["spirit_stones"] < artifact["activation_cost"]:
        return await ctx.send(f"❌ You need {artifact['activation_cost']} spirit stones to activate this artifact!")
    
    # Activate artifact
    player["spirit_stones"] -= artifact["activation_cost"]
    
    # Set cooldown
    if player_id not in artifact_cooldowns:
        artifact_cooldowns[player_id] = {}
    artifact_cooldowns[player_id][artifact_id] = now + artifact["cooldown"]
    
    update_player(player_id, player)
    
    embed = discord.Embed(
        title=f"✨ {artifact['name']} Activated!",
        description=f"**{artifact['special_effect']}**\n\n*{artifact['description']}*",
        color=0xff6b6b
    )
    
    embed.add_field(
        name="💰 Cost",
        value=f"-{artifact['activation_cost']} Spirit Stones",
        inline=True
    )
    
    embed.add_field(
        name="⏰ Cooldown",
        value=f"{artifact['cooldown']//60} minutes",
        inline=True
    )
    
    await ctx.send(embed=embed)

@bot.command(name="treasure_hunt")
async def treasure_hunt(ctx, *, location_name=None):
    """Explore dangerous locations to find treasures and artifacts"""
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    if not location_name:
        # Show available locations
        embed = discord.Embed(
            title="🗺️ Treasure Hunt Locations",
            description="Explore dangerous locations to find rare artifacts and treasures!",
            color=0x8b4513
        )
        
        for loc_id, location in TREASURE_LOCATIONS.items():
            difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴", "extreme": "⚫"}
            diff_color = difficulty_emoji.get(location["difficulty"], "⚪")
            
            embed.add_field(
                name=f"{location['emoji']} {location['name']} {diff_color}",
                value=f"**Difficulty:** {location['difficulty'].title()}\n**Time:** {location['exploration_time']//60} min\n**Cost:** {location['cost']} Spirit Stones\n**Success:** {int(location['success_chance']*100)}%\n*{location['description']}*",
                inline=True
            )
        
        embed.add_field(
            name="🚀 Start Hunt",
            value="`!treasure_hunt <location_name>`",
            inline=False
        )
        
        return await ctx.send(embed=embed)
    
    # Find location
    location_id = None
    for id, location in TREASURE_LOCATIONS.items():
        if location['name'].lower() == location_name.lower():
            location_id = id
            break
    
    if not location_id:
        return await ctx.send(f"❌ Location '{location_name}' not found! Use `!treasure_hunt` to see available locations.")
    
    location = TREASURE_LOCATIONS[location_id]
    
    # Check if already exploring
    if player_id in active_explorations:
        return await ctx.send("❌ You're already on a treasure hunt! Wait for it to complete.")
    
    # Check cost
    if player["spirit_stones"] < location["cost"]:
        return await ctx.send(f"❌ You need {location['cost']} spirit stones to explore {location['name']}!")
    
    # Start exploration
    player["spirit_stones"] -= location["cost"]
    update_player(player_id, player)
    
    active_explorations[player_id] = {
        "location": location_id,
        "start_time": time.time(),
        "duration": location["exploration_time"]
    }
    
    embed = discord.Embed(
        title=f"🚀 Treasure Hunt Started!",
        description=f"You begin exploring **{location['name']}**...\n\n*{location['description']}*",
        color=0x00ff00
    )
    
    embed.add_field(
        name="⏰ Duration",
        value=f"{location['exploration_time']//60} minutes",
        inline=True
    )
    
    embed.add_field(
        name="🎯 Success Chance",
        value=f"{int(location['success_chance']*100)}%",
        inline=True
    )
    
    embed.add_field(
        name="📅 Status",
        value=f"Use `!check_hunt` to see progress",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="check_hunt")
async def check_hunt(ctx):
    """Check the status of your current treasure hunt"""
    player_id = str(ctx.author.id)
    
    if player_id not in active_explorations:
        return await ctx.send("❌ You're not currently on a treasure hunt! Use `!treasure_hunt` to start one.")
    
    exploration = active_explorations[player_id]
    location = TREASURE_LOCATIONS[exploration["location"]]
    
    elapsed = time.time() - exploration["start_time"]
    remaining = exploration["duration"] - elapsed
    
    if remaining <= 0:
        # Exploration complete - determine results
        success = random.random() < location["success_chance"]
        
        # Remove from active explorations
        del active_explorations[player_id]
        
        player = get_player(player_id)
        
        if success:
            # Success! Give rewards
            rewards = location["rewards"]
            
            # Spirit stones
            if "spirit_stones" in rewards:
                stones_gained = random.randint(*rewards["spirit_stones"])
                player["spirit_stones"] += stones_gained
            
            # Power gain
            if "power_gain" in rewards:
                power_gained = random.randint(*rewards["power_gain"])
                player["total_power"] += power_gained
            
            # Qi gain
            if "qi_gain" in rewards:
                qi_gained = random.randint(*rewards["qi_gain"])
                player["qi"] += qi_gained
            
            # Artifact chance
            artifact_found = None
            if "artifacts" in rewards and random.random() < 0.3:  # 30% chance
                artifact_found = random.choice(rewards["artifacts"])
                if player_id not in player_artifacts:
                    player_artifacts[player_id] = []
                if artifact_found not in player_artifacts[player_id]:
                    player_artifacts[player_id].append(artifact_found)
            
            # Enlightenment chance
            enlightenment = None
            if "enlightenment_chance" in rewards and random.random() < rewards["enlightenment_chance"]:
                enlightenment_event = random.choice(list(ENLIGHTENMENT_EVENTS.values()))
                power_boost = random.randint(*enlightenment_event["power_boost"])
                qi_boost = random.randint(*enlightenment_event["qi_boost"])
                player["total_power"] += power_boost
                player["qi"] += qi_boost
                enlightenment = enlightenment_event
            
            update_player(player_id, player)
            
            embed = discord.Embed(
                title="🎉 Treasure Hunt Successful!",
                description=f"Your exploration of **{location['name']}** was successful!",
                color=0x00ff00
            )
            
            reward_text = []
            if "spirit_stones" in rewards:
                reward_text.append(f"💰 +{stones_gained} Spirit Stones")
            if "power_gain" in rewards:
                reward_text.append(f"⚡ +{power_gained} Power")
            if "qi_gain" in rewards:
                reward_text.append(f"🌀 +{qi_gained} Qi")
            
            if artifact_found:
                artifact = ARTIFACTS[artifact_found]
                reward_text.append(f"🏺 **{artifact['name']}** found!")
            
            if enlightenment:
                reward_text.append(f"{enlightenment['emoji']} **{enlightenment['name']}**!")
            
            embed.add_field(
                name="🎁 Rewards",
                value="\n".join(reward_text) if reward_text else "No rewards this time",
                inline=False
            )
            
            if enlightenment:
                embed.add_field(
                    name="💫 Enlightenment",
                    value=enlightenment["message"],
                    inline=False
                )
            
        else:
            # Failure
            embed = discord.Embed(
                title="💥 Treasure Hunt Failed!",
                description=f"Your exploration of **{location['name']}** was unsuccessful. You return empty-handed but wiser.",
                color=0xff0000
            )
            
            embed.add_field(
                name="🎓 Experience",
                value="You gained valuable experience from this dangerous adventure!",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    else:
        # Still in progress
        progress = (elapsed / exploration["duration"]) * 100
        remaining_minutes = int(remaining // 60)
        remaining_seconds = int(remaining % 60)
        
        embed = discord.Embed(
            title=f"🔍 Treasure Hunt in Progress...",
            description=f"Exploring **{location['name']}**\n\n*{location['description']}*",
            color=0xffff00
        )
        
        embed.add_field(
            name="📊 Progress",
            value=f"{progress:.1f}% Complete",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Time Remaining",
            value=f"{remaining_minutes}m {remaining_seconds}s",
            inline=True
        )
        
        await ctx.send(embed=embed)

@bot.command(name="formations")
async def formations(ctx):
    """View available cultivation formations"""
    embed = discord.Embed(
        title="✨ Cultivation Formations",
        description="Join with other cultivators to enhance your cultivation power!",
        color=0x9932cc
    )
    
    for form_id, formation in FORMATIONS.items():
        embed.add_field(
            name=f"{formation['emoji']} {formation['name']}",
            value=f"**Participants:** {formation['min_participants']}-{formation['max_participants']}\n**Duration:** {formation['duration']//60} minutes\n**Power Multiplier:** {formation['power_multiplier']}x\n**Qi Bonus:** {formation['qi_bonus']}x\n**Cost:** {formation['cost_per_person']} Spirit Stones\n*{formation['description']}*",
            inline=True
        )
    
    embed.add_field(
        name="🚀 Commands",
        value="`!join_formation <name>` - Join a formation\n`!create_formation <name>` - Create new formation\n`!active_formations` - View active formations",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="create_formation")
async def create_formation(ctx, *, formation_name=None):
    """Create a new cultivation formation"""
    if not formation_name:
        return await ctx.send("❌ Please specify a formation name! Use `!formations` to see available types.")
    
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    # Find formation type
    formation_id = None
    for id, formation in FORMATIONS.items():
        if formation['name'].lower() == formation_name.lower():
            formation_id = id
            break
    
    if not formation_id:
        return await ctx.send(f"❌ Formation '{formation_name}' not found! Use `!formations` to see available types.")
    
    formation = FORMATIONS[formation_id]
    
    # Check if player already in a formation
    for active_form in active_formations.values():
        if player_id in active_form["participants"]:
            return await ctx.send("❌ You're already in a formation! Leave it first or wait for it to complete.")
    
    # Check cost
    if player["spirit_stones"] < formation["cost_per_person"]:
        return await ctx.send(f"❌ You need {formation['cost_per_person']} spirit stones to create this formation!")
    
    # Create formation
    formation_instance_id = f"{formation_id}_{int(time.time())}"
    player["spirit_stones"] -= formation["cost_per_person"]
    update_player(player_id, player)
    
    active_formations[formation_instance_id] = {
        "type": formation_id,
        "creator": player_id,
        "participants": [player_id],
        "start_time": time.time(),
        "duration": formation["duration"],
        "status": "recruiting"
    }
    
    embed = discord.Embed(
        title=f"✨ {formation['name']} Created!",
        description=f"You have created a new cultivation formation!\n\n*{formation['description']}*",
        color=0x9932cc
    )
    
    embed.add_field(
        name="👥 Participants",
        value=f"1/{formation['max_participants']} (Need {formation['min_participants']} minimum)",
        inline=True
    )
    
    embed.add_field(
        name="⏰ Duration",
        value=f"{formation['duration']//60} minutes",
        inline=True
    )
    
    embed.add_field(
        name="🚀 Bonuses",
        value=f"**Power:** {formation['power_multiplier']}x\n**Qi:** {formation['qi_bonus']}x",
        inline=False
    )
    
    embed.add_field(
        name="📢 Recruiting",
        value="Other players can join using `!join_formation` command!",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name="join_formation")
async def join_formation(ctx, *, formation_name=None):
    """Join an active cultivation formation"""
    if not formation_name:
        return await ctx.send("❌ Please specify a formation name! Use `!active_formations` to see available formations.")
    
    player_id = str(ctx.author.id)
    player = get_player(player_id)
    if not player:
        return await ctx.send("❌ You need to register first! Use `!register`")
    
    # Check if player already in a formation
    for active_form in active_formations.values():
        if player_id in active_form["participants"]:
            return await ctx.send("❌ You're already in a formation! Wait for it to complete.")
    
    # Find active formation
    target_formation = None
    target_id = None
    for form_id, active_form in active_formations.items():
        formation_type = FORMATIONS[active_form["type"]]
        if formation_type['name'].lower() == formation_name.lower() and active_form["status"] == "recruiting":
            target_formation = active_form
            target_id = form_id
            break
    
    if not target_formation:
        return await ctx.send(f"❌ No recruiting formation '{formation_name}' found! Use `!active_formations` to see available formations.")
    
    formation = FORMATIONS[target_formation["type"]]
    
    # Check if formation is full
    if len(target_formation["participants"]) >= formation["max_participants"]:
        return await ctx.send(f"❌ The {formation['name']} is full!")
    
    # Check cost
    if player["spirit_stones"] < formation["cost_per_person"]:
        return await ctx.send(f"❌ You need {formation['cost_per_person']} spirit stones to join this formation!")
    
    # Join formation
    player["spirit_stones"] -= formation["cost_per_person"]
    update_player(player_id, player)
    
    target_formation["participants"].append(player_id)
    
    # Check if formation can start
    if len(target_formation["participants"]) >= formation["min_participants"]:
        target_formation["status"] = "active"
        target_formation["start_time"] = time.time()
        
        # Notify all participants
        for participant_id in target_formation["participants"]:
            try:
                user = await bot.fetch_user(int(participant_id))
                await user.send(f"🌟 **{formation['name']} Started!** Your formation cultivation has begun!")
            except:
                pass
    
    embed = discord.Embed(
        title=f"✨ Joined {formation['name']}!",
        description=f"You have joined the cultivation formation!\n\n*{formation['description']}*",
        color=0x00ff00
    )
    
    embed.add_field(
        name="👥 Participants",
        value=f"{len(target_formation['participants'])}/{formation['max_participants']}",
        inline=True
    )
    
    embed.add_field(
        name="📊 Status", 
        value=target_formation["status"].title(),
        inline=True
    )
    
    if target_formation["status"] == "active":
        embed.add_field(
            name="🎉 Formation Active!",
            value=f"Cultivation bonuses are now active for {formation['duration']//60} minutes!",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name="active_formations")
async def active_formations_cmd(ctx):
    """View all active cultivation formations"""
    if not active_formations:
        return await ctx.send("❌ No active formations found! Use `!create_formation` to start one.")
    
    embed = discord.Embed(
        title="✨ Active Formations",
        description="Join these formations to enhance your cultivation!",
        color=0x9932cc
    )
    
    for form_id, active_form in active_formations.items():
        formation = FORMATIONS[active_form["type"]]
        
        status_emoji = {"recruiting": "🔄", "active": "✅", "completed": "✅"}
        status = status_emoji.get(active_form["status"], "❓")
        
        participants_count = len(active_form["participants"])
        
        # Calculate remaining time
        if active_form["status"] == "active":
            elapsed = time.time() - active_form["start_time"]
            remaining = formation["duration"] - elapsed
            time_text = f"{int(remaining//60)}m {int(remaining%60)}s remaining" if remaining > 0 else "Completing..."
        else:
            time_text = "Recruiting participants"
        
        embed.add_field(
            name=f"{formation['emoji']} {formation['name']} {status}",
            value=f"**Participants:** {participants_count}/{formation['max_participants']}\n**Status:** {active_form['status'].title()}\n**Time:** {time_text}\n**Bonuses:** {formation['power_multiplier']}x Power, {formation['qi_bonus']}x Qi",
            inline=True
        )
    
    embed.add_field(
        name="🚀 Commands",
        value="`!join_formation <name>` - Join a recruiting formation\n`!create_formation <name>` - Create new formation",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Helper function to integrate enlightenment events into cultivation
def trigger_enlightenment_event(player_id):
    """Randomly trigger enlightenment events during cultivation"""
    for event_id, event in ENLIGHTENMENT_EVENTS.items():
        if random.random() < event["chance"]:
            player = get_player(player_id)
            if player:
                power_boost = random.randint(*event["power_boost"])
                qi_boost = random.randint(*event["qi_boost"])
                player["total_power"] += power_boost
                player["qi"] += qi_boost
                update_player(player_id, player)
                return event, power_boost, qi_boost
    return None, 0, 0

# ===============================
# COMPREHENSIVE HELP SYSTEM - UPDATED
# ===============================
@bot.command(name="guide")
async def help_command(ctx, category=None):
    """Comprehensive help system for all commands"""
    
    if category == "basic":
        embed = discord.Embed(title="📚 Basic Commands", color=0x00ff00)
        embed.add_field(name="!register", value="Register as a new cultivator", inline=False)
        embed.add_field(name="!profile", value="View your cultivation profile", inline=False)
        embed.add_field(name="!cultivate", value="Start cultivation session", inline=False)
        embed.add_field(name="!breakthrough", value="Advance to next cultivation stage", inline=False)
        embed.add_field(name="!leaderboard", value="View top cultivators", inline=False)
        embed.add_field(name="!daily", value="Claim daily cultivation rewards", inline=False)
        
    elif category == "combat":
        embed = discord.Embed(title="⚔️ Combat Commands", color=0xff0000)
        embed.add_field(name="!duel @user", value="Challenge another player to PvP", inline=False)
        embed.add_field(name="!boss_list", value="View available bosses", inline=False)
        embed.add_field(name="!challenge_boss <name>", value="Fight a boss solo", inline=False)
        embed.add_field(name="!world_boss_status", value="Check world boss status", inline=False)
        embed.add_field(name="!create_party", value="Create party for world boss", inline=False)
        embed.add_field(name="!join_party <leader>", value="Join a world boss party", inline=False)
        embed.add_field(name="!challenge_world_boss", value="Fight world boss with party", inline=False)
        
    elif category == "adventure":
        embed = discord.Embed(title="🗺️ Adventure Commands", color=0x0099ff)
        embed.add_field(name="!explore", value="Start AI-driven exploration adventure", inline=False)
        embed.add_field(name="!dungeon <name>", value="Enter a dungeon for rewards", inline=False)
        embed.add_field(name="!dungeon_list", value="View available dungeons", inline=False)
        embed.add_field(name="!quest", value="View and complete daily quests", inline=False)
        
    elif category == "npc":
        embed = discord.Embed(title="🧑‍🤝‍🧑 NPC Commands", color=0x9932cc)
        embed.add_field(name="!npc_list", value="View all available NPCs", inline=False)
        embed.add_field(name="!talk <npc_name>", value="Have AI-driven conversation with NPC", inline=False)
        embed.add_field(name="!gift <npc_name> <item>", value="Give gift to increase affection", inline=False)
        embed.add_field(name="!npc_info <npc_name>", value="View detailed NPC information", inline=False)
        
    elif category == "systems":
        embed = discord.Embed(title="🔧 System Commands", color=0xffff00)
        embed.add_field(name="!shop", value="Buy items and spirit beasts", inline=False)
        embed.add_field(name="!inventory", value="View your items and equipment", inline=False)
        embed.add_field(name="!techniques", value="Learn and upgrade techniques", inline=False)
        embed.add_field(name="!alchemy", value="Craft pills and potions", inline=False)
        embed.add_field(name="!spirit_beast", value="Manage your spirit beasts", inline=False)
        embed.add_field(name="!stats", value="View detailed player statistics", inline=False)
        
    else:
        # Main help menu
        embed = discord.Embed(
            title="🌟 Cultivation Discord Bot - Complete Command Guide",
            description="A comprehensive cultivation RPG with AI-driven NPCs, exploration, and epic battles!",
            color=0xffd700
        )
        embed.add_field(name="📚 Basic Commands", value="`!help basic` - Registration, profile, cultivation", inline=True)
        embed.add_field(name="⚔️ Combat Commands", value="`!help combat` - PvP, bosses, world bosses", inline=True)
        embed.add_field(name="🗺️ Adventure Commands", value="`!help adventure` - Exploration, dungeons, quests", inline=True)
        embed.add_field(name="🧑‍🤝‍🧑 NPC Commands", value="`!help npc` - AI-driven NPC interactions", inline=True)
        embed.add_field(name="🔧 System Commands", value="`!help systems` - Shop, inventory, techniques", inline=True)
        embed.add_field(name="🎮 Quick Start", value="1. `!register` to begin\n2. `!cultivate` to gain power\n3. `!explore` for AI adventures\n4. `!npc_list` to meet NPCs", inline=False)
        
        embed.add_field(name="🆕 New Features", value="• **AI Exploration** - Unpredictable adventures\n• **AI NPCs** - 20 unique cultivators with affection systems\n• **World Bosses** - Epic group battles with legendary equipment\n• **Enhanced Combat** - More bosses and dungeons", inline=False)
        
    embed.set_footer(text="💫 Continue your cultivation journey and achieve immortality!")
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