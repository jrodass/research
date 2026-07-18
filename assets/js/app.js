
document.addEventListener("DOMContentLoaded",()=>{
 const menu=document.querySelector(".menu"),nav=document.querySelector(".navlinks");
 menu?.addEventListener("click",()=>nav?.classList.toggle("open"));
 const search=document.querySelector("#pub-search"),year=document.querySelector("#year-filter");
 const cards=[...document.querySelectorAll(".pub")];
 if(year){
   [...new Set(cards.map(c=>c.dataset.year))].sort().reverse().forEach(y=>year.insertAdjacentHTML("beforeend",`<option>${y}</option>`));
 }
 const filter=()=>{
  const q=(search?.value||"").toLowerCase(), y=year?.value||"";
  cards.forEach(c=>{
   const ok=(!q||c.textContent.toLowerCase().includes(q))&&(!y||c.dataset.year===y);
   c.classList.toggle("hidden",!ok);
  });
 };
 search?.addEventListener("input",filter);year?.addEventListener("change",filter);
 document.querySelectorAll("[data-year-now]").forEach(x=>x.textContent=new Date().getFullYear());
});
