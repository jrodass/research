#!/usr/bin/env python3
"""Synchronize ORCID + Scopus works and enrich them with OpenAlex/Crossref."""
import html as html_lib
import json, os, re, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

ORCID = "0000-0001-6526-7740"
SCOPUS_AUTHOR_IDS = ("59258484700", "57188854666")
ADDITIONAL_DOIS = ("10.1016/j.bdr.2026.100630",)
HEAD = {"Accept": "application/json", "User-Agent": "JorgeRodasResearch/14.0"}

# Confirmed works published in journals registered by Latindex that are not
# consistently returned by the author-profile APIs.  English titles are used
# as the site's display standard; title_aliases retain the original titles for
# deduplication and OpenAlex matching.
LATINDEX_WORKS = (
    {
        "year": "2022",
        "publication_date": "2022-05-31",
        "title": "Comparative Analysis of Methodologies and Technological Tools for Business Intelligence Processes Aimed at Decision-Making",
        "title_aliases": [
            "Análisis comparativo de metodologías y herramientas tecnológicas para procesos de Business Intelligence orientado a la toma de decisiones",
        ],
        "journal": "Informática y Sistemas",
        "doi": "10.33936/isrtic.v6i1.4522",
        "url": "https://doi.org/10.33936/isrtic.v6i1.4522",
        "type": "Journal Article",
        "authors": "María José Guerrero García, Jorge Rodas-Silva",
        "open_access": True,
        "citations": 0,
        "abstract": "",
        "sources": ["Latindex"],
    },
    {
        "year": "2018",
        "publication_date": "2018-03-24",
        "title": "Selection of Deployment Configurations Using Recommender Systems on Android",
        "title_aliases": [
            "Selection of deployment configurations using Recommender Systems on Android",
        ],
        "journal": "RISTI - Revista Ibérica de Sistemas e Tecnologias de Informação",
        "doi": "",
        "url": "https://investigacion.unemi.edu.ec/perfil-docente/298/?subtab=articulos&tab=produccion",
        "type": "Journal Article",
        "authors": "Jorge Rodas-Silva, José A. Galindo, David Benavides, R. Soriano",
        "open_access": True,
        "citations": 0,
        "abstract": "",
        "sources": ["Latindex"],
    },
    {
        "year": "2015",
        "publication_date": "2015-12-01",
        "title": "Business Intelligence System and Its Impact on Decision-Making in Telecommunications Companies in La Troncal, Ecuador",
        "title_aliases": [
            "Business Intelligence System and Its Impact on Decision-Making in the Companies Telecommunications of the Town La Troncal, Ecuador",
        ],
        "journal": "Copérnico",
        "doi": "",
        "url": "https://investigacion.unemi.edu.ec/perfil-docente/298/?subtab=articulos&tab=produccion",
        "type": "Journal Article",
        "authors": "Jorge Luis Rodas-Silva, Manuel Guillermo Rodríguez-López, Jesennia Cárdenas-Cobo",
        "open_access": True,
        "citations": 0,
        "abstract": "",
        "sources": ["Latindex"],
    },
    {
        "year": "2015",
        "publication_date": "2015-09-15",
        "title": "Strategic Planning Through ICT in Rural Decentralized Autonomous Governments of Milagro Canton",
        "title_aliases": [
            "Planificación estratégica a través de las TIC en los Gobiernos Autónomos Descentralizados Rurales del cantón Milagro",
            "Strategic planning through ICT in rural Autonomous Governments canton Milagro",
        ],
        "journal": "Ciencia UNEMI",
        "doi": "10.29076/issn.2528-7737vol8iss15.2015pp40-49p",
        "url": "https://doi.org/10.29076/issn.2528-7737vol8iss15.2015pp40-49p",
        "type": "Journal Article",
        "authors": "Mariuxi Geovanna Vinueza Morales, Jorge Rodas-Silva, Ana Chacón Luna",
        "open_access": True,
        "citations": 0,
        "abstract": "",
        "sources": ["Latindex"],
    },
    {
        "year": "2015",
        "publication_date": "2015-04-01",
        "title": "Standards That Contribute to the Development and Delivery of High-Quality Software Products",
        "title_aliases": [
            "Estándares que contribuyen al desarrollo y entrega de productos de software de calidad",
            "Standards that contribute to the development and delivery of high quality software products",
        ],
        "journal": "Ciencia UNEMI",
        "doi": "10.29076/issn.2528-7737vol8iss13.2015pp90-99p",
        "url": "https://doi.org/10.29076/issn.2528-7737vol8iss13.2015pp90-99p",
        "type": "Journal Article",
        "authors": "Ana Chacón Luna, Jorge Luis Rodas-Silva, Mariuxi Vinueza Morales",
        "open_access": True,
        "citations": 0,
        "abstract": "",
        "sources": ["Latindex"],
    },
    {
        "year": "2014",
        "publication_date": "2014-12-19",
        "title": "Digital Management Systems to Improve Academic Processes in Educational Institutions",
        "title_aliases": [
            "Sistemas de Gestión Digital para mejorar los procesos académicos en instituciones educativas",
        ],
        "journal": "Universidad, Ciencia y Tecnología",
        "doi": "",
        "url": "https://ve.scielo.org/scielo.php?pid=S1316-48212014000400001&script=sci_arttext&tlng=es",
        "type": "Journal Article",
        "authors": "Jorge Rodas-Silva, Jesennia Cárdenas-Cobo",
        "open_access": True,
        "citations": 0,
        "abstract": "",
        "sources": ["Latindex"],
    },
    {
        "year": "2014",
        "publication_date": "2014-12-01",
        "title": "E-Commerce: A Perspective from SMEs for Developing Strategies to Promote Economic and Business Growth in the City of Milagro",
        "title_aliases": [
            "Comercio electrónico: Un enfoque desde las perspectivas de las PYMES en la generación de estrategias para potenciar el desarrollo económico y empresarial en la ciudad de Milagro",
            "E-commerce: an approach from the perspective of PYMES in generating strategies and business promote economic development in the Milagro city",
        ],
        "journal": "ECA Sinergia",
        "doi": "",
        "url": "https://revistas.utm.edu.ec/index.php/ECASinergia/article/view/177",
        "type": "Journal Article",
        "authors": "Jorge Luis Rodas-Silva, Ana Eva Chacón Luna, Mariuxi Geovanna Vinueza Morales",
        "open_access": True,
        "citations": 0,
        "abstract": "",
        "sources": ["Latindex"],
    },
    {
        "year": "2012",
        "publication_date": "2012-12-31",
        "title": "Study to Determine the Use and Application of ICT in Teaching and Learning Processes by Educators in Milagro and Neighboring Cantons",
        "title_aliases": [
            "Estudio para determinar el uso y aplicación de las TIC: En los procesos de enseñanza aprendizaje por parte de los docentes de la ciudad de Milagro y cantones aledaños",
        ],
        "journal": "Ciencia UNEMI",
        "doi": "10.29076/issn.2528-7737vol5iss8.2012pp79-92p",
        "url": "https://doi.org/10.29076/issn.2528-7737vol5iss8.2012pp79-92p",
        "type": "Journal Article",
        "authors": "Jorge Luis Rodas-Silva",
        "open_access": True,
        "citations": 0,
        "abstract": "",
        "sources": ["Latindex"],
    },
)

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

def iso_date_from_parts(parts):
    """Return the most precise valid ISO date available in a date-parts list."""
    if not parts:
        return ""
    try:
        year = int(parts[0])
        if not 1900 <= year <= 2100:
            return ""
        if len(parts) < 2 or parts[1] in (None, ""):
            return f"{year:04d}"
        month = int(parts[1])
        if not 1 <= month <= 12:
            return f"{year:04d}"
        if len(parts) < 3 or parts[2] in (None, ""):
            return f"{year:04d}-{month:02d}"
        day = int(parts[2])
        date(year, month, day)  # Validate the complete calendar date.
        return f"{year:04d}-{month:02d}-{day:02d}"
    except (TypeError, ValueError, IndexError):
        return ""

def normalize_publication_date(value):
    """Normalize YYYY, YYYY-MM or YYYY-MM-DD values used by source APIs."""
    match = re.search(
        r"\b((?:19|20)\d{2})(?:[-/](\d{1,2}))?(?:[-/](\d{1,2}))?\b",
        str(value or ""),
    )
    if not match:
        return ""
    return iso_date_from_parts([part for part in match.groups() if part is not None])

def orcid_publication_date(publication_date):
    """Build the most precise date supplied in an ORCID work summary."""
    publication_date = publication_date or {}
    parts = []
    for field in ("year", "month", "day"):
        value = (publication_date.get(field) or {}).get("value")
        if value in (None, ""):
            break
        parts.append(value)
    return iso_date_from_parts(parts)

def publication_sort_key(item):
    """Sort key for newest-first chronology, with year-only records last."""
    value = normalize_publication_date(
        item.get("publication_date") or item.get("year")
    )
    parts = [int(part) for part in value.split("-") if part]
    return tuple((parts + [0, 0, 0])[:3])

def normalized_title(value):
    return re.sub(r"\W+", "", (value or "").casefold())

def title_keys(item):
    """Return normalized display and alternate titles for deduplication."""
    values = [item.get("title") or ""] + list(item.get("title_aliases") or [])
    return {normalized_title(value) for value in values if normalized_title(value)}

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
                (message.get("published-online") or {}).get("date-parts")
                or (message.get("published-print") or {}).get("date-parts")
                or (message.get("issued") or {}).get("date-parts")
                or []
            )
            publication_date = iso_date_from_parts(
                date_parts[0] if date_parts else []
            )
            authors = []
            for author in message.get("author") or []:
                name = " ".join(filter(None, (author.get("given"), author.get("family"))))
                if name:
                    authors.append(name)
            works.append({
                "year": publication_date[:4] if publication_date else "—",
                "publication_date": publication_date,
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
        publication_date = orcid_publication_date(summary.get("publication-date"))
        works.append({
            "year": publication_date[:4] if publication_date else "—",
            "publication_date": publication_date,
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
            publication_date = normalize_publication_date(cover_date)
            scopus_id = re.sub(r"^SCOPUS_ID:", "", entry.get("dc:identifier") or "")
            rows.append({
                "year": publication_date[:4] if publication_date else "—",
                "publication_date": publication_date,
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
    target_date = normalize_publication_date(target.get("publication_date"))
    incoming_date = normalize_publication_date(incoming.get("publication_date"))
    if incoming_date and incoming_date.count("-") > target_date.count("-"):
        target["publication_date"] = incoming_date
    incoming_authors = incoming.get("authors") or ""
    target_authors = target.get("authors") or ""
    if incoming_authors and ("et al." in target_authors or len(incoming_authors) > len(target_authors)):
        target["authors"] = incoming_authors
    target["citations"] = max(int(target.get("citations") or 0), int(incoming.get("citations") or 0))
    target["open_access"] = bool(target.get("open_access") or incoming.get("open_access"))
    if len(incoming.get("abstract") or "") > len(target.get("abstract") or ""):
        target["abstract"] = incoming["abstract"]
    target["sources"] = sorted(set((target.get("sources") or []) + (incoming.get("sources") or [])))
    target["title_aliases"] = sorted(set(
        (target.get("title_aliases") or []) + (incoming.get("title_aliases") or [])
    ))
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
            titles = title_keys(incoming)
            match = next((
                item for item in catalog
                if (doi and clean_doi(item.get("doi") or "").casefold() == doi)
                or (eid and (item.get("scopus_eid") or "").casefold() == eid)
                or bool(titles & title_keys(item))
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
    # Scopus is authoritative when sources provide equally precise dates.
    # Put curated Latindex records first so their normalized English titles
    # remain the display titles while richer API metadata is merged into them.
    works = merge_catalog(LATINDEX_WORKS, scopus, orcid_works(), crossref_works(ADDITIONAL_DOIS), previous)
    alex = openalex_works()
    by_doi = {clean_doi(w.get("doi")).lower(): w for w in alex if w.get("doi")}
    by_title = {normalized_title(w.get("title")): w for w in alex}
    for item in works:
        match = by_doi.get(clean_doi(item.get("doi") or "").lower()) if item.get("doi") else None
        if not match:
            match = next((by_title[key] for key in title_keys(item) if key in by_title), None)
        if not match: continue
        authors = [a.get("author", {}).get("display_name") for a in match.get("authorships", [])]
        enrichment = {
            "authors": ", ".join(filter(None, authors)) or item["authors"],
            "publication_date": normalize_publication_date(
                match.get("publication_date") or match.get("publication_year")
            ),
            "citations": int(match.get("cited_by_count") or 0),
            "open_access": bool((match.get("open_access") or {}).get("is_oa")),
            "abstract": abstract_text(match.get("abstract_inverted_index")),
            "url": item["url"] if item["doi"] else (match.get("primary_location") or {}).get("landing_page_url") or item["url"],
            "sources": ["OpenAlex"],
        }
        merge_into(item, enrichment)
    for item in works:
        publication_date = normalize_publication_date(
            item.get("publication_date") or item.get("year")
        )
        item["publication_date"] = publication_date
        if publication_date:
            item["year"] = publication_date[:4]
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
    unique = merge_catalog(works)
    # Stable two-pass ordering: title for exact ties, then publication date.
    unique.sort(key=lambda item: normalized_title(item.get("title")))
    unique.sort(key=publication_sort_key, reverse=True)
    citations = sorted((int(item.get("citations") or 0) for item in unique), reverse=True)
    h_index = max((i for i, count in enumerate(citations, 1) if count >= i), default=0)
    sources = ["ORCID", "OpenAlex"]
    if scopus_enabled or any("Scopus" in (item.get("sources") or []) for item in unique):
        sources.insert(1, "Scopus")
    if any("Latindex" in (item.get("sources") or []) for item in unique):
        sources.append("Latindex")
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
