
const LANG=document.documentElement.lang.startsWith("en")?"en":"es";
const prefix=document.body.dataset.prefix||"";
let publications=[], posts=[];
const t=(obj,key)=>obj[`${key}_${LANG}`]||obj[`${key}_es`]||"";
function publicationCard(p){
 return `<article class="card pub">
 <div class="card-top"><span>${p.year}</span><span>${t(p,"type")}</span></div>
 <h3><a href="${p.url}" target="_blank" rel="noopener">${t(p,"title")}</a></h3>
 <p class="summary">${t(p,"summary")}</p><div class="journal">${p.journal}</div>
 <div class="card-foot"><span class="badge">${p.source}</span><a class="more" href="${p.url}" target="_blank" rel="noopener">${LANG==="en"?"Open article":"Ver artículo"} ↗</a></div></article>`;
}
function renderPublications(list){
 const el=document.querySelector("[data-publications]");if(!el)return;
 el.innerHTML=list.length?list.map(publicationCard).join(""):`<div class="empty">${LANG==="en"?"No publications match the selected criteria.":"No se encontraron publicaciones con los criterios seleccionados."}</div>`;
}
async function loadPublications(){
 const el=document.querySelector("[data-publications]");if(!el)return;
 try{
  const r=await fetch(`${prefix}data/publications.json`,{cache:"force-cache"});
  publications=await r.json();
  const home=document.body.dataset.page==="home";
  renderPublications(home?publications.slice(0,6):publications);
  if(!home)setupFilters();
 }catch{el.innerHTML=`<div class="empty">${LANG==="en"?"The local publication catalogue could not be loaded.":"No se pudo cargar el catálogo local de publicaciones."}</div>`}
}
function setupFilters(){
 const q=document.querySelector("#pub-search"),y=document.querySelector("#year-filter");if(!q||!y)return;
 [...new Set(publications.map(p=>p.year))].forEach(v=>y.insertAdjacentHTML("beforeend",`<option>${v}</option>`));
 const run=()=>{const s=q.value.toLowerCase(),yr=y.value;renderPublications(publications.filter(p=>(!yr||p.year===yr)&&(!s||`${t(p,"title")} ${t(p,"summary")} ${p.journal}`.toLowerCase().includes(s))))};
 q.addEventListener("input",run);y.addEventListener("change",run);
}
function postCard(p){
 return `<article class="card post"><div class="post-date">${p.date}</div><h3>${t(p,"title")}</h3><p>${t(p,"excerpt")}</p>
 <a class="post-link" href="${prefix}post.html?slug=${p.slug}">${LANG==="en"?"Read note":"Leer nota"} →</a></article>`;
}
async function loadPosts(){
 const list=document.querySelector("[data-posts]");const article=document.querySelector("[data-post]");
 if(!list&&!article)return;
 const r=await fetch(`${prefix}data/posts.json`);posts=await r.json();
 if(list)list.innerHTML=posts.map(postCard).join("");
 if(article){
  const slug=new URLSearchParams(location.search).get("slug");const p=posts.find(x=>x.slug===slug)||posts[0];
  article.innerHTML=`<div class="kicker">${p.date}</div><h1>${t(p,"title")}</h1><p class="lead">${t(p,"excerpt")}</p>${p[`content_${LANG}`].map(x=>`<p>${x}</p>`).join("")}`;
  document.title=`${t(p,"title")} | Jorge Rodas Silva`;
 }
}
document.addEventListener("DOMContentLoaded",()=>{
 document.querySelector(".menu")?.addEventListener("click",()=>document.querySelector(".links")?.classList.toggle("open"));
 document.querySelectorAll("[data-year]").forEach(x=>x.textContent=new Date().getFullYear());
 loadPublications();loadPosts();
});
