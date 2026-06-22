import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import xgboost as xgb
import joblib
import os
import json

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/melb_data.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models")


class PricePredictor:
    def __init__(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        self.rf_model = None
        self.xgb_model = None
        self.lr_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model_stats = {}
        self.feature_cols = [
            "Rooms", "Type", "Method", "Distance", "Landsize",
            "BuildingArea", "YearBuilt", "Bathroom", "Car",
            "Lattitude", "Longtitude", "Suburb_encoded"
        ]
        self._load_or_train()

    def _load_or_train(self):
        rf_path = os.path.join(MODEL_DIR, "rf_model.pkl")
        if os.path.exists(rf_path):
            self._load_models()
        else:
            self._train_models()

    def _prepare_data(self, df):
        df = df.copy()
        df = df.dropna(subset=["Price"])

        # Fill missing values
        df["BuildingArea"] = df["BuildingArea"].fillna(df["BuildingArea"].median())
        df["YearBuilt"] = df["YearBuilt"].fillna(df["YearBuilt"].median())
        df["Landsize"] = df["Landsize"].fillna(df["Landsize"].median())
        df["Bathroom"] = df["Bathroom"].fillna(1)
        df["Car"] = df["Car"].fillna(1)
        df["Lattitude"] = df["Lattitude"].fillna(df["Lattitude"].mean())
        df["Longtitude"] = df["Longtitude"].fillna(df["Longtitude"].mean())

        # Encode categoricals
        for col in ["Type", "Method", "Suburb"]:
            le = LabelEncoder()
            df[col + "_encoded"] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le

        # Encode type/method inline
        df["Type"] = df["Type_encoded"]
        df["Method"] = df["Method_encoded"]
        df["Suburb_encoded"] = df["Suburb_encoded"]

        # Feature engineering
        df["Price_per_sqm"] = df["Price"] / (df["BuildingArea"] + 1)
        df["Age"] = 2024 - df["YearBuilt"]
        df["Land_Building_ratio"] = df["Landsize"] / (df["BuildingArea"] + 1)

        return df

    def _train_models(self):
        try:
            df = pd.read_csv(DATA_PATH)
        except FileNotFoundError:
            print("Dataset not found. Using synthetic data for demo.")
            df = self._generate_synthetic_data()

        df = self._prepare_data(df)

        feature_cols = [
            "Rooms", "Type", "Method", "Distance", "Landsize",
            "BuildingArea", "YearBuilt", "Bathroom", "Car",
            "Lattitude", "Longtitude", "Suburb_encoded"
        ]

        X = df[feature_cols].fillna(0)
        y = df["Price"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale for LR
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Random Forest
        self.rf_model = RandomForestRegressor(
            n_estimators=200, max_depth=15, min_samples_split=5,
            random_state=42, n_jobs=-1
        )
        self.rf_model.fit(X_train, y_train)
        rf_pred = self.rf_model.predict(X_test)

        # XGBoost
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=200, learning_rate=0.05, max_depth=8,
            random_state=42, n_jobs=-1, verbosity=0
        )
        self.xgb_model.fit(X_train, y_train)
        xgb_pred = self.xgb_model.predict(X_test)

        # Linear Regression
        self.lr_model = LinearRegression()
        self.lr_model.fit(X_train_scaled, y_train)
        lr_pred = self.lr_model.predict(X_test_scaled)

        self.model_stats = {
            "random_forest": {
                "mae": float(mean_absolute_error(y_test, rf_pred)),
                "r2": float(r2_score(y_test, rf_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, rf_pred))),
            },
            "xgboost": {
                "mae": float(mean_absolute_error(y_test, xgb_pred)),
                "r2": float(r2_score(y_test, xgb_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, xgb_pred))),
            },
            "linear_regression": {
                "mae": float(mean_absolute_error(y_test, lr_pred)),
                "r2": float(r2_score(y_test, lr_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, lr_pred))),
            },
        }

        self._save_models()

    def _generate_synthetic_data(self):
        """Generate synthetic Melbourne housing data for demo"""
        np.random.seed(42)
        n = 2000
        suburbs = ["Richmond", "Fitzroy", "Collingwood", "Hawthorn", "St Kilda",
                   "Carlton", "South Yarra", "Prahran", "Toorak", "Malvern",
                   "Brunswick", "Footscray", "Docklands", "Southbank", "CBD"]
        data = {
            "Suburb": np.random.choice(suburbs, n),
            "Rooms": np.random.randint(1, 6, n),
            "Type": np.random.choice(["h", "u", "t"], n),
            "Method": np.random.choice(["S", "PI", "VB", "SA", "SP"], n),
            "Distance": np.random.uniform(1, 40, n),
            "Landsize": np.random.uniform(0, 1000, n),
            "BuildingArea": np.random.uniform(50, 400, n),
            "YearBuilt": np.random.randint(1900, 2020, n),
            "Bathroom": np.random.randint(1, 4, n),
            "Car": np.random.randint(0, 4, n),
            "Lattitude": np.random.uniform(-37.9, -37.7, n),
            "Longtitude": np.random.uniform(144.9, 145.2, n),
            "CouncilArea": np.random.choice(["Melbourne", "Yarra", "Stonnington", "Boroondara"], n),
        }
        # Generate price based on features
        price = (
            300000
            + data["Rooms"] * 80000
            + (40 - np.array(data["Distance"])) * 5000
            + np.array(data["BuildingArea"]) * 1500
            + np.array(data["Landsize"]) * 500
            + np.random.normal(0, 50000, n)
        )
        data["Price"] = price
        return pd.DataFrame(data)

    def _save_models(self):
        joblib.dump(self.rf_model, os.path.join(MODEL_DIR, "rf_model.pkl"))
        joblib.dump(self.xgb_model, os.path.join(MODEL_DIR, "xgb_model.pkl"))
        joblib.dump(self.lr_model, os.path.join(MODEL_DIR, "lr_model.pkl"))
        joblib.dump(self.scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
        joblib.dump(self.label_encoders, os.path.join(MODEL_DIR, "encoders.pkl"))
        with open(os.path.join(MODEL_DIR, "stats.json"), "w") as f:
            json.dump(self.model_stats, f)

    def _load_models(self):
        self.rf_model = joblib.load(os.path.join(MODEL_DIR, "rf_model.pkl"))
        self.xgb_model = joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl"))
        self.lr_model = joblib.load(os.path.join(MODEL_DIR, "lr_model.pkl"))
        self.scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
        self.label_encoders = joblib.load(os.path.join(MODEL_DIR, "encoders.pkl"))
        with open(os.path.join(MODEL_DIR, "stats.json"), "r") as f:
            self.model_stats = json.load(f)

    def _encode_input(self, prop):
        type_enc = self.label_encoders.get("Type")
        method_enc = self.label_encoders.get("Method")
        suburb_enc = self.label_encoders.get("Suburb")

        def safe_encode(encoder, val):
            if encoder is None:
                return 0
            classes = list(encoder.classes_)
            if val in classes:
                return encoder.transform([val])[0]
            return 0

        return np.array([[
            prop.get("rooms", 3),
            safe_encode(type_enc, prop.get("type", "h")),
            safe_encode(method_enc, prop.get("method", "S")),
            prop.get("distance", 10),
            prop.get("landsize", 500),
            prop.get("building_area", 150),
            prop.get("year_built", 2000),
            prop.get("bathroom", 1),
            prop.get("car", 1),
            prop.get("latitude", -37.8136),
            prop.get("longitude", 144.9631),
            safe_encode(suburb_enc, prop.get("suburb", "")),
        ]])

    def predict(self, prop: dict):
        X = self._encode_input(prop)
        X_scaled = self.scaler.transform(X)

        rf_price = float(self.rf_model.predict(X)[0])
        xgb_price = float(self.xgb_model.predict(X)[0])
        lr_price = float(self.lr_model.predict(X_scaled)[0])

        # Ensemble: weighted average (RF primary)
        predicted = 0.5 * rf_price + 0.35 * xgb_price + 0.15 * lr_price
        predicted = max(100000, predicted)

        building_area = prop.get("building_area", 150) or 150
        price_per_sqm = predicted / building_area

        low = predicted * 0.92
        high = predicted * 1.08

        return {
            "predicted_price": round(predicted),
            "price_range": {"low": round(low), "high": round(high)},
            "price_per_sqm": round(price_per_sqm),
            "model_comparison": {
                "random_forest": round(rf_price),
                "xgboost": round(xgb_price),
                "linear_regression": round(lr_price),
            },
            "confidence": "high" if abs(rf_price - xgb_price) / predicted < 0.1 else "medium",
        }

    def get_model_stats(self):
        return self.model_stats
