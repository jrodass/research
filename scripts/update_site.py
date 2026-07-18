#!/usr/bin/env python3
import json,re,urllib.request,html
from pathlib import Path
ORCID="0000-0001-6526-7740"
H={"Accept":"application/json","User-Agent":"JorgeRodasAcademicSite/4.0 (mailto:jorge.rodass@gmail.com)"}
def get(url):
 req=urllib.request.Request(url,headers=H)
 with urllib.request.urlopen(req,timeout=40) as r:return json.load(r)
def doi(ids):
 for x in ids or []:
  if str(x.get("external-id-type","")).lower()=="doi":
   return re.sub(r"^https?://(dx\.)?doi\.org/","",x.get("external-id-value",""),flags=re.I)
 return ""
def sync():
 raw=get(f"https://pub.orcid.org/v3.0/{ORCID}/works");rows=[]
 for g in raw.get("group",[]):
  s=(g.get("work-summary") or [{}])[0]
  title=(((s.get("title") or {}).get("title") or {}).get("value") or "Untitled work").strip()
  year=(((s.get("publication-date") or {}).get("year") or {}).get("value") or "—")
  journal=(s.get("journal-title") or {}).get("value") or ""
  d=doi((s.get("external-ids") or {}).get("external-id") or [])
  url=f"https://doi.org/{d}" if d else ((s.get("url") or {}).get("value") or f"https://orcid.org/{ORCID}")
  rows.append({"year":str(year),"title":title,"journal":journal,"doi":d,"url":url,"type":str(s.get("type") or "Publication").replace("_"," ").title()})
 seen=set();out=[]
 for x in sorted(rows,key=lambda z:(z["year"],z["title"]),reverse=True):
  k=("doi:"+x["doi"].lower()) if x["doi"] else ("title:"+re.sub(r"\W+","",x["title"].lower()))
  if k not in seen:seen.add(k);out.append(x)
 Path("data/publications.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
 return out
def icon():
 return '<svg viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9"/><path d="M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6"/></svg>'
def url(p):return p.get("url") or (f"https://doi.org/{p['doi']}" if p.get("doi") else f"https://orcid.org/{ORCID}")
def blocks(pubs,lang):
 recent=[]
 for p in pubs[:4]:
  open_text="Open article" if lang=="en" else "Ver artículo"
  source=("DOI "+p["doi"]) if p.get("doi") else "ORCID / source"
  recent.append(f'<article class="recent-card"><div class="recent-top"><span class="year-chip">{html.escape(p["year"])}</span><span>{html.escape(p["type"])}</span></div><h3><a target="_blank" href="{html.escape(url(p))}">{html.escape(p["title"])}</a></h3><p>{html.escape(p["journal"])}</p><div class="card-footer"><span>{html.escape(source)}</span><a class="article-link" target="_blank" href="{html.escape(url(p))}">{open_text}{icon()}</a></div></article>')
 rows=[]
 for p in pubs:
  d=f'<span>DOI {html.escape(p["doi"])}</span>' if p.get("doi") else ""
  rows.append(f'<article class="publication-row" data-year="{html.escape(p["year"])}"><div><h3><a target="_blank" href="{html.escape(url(p))}">{html.escape(p["title"])}</a></h3><div class="pub-meta"><span class="year-chip">{html.escape(p["year"])}</span><span>{html.escape(p["journal"])}</span>{d}</div></div><a class="publication-open" target="_blank" href="{html.escape(url(p))}">{icon()}</a></article>')
 return "".join(recent),"".join(rows)
def replace(path,pubs,lang):
 s=Path(path).read_text(encoding="utf-8");recent,rows=blocks(pubs,lang)
 s=re.sub(r'(<div class="recent-grid">).*?(</div></div></section>\s*<section class="section" id="all-publications">)',lambda m:m.group(1)+recent+m.group(2),s,flags=re.S)
 s=re.sub(r'(<div class="publication-list">).*?(</div></div></section>\s*<section class="section white" id="experience">)',lambda m:m.group(1)+rows+m.group(2),s,flags=re.S)
 s=re.sub(r'(<strong>)\d+(</strong><span>(?:ORCID works|Trabajos en ORCID))',rf'\g<1>{len(pubs)}\g<2>',s)
 Path(path).write_text(s,encoding="utf-8")
if __name__=="__main__":
 p=sync();replace("index.html",p,"es");replace("en/index.html",p,"en")
