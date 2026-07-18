import html,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def icon(name):
    icons={
      "external":'<svg viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9"/><path d="M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6"/></svg>',
      "quote":'<svg viewBox="0 0 24 24"><path d="M7 17H4a2 2 0 0 1-2-2v-3a7 7 0 0 1 7-7v3a4 4 0 0 0-4 4h2v5Zm13 0h-3a2 2 0 0 1-2-2v-3a7 7 0 0 1 7-7v3a4 4 0 0 0-4 4h2v5Z"/></svg>'
    }
    return icons[name]

def url(p):
    return p.get("url") or (f"https://doi.org/{p['doi']}" if p.get("doi") else "https://orcid.org/0000-0001-6526-7740")

def author_html(line):
    text=html.escape(line or "Jorge Rodas-Silva et al.")
    return text.replace("Jorge Rodas-Silva","<strong>Jorge Rodas-Silva</strong>")

def card(p,lang):
    source="DOI" if p.get("doi") else ("Source" if lang=="en" else "Fuente")
    return f'<article class="publication-card" data-year="{html.escape(str(p.get("year","")))}"><h3><a href="{html.escape(url(p))}" target="_blank" rel="noopener">{html.escape(p.get("title",""))}</a></h3><div class="authors">{author_html(p.get("authors",""))}</div><div class="publication-info"><span class="pub-badge">{html.escape(str(p.get("year","—")))} · {html.escape(p.get("type","Publication"))}</span><span class="journal">{html.escape(p.get("journal") or "Academic publication")}</span></div><div class="publication-actions"><a href="{html.escape(url(p))}" target="_blank" rel="noopener">{icon("external")} {source}</a><a href="{html.escape(url(p))}" target="_blank" rel="noopener">{icon("quote")} {"Cite" if lang=="en" else "Citar"}</a></div></article>'

def rebuild(pubs,metrics):
    for path,lang in [(ROOT/"index.html","es"),(ROOT/"en/index.html","en")]:
        s=path.read_text(encoding="utf-8")
        cards="".join(card(p,lang) for p in pubs)
        s=re.sub(r'(<div id="publication-list" class="publication-list">).*?(</div>\s*<nav class="pagination")',lambda m:m.group(1)+cards+m.group(2),s,flags=re.S)
        s=re.sub(r'(<strong id="visible-total">)\d+(</strong>)',rf'\g<1>{len(pubs)}\g<2>',s)
        s=re.sub(r'(<strong id="filtered-count">)\d+(</strong>)',rf'\g<1>{len(pubs)}\g<2>',s)
        for key,value in metrics.items():
            s=re.sub(rf'(<strong data-metric="{re.escape(key)}">).*?(</strong>)',lambda m:f'{m.group(1)}{html.escape(str(value))}{m.group(2)}',s)
        path.write_text(s,encoding="utf-8")
