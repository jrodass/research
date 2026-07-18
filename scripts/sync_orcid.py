#!/usr/bin/env python3
"""Synchronize ORCID works and enrich bibliometrics with OpenAlex."""
import json, re, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

ORCID = "0000-0001-6526-7740"
MAIL = "jrodass@unemi.edu.ec"
HEAD = {"Accept": "application/json", "User-Agent": f"JorgeRodasResearch/12.0 (mailto:{MAIL})"}

def get(url):
    req = urllib.request.Request(url, headers=HEAD)
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)

def clean_doi(value):
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", value or "", flags=re.I).strip()

def orcid_works():
    raw = get(f"https://pub.orcid.org/v3.0/{ORCID}/works")
    works = []
    for group in raw.get("group", []):
        summary = (group.get("work-summary") or [{}])[0]
        external = (summary.get("external-ids") or {}).get("external-id") or []
        doi = next((clean_doi(x.get("external-id-value")) for x in external if str(x.get("external-id-type", "")).lower() == "doi"), "")
        works.append({
            "year": str((((summary.get("publication-date") or {}).get("year") or {}).get("value") or "—")),
            "title": ((((summary.get("title") or {}).get("title") or {}).get("value") or "Untitled work").strip()),
            "journal": (summary.get("journal-title") or {}).get("value") or "",
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else ((summary.get("url") or {}).get("value") or f"https://orcid.org/{ORCID}"),
            "type": str(summary.get("type") or "Publication").replace("_", " ").title(),
            "authors": "Jorge Rodas-Silva et al.",
            "open_access": False,
            "citations": 0,
        })
    return works

def openalex_works():
    cursor, rows = "*", []
    base = "https://api.openalex.org/works?filter=author.orcid:https://orcid.org/" + ORCID
    while cursor:
        query = urllib.parse.urlencode({"per-page": 200, "cursor": cursor, "mailto": MAIL})
        payload = get(base + "&" + query)
        rows.extend(payload.get("results", []))
        cursor = (payload.get("meta") or {}).get("next_cursor")
        if not payload.get("results"): break
    return rows

def main():
    works = orcid_works()
    alex = openalex_works()
    by_doi = {clean_doi(w.get("doi")): w for w in alex if w.get("doi")}
    by_title = {re.sub(r"\W+", "", (w.get("title") or "").lower()): w for w in alex}
    for item in works:
        match = by_doi.get(item["doi"].lower()) if item["doi"] else by_title.get(re.sub(r"\W+", "", item["title"].lower()))
        if not match: continue
        authors = [a.get("author", {}).get("display_name") for a in match.get("authorships", [])]
        item.update({
            "authors": ", ".join(filter(None, authors)) or item["authors"],
            "citations": int(match.get("cited_by_count") or 0),
            "open_access": bool((match.get("open_access") or {}).get("is_oa")),
            "url": item["url"] if item["doi"] else (match.get("primary_location") or {}).get("landing_page_url") or item["url"],
        })
    unique, seen = [], set()
    for item in sorted(works, key=lambda x: (x["year"], x["title"]), reverse=True):
        key = "doi:" + item["doi"].lower() if item["doi"] else "title:" + re.sub(r"\W+", "", item["title"].lower())
        if key not in seen: seen.add(key); unique.append(item)
    citations = sorted((int(w.get("cited_by_count") or 0) for w in alex), reverse=True)
    h_index = max((i for i, count in enumerate(citations, 1) if count >= i), default=0)
    metrics = {
        "publications": len(unique),
        "journals": sum("journal" in p["type"].lower() for p in unique),
        "conference_papers": sum("conference" in p["type"].lower() for p in unique),
        "book_chapters": sum("book" in p["type"].lower() for p in unique),
        "doi_links": sum(bool(p["doi"]) for p in unique),
        "citations": sum(citations), "h_index": h_index,
        "i10_index": sum(c >= 10 for c in citations),
        "citations_per_publication": round(sum(citations) / len(alex), 1) if alex else 0,
        "cited_publications_share": f"{round(100 * sum(c > 0 for c in citations) / len(alex))}%" if alex else "0%",
        "open_access_share": f"{round(100 * sum(bool((w.get('open_access') or {}).get('is_oa')) for w in alex) / len(alex))}%" if alex else "0%",
        "updated": date.today().isoformat(), "sources": ["ORCID", "OpenAlex"]
    }
    Path("data/publications.json").write_text(json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8")
    Path("data/metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    import rebuild_site
    rebuild_site.rebuild(unique, metrics)

if __name__ == "__main__": main()
