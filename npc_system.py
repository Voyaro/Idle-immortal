# ===============================
# AI-DRIVEN NPC SYSTEM - COMPREHENSIVE
# ===============================

import random
import asyncio
import aiohttp
import json
import os
from utils import load_data, save_data

# NPC Database with 20 cultivators (10 male, 10 female)
NPCS = {
    # Male NPCs
    "chen_wei": {
        "name": "Chen Wei",
        "gender": "male",
        "emoji": "👨‍🦳",
        "cultivation_level": 45,
        "realm": "Immortal Realm",
        "personality": "wise_elder",
        "specialty": "sword_cultivation",
        "backstory": "Ancient sword master who ascended from humble beginnings",
        "dialogue_style": "formal_wise",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["ancient_scroll", "spirit_sword", "cultivation_manual"],
        "gifts_hated": ["demon_core", "cursed_item"],
        "relationship_status": "mentor"
    },
    "li_feng": {
        "name": "Li Feng",
        "gender": "male", 
        "emoji": "🧑‍💼",
        "cultivation_level": 35,
        "realm": "Mortal Realm",
        "personality": "business_minded",
        "specialty": "alchemy",
        "backstory": "Brilliant alchemist who turned cultivation into profit",
        "dialogue_style": "business_casual",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["rare_herbs", "spirit_stones", "gold"],
        "gifts_hated": ["cheap_items", "common_herbs"],
        "relationship_status": "acquaintance"
    },
    "zhao_ming": {
        "name": "Zhao Ming",
        "gender": "male",
        "emoji": "⚔️",
        "cultivation_level": 60,
        "realm": "Immortal Realm", 
        "personality": "battle_hungry",
        "specialty": "combat_techniques",
        "backstory": "Former demon slayer seeking stronger opponents",
        "dialogue_style": "aggressive_confident",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["weapons", "battle_manuals", "monster_cores"],
        "gifts_hated": ["peace_offerings", "defensive_items"],
        "relationship_status": "rival"
    },
    "wang_jun": {
        "name": "Wang Jun",
        "gender": "male",
        "emoji": "📚",
        "cultivation_level": 40,
        "realm": "Mortal Realm",
        "personality": "scholarly",
        "specialty": "formation_arrays",
        "backstory": "Scholar obsessed with ancient cultivation formations",
        "dialogue_style": "intellectual_verbose",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["ancient_texts", "formation_stones", "research_materials"],
        "gifts_hated": ["weapons", "crude_items"],
        "relationship_status": "mentor"
    },
    "liu_han": {
        "name": "Liu Han",
        "gender": "male",
        "emoji": "🌿",
        "cultivation_level": 25,
        "realm": "Mortal Realm",
        "personality": "nature_lover",
        "specialty": "beast_taming",
        "backstory": "Beast tamer who communicates with spirit animals",
        "dialogue_style": "gentle_nature",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["spirit_beasts", "natural_items", "beast_cores"],
        "gifts_hated": ["artificial_items", "demon_items"],
        "relationship_status": "friend"
    },
    "sun_lei": {
        "name": "Sun Lei",
        "gender": "male",
        "emoji": "⚡",
        "cultivation_level": 55,
        "realm": "Immortal Realm",
        "personality": "hot_tempered",
        "specialty": "lightning_cultivation",
        "backstory": "Lightning cultivator with explosive personality",
        "dialogue_style": "brash_energetic",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["lightning_crystals", "storm_items", "energy_cores"],
        "gifts_hated": ["earth_items", "slow_items"],
        "relationship_status": "acquaintance"
    },
    "ma_tian": {
        "name": "Ma Tian",
        "gender": "male",
        "emoji": "🗡️",
        "cultivation_level": 70,
        "realm": "Immortal Realm",
        "personality": "silent_assassin",
        "specialty": "stealth_techniques",
        "backstory": "Former assassin seeking redemption through cultivation",
        "dialogue_style": "brief_mysterious",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["shadow_items", "stealth_gear", "poison_antidotes"],
        "gifts_hated": ["loud_items", "bright_items"],
        "relationship_status": "mysterious"
    },
    "xu_bin": {
        "name": "Xu Bin",
        "gender": "male",
        "emoji": "🎭",
        "cultivation_level": 30,
        "realm": "Mortal Realm",
        "personality": "joker",
        "specialty": "illusion_arts",
        "backstory": "Trickster who uses illusions to confuse enemies",
        "dialogue_style": "playful_humorous",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["joke_items", "illusion_crystals", "entertainment"],
        "gifts_hated": ["serious_items", "boring_gifts"],
        "relationship_status": "friend"
    },
    "tang_hao": {
        "name": "Tang Hao",
        "gender": "male",
        "emoji": "🔥",
        "cultivation_level": 50,
        "realm": "Immortal Realm",
        "personality": "passionate",
        "specialty": "fire_cultivation", 
        "backstory": "Fire cultivator with burning passion for perfection",
        "dialogue_style": "intense_passionate",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["fire_crystals", "flame_items", "passion_gifts"],
        "gifts_hated": ["ice_items", "water_items"],
        "relationship_status": "acquaintance"
    },
    "gu_yun": {
        "name": "Gu Yun",
        "gender": "male",
        "emoji": "☯️",
        "cultivation_level": 80,
        "realm": "God Realm",
        "personality": "balanced_sage",
        "specialty": "dao_comprehension",
        "backstory": "Sage who achieved perfect balance between yin and yang",
        "dialogue_style": "philosophical_balanced",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["yin_yang_items", "balance_crystals", "dao_texts"],
        "gifts_hated": ["extreme_items", "chaotic_items"],
        "relationship_status": "sage"
    },
    
    # Female NPCs
    "mei_ling": {
        "name": "Mei Ling",
        "gender": "female",
        "emoji": "👩‍🦳",
        "cultivation_level": 65,
        "realm": "Immortal Realm",
        "personality": "ice_queen",
        "specialty": "ice_cultivation",
        "backstory": "Ice empress who rules over frozen domains",
        "dialogue_style": "cold_regal",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["ice_crystals", "winter_items", "elegant_gifts"],
        "gifts_hated": ["fire_items", "crude_gifts"],
        "relationship_status": "cold"
    },
    "xiao_yu": {
        "name": "Xiao Yu",
        "gender": "female",
        "emoji": "🌸",
        "cultivation_level": 28,
        "realm": "Mortal Realm",
        "personality": "gentle_healer",
        "specialty": "healing_arts",
        "backstory": "Gentle healer who saved countless lives",
        "dialogue_style": "soft_caring",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["healing_herbs", "life_crystals", "peaceful_items"],
        "gifts_hated": ["weapons", "violent_items"],
        "relationship_status": "friend"
    },
    "feng_yue": {
        "name": "Feng Yue",
        "gender": "female",
        "emoji": "🌙",
        "cultivation_level": 45,
        "realm": "Immortal Realm",
        "personality": "mysterious_beauty",
        "specialty": "moon_cultivation",
        "backstory": "Moon goddess descendant with ethereal beauty",
        "dialogue_style": "elegant_mysterious",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["moon_stones", "night_items", "beauty_items"],
        "gifts_hated": ["sun_items", "ugly_items"],
        "relationship_status": "mysterious"
    },
    "lan_xue": {
        "name": "Lan Xue",
        "gender": "female",
        "emoji": "❄️",
        "cultivation_level": 52,
        "realm": "Immortal Realm",
        "personality": "proud_warrior",
        "specialty": "sword_and_snow",
        "backstory": "Proud sword maiden who never lost a duel",
        "dialogue_style": "proud_confident",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["legendary_swords", "honor_items", "victory_tokens"],
        "gifts_hated": ["defeat_items", "dishonor_gifts"],
        "relationship_status": "rival"
    },
    "hua_rong": {
        "name": "Hua Rong",
        "gender": "female",
        "emoji": "🌺",
        "cultivation_level": 38,
        "realm": "Mortal Realm",
        "personality": "flower_maiden",
        "specialty": "plant_cultivation",
        "backstory": "Flower spirit who became human through cultivation",
        "dialogue_style": "flowery_sweet",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["rare_flowers", "garden_items", "nature_gifts"],
        "gifts_hated": ["poison_items", "withered_items"],
        "relationship_status": "friend"
    },
    "yun_xi": {
        "name": "Yun Xi",
        "gender": "female",
        "emoji": "☁️",
        "cultivation_level": 48,
        "realm": "Immortal Realm",
        "personality": "free_spirit",
        "specialty": "wind_cultivation",
        "backstory": "Free-spirited cultivator who travels the skies",
        "dialogue_style": "carefree_wandering",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["wind_crystals", "travel_items", "freedom_gifts"],
        "gifts_hated": ["chains", "binding_items"],
        "relationship_status": "friend"
    },
    "zi_yan": {
        "name": "Zi Yan",
        "gender": "female",
        "emoji": "🔮",
        "cultivation_level": 42,
        "realm": "Immortal Realm",
        "personality": "mystic_seer",
        "specialty": "divination",
        "backstory": "Oracle who can see fragments of the future",
        "dialogue_style": "mystical_prophetic",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["crystal_balls", "prophecy_items", "mystic_gifts"],
        "gifts_hated": ["mundane_items", "reality_items"],
        "relationship_status": "mysterious"
    },
    "ning_er": {
        "name": "Ning Er",
        "gender": "female",
        "emoji": "🎵",
        "cultivation_level": 35,
        "realm": "Mortal Realm",
        "personality": "musical_artist",
        "specialty": "sound_cultivation",
        "backstory": "Musician who weaponized sound through cultivation",
        "dialogue_style": "melodic_artistic",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["musical_items", "sound_crystals", "art_gifts"],
        "gifts_hated": ["silence_items", "noise_items"],
        "relationship_status": "friend"
    },
    "bai_su": {
        "name": "Bai Su",
        "gender": "female",
        "emoji": "🏺",
        "cultivation_level": 33,
        "realm": "Mortal Realm",
        "personality": "alchemist_genius",
        "specialty": "pill_refinement",
        "backstory": "Genius alchemist who creates miraculous pills",
        "dialogue_style": "scientific_precise",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["rare_ingredients", "alchemy_tools", "research_items"],
        "gifts_hated": ["impure_items", "contaminated_gifts"],
        "relationship_status": "colleague"
    },
    "qing_lian": {
        "name": "Qing Lian",
        "gender": "female",
        "emoji": "💎",
        "cultivation_level": 75,
        "realm": "God Realm",
        "personality": "jade_empress",
        "specialty": "jade_cultivation",
        "backstory": "Empress who rules over jade mountains and crystal valleys",
        "dialogue_style": "imperial_majestic",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["precious_jade", "imperial_items", "luxury_gifts"],
        "gifts_hated": ["common_items", "peasant_gifts"],
        "relationship_status": "royalty"
    }
}

# Affection thresholds for relationship changes
AFFECTION_THRESHOLDS = {
    0: "stranger",
    10: "acquaintance", 
    25: "friend",
    50: "close_friend",
    75: "beloved",
    90: "soulmate"
}

# NPC interaction data storage
NPC_INTERACTIONS = {}

async def query_ai_for_npc_dialogue(npc_data, player_data, context="general"):
    """Generate AI-driven dialogue for NPCs"""
    HF_TOKEN = os.environ.get("HUGGING_FACE_TOKEN", "")
    if not HF_TOKEN:
        return generate_fallback_dialogue(npc_data, context)
    
    prompt = f"""You are {npc_data['name']}, a {npc_data['personality']} {npc_data['gender']} cultivator in the {npc_data['realm']}. 

Background: {npc_data['backstory']}
Specialty: {npc_data['specialty']}
Dialogue Style: {npc_data['dialogue_style']}
Current Affection: {npc_data['affection_level']}/100
Relationship: {npc_data['relationship_status']}

Context: {context}

Respond as this character would, staying true to their personality and current relationship level. Keep response under 100 words and make it immersive for a cultivation world."""

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 150,
                "temperature": 0.8,
                "do_sample": True
            }
        }
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post("https://api-inference.huggingface.co/models/microsoft/DialoGPT-large", 
                                  headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated = result[0].get("generated_text", "")
                        return generated.replace(prompt, "").strip()
        
        return generate_fallback_dialogue(npc_data, context)
    except:
        return generate_fallback_dialogue(npc_data, context)

def generate_fallback_dialogue(npc_data, context):
    """Generate fallback dialogue when AI is unavailable"""
    personality = npc_data['personality']
    name = npc_data['name']
    affection = npc_data['affection_level']
    
    # Personality-based responses
    responses = {
        "wise_elder": [
            f"Young cultivator, the path of cultivation requires patience and wisdom.",
            f"I sense great potential in you. Continue your training diligently.",
            f"The dao is vast and mysterious. Seek understanding, not just power."
        ],
        "business_minded": [
            f"Ah, a potential customer! What brings you to my establishment?",
            f"Everything has a price in this world. What are you willing to pay?",
            f"Business is about mutual benefit. How can we help each other?"
        ],
        "battle_hungry": [
            f"You look strong! Want to spar and test your abilities?",
            f"The thrill of battle is what makes cultivation worthwhile!",
            f"Show me your techniques! I'm always eager for a good fight!"
        ],
        "ice_queen": [
            f"What brings you before me, mortal?",
            f"Your presence disturbs my meditation. Speak quickly.",
            f"Few dare to approach the Ice Empress. You have courage."
        ],
        "gentle_healer": [
            f"Are you injured? I can help heal your wounds.",
            f"Peace and compassion are the highest virtues.",
            f"Every life is precious. I'm here to help if you need it."
        ]
    }
    
    # Adjust based on affection level
    if affection >= 75:
        return f"{random.choice(responses.get(personality, ['Hello there.']))} (You notice {name} looks at you with deep affection.)"
    elif affection >= 50:
        return f"{random.choice(responses.get(personality, ['Hello there.']))} (You sense {name} truly cares about you.)"
    elif affection >= 25:
        return f"{random.choice(responses.get(personality, ['Hello there.']))} ({name} seems friendly towards you.)"
    else:
        return f"{random.choice(responses.get(personality, ['Hello there.']))} ({name} regards you neutrally.)"

def calculate_affection_change(npc_data, action_type, gift_item=None):
    """Calculate how much affection changes based on player actions"""
    change = 0
    
    if action_type == "talk":
        change = random.randint(1, 3)  # Small gain from talking
    elif action_type == "gift" and gift_item:
        if gift_item in npc_data["gifts_loved"]:
            change = random.randint(8, 15)  # Big gain for loved gifts
        elif gift_item in npc_data["gifts_hated"]:
            change = random.randint(-10, -5)  # Loss for hated gifts
        else:
            change = random.randint(2, 5)  # Moderate gain for neutral gifts
    elif action_type == "quest_complete":
        change = random.randint(5, 10)  # Good gain for completing quests
    elif action_type == "insult":
        change = random.randint(-15, -8)  # Big loss for insults
    
    return change

def get_npc_data(player_id, npc_id):
    """Get NPC data for a specific player (tracks individual relationships)"""
    if player_id not in NPC_INTERACTIONS:
        NPC_INTERACTIONS[player_id] = {}
    
    if npc_id not in NPC_INTERACTIONS[player_id]:
        # Initialize with base NPC data
        NPC_INTERACTIONS[player_id][npc_id] = NPCS[npc_id].copy()
    
    return NPC_INTERACTIONS[player_id][npc_id]

def update_npc_affection(player_id, npc_id, change):
    """Update NPC affection and relationship status"""
    npc_data = get_npc_data(player_id, npc_id)
    
    old_affection = npc_data["affection_level"]
    npc_data["affection_level"] = max(0, min(100, old_affection + change))
    
    # Update relationship status based on affection
    new_affection = npc_data["affection_level"]
    for threshold, status in reversed(list(AFFECTION_THRESHOLDS.items())):
        if new_affection >= threshold:
            npc_data["relationship_status"] = status
            break
    
    return old_affection, new_affection

def save_npc_data():
    """Save NPC interaction data to file"""
    try:
        with open("npc_data.json", "w") as f:
            json.dump(NPC_INTERACTIONS, f, indent=2)
    except Exception as e:
        print(f"Error saving NPC data: {e}")

def load_npc_data():
    """Load NPC interaction data from file"""
    global NPC_INTERACTIONS
    try:
        with open("npc_data.json", "r") as f:
            NPC_INTERACTIONS = json.load(f)
    except FileNotFoundError:
        NPC_INTERACTIONS = {}
    except Exception as e:
        print(f"Error loading NPC data: {e}")
        NPC_INTERACTIONS = {}

# Initialize NPC data on import
load_npc_data()