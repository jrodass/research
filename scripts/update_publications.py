#!/usr/bin/env python3
import json, re, urllib.request, urllib.parse
from pathlib import Path

ORCID="0000-0001-6526-7740"
HEADERS={"Accept":"application/json","User-Agent":"JorgeRodasAcademicSite/2.0 (mailto:jorge.rodass@gmail.com)"}

def get(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=40) as r:
        return json.load(r)

def doi_from(ids):
    for item in ids or []:
        if str(item.get("external-id-type","")).lower()=="doi":
            value=item.get("external-id-value","")
            return re.sub(r"^https?://(dx\.)?doi\.org/","",value,flags=re.I)
    return ""

def main():
    works=get(f"https://pub.orcid.org/v3.0/{ORCID}/works")
    output=[]
    for group in works.get("group",[]):
        summary=(group.get("work-summary") or [{}])[0]
        title=(((summary.get("title") or {}).get("title") or {}).get("value") or "Untitled work").strip()
        year=(((summary.get("publication-date") or {}).get("year") or {}).get("value") or "—")
        journal=(summary.get("journal-title") or {}).get("value") or ""
        ids=(summary.get("external-ids") or {}).get("external-id") or []
        doi=doi_from(ids)
        url=f"https://doi.org/{doi}" if doi else ((summary.get("url") or {}).get("value") or f"https://orcid.org/{ORCID}")
        output.append({
            "year":str(year),
            "title":title,
            "journal":journal,
            "doi":doi,
            "url":url,
            "type":str(summary.get("type") or "work").lower()
        })
    # De-duplicate by DOI when possible, otherwise normalized title.
    seen=set(); clean=[]
    for p in sorted(output,key=lambda x:(x["year"],x["title"]),reverse=True):
        key=("doi:"+p["doi"].lower()) if p["doi"] else ("title:"+re.sub(r"\W+","",p["title"].lower()))
        if key in seen: continue
        seen.add(key); clean.append(p)
    Path("data/publications.json").write_text(json.dumps(clean,ensure_ascii=False,indent=2),encoding="utf-8")
    metrics_path=Path("data/metrics.json")
    metrics=json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["orcid"]["works"]=len(clean)
    metrics_path.write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding="utf-8")

if __name__=="__main__":
    main()
