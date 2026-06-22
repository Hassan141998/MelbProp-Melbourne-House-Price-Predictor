"use client";
import { useState } from "react";
import { PROP_TYPES, METHODS, SUBURB_COORDS } from "@/lib/api";

interface Props {
  suburbs: string[];
  onSubmit: (data: any) => void;
  isLoading: boolean;
}

const COUNCILS = [
  "Banyule","Bayside","Boroondara","Brimbank","Cardinia","Casey","Darebin",
  "Frankston","Glen Eira","Greater Dandenong","Hobsons Bay","Hume","Kingston",
  "Knox","Manningham","Maribyrnong","Maroondah","Melbourne","Melton","Monash",
  "Moonee Valley","Moreland","Mornington Peninsula","Nillumbik","Port Phillip",
  "Stonnington","Whitehorse","Whittlesea","Wyndham","Yarra","Yarra Ranges",
];

const DEFAULT_SUBURBS = Object.keys(SUBURB_COORDS);

export default function PredictionForm({ suburbs, onSubmit, isLoading }: Props) {
  const [f, setF] = useState({
    suburb:        "Richmond",
    rooms:         3,
    bathroom:      2,
    car:           1,
    type:          "h",
    method:        "S",
    distance:      5.0,
    landsize:      400.0,
    building_area: 150.0,
    year_built:    2000,
    council_area:  "Yarra",
    latitude:      -37.8274,
    longitude:     145.0016,
  });

  const set = (k: string, v: any) =>
    setF(prev => {
      const next = { ...prev, [k]: v };
      if (k === "suburb") {
        const coords = SUBURB_COORDS[v];
        if (coords) { next.latitude = coords[0]; next.longitude = coords[1]; }
      }
      return next;
    });

  const inp = "w-full border border-charcoal/20 bg-sand px-3 py-2 font-mono text-sm focus:border-melb-blue outline-none";
  const lbl = "block font-mono text-[10px] uppercase tracking-widest text-charcoal/50 mb-1";
  const suburbList = suburbs.length > 0 ? suburbs : DEFAULT_SUBURBS;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-x-4 gap-y-3">

        {/* Suburb */}
        <div className="col-span-2">
          <label className={lbl}>Suburb</label>
          <select className={inp} value={f.suburb} onChange={e => set("suburb", e.target.value)}>
            {suburbList.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        {/* Rooms slider */}
        <div>
          <label className={lbl}>Bedrooms — {f.rooms}</label>
          <input type="range" min={1} max={10} value={f.rooms}
            onChange={e => set("rooms", +e.target.value)}
            className="w-full mt-1" />
        </div>

        {/* Bathrooms slider */}
        <div>
          <label className={lbl}>Bathrooms — {f.bathroom}</label>
          <input type="range" min={1} max={6} value={f.bathroom}
            onChange={e => set("bathroom", +e.target.value)}
            className="w-full mt-1" />
        </div>

        {/* Car spaces */}
        <div>
          <label className={lbl}>Car Spaces — {f.car}</label>
          <input type="range" min={0} max={5} value={f.car}
            onChange={e => set("car", +e.target.value)}
            className="w-full mt-1" />
        </div>

        {/* Property type */}
        <div>
          <label className={lbl}>Property Type</label>
          <select className={inp} value={f.type} onChange={e => set("type", e.target.value)}>
            {Object.entries(PROP_TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </div>

        {/* Method */}
        <div>
          <label className={lbl}>Sale Method</label>
          <select className={inp} value={f.method} onChange={e => set("method", e.target.value)}>
            {Object.entries(METHODS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </div>

        {/* Distance from CBD */}
        <div>
          <label className={lbl}>Distance from CBD (km)</label>
          <input type="number" step="0.1" min={0} max={60}
            className={inp} value={f.distance}
            onChange={e => set("distance", parseFloat(e.target.value) || 0)} />
        </div>

        {/* Land size */}
        <div>
          <label className={lbl}>Land Size (m²)</label>
          <input type="number" min={0}
            className={inp} value={f.landsize}
            onChange={e => set("landsize", parseFloat(e.target.value) || 0)} />
        </div>

        {/* Building area */}
        <div>
          <label className={lbl}>Building Area (m²)</label>
          <input type="number" min={10}
            className={inp} value={f.building_area}
            onChange={e => set("building_area", parseFloat(e.target.value) || 50)} />
        </div>

        {/* Year built */}
        <div>
          <label className={lbl}>Year Built</label>
          <input type="number" min={1850} max={2024}
            className={inp} value={f.year_built}
            onChange={e => set("year_built", parseInt(e.target.value) || 2000)} />
        </div>

        {/* Council */}
        <div className="col-span-2">
          <label className={lbl}>Council Area</label>
          <select className={inp} value={f.council_area} onChange={e => set("council_area", e.target.value)}>
            {COUNCILS.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        {/* Lat / Lng */}
        <div>
          <label className={lbl}>Latitude</label>
          <input type="number" step="0.0001"
            className={inp} value={f.latitude}
            onChange={e => set("latitude", parseFloat(e.target.value) || -37.81)} />
        </div>
        <div>
          <label className={lbl}>Longitude</label>
          <input type="number" step="0.0001"
            className={inp} value={f.longitude}
            onChange={e => set("longitude", parseFloat(e.target.value) || 144.96)} />
        </div>
      </div>

      <button
        onClick={() => onSubmit(f)}
        disabled={isLoading}
        className={[
          "w-full py-3 font-mono text-sm uppercase tracking-widest font-bold transition-all",
          isLoading
            ? "bg-charcoal/30 text-sand/30 cursor-not-allowed"
            : "bg-melb-blue text-white hover:bg-melb-blue-l active:scale-[0.99]",
        ].join(" ")}
      >
        {isLoading ? "Analysing…" : "Predict Price →"}
      </button>
    </div>
  );
}
