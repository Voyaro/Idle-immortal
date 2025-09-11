import discord
import random
import asyncio
import time
import math

# Data structures
WORLD_BOSSES = {
    "heavenly_dragon": {
        "name": "Heavenly Dragon",
        "emoji": "🐉",
        "level": 150,
        "health": 50000,
        "max_health": 50000,
        "damage": (800, 1000),
        "reward_exp": 15000000,  # 10x boost
        "reward_qi": 6000,
        "reward_stones": 5000,
        "element": "light",
        "weakness": "dark",
        "description": "Dragon surgawi yang turun setiap jam",
        "min_players": 2,
        "max_players": 10,
        "spawn_interval": 3600,
        "last_spawn": 0,
        "reward_equipment": [
            {"name": "Heavenly Sword", "type": "weapon", "power": 50000, "rarity": "legendary", "set": "Heavenly Dragon"},
            {"name": "Heavenly Armor", "type": "armor", "power": 50000, "rarity": "legendary", "set": "Heavenly Dragon"},
            {"name": "Heavenly Crown", "type": "helmet", "power": 50000, "rarity": "legendary", "set": "Heavenly Dragon"},
            {"name": "Heavenly Ring", "type": "accessory", "power": 50000, "rarity": "legendary", "set": "Heavenly Dragon"}
        ],
        "set_bonus": 200000
    },
    "abyssal_dragon": {
        "name": "Abyssal Dragon",
        "emoji": "🐉",
        "level": 200,
        "health": 75000,
        "max_health": 75000,
        "damage": (1200, 1800),
        "reward_exp": 30000000,  # 10x boost
        "reward_qi": 9000,
        "reward_stones": 7000,
        "element": "dark",
        "weakness": "light",
        "description": "Titan dari kedalaman abyss",
        "min_players": 2,
        "max_players": 12,
        "spawn_interval": 7200,
        "last_spawn": 0,
        "reward_equipment": [
            {"name": "Abyssal Dragon Sword", "type": "weapon", "power": 160000, "rarity": "mythic", "set": "Abyssal Dragon"},
            {"name": "Abyssal Dragon Armor", "type": "armor", "power": 170000, "rarity": "mythic", "set": "Abyssal Dragon"},
            {"name": "Abyssal Dragon Crown", "type": "helmet", "power": 180000, "rarity": "mythic", "set": "Abyssal Dragon"},
            {"name": "Abyssal Dragon Ring", "type": "accessory", "power": 190000, "rarity": "mythic", "set": "Abyssal Dragon"}
        ],
        "set_bonus": 400000
    },
    "void_emperor": {
        "name": "Void Emperor",
        "emoji": "👤",
        "level": 300,
        "health": 120000,
        "max_health": 120000,
        "damage": (2000, 3000),
        "reward_exp": 50000000,
        "reward_qi": 15000,
        "reward_stones": 12000,
        "element": "void",
        "weakness": "creation",
        "description": "Kaisar dari dimensi void yang menguasai kehampaan",
        "min_players": 3,
        "max_players": 15,
        "spawn_interval": 10800,
        "last_spawn": 0,
        "reward_equipment": [
            {"name": "Void Emperor Blade", "type": "weapon", "power": 250000, "rarity": "legendary", "set": "Void Emperor"},
            {"name": "Void Emperor Robe", "type": "armor", "power": 260000, "rarity": "legendary", "set": "Void Emperor"},
            {"name": "Void Emperor Mask", "type": "helmet", "power": 270000, "rarity": "legendary", "set": "Void Emperor"},
            {"name": "Void Emperor Orb", "type": "accessory", "power": 280000, "rarity": "legendary", "set": "Void Emperor"}
        ],
        "set_bonus": 600000
    },
    "stellar_phoenix": {
        "name": "Stellar Phoenix",
        "emoji": "🔥",
        "level": 400,
        "health": 180000,
        "max_health": 180000,
        "damage": (3000, 4500),
        "reward_exp": 75000000,
        "reward_qi": 20000,
        "reward_stones": 18000,
        "element": "stellar",
        "weakness": "black_hole",
        "description": "Phoenix bintang yang terlahir dari supernova",
        "min_players": 4,
        "max_players": 20,
        "spawn_interval": 14400,
        "last_spawn": 0,
        "reward_equipment": [
            {"name": "Stellar Phoenix Talon", "type": "weapon", "power": 350000, "rarity": "transcendent", "set": "Stellar Phoenix"},
            {"name": "Stellar Phoenix Plume", "type": "armor", "power": 360000, "rarity": "transcendent", "set": "Stellar Phoenix"},
            {"name": "Stellar Phoenix Crown", "type": "helmet", "power": 370000, "rarity": "transcendent", "set": "Stellar Phoenix"},
            {"name": "Stellar Phoenix Core", "type": "accessory", "power": 380000, "rarity": "transcendent", "set": "Stellar Phoenix"}
        ],
        "set_bonus": 800000
    },
    "cosmic_leviathan": {
        "name": "Cosmic Leviathan",
        "emoji": "🐙",
        "level": 500,
        "health": 250000,
        "max_health": 250000,
        "damage": (4500, 6000),
        "reward_exp": 100000000,
        "reward_qi": 30000,
        "reward_stones": 25000,
        "element": "cosmic",
        "weakness": "order",
        "description": "Leviathan cosmic yang berenang di lautan ruang angkasa",
        "min_players": 5,
        "max_players": 25,
        "spawn_interval": 18000,
        "last_spawn": 0,
        "reward_equipment": [
            {"name": "Cosmic Leviathan Tentacle", "type": "weapon", "power": 450000, "rarity": "divine", "set": "Cosmic Leviathan"},
            {"name": "Cosmic Leviathan Scale", "type": "armor", "power": 460000, "rarity": "divine", "set": "Cosmic Leviathan"},
            {"name": "Cosmic Leviathan Eye", "type": "helmet", "power": 470000, "rarity": "divine", "set": "Cosmic Leviathan"},
            {"name": "Cosmic Leviathan Heart", "type": "accessory", "power": 480000, "rarity": "divine", "set": "Cosmic Leviathan"}
        ],
        "set_bonus": 1000000
    },
    "primordial_titan": {
        "name": "Primordial Titan",
        "emoji": "🗿",
        "level": 777,
        "health": 500000,
        "max_health": 500000,
        "damage": (8000, 12000),
        "reward_exp": 200000000,
        "reward_qi": 50000,
        "reward_stones": 40000,
        "element": "primordial",
        "weakness": "evolution",
        "description": "Titan primordial yang ada sejak awal penciptaan",
        "min_players": 10,
        "max_players": 50,
        "spawn_interval": 86400,  # 24 hours
        "last_spawn": 0,
        "reward_equipment": [
            {"name": "Primordial Titan Fist", "type": "weapon", "power": 800000, "rarity": "primordial", "set": "Primordial Titan"},
            {"name": "Primordial Titan Shell", "type": "armor", "power": 850000, "rarity": "primordial", "set": "Primordial Titan"},
            {"name": "Primordial Titan Crown", "type": "helmet", "power": 900000, "rarity": "primordial", "set": "Primordial Titan"},
            {"name": "Primordial Titan Soul", "type": "accessory", "power": 1000000, "rarity": "primordial", "set": "Primordial Titan"}
        ],
        "set_bonus": 2000000
    }
}

ACTIVE_WORLD_BOSSES = {}
WORLD_BOSS_PARTIES = {}
PLAYER_PARTIES = {}

# Helper functions
def get_player(player_id):
    """Import get_player safely"""
    from main import get_player as main_get_player
    return main_get_player(player_id)

def update_player(player_id, data):
    """Import update_player safely"""
    from main import update_player as main_update_player
    return main_update_player(player_id, data)

def calculate_set_bonus(equipment):
    """Import calculate_set_bonus safely"""
    from main import calculate_set_bonus as main_calculate_set_bonus
    return main_calculate_set_bonus(equipment)

# Realm data untuk level calculation
REALMS = {
    "Mortal Realm": {"stages": ["Body Refining [Entry]", "Body Refining [Middle]", "Body Refining [Peak]"]},
    "Immortal Realm": {"stages": ["Half-Immortal [Entry]", "Half-Immortal [Middle]", "Half-Immortal [Peak]"]},
    "God Realm": {"stages": ["Lesser God [Entry]", "Lesser God [Middle]", "Lesser God [Peak]"]}
}

def get_player_level(p):
    """Hitung level player"""
    realm_idx = list(REALMS.keys()).index(p["realm"])
    stage_idx = REALMS[p["realm"]]["stages"].index(p["stage"])
    return (realm_idx * 100) + (stage_idx * 3) + 1

def create_health_bar(percentage):
    """Buat health bar visual"""
    filled = int(percentage / 10)
    return "█" * filled + "░" * (10 - filled)

# Party Functions
async def create_party(ctx, party_name: str):
    """Buat party untuk world boss"""
    player_id = ctx.author.id
    p = get_player(player_id)

    if not p:
        return await ctx.send("❌ Anda belum terdaftar!")

    if player_id in PLAYER_PARTIES:
        return await ctx.send("❌ Anda sudah berada dalam party!")

    party_id = party_name.lower()

    if party_id in WORLD_BOSS_PARTIES:
        return await ctx.send("❌ Nama party sudah digunakan!")

    # Create party
    PLAYER_PARTIES[player_id] = {
        "party_id": party_id,
        "role": "leader"
    }

    WORLD_BOSS_PARTIES[party_id] = {
        "members": [player_id],
        "leader": player_id,
        "invites": []
    }

    embed = discord.Embed(
        title="🎉 Party Created!",
        description=f"{ctx.author.mention} membuat party **{party_name}**",
        color=0x00ff00
    )
    embed.add_field(name="Leader", value=ctx.author.name, inline=True)
    embed.add_field(name="Members", value="1/10", inline=True)
    embed.add_field(name="Status", value="🟢 Recruiting", inline=True)

    await ctx.send(embed=embed)

async def invite_party(ctx, member: discord.Member):
    """Invite player ke party"""
    player_id = ctx.author.id

    if player_id not in PLAYER_PARTIES:
        return await ctx.send("❌ Anda tidak memiliki party!")

    party_data = PLAYER_PARTIES[player_id]
    if party_data["role"] != "leader":
        return await ctx.send("❌ Hanya leader yang bisa invite!")

    target_id = member.id
    if target_id in PLAYER_PARTIES:
        return await ctx.send("❌ Player tersebut sudah dalam party!")

    # Send invite
    party_id = party_data["party_id"]
    if target_id not in WORLD_BOSS_PARTIES[party_id]["invites"]:
        WORLD_BOSS_PARTIES[party_id]["invites"].append(target_id)

    try:
        await member.send(f"🎯 Anda diundang ke party **{party_id}** oleh {ctx.author.name}!\nGunakan `!join_party {party_id}` untuk bergabung.")
    except:
        pass

    await ctx.send(f"✅ Undangan dikirim ke {member.mention}!")

async def join_party(ctx, party_name: str):
    """Bergabung dengan party"""
    player_id = ctx.author.id
    p = get_player(player_id)

    if not p:
        return await ctx.send("❌ Anda belum terdaftar!")

    if player_id in PLAYER_PARTIES:
        return await ctx.send("❌ Anda sudah berada dalam party!")

    party_id = party_name.lower()
    if party_id not in WORLD_BOSS_PARTIES:
        return await ctx.send("❌ Party tidak ditemukan!")

    if player_id not in WORLD_BOSS_PARTIES[party_id]["invites"]:
        return await ctx.send("❌ Anda tidak diundang ke party ini!")

    if len(WORLD_BOSS_PARTIES[party_id]["members"]) >= 10:
        return await ctx.send("❌ Party sudah penuh!")

    # Join party
    PLAYER_PARTIES[player_id] = {
        "party_id": party_id,
        "role": "member"
    }

    WORLD_BOSS_PARTIES[party_id]["members"].append(player_id)
    WORLD_BOSS_PARTIES[party_id]["invites"].remove(player_id)

    embed = discord.Embed(
        title="🎉 Joined Party!",
        description=f"{ctx.author.mention} bergabung dengan party **{party_name}**",
        color=0x00ff00
    )
    embed.add_field(name="Total Members", value=f"{len(WORLD_BOSS_PARTIES[party_id]['members'])}/10", inline=True)
    embed.add_field(name="Leader", value=f"<@{WORLD_BOSS_PARTIES[party_id]['leader']}>", inline=True)

    await ctx.send(embed=embed)

async def leave_party(ctx):
    """Keluar dari party"""
    player_id = ctx.author.id

    if player_id not in PLAYER_PARTIES:
        return await ctx.send("❌ Anda tidak berada dalam party!")

    party_data = PLAYER_PARTIES[player_id]
    party_id = party_data["party_id"]

    # Remove from party
    if player_id in WORLD_BOSS_PARTIES[party_id]["members"]:
        WORLD_BOSS_PARTIES[party_id]["members"].remove(player_id)

    # If leader leaves, disband party or transfer leadership
    if player_id == WORLD_BOSS_PARTIES[party_id]["leader"]:
        if len(WORLD_BOSS_PARTIES[party_id]["members"]) > 0:
            # Transfer leadership to next member
            new_leader = WORLD_BOSS_PARTIES[party_id]["members"][0]
            WORLD_BOSS_PARTIES[party_id]["leader"] = new_leader
            PLAYER_PARTIES[new_leader]["role"] = "leader"
            await ctx.send(f"👑 Leadership diberikan ke <@{new_leader}>")
        else:
            # Disband party
            del WORLD_BOSS_PARTIES[party_id]

    del PLAYER_PARTIES[player_id]
    await ctx.send("✅ Anda keluar dari party!")

async def party_info(ctx):
    """Lihat info party"""
    player_id = ctx.author.id

    if player_id not in PLAYER_PARTIES:
        return await ctx.send("❌ Anda tidak berada dalam party!")

    party_data = PLAYER_PARTIES[player_id]
    party_id = party_data["party_id"]

    if party_id not in WORLD_BOSS_PARTIES:
        return await ctx.send("❌ Party tidak ditemukan!")

    party_info = WORLD_BOSS_PARTIES[party_id]

    embed = discord.Embed(
        title=f"👥 Party {party_id}",
        description=f"Party untuk World Boss battles",
        color=0x7289da
    )

    # Member list
    members_text = ""
    for member_id in party_info["members"]:
        try:
            member = await ctx.bot.fetch_user(member_id)
            role = "👑" if member_id == party_info["leader"] else "👤"
            p_data = get_player(member_id)
            level = get_player_level(p_data)
            members_text += f"{role} {member.name} (Lv. {level})\n"
        except:
            members_text += f"👤 Unknown User ({member_id})\n"

    embed.add_field(name="Members", value=members_text or "No members", inline=False)
    embed.add_field(name="Total", value=f"{len(party_info['members'])}/10 players", inline=True)
    embed.add_field(name="Status", value="🟢 Ready" if len(party_info['members']) >= 3 else "🟡 Recruiting", inline=True)

    # Invites
    if party_info["invites"]:
        invites_text = "\n".join([f"<@{invite_id}>" for invite_id in party_info["invites"][:3]])
        embed.add_field(name="Pending Invites", value=invites_text, inline=False)

    await ctx.send(embed=embed)

# World Boss Functions
async def spawn_world_boss():
    """Spawn world boss secara otomatis"""
    current_time = time.time()

    for boss_id, boss_data in WORLD_BOSSES.items():
        if current_time - boss_data["last_spawn"] >= boss_data["spawn_interval"]:
            # Reset boss health
            boss_data["health"] = boss_data["max_health"]
            boss_data["last_spawn"] = current_time

            # Find active boss channel (ganti dengan channel ID yang sesuai)
            # Channel ID akan di-set dari main.py
            return boss_data

    return None

async def challenge_world_boss(ctx, boss_name: str):
    """Tantang world boss dengan party"""
    player_id = ctx.author.id

    if player_id not in PLAYER_PARTIES:
        return await ctx.send("❌ Anda harus dalam party untuk challenge world boss!")

    party_data = PLAYER_PARTIES[player_id]
    party_id = party_data["party_id"]

    if party_data["role"] != "leader":
        return await ctx.send("❌ Hanya party leader yang bisa challenge world boss!")

    # Cari boss
    boss_data = None
    for boss_id, data in WORLD_BOSSES.items():
        if data["name"].lower() == boss_name.lower():
            boss_data = data
            break

    if not boss_data:
        return await ctx.send("❌ World boss tidak ditemukan!")

    # Check boss availability
    current_time = time.time()
    if current_time - boss_data["last_spawn"] > boss_data["spawn_interval"]:
        return await ctx.send("❌ World boss belum spawn! Tunggu announcement.")

    # Check if boss already being fought
    if boss_data["name"] in ACTIVE_WORLD_BOSSES:
        return await ctx.send("❌ World boss sedang dilawan party lain!")

    # Start world boss battle
    battle_id = f"world_boss_{boss_data['name'].lower()}_{party_id}"

    ACTIVE_WORLD_BOSSES[boss_data["name"]] = {
        "battle_id": battle_id,
        "boss_data": boss_data,
        "party_id": party_id,
        "party_members": WORLD_BOSS_PARTIES[party_id]["members"].copy(),
        "boss_health": boss_data["health"],
        "player_health": {member_id: 1000 for member_id in WORLD_BOSS_PARTIES[party_id]["members"]},
        "round": 0,
        "start_time": current_time,
        "damage_dealt": {member_id: 0 for member_id in WORLD_BOSS_PARTIES[party_id]["members"]}
    }

    embed = discord.Embed(
        title=f"🌍 WORLD BOSS BATTLE - {boss_data['name']}",
        description=f"Party **{party_id}** menantang {boss_data['emoji']} {boss_data['name']}!",
        color=0xff0000
    )
    embed.add_field(name="Party Size", value=f"{len(WORLD_BOSS_PARTIES[party_id]['members'])} players", inline=True)
    embed.add_field(name="Boss Health", value=f"{boss_data['health']:,}", inline=True)
    embed.add_field(name="Time Limit", value="10 minutes", inline=True)

    await ctx.send(embed=embed)

    # Start battle task
    asyncio.create_task(world_boss_battle_task(boss_data["name"], ctx))

async def world_boss_battle_task(boss_name, ctx):
    """Background task untuk world boss battle"""
    try:
        battle_data = ACTIVE_WORLD_BOSSES[boss_name]

        # 10 minute time limit
        end_time = time.time() + 600

        while (time.time() < end_time and 
               battle_data["boss_health"] > 0 and
               any(hp > 0 for hp in battle_data["player_health"].values())):

            await world_boss_round(battle_data, ctx)
            await asyncio.sleep(5)

            # Update battle data reference
            if boss_name not in ACTIVE_WORLD_BOSSES:
                break

        # Battle finished
        victory = battle_data["boss_health"] <= 0
        await finish_world_boss_battle(battle_data, ctx, victory)

    except Exception as e:
        print(f"Error in world boss battle task: {e}")
    finally:
        if boss_name in ACTIVE_WORLD_BOSSES:
            del ACTIVE_WORLD_BOSSES[boss_name]

async def world_boss_round(battle_data, ctx):
    """Satu round world boss battle"""
    battle_data["round"] += 1
    boss_data = battle_data["boss_data"]

    # All players attack
    total_damage = 0
    for player_id in battle_data["party_members"]:
        if battle_data["player_health"][player_id] > 0:
            p = get_player(player_id)
            player_damage = calculate_player_damage(p, boss_data)
            battle_data["damage_dealt"][player_id] += player_damage
            total_damage += player_damage

    battle_data["boss_health"] = max(0, battle_data["boss_health"] - total_damage)

    # Boss attacks random player
    alive_players = [pid for pid, hp in battle_data["player_health"].items() if hp > 0]
    if alive_players:
        target_id = random.choice(alive_players)
        boss_damage = random.randint(boss_data["damage"][0], boss_data["damage"][1])
        battle_data["player_health"][target_id] = max(0, battle_data["player_health"][target_id] - boss_damage)

        try:
            target_user = await ctx.bot.fetch_user(target_id)
            await ctx.send(f"⚡ {boss_data['name']} attacks {target_user.mention} for **{boss_damage} damage**!")
        except:
            pass

    # Update battle status
    embed = create_world_boss_embed(battle_data, ctx)
    try:
        await ctx.send(embed=embed)
    except:
        pass

def calculate_player_damage(player_data, boss_data):
    """Hitung damage player ke boss"""
    base_damage = player_data["total_power"]

    # Element advantage (sederhana)
    element_advantage = 1.0
    if boss_data["weakness"] == "light":
        element_advantage = 1.5
    elif boss_data["weakness"] == "dark":
        element_advantage = 1.5

    base_damage = int(base_damage * element_advantage)

    # Random variation
    damage = random.randint(int(base_damage * 0.8), int(base_damage * 1.2))
    return max(10, damage)

def create_world_boss_embed(battle_data, ctx):
    """Buat embed untuk world boss battle"""
    boss_data = battle_data["boss_data"]

    embed = discord.Embed(
        title=f"🌍 {boss_data['name']} Battle - Round {battle_data['round']}",
        color=0xff0000
    )

    # Boss health
    boss_hp_percent = (battle_data["boss_health"] / boss_data["max_health"]) * 100
    embed.add_field(
        name=f"{boss_data['emoji']} {boss_data['name']}",
        value=f"{create_health_bar(boss_hp_percent)} {battle_data['boss_health']:,}/{boss_data['max_health']:,} HP",
        inline=False
    )

    # Player status
    players_text = ""
    for player_id in battle_data["party_members"]:
        try:
            player = get_player(player_id)
            user = ctx.bot.get_user(player_id)
            hp_percent = (battle_data["player_health"][player_id] / 1000) * 100
            status = "❤️" if battle_data["player_health"][player_id] > 0 else "💀"
            players_text += f"{status} {user.name} - {create_health_bar(hp_percent)} {battle_data['damage_dealt'][player_id]:,} damage\n"
        except:
            continue

    embed.add_field(name="👥 Party Status", value=players_text, inline=False)

    return embed

async def finish_world_boss_battle(battle_data, ctx, victory):
    """Selesaikan world boss battle"""
    boss_data = battle_data["boss_data"]

    if victory:
        # Calculate rewards based on damage contribution
        total_damage = sum(battle_data["damage_dealt"].values())
        rewards = {}
        drop_winners = []  # Untuk melacak siapa yang dapat equipment

        for player_id in battle_data["party_members"]:
            if battle_data["player_health"][player_id] > 0:  # Only alive players get rewards
                damage_share = battle_data["damage_dealt"][player_id] / total_damage

                p = get_player(player_id)
                if p is None:
                    continue
                    
                p["exp"] += int(boss_data["reward_exp"] * damage_share)
                p["qi"] += int(boss_data["reward_qi"] * damage_share)
                p["spirit_stones"] += int(boss_data["reward_stones"] * damage_share)

                # DROP CHANCE EQUIPMENT (5%)
                if "reward_equipment" in boss_data:
                    if random.random() < 0.05:  # 5% chance
                        equip = random.choice(boss_data["reward_equipment"])
                        if "equipment" not in p:
                            p["equipment"] = {}
                        if "equipment" not in p or p["equipment"] is None:
                            p["equipment"] = {}
                        # Add equipment properly
                        equip_id = equip["name"].lower().replace(" ", "_")
                        p["equipment"][equip_id] = equip.get("power", 100)

                        # Cek apakah player punya full set
                        player_set_items = [e for e in p["equipment"] if e.get("set") == equip["set"]]
                        boss_equips = [e["name"] for e in boss_data["reward_equipment"]]

                        if len({e["name"] for e in player_set_items}) == len(boss_equips):
                            p["power"] += boss_data["set_bonus"]

                        drop_winners.append((player_id, equip["name"]))

                # Track world boss kills
                if "world_boss_kills" not in p or p["world_boss_kills"] is None:
                    p["world_boss_kills"] = {}
                boss_name = boss_data["name"]
                p["world_boss_kills"][boss_name] = p["world_boss_kills"].get(boss_name, 0) + 1

                update_player(player_id, p)

                rewards[player_id] = {
                    "exp": int(boss_data["reward_exp"] * damage_share),
                    "qi": int(boss_data["reward_qi"] * damage_share),
                    "stones": int(boss_data["reward_stones"] * damage_share)
                }

        # Victory embed
        embed = discord.Embed(
            title=f"🎉 WORLD BOSS DEFEATED! {boss_data['emoji']}",
            description=f"Party berhasil mengalahkan {boss_data['name']}!",
            color=0x00ff00
        )

        rewards_text = ""
        for player_id, reward in rewards.items():
            try:
                user = await ctx.bot.fetch_user(player_id)
                rewards_text += f"{user.mention}: {reward['exp']} EXP, {reward['qi']} Qi, {reward['stones']} Stones\n"
            except:
                continue

        # Tambahkan info equipment drops jika ada
        if drop_winners:
            drops_text = "\n".join([f"<@{winner[0]}> mendapatkan **{winner[1]}**!" for winner in drop_winners])
            embed.add_field(name="🎁 Equipment Drops", value=drops_text, inline=False)

        embed.add_field(name="🎁 Rewards", value=rewards_text, inline=False)

    else:
        # Defeat
        embed = discord.Embed(
            title=f"💀 WORLD BOSS VICTORIOUS! {boss_data['emoji']}",
            description=f"{boss_data['name']} mengalahkan party!",
            color=0xff0000
        )

    await ctx.send(embed=embed)

async def world_boss_status(ctx):
    """Lihat status world boss"""
    current_time = time.time()

    embed = discord.Embed(
        title="🌍 World Boss Status",
        color=0x7289da
    )

    for boss_id, boss_data in WORLD_BOSSES.items():
        time_until_spawn = max(0, boss_data["spawn_interval"] - (current_time - boss_data["last_spawn"]))
        hours = int(time_until_spawn // 3600)
        minutes = int((time_until_spawn % 3600) // 60)

        status = "🟢 **SPAWNED**" if time_until_spawn == 0 else f"⏰ {hours}h {minutes}m"

        if boss_data["name"] in ACTIVE_WORLD_BOSSES:
            battle_data = ACTIVE_WORLD_BOSSES[boss_data["name"]]
            hp_percent = (battle_data["boss_health"] / boss_data["max_health"]) * 100
            status = f"⚔️ **IN BATTLE** ({hp_percent:.1f}% HP)"

        embed.add_field(
            name=f"{boss_data['emoji']} {boss_data['name']}",
            value=f"{status}\nLevel: {boss_data['level']}\nRequires: {boss_data['min_players']}+ players\nSpawn: Every {boss_data['spawn_interval']//3600} hours",
            inline=False
        )

    await ctx.send(embed=embed)

# Background task
async def start_world_boss_tasks():
    """Start semua background tasks untuk world boss"""
    while True:
        try:
            await spawn_world_boss()
            await asyncio.sleep(300)
        except Exception as e:
            print(f"Error in world boss spawn task: {e}")
            await asyncio.sleep(60)