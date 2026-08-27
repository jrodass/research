#!/usr/bin/env python3
"""Synchronize ORCID + Scopus works and enrich them with OpenAlex/Crossref."""
import html as html_lib
import json, os, re, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

ORCID = "0000-0001-6526-7740"
SCOPUS_AUTHOR_IDS = ("59258484700", "57188854666")
ADDITIONAL_DOIS = ("10.1016/j.bdr.2026.100630",)
HEAD = {"Accept": "application/json", "User-Agent": "JorgeRodasResearch/13.0"}

def get(url, headers=None):
    request_headers = dict(HEAD)
    request_headers.update(headers or {})
    req = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)

def clean_doi(value):
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", value or "", flags=re.I).strip()

def clean_text(value):
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()

def normalized_title(value):
    return re.sub(r"\W+", "", (value or "").casefold())

def abstract_text(inverted):
    """Reconstruct OpenAlex's inverted abstract index as readable text."""
    if not inverted:
        return ""
    words = []
    for word, positions in inverted.items():
        words.extend((position, word) for position in positions)
    return " ".join(word for _, word in sorted(words))

def crossref_abstract(doi):
    if not doi:
        return ""
    try:
        payload = get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
        raw = (payload.get("message") or {}).get("abstract") or ""
        return clean_text(raw)
    except Exception:
        return ""

def crossref_works(dois):
    """Retrieve confirmed publications by DOI while author-profile APIs catch up."""
    works = []
    for requested_doi in dois:
        doi = clean_doi(requested_doi)
        try:
            payload = get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
            message = payload.get("message") or {}
            date_parts = (
                (message.get("published-print") or {}).get("date-parts")
                or (message.get("published-online") or {}).get("date-parts")
                or (message.get("issued") or {}).get("date-parts")
                or []
            )
            authors = []
            for author in message.get("author") or []:
                name = " ".join(filter(None, (author.get("given"), author.get("family"))))
                if name:
                    authors.append(name)
            works.append({
                "year": str(date_parts[0][0]) if date_parts and date_parts[0] else "—",
                "title": clean_text(next(iter(message.get("title") or []), "Untitled work")),
                "journal": clean_text(next(iter(message.get("container-title") or []), "")),
                "doi": doi,
                "url": f"https://doi.org/{doi}",
                "type": str(message.get("type") or "Publication").replace("-", " ").title(),
                "authors": ", ".join(authors) or "Jorge Rodas-Silva et al.",
                "open_access": False,
                "citations": int(message.get("is-referenced-by-count") or 0),
                "abstract": clean_text(message.get("abstract")),
                "sources": ["Crossref"],
            })
        except Exception as exc:
            print(f"Crossref fallback unavailable for {doi}: {exc}")
    return works

def short_summary(abstract, title, journal, lang):
    text = re.sub(r"^(abstract|resumen)\s*[:.—-]*\s*", "", abstract or "", flags=re.I).strip()
    if text:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        result = " ".join(sentences[:2]).strip()
        return result if len(result) <= 520 else result[:517].rsplit(" ", 1)[0] + "…"
    venue = journal or ("the indexed scientific record" if lang == "en" else "el registro científico indexado")
    if lang == "en":
        return f'This publication examines “{title}”. Based on its title and bibliographic record in {venue}, it addresses the stated research problem and presents findings relevant to its academic and professional field.'
    return f'Esta publicación examina «{title}». A partir de su título y registro bibliográfico en {venue}, aborda el problema de investigación planteado y presenta aportes relevantes para su campo académico y profesional.'

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
            "abstract": "",
            "sources": ["ORCID"],
        })
    return works

def scopus_headers():
    headers = {
        "X-ELS-APIKey": os.environ["ELSEVIER_API_KEY"],
        "Accept": "application/json",
    }
    token = os.environ.get("ELSEVIER_INSTTOKEN", "").strip()
    if token:
        headers["X-ELS-Insttoken"] = token
    return headers

def scopus_public_url(eid):
    return "https://www.scopus.com/record/display.uri?" + urllib.parse.urlencode({
        "eid": eid,
        "origin": "resultslist",
    })

def scopus_authors(entry):
    authors = entry.get("author") or []
    if isinstance(authors, dict):
        authors = [authors]
    names = []
    for author in authors:
        name = author.get("authname") or author.get("ce:indexed-name")
        if not name:
            preferred = author.get("preferred-name") or {}
            given = preferred.get("ce:given-name") or author.get("ce:given-name") or ""
            surname = preferred.get("ce:surname") or author.get("ce:surname") or ""
            name = f"{given} {surname}".strip()
        if name:
            names.append(name)
    return ", ".join(names)

def scopus_works():
    """Return all records assigned to either of the author's Scopus profiles."""
    if not os.environ.get("ELSEVIER_API_KEY", "").strip():
        print("Scopus sync skipped: ELSEVIER_API_KEY is not configured.")
        return [], False
    query = " OR ".join(f"AU-ID({author_id})" for author_id in SCOPUS_AUTHOR_IDS)
    start, total, rows = 0, None, []
    while total is None or start < total:
        params = urllib.parse.urlencode({
            "query": query,
            "start": start,
            "count": 25,
            "view": "STANDARD",
        })
        payload = get(
            "https://api.elsevier.com/content/search/scopus?" + params,
            scopus_headers(),
        )
        result = payload.get("search-results") or {}
        entries = result.get("entry") or []
        total = int(result.get("opensearch:totalResults") or 0)
        if not entries:
            break
        for entry in entries:
            doi = clean_doi(entry.get("prism:doi") or "")
            eid = entry.get("eid") or ""
            cover_date = entry.get("prism:coverDate") or entry.get("prism:coverDisplayDate") or ""
            year_match = re.search(r"\b(19|20)\d{2}\b", cover_date)
            scopus_id = re.sub(r"^SCOPUS_ID:", "", entry.get("dc:identifier") or "")
            rows.append({
                "year": year_match.group(0) if year_match else "—",
                "title": clean_text(entry.get("dc:title")) or "Untitled work",
                "journal": clean_text(entry.get("prism:publicationName")),
                "doi": doi,
                "url": f"https://doi.org/{doi}" if doi else scopus_public_url(eid),
                "type": clean_text(entry.get("subtypeDescription") or entry.get("prism:aggregationType") or "Publication"),
                "authors": scopus_authors(entry) or "Jorge Rodas-Silva et al.",
                "open_access": str(entry.get("openaccess") or "") == "1",
                "citations": int(entry.get("citedby-count") or 0),
                "abstract": clean_text(entry.get("dc:description")),
                "scopus_eid": eid,
                "scopus_id": scopus_id,
                "sources": ["Scopus"],
            })
        start += len(entries)
    return rows, True

def scopus_detail(eid):
    """Retrieve an abstract when the Scopus search record does not include one."""
    if not eid or not os.environ.get("ELSEVIER_API_KEY", "").strip():
        return {}
    try:
        params = urllib.parse.urlencode({"view": "FULL"})
        payload = get(
            "https://api.elsevier.com/content/abstract/eid/"
            + urllib.parse.quote(eid, safe="-.:")
            + "?"
            + params,
            scopus_headers(),
        )
        response = payload.get("abstracts-retrieval-response") or {}
        core = response.get("coredata") or {}
        authors = scopus_authors(response.get("authors") or {})
        return {
            "abstract": clean_text(core.get("dc:description")),
            "authors": authors,
        }
    except Exception as exc:
        print(f"Scopus abstract unavailable for {eid}: {exc}")
        return {}

def openalex_works():
    cursor, rows = "*", []
    base = "https://api.openalex.org/works?filter=author.orcid:https://orcid.org/" + ORCID
    while cursor:
        query = urllib.parse.urlencode({"per-page": 200, "cursor": cursor})
        payload = get(base + "&" + query)
        rows.extend(payload.get("results", []))
        cursor = (payload.get("meta") or {}).get("next_cursor")
        if not payload.get("results"): break
    return rows

def merge_into(target, incoming):
    """Merge two representations of the same publication without losing data."""
    defaults = {"", "—", "Publication", "Untitled work", "Academic publication"}
    for field in ("year", "title", "journal", "doi", "url", "type", "scopus_eid", "scopus_id"):
        value = incoming.get(field)
        if value and (not target.get(field) or target.get(field) in defaults):
            target[field] = value
    incoming_authors = incoming.get("authors") or ""
    target_authors = target.get("authors") or ""
    if incoming_authors and ("et al." in target_authors or len(incoming_authors) > len(target_authors)):
        target["authors"] = incoming_authors
    target["citations"] = max(int(target.get("citations") or 0), int(incoming.get("citations") or 0))
    target["open_access"] = bool(target.get("open_access") or incoming.get("open_access"))
    if len(incoming.get("abstract") or "") > len(target.get("abstract") or ""):
        target["abstract"] = incoming["abstract"]
    target["sources"] = sorted(set((target.get("sources") or []) + (incoming.get("sources") or [])))
    if target.get("doi"):
        target["doi"] = clean_doi(target["doi"])
        target["url"] = f"https://doi.org/{target['doi']}"
    return target

def merge_catalog(*collections):
    """Deduplicate first by DOI, then Scopus EID, finally normalized title."""
    catalog = []
    for collection in collections:
        for incoming in collection:
            doi = clean_doi(incoming.get("doi") or "").casefold()
            eid = (incoming.get("scopus_eid") or "").casefold()
            title = normalized_title(incoming.get("title"))
            match = next((
                item for item in catalog
                if (doi and clean_doi(item.get("doi") or "").casefold() == doi)
                or (eid and (item.get("scopus_eid") or "").casefold() == eid)
                or (title and normalized_title(item.get("title")) == title)
            ), None)
            if match:
                merge_into(match, incoming)
            else:
                item = dict(incoming)
                item["sources"] = sorted(set(item.get("sources") or []))
                catalog.append(item)
    return catalog

def main():
    previous_path = Path("data/publications.json")
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else []
    scopus, scopus_enabled = scopus_works()
    works = merge_catalog(orcid_works(), scopus, crossref_works(ADDITIONAL_DOIS), previous)
    alex = openalex_works()
    by_doi = {clean_doi(w.get("doi")).lower(): w for w in alex if w.get("doi")}
    by_title = {normalized_title(w.get("title")): w for w in alex}
    for item in works:
        match = by_doi.get(clean_doi(item.get("doi") or "").lower()) if item.get("doi") else by_title.get(normalized_title(item["title"]))
        if not match: continue
        authors = [a.get("author", {}).get("display_name") for a in match.get("authorships", [])]
        enrichment = {
            "authors": ", ".join(filter(None, authors)) or item["authors"],
            "citations": int(match.get("cited_by_count") or 0),
            "open_access": bool((match.get("open_access") or {}).get("is_oa")),
            "abstract": abstract_text(match.get("abstract_inverted_index")),
            "url": item["url"] if item["doi"] else (match.get("primary_location") or {}).get("landing_page_url") or item["url"],
            "sources": ["OpenAlex"],
        }
        merge_into(item, enrichment)
    for item in works:
        if not item.get("abstract") and item.get("scopus_eid"):
            detail = scopus_detail(item["scopus_eid"])
            if detail.get("abstract"):
                item["abstract"] = detail["abstract"]
            if detail.get("authors") and ("et al." in (item.get("authors") or "")):
                item["authors"] = detail["authors"]
        if not item.get("abstract"):
            item["abstract"] = crossref_abstract(item.get("doi"))
        item["summary_es"] = short_summary(item.get("abstract"), item["title"], item.get("journal"), "es")
        item["summary_en"] = short_summary(item.get("abstract"), item["title"], item.get("journal"), "en")
    override_path = Path("data/summary_overrides.json")
    overrides = json.loads(override_path.read_text(encoding="utf-8")) if override_path.exists() else {}
    for item in works:
        override = overrides.get(item.get("doi")) or overrides.get(item["title"])
        if override:
            item["summary_es"] = override["es"]
            item["summary_en"] = override["en"]
    unique = sorted(merge_catalog(works), key=lambda x: (x["year"], x["title"]), reverse=True)
    citations = sorted((int(item.get("citations") or 0) for item in unique), reverse=True)
    h_index = max((i for i, count in enumerate(citations, 1) if count >= i), default=0)
    sources = ["ORCID", "OpenAlex"]
    if scopus_enabled or any("Scopus" in (item.get("sources") or []) for item in unique):
        sources.insert(1, "Scopus")
    metrics = {
        "publications": len(unique),
        "journals": sum("journal" in p["type"].lower() for p in unique),
        "conference_papers": sum("conference" in p["type"].lower() for p in unique),
        "book_chapters": sum("book" in p["type"].lower() for p in unique),
        "doi_links": sum(bool(p["doi"]) for p in unique),
        "citations": sum(citations), "h_index": h_index,
        "i10_index": sum(c >= 10 for c in citations),
        "citations_per_publication": round(sum(citations) / len(unique), 1) if unique else 0,
        "cited_publications_share": f"{round(100 * sum(c > 0 for c in citations) / len(unique))}%" if unique else "0%",
        "open_access_share": f"{round(100 * sum(bool(item.get('open_access')) for item in unique) / len(unique))}%" if unique else "0%",
        "updated": date.today().isoformat(), "sources": sources,
        "scopus_author_ids": list(SCOPUS_AUTHOR_IDS),
    }
    Path("data/publications.json").write_text(json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8")
    Path("data/metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    import rebuild_site
    rebuild_site.rebuild(unique, metrics)

if __name__ == "__main__": main()

