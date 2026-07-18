
const ORCID="0000-0001-6526-7740";
const ORCID_API="https://pub.orcid.org/v3.0";
const CROSSREF="https://api.crossref.org/works/";
const fallbackSummary=(title)=>`Publicación académica vinculada con ${title.toLowerCase()}. Consulte el artículo completo para conocer el problema abordado, el enfoque metodológico y sus principales resultados.`;

const cleanHTML=(s="")=>{
 const d=document.createElement("div"); d.innerHTML=s;
 return (d.textContent||d.innerText||"").replace(/\s+/g," ").trim();
};
const clip=(s,n=530)=>s.length>n?s.slice(0,n).replace(/\s+\S*$/,"")+"…":s;
const doiFrom=(ids=[])=>{
 const x=ids.find(i=>(i["external-id-type"]||"").toLowerCase()==="doi");
 return x?.["external-id-value"]?.replace(/^https?:\/\/(dx\.)?doi\.org\//i,"")||"";
};
async function crossrefAbstract(doi){
 if(!doi)return "";
 try{
  const r=await fetch(CROSSREF+encodeURIComponent(doi));
  if(!r.ok)return "";
  const m=(await r.json()).message||{};
  return cleanHTML(m.abstract||m.subtitle?.[0]||"");
 }catch{return ""}
}
async function workDetail(putCode){
 try{
  const r=await fetch(`${ORCID_API}/${ORCID}/work/${putCode}`,{headers:{Accept:"application/json"}});
  return r.ok?await r.json():{};
 }catch{return {}}
}
async function loadLocal(){
 try{
  const r=await fetch("data/publications.json",{cache:"no-store"});
  if(r.ok){const x=await r.json();if(Array.isArray(x)&&x.length)return x}
 }catch{}
 return [];
}
async function loadOrcid(){
 const r=await fetch(`${ORCID_API}/${ORCID}/works`,{headers:{Accept:"application/json"}});
 if(!r.ok)throw Error("ORCID");
 const data=await r.json();
 const basic=(data.group||[]).map(g=>{
  const s=g["work-summary"]?.[0]||{};
  return {
   putCode:s["put-code"], title:s.title?.title?.value||"Publicación sin título",
   year:s["publication-date"]?.year?.value||"—",
   type:(s.type||"journal-article").replaceAll("_"," ").toLowerCase(),
   journal:s["journal-title"]?.value||"",
   doi:doiFrom(s["external-ids"]?.["external-id"]||[]),
   url:s.url?.value||""
  }
 }).sort((a,b)=>String(b.year).localeCompare(String(a.year)));
 const enriched=[];
 for(const w of basic){
  const detail=await workDetail(w.putCode);
  const desc=cleanHTML(detail["short-description"]||"");
  const ids=detail["external-ids"]?.["external-id"]||[];
  const doi=w.doi||doiFrom(ids);
  let abstract=desc;
  if(!abstract&&doi)abstract=await crossrefAbstract(doi);
  const source=doi?`https://doi.org/${doi}`:(detail.url?.value||w.url||`https://orcid.org/${ORCID}`);
  enriched.push({...w,doi,url:source,summary:clip(abstract||fallbackSummary(w.title))});
 }
 return enriched;
}
function card(w){
 const url=w.url||w.doi&&`https://doi.org/${w.doi}`||`https://orcid.org/${ORCID}`;
 return `<article class="pub">
  <div class="pub-top"><span>${w.year}</span><span>${w.type||"Publicación"}</span></div>
  <h3><a href="${url}" target="_blank" rel="noopener">${w.title}</a></h3>
  <p class="pub-summary">${w.summary||fallbackSummary(w.title)}</p>
  <div class="pub-journal">${w.journal||"Registro académico en ORCID"}</div>
  <div class="pub-footer"><span class="badge">${w.doi?"DOI":"ORCID"}</span>
  <a class="pub-link" href="${url}" target="_blank" rel="noopener">Ver artículo ↗</a></div>
 </article>`;
}
let works=[];
function render(list){
 const el=document.querySelector("[data-publications]");
 if(!el)return;
 el.innerHTML=list.length?list.map(card).join(""):`<div class="empty">No se encontraron publicaciones con estos criterios.</div>`;
}
function filters(){
 const q=document.querySelector("#pub-search"), y=document.querySelector("#year-filter");
 if(!q||!y)return;
 [...new Set(works.map(x=>x.year))].forEach(v=>y.insertAdjacentHTML("beforeend",`<option value="${v}">${v}</option>`));
 const run=()=>{const s=q.value.toLowerCase(),yr=y.value;render(works.filter(w=>(!yr||w.year==yr)&&(!s||`${w.title} ${w.summary} ${w.journal}`.toLowerCase().includes(s))))};
 q.addEventListener("input",run);y.addEventListener("change",run);
}
async function initPublications(){
 const el=document.querySelector("[data-publications]");if(!el)return;
 try{
  works=await loadLocal(); if(!works.length)works=await loadOrcid();
  const home=document.body.dataset.page==="home";
  render(home?works.slice(0,6):works); if(!home)filters();
 }catch{
  el.innerHTML=`<div class="empty">La fuente ORCID no respondió temporalmente. Puede consultar el perfil institucional directamente en <a href="https://orcid.org/${ORCID}" target="_blank"><strong>ORCID</strong></a>.</div>`;
 }
}
document.addEventListener("DOMContentLoaded",()=>{
 document.querySelector(".menu")?.addEventListener("click",()=>document.querySelector(".links")?.classList.toggle("open"));
 document.querySelectorAll("[data-year]").forEach(x=>x.textContent=new Date().getFullYear());
 initPublications();
});
