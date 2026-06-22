import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "melb_data.csv")

# Curated Unsplash images by property type — no upload needed
HOUSE_IMAGES = {
    "h": [
        "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&q=80",
        "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=400&q=80",
        "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&q=80",
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=400&q=80",
        "https://images.unsplash.com/photo-1449844908441-8829872d2607?w=400&q=80",
    ],
    "u": [
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&q=80",
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400&q=80",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400&q=80",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=400&q=80",
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=400&q=80",
    ],
    "t": [
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&q=80",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=400&q=80",
        "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=400&q=80",
        "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=400&q=80",
        "https://images.unsplash.com/photo-1600210492493-0946911123ea?w=400&q=80",
    ],
}


class KNNService:
    def __init__(self):
        self.knn = None
        self.data = None
        self.scaler = StandardScaler()
        self._setup()

    def _setup(self):
        try:
            df = pd.read_csv(DATA_PATH)
        except FileNotFoundError:
            df = self._synthetic()

        needed = ["Price", "Rooms", "Distance", "BuildingArea", "Landsize", "Lattitude", "Longtitude"]
        for col in needed:
            if col not in df.columns:
                df[col] = 0
        df = df.dropna(subset=["Price"]).copy()
        for col in needed[1:]:
            df[col] = df[col].fillna(df[col].median())

        self.data = df.reset_index(drop=True)
        feat_cols = ["Rooms", "Distance", "BuildingArea", "Landsize", "Lattitude", "Longtitude"]
        X = df[feat_cols].values
        self.scaler.fit(X)
        self.knn = NearestNeighbors(n_neighbors=min(6, len(df)), metric="euclidean")
        self.knn.fit(self.scaler.transform(X))

    def _synthetic(self) -> pd.DataFrame:
        np.random.seed(99)
        n = 600
        suburbs = ["Richmond", "Fitzroy", "Collingwood", "Hawthorn", "St Kilda",
                   "Carlton", "South Yarra", "Toorak", "Malvern", "Brunswick"]
        return pd.DataFrame({
            "Suburb":       np.random.choice(suburbs, n),
            "Rooms":        np.random.randint(1, 7, n),
            "Type":         np.random.choice(["h", "u", "t"], n),
            "Distance":     np.random.uniform(1, 30, n),
            "BuildingArea": np.random.uniform(50, 400, n),
            "Landsize":     np.random.uniform(0, 1000, n),
            "YearBuilt":    np.random.randint(1920, 2022, n),
            "Bathroom":     np.random.randint(1, 4, n),
            "Car":          np.random.randint(0, 3, n),
            "Lattitude":    np.random.uniform(-37.95, -37.65, n),
            "Longtitude":   np.random.uniform(144.85, 145.20, n),
            "Price":        np.random.uniform(400_000, 2_500_000, n),
        })

    def find_similar(self, prop: dict, n: int = 5) -> list:
        if self.knn is None:
            return []
        query = np.array([[
            prop.get("rooms", 3),
            prop.get("distance", 10),
            prop.get("building_area", 150),
            prop.get("landsize", 500),
            prop.get("latitude", -37.81),
            prop.get("longitude", 144.96),
        ]], dtype=float)
        query_sc = self.scaler.transform(query)
        distances, indices = self.knn.kneighbors(query_sc, n_neighbors=min(n + 1, len(self.data)))

        prop_type = str(prop.get("type", "h"))
        images = HOUSE_IMAGES.get(prop_type, HOUSE_IMAGES["h"])
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0][1:], indices[0][1:])):
            row = self.data.iloc[idx]
            yb = row.get("YearBuilt", 2000)
            results.append({
                "suburb":           str(row.get("Suburb", "Unknown")),
                "rooms":            int(row.get("Rooms", 0)),
                "type":             str(row.get("Type", "h")),
                "distance":         float(row.get("Distance", 0)),
                "building_area":    float(row.get("BuildingArea", 0)),
                "landsize":         float(row.get("Landsize", 0)),
                "year_built":       int(yb) if not pd.isna(yb) else 2000,
                "price":            float(row.get("Price", 0)),
                "similarity_score": round(1 / (1 + dist), 3),
                "image":            images[i % len(images)],
                "latitude":         float(row.get("Lattitude", -37.81)),
                "longitude":        float(row.get("Longtitude", 144.96)),
            })
        return results
