# Plan de bataille SEO local · WM Couverture

Objectif : première position dans le pack local (les trois fiches avec la carte)
et dans les résultats classiques, sur le secteur Nonancourt / Dreux / Évreux.

Ce document sépare **ce qui est déjà fait dans le site** de **ce que seul WM peut
faire**. La deuxième liste pèse plus lourd que la première : le site représente
environ 15 à 19 % des signaux du pack local, la fiche Google 32 % et les avis 20 %.

---

## 1. Ce que seul WM peut faire (le plus gros de la note)

### 1.1 La catégorie principale de la fiche Google

C'est **le premier facteur de classement du pack local**, et une mauvaise
catégorie est le pire réglage possible.

- Catégorie principale : **Couvreur** (`Roofing contractor`).
- Catégories secondaires, dans cet ordre :
  `Entreprise de couverture`, `Charpentier`, `Entreprise de nettoyage`,
  `Entrepreneur en isolation`, `Entreprise de rénovation`.
- Ne pas mettre `Entreprise de construction` en principale : trop large, elle
  fait perdre les requêtes « couvreur ».

### 1.2 Le nom de la fiche

Deuxième facteur du pack. Le nom doit rester le nom réel de l'entreprise, mais
Google tolère la mention du métier quand elle figure sur l'enseigne et les devis.

- Nom recommandé : **WM Couverture**
- Si l'enseigne le porte réellement : `WM Couverture · Couvreur à Nonancourt`
- Ne jamais bourrer de villes (`WM Couverture Dreux Évreux Verneuil`) : c'est un
  motif de suspension, pas un raccourci.

### 1.3 Les avis, deuxième bloc de signaux

Deux règles issues des études les plus récentes :

- **Seuil des 10 avis** : le saut de 9 à 10 avis produit une hausse visible de
  classement. Passer de 10 à 11 n'apporte plus le même bond.
- **Règle des 18 jours** : sans nouvel avis pendant environ trois semaines, les
  positions décrochent. C'est la **régularité** qui compte, pas le total.

Objectif concret : **deux à quatre nouveaux avis Google par mois, tous les mois**,
indéfiniment. Pas de campagne d'un coup puis plus rien.

Méthode, à appliquer à chaque fin de chantier :

1. Le jour de la réception, sur place, montrer le toit fini au client.
2. Envoyer un SMS dans l'heure, tant que la satisfaction est fraîche :

   > Bonjour [prénom], merci de nous avoir fait confiance pour votre toiture.
   > Si le travail vous a plu, un avis Google nous aide vraiment : [lien court]
   > Merci beaucoup. WM Couverture

3. Créer le lien court depuis la fiche : *Demander des avis* → copier le lien.
4. **Répondre à 100 % des avis**, en moins de 48 h, en nommant la prestation et
   la commune : « Merci [prénom]. Content que la réfection de la toiture à
   [commune] vous convienne. » Cela nourrit la pertinence sémantique locale.
5. **Ne jamais filtrer** : demander l'avis seulement aux clients contents est
   interdit par Google et par la réglementation sur les avis en ligne.

### 1.4 Les photos de la fiche

- Ajouter des photos **régulièrement**, pas 40 d'un coup. Une par chantier suffit.
- Photos utiles : avant/après, l'équipe au travail, le camion, l'atelier.
- Le géotaggage des photos n'a **aucun effet** sur le classement. Inutile de payer
  un outil pour ça.

### 1.5 Le menu Services de la fiche

Recopier les quatre prestations du site, avec la même formulation :

| Service | Description courte |
|---|---|
| Rénovation de toiture | Dépose, charpente, écran de sous-toiture, couverture neuve. |
| Zinguerie et gouttières | Gouttières, chéneaux, solins, rives, isolation sous toiture. |
| Nettoyage et démoussage | Nettoyage haute pression et traitement anti-mousse. |
| Dépannage et urgence | Fuite, tuiles arrachées, bâchage, mise hors d'eau 24 h/24. |

### 1.6 Les autres fiches à créer

Trois des cinq premiers facteurs de visibilité dans les moteurs IA sont liés aux
citations. Et ChatGPT ne lit pas Google : il s'appuie sur l'index Bing.

Par ordre d'utilité :

1. **Bing Places** (indispensable : alimente ChatGPT, Copilot, Alexa).
2. **Apple Business Connect** (l'usage d'Apple Plans a doublé en un an).
3. **PagesJaunes**, **Facebook**, **Yelp**.
4. Annuaires bâtiment : Houzz, Travaux.com, Quotatis.

**La règle absolue : le NAP identique partout, au caractère près.**

```
WM Couverture
Route de Saint-Remy
27320 Nonancourt
06 24 59 26 77
```

Pas de « Rte de Saint-Rémy », pas de « 06.24.59.26.77 », pas de second numéro.

### 1.7 Horaires

« Ouvert au moment de la recherche » est un facteur de classement confirmé.
Les horaires 8 h - 21 h, sept jours sur sept, sont déjà un avantage sur les
concurrents fermés le week-end : **ils doivent être exacts sur la fiche**, et les
jours fériés renseignés.

---

## 2. Ce qui est déjà fait dans le site

| Levier | État |
|---|---|
| Pages service dédiées (facteur de classement direct) | 4 pages, 850 à 950 mots chacune |
| Pages commune à contenu unique | 12 pages, 580 à 640 mots, bâti local décrit |
| Guides informationnels | 5 guides de 900 à 1 200 mots + un hub, avec bloc « En bref » citable |
| Calculateur de surface de rampant | sur le guide prix, aimant à liens et à partages |
| Balisage `RoofingContractor` complet | geo, horaires, `areaServed` sur 24 communes, `hasOfferCatalog` |
| Fil d'Ariane balisé | `BreadcrumbList` sur toutes les pages internes |
| NAP identique sur chaque page | pied de page + balisage |
| Maillage interne | services ↔ communes croisés, index des communes lié depuis l'accueil |
| Redirections 301 des anciennes URLs | `_redirects` et `.htaccess` |
| `sitemap.xml`, `robots.txt` | générés, avec `lastmod` |
| Crawlers IA autorisés | GPTBot, PerplexityBot, ClaudeBot, Applebot, CCBot |
| `llms.txt` | résumé structuré pour les moteurs génératifs |
| Images | AVIF + WebP, 5 largeurs, `srcset` |
| Polices | auto-hébergées, plus aucun blocage de rendu par un tiers |

---

## 3. Réglages à faire avant la mise en ligne

1. **Coordonnées GPS** : `GEO_LAT` et `GEO_LON` dans `build.py` sont approximatives.
   Les caler exactement sur l'épingle de la fiche Google, cinq décimales minimum.
   La proximité explique à elle seule plus de la moitié du classement dans le pack.
2. **`SAMEAS`** dans `build.py` : y mettre l'URL de la fiche Google, du Facebook et
   des autres profils une fois créés. Laisser vide tant qu'on ne les a pas.
3. **`aggregateRating`** : à ajouter au balisage seulement quand la note et le
   nombre d'avis affichés sur la fiche sont connus. Ne jamais inventer.
4. **Search Console et Bing Webmaster Tools** : vérifier le domaine, envoyer le
   sitemap, demander l'indexation des 23 pages le jour de la bascule.
5. **Vérifier les 301** après le changement de DNS, une URL à la fois.

---

## 4. Ce qu'il faut surveiller, et à quelle fréquence

| Indicateur | Où | Rythme | Seuil d'alerte |
|---|---|---|---|
| Nouveaux avis Google | Fiche | chaque semaine | plus de 18 jours sans avis |
| Appels depuis la fiche | Statistiques GBP | chaque mois | baisse deux mois de suite |
| Position sur « couvreur + commune » | recherche en navigation privée | chaque mois | sortie du top 3 |
| Pages indexées | Search Console | chaque mois | moins de 23 |
| Cohérence du NAP | recherche du numéro entre guillemets | chaque trimestre | toute variante trouvée |

---

## 5. Comment on saura que ça n'a pas marché

À poser franchement, parce qu'un plan sans critère d'échec ne vaut rien :

- **Trois mois après la mise en ligne**, si les pages commune ne rapportent aucune
  impression dans la Search Console, c'est que le contenu local n'est pas jugé
  assez distinctif. Correctif : ajouter à chaque page une réalisation réelle
  photographiée dans la commune.
- **Si la fiche ne progresse pas** alors que les avis rentrent au rythme prévu,
  le frein est la proximité : hors du rayon de quelques kilomètres autour de
  Nonancourt, aucune optimisation ne compense la distance. Le relais devient
  alors le référencement classique, où les pages commune travaillent, elles.
- **Si les guides prennent des impressions sans clics**, le titre ou la description
  ne correspondent pas à la question posée. Correctif : réécrire le bloc « En bref »
  pour qu'il réponde en une phrase, et aligner la description dessus.
- **Si le trafic monte sans que le téléphone sonne**, le problème n'est pas le
  SEO mais la page : revoir l'accroche et la position du numéro.
