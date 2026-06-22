"use client";
import { useEffect, useRef } from "react";
import { fmts, PROP_TYPES } from "@/lib/api";

interface Props { prediction:any; similarProperties:any[]; }

export default function MapView({prediction,similarProperties}:Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef       = useRef<any>(null);
  const markersRef   = useRef<any[]>([]);

  useEffect(()=>{
    if(typeof window==="undefined"||mapRef.current)return;
    (async()=>{
      const L=(await import("leaflet")).default;
      const map=L.map(containerRef.current!,{center:[-37.8136,144.9631],zoom:12});
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:"© OpenStreetMap",maxZoom:19}).addTo(map);
      L.circle([-37.8136,144.9631],{radius:600,color:"#0057b7",fillColor:"#0057b7",fillOpacity:0.15,weight:2}).addTo(map).bindPopup("<b>Melbourne CBD</b>");
      mapRef.current=map;
    })();
    return()=>{ if(mapRef.current){mapRef.current.remove();mapRef.current=null;} };
  },[]);

  useEffect(()=>{
    if(!mapRef.current||typeof window==="undefined")return;
    (async()=>{
      const L=(await import("leaflet")).default;
      markersRef.current.forEach(m=>mapRef.current.removeLayer(m));
      markersRef.current=[];
      similarProperties.forEach(p=>{
        if(!p.latitude||!p.longitude)return;
        const icon=L.divIcon({className:"",html:`<div style="background:#0057b7;color:#fff;font-family:'Space Mono',monospace;font-size:10px;padding:2px 6px;border-radius:2px;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,.35)">${fmts(p.price)}</div>`,iconAnchor:[24,14]});
        markersRef.current.push(L.marker([p.latitude,p.longitude],{icon}).addTo(mapRef.current).bindPopup(`<b>${p.suburb}</b><br>${p.rooms} bed · ${PROP_TYPES[p.type]||p.type}<br>${fmts(p.price)}`));
      });
      if(prediction?.latitude&&prediction?.longitude){
        const icon=L.divIcon({className:"",html:`<div style="background:#1a1a2e;color:#d4a017;font-family:'Space Mono',monospace;font-size:13px;font-weight:bold;padding:5px 10px;border-radius:3px;white-space:nowrap;box-shadow:0 3px 10px rgba(0,0,0,.5);border:2px solid #0057b7">${fmts(prediction.predicted_price)}</div>`,iconAnchor:[50,32]});
        markersRef.current.push(L.marker([prediction.latitude,prediction.longitude],{icon}).addTo(mapRef.current).bindPopup(`<b style="color:#d4a017">🏠 ${prediction.suburb}</b><br>Predicted: ${fmts(prediction.predicted_price)}`).openPopup());
        mapRef.current.flyTo([prediction.latitude,prediction.longitude],14,{duration:1.2});
      }
    })();
  },[prediction,similarProperties]);

  return (
    <div className="relative w-full h-full min-h-[380px]">
      <div ref={containerRef} className="absolute inset-0"/>
      <div className="absolute bottom-3 left-3 z-[999] bg-charcoal/90 text-sand p-2.5 font-mono text-xs space-y-1.5 pointer-events-none">
        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-sm bg-melb-gold border-2 border-melb-blue"/><span>Your property</span></div>
        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-sm bg-melb-blue"/><span>Similar (KNN)</span></div>
        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-melb-blue opacity-30"/><span>CBD</span></div>
      </div>
    </div>
  );
}
