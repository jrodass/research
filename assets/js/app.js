
const LANG=document.documentElement.lang.startsWith("en")?"en":"es";
const PREFIX=document.body.dataset.prefix||"";
let publications=[];
async function getJSON(path){
 const r=await fetch(PREFIX+path,{cache:"no-store"});
 if(!r.ok)throw new Error(path);
 return r.json();
}
function icon(name){return `<img src="${PREFIX}assets/icons/${name}.svg" alt="" aria-hidden="true">`}
function pubLink(p){return p.url||(p.doi?`https://doi.org/${p.doi}`:"#")}
function recentCard(p){
 return `<article class="recent-card"><div class="recent-top"><span>${p.year||"—"}</span><span>${p.type||"publication"}</span></div>
 <h3><a href="${pubLink(p)}" target="_blank" rel="noopener">${p.title}</a></h3>
 <p>${p.journal||"Academic publication"}</p>
 <div class="recent-footer"><span class="source">${p.doi?`DOI ${p.doi}`:"ORCID record"}</span>
 <a class="article-link" href="${pubLink(p)}" target="_blank" rel="noopener">${LANG==="en"?"Open article":"Ver artículo"} ${icon("external")}</a></div></article>`;
}
function pubRow(p){
 return `<article class="pub-row" data-year="${p.year||""}"><div><h3><a href="${pubLink(p)}" target="_blank" rel="noopener">${p.title}</a></h3>
 <div class="pub-meta"><span class="pub-year">${p.year||"—"}</span><span>${p.journal||"Academic publication"}</span>${p.doi?`<span>DOI ${p.doi}</span>`:""}</div></div>
 <a class="pub-open" href="${pubLink(p)}" target="_blank" rel="noopener">${icon("external")}</a></article>`;
}
function renderPublications(){
 const q=(document.querySelector("#pub-search")?.value||"").toLowerCase();
 const y=document.querySelector("#year-filter")?.value||"";
 const list=publications.filter(p=>(!q||`${p.title} ${p.journal}`.toLowerCase().includes(q))&&(!y||p.year===y));
 const target=document.querySelector("#publication-list");
 if(target)target.innerHTML=list.map(pubRow).join("");
}
async function initPublications(){
 publications=await getJSON("data/publications.json");
 publications.sort((a,b)=>String(b.year).localeCompare(String(a.year))||a.title.localeCompare(b.title));
 document.querySelector("#recent-publications").innerHTML=publications.slice(0,4).map(recentCard).join("");
 document.querySelector("#works-count").textContent=publications.length;
 document.querySelector("#recent-count").textContent=Math.min(4,publications.length);
 const sel=document.querySelector("#year-filter");
 [...new Set(publications.map(p=>p.year).filter(Boolean))].forEach(y=>sel?.insertAdjacentHTML("beforeend",`<option>${y}</option>`));
 renderPublications();
 document.querySelector("#pub-search")?.addEventListener("input",renderPublications);
 sel?.addEventListener("change",renderPublications);
}
async function initProfile(){
 const p=await getJSON("data/profile.json");
 document.querySelector("#experience-list").innerHTML=p.experience.map(x=>`<article class="timeline-item"><div class="timeline-date">${x[`date_${LANG}`]}</div><div class="timeline-main"><h3>${x[`title_${LANG}`]}</h3><p>${x.org}</p><span class="role-tag">${x[`area_${LANG}`]}</span></div></article>`).join("");
 document.querySelector("#education-list").innerHTML=p.education.map(x=>`<article class="education-item"><div class="education-year">${x.year}</div><div><h3>${x[`degree_${LANG}`]}</h3><p>${x[`org_${LANG}`]}</p></div><span class="honor">${x[`honor_${LANG}`]}</span></article>`).join("");
 document.querySelector("#awards-list").innerHTML=p.awards.map(x=>`<article class="award-card"><div class="award-icon">${icon("award")}</div><h3>${x[`title_${LANG}`]}</h3><p>${x[`detail_${LANG}`]}</p></article>`).join("");
 document.querySelector("#affiliations-list").innerHTML=p.affiliations.map(x=>`<article class="affiliation-card"><div class="affiliation-icon">${icon("building")}</div><div><h3>${x.institution}</h3><p>${x.location}</p><p>${x[`role_${LANG}`]} · ${x[`date_${LANG}`]}</p>${x.current?`<span class="current">${LANG==="en"?"Current affiliation":"Afiliación actual"}</span>`:""}</div></article>`).join("");
}
document.addEventListener("DOMContentLoaded",()=>{
 document.querySelector(".menu")?.addEventListener("click",()=>document.querySelector(".navlinks")?.classList.toggle("open"));
 document.querySelectorAll("[data-year-now]").forEach(x=>x.textContent=new Date().getFullYear());
 Promise.allSettled([initPublications(),initProfile()]);
});
