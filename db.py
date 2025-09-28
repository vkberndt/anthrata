import os
import asyncio
import asyncpg
from datetime import datetime, timezone

POOL = None

async def init_db_pool():
    """
    Initialize a global asyncpg connection pool using DB_DSN from environment.
    Example DSN:
    postgresql://postgres:YOURPASSWORD@db.YOURHOST.supabase.co:5432/postgres
    """
    global POOL
    dsn = os.environ.get("DB_DSN")
    if not dsn:
        raise RuntimeError("DB_DSN environment variable not set")

    POOL = await asyncpg.create_pool(
        dsn=dsn,
        min_size=2,
        max_size=10,
        timeout=10
    )
    print("[SQL] Connection pool initialized")

async def log_species_event(aid: str, species: str, event_type: str = "PlayerRespawn"):
    """
    Log a species login event into the database.
    """
    ts = datetime.now(timezone.utc)
    try:
        async with POOL.acquire() as conn:
            await conn.execute(
                """INSERT INTO public.species_logins (ts, aid, species, event_type)
                   VALUES ($1, $2, $3, $4)""",
                ts, aid, species, event_type
            )
        print(f"[SQL] Logged {aid} as {species} at {ts.isoformat()}")
    except Exception as e:
        print(f"[ERROR] Failed to log event for AID {aid}: {e}")