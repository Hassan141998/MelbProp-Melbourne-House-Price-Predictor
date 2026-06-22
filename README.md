# 🏠 MelbProp — Melbourne House Price Predictor

AI-powered Melbourne property valuations using **Random Forest · XGBoost · Linear Regression**  
Interactive Leaflet map · KNN similar properties with house images · Suburb comparison · Neon DB history · PDF export

---

## ✅ Correct Folder Structure

After unzipping, your PyCharm project root (`E:\pycharm\MelbProp\`) should look exactly like this:

```
MelbProp/                        ← PyCharm project root / git root
│
├── main.py                      ← ✅ Run THIS in PyCharm
├── requirements.txt
├── Procfile                     ← Railway deploy
├── .env                         ← Add DATABASE_URL here
├── .gitignore
│
├── services/
│   ├── __init__.py
│   ├── predictor.py             ← RF + XGBoost + LinearRegression
│   ├── knn_service.py           ← KNN similar properties + house images
│   ├── stats_service.py         ← Suburb stats + price trends
│   └── db_service.py            ← Neon PostgreSQL (async)
│
├── data/
│   └── melb_data.csv            ← Download from Kaggle (see below)
│
├── models/                      ← Auto-created .pkl files on first run
│
└── frontend/                    ← Next.js 14 app
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── tsconfig.json
    ├── vercel.json
    ├── .env.local
    └── app/
        ├── layout.tsx
        ├── page.tsx
        ├── globals.css
        ├── lib/
        │   └── api.ts
        └── components/
            ├── Header.tsx
            ├── MapView.tsx
            ├── PredictionForm.tsx
            ├── ResultPanel.tsx
            ├── SimilarProperties.tsx
            ├── SuburbCompare.tsx
            ├── PriceTrends.tsx
            ├── ModelAccuracy.tsx
            └── PredictionHistory.tsx
```

---

## 🚀 Local Setup (Step by Step)

### Step 1 — Install Python dependencies

In PyCharm terminal (or any terminal at `E:\pycharm\MelbProp\`):

```bash
pip install -r requirements.txt
```

### Step 2 — Get the dataset (optional but recommended)

Download `melb_data.csv` from Kaggle:
👉 https://www.kaggle.com/datasets/dansbecker/melbourne-housing-snapshot

Place it at:
```
E:\pycharm\MelbProp\data\melb_data.csv
```

> **No dataset?** The app auto-generates synthetic Melbourne housing data — all features still work.

### Step 3 — Run the backend

In PyCharm: open `main.py` → click the green ▶ Run button

Or in terminal:
```bash
cd E:\pycharm\MelbProp
python main.py
```

You should see:
```
Training models for first time (this takes ~30-60 seconds)...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Visit: http://localhost:8000/docs  ← Swagger API explorer

### Step 4 — Run the frontend

Open a **second terminal**:

```bash
cd E:\pycharm\MelbProp\frontend
npm install
npm run dev
```

Visit: http://localhost:3000

---

## 📤 GitHub Push Commands

```bash
# Navigate to project root
cd E:\pycharm\MelbProp

# Initialise git (first time only)
git init
git remote add origin https://github.com/YOUR_USERNAME/melbprop.git

# Stage all files
git add .

# Commit
git commit -m "feat: initial MelbProp commit — FastAPI + Next.js + ML ensemble"

# Push
git branch -M main
git push -u origin main

# ── Future pushes ──
git add .
git commit -m "fix: your change description"
git push
```

---

## ☁️ Deploy to Production

### 1. Backend → Railway (free tier)

1. Go to https://railway.app → **New Project** → **Deploy from GitHub repo**
2. Select your repo
3. Set **Root Directory** = `/` (the project root, where `main.py` lives)
4. Railway detects `Procfile` automatically
5. Add environment variable: `DATABASE_URL` = your Neon connection string
6. Copy the generated URL e.g. `https://melbprop.up.railway.app`

### 2. Database → Neon (free tier)

1. Go to https://neon.tech → **Create Project** → name it `melbprop`
2. Copy the **Connection String** from the Dashboard
3. Paste it into:
   - Local: `MelbProp/.env` → `DATABASE_URL=postgresql://...`
   - Railway: Environment Variables → `DATABASE_URL`
4. Tables auto-create on first prediction

### 3. Frontend → Vercel

```bash
# Install Vercel CLI
npm install -g vercel

cd E:\pycharm\MelbProp\frontend

# Deploy (follow prompts — set root to current directory)
vercel

# Set your backend URL
vercel env add NEXT_PUBLIC_API_URL
# Enter: https://melbprop.up.railway.app

# Redeploy with env
vercel --prod
```

Or use Vercel Dashboard:
- Import Git repo → set **Root Directory** to `frontend`
- Add env var `NEXT_PUBLIC_API_URL` = your Railway URL

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/` | Health check |
| GET  | `/api/health` | Status + timestamp |
| POST | `/api/predict-price` | Ensemble price prediction |
| GET  | `/api/suburb-stats/{suburb}` | Suburb statistics |
| POST | `/api/compare-suburbs` | Compare two suburbs |
| GET  | `/api/suburbs` | All suburb names |
| GET  | `/api/history` | Prediction history (Neon) |
| GET  | `/api/price-trends` | Year-by-year median prices |
| GET  | `/api/model-accuracy` | MAE, R², RMSE per model |

Full interactive docs: http://localhost:8000/docs

---

## 🐛 Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `can't open file 'main.py'` | Run from `MelbProp/` root, not a subdirectory |
| `ModuleNotFoundError: xgboost` | Run `pip install -r requirements.txt` |
| `CORS error` in browser | Backend not running — start `python main.py` first |
| Map not showing | Normal on first load — Leaflet needs client-side render |
| History tab empty | Add `DATABASE_URL` to `.env` — works without it, just no history |
| `Cannot find module '@/components/...'` | Run `npm install` inside `frontend/` |

---

## 🎨 Design Tokens

| Name | Hex | Usage |
|------|-----|-------|
| Sand | `#f5f0e8` | Background |
| Charcoal | `#1a1a2e` | Headers, dark panels |
| Melbourne Blue | `#0057b7` | Primary CTA, map markers |
| Melbourne Gold | `#d4a017` | Price highlights |
| Libre Baskerville | — | Display / serif headings |
| Space Mono | — | Data, labels, mono values |
