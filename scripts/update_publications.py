#!/usr/bin/env python3
import json, re, html, urllib.request, urllib.parse
from pathlib import Path
ORCID="0000-0001-6526-7740"
HEAD={"Accept":"application/json","User-Agent":"JorgeRodasAcademicSite/1.0 (mailto:jorge.rodass@gmail.com)"}
def get(url):
    req=urllib.request.Request(url,headers=HEAD)
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def clean(s):
    if not s:return ""
    s=re.sub(r"<[^>]+>"," ",html.unescape(s))
    return re.sub(r"\s+"," ",s).strip()
def doi(ids):
    for x in ids or []:
        if str(x.get("external-id-type","")).lower()=="doi":
            return re.sub(r"^https?://(dx\.)?doi.org/","",x.get("external-id-value",""),flags=re.I)
    return ""
def main():
    works=get(f"https://pub.orcid.org/v3.0/{ORCID}/works")
    out=[]
    for g in works.get("group",[]):
        s=(g.get("work-summary") or [{}])[0]
        pc=s.get("put-code")
        d=get(f"https://pub.orcid.org/v3.0/{ORCID}/work/{pc}") if pc else {}
        title=((s.get("title") or {}).get("title") or {}).get("value") or "Publicación sin título"
        ids=(d.get("external-ids") or {}).get("external-id") or (s.get("external-ids") or {}).get("external-id") or []
        idoi=doi(ids)
        abstract=clean(d.get("short-description",""))
        if not abstract and idoi:
            try:
                cr=get("https://api.crossref.org/works/"+urllib.parse.quote(idoi,safe=""))
                abstract=clean((cr.get("message") or {}).get("abstract",""))
            except Exception: pass
        if not abstract:
            abstract=f"Publicación académica vinculada con {title.lower()}. Consulte el artículo completo para conocer el problema, el enfoque metodológico y los resultados."
        year=(((s.get("publication-date") or {}).get("year") or {}).get("value") or "—")
        url=f"https://doi.org/{idoi}" if idoi else ((d.get("url") or {}).get("value") or (s.get("url") or {}).get("value") or f"https://orcid.org/{ORCID}")
        out.append({"title":title,"year":year,"type":str(s.get("type") or "journal-article").replace("_"," ").lower(),
          "journal":(s.get("journal-title") or {}).get("value") or "Registro académico en ORCID",
          "doi":idoi,"url":url,"summary":abstract[:700]})
    out.sort(key=lambda x:str(x["year"]),reverse=True)
    Path("data/publications.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__":main()
