import os, asyncpg
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL","")


class DBService:
    def __init__(self): self.pool = None

    async def _get_pool(self):
        if not DATABASE_URL: return None
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(DATABASE_URL, ssl="require", min_size=1, max_size=5)
                await self._create_tables()
            except Exception as e:
                print(f"[DB] Error: {e}"); self.pool = None
        return self.pool

    async def _create_tables(self):
        async with self.pool.acquire() as c:
            await c.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY, suburb VARCHAR(100), rooms INTEGER,
                    type VARCHAR(5), distance FLOAT, landsize FLOAT,
                    building_area FLOAT, predicted_price BIGINT,
                    latitude FLOAT, longitude FLOAT, created_at TIMESTAMP DEFAULT NOW()
                )""")

    async def save_prediction(self, d: dict):
        p = await self._get_pool()
        if not p: return
        try:
            async with p.acquire() as c:
                await c.execute(
                    "INSERT INTO predictions (suburb,rooms,type,distance,landsize,building_area,predicted_price,latitude,longitude) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)",
                    d.get("suburb"), int(d.get("rooms",0)), d.get("type"),
                    float(d.get("distance",0)), float(d.get("landsize",0)),
                    float(d.get("building_area",0)), int(d.get("predicted_price",0)),
                    float(d.get("latitude",0)), float(d.get("longitude",0)))
        except Exception as e: print(f"[DB] Save error: {e}")

    async def get_history(self, limit=20):
        p = await self._get_pool()
        if not p: return []
        try:
            async with p.acquire() as c:
                rows = await c.fetch("SELECT * FROM predictions ORDER BY created_at DESC LIMIT $1", limit)
                return [dict(r) for r in rows]
        except Exception as e:
            print(f"[DB] Fetch error: {e}"); return []
