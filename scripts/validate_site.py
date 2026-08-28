#!/usr/bin/env python3
"""Fail the update when publication cards are missing or hidden by default."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Counter(HTMLParser):
    def __init__(self):
        super().__init__(); self.cards = 0; self.abstracts = 0; self.featured = 0
    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        if tag == "article" and "publication-card" in classes: self.cards += 1
        if tag == "article" and "featured-publication" in classes: self.featured += 1
        if tag == "p" and "publication-abstract" in classes: self.abstracts += 1

publications = json.loads((ROOT / "data/publications.json").read_text(encoding="utf-8"))
expected = len(publications)
assert expected > 0, "The scientific catalogue is empty"
assert all(item.get("summary_es") and item.get("summary_en") for item in publications), "Every publication requires ES and EN summaries"
for relative in ("index.html", "en/index.html"):
    counter = Counter(); counter.feed((ROOT / relative).read_text(encoding="utf-8"))
    assert counter.cards == expected, f"{relative}: expected {expected} cards, found {counter.cards}"
    assert counter.abstracts == expected, f"{relative}: every card must include an abstract"
    assert counter.featured == min(3, expected), f"{relative}: expected three recent featured publications"
    source=(ROOT / relative).read_text(encoding="utf-8")
    assert 'id="research"' in source, f"{relative}: research section is missing"
    assert source.count('data-topic-filter=') == 6, f"{relative}: expected six research filters"
    section_order = [source.index(f'id="{section}"') for section in ("impact", "publications", "research", "publication-catalogue", "experience")]
    assert section_order == sorted(section_order), f"{relative}: research-first section hierarchy is incorrect"
    assert source.count('class="metric metric-primary"') == 4, f"{relative}: expected four primary impact metrics"
    assert 'class="secondary-metrics"' in source, f"{relative}: complementary metrics must remain available"
    assert "Actualización automática" not in source and "Automatic update" not in source, f"{relative}: automation must not appear as a headline metric"
css = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")
assert "--max:1200px" in css, "Desktop content must remain centered in a 1200px container"
assert ".container{width:min(calc(100% - 64px),var(--max));margin-inline:auto}" in css, "Desktop container must preserve balanced side margins"
assert not re.search(r"(?<!\.js-ready )\.publication-card\{display:none\}", css), "Cards must not be hidden without a JS-ready scope"
assert ".publication-list{min-height:820px}" not in css, "Filtered result lists must shrink to their content"
assert ".publication-list{min-height:0!important;height:auto!important;align-content:start;grid-auto-rows:max-content}" in css, "Publication grid must use content-sized rows"
assert ".featured-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}" in css, "Recent publications must use a three-column desktop grid"
javascript = (ROOT / "assets/js/app.js").read_text(encoding="utf-8")
assert 'querySelectorAll("[data-year]")' not in javascript, "Publication data-year attributes must never be overwritten"
assert 'querySelectorAll("[data-current-year]")' in javascript, "Footer year must use its dedicated selector"
assert 'gridAutoRows="max-content"' in javascript, "Filtered cards must use content-sized grid rows"
assert 'data-topic-filter' in javascript and 'dataset.topics' in javascript, "Research cards must filter publications by topic"
assert 'querySelector("#publication-catalogue")' in javascript, "Topic filters must open the full catalogue"
rebuild = (ROOT / "scripts/rebuild_site.py").read_text(encoding="utf-8")
assert 'pubs[:3]' in rebuild and 'featured-publications' in rebuild, "Recent publications must rebuild automatically"
print(f"Validated {expected} visible publication cards in ES and EN")
