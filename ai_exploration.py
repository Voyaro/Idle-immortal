import discord
import asyncio
import random
import requests
import os
from discord.ext import commands

# ===============================
# AI Exploration System
# ===============================

# Konfigurasi AI
HF_TOKEN = os.environ.get('HUGGING_FACE_TOKEN')
API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-1.3B"
headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

def query_ai(prompt):
    """Function untuk meminta respons dari AI"""
    if not HF_TOKEN:
        return None

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 150,
            "temperature": 0.9,
            "do_sample": True,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error accessing AI: {e}")
        return None

class AIExploration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_adventures = {}

    @commands.command()
    async def explore(self, ctx):
        """Mulai petualangan AI yang tidak terduga!"""
        user_id = ctx.author.id

        if user_id in self.active_adventures:
            await ctx.send("⏳ Anda sedang dalam petualangan! Selesaikan dulu.")
            return

        # Setup awal petualangan
        initial_prompt = """
        Create a short fantasy adventure prompt with 3 choices. Format:
        [Deskripsi situasi singkat]
        1. [Pilihan aksi 1]
        2. [Pilihan aksi 2] 
        3. [Pilihan aksi 3]
        """

        # Kirim status sedang memproses
        processing_msg = await ctx.send("🧠 AI sedang memikirkan petualangan...")

        # Dapatkan scenario awal dari AI
        ai_response = query_ai(initial_prompt)

        if not ai_response:
            await processing_msg.delete()
            await ctx.send("❌ AI sedang sibuk. Coba lagi nanti!")
            return

        # Extract text dari response
        scenario_text = ai_response[0]['generated_text']

        # Split menjadi deskripsi dan pilihan
        lines = scenario_text.strip().split('\n')
        description = lines[0] if lines else "Kamu memulai petualangan misterius..."
        choices = [line for line in lines[1:] if line.strip() and any(char.isdigit() for char in line)]

        # Jika AI tidak generate cukup pilihan, gunakan default
        if len(choices) < 3:
            choices = [
                "1. Terus menjelajah ke dalam",
                "2. Investigasi area sekitarnya", 
                "3. Beristirahat sejenak"
            ]

        await processing_msg.delete()

        # Tampilkan scenario pertama
        embed = discord.Embed(
            title="🌌 AI Adventure Time!",
            description=f"**{description}**\n\n**Pilihan:**",
            color=0x00ff00
        )

        for choice in choices[:3]:
            embed.add_field(name="\u200b", value=choice, inline=False)

        embed.set_footer(text="Bereaksi dengan emoji untuk memilih!")

        message = await ctx.send(embed=embed)

        # Tambahkan emoji reactions
        emojis = ['1️⃣', '2️⃣', '3️⃣', '❌']
        for emoji in emojis:
            await message.add_reaction(emoji)

        # Simpan data adventure
        self.active_adventures[user_id] = {
            "message": message,
            "current_story": description,
            "choices": choices,
            "adventure_log": [f"Memulai: {description}"],
            "active": True
        }

        # Start adventure task
        asyncio.create_task(self.adventure_task(ctx, user_id))

    async def adventure_task(self, ctx, user_id):
        """Background task untuk adventure"""
        try:
            adventure_data = self.active_adventures[user_id]

            while adventure_data["active"] and user_id in self.active_adventures:
                # Tunggu reaksi user
                def check(reaction, user):
                    return (user.id == user_id and 
                            str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '❌'] and 
                            reaction.message.id == adventure_data["message"].id)

                try:
                    reaction, user = await self.bot.wait_for(
                        'reaction_add', 
                        timeout=120.0, 
                        check=check
                    )

                    # Handle pilihan berhenti
                    if str(reaction.emoji) == '❌':
                        adventure_data["active"] = False
                        end_message = "**Petualangan diakhiri!**\n\n"
                        end_message += "\n".join(adventure_data["adventure_log"])
                        await ctx.send(end_message[:2000])
                        break

                    # Dapatkan pilihan user (1, 2, atau 3)
                    choice_index = ['1️⃣', '2️⃣', '3️⃣'].index(str(reaction.emoji))

                    if choice_index < len(adventure_data["choices"]):
                        # Buat prompt lanjutan
                        continue_prompt = f"""
                        Continue this fantasy adventure story:
                        Previous story: {adventure_data['current_story']}
                        Player chose: {adventure_data['choices'][choice_index]}

                        Create the next part with 3 new choices. Format:
                        [Next story development]
                        1. [Choice 1]
                        2. [Choice 2] 
                        3. [Choice 3]
                        """

                        # Kirim status processing
                        processing_msg = await ctx.send("🧠 AI sedang melanjutkan cerita...")

                        # Dapatkan respons AI
                        ai_continue = query_ai(continue_prompt)

                        await processing_msg.delete()

                        if ai_continue and 'generated_text' in ai_continue[0]:
                            new_story = ai_continue[0]['generated_text']

                            # Parse respons AI
                            new_lines = new_story.strip().split('\n')
                            adventure_data["current_story"] = new_lines[0] if new_lines else "Petualangan berlanjut..."
                            new_choices = [line for line in new_lines[1:] if line.strip() and any(char.isdigit() for char in line)]

                            if len(new_choices) >= 3:
                                adventure_data["choices"] = new_choices[:3]

                            # Update adventure log
                            adventure_data["adventure_log"].append(
                                f"Pilih {choice_index + 1}: {adventure_data['current_story']}"
                            )

                            # Update embed
                            embed = discord.Embed(
                                title="🌠 Petualangan Berlanjut...",
                                description=f"**{adventure_data['current_story']}**\n\n**Pilihan:**",
                                color=0xff9900
                            )

                            for i, choice in enumerate(adventure_data["choices"][:3]):
                                embed.add_field(name="\u200b", value=choice, inline=False)

                            embed.set_footer(text=f"Petualangan #{len(adventure_data['adventure_log'])}")

                            await adventure_data["message"].edit(embed=embed)
                            await adventure_data["message"].clear_reactions()

                            # Tambahkan reactions kembali
                            for emoji in ['1️⃣', '2️⃣', '3️⃣', '❌']:
                                await adventure_data["message"].add_reaction(emoji)

                        else:
                            await ctx.send("❌ AI sedang mengalami gangguan. Petualangan dihentikan.")
                            adventure_data["active"] = False

                    # Hapus reaksi user
                    await adventure_data["message"].remove_reaction(reaction.emoji, user)

                except asyncio.TimeoutError:
                    await ctx.send("⏰ Waktu petualangan habis! Gunakan `!explore` lagi untuk melanjutkan.")
                    adventure_data["active"] = False
                except Exception as e:
                    print(f"Error in adventure: {e}")
                    adventure_data["active"] = False

        finally:
            # Cleanup
            if user_id in self.active_adventures:
                del self.active_adventures[user_id]

    @commands.command()
    async def stop_explore(self, ctx):
        """Hentikan petualangan yang sedang berjalan"""
        user_id = ctx.author.id

        if user_id in self.active_adventures:
            self.active_adventures[user_id]["active"] = False
            await ctx.send("✅ Petualangan dihentikan!")
        else:
            await ctx.send("❌ Anda tidak sedang dalam petualangan!")

async def setup(bot):
    await bot.add_cog(AIExploration(bot))