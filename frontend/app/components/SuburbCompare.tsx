"use client";
import { useState } from "react";
import { API, formatPrice, formatShort } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const DEFAULT = ["Richmond", "Toorak", "Fitzroy", "Hawthorn", "St Kilda", "Carlton"];
const TYPE_LABELS: Record<string, string> = { h: "Houses", u: "Units", t: "Townhouses" };

export default function SuburbCompare({ suburbs }: { suburbs: string[] }) {
  const [s1, setS1]     = useState("Richmond");
  const [s2, setS2]     = useState("Toorak");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error,  setError]   = useState<string | null>(null);

  const list = suburbs.length > 0 ? suburbs : DEFAULT;
  const sel  = "border border-charcoal/20 bg-sand px-3 py-2 font-mono text-sm w-full focus:border-melb-blue outline-none";

  const compare = async () => {
    setLoading(true); setError(null);
    try   { setResult(await API.compareSuburbs(s1, s2)); }
    catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const chart = result
    ? [
        { name: s1, price: result.suburb1?.median_price ?? 0 },
        { name: s2, price: result.suburb2?.median_price ?? 0 },
      ]
    : [];

  return (
    <div className="max-w-5xl mx-auto space-y-5">
      <div className="bg-white border border-charcoal/10 shadow-sm">
        <div className="bg-charcoal px-5 py-2.5">
          <span className="font-mono text-xs uppercase tracking-widest text-sand">Suburb Comparison</span>
        </div>
        <div className="p-5">

          {/* Selector row */}
          <div className="flex gap-4 items-end mb-6">
            <div className="flex-1">
              <label className="block font-mono text-[10px] uppercase tracking-widest text-charcoal/40 mb-1">Suburb 1</label>
              <select className={sel} value={s1} onChange={e => setS1(e.target.value)}>
                {list.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="font-mono text-lg text-charcoal/25 pb-2 flex-shrink-0">VS</div>
            <div className="flex-1">
              <label className="block font-mono text-[10px] uppercase tracking-widest text-charcoal/40 mb-1">Suburb 2</label>
              <select className={sel} value={s2} onChange={e => setS2(e.target.value)}>
                {list.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <button
              onClick={compare} disabled={loading}
              className="bg-melb-blue text-white font-mono text-sm px-6 py-2 uppercase tracking-wider hover:bg-melb-blue-l transition-colors disabled:opacity-40 flex-shrink-0"
            >
              {loading ? "…" : "Compare"}
            </button>
          </div>

          {error && (
            <p className="p-3 bg-red-50 border-l-4 border-red-500 font-mono text-xs text-red-700 mb-4">{error}</p>
          )}

          {result && (
            <div className="space-y-5 fade-in-up">

              {/* Bar chart */}
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chart} margin={{ top: 5, right: 10, left: 30, bottom: 5 }}>
                    <XAxis dataKey="name" tick={{ fontFamily: "Space Mono", fontSize: 11 }} />
                    <YAxis tickFormatter={v => formatShort(v)} tick={{ fontFamily: "Space Mono", fontSize: 9 }} />
                    <Tooltip
                      formatter={(v: number) => [formatPrice(v), "Median Price"]}
                      contentStyle={{ fontFamily: "Space Mono", fontSize: 11, background: "#1a1a2e", color: "#f5f0e8", border: "none" }}
                      labelStyle={{ color: "#d4a017" }}
                    />
                    <Bar dataKey="price" radius={[2, 2, 0, 0]}>
                      <Cell fill="#0057b7" />
                      <Cell fill="#1a1a2e" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Side-by-side stats */}
              <div className="grid grid-cols-2 gap-4">
                {([["suburb1", s1], ["suburb2", s2]] as const).map(([key, label]) => {
                  const d = result[key];
                  return (
                    <div key={key} className="bg-sand-dark p-4">
                      <h3 className="font-serif font-bold text-base border-b border-charcoal/10 pb-2 mb-3">{label}</h3>
                      {d ? (
                        <div className="space-y-1.5 font-mono text-xs">
                          {[
                            ["Median Price",  formatPrice(d.median_price)],
                            ["Mean Price",    formatPrice(d.mean_price)],
                            ["# Properties", String(d.count)],
                            ["Avg Rooms",     String(d.avg_rooms)],
                            ["Avg Bld Area",  `${d.avg_building_area} m²`],
                            ["Avg Distance",  `${d.avg_distance} km`],
                          ].map(([lbl, val]) => (
                            <div key={lbl} className="flex justify-between">
                              <span className="text-charcoal/50">{lbl}</span>
                              <span className="font-bold">{val}</span>
                            </div>
                          ))}
                          {d.by_type && Object.entries(d.by_type).map(([t, info]: any) => (
                            <div key={t} className="flex justify-between text-[10px]">
                              <span className="text-charcoal/35">{TYPE_LABELS[t]}</span>
                              <span>{formatShort(info.median)} ({info.count})</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="font-mono text-xs text-charcoal/30">No data</p>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Winner line */}
              {result.suburb1 && result.suburb2 && (
                <div className="bg-charcoal text-sand py-3 px-4 font-mono text-sm text-center">
                  {(() => {
                    const diff = Math.abs(result.suburb1.median_price - result.suburb2.median_price);
                    const winner = result.suburb1.median_price > result.suburb2.median_price ? s1 : s2;
                    return <span><b className="text-melb-gold">{winner}</b> commands higher median prices by <b className="text-melb-gold">{formatPrice(diff)}</b></span>;
                  })()}
                </div>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
