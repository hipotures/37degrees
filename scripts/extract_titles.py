#!/usr/bin/env python3
# plik: extract_titles.py
import re, sys, io

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/snap.yaml"

with io.open(path, "r", encoding="utf-8") as f:
    text = f.read()

# linie typu: - generic [ref=e185]: "Jądro Ciemności: …"
rx = re.compile(r'^\s*-\s*generic\s*\[ref=[^\]]+\]:\s*"([^"]+)"\s*$', re.MULTILINE)

candidates = rx.findall(text)

# odfiltruj oczywiste etykiety nie-będące tytułem
ban = {"Share","Settings","Sources","Chat","Studio","Analytics","PRO",
       "Audio Overview","Video Overview","Mind Map","Reports","Flashcards","Quiz"}
titles = []
seen = set()
for s in candidates:
    if s in ban: 
        continue
    if "Deep dive" in s or "source" in s or "Play" in s or "More" in s:
        continue
    if len(s) < 15:  # krótkie etykiety pomiń
        continue
    if s not in seen:
        seen.add(s)
        titles.append(s)

for t in titles:
    print(t)

