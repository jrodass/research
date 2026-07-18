
document.addEventListener("DOMContentLoaded",()=>{
  document.body.classList.add("js-ready");
  fetch(document.documentElement.lang.startsWith("en")?"../data/metrics.json":"data/metrics.json")
    .then(response=>response.ok?response.json():Promise.reject())
    .then(metrics=>document.querySelectorAll("[data-metric]").forEach(el=>{const value=metrics[el.dataset.metric];if(value!==undefined)el.textContent=value;}))
    .catch(()=>{});
  const menu=document.querySelector(".menu");
  const nav=document.querySelector(".nav-links");
  menu?.addEventListener("click",()=>{const open=nav?.classList.toggle("open");menu.setAttribute("aria-expanded",String(Boolean(open)));});
  document.querySelectorAll("[data-print-cv]").forEach(link=>link.addEventListener("click",event=>{event.preventDefault();window.print();}));

  const search=document.querySelector("#pub-search");
  const year=document.querySelector("#year-filter");
  const cards=[...document.querySelectorAll(".publication-card")];
  const prev=document.querySelector("#prev-page");
  const next=document.querySelector("#next-page");
  const pageStatus=document.querySelector("#page-status");
  const filteredCount=document.querySelector("#filtered-count");
  const visibleTotal=document.querySelector("#visible-total");
  const pageSize=5;
  let page=1;

  if(year){
    [...new Set(cards.map(card=>card.dataset.year).filter(Boolean))]
      .sort().reverse()
      .forEach(value=>year.insertAdjacentHTML("beforeend",`<option>${value}</option>`));
  }

  const matchingCards=()=>{
    const query=(search?.value||"").trim().toLowerCase();
    const selectedYear=year?.value||"";
    return cards.filter(card=>{
      const matchesQuery=!query||card.textContent.toLowerCase().includes(query);
      const matchesYear=!selectedYear||card.dataset.year===selectedYear;
      return matchesQuery&&matchesYear;
    });
  };

  const render=()=>{
    const results=matchingCards();
    const pageCount=Math.max(1,Math.ceil(results.length/pageSize));
    if(page>pageCount) page=pageCount;
    cards.forEach(card=>card.classList.remove("is-visible"));
    const start=(page-1)*pageSize;
    results.slice(start,start+pageSize).forEach(card=>card.classList.add("is-visible"));

    if(pageStatus){
      const label=document.documentElement.lang.startsWith("en")?"Page":"Página";
      pageStatus.textContent=`${label} ${page} ${document.documentElement.lang.startsWith("en")?"of":"de"} ${pageCount}`;
    }
    if(filteredCount) filteredCount.textContent=results.length;
    if(visibleTotal) visibleTotal.textContent=cards.length;
    if(prev) prev.disabled=page<=1;
    if(next) next.disabled=page>=pageCount;
  };

  search?.addEventListener("input",()=>{page=1;render();});
  year?.addEventListener("change",()=>{page=1;render();});
  prev?.addEventListener("click",()=>{if(page>1){page--;render();document.querySelector("#publication-list")?.scrollIntoView({behavior:"smooth",block:"start"});}});
  next?.addEventListener("click",()=>{const count=Math.max(1,Math.ceil(matchingCards().length/pageSize));if(page<count){page++;render();document.querySelector("#publication-list")?.scrollIntoView({behavior:"smooth",block:"start"});}});

  document.querySelectorAll("[data-year]").forEach(el=>el.textContent=new Date().getFullYear());
  render();
});
