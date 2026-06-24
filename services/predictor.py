import numpy as np, pandas as pd, joblib, os, json
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import xgboost as xgb

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "melb_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")

class PricePredictor:
    def __init__(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        self.rf_model = self.xgb_model = self.lr_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.model_stats = {}
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(os.path.join(MODEL_DIR, "rf_model.pkl")):
            print("[MelbProp] Loading saved models...")
            self._load_models()
        else:
            print("[MelbProp] Training models (first run ~60s)...")
            self._train_models()

    def _prepare(self, df):
        df = df.copy().dropna(subset=["Price"])
        for col in ["BuildingArea","YearBuilt","Landsize","Bathroom","Car","Lattitude","Longtitude"]:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        for col in ["Type","Method","Suburb"]:
            if col in df.columns:
                le = LabelEncoder()
                df[col+"_enc"] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        return df

    def _Xmat(self, df):
        return df[["Rooms","Type_enc","Method_enc","Distance","Landsize",
                   "BuildingArea","YearBuilt","Bathroom","Car",
                   "Lattitude","Longtitude","Suburb_enc"]].fillna(0).values

    def _synthetic(self):
        np.random.seed(42); n = 3000
        suburbs = ["Richmond","Fitzroy","Collingwood","Hawthorn","St Kilda",
                   "Carlton","South Yarra","Prahran","Toorak","Malvern",
                   "Brunswick","Footscray","Essendon","Moonee Ponds","Glen Waverley"]
        sub=np.random.choice(suburbs,n); rooms=np.random.randint(1,7,n)
        dist=np.random.uniform(1,40,n); ba=np.random.uniform(50,450,n)
        land=np.random.uniform(0,1200,n); yb=np.random.randint(1900,2022,n)
        price=200000+rooms*90000+(40-dist)*6000+ba*1800+land*400+(yb-1900)*1500+np.random.normal(0,80000,n)
        return pd.DataFrame({"Suburb":sub,"Rooms":rooms,"Type":np.random.choice(["h","u","t"],n),
            "Method":np.random.choice(["S","PI","VB","SA","SP"],n),"Distance":dist,
            "Landsize":land,"BuildingArea":ba,"YearBuilt":yb,
            "Bathroom":np.random.randint(1,4,n),"Car":np.random.randint(0,4,n),
            "Lattitude":np.random.uniform(-37.95,-37.65,n),
            "Longtitude":np.random.uniform(144.85,145.20,n),"Price":price})

    def _train_models(self):
        try:
            df = pd.read_csv(DATA_PATH); print(f"[MelbProp] Dataset: {len(df)} rows")
        except FileNotFoundError:
            print("[MelbProp] No CSV - using synthetic data"); df = self._synthetic()
        df = self._prepare(df)
        X, y = self._Xmat(df), df["Price"].values
        Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2,random_state=42)
        Xtr_sc=self.scaler.fit_transform(Xtr); Xte_sc=self.scaler.transform(Xte)
        self.rf_model=RandomForestRegressor(n_estimators=200,max_depth=15,min_samples_split=5,random_state=42,n_jobs=-1)
        self.rf_model.fit(Xtr,ytr)
        self.xgb_model=xgb.XGBRegressor(n_estimators=200,learning_rate=0.05,max_depth=8,random_state=42,n_jobs=-1,verbosity=0)
        self.xgb_model.fit(Xtr,ytr)
        self.lr_model=LinearRegression(); self.lr_model.fit(Xtr_sc,ytr)
        def m(yt,yp): return {"mae":float(mean_absolute_error(yt,yp)),"r2":float(r2_score(yt,yp)),"rmse":float(np.sqrt(mean_squared_error(yt,yp)))}
        self.model_stats={"random_forest":m(yte,self.rf_model.predict(Xte)),
                          "xgboost":m(yte,self.xgb_model.predict(Xte)),
                          "linear_regression":m(yte,self.lr_model.predict(Xte_sc))}
        self._save_models(); print("[MelbProp] Models saved!")

    def _save_models(self):
        joblib.dump(self.rf_model,os.path.join(MODEL_DIR,"rf_model.pkl"))
        joblib.dump(self.xgb_model,os.path.join(MODEL_DIR,"xgb_model.pkl"))
        joblib.dump(self.lr_model,os.path.join(MODEL_DIR,"lr_model.pkl"))
        joblib.dump(self.scaler,os.path.join(MODEL_DIR,"scaler.pkl"))
        joblib.dump(self.label_encoders,os.path.join(MODEL_DIR,"encoders.pkl"))
        with open(os.path.join(MODEL_DIR,"stats.json"),"w") as f: json.dump(self.model_stats,f,indent=2)

    def _load_models(self):
        self.rf_model=joblib.load(os.path.join(MODEL_DIR,"rf_model.pkl"))
        self.xgb_model=joblib.load(os.path.join(MODEL_DIR,"xgb_model.pkl"))
        self.lr_model=joblib.load(os.path.join(MODEL_DIR,"lr_model.pkl"))
        self.scaler=joblib.load(os.path.join(MODEL_DIR,"scaler.pkl"))
        self.label_encoders=joblib.load(os.path.join(MODEL_DIR,"encoders.pkl"))
        with open(os.path.join(MODEL_DIR,"stats.json")) as f: self.model_stats=json.load(f)

    def _enc(self,key,val):
        le=self.label_encoders.get(key)
        if not le: return 0
        s=str(val); return int(le.transform([s])[0]) if s in le.classes_ else 0

    def predict(self,p):
        X=np.array([[p.get("rooms",3),self._enc("Type",p.get("type","h")),
                     self._enc("Method",p.get("method","S")),p.get("distance",10),
                     p.get("landsize",400),p.get("building_area",150),p.get("year_built",2000),
                     p.get("bathroom",1),p.get("car",1),p.get("latitude",-37.81),
                     p.get("longitude",144.96),self._enc("Suburb",p.get("suburb",""))]],dtype=float)
        Xsc=self.scaler.transform(X)
        rf=float(self.rf_model.predict(X)[0]); xg=float(self.xgb_model.predict(X)[0])
        lr=float(self.lr_model.predict(Xsc)[0])
        pred=max(100000,0.5*rf+0.35*xg+0.15*lr)
        ba=max(1,p.get("building_area",150) or 150)
        conf="high" if abs(rf-xg)/max(pred,1)<0.10 else "medium"
        return {"predicted_price":round(pred),"price_range":{"low":round(pred*0.92),"high":round(pred*1.08)},
                "price_per_sqm":round(pred/ba),"confidence":conf,
                "model_comparison":{"random_forest":round(rf),"xgboost":round(xg),"linear_regression":round(lr)}}

    def get_model_stats(self): return self.model_stats
