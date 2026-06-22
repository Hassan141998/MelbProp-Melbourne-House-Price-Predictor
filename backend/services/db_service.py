import os
import asyncpg
from datetime import datetime
from typing import Optional

DATABASE_URL = os.environ.get("DATABASE_URL", "")


class DBService:
    def __init__(self):
        self.pool = None

    async def _get_pool(self):
        if not self.pool and DATABASE_URL:
            try:
                self.pool = await asyncpg.create_pool(DATABASE_URL, ssl="require")
                await self._create_tables()
            except Exception as e:
                print(f"DB connection error: {e}")
        return self.pool

    async def _create_tables(self):
        pool = self.pool
        if not pool:
            return
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    suburb VARCHAR(100),
                    rooms INTEGER,
                    type VARCHAR(5),
                    distance FLOAT,
                    landsize FLOAT,
                    building_area FLOAT,
                    predicted_price BIGINT,
                    latitude FLOAT,
                    longitude FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

    async def save_prediction(self, data: dict):
        pool = await self._get_pool()
        if not pool:
            print("DB not available, skipping save")
            return

        try:
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO predictions
                    (suburb, rooms, type, distance, landsize, building_area, predicted_price, latitude, longitude)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                    data.get("suburb"),
                    data.get("rooms"),
                    data.get("type"),
                    data.get("distance"),
                    data.get("landsize"),
                    data.get("building_area"),
                    int(data.get("predicted_price", 0)),
                    data.get("latitude"),
                    data.get("longitude"),
                )
        except Exception as e:
            print(f"DB save error: {e}")

    async def get_history(self, limit: int = 20):
        pool = await self._get_pool()
        if not pool:
            return []

        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT * FROM predictions ORDER BY created_at DESC LIMIT $1", limit
                )
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"DB fetch error: {e}")
            return []
