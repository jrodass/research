import json,html,re
from pathlib import Path
def icon(name):
 d={"file":'<svg viewBox="0 0 24 24"><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>',"quote":'<svg viewBox="0 0 24 24"><path d="M7 17H4a2 2 0 0 1-2-2v-3a7 7 0 0 1 7-7v3a4 4 0 0 0-4 4h2v5Zm13 0h-3a2 2 0 0 1-2-2v-3a7 7 0 0 1 7-7v3a4 4 0 0 0-4 4h2v5Z"/></svg>',"chart":'<svg viewBox="0 0 24 24"><path d="M4 20V10h4v10H4Zm6 0V4h4v16h-4Zm6 0v-7h4v7h-4Z"/></svg>',"percent":'<svg viewBox="0 0 24 24"><path d="m5 19 14-14"/><circle cx="7" cy="7" r="2"/><circle cx="17" cy="17" r="2"/></svg>',"target":'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/></svg>',"external":'<svg viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9"/><path d="M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6"/></svg>',"unlock":'<svg viewBox="0 0 24 24"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 7-2"/></svg>'}
 return d[name]
def u(p):return p.get("url") or (f"https://doi.org/{p['doi']}" if p.get("doi") else "https://orcid.org/0000-0001-6526-7740")
def card(p):
 doi=f'<a href="{html.escape(u(p))}" target="_blank">{icon("external")} DOI</a>' if p.get("doi") else f'<a href="{html.escape(u(p))}" target="_blank">{icon("external")} Source</a>'
 return f'<article class="publication-card" data-year="{html.escape(str(p["year"]))}"><h3><a href="{html.escape(u(p))}" target="_blank">{html.escape(p["title"])}</a></h3><div class="authors">{html.escape(p.get("authors","Jorge Rodas-Silva et al."))}</div><div class="publication-info"><span class="pub-badge">{html.escape(str(p["year"]))} · {html.escape(p["type"])}</span><span class="journal">{html.escape(p["journal"])}</span></div><div class="publication-actions">{doi}<a href="{html.escape(u(p))}" target="_blank">{icon("quote")} Cite</a></div></article>'
def metrics_block(m,en):
 return f'<div class="metrics-grid"><article class="metric"><div class="metric-head">{icon("file")}<span>{"Publications" if en else "Publicaciones"} (P)</span></div><strong id="publication-count">{m["publications"]}</strong></article><article class="metric"><div class="metric-head">{icon("quote")}<span>{"Recent displayed" if en else "Recientes visibles"}</span></div><strong>{m["recent_visible"]}</strong></article><article class="metric"><div class="metric-head">{icon("chart")}<span>{"Journal articles" if en else "Artículos de revista"}</span></div><strong>{m["journals"]}</strong></article><article class="metric"><div class="metric-head">{icon("percent")}<span>{"Conference works" if en else "Trabajos en congresos"}</span></div><strong>{m["conference_papers"]}</strong></article><article class="metric"><div class="metric-head">{icon("target")}<span>{"DOI links" if en else "Enlaces DOI"}</span></div><strong>{m["doi_links"]}</strong></article></div>'
def rebuild(pubs,metrics):
 for path,en in [(Path("index.html"),False),(Path("en/index.html"),True)]:
  s=path.read_text(encoding="utf-8")
  s=re.sub(r'<!--METRICS_START-->.*?<!--METRICS_END-->',"<!--METRICS_START-->"+metrics_block(metrics,en)+"<!--METRICS_END-->",s,flags=re.S)
  s=re.sub(r'<!--PUBLICATIONS_START-->.*?<!--PUBLICATIONS_END-->',"<!--PUBLICATIONS_START--><div class=\"publication-list\">"+"".join(card(p) for p in pubs)+"</div><!--PUBLICATIONS_END-->",s,flags=re.S)
  s=re.sub(r'<span>\\d+ (publications|publicaciones) ·',f'<span>{len(pubs)} '+('publications' if en else 'publicaciones')+' ·',s)
  path.write_text(s,encoding="utf-8")
