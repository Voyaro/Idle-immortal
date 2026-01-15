import discord
import random
import asyncio
import time
import math
from utils import load_data, save_data, calculate_set_bonus

# ===============================
# BOSS DATA - REWARD EXP DIATAS 500.000! NO LEVEL REQUIREMENT!
# ===============================
BOSSES = {
    "ancient_dragon": {
        "name": "Ancient Dragon",
        "emoji": "🐉",
        "level": 1,  # No level requirement
        "health": 10000,
        "damage": (600, 800),
        "reward_exp": 10000000,  # 2x boost (was 5M)
        "reward_qi": 10000,
        "reward_stones": 6000,
        "element": "fire",
        "weakness": "water",
        "description": "Naga kuno yang menjaga gunung berapi",
        "phases": 3,
        "special_attacks": [
            {"name": "Fire Breath", "damage_multiplier": 1.5, "description": "Napas api yang membakar"},
            {"name": "Tail Swipe", "damage_multiplier": 1.2, "description": "Sabetan ekor yang mematikan"},
            {"name": "Dive Bomb", "damage_multiplier": 2.0, "description": "Serangan udara yang menghancurkan"}
        ]
    },
    "celestial_phoenix": {
        "name": "Celestial Phoenix", 
        "emoji": "🔥",
        "level": 1,  # No level requirement
        "health": 20000,
        "damage": (1000, 1500),
        "reward_exp": 15000000,  # 2x boost (was 7.5M)
        "reward_qi": 16000, 
        "reward_stones": 12000,
        "element": "light",
        "weakness": "dark",
        "description": "Burung phoenix suci dari langit",
        "phases": 4,
        "special_attacks": [
            {"name": "Solar Flare", "damage_multiplier": 1.8, "description": "Ledakan energi matahari"},
            {"name": "Divine Wind", "damage_multiplier": 1.3, "description": "Angin suci yang menyapu"},
            {"name": "Rebirth", "damage_multiplier": 0.5, "description": "Menyembuhkan diri dan kembali kuat"}
        ]
    },
    "abyssal_kraken": {
        "name": "Abyssal Kraken",
        "emoji": "🐙", 
        "level": 1,  # No level requirement
        "health": 300000,
        "damage": (2000, 2500),
        "reward_exp": 20000000,  # 2x boost (was 10M)
        "reward_qi": 24000,
        "reward_stones": 20000,
        "element": "water",
        "weakness": "lightning", 
        "description": "Monster laut dari kedalaman abyss",
        "phases": 5,
        "special_attacks": [
            {"name": "Tentacle Crush", "damage_multiplier": 1.6, "description": "Hantaman tentakel yang menghancurkan"},
            {"name": "Ink Cloud", "damage_multiplier": 1.0, "description": "Awan tinta yang mengurangi akurasi"},
            {"name": "Tsunami", "damage_multiplier": 2.2, "description": "Gelombang raksasa yang menyapu"}
        ]
    },
    "void_titan": {
        "name": "Void Titan",
        "emoji": "🌌",
        "level": 1,  # No level requirement
        "health": 40000,
        "damage": (4000, 5000),
        "reward_exp": 40000000,  # 2x boost (was 20M)
        "reward_qi": 30000,
        "reward_stones": 24000,
        "element": "void",
        "weakness": "light",
        "description": "Titan dari dimensi void yang menguasai kegelapan",
        "phases": 6,
        "special_attacks": [
            {"name": "Void Crush", "damage_multiplier": 2.5, "description": "Serangan void yang menghancurkan realitas"},
            {"name": "Dark Matter", "damage_multiplier": 2.0, "description": "Materi gelap yang menyerap energi"},
            {"name": "Reality Tear", "damage_multiplier": 3.0, "description": "Merobek dimensi untuk serangan dahsyat"}
        ]
    },
    "eternal_dragon": {
        "name": "Eternal Dragon",
        "emoji": "🐲",
        "level": 1,
        "health": 60000,
        "damage": (6000, 8000),
        "reward_exp": 60000000,  # 2x boost (was 30M)
        "reward_qi": 40000,
        "reward_stones": 36000,
        "element": "time",
        "weakness": "space",
        "description": "Naga abadi yang menguasai waktu dan takdir",
        "phases": 7,
        "special_attacks": [
            {"name": "Time Stop", "damage_multiplier": 2.8, "description": "Menghentikan waktu untuk serangan mematikan"},
            {"name": "Fate Slash", "damage_multiplier": 3.2, "description": "Memotong garis takdir musuh"},
            {"name": "Temporal Burst", "damage_multiplier": 4.0, "description": "Ledakan energi temporal"}
        ]
    },
    "chaos_emperor": {
        "name": "Chaos Emperor",
        "emoji": "👑",
        "level": 1,
        "health": 80000,
        "damage": (8000, 12000),
        "reward_exp": 100000000,  # 2x boost (was 50M)
        "reward_qi": 60000,
        "reward_stones": 50000,
        "element": "chaos",
        "weakness": "order",
        "description": "Kaisar chaos yang menguasai kekacauan primordial",
        "phases": 8,
        "special_attacks": [
            {"name": "Chaos Storm", "damage_multiplier": 3.5, "description": "Badai chaos yang mengacak realitas"},
            {"name": "Disorder Wave", "damage_multiplier": 3.0, "description": "Gelombang yang menciptakan kekacauan"},
            {"name": "Primordial Wrath", "damage_multiplier": 5.0, "description": "Murka primordial yang menghancurkan segalanya"}
        ]
    },
    "cosmic_sovereign": {
        "name": "Cosmic Sovereign",
        "emoji": "🌠",
        "level": 1,
        "health": 100000,
        "damage": (10000, 15000),
        "reward_exp": 150000000,  # 2x boost (was 75M)
        "reward_qi": 80000,
        "reward_stones": 70000,
        "element": "cosmic",
        "weakness": "mortal",
        "description": "Penguasa cosmic yang mengendalikan seluruh alam semesta",
        "phases": 10,
        "special_attacks": [
            {"name": "Galaxy Crusher", "damage_multiplier": 4.0, "description": "Menghancurkan galaksi dengan satu pukulan"},
            {"name": "Star Collapse", "damage_multiplier": 4.5, "description": "Meruntuhkan bintang-bintang"},
            {"name": "Universe Domination", "damage_multiplier": 6.0, "description": "Dominasi universal yang absolut"}
        ]
    },
    "infinity_sage": {
        "name": "Infinity Sage",
        "emoji": "♾️",
        "level": 1,
        "health": 150000,
        "damage": (15000, 20000),
        "reward_exp": 200000000,  # 2x boost (was 100M)
        "reward_qi": 100000,
        "reward_stones": 90000,
        "element": "infinity",
        "weakness": "finite",
        "description": "Sage tak terbatas yang mencapai pencerahan ultimate",
        "phases": 12,
        "special_attacks": [
            {"name": "Infinite Wisdom", "damage_multiplier": 5.0, "description": "Kebijaksanaan tak terbatas yang menghancurkan ignorance"},
            {"name": "Eternal Truth", "damage_multiplier": 5.5, "description": "Kebenaran abadi yang absolute"},
            {"name": "Transcendent Strike", "damage_multiplier": 8.0, "description": "Serangan yang melampaui segala batasan"}
        ]
    },
    "infinity_dragon": {
        "name": "Infinity Dragon",
        "emoji": "∞",
        "level": 1,  # No level requirement
        "health": 300000,
        "damage": (30000, 70000),
        "reward_exp": 500000000,  # 2x boost (was 5M)
        "reward_qi": 60000,
        "reward_stones": 40000,
        "element": "all",
        "weakness": "none",
        "description": "Dragon legendaris dengan kekuatan tak terbatas",
        "phases": 7,
        "special_attacks": [
            {"name": "Infinity Breath", "damage_multiplier": 2.8, "description": "Napas kekuatan tak terbatas"},
            {"name": "Reality Tear", "damage_multiplier": 3.2, "description": "Mengoyak realitas"},
            {"name": "Eternal End", "damage_multiplier": 4.0, "description": "Akhir yang kekal"}
        ]
    }
}

BOSS_LOOT_TABLE = {
    "Ancient Dragon": [
        {"id": "dragon_scale", "name": "Dragon Scale", "emoji": "🐉", "chance": 0.6},
        {"id": "dragon_heart", "name": "Dragon Heart", "emoji": "❤️", "chance": 0.3},
        {"id": "fire_crystal", "name": "Fire Crystal", "emoji": "🔴", "chance": 0.4}
    ],
    "Celestial Phoenix": [
        {"id": "phoenix_feather", "name": "Phoenix Feather", "emoji": "🪶", "chance": 0.5},
        {"id": "solar_essence", "name": "Solar Essence", "emoji": "☀️", "chance": 0.4},
        {"id": "divine_ember", "name": "Divine Ember", "emoji": "✨", "chance": 0.3}
    ],
    "Abyssal Kraken": [
        {"id": "kraken_tentacle", "name": "Kraken Tentacle", "emoji": "🐙", "chance": 0.7},
        {"id": "abyssal_pearl", "name": "Abyssal Pearl", "emoji": "🔵", "chance": 0.2},
        {"id": "water_orb", "name": "Water Orb", "emoji": "💧", "chance": 0.5}
    ],
    "Void Titan": [
        {"id": "void_shard", "name": "Void Shard", "emoji": "💠", "chance": 0.5},
        {"id": "titan_core", "name": "Titan Core", "emoji": "⚙️", "chance": 0.3},
        {"id": "cosmic_dust", "name": "Cosmic Dust", "emoji": "✨", "chance": 0.6}
    ],
    "Infinity Dragon": [
        {"id": "infinity_fragment", "name": "Infinity Fragment", "emoji": "∞", "chance": 0.4},
        {"id": "dragon_soul", "name": "Dragon Soul", "emoji": "💎", "chance": 0.2},
        {"id": "eternity_crystal", "name": "Eternity Crystal", "emoji": "🔶", "chance": 0.1}
    ]
}

# Active boss battles
ACTIVE_BOSS_BATTLES = {}

# Realm order untuk level calculation
REALMS = {
    "Mortal Realm": {"stages": ["Body Refining [Entry]", "Body Refining [Middle]", "Body Refining [Peak]"]},
    "Immortal Realm": {"stages": ["Half-Immortal [Entry]", "Half-Immortal [Middle]", "Half-Immortal [Peak]"]},
    "God Realm": {"stages": ["Lesser God [Entry]", "Lesser God [Middle]", "Lesser God [Peak]"]}
}

# ===============================
# BOSS FUNCTIONS
# ===============================
def get_player(player_id):
    """Dapatkan player data dari utils"""
    data = load_data()
    return data["players"].get(str(player_id))

def update_player(player_id, player_data):
    """Update player data melalui utils"""
    data = load_data()
    data["players"][str(player_id)] = player_data
    return save_data(data)

async def list_bosses(ctx):
    """List semua boss yang available"""
    embed = discord.Embed(title="🐲 LEGENDARY BOSSES 🐲", color=0xff0000)
    
    for boss_id, boss_data in BOSSES.items():
        embed.add_field(
            name=f"{boss_data['emoji']} {boss_data['name']}",
            value=f"{boss_data['description']}\n"
                  f"**Health:** {boss_data['health']} | **Damage:** {boss_data['damage'][0]}-{boss_data['damage'][1]}\n"
                  f"**Element:** {boss_data['element']} | **Weakness:** {boss_data['weakness']}\n"
                  f"**Rewards:** {boss_data['reward_exp']:,} EXP, {boss_data['reward_qi']} Qi, {boss_data['reward_stones']} Stones\n"
                  f"**Command:** `!boss challenge {boss_data['name'].lower()}`",
            inline=False
        )
    
    embed.set_footer(text="🚀 NO LEVEL REQUIREMENT! Semua player bisa challenge!")
    await ctx.send(embed=embed)

async def show_boss_info(ctx):
    """Show boss system info"""
    embed = discord.Embed(
        title="🐲 LEGENDARY BOSS SYSTEM",
        description="Tantang boss LEGENDARY untuk mendapatkan REWARD BESAR!",
        color=0xff0000
    )
    
    embed.add_field(
        name="📋 Commands",
        value="`!boss list` - Lihat semua boss\n"
              "`!boss challenge [nama]` - Tantang boss\n"
              "`!boss cooldown` - Lihat cooldown boss\n"
              "`!boss status` - Status battle sedang berlangsung",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Features",
        value="• 🚀 **NO LEVEL REQUIREMENT** - Semua player bisa challenge!\n"
              "• 💰 **REWARD BESAR** - EXP diatas 500.000!\n"
              "• ⚔️ **ELEMENT SYSTEM** - Gunakan element advantage\n"
              "• 🎁 **RARE LOOT** - Dapatkan item langka\n"
              "• ⏰ **24H COOLDOWN** - Setelah menang",
        inline=False
    )
    
    await ctx.send(embed=embed)

async def challenge_boss(ctx, boss_name):
    """Tantang boss tertentu"""
    player_id = ctx.author.id
    p = get_player(player_id)
    
    if not p:
        return await ctx.send("❌ Anda belum terdaftar! Gunakan `!register` dulu.")
    
    # Cari boss - FLEXIBLE MATCHING
    boss_data = None
    boss_name_lower = boss_name.lower().replace(" ", "_")
    
    for boss_id, data in BOSSES.items():
        # Check multiple variations
        if (data["name"].lower() == boss_name.lower() or
            boss_id == boss_name_lower or
            data["name"].lower().replace(" ", "") == boss_name.lower().replace(" ", "") or
            any(word in data["name"].lower() for word in boss_name.lower().split()) or
            boss_name.lower() in data["name"].lower()):
            boss_data = data
            break
    
    if not boss_data:
        available_bosses = ", ".join([data["name"] for data in BOSSES.values()])
        return await ctx.send(f"❌ Boss '{boss_name}' tidak ditemukan! Boss available: {available_bosses}")
    
    # 🚀 NO LEVEL REQUIREMENT CHECK - DIHAPUS!
    # Semua player bisa challenge regardless of level!
    
    # Check cooldown
    last_challenge = p.get("last_boss_challenge", {}).get(boss_data["name"], 0)
    current_time = time.time()
    cooldown_remaining = 86400 - (current_time - last_challenge)
    
    if cooldown_remaining > 0:
        hours = int(cooldown_remaining // 3600)
        minutes = int((cooldown_remaining % 3600) // 60)
        return await ctx.send(f"⏰ Boss masih cooldown! Coba lagi dalam {hours} jam {minutes} menit.")
    
    # Check if already in battle
    battle_id = f"boss_{player_id}"
    if battle_id in ACTIVE_BOSS_BATTLES:
        return await ctx.send("❌ Anda sudah sedang dalam boss battle!")
    
    # Start boss battle
    ACTIVE_BOSS_BATTLES[battle_id] = {
        "player_id": player_id,
        "boss_name": boss_data["name"],
        "boss_data": boss_data,
        "boss_health": boss_data["health"],
        "player_health": 1000,
        "phase": 1,
        "round": 0,
        "start_time": current_time,
        "message": None,
        "log": []
    }
    
    # Add battle log
    ACTIVE_BOSS_BATTLES[battle_id]["log"].append(f"⚔️ Battle dimulai! {ctx.author.name} vs {boss_data['name']}")
    
    # Kirim battle embed
    embed = create_boss_battle_embed(battle_id, ctx)
    message = await ctx.send(embed=embed)
    ACTIVE_BOSS_BATTLES[battle_id]["message"] = message
    
    # Start battle task
    asyncio.create_task(boss_battle_task(battle_id, ctx))

def create_boss_battle_embed(battle_id, ctx):
    """Buat embed untuk boss battle"""
    battle_data = ACTIVE_BOSS_BATTLES[battle_id]
    boss_data = battle_data["boss_data"]
    
    embed = discord.Embed(
        title=f"🐲 {boss_data['name']} Battle",
        description=f"Phase {battle_data['phase']}/{boss_data['phases']} - Round {battle_data['round']}",
        color=0xff0000
    )
    
    # Health bars
    boss_hp_percent = (battle_data["boss_health"] / boss_data["health"]) * 100
    player_hp_percent = (battle_data["player_health"] / 1000) * 100
    
    embed.add_field(
        name=f"{boss_data['emoji']} {boss_data['name']}",
        value=f"{create_health_bar(boss_hp_percent)} {battle_data['boss_health']}/{boss_data['health']} HP",
        inline=False
    )
    
    embed.add_field(
        name=f"🧘 {ctx.author.name}",
        value=f"{create_health_bar(player_hp_percent)} {battle_data['player_health']}/1000 HP",
        inline=False
    )
    
    # Battle log (last 3 events)
    if battle_data["log"]:
        log_text = "\n".join(battle_data["log"][-3:])
        embed.add_field(name="📜 Battle Log", value=log_text, inline=False)
    
    # Element info
    embed.add_field(
        name="⚡ Element Info",
        value=f"**Boss Element:** {boss_data['element']}\n**Weakness:** {boss_data['weakness']}",
        inline=True
    )
    
    # Reward preview
    embed.add_field(
        name="💰 Reward",
        value=f"**EXP:** {boss_data['reward_exp']:,}\n**Qi:** {boss_data['reward_qi']}\n**Stones:** {boss_data['reward_stones']}",
        inline=True
    )
    
    return embed

def create_health_bar(percentage):
    """Buat health bar visual"""
    filled = int(percentage / 10)
    return "█" * filled + "░" * (10 - filled)

async def boss_battle_task(battle_id, ctx):
    """Background task untuk boss battle"""
    try:
        battle_data = ACTIVE_BOSS_BATTLES[battle_id]
        
        while (battle_id in ACTIVE_BOSS_BATTLES and 
               battle_data["boss_health"] > 0 and 
               battle_data["player_health"] > 0):
            
            await boss_battle_round(battle_id, ctx)
            await asyncio.sleep(3)
            
            # Update battle data reference
            if battle_id not in ACTIVE_BOSS_BATTLES:
                break
            battle_data = ACTIVE_BOSS_BATTLES[battle_id]
        
        # Battle finished
        victory = battle_data["boss_health"] <= 0
        await finish_boss_battle(battle_id, ctx, victory)
        
    except Exception as e:
        print(f"Error in boss battle task: {e}")
    finally:
        if battle_id in ACTIVE_BOSS_BATTLES:
            del ACTIVE_BOSS_BATTLES[battle_id]

async def boss_battle_round(battle_id, ctx):
    """Satu round boss battle"""
    battle_data = ACTIVE_BOSS_BATTLES[battle_id]
    boss_data = battle_data["boss_data"]
    player_id = battle_data["player_id"]
    
    battle_data["round"] += 1
    
    # Player attack
    p = get_player(player_id)
    player_damage = calculate_player_damage(p, boss_data)
    battle_data["boss_health"] = max(0, battle_data["boss_health"] - player_damage)
    
    # Add to log
    element_emoji = get_element_emoji(p)
    battle_data["log"].append(f"{element_emoji} {ctx.author.name} attacks for **{player_damage} damage**!")
    
    # Check if boss defeated
    if battle_data["boss_health"] <= 0:
        return
    
    # Boss attack
    boss_damage = calculate_boss_damage(boss_data, battle_data["phase"])
    battle_data["player_health"] = max(0, battle_data["player_health"] - boss_damage)
    
    # Special attack chance
    if random.random() < 0.3:
        special_attack = random.choice(boss_data["special_attacks"])
        special_damage = int(boss_damage * special_attack["damage_multiplier"])
        battle_data["player_health"] = max(0, battle_data["player_health"] - (special_damage - boss_damage))
        battle_data["log"].append(f"⚡ {boss_data['name']} uses **{special_attack['name']}**! {special_attack['description']}")
    
    # Phase transition
    phase_health_threshold = boss_data["health"] * (1 - (battle_data["phase"] / boss_data["phases"]))
    if battle_data["boss_health"] < phase_health_threshold and battle_data["phase"] < boss_data["phases"]:
        battle_data["phase"] += 1
        battle_data["log"].append(f"🌪️ **PHASE {battle_data['phase']}**! {boss_data['name']} becomes more aggressive!")
    
    # Update message
    try:
        embed = create_boss_battle_embed(battle_id, ctx)
        await battle_data["message"].edit(embed=embed)
    except:
        pass

def calculate_player_damage(player_data, boss_data):
    """Hitung damage player ke boss"""
    base_damage = player_data["total_power"]
    
    # Element advantage
    element_advantage = get_element_advantage(player_data, boss_data["element"])
    if element_advantage > 1:
        base_damage = int(base_damage * element_advantage)
    
    # Random variation
    damage = random.randint(int(base_damage * 0.8), int(base_damage * 1.2))
    return max(10, damage)

def calculate_boss_damage(boss_data, phase):
    """Hitung damage boss ke player"""
    min_dmg, max_dmg = boss_data["damage"]
    
    # Phase multiplier
    phase_multiplier = 1 + ((phase - 1) * 0.3)
    min_dmg = int(min_dmg * phase_multiplier)
    max_dmg = int(max_dmg * phase_multiplier)
    
    return random.randint(min_dmg, max_dmg)

def get_element_advantage(player_data, boss_element):
    """Dapatkan element advantage multiplier"""
    element_relations = {
        "fire": {"weakness": "water", "strength": "wind"},
        "water": {"weakness": "lightning", "strength": "fire"},
        "wind": {"weakness": "earth", "strength": "lightning"},
        "earth": {"weakness": "fire", "strength": "water"},
        "lightning": {"weakness": "earth", "strength": "wind"},
        "light": {"weakness": "dark", "strength": "dark"},
        "dark": {"weakness": "light", "strength": "light"},
        "ice": {"weakness": "fire", "strength": "wind"},
        "all": {"weakness": "none", "strength": "all"},
        "none": {"weakness": "all", "strength": "none"}
    }
    
    # Check player techniques for elements
    player_elements = set()
    for technique in player_data.get("techniques", []):
        player_elements.add(technique.get("element", "neutral"))
    
    # Check for advantage
    for element in player_elements:
        if element in element_relations:
            if element_relations[element]["strength"] == boss_element:
                return 1.5
            elif element_relations[element]["weakness"] == boss_element:
                return 0.7
    
    return 1.0

def get_element_emoji(player_data):
    """Dapatkan element emoji berdasarkan techniques"""
    element_emojis = {
        "fire": "🔥", "water": "💧", "wind": "💨", "earth": "🌍",
        "lightning": "⚡", "light": "✨", "dark": "🌙", "ice": "❄️",
        "all": "∞", "none": "⚫"
    }
    
    for technique in player_data.get("techniques", []):
        element = technique.get("element")
        if element in element_emojis:
            return element_emojis[element]
    
    return "⚔️"

def get_boss_loot(boss_name):
    """Dapatkan random loot dari boss"""
    if boss_name not in BOSS_LOOT_TABLE:
        return None
    
    for loot_item in BOSS_LOOT_TABLE[boss_name]:
        if random.random() < loot_item["chance"]:
            return loot_item
    
    return None

async def finish_boss_battle(battle_id, ctx, victory):
    """Selesaikan boss battle dan berikan rewards"""
    battle_data = ACTIVE_BOSS_BATTLES[battle_id]
    player_id = battle_data["player_id"]
    boss_data = battle_data["boss_data"]
    
    p = get_player(player_id)
    
    if victory:
        # VICTORY REWARDS
        rewards = {
            "exp": boss_data["reward_exp"],
            "qi": boss_data["reward_qi"],
            "spirit_stones": boss_data["reward_stones"]
        }
        
        p["exp"] += rewards["exp"]
        p["qi"] += rewards["qi"]
        p["spirit_stones"] += rewards["spirit_stones"]
        
        # Track boss defeat
        if "bosses_defeated" not in p:
            p["bosses_defeated"] = []
        if boss_data["name"] not in p["bosses_defeated"]:
            p["bosses_defeated"].append(boss_data["name"])
        
        # Set cooldown
        if "last_boss_challenge" not in p:
            p["last_boss_challenge"] = {}
        p["last_boss_challenge"][boss_data["name"]] = time.time()
        
        # Random loot
        loot = get_boss_loot(boss_data["name"])
        if loot:
            p["inventory"][loot["id"]] = p["inventory"].get(loot["id"], 0) + 1
        
        # Update player
        update_player(player_id, p)
        
        # Update server stats
        data = load_data()
        data["server_stats"]["bosses_defeated"] = data["server_stats"].get("bosses_defeated", 0) + 1
        save_data(data)
        
        # Victory embed
        embed = discord.Embed(
            title=f"🎉 LEGENDARY VICTORY! {boss_data['name']} Defeated!",
            description=f"{ctx.author.mention} berhasil mengalahkan {boss_data['emoji']} {boss_data['name']}!",
            color=0x00ff00
        )
        
        reward_text = f"EXP: +{rewards['exp']:,}\nQi: +{rewards['qi']}\nSpirit Stones: +{rewards['spirit_stones']}"
        if loot:
            reward_text += f"\n🎁 **RARE LOOT:** {loot['emoji']} {loot['name']}"
        
        embed.add_field(name="💰 REWARDS", value=reward_text, inline=False)
        embed.add_field(name="⏰ Cooldown", value="Bisa challenge lagi dalam 24 jam", inline=True)
        embed.add_field(name="🏆 Total Wins", value=f"{len(p.get('bosses_defeated', []))} bosses", inline=True)
        
    else:
        # DEFEAT
        embed = discord.Embed(
            title=f"💀 DEFEAT! {boss_data['name']} Wins!",
            description=f"{ctx.author.mention} dikalahkan oleh {boss_data['emoji']} {boss_data['name']}!",
            color=0xff0000
        )
        
        embed.add_field(name="💡 Tips", value="• Level up lebih tinggi\n• Gunakan element advantage\n• Upgrade equipment\n• Pelajari technique baru", inline=False)
        embed.add_field(name="⏰ Cooldown", value="Bisa coba lagi dalam 1 jam", inline=True)
        
        # Shorter cooldown for defeat
        if "last_boss_challenge" not in p:
            p["last_boss_challenge"] = {}
        p["last_boss_challenge"][boss_data["name"]] = time.time() - 82800
    
    try:
        await battle_data["message"].edit(embed=embed)
    except:
        await ctx.send(embed=embed)

async def boss_status(ctx):
    """Lihat status boss battle sedang berlangsung"""
    player_id = ctx.author.id
    battle_id = f"boss_{player_id}"
    
    if battle_id not in ACTIVE_BOSS_BATTLES:
        return await ctx.send("❌ Anda tidak sedang dalam boss battle!")
    
    embed = create_boss_battle_embed(battle_id, ctx)
    await ctx.send(embed=embed)

async def boss_cooldown(ctx):
    """Lihat cooldown boss"""
    player_id = ctx.author.id
    p = get_player(player_id)
    
    if not p:
        return await ctx.send("❌ Anda belum terdaftar!")
    
    embed = discord.Embed(title="⏰ Boss Cooldowns", color=0x7289da)
    
    if "last_boss_challenge" not in p or not p["last_boss_challenge"]:
        embed.description = "Anda belum challenge boss apapun!"
        return await ctx.send(embed=embed)
    
    current_time = time.time()
    ready_bosses = []
    cooldown_bosses = []
    
    for boss_name, last_time in p["last_boss_challenge"].items():
        cooldown_remaining = 86400 - (current_time - last_time)
        
        if cooldown_remaining <= 0:
            ready_bosses.append(boss_name)
        else:
            hours = int(cooldown_remaining // 3600)
            minutes = int((cooldown_remaining % 3600) // 60)
            cooldown_bosses.append(f"{boss_name} - {hours}h {minutes}m")
    
    if ready_bosses:
        embed.add_field(name="✅ Ready to Challenge", value="\n".join(ready_bosses), inline=False)
    
    if cooldown_bosses:
        embed.add_field(name="⏰ On Cooldown", value="\n".join(cooldown_bosses), inline=False)
    
    if not ready_bosses and not cooldown_bosses:
        embed.description = "Anda belum challenge boss apapun!"
    
    await ctx.send(embed=embed)