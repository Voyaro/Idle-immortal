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
    },

    # ===============================
    # 30 NEW NPCS - EXPANSION (10 Male + 20 Female)
    # ===============================
    
    # Additional 10 Male NPCs
    "yang_kai": {
        "name": "Yang Kai",
        "gender": "male",
        "emoji": "🌋",
        "cultivation_level": 58,
        "realm": "Immortal Realm",
        "personality": "volcanic_warrior",
        "specialty": "earth_fire_fusion",
        "backstory": "Warrior who merged volcanic fire with earth cultivation",
        "dialogue_style": "explosive_determined",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["volcanic_stones", "earth_crystals", "fire_gems"],
        "gifts_hated": ["water_items", "ice_crystals"],
        "relationship_status": "acquaintance"
    },
    "shen_long": {
        "name": "Shen Long",
        "gender": "male",
        "emoji": "🐲",
        "cultivation_level": 85,
        "realm": "God Realm",
        "personality": "dragon_lord",
        "specialty": "dragon_transformation",
        "backstory": "Ancient dragon who took human form to understand mortals",
        "dialogue_style": "majestic_ancient",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["dragon_scales", "ancient_treasures", "divine_items"],
        "gifts_hated": ["cheap_items", "modern_objects"],
        "relationship_status": "divine"
    },
    "fu_chen": {
        "name": "Fu Chen",
        "gender": "male",
        "emoji": "📿",
        "cultivation_level": 72,
        "realm": "God Realm",
        "personality": "buddhist_monk",
        "specialty": "enlightenment_cultivation",
        "backstory": "Buddhist monk who achieved enlightenment through compassion",
        "dialogue_style": "serene_wise",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["prayer_beads", "enlightenment_texts", "lotus_items"],
        "gifts_hated": ["violent_items", "evil_artifacts"],
        "relationship_status": "mentor"
    },
    "wei_xiao": {
        "name": "Wei Xiao",
        "gender": "male",
        "emoji": "🌊",
        "cultivation_level": 44,
        "realm": "Immortal Realm",
        "personality": "ocean_wanderer",
        "specialty": "water_cultivation",
        "backstory": "Ocean cultivator who controls the seven seas",
        "dialogue_style": "flowing_calm",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["sea_pearls", "water_crystals", "ocean_treasures"],
        "gifts_hated": ["desert_items", "fire_items"],
        "relationship_status": "friend"
    },
    "han_mo": {
        "name": "Han Mo",
        "gender": "male",
        "emoji": "🖤",
        "cultivation_level": 66,
        "realm": "Immortal Realm",
        "personality": "dark_scholar",
        "specialty": "shadow_research",
        "backstory": "Scholar who studies the balance between light and darkness",
        "dialogue_style": "intellectual_dark",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["shadow_tomes", "dark_crystals", "research_notes"],
        "gifts_hated": ["light_items", "holy_artifacts"],
        "relationship_status": "mysterious"
    },
    "bai_yu": {
        "name": "Bai Yu",
        "gender": "male",
        "emoji": "🤍",
        "cultivation_level": 39,
        "realm": "Mortal Realm",
        "personality": "pure_heart",
        "specialty": "purification_arts",
        "backstory": "Young cultivator with the purest heart and strongest will",
        "dialogue_style": "innocent_determined",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["pure_crystals", "white_jade", "blessing_items"],
        "gifts_hated": ["corrupted_items", "dark_artifacts"],
        "relationship_status": "friend"
    },
    "luo_feng": {
        "name": "Luo Feng",
        "gender": "male",
        "emoji": "🌪️",
        "cultivation_level": 53,
        "realm": "Immortal Realm",
        "personality": "storm_chaser",
        "specialty": "storm_cultivation",
        "backstory": "Daredevil who cultivates by riding the most dangerous storms",
        "dialogue_style": "wild_adventurous",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["storm_cores", "lightning_rods", "wind_chimes"],
        "gifts_hated": ["calm_items", "peaceful_gifts"],
        "relationship_status": "acquaintance"
    },
    "jin_wu": {
        "name": "Jin Wu",
        "gender": "male",
        "emoji": "👑",
        "cultivation_level": 67,
        "realm": "Immortal Realm",
        "personality": "fallen_prince",
        "specialty": "royal_techniques",
        "backstory": "Former prince who lost his kingdom but gained cultivation power",
        "dialogue_style": "noble_melancholic",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["royal_artifacts", "crown_jewels", "noble_items"],
        "gifts_hated": ["peasant_items", "reminder_items"],
        "relationship_status": "noble"
    },
    "tie_shan": {
        "name": "Tie Shan",
        "gender": "male",
        "emoji": "⛰️",
        "cultivation_level": 61,
        "realm": "Immortal Realm",
        "personality": "mountain_guardian",
        "specialty": "mountain_cultivation",
        "backstory": "Guardian spirit of the sacred mountain ranges",
        "dialogue_style": "steady_powerful",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["mountain_stones", "earth_gems", "stability_items"],
        "gifts_hated": ["erosion_items", "unstable_gifts"],
        "relationship_status": "guardian"
    },
    "yu_long": {
        "name": "Yu Long",
        "gender": "male",
        "emoji": "🌟",
        "cultivation_level": 78,
        "realm": "God Realm",
        "personality": "star_emperor",
        "specialty": "stellar_cultivation",
        "backstory": "Emperor who commands the power of stars and constellations",
        "dialogue_style": "stellar_commanding",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["star_fragments", "celestial_items", "constellation_maps"],
        "gifts_hated": ["earthly_items", "mundane_gifts"],
        "relationship_status": "divine"
    },

    # Additional 20 Female NPCs
    "li_mei": {
        "name": "Li Mei",
        "gender": "female",
        "emoji": "🦋",
        "cultivation_level": 33,
        "realm": "Mortal Realm",
        "personality": "butterfly_dancer",
        "specialty": "transformation_arts",
        "backstory": "Dancer who learned transformation from observing butterflies",
        "dialogue_style": "graceful_playful",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["silk_scarves", "butterfly_pins", "dance_items"],
        "gifts_hated": ["heavy_items", "clumsy_gifts"],
        "relationship_status": "friend"
    },
    "xu_ying": {
        "name": "Xu Ying",
        "gender": "female",
        "emoji": "👤",
        "cultivation_level": 59,
        "realm": "Immortal Realm",
        "personality": "shadow_mistress",
        "specialty": "shadow_manipulation",
        "backstory": "Mistress of shadows who can become one with darkness",
        "dialogue_style": "whispered_seductive",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["shadow_silk", "dark_roses", "mystery_boxes"],
        "gifts_hated": ["bright_lights", "revealing_items"],
        "relationship_status": "mysterious"
    },
    "chen_xue": {
        "name": "Chen Xue",
        "gender": "female",
        "emoji": "🏔️",
        "cultivation_level": 56,
        "realm": "Immortal Realm",
        "personality": "glacier_princess",
        "specialty": "eternal_ice",
        "backstory": "Princess born from eternal glaciers with ice-cold heart",
        "dialogue_style": "crystal_clear",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["eternal_ice", "crystal_jewelry", "winter_flowers"],
        "gifts_hated": ["melting_items", "warm_gifts"],
        "relationship_status": "cold"
    },
    "hong_lian": {
        "name": "Hong Lian",
        "gender": "female",
        "emoji": "🔥",
        "cultivation_level": 49,
        "realm": "Immortal Realm",
        "personality": "fire_phoenix",
        "specialty": "phoenix_rebirth",
        "backstory": "Phoenix cultivator who can be reborn from her own ashes",
        "dialogue_style": "fiery_passionate",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["phoenix_feathers", "rebirth_stones", "flame_jewelry"],
        "gifts_hated": ["death_items", "extinguishing_gifts"],
        "relationship_status": "passionate"
    },
    "mu_qing": {
        "name": "Mu Qing",
        "gender": "female",
        "emoji": "🌳",
        "cultivation_level": 41,
        "realm": "Immortal Realm",
        "personality": "forest_guardian",
        "specialty": "nature_communion",
        "backstory": "Guardian who can communicate with all forest creatures",
        "dialogue_style": "natural_harmonious",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["ancient_seeds", "forest_gems", "nature_crowns"],
        "gifts_hated": ["metal_items", "artificial_goods"],
        "relationship_status": "guardian"
    },
    "yue_ling": {
        "name": "Yue Ling",
        "gender": "female",
        "emoji": "🌕",
        "cultivation_level": 64,
        "realm": "Immortal Realm",
        "personality": "moon_empress",
        "specialty": "lunar_cultivation",
        "backstory": "Empress who draws power from all phases of the moon",
        "dialogue_style": "lunar_majestic",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["moon_pearls", "lunar_crowns", "night_jewels"],
        "gifts_hated": ["sun_items", "day_gifts"],
        "relationship_status": "noble"
    },
    "shui_ling": {
        "name": "Shui Ling",
        "gender": "female",
        "emoji": "💎",
        "cultivation_level": 37,
        "realm": "Mortal Realm",
        "personality": "water_spirit",
        "specialty": "water_dancing",
        "backstory": "Spirit born from the purest mountain spring water",
        "dialogue_style": "flowing_musical",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["water_gems", "spring_flowers", "pure_items"],
        "gifts_hated": ["pollution_items", "dirty_gifts"],
        "relationship_status": "spirit"
    },
    "yan_fei": {
        "name": "Yan Fei",
        "gender": "female",
        "emoji": "🎨",
        "cultivation_level": 43,
        "realm": "Immortal Realm",
        "personality": "artistic_genius",
        "specialty": "reality_painting",
        "backstory": "Artist who can paint scenes that become reality",
        "dialogue_style": "creative_inspired",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["art_supplies", "rare_pigments", "inspiration_items"],
        "gifts_hated": ["crude_items", "artless_gifts"],
        "relationship_status": "artist"
    },
    "lin_wan": {
        "name": "Lin Wan",
        "gender": "female",
        "emoji": "🌸",
        "cultivation_level": 46,
        "realm": "Immortal Realm",
        "personality": "cherry_blossom",
        "specialty": "seasonal_cultivation",
        "backstory": "Cultivator who embodies the beauty and transience of spring",
        "dialogue_style": "poetic_seasonal",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["spring_items", "cherry_blossoms", "seasonal_gifts"],
        "gifts_hated": ["winter_items", "permanent_gifts"],
        "relationship_status": "seasonal"
    },
    "ji_yun": {
        "name": "Ji Yun",
        "gender": "female",
        "emoji": "⚗️",
        "cultivation_level": 51,
        "realm": "Immortal Realm",
        "personality": "mad_alchemist",
        "specialty": "experimental_alchemy",
        "backstory": "Brilliant but eccentric alchemist who creates impossible potions",
        "dialogue_style": "excited_scientific",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["rare_ingredients", "experiment_tools", "chaos_items"],
        "gifts_hated": ["stable_items", "predictable_gifts"],
        "relationship_status": "mad_scientist"
    },
    "wan_yu": {
        "name": "Wan Yu",
        "gender": "female",
        "emoji": "🌈",
        "cultivation_level": 38,
        "realm": "Mortal Realm",
        "personality": "rainbow_maiden",
        "specialty": "color_cultivation",
        "backstory": "Maiden who can control and weaponize the colors of rainbows",
        "dialogue_style": "colorful_cheerful",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["rainbow_gems", "colorful_items", "prism_stones"],
        "gifts_hated": ["grey_items", "colorless_gifts"],
        "relationship_status": "cheerful"
    },
    "leng_yue": {
        "name": "Leng Yue",
        "gender": "female",
        "emoji": "🗡️",
        "cultivation_level": 68,
        "realm": "Immortal Realm",
        "personality": "sword_saint",
        "specialty": "ultimate_swordsmanship",
        "backstory": "Legendary sword saint who never drew her blade in vain",
        "dialogue_style": "honor_bound",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["legendary_blades", "honor_tokens", "warrior_items"],
        "gifts_hated": ["dishonor_items", "coward_gifts"],
        "relationship_status": "warrior"
    },
    "xing_chen": {
        "name": "Xing Chen",
        "gender": "female",
        "emoji": "✨",
        "cultivation_level": 76,
        "realm": "God Realm",
        "personality": "star_weaver",
        "specialty": "constellation_creation",
        "backstory": "Divine being who weaves new constellations in the night sky",
        "dialogue_style": "cosmic_creative",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["star_dust", "cosmic_threads", "celestial_tools"],
        "gifts_hated": ["earth_bound", "limited_gifts"],
        "relationship_status": "divine"
    },
    "meng_die": {
        "name": "Meng Die",
        "gender": "female",
        "emoji": "💭",
        "cultivation_level": 54,
        "realm": "Immortal Realm",
        "personality": "dream_weaver",
        "specialty": "dream_cultivation",
        "backstory": "Cultivator who can enter and manipulate the dreams of others",
        "dialogue_style": "dreamy_ethereal",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["dream_catchers", "sleep_herbs", "illusion_gems"],
        "gifts_hated": ["nightmare_items", "wake_up_gifts"],
        "relationship_status": "dreamy"
    },
    "qiu_shui": {
        "name": "Qiu Shui",
        "gender": "female",
        "emoji": "🍂",
        "cultivation_level": 45,
        "realm": "Immortal Realm",
        "personality": "autumn_spirit",
        "specialty": "harvest_cultivation",
        "backstory": "Spirit of autumn who brings the harvest and changing seasons",
        "dialogue_style": "mature_seasonal",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["autumn_leaves", "harvest_items", "golden_gifts"],
        "gifts_hated": ["spring_items", "young_gifts"],
        "relationship_status": "seasonal"
    },
    "ling_er": {
        "name": "Ling Er",
        "gender": "female",
        "emoji": "🧚",
        "cultivation_level": 29,
        "realm": "Mortal Realm",
        "personality": "fairy_child",
        "specialty": "fairy_magic",
        "backstory": "Young fairy who escaped from the fairy realm to learn human ways",
        "dialogue_style": "childlike_magical",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["fairy_items", "sparkly_gifts", "magical_toys"],
        "gifts_hated": ["adult_items", "serious_gifts"],
        "relationship_status": "childlike"
    },
    "bai_feng": {
        "name": "Bai Feng",
        "gender": "female",
        "emoji": "🕊️",
        "cultivation_level": 62,
        "realm": "Immortal Realm",
        "personality": "peaceful_dove",
        "specialty": "peace_cultivation",
        "backstory": "Dove spirit who seeks to bring peace to all conflicts",
        "dialogue_style": "gentle_peaceful",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["peace_offerings", "white_items", "harmony_gifts"],
        "gifts_hated": ["war_items", "conflict_gifts"],
        "relationship_status": "peaceful"
    },
    "hei_mei": {
        "name": "Hei Mei",
        "gender": "female",
        "emoji": "🖤",
        "cultivation_level": 57,
        "realm": "Immortal Realm",
        "personality": "dark_rose",
        "specialty": "thorn_cultivation",
        "backstory": "Beautiful but dangerous cultivator with thorns that protect her",
        "dialogue_style": "beautiful_dangerous",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["black_roses", "thorn_jewelry", "danger_items"],
        "gifts_hated": ["safe_items", "gentle_gifts"],
        "relationship_status": "dangerous"
    },
    "cang_yue": {
        "name": "Cang Yue",
        "gender": "female",
        "emoji": "🌊",
        "cultivation_level": 71,
        "realm": "God Realm",
        "personality": "ocean_goddess",
        "specialty": "tidal_cultivation",
        "backstory": "Goddess who controls the tides and depths of all oceans",
        "dialogue_style": "deep_mysterious",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["ocean_treasures", "deep_pearls", "tidal_items"],
        "gifts_hated": ["desert_items", "dry_gifts"],
        "relationship_status": "divine"
    },
    "zi_yun": {
        "name": "Zi Yun",
        "gender": "female",
        "emoji": "☁️",
        "cultivation_level": 48,
        "realm": "Immortal Realm",
        "personality": "cloud_dancer",
        "specialty": "cloud_formation",
        "backstory": "Cultivator who dances among clouds and shapes weather patterns",
        "dialogue_style": "airy_graceful",
        "affection_level": 0,
        "max_affection": 100,
        "gifts_loved": ["cloud_silk", "weather_items", "sky_gems"],
        "gifts_hated": ["ground_items", "heavy_gifts"],
        "relationship_status": "graceful"
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
    """Update NPC affection and relationship status with exclusive relationship limits"""
    npc_data = get_npc_data(player_id, npc_id)
    
    old_affection = npc_data["affection_level"]
    potential_new_affection = max(0, min(100, old_affection + change))
    
    # Check exclusive relationship limits
    try:
        from main import check_exclusive_relationship_limit
        allowed, blocking_npc = check_exclusive_relationship_limit(player_id, npc_id, potential_new_affection)
        
        if not allowed and blocking_npc:
            # Block the increase, cap at 80% if trying to go higher
            if potential_new_affection > 80:
                npc_data["affection_level"] = 80
                # Set appropriate relationship status for 80%
                for threshold, status in reversed(list(AFFECTION_THRESHOLDS.items())):
                    if 80 >= threshold:
                        npc_data["relationship_status"] = status
                        break
                return old_affection, 80, f"🔒 **Exclusive Relationship Limit**: {blocking_npc} is your soulmate (100% affection). Others cannot exceed 80% affection."
            else:
                npc_data["affection_level"] = potential_new_affection
        else:
            npc_data["affection_level"] = potential_new_affection
    except:
        # If there's an error with the exclusive check, just apply normal affection
        npc_data["affection_level"] = potential_new_affection
    
    # Update relationship status based on affection
    new_affection = npc_data["affection_level"]
    for threshold, status in reversed(list(AFFECTION_THRESHOLDS.items())):
        if new_affection >= threshold:
            npc_data["relationship_status"] = status
            break
    
    # Handle special message for reaching 100% (soulmate status)
    exclusive_message = ""
    if new_affection >= 100 and old_affection < 100:
        # Count how many other NPCs were reduced to 80%
        capped_npcs = []
        for other_npc_id in NPCS.keys():
            if other_npc_id != npc_id:
                other_npc_data = get_npc_data(player_id, other_npc_id)
                if other_npc_data["affection_level"] == 80:  # Newly capped
                    capped_npcs.append(other_npc_data["name"])
        
        if capped_npcs:
            if len(capped_npcs) == 1:
                exclusive_message = f"💔 **Exclusive Bond**: {capped_npcs[0]}'s affection was capped at 80% due to your exclusive relationship with {npc_data['name']}."
            else:
                exclusive_message = f"💔 **Exclusive Bond**: {len(capped_npcs)} other NPCs had their affection capped at 80% due to your exclusive relationship with {npc_data['name']}."
    
    return old_affection, new_affection, exclusive_message if exclusive_message else ""

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