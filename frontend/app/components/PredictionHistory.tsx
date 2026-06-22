"use client";
import { useEffect, useState } from "react";
import { API, fmts, PROP_TYPES } from "@/lib/api";

export default function PredictionHistory() {
  const [rows,setRows]=useState<any[]>([]);
  const [loading,setLoading]=useState(true);
  const load=()=>{ setLoading(true); API.getHistory(20).then(setRows).catch(()=>setRows([])).finally(()=>setLoading(false)); };
  useEffect(load,[]);
  return (
    <div className="max-w-5xl mx-auto">
      <div className="bg-white border border-charcoal/10 shadow-sm">
        <div className="bg-charcoal px-5 py-2.5 flex items-center justify-between">
          <span className="font-mono text-xs uppercase tracking-widest text-sand">Prediction History (Neon DB)</span>
          <button onClick={load} className="font-mono text-xs text-sand/40 hover:text-sand transition-colors">Refresh ↺</button>
        </div>
        <div className="p-5">
          {loading?(<div className="h-32 flex items-center justify-center font-mono text-xs text-charcoal/30">Loading…</div>)
          :rows.length===0?(
            <div className="py-10 text-center font-mono text-xs text-charcoal/30 space-y-1">
              <p>No predictions saved yet.</p>
              <p>Add DATABASE_URL to .env to enable Neon DB storage.</p>
            </div>
          ):(
            <div className="overflow-x-auto">
              <table className="w-full font-mono text-xs">
                <thead><tr className="border-b-2 border-charcoal/10">{["#","Suburb","Type","Rooms","Distance","Predicted","Date"].map(h=><th key={h} className="text-left py-2 pr-4 text-charcoal/35 uppercase tracking-wider">{h}</th>)}</tr></thead>
                <tbody>
                  {rows.map((r,i)=>(
                    <tr key={r.id??i} className="border-b border-charcoal/5 hover:bg-sand-dark transition-colors">
                      <td className="py-2 pr-4 text-charcoal/25">{i+1}</td>
                      <td className="py-2 pr-4 font-bold">{r.suburb}</td>
                      <td className="py-2 pr-4 text-charcoal/50">{PROP_TYPES[r.type]??r.type}</td>
                      <td className="py-2 pr-4">{r.rooms}</td>
                      <td className="py-2 pr-4">{r.distance?.toFixed(1)} km</td>
                      <td className="py-2 pr-4 font-bold text-melb-blue">{fmts(r.predicted_price)}</td>
                      <td className="py-2 pr-4 text-charcoal/35">{r.created_at?new Date(r.created_at).toLocaleDateString("en-AU"):"—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
