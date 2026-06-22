"use client";
import { useState } from "react";
import { fmts, PROP_TYPES } from "@/lib/api";

const FALLBACK:Record<string,string>={
  h:"https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&q=80",
  u:"https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&q=80",
  t:"https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&q=80",
};

export default function SimilarProperties({properties}:{properties:any[]}) {
  const [err,setErr]=useState<Record<number,boolean>>({});
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {properties.map((p,i)=>(
        <div key={i} className="prop-card border border-charcoal/10 bg-white overflow-hidden">
          <div className="relative h-40 bg-sand-dark overflow-hidden">
            <img src={err[i]?(FALLBACK[p.type]??FALLBACK.h):p.image} alt={p.suburb}
              className="w-full h-full object-cover" onError={()=>setErr(e=>({...e,[i]:true}))}/>
            <div className="absolute top-2 left-2"><span className="bg-charcoal text-sand font-mono text-[10px] px-2 py-0.5">{PROP_TYPES[p.type]||p.type}</span></div>
            <div className="absolute top-2 right-2"><span className="bg-melb-blue text-white font-mono text-[10px] px-2 py-0.5">{Math.round(p.similarity_score*100)}% match</span></div>
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent px-3 py-2">
              <span className="font-mono text-sm font-bold text-white">{fmts(p.price)}</span>
            </div>
          </div>
          <div className="p-3 space-y-1.5">
            <div className="flex items-center justify-between">
              <p className="font-serif font-bold text-sm">{p.suburb}</p>
              <p className="font-mono text-xs text-charcoal/40">{p.distance.toFixed(1)} km</p>
            </div>
            <div className="grid grid-cols-2 gap-x-3 font-mono text-[11px] text-charcoal/50">
              <span>🛏 {p.rooms} bed</span><span>🏗 {p.building_area.toFixed(0)} m²</span>
              <span>🌿 {p.landsize.toFixed(0)} m²</span>{p.year_built?<span>📅 {p.year_built}</span>:null}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
