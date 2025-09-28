import os
import asyncio
import json
import redis.asyncio as redis
from dotenv import load_dotenv

from db import init_db_pool, log_species_event

# Load environment variables from .env
load_dotenv()

REDIS_URL = os.environ["REDIS_URL"]

async def handle_respawn_events():
    """Subscribe to Redis channel and log species events into Supabase."""
    client = redis.from_url(REDIS_URL, decode_responses=True)
    pubsub = client.pubsub()
    await pubsub.subscribe("pot_events")
    print("[READY] Listening for PlayerRespawn events...")

    async for msg in pubsub.listen():
        if msg.get("type") != "message":
            continue

        try:
            payload = json.loads(msg["data"])
        except Exception:
            continue

        # Only handle PlayerRespawn events
        if payload.get("event") != "PlayerRespawn":
            continue

        # Extract description
        desc = payload["data"]["embeds"][0]["description"]
        details = {}
        for line in desc.splitlines():
            clean = line.strip().replace("**", "")
            if ": " in clean:
                k, v = clean.split(": ", 1)
                details[k] = v

        dino = details.get("DinosaurType")
        aid = details.get("PlayerAlderonId")

        if dino and aid:
            await log_species_event(aid, dino)
            print(f"[LOGGED] {aid} spawned as {dino}")

async def main():
    await init_db_pool()
    await handle_respawn_events()

if __name__ == "__main__":
    asyncio.run(main())