"use client";
import { useEffect, useState } from "react";
import { API, formatShort, formatPrice } from "@/lib/api";
import { AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

export default function PriceTrends() {
  const [trends,  setTrends]  = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.getPriceTrends()
      .then(d => setTrends(Array.isArray(d) ? d : []))
      .catch(() => setTrends([]))
      .finally(() => setLoading(false));
  }, []);

  const growth = trends.length >= 2
    ? (((trends.at(-1)!.median_price - trends[0].median_price) / trends[0].median_price) * 100).toFixed(1)
    : null;

  return (
    <div className="max-w-5xl mx-auto space-y-5">
      <div className="bg-white border border-charcoal/10 shadow-sm">
        <div className="bg-charcoal px-5 py-2.5 flex justify-between items-center">
          <span className="font-mono text-xs uppercase tracking-widest text-sand">Melbourne Median Price Trend</span>
          {growth && <span className="font-mono text-xs text-melb-gold">+{growth}% total growth</span>}
        </div>
        <div className="p-5">
          {loading ? (
            <div className="h-56 flex items-center justify-center font-mono text-xs text-charcoal/30">Loading…</div>
          ) : trends.length === 0 ? (
            <div className="h-56 flex items-center justify-center font-mono text-xs text-charcoal/30 text-center">
              No trend data.<br />Add <code>melb_data.csv</code> to <code>MelbProp/data/</code>
            </div>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends} margin={{ top: 8, right: 16, left: 36, bottom: 4 }}>
                  <defs>
                    <linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#0057b7" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#0057b7" stopOpacity={0}    />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1a2e0d" />
                  <XAxis dataKey="year" tick={{ fontFamily: "Space Mono", fontSize: 11 }} />
                  <YAxis tickFormatter={v => formatShort(v)} tick={{ fontFamily: "Space Mono", fontSize: 9 }} />
                  <Tooltip
                    formatter={(v: number) => [formatPrice(v), "Median Price"]}
                    contentStyle={{ fontFamily: "Space Mono", fontSize: 11, background: "#1a1a2e", color: "#f5f0e8", border: "none" }}
                    labelStyle={{ color: "#d4a017" }}
                  />
                  <Area type="monotone" dataKey="median_price"
                    stroke="#0057b7" strokeWidth={2.5}
                    fill="url(#pg)"
                    dot={{ fill: "#0057b7", r: 4 }}
                    activeDot={{ r: 6, fill: "#d4a017" }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Summary cards */}
      {trends.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "First Year",     value: String(trends[0].year)    },
            { label: "Latest Year",    value: String(trends.at(-1)!.year) },
            { label: "Lowest Median",  value: formatShort(Math.min(...trends.map(t => t.median_price))) },
            { label: "Highest Median", value: formatShort(Math.max(...trends.map(t => t.median_price))) },
          ].map(({ label, value }) => (
            <div key={label} className="bg-white border border-charcoal/10 p-4 text-center">
              <p className="font-mono text-[10px] uppercase tracking-widest text-charcoal/35 mb-1">{label}</p>
              <p className="font-serif text-xl font-bold text-melb-blue">{value}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
