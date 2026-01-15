import json
import os
import time
import datetime
import shutil

# Data penyimpanan dengan backup system
DATA_FILE = "data.json"
BACKUP_DIR = "backups"

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
                "total_world_boss_kills": 0,
                "last_update": datetime.datetime.now().isoformat()
            },
            "daily_quests_reset": datetime.datetime.now().isoformat(),
            "world_bosses": {}
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
                "last_login": player_data.get("last_login", "0"),
                "world_boss_kills": player_data.get("world_boss_kills", {}),
                "last_world_boss": player_data.get("last_world_boss", "0")
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
            "total_world_boss_kills": 0,
            "last_update": datetime.datetime.now().isoformat()
        },
        "guilds": {},
        "market_items": [],
        "server_events": {},
        "daily_quests_reset": datetime.datetime.now().isoformat(),
        "world_bosses": {}
    }

    # Simpan data default
    save_data(default_data)
    return default_data

def save_data(data):
    """Save data dengan backup otomatis setiap 5 menit"""
    try:
        # Backup data lama sebelum menimpa jika sudah 5 menit sejak backup terakhir
        current_time = int(time.time())
        last_backup = data.get("last_backup", 0)
        
        if os.path.exists(DATA_FILE) and (current_time - last_backup >= 300):
            backup_data()
            data["last_backup"] = current_time

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
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        if os.path.exists(DATA_FILE):
            timestamp = int(time.time())
            backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json")
            shutil.copy2(DATA_FILE, backup_path)

            # Hapus backup lama (simpan hanya 5 terbaru)
            backups = []
            if os.path.exists(BACKUP_DIR):
                backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_") and f.endswith(".json")])

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

def calculate_set_bonus(equipment_dict):
    """Calculate set bonuses from equipment"""
    set_counts = {}
    total_bonus = 0

    # Count items per set
    for item_id in equipment_dict.keys():
        # Import equipment shop data
        from main import EQUIPMENT_SHOP
        item_data = EQUIPMENT_SHOP.get(item_id, {})
        if "set" in item_data:
            set_name = item_data["set"]
            set_counts[set_name] = set_counts.get(set_name, 0) + 1

    # Calculate bonuses
    for set_name, count in set_counts.items():
        # Import set bonuses
        from main import SET_BONUSES
        if set_name in SET_BONUSES:
            if count >= 3 and "3_piece" in SET_BONUSES[set_name]:
                total_bonus += SET_BONUSES[set_name]["3_piece"]
            elif count >= 2 and "2_piece" in SET_BONUSES[set_name]:
                total_bonus += SET_BONUSES[set_name]["2_piece"]

    return total_bonus

def get_realm_order_index(realm_name):
    """Get realm order for equipment access checks"""
    # Import realm order
    from main import REALM_ORDER
    return REALM_ORDER.index(realm_name) if realm_name in REALM_ORDER else 0

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

    # Import achievements
    from main import ACHIEVEMENTS

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
                    # Import get_exp_cap function
                    from main import get_exp_cap
                    player_data["exp"] = min(player_data["exp"] + amount, get_exp_cap(player_data))
                elif reward_type == "qi":
                    player_data["qi"] += amount
                elif reward_type == "power":
                    player_data["base_power"] += amount

            new_achievements.append(achievement_data)

    if new_achievements:
        # Import update_player function
        from main import update_player
        update_player(player_id, player_data)

    return new_achievements

def reset_daily_quests():
    """Reset daily quests for all players"""
    data = load_data()
    now = datetime.datetime.now()

    # Handle string or datetime
    if isinstance(data.get("daily_quests_reset"), str):
        last_reset = datetime.datetime.fromisoformat(data.get("daily_quests_reset", now.isoformat()))
    else:
        last_reset = data.get("daily_quests_reset", now)

    # Check if it's a new day
    if now.date() > last_reset.date():
        # Import daily quests
        from main import DAILY_QUESTS

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

def save_world_boss_data():
    """Simpan data world boss"""
    try:
        # Import world boss data dari main
        from main import WORLD_BOSSES, ACTIVE_WORLD_BOSSES, WORLD_BOSS_PARTIES, PLAYER_PARTIES

        data = load_data()

        data["world_bosses"] = {
            "bosses": WORLD_BOSSES,
            "active_bosses": ACTIVE_WORLD_BOSSES,
            "parties": WORLD_BOSS_PARTIES,
            "player_parties": PLAYER_PARTIES
        }

        save_data(data)
        print("✅ World boss data saved!")
        return True
    except Exception as e:
        print(f"❌ Error saving world boss data: {e}")
        return False

def load_world_boss_data():
    """Load data world boss"""
    try:
        # Import world boss data dari main
        from main import WORLD_BOSSES, ACTIVE_WORLD_BOSSES, WORLD_BOSS_PARTIES, PLAYER_PARTIES

        data = load_data()
        if "world_bosses" in data:
            world_boss_data = data["world_bosses"]

            # Update boss data
            for boss_id, boss_data in world_boss_data.get("bosses", {}).items():
                if boss_id in WORLD_BOSSES:
                    WORLD_BOSSES[boss_id].update(boss_data)

            # Load active bosses and parties
            ACTIVE_WORLD_BOSSES.clear()
            ACTIVE_WORLD_BOSSES.update(world_boss_data.get("active_bosses", {}))

            WORLD_BOSS_PARTIES.clear()
            WORLD_BOSS_PARTIES.update(world_boss_data.get("parties", {}))

            PLAYER_PARTIES.clear()
            PLAYER_PARTIES.update(world_boss_data.get("player_parties", {}))

            print("✅ World boss data loaded!")
            return True
    except Exception as e:
        print(f"❌ Error loading world boss data: {e}")
        return False

def update_world_boss_kill_count(boss_name):
    """Update server stats untuk world boss kills"""
    try:
        data = load_data()
        data["server_stats"]["total_world_boss_kills"] = data["server_stats"].get("total_world_boss_kills", 0) + 1
        save_data(data)
        return True
    except Exception as e:
        print(f"❌ Error updating world boss kill count: {e}")
        return False

def get_player_level(p):
    """Hitung level player berdasarkan realm dan stage"""
    try:
        # Import realm data
        from main import REALMS, REALM_ORDER

        realm_idx = REALM_ORDER.index(p["realm"])
        stage_idx = REALMS[p["realm"]]["stages"].index(p["stage"])

        base_level = (realm_idx * 100) + (stage_idx * 3) + 1

        # Apply race bonus jika ada
        from main import RACES
        race_data = RACES.get(p.get("race", "human"), RACES["human"])
        if "exp" in race_data["bonuses"]:
            base_level = int(base_level * (1 + race_data["bonuses"]["exp"]))

        return base_level
    except:
        return 1

def get_exp_cap(p):
    """Dapatkan EXP cap untuk stage player saat ini"""
    try:
        # Import realm data
        from main import REALMS

        realm_data = REALMS[p["realm"]]
        stage_idx = realm_data["stages"].index(p["stage"])

        # Base EXP untuk stage pertama di Mortal Realm
        base_exp = 1000

        # Exponential growth per stage: 1.5x per stage
        stage_exp = base_exp * (1.5 ** stage_idx)

        # Realm multiplier 
        realm_multiplier = realm_data["exp_multiplier"]

        # Additional difficulty scaling
        difficulty_multiplier = 1 + (stage_idx * 0.1)

        exp_cap = int(stage_exp * realm_multiplier * difficulty_multiplier)

        return max(1000, exp_cap)
    except:
        return 1000

def generate_random_technique(player_realm, player_stage):
    """Generate random cultivation technique"""
    try:
        # Import technique data
        from main import CULTIVATION_SECTS, TECHNIQUE_TYPES, ELEMENT_TYPES
        import random

        sect = random.choice(list(CULTIVATION_SECTS.keys()))
        technique_type = random.choice(list(TECHNIQUE_TYPES.keys()))
        element = random.choice(list(ELEMENT_TYPES.keys()))

        # Determine power based on realm
        from main import REALM_ORDER, REALMS
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
    except Exception as e:
        print(f"❌ Error generating technique: {e}")
        # Return default technique jika error
        return {
            "id": "basic_attack_fire_0001",
            "name": "Basic Fire Palm",
            "sect": "elemental",
            "type": "attack",
            "element": "fire",
            "power_bonus": 0.1,
            "description": "Basic fire technique for beginners",
            "cost": 100,
            "emoji": "🔥",
            "element_emoji": "🔥",
            "requirements": {
                "realm": "Mortal Realm",
                "stage": "Body Refining [Entry]"
            }
        }

# Helper function untuk world boss system
def can_access_world_boss(player_level, boss_level):
    """Check if player can access world boss berdasarkan level"""
    return player_level >= boss_level * 0.5  # Player level harus minimal 50% dari boss level

def calculate_world_boss_rewards(player_level, boss_level, damage_contribution):
    """Hitung rewards world boss berdasarkan level dan kontribusi damage"""
    base_exp = boss_level * 10
    base_qi = boss_level * 5
    base_stones = boss_level * 2

    # Scale berdasarkan level player
    level_factor = min(2.0, player_level / boss_level)

    exp_reward = int(base_exp * level_factor * damage_contribution)
    qi_reward = int(base_qi * level_factor * damage_contribution)
    stones_reward = int(base_stones * level_factor * damage_contribution)

    return exp_reward, qi_reward, stones_reward

def cleanup_old_parties():
    """Bersihkan party yang sudah tidak aktif"""
    try:
        from main import WORLD_BOSS_PARTIES, PLAYER_PARTIES
        current_time = time.time()
        inactive_threshold = 3600  # 1 jam

        parties_to_remove = []

        for party_id, party_data in list(WORLD_BOSS_PARTIES.items()):
            # Jika party kosong atau tidak aktif dalam 1 jam
            if not party_data.get("members") or current_time - party_data.get("last_activity", 0) > inactive_threshold:
                parties_to_remove.append(party_id)

        # Hapus party yang tidak aktif
        for party_id in parties_to_remove:
            # Hapus semua member dari party ini
            for player_id, player_party in list(PLAYER_PARTIES.items()):
                if player_party.get("party_id") == party_id:
                    del PLAYER_PARTIES[player_id]

            # Hapus party
            del WORLD_BOSS_PARTIES[party_id]

        if parties_to_remove:
            print(f"🧹 Cleaned up {len(parties_to_remove)} inactive parties")

        return len(parties_to_remove)
    except Exception as e:
        print(f"❌ Error cleaning up parties: {e}")
        return 0