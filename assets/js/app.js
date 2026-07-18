
const LANG=document.documentElement.lang.startsWith("en")?"en":"es";
const PREFIX=document.body.dataset.prefix||"";
const PAGE_SIZE=8;
let allPublications=[], shown=PAGE_SIZE;

async function loadJSON(path){
 const r=await fetch(PREFIX+path,{cache:"no-store"});
 if(!r.ok) throw new Error(path);
 return r.json();
}
function pubRow(p){
 const url=p.url||(p.doi?`https://doi.org/${p.doi}`:"#");
 const journal=p.journal||"Academic publication";
 const doiLabel=p.doi?`DOI ↗`:(LANG==="en"?"Open ↗":"Abrir ↗");
 return `<article class="pub-row" data-year="${p.year||""}">
 <div><h3><a href="${url}" target="_blank" rel="noopener">${p.title}</a></h3>
 <div class="pub-meta"><span class="year">${p.year||"—"}</span><span class="journal">${journal}</span><a class="doi" href="${url}" target="_blank" rel="noopener">${doiLabel}</a></div></div>
 <a class="open-arrow" href="${url}" target="_blank" rel="noopener" aria-label="Open">↗</a></article>`;
}
function filtered(){
 const q=(document.querySelector("#pub-search")?.value||"").toLowerCase();
 const y=document.querySelector("#year-filter")?.value||"";
 return allPublications.filter(p=>(!q||`${p.title} ${p.journal}`.toLowerCase().includes(q))&&(!y||p.year===y));
}
function render(){
 const list=document.querySelector("#publication-list"); if(!list)return;
 const result=filtered();
 list.innerHTML=result.slice(0,shown).map(pubRow).join("");
 const more=document.querySelector("#show-more");
 if(more)more.hidden=shown>=result.length;
 document.querySelector("#pub-count").textContent=result.length;
}
async function initPublications(){
 try{
  allPublications=await loadJSON("data/publications.json");
  allPublications.sort((a,b)=>String(b.year).localeCompare(String(a.year))||a.title.localeCompare(b.title));
  const sel=document.querySelector("#year-filter");
  if(sel)[...new Set(allPublications.map(p=>p.year).filter(Boolean))].forEach(y=>sel.insertAdjacentHTML("beforeend",`<option>${y}</option>`));
  render();
  document.querySelector("#pub-search")?.addEventListener("input",()=>{shown=PAGE_SIZE;render()});
  sel?.addEventListener("change",()=>{shown=PAGE_SIZE;render()});
  document.querySelector("#show-more")?.addEventListener("click",()=>{shown+=PAGE_SIZE;render()});
 }catch(e){
  document.querySelector("#publication-list").innerHTML=`<div class="pub-row">${LANG==="en"?"The local publication catalogue could not be loaded.":"No se pudo cargar el catálogo local de publicaciones."}</div>`;
 }
}
async function initProfile(){
 try{
  const p=await loadJSON("data/profile.json");
  const exp=document.querySelector("#experience-list");
  if(exp)exp.innerHTML=p.experience.map(x=>`<article class="timeline-row"><div class="timeline-date">${x[`date_${LANG}`]}</div><div class="timeline-content"><h3>${x[`title_${LANG}`]}</h3><p>${x.org}</p><span class="pill">${x[`area_${LANG}`]}</span></div></article>`).join("");
  const edu=document.querySelector("#education-list");
  if(edu)edu.innerHTML=p.education.map(x=>`<article class="edu-card"><div class="edu-year">${x.year}</div><div><h3>${x[`degree_${LANG}`]}</h3><p>${x[`org_${LANG}`]}</p><p class="honor">${x[`honor_${LANG}`]}</p></div></article>`).join("");
  const aw=document.querySelector("#awards-list");
  if(aw)aw.innerHTML=p.awards.map((x,i)=>`<article class="award"><div class="award-number">0${i+1}</div><h3>${x[`title_${LANG}`]}</h3><p>${x[`detail_${LANG}`]}</p></article>`).join("");
  const af=document.querySelector("#affiliations-list");
  if(af)af.innerHTML=p.affiliations.map(x=>`<article class="aff"><div class="aff-top"><span class="aff-date">${x[`date_${LANG}`]}</span>${x.current?`<span class="current">${LANG==="en"?"Current":"Actual"}</span>`:""}</div><h3>${x.institution}</h3><p>${x.location}</p><p>${x[`role_${LANG}`]}</p></article>`).join("");
 }catch(e){}
}
async function initMetrics(){
 try{
  const m=await loadJSON("data/metrics.json");
  ["scopus","wos","scholar"].forEach(k=>{
   document.querySelector(`#${k}-works`).textContent=m[k].works;
   document.querySelector(`#${k}-citations`).textContent=m[k].citations;
   document.querySelector(`#${k}-hindex`).textContent=m[k].hindex;
   document.querySelector(`#${k}-link`).href=m[k].url;
  });
  document.querySelector("#orcid-works").textContent=m.orcid.works;
  document.querySelector("#orcid-link").href=m.orcid.url;
 }catch(e){}
}
document.addEventListener("DOMContentLoaded",()=>{
 document.querySelector(".menu")?.addEventListener("click",()=>document.querySelector(".navlinks")?.classList.toggle("open"));
 document.querySelectorAll("[data-year-now]").forEach(x=>x.textContent=new Date().getFullYear());
 initPublications();initProfile();initMetrics();
});
