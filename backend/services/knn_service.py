import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import joblib
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/melb_data.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models")

# Melbourne house image mapping by type
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
            df = df.dropna(subset=["Price", "Rooms", "Distance", "BuildingArea", "Landsize"])
            df["BuildingArea"] = df["BuildingArea"].fillna(df["BuildingArea"].median())
            df["Lattitude"] = df["Lattitude"].fillna(df["Lattitude"].mean())
            df["Longtitude"] = df["Longtitude"].fillna(df["Longtitude"].mean())
        except FileNotFoundError:
            df = self._generate_synthetic()

        self.data = df.reset_index(drop=True)
        features = ["Rooms", "Distance", "BuildingArea", "Landsize", "Lattitude", "Longtitude"]
        X = df[features].fillna(0).values
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.knn = NearestNeighbors(n_neighbors=6, metric="euclidean")
        self.knn.fit(X_scaled)

    def _generate_synthetic(self):
        np.random.seed(42)
        n = 500
        suburbs = ["Richmond", "Fitzroy", "Collingwood", "Hawthorn", "St Kilda",
                   "Carlton", "South Yarra", "Prahran", "Toorak", "Malvern"]
        df = pd.DataFrame({
            "Suburb": np.random.choice(suburbs, n),
            "Rooms": np.random.randint(1, 6, n),
            "Type": np.random.choice(["h", "u", "t"], n),
            "Method": np.random.choice(["S", "PI", "VB"], n),
            "Distance": np.random.uniform(1, 30, n),
            "Landsize": np.random.uniform(0, 1000, n),
            "BuildingArea": np.random.uniform(50, 400, n),
            "YearBuilt": np.random.randint(1920, 2020, n),
            "Bathroom": np.random.randint(1, 4, n),
            "Car": np.random.randint(0, 3, n),
            "Lattitude": np.random.uniform(-37.9, -37.7, n),
            "Longtitude": np.random.uniform(144.9, 145.2, n),
            "Price": np.random.uniform(400000, 2000000, n),
        })
        return df

    def find_similar(self, prop: dict, n: int = 5):
        if self.knn is None:
            return []

        query = np.array([[
            prop.get("rooms", 3),
            prop.get("distance", 10),
            prop.get("building_area", 150),
            prop.get("landsize", 500),
            prop.get("latitude", -37.81),
            prop.get("longitude", 144.96),
        ]])

        query_scaled = self.scaler.transform(query)
        distances, indices = self.knn.kneighbors(query_scaled, n_neighbors=min(n + 1, len(self.data)))

        results = []
        prop_type = prop.get("type", "h")
        images = HOUSE_IMAGES.get(prop_type, HOUSE_IMAGES["h"])

        for i, (dist, idx) in enumerate(zip(distances[0][1:], indices[0][1:])):
            row = self.data.iloc[idx]
            results.append({
                "suburb": str(row.get("Suburb", "Unknown")),
                "rooms": int(row.get("Rooms", 0)),
                "type": str(row.get("Type", "h")),
                "distance": float(row.get("Distance", 0)),
                "building_area": float(row.get("BuildingArea", 0)),
                "landsize": float(row.get("Landsize", 0)),
                "year_built": int(row.get("YearBuilt", 2000)) if not pd.isna(row.get("YearBuilt", 2000)) else 2000,
                "price": float(row.get("Price", 0)),
                "similarity_score": round(1 / (1 + dist), 3),
                "image": images[i % len(images)],
                "latitude": float(row.get("Lattitude", -37.81)),
                "longitude": float(row.get("Longtitude", 144.96)),
            })

        return results
