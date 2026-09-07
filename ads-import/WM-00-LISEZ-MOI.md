# Import Google Ads · WM Couverture

Fichiers prêts pour **Google Ads Editor**. Le plan et le raisonnement sont dans
[GOOGLE-ADS-PLAN.md](../GOOGLE-ADS-PLAN.md).

## Avant d'importer

1. Créer le compte Google Ads du client, récupérer son **ID client** (format
   `123-456-7890`).
2. Remplacer `XXX-XXX-XXXX` par cet ID dans les quatre CSV :
   ```bash
   sed -i '' 's/XXX-XXX-XXXX/123-456-7890/g' ads-import/WM-0*.csv
   ```
3. Vérifier que le **site est en ligne** et que les pages de destination
   répondent. Sinon les annonces seront refusées.

## Ordre d'import dans Google Ads Editor

| Ordre | Fichier | Contenu |
|---|---|---|
| 1 | `WM-01-campagnes.csv` | 3 campagnes, créées **en pause** |
| 2 | `WM-02-groupes-annonces.csv` | 7 groupes d'annonces avec leur plafond de CPC |
| 3 | `WM-03-mots-cles.csv` | 160 mots-clés, exact et expression uniquement |
| 4 | `WM-04-annonces-rsa.csv` | 7 annonces responsives, 15 titres et 4 descriptions chacune |
| 5 | `WM-05-mots-cles-negatifs.txt` | 54 exclusions, à coller en liste partagée |

Les longueurs de titres (30 caractères) et de descriptions (90) sont vérifiées :
aucun dépassement.

## À régler à la main, l'éditeur ne le fait pas

- **Zones géographiques** : 35 km autour de Nonancourt pour Entretien, 25 km pour
  Urgence, 40 km pour Marque. Dans les options, choisir **« Présence »** et non
  l'option par défaut qui inclut les personnes seulement intéressées par la zone.
- **Calendrier** : 7 h à 21 h, 7 j/7. Ajustements +25 % en semaine de 18 h à 21 h,
  +20 % le week-end, +10 % de 7 h à 9 h.
- **Appareils** : +30 % sur mobile.
- **Assets** : numéro de téléphone, liens annexes, accroches, extraits structurés,
  et lieu une fois la fiche Google liée au compte.
- **Annonces appel seul** sur les groupes Fuite et Dépannage.
- **Réseau** : décocher le Réseau Display et les partenaires du Réseau de Recherche.
- **Conversions** : les 4 actions décrites dans le plan, avant d'activer.

## Ne pas activer avant

Les campagnes sont importées **en pause**, volontairement. Les quatre points
bloquants sont listés en fin de plan : site en ligne, clé Web3Forms, suivi des
conversions, fiche Google liée.
