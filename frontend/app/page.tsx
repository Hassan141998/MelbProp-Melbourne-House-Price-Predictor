"use client";
import { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import { API } from "@/lib/api";
import Header            from "@/components/Header";
import PredictionForm    from "@/components/PredictionForm";
import ResultPanel       from "@/components/ResultPanel";
import SimilarProperties from "@/components/SimilarProperties";
import SuburbCompare     from "@/components/SuburbCompare";
import PriceTrends       from "@/components/PriceTrends";
import ModelAccuracy     from "@/components/ModelAccuracy";
import PredictionHistory from "@/components/PredictionHistory";

const MapView = dynamic(() => import("@/components/MapView"), { ssr: false });

type Tab = "predict"|"compare"|"trends"|"history";
const TABS: {id:Tab;label:string}[] = [
  {id:"predict",label:"🏠 Predict"},{id:"compare",label:"⚖️ Compare"},
  {id:"trends",label:"📈 Trends"},{id:"history",label:"🕒 History"},
];

export default function Home() {
  const [tab,setPredTab]  = useState<Tab>("predict");
  const [prediction,setPrediction] = useState<any>(null);
  const [loading,setLoading]       = useState(false);
  const [error,setError]           = useState<string|null>(null);
  const [suburbs,setSuburbs]       = useState<string[]>([]);
  const [modelStats,setModelStats] = useState<any>(null);

  useEffect(()=>{ API.getSuburbs().then(setSuburbs).catch(()=>{}); API.getModelAccuracy().then(setModelStats).catch(()=>{}); },[]);

  const handlePredict = useCallback(async(f:any)=>{
    setLoading(true); setError(null);
    try { setPrediction(await API.predictPrice(f)); }
    catch(e:any) { setError(e.message||"Prediction failed — is the backend running?"); }
    finally { setLoading(false); }
  },[]);

  return (
    <div className="min-h-screen flex flex-col bg-sand">
      <Header />
      <nav className="bg-charcoal border-b border-white/5">
        <div className="max-w-screen-2xl mx-auto flex px-4">
          {TABS.map(({id,label})=>(
            <button key={id} onClick={()=>setPredTab(id)}
              className={`font-mono text-xs uppercase tracking-widest px-5 py-3 transition-colors ${tab===id?"bg-melb-blue text-white":"text-sand/50 hover:text-sand"}`}>
              {label}
            </button>
          ))}
        </div>
      </nav>

      <main className="flex-1 max-w-screen-2xl mx-auto w-full">
        {tab==="predict" && (
          <div className="flex flex-col xl:flex-row" style={{minHeight:"calc(100vh - 112px)"}}>
            <div className="xl:w-[40%] h-[45vh] xl:h-auto xl:sticky xl:top-0 border-r-2 border-charcoal/10 overflow-hidden">
              <MapView prediction={prediction} similarProperties={prediction?.similar_properties||[]} />
            </div>
            <div className="xl:w-[60%] overflow-y-auto p-5 space-y-5">
              <div className="bg-white border border-charcoal/10 shadow-sm">
                <div className="bg-charcoal px-5 py-2.5 flex justify-between items-center">
                  <span className="font-mono text-xs uppercase tracking-widest text-sand">Property Details</span>
                  <span className="font-mono text-xs text-sand/40">RF + XGB + LR ensemble</span>
                </div>
                <div className="p-5">
                  <PredictionForm suburbs={suburbs} onSubmit={handlePredict} isLoading={loading} />
                  {error && <p className="mt-4 p-3 bg-red-50 border-l-4 border-red-500 font-mono text-xs text-red-700">{error}</p>}
                </div>
              </div>
              {prediction && <div className="fade-in-up"><ResultPanel prediction={prediction} /></div>}
              {modelStats && Object.keys(modelStats).length>0 && (
                <div className="bg-white border border-charcoal/10 shadow-sm">
                  <div className="bg-charcoal px-5 py-2.5"><span className="font-mono text-xs uppercase tracking-widest text-sand">Model Accuracy (test set)</span></div>
                  <div className="p-5"><ModelAccuracy stats={modelStats} /></div>
                </div>
              )}
              {prediction?.similar_properties?.length>0 && (
                <div className="fade-in-up bg-white border border-charcoal/10 shadow-sm">
                  <div className="bg-charcoal px-5 py-2.5"><span className="font-mono text-xs uppercase tracking-widest text-sand">5 Similar Properties (KNN)</span></div>
                  <div className="p-5"><SimilarProperties properties={prediction.similar_properties} /></div>
                </div>
              )}
            </div>
          </div>
        )}
        {tab==="compare" && <div className="p-5"><SuburbCompare suburbs={suburbs} /></div>}
        {tab==="trends"  && <div className="p-5"><PriceTrends /></div>}
        {tab==="history" && <div className="p-5"><PredictionHistory /></div>}
      </main>
    </div>
  );
}
