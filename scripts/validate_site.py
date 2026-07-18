#!/usr/bin/env python3
"""Fail the update when publication cards are missing or hidden by default."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Counter(HTMLParser):
    def __init__(self):
        super().__init__(); self.cards = 0; self.abstracts = 0
    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        if tag == "article" and "publication-card" in classes: self.cards += 1
        if tag == "p" and "publication-abstract" in classes: self.abstracts += 1

publications = json.loads((ROOT / "data/publications.json").read_text(encoding="utf-8"))
expected = len(publications)
assert expected > 0, "The scientific catalogue is empty"
for relative in ("index.html", "en/index.html"):
    counter = Counter(); counter.feed((ROOT / relative).read_text(encoding="utf-8"))
    assert counter.cards == expected, f"{relative}: expected {expected} cards, found {counter.cards}"
    assert counter.abstracts == expected, f"{relative}: every card must include an abstract"
css = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")
assert not re.search(r"(?<!\.js-ready )\.publication-card\{display:none\}", css), "Cards must not be hidden without a JS-ready scope"
javascript = (ROOT / "assets/js/app.js").read_text(encoding="utf-8")
assert 'querySelectorAll("[data-year]")' not in javascript, "Publication data-year attributes must never be overwritten"
assert 'querySelectorAll("[data-current-year]")' in javascript, "Footer year must use its dedicated selector"
print(f"Validated {expected} visible publication cards in ES and EN")
