import pandas as pd
import numpy as np
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/melb_data.csv")


class StatsService:
    def __init__(self):
        self.df = None
        self._load_data()

    def _load_data(self):
        try:
            df = pd.read_csv(DATA_PATH)
            df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
            df["Year"] = df["Date"].dt.year
            self.df = df
        except FileNotFoundError:
            self.df = self._generate_synthetic()

    def _generate_synthetic(self):
        np.random.seed(42)
        n = 2000
        suburbs = [
            "Richmond", "Fitzroy", "Collingwood", "Hawthorn", "St Kilda",
            "Carlton", "South Yarra", "Prahran", "Toorak", "Malvern",
            "Brunswick", "Footscray", "Docklands", "Southbank", "Essendon",
            "Moonee Ponds", "Glen Waverley", "Box Hill", "Dandenong", "Frankston"
        ]
        years = np.random.choice([2013, 2014, 2015, 2016, 2017, 2018], n)
        suburb_list = np.random.choice(suburbs, n)
        base_prices = {s: np.random.uniform(600000, 1800000) for s in suburbs}
        prices = [base_prices[s] * (1 + (y - 2013) * 0.05) + np.random.normal(0, 100000)
                  for s, y in zip(suburb_list, years)]
        return pd.DataFrame({
            "Suburb": suburb_list,
            "Price": prices,
            "Rooms": np.random.randint(1, 6, n),
            "Type": np.random.choice(["h", "u", "t"], n),
            "Distance": np.random.uniform(1, 40, n),
            "BuildingArea": np.random.uniform(50, 400, n),
            "Landsize": np.random.uniform(0, 1000, n),
            "Year": years,
            "Lattitude": np.random.uniform(-37.9, -37.7, n),
            "Longtitude": np.random.uniform(144.9, 145.2, n),
        })

    def get_suburb_stats(self, suburb: str):
        if self.df is None:
            return None

        sub = self.df[self.df["Suburb"].str.lower() == suburb.lower()]
        if sub.empty:
            return None

        sub = sub.dropna(subset=["Price"])
        by_type = {}
        for t in ["h", "u", "t"]:
            t_data = sub[sub["Type"] == t]["Price"]
            if not t_data.empty:
                by_type[t] = {
                    "median": round(t_data.median()),
                    "count": int(t_data.count()),
                }

        return {
            "suburb": suburb,
            "count": int(sub.shape[0]),
            "median_price": round(sub["Price"].median()),
            "mean_price": round(sub["Price"].mean()),
            "min_price": round(sub["Price"].min()),
            "max_price": round(sub["Price"].max()),
            "avg_rooms": round(sub["Rooms"].mean(), 1),
            "avg_building_area": round(sub["BuildingArea"].mean(), 1) if "BuildingArea" in sub else 0,
            "avg_distance": round(sub["Distance"].mean(), 1) if "Distance" in sub else 0,
            "by_type": by_type,
            "latitude": float(sub["Lattitude"].mean()) if "Lattitude" in sub else -37.81,
            "longitude": float(sub["Longtitude"].mean()) if "Longtitude" in sub else 144.96,
        }

    def get_all_suburbs(self):
        if self.df is None:
            return []
        return sorted(self.df["Suburb"].dropna().unique().tolist())

    def get_price_trends(self):
        if self.df is None or "Year" not in self.df.columns:
            return []
        trends = (
            self.df.dropna(subset=["Price", "Year"])
            .groupby("Year")["Price"]
            .median()
            .reset_index()
        )
        return [
            {"year": int(row["Year"]), "median_price": round(row["Price"])}
            for _, row in trends.iterrows()
        ]
