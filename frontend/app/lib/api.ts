const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
async function req<T=any>(path:string,init?:RequestInit):Promise<T>{
  const res=await fetch(`${BASE}${path}`,{headers:{"Content-Type":"application/json"},...init});
  if(!res.ok){const e=await res.json().catch(()=>({}));throw new Error((e as any).detail||`HTTP ${res.status}`);}
  return res.json();
}
export const API={
  predictPrice:(b:any)=>req("/api/predict-price",{method:"POST",body:JSON.stringify(b)}),
  getSuburbStats:(s:string)=>req(`/api/suburb-stats/${encodeURIComponent(s)}`),
  compareSuburbs:(s1:string,s2:string)=>req("/api/compare-suburbs",{method:"POST",body:JSON.stringify({suburb1:s1,suburb2:s2})}),
  getSuburbs:()=>req<{suburbs:string[]}>("/api/suburbs").then(r=>r.suburbs),
  getHistory:(limit=20)=>req<{history:any[]}>(`/api/history?limit=${limit}`).then(r=>r.history),
  getPriceTrends:()=>req("/api/price-trends"),
  getModelAccuracy:()=>req("/api/model-accuracy"),
  health:()=>req("/api/health"),
};
export const fmt=(n:number)=>new Intl.NumberFormat("en-AU",{style:"currency",currency:"AUD",maximumFractionDigits:0}).format(n);
export const fmts=(n:number)=>n>=1000000?`$${(n/1000000).toFixed(2)}M`:n>=1000?`$${(n/1000).toFixed(0)}K`:`$${n}`;
export const PROP_TYPES:Record<string,string>={h:"House",u:"Unit / Apartment",t:"Townhouse"};
export const METHODS:Record<string,string>={S:"Private Sale",PI:"Passed In",VB:"Vendor Bid",SA:"Sold After Auction",SP:"Sold Prior"};
export const SUBURB_COORDS:Record<string,[number,number]>={
  "Richmond":[-37.8274,145.0016],"Fitzroy":[-37.7994,144.9775],"Collingwood":[-37.8041,144.9876],
  "Hawthorn":[-37.8225,145.0264],"St Kilda":[-37.8618,144.9793],"Carlton":[-37.7997,144.9662],
  "South Yarra":[-37.8395,144.9905],"Prahran":[-37.8494,144.9935],"Toorak":[-37.8461,145.0153],
  "Malvern":[-37.8575,145.0302],"Brunswick":[-37.7659,144.9606],"Footscray":[-37.8016,144.8987],
  "Essendon":[-37.7487,144.9180],"Moonee Ponds":[-37.7652,144.9208],"Glen Waverley":[-37.8783,145.1633],
  "Box Hill":[-37.8198,145.1217],"Docklands":[-37.8140,144.9458],"Southbank":[-37.8254,144.9631],
};
