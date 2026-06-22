import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import xgboost as xgb
import joblib
import os
import json

# Paths relative to this file's location (services/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "melb_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")


class PricePredictor:
    def __init__(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        self.rf_model = None
        self.xgb_model = None
        self.lr_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model_stats = {}
        self._load_or_train()

    def _load_or_train(self):
        rf_path = os.path.join(MODEL_DIR, "rf_model.pkl")
        if os.path.exists(rf_path):
            print("Loading existing models...")
            self._load_models()
        else:
            print("Training models for first time (this takes ~30-60 seconds)...")
            self._train_models()

    def _prepare_data(self, df: pd.DataFrame):
        df = df.copy()
        df = df.dropna(subset=["Price"])

        num_cols = ["BuildingArea", "YearBuilt", "Landsize", "Bathroom", "Car", "Lattitude", "Longtitude"]
        for col in num_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())

        for col in ["Type", "Method", "Suburb"]:
            if col in df.columns:
                le = LabelEncoder()
                df[col + "_enc"] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le

        return df

    def _build_X(self, df: pd.DataFrame):
        return df[[
            "Rooms", "Type_enc", "Method_enc", "Distance",
            "Landsize", "BuildingArea", "YearBuilt", "Bathroom", "Car",
            "Lattitude", "Longtitude", "Suburb_enc"
        ]].fillna(0).values

    def _train_models(self):
        try:
            df = pd.read_csv(DATA_PATH)
            print(f"Loaded dataset: {len(df)} rows")
        except FileNotFoundError:
            print(f"Dataset not found at {DATA_PATH}. Using synthetic data.")
            df = self._synthetic_data()

        df = self._prepare_data(df)
        X = self._build_X(df)
        y = df["Price"].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_tr_sc = self.scaler.fit_transform(X_train)
        X_te_sc = self.scaler.transform(X_test)

        # Random Forest
        print("Training Random Forest...")
        self.rf_model = RandomForestRegressor(n_estimators=200, max_depth=15,
                                               min_samples_split=5, random_state=42, n_jobs=-1)
        self.rf_model.fit(X_train, y_train)
        rf_pred = self.rf_model.predict(X_test)

        # XGBoost
        print("Training XGBoost...")
        self.xgb_model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05,
                                            max_depth=8, random_state=42, n_jobs=-1, verbosity=0)
        self.xgb_model.fit(X_train, y_train)
        xgb_pred = self.xgb_model.predict(X_test)

        # Linear Regression
        print("Training Linear Regression...")
        self.lr_model = LinearRegression()
        self.lr_model.fit(X_tr_sc, y_train)
        lr_pred = self.lr_model.predict(X_te_sc)

        self.model_stats = {
            "random_forest": {
                "mae": float(mean_absolute_error(y_test, rf_pred)),
                "r2":  float(r2_score(y_test, rf_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, rf_pred))),
            },
            "xgboost": {
                "mae": float(mean_absolute_error(y_test, xgb_pred)),
                "r2":  float(r2_score(y_test, xgb_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, xgb_pred))),
            },
            "linear_regression": {
                "mae": float(mean_absolute_error(y_test, lr_pred)),
                "r2":  float(r2_score(y_test, lr_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, lr_pred))),
            },
        }
        print("All models trained. Saving...")
        self._save_models()
        print("Done! Models saved to /models/")

    def _synthetic_data(self) -> pd.DataFrame:
        np.random.seed(42)
        n = 3000
        suburbs = ["Richmond", "Fitzroy", "Collingwood", "Hawthorn", "St Kilda",
                   "Carlton", "South Yarra", "Prahran", "Toorak", "Malvern",
                   "Brunswick", "Footscray", "Essendon", "Moonee Ponds", "Glen Waverley"]
        suburb_arr = np.random.choice(suburbs, n)
        rooms = np.random.randint(1, 7, n)
        dist  = np.random.uniform(1, 40, n)
        barea = np.random.uniform(50, 450, n)
        land  = np.random.uniform(0, 1200, n)
        yrbuilt = np.random.randint(1900, 2022, n)
        price = (
            200000
            + rooms * 90000
            + (40 - dist) * 6000
            + barea * 1800
            + land * 400
            + (yrbuilt - 1900) * 1500
            + np.random.normal(0, 80000, n)
        )
        return pd.DataFrame({
            "Suburb": suburb_arr,
            "Rooms": rooms,
            "Type": np.random.choice(["h", "u", "t"], n),
            "Method": np.random.choice(["S", "PI", "VB", "SA", "SP"], n),
            "Distance": dist,
            "Landsize": land,
            "BuildingArea": barea,
            "YearBuilt": yrbuilt,
            "Bathroom": np.random.randint(1, 4, n),
            "Car": np.random.randint(0, 4, n),
            "Lattitude": np.random.uniform(-37.95, -37.65, n),
            "Longtitude": np.random.uniform(144.85, 145.20, n),
            "Price": price,
        })

    def _save_models(self):
        joblib.dump(self.rf_model,       os.path.join(MODEL_DIR, "rf_model.pkl"))
        joblib.dump(self.xgb_model,      os.path.join(MODEL_DIR, "xgb_model.pkl"))
        joblib.dump(self.lr_model,       os.path.join(MODEL_DIR, "lr_model.pkl"))
        joblib.dump(self.scaler,         os.path.join(MODEL_DIR, "scaler.pkl"))
        joblib.dump(self.label_encoders, os.path.join(MODEL_DIR, "encoders.pkl"))
        with open(os.path.join(MODEL_DIR, "stats.json"), "w") as f:
            json.dump(self.model_stats, f, indent=2)

    def _load_models(self):
        self.rf_model       = joblib.load(os.path.join(MODEL_DIR, "rf_model.pkl"))
        self.xgb_model      = joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl"))
        self.lr_model       = joblib.load(os.path.join(MODEL_DIR, "lr_model.pkl"))
        self.scaler         = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
        self.label_encoders = joblib.load(os.path.join(MODEL_DIR, "encoders.pkl"))
        with open(os.path.join(MODEL_DIR, "stats.json")) as f:
            self.model_stats = json.load(f)

    def _encode_input(self, prop: dict) -> np.ndarray:
        def safe_enc(key, val):
            le = self.label_encoders.get(key)
            if le is None:
                return 0
            val = str(val)
            if val in le.classes_:
                return int(le.transform([val])[0])
            return 0

        return np.array([[
            prop.get("rooms", 3),
            safe_enc("Type", prop.get("type", "h")),
            safe_enc("Method", prop.get("method", "S")),
            prop.get("distance", 10.0),
            prop.get("landsize", 400.0),
            prop.get("building_area", 150.0),
            prop.get("year_built", 2000),
            prop.get("bathroom", 1),
            prop.get("car", 1),
            prop.get("latitude", -37.8136),
            prop.get("longitude", 144.9631),
            safe_enc("Suburb", prop.get("suburb", "")),
        ]], dtype=float)

    def predict(self, prop: dict) -> dict:
        X = self._encode_input(prop)
        X_sc = self.scaler.transform(X)

        rf_price  = float(self.rf_model.predict(X)[0])
        xgb_price = float(self.xgb_model.predict(X)[0])
        lr_price  = float(self.lr_model.predict(X_sc)[0])

        # Weighted ensemble: RF primary
        predicted = max(100_000, 0.5 * rf_price + 0.35 * xgb_price + 0.15 * lr_price)
        ba = max(1, prop.get("building_area", 150) or 150)

        spread = abs(rf_price - xgb_price) / max(predicted, 1)
        confidence = "high" if spread < 0.10 else "medium"

        return {
            "predicted_price": round(predicted),
            "price_range": {
                "low":  round(predicted * 0.92),
                "high": round(predicted * 1.08),
            },
            "price_per_sqm": round(predicted / ba),
            "confidence": confidence,
            "model_comparison": {
                "random_forest":     round(rf_price),
                "xgboost":           round(xgb_price),
                "linear_regression": round(lr_price),
            },
        }

    def get_model_stats(self) -> dict:
        return self.model_stats
