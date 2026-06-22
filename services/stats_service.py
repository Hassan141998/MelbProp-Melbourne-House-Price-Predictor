import pandas as pd, numpy as np, os

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "melb_data.csv")


class StatsService:
    def __init__(self):
        self.df = None; self._load()

    def _load(self):
        try:
            df = pd.read_csv(DATA_PATH)
            df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
            df["Year"] = df["Date"].dt.year
            self.df = df
        except FileNotFoundError:
            self.df = self._synthetic()

    def _synthetic(self):
        np.random.seed(7); n = 3000
        suburbs = ["Richmond","Fitzroy","Collingwood","Hawthorn","St Kilda","Carlton",
                   "South Yarra","Prahran","Toorak","Malvern","Brunswick","Footscray",
                   "Essendon","Moonee Ponds","Glen Waverley","Box Hill","Dandenong","Frankston"]
        years = np.random.choice([2013,2014,2015,2016,2017,2018], n)
        sub   = np.random.choice(suburbs, n)
        base  = {s: np.random.uniform(500_000,2_000_000) for s in suburbs}
        prices = [base[s]*(1+(y-2013)*0.06)+np.random.normal(0,120_000) for s,y in zip(sub,years)]
        return pd.DataFrame({"Suburb":sub,"Price":prices,
            "Rooms":np.random.randint(1,7,n),"Type":np.random.choice(["h","u","t"],n),
            "Distance":np.random.uniform(1,40,n),"BuildingArea":np.random.uniform(50,400,n),
            "Landsize":np.random.uniform(0,1200,n),"Year":years,
            "Lattitude":np.random.uniform(-37.95,-37.65,n),
            "Longtitude":np.random.uniform(144.85,145.20,n)})

    def get_suburb_stats(self, suburb: str):
        if self.df is None: return None
        sub = self.df[self.df["Suburb"].str.lower()==suburb.lower()].dropna(subset=["Price"])
        if sub.empty: return None
        by_type = {}
        for t in ["h","u","t"]:
            td = sub[sub["Type"]==t]["Price"]
            if not td.empty: by_type[t] = {"median":round(td.median()),"count":int(td.count())}
        return {"suburb":suburb,"count":int(len(sub)),
                "median_price":round(sub["Price"].median()),
                "mean_price":round(sub["Price"].mean()),
                "min_price":round(sub["Price"].min()),
                "max_price":round(sub["Price"].max()),
                "avg_rooms":round(sub["Rooms"].mean(),1) if "Rooms" in sub else 0,
                "avg_building_area":round(sub["BuildingArea"].mean(),1) if "BuildingArea" in sub else 0,
                "avg_distance":round(sub["Distance"].mean(),1) if "Distance" in sub else 0,
                "by_type":by_type,
                "latitude":float(sub["Lattitude"].mean()) if "Lattitude" in sub else -37.81,
                "longitude":float(sub["Longtitude"].mean()) if "Longtitude" in sub else 144.96}

    def get_all_suburbs(self):
        return sorted(self.df["Suburb"].dropna().unique().tolist()) if self.df is not None else []

    def get_price_trends(self):
        if self.df is None or "Year" not in self.df.columns: return []
        t = (self.df.dropna(subset=["Price","Year"])
               .groupby("Year")["Price"].median().reset_index().sort_values("Year"))
        return [{"year":int(r["Year"]),"median_price":round(r["Price"])} for _,r in t.iterrows()]
