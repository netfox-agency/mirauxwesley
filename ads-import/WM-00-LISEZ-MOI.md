# ⚠️ Ces CSV sont PÉRIMÉS — ne pas les importer

Le 16/09/2026, la structure a été créée **directement dans le compte**
`8973082946` (Miraux Wesley), par `~/ads-write/creer-campagnes-wm.py`.

**Importer ces fichiers créerait tout en double.**

Ils sont gardés uniquement comme trace de la première version du plan.

## Ce qui est réellement en ligne dans le compte

| | |
|---|---|
| 4 campagnes | Appels-Couvreur (5,00 €/j) · Entretien-Toiture (3,50) · Gros-Chantiers (2,55) · Marque (1,00) |
| État | **toutes en PAUSED** |
| 8 groupes | 216 mots-clés, tous en correspondance EXPRESSION |
| 8 annonces | 15 titres et 4 descriptions chacune |
| 120 exclusions | réparties en 7 listes partagées |
| Extensions | 1 appel · 6 liens annexes · 6 accroches · 1 bloc d'extraits |
| Conversions | devis (200 €) · appel site (100 €) · appel annonces (100 €, ≥ 30 s) |

La campagne **Marque** n'est pas du confort : l'ancien site de l'agence
précédente reste en ligne sur `wm-couverture.fr` et sort premier sur
« WM Couverture ». Une annonce passe au-dessus du naturel. C'est le seul
levier direct contre lui, et il coûte un euro par jour.

## Ce qui bloque l'activation

1. **Facturation** : `billing_setup` est en `PENDING`. Rien ne peut diffuser.
2. Lien du site à changer dans la fiche Google vers `wmcouverture.fr`.

Une fois débloqué, n'ouvrir que **Appels-Couvreur**, **Entretien-Toiture** et
**Marque** (9,50 €/j). Gros-Chantiers attend le mois 2 : sans historique de
conversion, un clic à 5 € mange un tiers du budget du jour pour rien.

## Modifier la structure

```bash
cd ~/ads-write && ./.venv/bin/python creer-campagnes-wm.py 8973082946
```

Sans `--appliquer`, rien n'est écrit : chaque opération est résolue contre le
compte réel, donc une faute de nom sort en simulation et pas en production.
