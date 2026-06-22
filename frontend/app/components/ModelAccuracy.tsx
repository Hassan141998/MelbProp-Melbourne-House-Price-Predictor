"use client";
import { formatShort } from "@/lib/api";

const META: Record<string, { label: string; color: string; desc: string }> = {
  random_forest:     { label: "Random Forest",     color: "#0057b7", desc: "Primary — 50% ensemble weight" },
  xgboost:           { label: "XGBoost",           color: "#1a1a2e", desc: "Secondary — 35% ensemble weight" },
  linear_regression: { label: "Linear Regression", color: "#d4a017", desc: "Baseline — 15% ensemble weight" },
};

export default function ModelAccuracy({ stats }: { stats: Record<string, any> }) {
  const best = Object.entries(stats).reduce(
    (acc, [k, v]) => (v.r2 > acc.r2 ? { k, r2: v.r2 } : acc),
    { k: "", r2: -Infinity }
  );

  return (
    <div className="space-y-3">
      {Object.entries(stats).map(([key, s]) => {
        const m = META[key] || { label: key, color: "#888", desc: "" };
        return (
          <div key={key} className="border border-charcoal/10 p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: m.color }} />
                <span className="font-mono text-xs font-bold">{m.label}</span>
                {best.k === key && (
                  <span className="font-mono text-[9px] bg-melb-gold text-white px-1.5 py-0.5 rounded">BEST</span>
                )}
              </div>
              <span className="font-mono text-[10px] text-charcoal/40">{m.desc}</span>
            </div>
            <div className="grid grid-cols-3 gap-3 font-mono text-xs">
              <div>
                <p className="text-charcoal/40 text-[10px] mb-1">R² Score</p>
                <div className="h-1.5 bg-sand-dark rounded overflow-hidden mb-1">
                  <div className="h-full rounded" style={{ width: `${Math.round(s.r2 * 100)}%`, background: m.color }} />
                </div>
                <p className="font-bold">{s.r2.toFixed(3)}</p>
              </div>
              <div>
                <p className="text-charcoal/40 text-[10px] mb-1">MAE</p>
                <p className="font-bold">{formatShort(s.mae)}</p>
              </div>
              <div>
                <p className="text-charcoal/40 text-[10px] mb-1">RMSE</p>
                <p className="font-bold">{formatShort(s.rmse)}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
