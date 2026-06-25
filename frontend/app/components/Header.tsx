"use client";
import { useEffect, useState } from "react";
import { API } from "@/lib/api";
export default function Header() {
  const [alive,setAlive]=useState<boolean|null>(null);
  useEffect(()=>{API.health().then(()=>setAlive(true)).catch(()=>setAlive(false));},[]);
  return (
    <header className="bg-charcoal border-b-4 border-melb-blue text-sand">
      <div className="max-w-screen-2xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-melb-blue flex items-center justify-center text-white font-mono font-bold text-lg">M</div>
          <div>
            <h1 className="font-serif font-bold text-xl leading-tight">MelbProp</h1>
            <p className="font-mono text-[10px] text-sand/40 uppercase tracking-widest">Melbourne House Price Predictor</p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-5 font-mono text-xs text-sand/50">
          <span className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${alive===null?"bg-yellow-400 animate-pulse":alive?"bg-green-400":"bg-red-400"}`}/>
            {alive===null?"Connecting…":alive?"Backend Online":"Backend Offline"}
          </span>
          <span className="text-sand/20">|</span>
          <span>RF · XGB · LR</span>
          <span className="text-sand/20">|</span>
          <a href="https://www.kaggle.com/datasets/dansbecker/melbourne-housing-snapshot" target="_blank" rel="noopener noreferrer" className="text-melb-blue hover:text-blue-300 underline">Dataset ↗</a>
        </div>
      </div>
    </header>
  );
}
