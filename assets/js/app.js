
const CONFIG = {
  orcid: "0000-0001-6526-7740",
  api: "https://pub.orcid.org/v3.0",
  perPage: 9
};

function menu(){
  const b=document.querySelector(".menu-btn"), n=document.querySelector(".nav-links");
  if(b&&n)b.addEventListener("click",()=>n.classList.toggle("open"));
}
function year(){document.querySelectorAll("[data-year]").forEach(e=>e.textContent=new Date().getFullYear())}
function clean(v){return (v||"").replace(/<[^>]*>/g,"").trim()}
function doiUrl(extIds=[]){
  const doi=extIds.find(x=>(x["external-id-type"]||"").toLowerCase()==="doi");
  return doi ? `https://doi.org/${doi["external-id-value"]}` : "";
}
async function loadWorks(limit){
  const target=document.querySelector("[data-publications]");
  if(!target)return;
  try{
    const r=await fetch(`${CONFIG.api}/${CONFIG.orcid}/works`,{headers:{Accept:"application/json"}});
    if(!r.ok)throw new Error("ORCID unavailable");
    const data=await r.json();
    let works=(data.group||[]).map(g=>{
      const s=g["work-summary"]?.[0]||{};
      return {
        title:clean(s.title?.title?.value)||"Untitled work",
        year:s["publication-date"]?.year?.value||"—",
        type:(s.type||"research-output").replaceAll("_"," ").toLowerCase(),
        journal:clean(s["journal-title"]?.value),
        url:doiUrl(s["external-ids"]?.["external-id"]||[]) || s.url?.value || ""
      };
    }).sort((a,b)=>String(b.year).localeCompare(String(a.year)));
    window.__works=works;
    renderWorks(limit?works.slice(0,limit):works);
    buildYearFilter(works);
  }catch(e){
    target.innerHTML=`<div class="empty">No fue posible consultar ORCID en este momento. Visita el perfil ORCID desde el enlace institucional.</div>`;
  }
}
function renderWorks(works){
 const target=document.querySelector("[data-publications]");
 if(!target)return;
 target.innerHTML=works.map(w=>`<article class="card">
   <div class="meta">${w.year} · ${w.type}</div>
   <h3>${w.url?`<a href="${w.url}" target="_blank" rel="noopener">${w.title}</a>`:w.title}</h3>
   <p class="meta">${w.journal||"Academic publication"}</p>
   <div class="tags"><span class="tag">Research</span>${w.url?'<span class="tag">DOI / Link</span>':''}</div>
 </article>`).join("") || '<div class="empty">No hay publicaciones para mostrar.</div>';
}
function buildYearFilter(works){
 const sel=document.querySelector("#year-filter");
 if(!sel)return;
 [...new Set(works.map(w=>w.year))].forEach(y=>sel.insertAdjacentHTML("beforeend",`<option>${y}</option>`));
 const run=()=>{
   const q=(document.querySelector("#pub-search")?.value||"").toLowerCase();
   const y=sel.value;
   renderWorks(works.filter(w=>(!q||`${w.title} ${w.journal} ${w.type}`.toLowerCase().includes(q))&&(!y||w.year===y)));
 };
 document.querySelector("#pub-search")?.addEventListener("input",run);
 sel.addEventListener("change",run);
}
document.addEventListener("DOMContentLoaded",()=>{menu();year();loadWorks(document.body.dataset.page==="home"?6:null)});
