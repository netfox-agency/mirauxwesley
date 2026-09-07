#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vérifie les fichiers d'import Google Ads avant de les charger dans l'éditeur.

    python3 tools/verif-ads.py

Contrôle : numéros de téléphone dans le texte (interdits par Google, ils vont
dans l'asset d'appel), majuscules abusives, ponctuation répétée, termes
interdits, longueurs, titres identiques, mots-clés présents dans deux groupes,
exclusions qui bloqueraient un mot-clé actif, groupes orphelins.
"""
import csv, re, sys, os, collections

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ads-import')
TEL = re.compile(r'\b0\s?[1-9](?:[\s.\-]?\d{2}){4}\b')
CAPS = re.compile(r'\b[A-ZÀ-ÖØ-Þ]{5,}\b')      # sans re.I, sinon tout matche
PONCT = re.compile(r'!{2,}|\?{2,}')
MOTS = [r'\bn°\s?1\b', r'\bmeilleur', r'\bmoins cher', r'\bpas cher', r'\bclique']

def lire(n):
    return list(csv.DictReader(open(os.path.join(D, n), encoding='utf-8-sig')))

pb = []
ads = lire('WM-04-annonces-rsa.csv')
for r in ads:
    g = r['Ad Group']
    hs = [r[f'Headline {i}'] for i in range(1, 16) if r.get(f'Headline {i}')]
    ds = [r[f'Description {i}'] for i in range(1, 5) if r.get(f'Description {i}')]
    for c in hs + ds:
        if TEL.search(c):   pb.append(f'téléphone dans le texte · {g} · {c}')
        if CAPS.search(c):  pb.append(f'majuscules · {g} · {c}')
        if PONCT.search(c): pb.append(f'ponctuation répétée · {g} · {c}')
        for m in MOTS:
            if re.search(m, c, re.I): pb.append(f'terme interdit · {g} · {c}')
    dup = [k for k, v in collections.Counter(hs).items() if v > 1]
    if dup: pb.append(f'titres identiques · {g} · {dup}')
    pb += [f'titre {len(h)} car · {g} · {h}' for h in hs if len(h) > 30]
    pb += [f'description {len(x)} car · {g}' for x in ds if len(x) > 90]
    if len(hs) != 15 or len(ds) != 4:
        pb.append(f'{len(hs)} titres / {len(ds)} descriptions · {g}')

kw = lire('WM-03-mots-cles.csv')
seen = collections.defaultdict(set)
for k in kw: seen[(k['Keyword'], k['Match Type'])].add(k['Ad Group'])
pb += [f'mot-clé dans plusieurs groupes · {k}' for (k, _), g in seen.items() if len(g) > 1]

neg = [l.strip() for l in open(os.path.join(D, 'WM-05-mots-cles-negatifs.txt'),
                               encoding='utf-8') if l.strip()]
actifs = {k['Keyword'] for k in kw}
pb += [f'exclusion qui bloque un mot-clé actif · {n}' for n in neg
       if any(re.search(rf'\b{re.escape(n)}\b', a) for a in actifs)]

gk = {k['Ad Group'] for k in kw}; ga = {r['Ad Group'] for r in ads}
pb += [f'groupe sans annonce · {g}' for g in gk - ga]
pb += [f'groupe sans mot-clé · {g}' for g in ga - gk]

camps = lire('WM-01-campagnes.csv')
print(f"{sum(float(c['Budget']) for c in camps):.2f} €/jour · {len(camps)} campagnes · "
      f"{len(kw)} mots-clés · {len(ads)} annonces · {len(neg)} exclusions")
print(f"\n{len(pb)} problème(s)")
for x in pb: print(' -', x)
sys.exit(1 if pb else 0)
