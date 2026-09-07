# WM Couverture · refonte du site (Nonancourt, 27)

Refonte statique de [wm-couverture.fr](https://www.wm-couverture.fr/) : onze pages
générées, sans framework ni bundler. Uniquement du HTML, du CSS et un fichier JS
de 300 lignes, plus deux scripts Python de génération.

## Construire

```bash
python3 build.py          # pages service + commune, sitemap, robots, redirections
python3 tools/images.py   # déclinaisons AVIF/WebP + <picture> dans toutes les pages
python3 -m http.server 4207
```

- `build.py` génère les 10 pages internes. **Elles ne s'éditent jamais à la main**,
  elles sont écrasées à chaque build. Le contenu vit dans les listes `SERVICES` et
  `VILLES` en tête du fichier, avec les constantes (téléphone, domaine, clé Web3Forms).
- `index.html` et `mentions-legales.html` s'éditent à la main.
- `tools/images.py` recrée `assets/img/r/` (5 largeurs × AVIF + WebP) et réécrit les
  `<img>` en `<picture>` avec `srcset`/`sizes`. Option `--keep` pour ne pas
  réencoder les images et seulement recâbler le HTML.
- Entrée `wm-couverture-refonte` dans `.claude/launch.json`, port 4207.

## Arborescence

34 pages indexables, environ 28 100 mots.

| Type | Pages | Mots | Images |
|---|---|---|---|
| Accueil | 1 | 1 020 | 23 |
| **Pages métier** | **9** | 8 340 | 9 |
| Pages commune | 12 | 8 130 | 12 |
| Guides + hub | 11 | 10 600 | **10** |
| Plan du site, 404, mentions | 3 | | |

**Métiers** : rénovation de toiture · zinguerie et gouttières · nettoyage et
démoussage · dépannage et urgence · **charpente** · **isolation de toiture** ·
**recherche de fuite** · **fenêtre de toit** · **bardage**.

Les cinq derniers ont été ajoutés après constat : « charpente » était citée
340 fois sur le site, « isolation » 244, « solins » 66, « velux » 48, sans
aucune page dédiée. Chacune de ces prestations est une intention de recherche
distincte, et les pages service dédiées comptent parmi les facteurs de
classement du pack local.

**Communes** : Nonancourt, Dreux, Vernouillet, Saint-Rémy-sur-Avre, Anet,
Ivry-la-Bataille, Verneuil d'Avre et d'Iton, Tillières-sur-Avre, Brezolles,
Nogent-le-Roi, Breteuil, Évreux.

**Guides** : prix d'une réfection (avec calculateur de surface de rampant),
fuite de toiture, démoussage, aides et TVA, autorisation d'urbanisme, quelle
tuile choisir, isoler sa toiture, tempête et assurance, entretien annuel,
fenêtre de toit.

Chaque guide porte désormais son propre bandeau illustré. **Pas de service ×
ville** : ce serait 108 pages quasi identiques, traitées comme des pages
satellites.

Chaque page porte son `title` (60 caractères maximum), sa `meta description`
(120 à 158), son fil d'Ariane, son JSON-LD et un maillage croisé. Aucun titre
ni aucune description n'est dupliqué sur les 34 pages.

### Prestations volontairement sans page

`hydrofuge de toiture` et `étanchéité de toit plat` sont de bons mots-clés, mais
le site actuel de WM ne dit nulle part qu'il les propose. Pas de page pour une
prestation invérifiable. Deux pages à créer en une heure si Wesley confirme.

## Les trois intentions couvertes

| Intention | Ce que tape la personne | Où elle atterrit |
|---|---|---|
| Transactionnelle | « couvreur Dreux », « démoussage toiture prix » | page service, page commune |
| Locale | « couvreur près de moi », recherche sur Maps | fiche Google, puis page commune |
| Informationnelle | « prix réfection toiture au m2 », « fuite toiture que faire » | guide, qui renvoie vers la page service |

Les guides ne sont pas du remplissage : ce sont eux qui captent le volume, et
surtout ce sont les passages qu'un moteur génératif cite. Chacun s'ouvre sur un
bloc **En bref** de trois à quatre phrases qui répond directement à la question,
suivi des sections détaillées. C'est ce bloc que Google reprend en extrait et que
ChatGPT ou Perplexity citent.

Le guide sur le prix embarque un **calculateur de surface de rampant** : l'internaute
saisit l'emprise au sol et la pente, il obtient la surface réelle du toit. Aucun prix
n'est affiché, parce que nous n'en inventons pas. C'est le chiffre qui manque à tout
le monde pour comparer deux devis, et c'est le genre de page qui attire des liens.

Trois mécanismes relient ce trafic aux pages qui vendent :

1. **Des liens contextuels dans le corps du texte.** Chaque guide renvoie vers la
   page service concernée depuis l'intérieur d'un paragraphe, là où le lien a le plus
   de poids et où le lecteur est le plus disposé à cliquer.
2. **Un bloc de rattrapage local** en fin de guide : « nous intervenons dans l'Eure
   et le Drouais », avec les huit communes principales. Le trafic informationnel est
   national, ce bloc attrape ceux qui sont dans la zone.
3. **Un maillage guides ↔ guides** qui garde le lecteur sur le site quand sa question
   en appelle une autre, ce qui est le cas en permanence sur un sujet de toiture.

## Accessibilité, mesurée et corrigée

L'accessibilité est le premier poste de qualité du référentiel métier, et c'est aussi
du chiffre d'affaires : la clientèle d'un couvreur est âgée, elle lit sur téléphone,
souvent dehors.

Un audit automatisé sur les 25 pages a trouvé et corrigé :

- **Sept échecs de contraste WCAG AA.** Le gris de texte était à 3,91:1 et le laiton
  à 3,23:1 sur le papier, pour un minimum de 4,5:1. Deux nouveaux jetons :
  `--muted` passe à `#5D676D` (5,13:1) et un `--brass-ink` `#8A5E1E` (5,03:1) prend
  en charge tous les usages **texte** du laiton. Le `--brass` d'origine reste pour
  les traits, les fonds et les remplissages, où le seuil est de 3:1.
- **Le bouton laiton** était en blanc sur laiton, 3,64:1. Il passe en encre sur
  laiton, 4,68:1, et gagne au passage en lisibilité sur les bandes sombres.
- **Toutes les cibles tactiles sous 44 px** : liens de pied de page à 18 px, fil
  d'Ariane, index des communes, coordonnées. Corrigé par des paddings sous media
  query, sans toucher au rendu desktop.
- **Mouvement réduit** : la pastille qui pulse, le bandeau défilant, le zoom lent du
  hero et l'ouverture du menu sont désormais coupés sous `prefers-reduced-motion`.

État après correction, sur les 25 pages : **zéro échec de contraste, zéro cible
tactile insuffisante, zéro saut de niveau de titre, un seul H1 par page, zéro image
sans attribut alt, zéro champ sans étiquette.**

## Ce qui n'est pas fait, et pourquoi

Trois volets du référencement restent ouverts. Aucun n'est un oubli : ils dépendent
de données ou d'accès que nous n'avons pas encore.

**1. Aucune donnée de volume de recherche.** Le choix des mots-clés repose sur la
connaissance du métier et de la zone, pas sur des volumes mesurés. Aucune source de
données (Search Console, Ahrefs, DataForSEO, SE Ranking) n'est connectée. Conséquence
possible : un guide sur-investi pour peu de volume, ou une requête forte oubliée. Se
corrige en trois jours dès qu'un accès est branché.

**2. Aucun travail de netlinking.** Les liens entrants pèsent peu dans le pack local
mais comptent en organique. Ils s'obtiennent, ils ne se codent pas. Pistes réelles
pour un couvreur : fabricants de tuiles et fournisseurs (page « nos poseurs »),
organisations professionnelles, sites de communes, partenaires locaux, presse locale
sur un chantier notable.

**3. Aucune mesure possible avant la mise en ligne.** Position, impressions, Core Web
Vitals de terrain, taux de clic : tout cela demande un site en production et une
Search Console. Le premier vrai bilan se fait six à huit semaines après la bascule.

En revanche, le poids de la page d'accueil est mesuré : **320 Ko et 13 requêtes**,
DOM prêt en 154 ms, décalage de mise en page nul. Il n'y a pas de gain de performance
significatif à aller chercher.

## Ce que dit le SERP réel

**[SEO-REALITE-SERP.md](SEO-REALITE-SERP.md)** : relevé des résultats Google réels
sur les requêtes cibles, et ce que cela invalide. Deux conclusions structurantes.

« Couvreur Dreux » n'est pas gagnable à court terme : en face, des entreprises
implantées depuis 15 à 44 ans avec 71 à 245 avis Google, dans Dreux même. Le terrain
réellement gagnable est le rayon immédiat autour de Nonancourt. Sur Dreux, la voie
rapide est de figurer dans les annuaires que Google affiche lui-même.

Sur « prix réfection toiture », toutes les pages classées donnent une fourchette
chiffrée. Le guide n'en donnait aucune, donc il ne répondait pas à l'intention. Il
publie désormais les fourchettes du marché, sourcées et nommées, en précisant que ce
ne sont pas nos tarifs.

## SEO local

Le plan complet est dans **[SEO-LOCAL.md](SEO-LOCAL.md)** : ce que fait le site,
et surtout ce que seul WM peut faire (catégorie de la fiche Google, avis, NAP,
autres annuaires). Le site pèse environ 15 à 19 % des signaux du pack local, la
fiche Google 32 % et les avis 20 %.

Côté code, en place :

- balisage `RoofingContractor` complet, partagé par `@id` entre toutes les pages :
  `geo`, `openingHoursSpecification`, `areaServed` sur 24 communes, `hasOfferCatalog`,
  `priceRange`, `hasMap` ;
- `WebSite`, `WebPage`, `FAQPage` sur l'accueil, `Service` + `FAQPage` +
  `BreadcrumbList` sur les pages service, `BreadcrumbList` sur les pages commune ;
- NAP identique au caractère près sur chaque page et dans le balisage ;
- `robots.txt` autorisant explicitement GPTBot, PerplexityBot, ClaudeBot, Applebot
  et CCBot, plus un `llms.txt` structuré : ChatGPT ne lit pas la fiche Google, il
  passe par l'index Bing et les citations ;
- `sitemap.xml` avec `lastmod` et priorités ;
- redirections 301 des six anciennes URLs WordPress dans `_redirects` et `.htaccess` ;
- images en AVIF et WebP sur cinq largeurs, polices auto-hébergées, aucun appel
  à un tiers au chargement.

## ⚠️ À faire avant la mise en ligne

1. **Clé Web3Forms** : remplacer `REMPLACER_PAR_VOTRE_CLE_WEB3FORMS` dans
   `index.html` **et** dans la constante `W3F_KEY` de `build.py`, puis rebuild.
   Tant que le placeholder est là, le formulaire renvoie vers le téléphone.
2. **Mentions légales** : SIRET, forme juridique, TVA, responsable de publication,
   e-mail, assurance décennale, hébergeur.
3. **Coordonnées GPS** : `GEO_LAT` et `GEO_LON` dans `build.py` sont approximatives.
   Les caler sur l'épingle exacte de la fiche Google. La proximité explique à elle
   seule plus de la moitié du classement dans le pack local.
4. **`SAMEAS`** dans `build.py` : URL de la fiche Google et des autres profils, une
   fois créés. Laisser vide plutôt que d'y mettre une URL approximative.
5. **`aggregateRating`** : à ajouter seulement quand la note et le nombre d'avis
   réels sont connus.
6. **Search Console et Bing Webmaster Tools** : vérifier le domaine, envoyer le
   sitemap, demander l’indexation des 23 pages le jour de la bascule.
7. **Vérifier les 301** après le changement de DNS, une URL à la fois.

À faire valider par l'artisan : la zone d'intervention, la description du bâti de
chaque commune, et les contraintes d'urbanisme évoquées (secteurs protégés d'Anet
et de Verneuil).

## Contenu

Toutes les informations viennent de l'ancien site : téléphone 06 24 59 26 77,
route de Saint-Remy à Nonancourt, 8 h à 21 h tous les jours, dépannage 24 h/24,
14 ans d'expérience, entreprise familiale de père en fils, devis gratuit,
paiement en plusieurs fois. Les cinq avis sont recopiés mot pour mot depuis
la page d'accueil. Rien n'a été inventé : aucune certification, aucun label,
aucun prix.

La zone d'intervention (24 communes de l'Eure et de l'Eure-et-Loir) est une
proposition cohérente avec l'implantation, **à faire valider par l'artisan**.

## Photos

**Preuve : les photos du client.** Les visuels de chantier viennent de son propre
site (récupérés via l'API REST WordPress), recadrés et réencodés en webp. Ce sont
eux qui portent la galerie, l'avant / après et le hero.

Le couple avant / après (`avant-longere.webp` et `apres-longere.webp`) est la même
longère, recadrée pour que la ligne de toit coïncide de part et d'autre de la
poignée du comparateur.

**Illustration : quatre photos Pexels** (libres, sans attribution obligatoire),
choisies pour ce projet uniquement, jamais utilisées sur un autre site de l'agence :

| Fichier | Pexels | Usage |
|---|---|---|
| `amb-charpente.webp` | 31763539 | second visuel du chapitre 01 |
| `zinguerie-descente.webp` | 25682676 | bandeau du chapitre 02 |
| `amb-combles.webp` | 9043415 | galerie, combles avant isolation |
| `amb-toits.webp` | 19808100 | fond de la bande citation |

À remplacer par des photos de WM dès qu'il en fournit d'équivalentes.

## Parti pris visuel

Papier chaux `#F4F1EA`, encre `#14181B`, ardoise `#182229` pour les bandes sombres,
laiton `#B07C2E` en accent. Archivo pour les titres, Instrument Serif en italique sur
les mots porteurs, Inter Tight pour le texte.

Règles tenues pour éviter le rendu « template » :

- **aucun bloc de cartes répété** : filets horizontaux, listes de spécifications
  (terme à gauche, définition à droite), index numéroté ;
- **trois chapitres de prestations aux compositions différentes** : diptyque décalé,
  bandeau large puis double colonne, image pleine à gauche ;
- **échelle de rayons volontaire** : hero 18 px, photos 8 px, vignettes 4 px,
  boutons en pilule ;
- **une carte SVG dessinée** pour la zone d'intervention (24 communes projetées en
  équirectangulaire, cercles à 20 et 35 km) plutôt qu'un mur d'étiquettes ;
- **avis en composition éditoriale** : une citation vedette en grand, trois en appui,
  sans cartouche.

Effets : montée des mots du titre, révélations au scroll, Ken Burns lent sur la photo
du hero, marquee des métiers, comparateur avant / après au glisser, légendes de
galerie au survol, visionneuse, barre d'appel mobile. Tout est neutralisé sous
`prefers-reduced-motion`.

## Suivi

`assets/app.js` pousse `form_start`, `generate_lead` et `phone_call` dans
`dataLayer`. Il suffit de brancher GTM ou gtag pour câbler les conversions
Google Ads, rien d'autre à modifier dans le code.
