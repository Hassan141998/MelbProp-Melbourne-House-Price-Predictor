import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()  # reads .env at project root
DATABASE_URL = os.environ.get("DATABASE_URL", "")


class DBService:
    def __init__(self):
        self.pool = None

    async def _get_pool(self):
        if not DATABASE_URL:
            return None
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(DATABASE_URL, ssl="require", min_size=1, max_size=5)
                await self._create_tables()
            except Exception as e:
                print(f"[DB] Connection error: {e}")
                self.pool = None
        return self.pool

    async def _create_tables(self):
        if not self.pool:
            return
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id            SERIAL PRIMARY KEY,
                    suburb        VARCHAR(100),
                    rooms         INTEGER,
                    type          VARCHAR(5),
                    distance      FLOAT,
                    landsize      FLOAT,
                    building_area FLOAT,
                    predicted_price BIGINT,
                    latitude      FLOAT,
                    longitude     FLOAT,
                    created_at    TIMESTAMP DEFAULT NOW()
                );
            """)

    async def save_prediction(self, data: dict):
        pool = await self._get_pool()
        if not pool:
            print("[DB] Skipping save — no DATABASE_URL configured")
            return
        try:
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO predictions
                      (suburb, rooms, type, distance, landsize, building_area, predicted_price, latitude, longitude)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                """,
                    data.get("suburb"),
                    int(data.get("rooms", 0)),
                    data.get("type"),
                    float(data.get("distance", 0)),
                    float(data.get("landsize", 0)),
                    float(data.get("building_area", 0)),
                    int(data.get("predicted_price", 0)),
                    float(data.get("latitude", 0)),
                    float(data.get("longitude", 0)),
                )
        except Exception as e:
            print(f"[DB] Save error: {e}")

    async def get_history(self, limit: int = 20) -> list:
        pool = await self._get_pool()
        if not pool:
            return []
        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT * FROM predictions ORDER BY created_at DESC LIMIT $1", limit
                )
                return [dict(r) for r in rows]
        except Exception as e:
            print(f"[DB] Fetch error: {e}")
            return []
