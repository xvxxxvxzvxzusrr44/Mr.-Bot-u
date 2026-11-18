import os
import json
import time
import discord
from discord import app_commands
from discord.ext import commands

# ตั้งค่า Intents (ต้องเปิดใน Discord Developer Portal ด้วย)
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # ซิงค์ Slash Commands เพื่อให้เคลมเหรียญตราได้
        await self.tree.sync()
        print("ซิงค์คำสั่ง Slash Command เรียบร้อยแล้ว!")

bot = MyBot()

# ไฟล์เก็บข้อมูลเวลาและแต้ม (หมายเหตุ: บน Render แบบฟรี ข้อมูลจะรีเซ็ตเมื่อบอทรีสตาร์ท)
DATA_FILE = "voice_data.json"
active_voice = {}  # เก็บเวลาเริ่มเข้าห้อง {user_id: timestamp}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# 1. คำสั่ง Slash Command สำหรับเคลมเหรียญตรา Active Developer
@bot.tree.command(name="hello", description="คำสั่งทดสอบระบบและใช้สำหรับเคลมเหรียญตรานักพัฒนา")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"สวัสดีคุณ {interaction.user.mention}! ระบบบอททำงานปกติ พร้อมสำหรับเคลมเหรียญตราแล้วครับ 🎉"
    )

# 2. ระบบจับเวลาเข้า-ออกห้องเสียง (Voice Channel)
@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    user_id = str(member.id)
    now = time.time()

    # กรณีเพิ่งเข้าห้องเสียง
    if before.channel is None and after.channel is not None:
        active_voice[user_id] = now

    # กรณีออกจากห้องเสียง
    elif before.channel is not None and after.channel is None:
        if user_id in active_voice:
            start_time = active_voice.pop(user_id)
            duration_seconds = int(now - start_time)
            
            if duration_seconds > 0:
                data = load_data()
                if user_id not in data:
                    data[user_id] = {"seconds": 0, "points": 0}
                
                data[user_id]["seconds"] += duration_seconds
                # คำนวณแต้ม: อยู่ครบทุกๆ 1 นาที (60 วินาที) ได้ 1 แต้ม
                data[user_id]["points"] = data[user_id]["seconds"] // 60
                save_data(data)

# 3. คำสั่งดูเวลาและแต้มของตัวเอง
@bot.tree.command(name="profile", description="เช็กเวลาเข้าห้องเสียงและแต้มพ้อยของคุณ")
async def profile(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = load_data()
    
    total_sec = data.get(user_id, {}).get("seconds", 0)
    # บวกเวลาที่กำลังอยู่ในห้องตอนนี้ (ถ้ายังไม่ออก)
    if user_id in active_voice:
        total_sec += int(time.time() - active_voice[user_id])
        
    points = total_sec // 60
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60

    embed = discord.Embed(
        title=f"📊 สถิติของ {interaction.user.display_name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="⏱️ เวลาอยู่ในห้องรวม", value=f"{hours} ชั่วโมง {minutes} นาที", inline=True)
    embed.add_field(name="⭐ แต้มพ้อยสะสม", value=f"{points:,} คะแนน", inline=True)
    await interaction.response.send_message(embed=embed)

# 4. คำสั่งจัดอันดับ Top 10 คนออนไลน์ในห้องเสียงเยอะที่สุด
@bot.tree.command(name="top", description="จัดอันดับ Top 10 คนเข้าห้องเสียงนานที่สุด")
async def top(interaction: discord.Interaction):
    data = load_data()
    now = time.time()
    
    # รวมเวลาของคนที่กำลังอยู่ในห้องปัจจุบันเข้าไปคำนวณด้วย
    combined = {}
    for uid, stats in data.items():
        combined[uid] = stats.get("seconds", 0)
    for uid, start_t in active_voice.items():
        combined[uid] = combined.get(uid, 0) + int(now - start_t)

    if not combined:
        await interaction.response.send_message("ยังไม่มีข้อมูลสถิติการเข้าห้องเสียงในขณะนี้ครับ")
        return

    # เรียงลำดับจากมากไปน้อย เอาแค่ 10 อันดับแรก
    sorted_users = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:10]

    embed = discord.Embed(
        title="🏆 อันดับ Top 10 นักสิงห้องเสียงประจำเซิร์ฟเวอร์",
        color=discord.Color.gold()
    )
    
    desc_lines = []
    medals = ["🥇", "🥈", "🥉"]
    for idx, (uid, sec) in enumerate(sorted_users, start=1):
        medal = medals[idx - 1] if idx <= 3 else f"**#{idx}**"
        points = sec // 60
        hours = sec // 3600
        minutes = (sec % 3600) // 60
        desc_lines.append(f"{medal} <@{uid}> — **{points:,} แต้ม** ({hours} ชม. {minutes} นาที)")

    embed.description = "\n".join(desc_lines)
    await interaction.response.send_message(embed=embed)

# ดึง Token จาก Environment Variable บน Render
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERROR: ไม่พบตัวแปร DISCORD_TOKEN กรุณาตั้งค่าใน Render")
