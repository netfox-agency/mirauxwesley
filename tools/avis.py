#!/usr/bin/env python3
"""Recupere les vrais avis de la fiche Google et ecrit avis.json.

    python3 tools/avis.py --cle AIza...        # ecrit avis.json
    python3 tools/avis.py --cle AIza... --voir # affiche sans ecrire

Pourquoi un script et pas un widget
-----------------------------------
Les widgets d'avis du marche (Elfsight, Trustindex...) chargent leur propre
JavaScript depuis leur serveur : une dependance tierce de plus sur la page
d'atterrissage de la publicite, un abonnement mensuel, souvent leur logo, et
un cookie a declarer. Ici on lit l'API au moment du build et on ecrit du HTML
statique : aucune requete tierce chez le visiteur, rien a declarer, et la page
reste aussi rapide qu'avant.

Ce que renvoie l'API
--------------------
L'API Places ne donne que **cinq avis au maximum**, ceux que Google juge les
plus pertinents. Le compte total et la note, eux, sont exacts. On affiche donc
cinq avis et on renvoie vers la fiche pour les autres.

Conditions d'utilisation
------------------------
Google demande que les avis affiches soient attribues a Google et renvoient
vers la fiche : c'est fait dans le rendu. Le contenu ne doit pas etre conserve
plus de 30 jours, donc **ce script doit tourner au moins une fois par mois**,
sinon les avis affiches ne sont plus a jour ni conformes.

La cle
------
Console Google Cloud > APIs & Services > Credentials > Create API key, puis
activer « Places API (New) ». La restreindre a cette seule API. Elle n'apparait
jamais dans le site genere : elle ne sert qu'ici, au moment du build.
"""
import argparse
import datetime
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

RACINE = pathlib.Path(__file__).resolve().parent.parent
SORTIE = RACINE / "avis.json"

# Ce qu'on cherche. Le nom de la fiche est volontairement celui qui est
# affiche sur Google aujourd'hui, mots-cles compris, sinon la recherche ne
# retombe pas dessus.
REQUETE = "Couvreur Nonancourt Wm-couverture"
BIAIS = (48.7632745, 1.2240144)
FICHE = "https://maps.google.com/?cid=17637010817244759536"


def appel(url, entetes, corps=None):
    donnees = json.dumps(corps).encode() if corps is not None else None
    req = urllib.request.Request(url, data=donnees, headers=entetes,
                                 method="POST" if corps is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:400]
        sys.exit(f"L'API a refuse ({e.code}) :\n{detail}\n\n"
                 "Causes habituelles : « Places API (New) » pas activee sur le "
                 "projet, ou cle restreinte a une autre API.")


def trouver_fiche(cle):
    """Le lien de la fiche porte un identifiant de graphe (/g/...), pas
    l'identifiant Places attendu par l'API. On le retrouve par recherche."""
    r = appel(
        "https://places.googleapis.com/v1/places:searchText",
        {"Content-Type": "application/json", "X-Goog-Api-Key": cle,
         "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress"},
        {"textQuery": REQUETE, "languageCode": "fr",
         "locationBias": {"circle": {"center": {"latitude": BIAIS[0],
                                                "longitude": BIAIS[1]},
                                     "radius": 2000.0}}})
    lieux = r.get("places") or []
    if not lieux:
        sys.exit(f"Aucune fiche trouvee pour « {REQUETE} ».")
    if len(lieux) > 1:
        print(f"  {len(lieux)} fiches trouvees, on prend la premiere :")
        for p in lieux[:3]:
            print(f"    - {p['displayName']['text']} · {p.get('formattedAddress','')}")
    return lieux[0]["id"]


def details(cle, place_id):
    return appel(
        f"https://places.googleapis.com/v1/places/{place_id}?languageCode=fr",
        {"X-Goog-Api-Key": cle,
         "X-Goog-FieldMask": "id,displayName,rating,userRatingCount,reviews,googleMapsUri"})


def initiale(nom):
    for c in nom.strip():
        if c.isalpha():
            return c.upper()
    return "?"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cle", default=os.environ.get("GOOGLE_PLACES_KEY"),
                    help="cle API Places (ou variable GOOGLE_PLACES_KEY)")
    ap.add_argument("--voir", action="store_true", help="affiche sans ecrire")
    a = ap.parse_args()
    if not a.cle:
        sys.exit("Il manque la cle : --cle AIza... ou GOOGLE_PLACES_KEY=...\n"
                 "Voir l'en-tete de ce fichier pour l'obtenir.")

    print("Recherche de la fiche...")
    pid = trouver_fiche(a.cle)
    print(f"  identifiant Places : {pid}")

    d = details(a.cle, pid)
    note = d.get("rating")
    total = d.get("userRatingCount")
    bruts = d.get("reviews") or []
    print(f"  {d['displayName']['text']} · {note} sur {total} avis · "
          f"{len(bruts)} avis renvoyes par l'API")

    avis = []
    for r in bruts:
        texte = (r.get("originalText") or r.get("text") or {}).get("text", "").strip()
        nom = (r.get("authorAttribution") or {}).get("displayName", "").strip()
        if not texte or not nom:
            continue
        avis.append({
            "auteur": nom,
            "initiale": initiale(nom),
            "note": r.get("rating", 5),
            "quand": r.get("relativePublishTimeDescription", ""),
            "texte": texte,
        })

    if not avis:
        sys.exit("L'API n'a renvoye aucun avis exploitable. avis.json non modifie.")

    data = {
        "_lisez_moi": ("Genere par tools/avis.py depuis l'API Google Places. "
                       "Ne pas editer a la main : la prochaine execution ecrase. "
                       "A relancer au moins une fois par mois (conditions Google)."),
        "recupere_le": datetime.date.today().isoformat(),
        "fiche": d.get("googleMapsUri") or FICHE,
        "note": note,
        "total": total,
        "source": "google_places_api",
        "avis": avis,
    }

    if a.voir:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    SORTIE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(f"\navis.json ecrit : {note} sur {total} avis, {len(avis)} affichables.")
    print("Puis : python3 build.py && python3 tools/images.py --keep")
    return 0


if __name__ == "__main__":
    sys.exit(main())
