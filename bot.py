import os
import discord
from discord import app_commands
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_time = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    if not count_voice_time.is_running():
        count_voice_time.start()

@tasks.loop(minutes=1)
async def count_voice_time():
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            for member in vc.members:
                if not member.bot:
                    voice_time[member.id] = voice_time.get(member.id, 0) + 60

@count_voice_time.before_loop
async def before_count():
    await bot.wait_until_ready()

@bot.tree.command(name="hello", description="Check if the bot is online")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hello {interaction.user.mention}! The bot is online."
    )

@bot.tree.command(name="profile", description="Check your personal voice time and points")
async def profile(interaction: discord.Interaction):
    total_sec = voice_time.get(interaction.user.id, 0)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    points = total_sec // 60

    embed = discord.Embed(
        title=f"{interaction.user.display_name}'s Profile",
        color=discord.Color.from_rgb(255, 182, 193)
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="Voice Time", value=f"{hours} hrs {minutes} mins", inline=False)
    embed.add_field(name="Points", value=f"{points} pts", inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="top", description="View the Top 10 Online Eboy & Egirl leaderboard")
async def top(interaction: discord.Interaction):
    if not voice_time:
        await interaction.response.send_message("No users in voice channels yet.")
        return

    sorted_users = sorted(voice_time.items(), key=lambda x: x[1], reverse=True)
    top_10 = sorted_users[:10]

    embed = discord.Embed(
        title="Top 10 Online Eboy & Egirl",
        color=discord.Color.from_rgb(255, 182, 193)
    )

    description = ""
    for idx, (member_id, total_sec) in enumerate(top_10, 1):
        member = interaction.guild.get_member(member_id)
        name = member.mention if member else f"Unknown User ({member_id})"
        hours = total_sec // 3600
        minutes = (total_sec % 3600) // 60
        points = total_sec // 60

        # :emoji_11: = อุ้งเท้าขาว (หน้าอันดับ), :emoji_10: = อุ้งเท้าดำ (หน้าเวลาและพ้อยท์)
        description += f":emoji_11: #{idx} {name} — :emoji_10: {points} pts ({hours}h {minutes}m)\n"

    embed.description = description
    await interaction.response.send_message(embed=embed)
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

token = os.environ.get("DISCORD_TOKEN")
if not token:
    print("ERROR: DISCORD_TOKEN not found. Please set it in Render Environment Variables.")
else:
    bot.run(token)
