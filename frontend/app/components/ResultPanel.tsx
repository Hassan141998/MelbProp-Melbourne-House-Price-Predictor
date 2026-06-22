"use client";
import { fmt, fmts } from "@/lib/api";

const MODEL_META: Record<string,{label:string;color:string}> = {
  random_forest:{label:"Random Forest",color:"#0057b7"},
  xgboost:{label:"XGBoost",color:"#1a1a2e"},
  linear_regression:{label:"Linear Regression",color:"#d4a017"},
};

export default function ResultPanel({prediction}:{prediction:any}) {
  const {predicted_price,price_range,price_per_sqm,model_comparison,confidence,suburb}=prediction;

  const exportPDF=async()=>{
    const {jsPDF}=await import("jspdf");
    const doc=new jsPDF();
    doc.setFillColor(26,26,46); doc.rect(0,0,210,30,"F");
    doc.setTextColor(245,240,232); doc.setFontSize(18); doc.setFont("helvetica","bold");
    doc.text("MelbProp — Property Valuation",14,20);
    doc.setFillColor(0,87,183); doc.rect(0,30,210,3,"F");
    doc.setTextColor(26,26,46); doc.setFontSize(11); doc.setFont("helvetica","normal");
    let y=42;
    const row=(l:string,v:string)=>{ doc.setFont("helvetica","bold");doc.text(l,14,y);doc.setFont("helvetica","normal");doc.text(v,75,y);y+=8; };
    row("Suburb:",suburb); row("Predicted:",fmt(predicted_price));
    row("Low:",fmt(price_range.low)); row("High:",fmt(price_range.high));
    row("Per m²:",fmt(price_per_sqm)); row("Confidence:",confidence.toUpperCase());
    y+=5; doc.setFontSize(13); doc.setFont("helvetica","bold"); doc.text("Model Comparison",14,y); y+=8;
    Object.entries(model_comparison).forEach(([k,v])=>row((MODEL_META[k]?.label||k)+":",fmt(v as number)));
    doc.setFontSize(8); doc.setTextColor(150,150,150); doc.text(`MelbProp · ${new Date().toLocaleDateString("en-AU")}`,14,285);
    doc.save(`MelbProp-${suburb}-${Date.now()}.pdf`);
  };

  const maxP=Math.max(...Object.values(model_comparison).map(Number));
  return (
    <div className="space-y-4">
      <div className="bg-charcoal text-sand p-6 relative overflow-hidden">
        <div className="absolute inset-0 opacity-[0.04]" style={{backgroundImage:"repeating-linear-gradient(45deg,#0057b7 0,#0057b7 1px,transparent 0,transparent 12px)",backgroundSize:"17px 17px"}}/>
        <div className="relative z-10">
          <div className="flex flex-wrap items-start justify-between gap-3 mb-5">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-widest text-sand/40 mb-1">Estimated Value — {suburb}</p>
              <p className="font-serif text-4xl font-bold">{fmt(predicted_price)}</p>
            </div>
            <div className="flex flex-col items-end gap-2">
              <span className={`font-mono text-[10px] px-2 py-1 rounded-full ${confidence==="high"?"bg-green-600":"bg-yellow-600"}`}>{confidence==="high"?"HIGH CONFIDENCE":"MEDIUM CONFIDENCE"}</span>
              <button onClick={exportPDF} className="font-mono text-xs bg-melb-blue hover:bg-melb-blue-l px-3 py-1.5 transition-colors">Export PDF ↓</button>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 border-t border-white/10 pt-4">
            <div><p className="font-mono text-[10px] text-sand/40 mb-1">LOW</p><p className="font-mono text-xl font-bold text-melb-gold">{fmts(price_range.low)}</p></div>
            <div className="text-center"><p className="font-mono text-[10px] text-sand/40 mb-1">PER M²</p><p className="font-mono text-xl font-bold">{fmts(price_per_sqm)}</p></div>
            <div className="text-right"><p className="font-mono text-[10px] text-sand/40 mb-1">HIGH</p><p className="font-mono text-xl font-bold text-melb-gold">{fmts(price_range.high)}</p></div>
          </div>
        </div>
      </div>
      <div className="bg-white border border-charcoal/10 p-4">
        <p className="font-mono text-[10px] uppercase tracking-widest text-charcoal/40 mb-3">Model Predictions</p>
        <div className="space-y-3">
          {Object.entries(model_comparison).map(([key,val])=>{
            const v=val as number; const m=MODEL_META[key]||{label:key,color:"#999"};
            return (
              <div key={key}>
                <div className="flex justify-between mb-1"><span className="font-mono text-xs text-charcoal/60">{m.label}</span><span className="font-mono text-xs font-bold">{fmts(v)}</span></div>
                <div className="h-2 bg-sand-dark rounded overflow-hidden"><div className="h-full rounded transition-all duration-700" style={{width:`${Math.round((v/maxP)*100)}%`,background:m.color}}/></div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
