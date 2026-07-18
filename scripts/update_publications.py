#!/usr/bin/env python3
import json, re, urllib.request
from pathlib import Path

ORCID="0000-0001-6526-7740"
HEADERS={"Accept":"application/json","User-Agent":"JorgeRodasAcademicSite/3.0 (mailto:jorge.rodass@gmail.com)"}

def get(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=40) as r:
        return json.load(r)

def find_doi(ids):
    for item in ids or []:
        if str(item.get("external-id-type","")).lower()=="doi":
            return re.sub(r"^https?://(dx\.)?doi\.org/","",item.get("external-id-value",""),flags=re.I)
    return ""

def main():
    raw=get(f"https://pub.orcid.org/v3.0/{ORCID}/works")
    rows=[]
    for group in raw.get("group",[]):
        s=(group.get("work-summary") or [{}])[0]
        title=(((s.get("title") or {}).get("title") or {}).get("value") or "Untitled work").strip()
        year=(((s.get("publication-date") or {}).get("year") or {}).get("value") or "—")
        journal=(s.get("journal-title") or {}).get("value") or ""
        doi=find_doi((s.get("external-ids") or {}).get("external-id") or [])
        url=f"https://doi.org/{doi}" if doi else ((s.get("url") or {}).get("value") or f"https://orcid.org/{ORCID}")
        rows.append({"year":str(year),"title":title,"journal":journal,"doi":doi,"url":url,"type":str(s.get("type") or "work").lower()})
    seen=set(); output=[]
    for row in sorted(rows,key=lambda x:(x["year"],x["title"]),reverse=True):
        key=("doi:"+row["doi"].lower()) if row["doi"] else ("title:"+re.sub(r"\W+","",row["title"].lower()))
        if key in seen: continue
        seen.add(key); output.append(row)
    Path("data/publications.json").write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__":
    main()
