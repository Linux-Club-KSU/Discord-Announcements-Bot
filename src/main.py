import json
import os

import discord
from discord.client import Client
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = "data"  # should be the same directory where api.py will read from
TOKEN = str(os.getenv("DISCORD_TOKEN"))
channel_ids: list[str] = str(os.getenv("CHANNEL_IDS")).split()
WATCHED_CHANNEL_IDS: list[int] = list(map(int, channel_ids))


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
os.makedirs(OUTPUT_DIR, exist_ok=True)


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def json_path(channel_id: int) -> str:
    return os.path.join(OUTPUT_DIR, f"{channel_id}.json")


def message_to_dict(message: discord.Message) -> dict:
    return {
        "id": message.id,
        "author": str(message.author),
        "author_id": message.author.id,
        "content": message.content,
        "timestamp": message.created_at.isoformat(),
        "attachments": [a.url for a in message.attachments],
    }


def load_history(channel_id: int) -> list:
    path = json_path(channel_id)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(channel_id: int, data: list) -> None:
    path = json_path(channel_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def initial_dump(channel: discord.abc.Messageable, channel_id: int) -> None:
    """Pull full history once, oldest-first, and write it to disk."""
    print(f"Dumping full history for channel {channel_id}...")
    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        messages.append(message_to_dict(msg))
    save_history(channel_id, messages)
    print(f"Saved {len(messages)} messages to {json_path(channel_id)}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    for channel_id in WATCHED_CHANNEL_IDS:
        channel = client.get_channel(channel_id)
        if channel is None:
            print(
                f"WARNING: could not find channel {channel_id} (check ID/permissions)"
            )
            continue

        # Only do the big initial dump if we don't already have a file.
        if not os.path.exists(json_path(channel_id)):
            await initial_dump(channel, channel_id)
        else:
            print(
                f"History file already exists for {channel_id}, skipping initial dump."
            )

    print("Now watching for new messages...")


@client.event
async def on_message(message: discord.Message):
    if message.channel.id not in WATCHED_CHANNEL_IDS:
        return

    history = load_history(message.channel.id)
    history.append(message_to_dict(message))
    save_history(message.channel.id, history)

    print(f"[{message.channel.id}] logged message from {message.author}")


client.run(TOKEN)
