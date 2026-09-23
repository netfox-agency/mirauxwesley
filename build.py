#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les pages internes de wmcouverture.fr (services + communes),
le sitemap, le robots.txt et les règles de redirection 301.

    python3 build.py

L'accueil (index.html) n'est PAS généré : il s'édite à la main.
Les pages produites ne s'éditent jamais directement, elles sont écrasées.
"""
import os
import pathlib, re, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
PRE = "../"   # prefixe vers la racine, ajuste selon la profondeur de la page

# ─────────────────────────────────────────────────────────── constantes ────
TEL_TXT   = "06 24 59 26 77"
TEL_HREF  = "+33624592677"
DOMAIN    = "https://wmcouverture.fr"
ADDR      = "577A les maisons rouges, 27320 Nonancourt"
ADS_GTAG       = "AW-18440677778"          # identifiant de conversion du compte Miraux Wesley
ADS_CONV_DEVIS = "2vnCCLbgjPocEJLTmdlE"    # « Demande de devis (site) »
ADS_CONV_APPEL = "l6LECPvZkvocEJLTmdlE"    # « Appel depuis le site »

W3F_KEY   = "b8529af1-dc00-4478-a060-25b363122aaf"   # cle publique Web3Forms, prevue pour le code client
MAPS      = "https://www.google.com/maps/search/?api=1&query=577A+les+maisons+rouges+27320+Nonancourt"
# Coordonnees a caler EXACTEMENT sur l'epingle de la fiche Google avant mise en ligne.
GEO_LAT   = "48.7632745"
GEO_LON   = "1.2240144"
PRICE     = "$$"
# URL de la fiche Google, du Facebook, etc. Laisser vide tant qu'on ne les a pas :
# une URL fausse dans sameAs fait plus de mal que pas de sameAs du tout.
SAMEAS    = [
    # La fiche Google porte 81 avis 5/5. Comme l'ancien site de l'agence
    # revendique la meme entreprise, ce lien est le signal qui rattache le
    # domaine neuf a la bonne entite. URL par cid : elle ne bouge jamais.
    "https://maps.google.com/?cid=17637010817244759536",
]
# Communes desservies au-dela des pages dediees.
ZONE_PLUS = ["La Madeleine-de-Nonancourt", "Muzy", "Illiers-l'Eveque", "Saint-Georges-Motel",
             "Marcilly-sur-Eure", "Garennes-sur-Eure", "Bueil", "Ezy-sur-Eure",
             "Damville", "Conches-en-Ouche", "Chateauneuf-en-Thymerais", "Senonches"]
ZONE_PLUS_ACCENTS = ["La Madeleine-de-Nonancourt", "Muzy", "Illiers-l'Évêque",
             "Saint-Georges-Motel", "Marcilly-sur-Eure", "Garennes-sur-Eure", "Bueil",
             "Ézy-sur-Eure", "Damville", "Conches-en-Ouche", "Châteauneuf-en-Thymerais",
             "Senonches"]

MARK = ('<svg class="brand__mark" viewBox="0 0 44 28" aria-hidden="true">'
        '<path d="M2 18.5 22 3.5l20 15"/><path d="M31 8.6V3h4.4v9"/>'
        '<path d="M8.5 24.5h27" class="b-accent"/></svg>')
ARROW = '<svg viewBox="0 0 24 12" aria-hidden="true"><path d="M0 6h22M17 1l5 5-5 5"/></svg>'
PHONE = ('<svg viewBox="0 0 20 20" aria-hidden="true" class="ico"><path d="M4.2 2.8h3.1l1.5 3.8-1.9 '
         '1.3a11 11 0 0 0 4.2 4.2l1.3-1.9 3.8 1.5v3.1a1.4 1.4 0 0 1-1.5 1.4A13.6 13.6 0 0 1 2.8 '
         '4.3a1.4 1.4 0 0 1 1.4-1.5Z"/></svg>')

# ── avis Google ────────────────────────────────────────────────────────────
# Source unique : avis.json, regenere par `python3 tools/avis.py --cle AIza...`
# depuis l'API Google Places. Rien ici n'ecrit le nombre d'avis en dur : c'est
# ce qui garantit qu'il reste a jour partout d'un seul coup.
import json as _json
_AVIS_JSON = _json.loads((pathlib.Path(__file__).resolve().parent / "avis.json")
                         .read_text(encoding="utf-8"))
AVIS_NOTE  = _AVIS_JSON["note"]                 # 5.0
AVIS_TOTAL = _AVIS_JSON["total"]                # 81
AVIS_FICHE = _AVIS_JSON["fiche"]
AVIS       = _AVIS_JSON["avis"]

def note_fr():
    """5.0 -> « 5,0 ». Une note entiere reste ecrite avec sa decimale : c'est
    ainsi que Google l'affiche, et c'est ce que le visiteur reconnait."""
    return f"{AVIS_NOTE:.1f}".replace(".", ",")

def avis_resume():
    return f"{note_fr()} sur {AVIS_TOTAL} avis"


# ──────────────────────────────────────────────────────────── services ─────
SERVICES = [
    dict(
        slug="renovation-toiture",
        pitch="Dépose, charpente, écran de sous-toiture et couverture neuve.",
        nav="Rénovation de toiture",
        h1=("Rénovation de <em>toiture</em>", "à Nonancourt et dans l'Eure"),
        title="Rénovation de toiture · Nonancourt et Dreux · WM Couverture",
        desc="Réfection complète de toiture en tuile, ardoise ou acier à Nonancourt, Dreux et Évreux. Charpente, écran de sous-toiture, zinguerie. Devis gratuit.",
        hero="renovation-toiture-charpente-liteaux-neufs.webp",
        heroalt="Charpente et liteaux neufs sur une toiture en rénovation à Nonancourt",
        lead="Quand la couverture a fait son temps, la réparer coûte plus cher que la refaire. "
             "Nous déposons l'ancienne toiture, reprenons la charpente si besoin, et posons une "
             "couverture neuve avec son écran de sous-toiture et sa zinguerie.",
        specs=[("Dépose", "Retrait complet de l'ancienne couverture, tri et évacuation des gravats."),
               ("Charpente", "Contrôle, remplacement des pièces attaquées, renfort si la portée l'exige."),
               ("Sous-toiture", "Écran HPV, contre-lattage et liteaunage neufs, ventilation respectée."),
               ("Couverture", "Tuile mécanique ou plate, ardoise, bac acier, selon le bâti."),
               ("Finitions", "Rives, faîtage, solins de cheminée, gouttières reprises ou remplacées.")],
        alerte_t="Les signes qui disent qu'il faut y passer",
        alerte=["Des tuiles qui glissent ou se cassent après chaque coup de vent.",
                "Des traces d'humidité sur les plafonds de l'étage ou dans les combles.",
                "Une charpente qui a des points blancs, de la sciure, ou du bois qui s'effrite.",
                "Une couverture de plus de cinquante ans jamais reprise.",
                "Pas d'écran de sous-toiture : c'est le cas de presque tous les toits anciens."],
        mat_t="Quel matériau pour votre toit",
        mat=[("Tuile mécanique",
              "Le plus courant sur les pavillons du secteur. Pose rapide, coût maîtrisé, "
              "durée de vie de quarante à cinquante ans. C'est le choix par défaut sur une "
              "maison des années soixante à quatre-vingt."),
             ("Tuile plate de pays",
              "Le matériau du bâti ancien de la vallée de l'Avre. Petit format, beaucoup de "
              "pièces au mètre carré, donc plus de main-d'œuvre. Obligatoire près d'un "
              "monument classé, et souvent imposé par le PLU sur les centres anciens."),
             ("Ardoise",
              "Fréquente sur les maisons de ville à forte pente, notamment à Dreux et à Évreux. "
              "Très longue durée de vie, pose au crochet ou au clou. Plus chère à l'achat, "
              "moins chère sur cinquante ans."),
             ("Bac acier",
              "Réservé aux dépendances, garages, hangars et bâtiments agricoles. Léger, rapide, "
              "peu coûteux. À éviter sur une maison d'habitation sans isolation acoustique.")],
        prix_t="Ce qui fait varier le prix",
        prix=["**La surface de rampant**, pas la surface au sol : un toit à forte pente développe "
              "beaucoup plus de mètres carrés qu'on ne l'imagine depuis le jardin.",
              "**La complexité** : chaque lucarne, cheminée, noue ou fenêtre de toit ajoute des "
              "découpes, de la zinguerie et du temps.",
              "**L'accès** : un pavillon avec du terrain autour coûte moins cher à couvrir qu'une "
              "maison de ville où il faut échafauder sur trottoir et sortir les gravats à la main.",
              "**L'état de la charpente**, qu'on ne connaît vraiment qu'une fois la couverture "
              "déposée. Nous chiffrons cette reprise séparément pour que vous voyiez ce que vous payez.",
              "**Le matériau** retenu, et le fait que le PLU vous en impose un ou non."],
        budget="Nous venons mesurer, nous chiffrons ligne par ligne, et le devis est gratuit. "
               "Le règlement peut être étalé en plusieurs fois sur les gros chantiers.",
        faq=[("Faut-il déposer la charpente pour refaire une toiture ?",
              "Non. Dans la très grande majorité des cas elle reste en place. Nous la contrôlons "
              "une fois la couverture déposée et nous ne remplaçons que les pièces abîmées."),
             ("Combien de temps dure le chantier ?",
              "Une à deux semaines pour un pavillon courant, selon la surface et la météo. Une "
              "bâche est posée chaque soir tant que la couverture n'est pas fermée."),
             ("Peut-on habiter la maison pendant les travaux ?",
              "Oui. Le chantier se fait par l'extérieur et la maison reste hors d'eau tous les soirs."),
             ("Faut-il une autorisation d'urbanisme ?",
              "Une déclaration préalable est demandée en mairie dès que l'aspect extérieur change, "
              "et presque toujours en secteur protégé. Nous vous disons au devis ce qu'il faut déposer."),
             ("Peut-on isoler en même temps ?",
              "C'est le bon moment, et le seul où l'on peut traiter correctement l'écran de "
              "sous-toiture et les rampants par l'extérieur. Nous le chiffrons en option.")],
    ),
    dict(
        slug="zinguerie-gouttieres",
        pitch="Gouttières, chéneaux, solins, rives et isolation sous toiture.",
        nav="Zinguerie et gouttières",
        h1=("Zinguerie <em>&amp;</em>&nbsp;gouttières", "dans l'Eure et le Drouais"),
        title="Zinguerie et gouttières · Nonancourt, Dreux · WM Couverture",
        desc="Pose et réparation de gouttières, chéneaux, descentes et solins à Nonancourt, Dreux et Anet. Nettoyage de chéneaux, isolation. Devis gratuit.",
        hero="zinguerie-souche-zinc-toiture.webp",
        heroalt="Souche de cheminée habillée en zinc sur une toiture en tuiles plates patinées",
        lead="La zinguerie décide où part l'eau. Une descente bouchée ou un solin fendu suffit "
             "à abîmer un mur en deux hivers. Nous posons, réparons et entretenons.",
        specs=[("Évacuation", "Gouttières pendantes ou havraises, chéneaux, naissances, descentes."),
               ("Étanchéité", "Solins de cheminée, abergements, noues, faîtages, closoirs ventilés."),
               ("Rives", "Habillage de rives et de sous-face, planches de rive, bandeaux."),
               ("Entretien", "Purge et nettoyage de chéneaux, remise en pente, pose de crapaudines."),
               ("Isolation", "Sous rampants, combles perdus, toiture-terrasse.")],
        alerte_t="Ce qui doit vous faire monter voir",
        alerte=["De l'eau qui déborde de la gouttière dès qu'il pleut fort.",
                "Une trace verte ou une auréole sur la façade sous une descente.",
                "Un solin de cheminée fissuré, ou du mastic sec qui se décolle.",
                "Des végétaux qui poussent dans le chéneau : la pente ne fait plus son travail.",
                "Du zinc percé au fond de la gouttière, souvent aux soudures."],
        mat_t="Zinc, aluminium ou PVC",
        mat=[("Zinc",
              "Le standard du métier. Il se soude, donc il se répare sans tout changer, et il "
              "tient quarante ans et plus. C'est ce que nous posons par défaut, en particulier "
              "sur le bâti ancien où l'aspect compte."),
             ("Aluminium laqué",
              "Bon compromis quand on veut une couleur précise ou un profil sans soudure. Ne "
              "rouille pas, se pose en grande longueur. Une réparation demande souvent de "
              "remplacer la section entière."),
             ("PVC",
              "Le moins cher à la pose. Il se déforme à la chaleur, casse au froid, et les "
              "colles vieillissent mal. Nous le proposons sur une dépendance, rarement sur une "
              "maison qu'on garde."),
             ("Cuivre",
              "Pour les toitures de caractère et les édifices anciens. Très durable, patine "
              "verte avec le temps. Coût élevé, à réserver aux ouvrages visibles.")],
        prix_t="Ce qui fait varier le prix",
        prix=["**Le mètre linéaire** de gouttière, qui suit le développé du toit et non sa façade.",
              "**Le développé du profil** : une gouttière havraise demande plus de matière qu'une "
              "demi-ronde pendante.",
              "**La hauteur d'accès** : au-delà d'un étage, l'échafaudage ou la nacelle pèsent "
              "plus lourd que la zinguerie elle-même.",
              "**Le nombre de points singuliers** : angles, naissances, dauphins, traversées de "
              "corniche, raccords sur mitoyen.",
              "**Le matériau** retenu, et la contrainte d'aspect en secteur protégé."],
        budget="Une réparation ponctuelle se règle en une intervention. Un remplacement complet "
               "se chiffre au mètre linéaire. Nous passons voir avant de chiffrer, c'est gratuit.",
        faq=[("Zinc ou PVC ?",
              "Le zinc dure trois à quatre fois plus longtemps et se répare à la soudure. Sur une "
              "maison qu'on garde, c'est presque toujours le bon calcul."),
             ("Vous nettoyez les gouttières seules ?",
              "Oui, et c'est l'intervention la moins chère qui évite le plus de dégâts. Un passage "
              "par an suffit ici, deux si vous avez des arbres au-dessus."),
             ("Un solin peut-il causer une fuite loin de la cheminée ?",
              "Oui. L'eau court le long d'un chevron avant de tomber, et la tache au plafond "
              "apparaît souvent à plusieurs mètres du point d'entrée."),
             ("Faut-il poser des crapaudines ?",
              "Sous les arbres, oui : elles retiennent les feuilles à l'entrée des descentes. "
              "Elles ne dispensent pas d'une purge annuelle, elles la rendent plus rapide."),
             ("Qui paie la gouttière mitoyenne ?",
              "Sur un chéneau commun à deux maisons, la dépense se partage entre voisins. Nous "
              "établissons un devis lisible par les deux parties pour éviter les discussions.")],
    ),
    dict(
        slug="demoussage-toiture",
        pitch="Nettoyage haute pression et traitement anti-mousse professionnel.",
        nav="Nettoyage et démoussage",
        h1=("Nettoyage <em>&amp;</em>&nbsp;démoussage", "de toiture dans l'Eure"),
        title="Démoussage de toiture · Nonancourt, Dreux · WM Couverture",
        desc="Nettoyage haute pression et traitement anti-mousse des toitures à Nonancourt, "
             "Dreux, Verneuil et Évreux. Purge de gouttières, entretien annuel. Devis gratuit.",
        hero="demoussage-toiture-mousse-echafaudage.webp",
        heroalt="Toiture couverte de mousse en cours de nettoyage à Nonancourt",
        lead="Ici, les toits verdissent vite. La mousse retient l'eau contre la tuile, la gèle "
             "en hiver, la fait éclater, et finit par boucher les gouttières.",
        specs=[("Nettoyage", "Haute pression dosée selon le matériau, sans décaper l'engobe."),
               ("Traitement", "Anti-mousse professionnel pulvérisé, effet prolongé, sans rinçage."),
               ("Gouttières", "Purge complète des chéneaux et des descentes dans la foulée."),
               ("Contrôle", "Repérage des tuiles cassées et des solins fatigués pendant le passage."),
               ("Hydrofuge", "En option, sur une couverture saine, pour ralentir la reprise.")],
        alerte_t="Quand faut-il s'en occuper",
        alerte=["Le toit est vert sur le versant nord ou sous les arbres.",
                "Les gouttières se bouchent plusieurs fois par an.",
                "Des fragments de tuile tombent au sol après une période de gel.",
                "Le dernier démoussage remonte à plus de cinq ans.",
                "Vous vendez la maison : un toit propre change la première impression."],
        mat_t="Comment nous procédons",
        mat=[("1. Nous montons voir",
              "Avant de sortir la lance, nous regardons l'état des tuiles. Une couverture déjà "
              "poreuse ou fendue ne se nettoie pas à la même pression qu'une tuile saine."),
             ("2. Nettoyage haute pression",
              "Toujours dans le sens de la pente, jamais sous la tuile. La pression est réglée "
              "selon le matériau pour retirer la mousse sans décaper l'engobe."),
             ("3. Traitement anti-mousse",
              "Un produit professionnel est pulvérisé sur toute la surface. Il continue d'agir "
              "plusieurs semaines et tue les racines que le jet n'a pas emportées."),
             ("4. Gouttières et abords",
              "Nous purgeons les chéneaux et les descentes, puis nous nettoyons le sol. Les "
              "résidus de mousse ne restent pas dans votre jardin.")],
        prix_t="Ce qui fait varier le prix",
        prix=["**La surface de rampant** et la pente, qui décident du temps passé.",
              "**L'épaisseur de la mousse** : un toit laissé quinze ans demande deux passages.",
              "**L'accès** : la présence d'une véranda, d'une terrasse ou d'un massif à protéger.",
              "**Le matériau** : la tuile plate ancienne et l'ardoise se traitent avec plus de "
              "précaution que la tuile mécanique.",
              "**L'hydrofuge** si vous le prenez en option, qui se chiffre à part."],
        budget="Le démoussage est de loin l'intervention la moins chère du métier, et celle qui "
               "repousse le plus loin la réfection complète. Le devis est gratuit.",
        faq=[("La haute pression abîme-t-elle les tuiles ?",
              "Mal dosée, oui : elle décape l'engobe et rend la tuile poreuse. Nous adaptons la "
              "pression au matériau, et sur les couvertures fragiles nous travaillons à la brosse."),
             ("Tous les combien faut-il démousser ?",
              "Tous les trois à cinq ans dans le secteur, selon l'exposition et les arbres. Un "
              "contrôle visuel chaque année suffit entre deux passages."),
             ("Faut-il être présent le jour de l'intervention ?",
              "Non, du moment que nous avons accès au terrain et à un point d'eau. Nous vous "
              "envoyons les photos avant et après."),
             ("L'hydrofuge, ça sert vraiment ?",
              "Sur une tuile saine, il ralentit la reprise de la mousse et limite l'absorption "
              "d'eau. Sur une tuile déjà poreuse, il masque un problème au lieu de le régler."),
             ("Le produit est-il dangereux pour le jardin ?",
              "Nous bâchons les massifs sensibles et nous rinçons les abords. Les traitements "
              "professionnels que nous utilisons sont prévus pour un usage en toiture habitée.")],
    ),
    dict(
        slug="depannage-toiture",
        pitch="Fuite, tuiles arrachées, bâchage : mise hors d'eau 24 h/24.",
        nav="Dépannage et urgence",
        h1=("Dépannage de toiture", "<em>24 h/24</em> autour de Nonancourt"),
        title="Dépannage toiture 24 h/24 · Nonancourt, Dreux · WM",
        desc="Fuite, tuiles arrachées, bâchage d'urgence : intervention 24 h/24 à Nonancourt, Dreux et Anet. Recherche de fuite et mise hors d'eau rapide.",
        hero="depannage-toiture-depose-tuiles-urgence.webp",
        heroalt="Toiture partiellement déposée après un sinistre, liteaux apparents",
        lead="Une toiture qui prend l'eau n'attend pas. Nous répondons tous les jours de 8 h à "
             "21 h, et la nuit en cas d'urgence. La priorité est de mettre hors d'eau.",
        specs=[("Mise hors d'eau", "Bâchage et calfeutrement provisoire dès le premier passage."),
               ("Recherche de fuite", "Inspection du toit, des solins, des noues et des pénétrations."),
               ("Réparation", "Remplacement des tuiles, reprise de solin, ressoudure de zinc."),
               ("Tempête", "Reprise des tuiles arrachées, faîtage descellé, antenne ou cheminée."),
               ("Assurance", "Photos et constat écrit du sinistre pour votre déclaration.")],
        alerte_t="Ce qui relève de l'urgence",
        alerte=["De l'eau qui coule à l'intérieur pendant qu'il pleut.",
                "Des tuiles au sol après un coup de vent, ou un faîtage descellé.",
                "Une bâche posée dans l'urgence qui ne tient plus.",
                "Un arbre ou une branche tombée sur la couverture.",
                "Une infiltration qui touche un tableau électrique ou des combles isolés."],
        mat_t="D'où viennent les fuites, dans l'ordre",
        mat=[("Le solin de cheminée",
              "C'est la première cause, de loin. Le mastic sèche, se rétracte, et l'eau passe "
              "entre la maçonnerie et la couverture. La tache apparaît souvent loin du conduit."),
             ("Les tuiles déplacées",
              "Un coup de vent soulève une tuile, la suivante ne recouvre plus. Sans écran de "
              "sous-toiture, l'eau tombe directement sur le plancher des combles."),
             ("La noue",
              "L'angle rentrant entre deux versants concentre toute l'eau du toit. Une noue "
              "encrassée ou percée déborde sous la couverture au premier gros orage."),
             ("Les pénétrations",
              "Sortie de VMC, chatière, passage d'antenne, fenêtre de toit : chaque trou dans la "
              "couverture est un point à contrôler quand la fuite ne s'explique pas autrement.")],
        prix_t="Ce qui fait varier le prix",
        prix=["**L'heure et le jour** : une intervention de nuit ou un dimanche ne se facture pas "
              "comme un mardi matin.",
              "**La mise hors d'eau** seule, qui est rapide, ou la réparation définitive derrière.",
              "**L'accès** : la hauteur, la pente, la nécessité d'un échafaudage ou d'une nacelle.",
              "**La cause** : un solin à reprendre n'a rien à voir avec une noue à refaire.",
              "**Les fournitures**, quand la tuile d'origine n'est plus fabriquée et qu'il faut "
              "trouver un équivalent."],
        budget="Un dépannage se facture au temps passé et aux fournitures. Nous annonçons un "
               "ordre de grandeur au téléphone avant de nous déplacer, et le devis de la "
               "réparation définitive est gratuit.",
        faq=[("Vous vous déplacez la nuit ?",
              "Oui, pour les urgences. En pleine nuit et sous la pluie, monter sur un toit est "
              "dangereux : nous protégeons l'intérieur, puis nous bâchons dès que c'est praticable."),
             ("L'assurance prend-elle en charge ?",
              "Pour un événement climatique, souvent oui, selon votre contrat. Nous fournissons "
              "les photos et le descriptif écrit dont votre assureur a besoin."),
             ("Vous trouvez toujours la fuite ?",
              "Presque toujours au premier passage. L'eau circule parfois longtemps sous la "
              "couverture : dans ces cas-là nous reprenons les points de pénétration un par un."),
             ("Que faire en attendant votre arrivée ?",
              "Coupez l'électricité de la pièce touchée, posez un seau, écartez les meubles et "
              "percez le plafond au point le plus bas si l'eau s'accumule. Ne montez pas sur le toit."),
             ("Sous quel délai intervenez-vous ?",
              "Le jour même pour une fuite active dans notre rayon habituel. Nous vous disons au "
              "téléphone à quelle heure nous passons, pas « dans la journée ».")],
    ),
    dict(
        slug="charpente",
        pitch="Contrôle, reprise de pièces, renfort et charpente traditionnelle.",
        nav="Charpente",
        h1=("<em>Charpente</em> :", "contrôle, reprise, renfort"),
        title="Charpentier à Nonancourt (27) et Dreux · WM Couverture",
        desc="Contrôle de charpente, remplacement de pièces attaquées, renfort et charpente "
             "traditionnelle à Nonancourt, Dreux et Verneuil. Devis gratuit après visite.",
        hero="charpente-ancienne-sous-toiture.webp",
        heroalt="Charpente ancienne en chêne vue depuis les combles, avant reprise",
        lead="La charpente porte tout le reste. On ne la voit qu'une fois la couverture déposée, "
             "et c'est là que se joue une bonne partie du budget d'une réfection.",
        specs=[("Contrôle", "Inspection pièce par pièce dès la dépose : pannes, chevrons, sablières."),
               ("Reprise", "Remplacement des seules pièces attaquées, chiffré à l'unité."),
               ("Renfort", "Moisage, jambe de force, entretoise quand la portée l'exige."),
               ("Traditionnelle", "Charpente neuve en chêne ou en résineux, assemblée sur place."),
               ("Traitement", "Curatif contre les insectes à larves xylophages et les champignons.")],
        alerte_t="Ce qui doit vous alerter",
        alerte=["De la sciure fine au sol des combles, en petits tas réguliers.",
                "Des trous de sortie de quelques millimètres dans le bois.",
                "Une pièce qui s'effrite ou se creuse quand on appuie avec un tournevis.",
                "Des taches sombres et cotonneuses : c'est un champignon, pas de l'humidité.",
                "Une panne qui fléchit visiblement, ou une ligne de faîtage qui ondule."],
        mat_t="Les cinq pièces qui posent problème",
        mat=[("Les pieds de chevrons",
              "C'est là que ça commence presque toujours. L'about du chevron repose sur la "
              "sablière, au point le plus exposé aux infiltrations de rive. On le découvre "
              "attaqué en déposant la couverture, et il se répare par greffe sans toucher au reste."),
             ("La sablière",
              "La pièce horizontale posée sur le mur, qui reçoit tous les chevrons. Si elle a "
              "pris l'eau par un débord mal protégé, la reprise est plus lourde : il faut "
              "soulager la charpente pour la remplacer."),
             ("L'entrait et les pannes",
              "Les grandes pièces porteuses. Une flèche visible signale une surcharge ou une "
              "section devenue insuffisante. On renforce par moisage plutôt que de remplacer, "
              "c'est plus rapide et souvent aussi solide."),
             ("Autour de la cheminée",
              "L'humidité d'un solin fatigué descend le long du conduit et attaque les bois au "
              "contact. C'est un foyer classique, et invisible depuis le sol."),
             ("Les fermettes industrielles",
              "Sur les pavillons des années soixante à quatre-vingt-dix, la charpente est en "
              "fermettes. Elle est saine dans la quasi-totalité des cas, mais on ne peut pas y "
              "toucher pour aménager les combles sans une étude. Nous vous le disons franchement.")],
        prix_t="Ce qui fait varier le prix",
        prix=["**Le nombre de pièces** réellement à reprendre, qui n'est connu qu'une fois la "
              "couverture déposée. C'est pour cela qu'un bon devis chiffre un prix unitaire.",
              "**L'accessibilité** : intervenir depuis les combles ou depuis le toit ne demande "
              "ni le même temps ni le même matériel.",
              "**L'essence et la section** du bois, et le fait qu'il faille du sur-mesure ou du "
              "standard.",
              "**Le traitement** : un curatif se facture au mètre carré de bois traité, et il "
              "n'a de sens qu'une fois les pièces mortes retirées.",
              "**La nécessité d'étayer** pendant l'intervention, sur les grandes portées."],
        budget="Nous ne chiffrons jamais une charpente sans être montés voir. Sur une réfection, "
               "la reprise est chiffrée séparément et à l'unité, pour que vous sachiez exactement "
               "à quoi vous vous engagez si le bois réserve des surprises.",
        faq=[("Faut-il tout refaire quand une pièce est attaquée ?",
              "Presque jamais. On remplace la pièce ou on greffe la partie morte. Une dépose "
              "complète de charpente est rare et se voit tout de suite au premier coup d'œil."),
             ("Le traitement des bois, c'est utile ?",
              "Curatif, oui, quand il y a une attaque active. Préventif sur une charpente saine "
              "et sèche, l'intérêt est plus discutable et cela se discute au cas par cas."),
             ("On peut aménager les combles sous des fermettes ?",
              "C'est possible mais cela suppose de reprendre la structure avec une étude. Nous "
              "ne le faisons pas à l'improvisation, et nous vous dirons si c'est déraisonnable."),
             ("Combien de temps dure une charpente ?",
              "Plusieurs siècles si elle reste sèche et ventilée. Ce qui la tue, c'est l'eau : "
              "une couverture qui fuit pendant deux hivers fait plus de dégâts que cinquante ans "
              "de service normal."),
             ("Vous faites de la charpente neuve ?",
              "Oui, traditionnelle, pour une extension, un auvent, une dépendance ou une "
              "réfection lourde.")],
    ),
    dict(
        slug="isolation-toiture",
        pitch="Combles perdus, sous rampants ou par l'extérieur au moment de la réfection.",
        nav="Isolation de toiture",
        h1=("<em>Isolation</em> de toiture", "et de combles"),
        title="Isolation de toiture et combles (27)",
        desc="Isolation des combles perdus, sous rampants ou par l'extérieur à Nonancourt, Dreux "
             "et Évreux. Traitée au moment de la réfection de toiture. Devis gratuit.",
        hero="combles-avant-isolation-sous-rampants.webp",
        heroalt="Combles dégagés sous charpente, prêts à recevoir l'isolation",
        lead="La chaleur monte : un toit mal isolé est le premier poste de déperdition d'une "
             "maison. Et c'est au moment où la couverture se refait que l'isolation coûte le "
             "moins cher à poser correctement.",
        specs=[("Combles perdus", "Soufflage de laine sur le plancher, une journée, effet immédiat."),
               ("Sous rampants", "Isolation entre et sous chevrons, quand les combles sont aménagés."),
               ("Par l'extérieur", "Isolant posé sur les chevrons pendant la réfection, sans perte de hauteur."),
               ("Toit plat", "Isolation et étanchéité sur les extensions et les garages."),
               ("Ventilation", "Écran HPV, lame d'air continue, entrées basses et sortie en faîtage.")],
        alerte_t="Les signes d'une isolation qui ne fait plus son travail",
        alerte=["Un étage glacial en hiver et invivable en été, alors que le bas est correct.",
                "De la neige qui fond plus vite sur votre toit que sur celui du voisin.",
                "Un isolant tassé, noirci ou humide quand on regarde dans les combles.",
                "Des traces sombres sur les chevrons, signe de condensation.",
                "Une isolation posée lors d'une campagne à un euro, sans lame d'air ventilée."],
        mat_t="Quelle méthode pour quelle situation",
        mat=[("Combles perdus, couverture saine",
              "Soufflage de laine sur le plancher des combles. Une journée de travail, le coût le "
              "plus bas du bâtiment pour le gain thermique obtenu. C'est le premier geste à faire "
              "quand il n'a jamais été fait."),
             ("Combles aménagés, couverture saine",
              "Isolation sous rampants, par l'intérieur. On perd quelques centimètres sous plafond "
              "et il faut refaire les finitions, mais on ne touche pas au toit."),
             ("Couverture à refaire",
              "Isolation par l'extérieur, sur les chevrons, sous la couverture neuve. Aucune perte "
              "de hauteur, aucun pont thermique au droit des chevrons, et les combles restent "
              "habitables pendant le chantier. C'est techniquement la meilleure solution, et elle "
              "n'est accessible qu'à ce moment-là."),
             ("L'erreur qui coûte cher",
              "Isoler sans ventiler. La vapeur d'eau de la maison se condense sur la sous-toiture "
              "froide, mouille l'isolant qui n'isole plus rien, et attaque la charpente. Le "
              "désordre met deux à cinq ans à se voir et coûte plus cher que l'isolation.")],
        prix_t="Ce qui fait varier le prix",
        prix=["**La méthode** : un soufflage en combles perdus et un sarking par l'extérieur ne "
              "jouent pas dans la même catégorie.",
              "**La résistance thermique visée**, qui décide de l'épaisseur et donc du volume "
              "d'isolant.",
              "**L'isolant retenu** : laine minérale, laine de bois, polyuréthane. Le dernier "
              "isole plus à épaisseur égale, ce qui compte en sarking.",
              "**L'accès aux combles**, et le fait qu'il faille les vider ou non avant.",
              "**Les travaux induits** : reprise des finitions, déplacement de l'électricité, "
              "surélévation des rives en isolation par l'extérieur."],
        budget="Nous chiffrons l'isolation séparément de la couverture, pour que vous voyiez ce "
               "que chaque poste vous coûte. C'est aussi ce qui permet de savoir ce qui relève de "
               "la rénovation énergétique et ce qui n'en relève pas.",
        faq=[("Refaire ma toiture me donne-t-il droit à une aide ?",
              "La couverture seule, non : ce n'est pas un geste de rénovation énergétique. "
              "L'isolation réalisée en même temps, oui, sous conditions."),
             ("Quelle épaisseur d'isolant faut-il ?",
              "C'est la résistance thermique qui compte, pas l'épaisseur brute. Elle doit figurer "
              "sur le devis, c'est le seul chiffre comparable d'une entreprise à l'autre."),
             ("Peut-on isoler par l'extérieur sans refaire la couverture ?",
              "Non, il faut déposer. C'est pour cela que les deux se font ensemble, sinon vous "
              "payez deux fois la dépose et l'échafaudage."),
             ("Mon isolation a été faite à un euro, faut-il tout refaire ?",
              "Pas systématiquement. On monte regarder : si la lame d'air existe et que l'isolant "
              "est sec, il n'y a rien à faire. S'il est tassé ou humide, il ne sert plus à rien."),
             ("L'isolation par l'extérieur surélève-t-elle le toit ?",
              "De quelques centimètres, oui. Il faut adapter les rives, les solins et parfois la "
              "sortie de cheminée. C'est prévu au devis.")],
    ),
    dict(
        slug="recherche-de-fuite",
        pitch="Inspection du toit, des solins, des noues et des pénétrations.",
        nav="Recherche de fuite",
        h1=("<em>Recherche</em> de fuite", "sur toiture"),
        title="Recherche de fuite toiture · Dreux",
        desc="Recherche de fuite et d'infiltration sur toiture à Nonancourt, Dreux et "
             "Saint-Rémy-sur-Avre. Inspection des solins, noues et pénétrations. Devis gratuit.",
        hero="depannage-toiture-depose-tuiles-urgence.webp",
        heroalt="Toiture en cours d'inspection, tuiles déposées pour localiser une infiltration",
        lead="Une fuite apparaît rarement là où elle entre. L'eau court le long d'un chevron ou "
             "d'un liteau avant de tomber, et la tache au plafond peut être à plusieurs mètres "
             "du vrai point d'entrée.",
        specs=[("Sur le toit", "Inspection des tuiles, des rives, du faîtage et des recouvrements."),
               ("Points singuliers", "Solins de cheminée, noues, abergements, sorties de VMC."),
               ("Dans les combles", "Lecture des traces sur les bois pour remonter au point d'entrée."),
               ("Test à l'eau", "Arrosage méthodique zone par zone quand la cause reste incertaine."),
               ("Compte rendu", "Photos et explication écrite de ce qui a été trouvé.")],
        alerte_t="Ce qu'il faut nous dire au téléphone",
        alerte=["Depuis quand ça coule, et si c'est continu ou seulement par forte pluie.",
                "Si l'eau apparaît par vent d'ouest ou quelle que soit la direction.",
                "L'endroit exact de la tache, et s'il y a une cheminée ou un velux au-dessus.",
                "Si des travaux ont été faits récemment sur le toit ou la façade.",
                "L'âge approximatif de la couverture, même en ordre de grandeur."],
        mat_t="D'où viennent les fuites, dans l'ordre de fréquence",
        mat=[("Le solin de cheminée",
              "Première cause, de très loin. Le mastic sèche, se rétracte, et l'eau passe entre la "
              "maçonnerie et la couverture. C'est le premier endroit que nous regardons, et c'est "
              "souvent le dernier."),
             ("Une tuile déplacée ou fendue",
              "Un coup de vent soulève une tuile, la suivante ne recouvre plus. Sans écran de "
              "sous-toiture, l'eau tombe directement sur le plancher des combles. Réparation "
              "rapide dès que le point est trouvé."),
             ("La noue",
              "L'angle rentrant entre deux versants concentre l'eau de tout le toit. Encrassée par "
              "les feuilles ou percée par la corrosion, elle déborde sous la couverture au premier "
              "gros orage."),
             ("Les pénétrations",
              "Sortie de VMC, chatière, passage d'antenne, fenêtre de toit. Chaque trou volontaire "
              "dans la couverture est un point à contrôler quand le reste ne donne rien."),
             ("La gouttière",
              "Une gouttière bouchée déborde vers l'arrière, sous la première rangée de tuiles. "
              "L'eau mouille le mur et le bas de charpente, et on croit à une fuite de toiture.")],
        prix_t="Ce qui fait varier le prix",
        prix=["**Le temps de recherche** : une fuite évidente se trouve en vingt minutes, une "
              "infiltration capricieuse demande un test à l'eau méthodique.",
              "**L'accès** : hauteur, pente, nécessité d'un échafaudage ou d'une nacelle.",
              "**L'urgence** : une intervention un dimanche ne se facture pas comme un mardi.",
              "**La réparation** qui suit, chiffrée à part une fois la cause connue.",
              "**Le rapport écrit** si vous en avez besoin pour une assurance ou une vente."],
        budget="La recherche se facture au temps passé, et nous annonçons un ordre de grandeur au "
               "téléphone avant de nous déplacer. La réparation qui suit fait l'objet d'un devis "
               "gratuit, pour que vous décidiez en connaissance de cause.",
        faq=[("Vous trouvez toujours la fuite ?",
              "Presque toujours au premier passage. Quand l'eau circule longtemps sous la "
              "couverture, nous reprenons les points de pénétration un par un jusqu'à isoler la "
              "cause."),
             ("La tache est loin de la cheminée, est-ce quand même elle ?",
              "Très souvent, oui. L'eau suit la pente d'un chevron avant de tomber. C'est pour "
              "cela que la recherche se fait sur le toit et dans les combles, pas depuis le salon."),
             ("Peut-on chercher sous la pluie ?",
              "C'est même parfois le meilleur moment pour observer, depuis l'intérieur. Monter "
              "sur un toit mouillé, en revanche, est dangereux et nous attendons une accalmie."),
             ("Faut-il une caméra thermique ?",
              "Sur une toiture en pente, rarement : l'observation et le test à l'eau suffisent. "
              "Méfiez-vous de qui vous vend d'emblée du matériel sophistiqué."),
             ("Et si la fuite ne vient pas du toit ?",
              "Ça arrive : une remontée par la façade, une condensation, une fuite de plomberie. "
              "Nous vous le dirons plutôt que de vous facturer une réparation inutile.")],
    ),
    dict(
        slug="fenetre-de-toit",
        pitch="Pose et remplacement de fenêtres de toit, raccord à la couverture.",
        nav="Fenêtre de toit",
        h1=("Pose de <em>fenêtre</em>", "de toit"),
        title="Pose de fenêtre de toit · Nonancourt",
        desc="Pose et remplacement de fenêtres de toit à Nonancourt, Dreux et Anet. Raccord à la "
             "couverture, écran de sous-toiture, volet extérieur. Devis gratuit.",
        hero="pose-fenetre-de-toit-velux.webp",
        heroalt="Fenêtre de toit posée dans une couverture en tuile, raccord terminé",
        lead="Une fenêtre de toit est un trou volontaire dans une couverture. Ce qui la rend "
             "étanche n'est pas le châssis, c'est le raccord à la couverture. C'est là que naît "
             "la quasi-totalité des infiltrations.",
        specs=[("Pose", "Dépose locale, adaptation des liteaux, costière adaptée au matériau."),
               ("Étanchéité", "Raccord à l'écran de sous-toiture et collerette pare-vapeur intérieure."),
               ("Remplacement", "Dépose de l'ancien châssis et pose d'un neuf, souvent en une journée."),
               ("Volet extérieur", "Posé en même temps, sans surcoût de main-d'œuvre."),
               ("Réparation", "Reprise d'un raccord qui fuit ou d'une condensation autour du cadre.")],
        alerte_t="Les signes d'une pose ratée",
        alerte=["De l'eau qui apparaît en haut du cadre dès qu'il pleut avec du vent.",
                "De la condensation permanente sur le pourtour intérieur.",
                "Une tache brune sur la finition intérieure, en général en angle.",
                "Un châssis qui ferme mal ou qui grince, signe d'un cadre déformé.",
                "Un raccord visiblement bricolé au mastic depuis le toit."],
        mat_t="Ce qui se joue à la pose",
        mat=[("La costière, adaptée au matériau",
              "Un kit de raccordement prévu pour de la tuile mécanique posé sur de l'ardoise fuit. "
              "Chaque matériau et chaque hauteur d'onde a le sien. C'est le premier point à "
              "vérifier sur un devis."),
             ("Le raccord à l'écran de sous-toiture",
              "L'écran doit être découpé et raccordé proprement autour du châssis. Sans ça, l'eau "
              "qui passerait sous une tuile n'a plus de chemin d'évacuation et entre directement."),
             ("La collerette pare-vapeur",
              "Côté intérieur. Sans elle, la vapeur d'eau de la maison se condense dans l'isolant "
              "autour du cadre. Vous croirez à une fuite alors que c'est de la condensation, et "
              "aucune reprise sur le toit ne la corrigera."),
             ("Le bon moment pour poser",
              "Pendant une réfection, si la toiture doit être refaite : l'échafaudage est déjà là "
              "et le raccord se fait proprement dans la foulée. Sur une couverture en fin de vie, "
              "ne posez rien : vous investissez dans un châssis à redéposer dans trois ans.")],
        prix_t="Ce qui fait varier le prix",
        prix=["**La dimension** du châssis, et le fait qu'il faille ou non modifier le chevronnage.",
              "**Le matériau de couverture**, qui décide de la costière et du temps de raccord.",
              "**Le vitrage** : standard, phonique, sécurité, retardateur d'effraction.",
              "**Le volet ou le store**, extérieur ou intérieur, manuel ou motorisé.",
              "**Les finitions intérieures**, souvent oubliées des devis : habillage, plaque, peinture."],
        budget="Comptez une journée par châssis sur une toiture existante, moins si c'est fait "
               "pendant une réfection. Le devis est gratuit et détaille séparément le châssis, la "
               "pose et les finitions.",
        faq=[("Faut-il une autorisation pour poser une fenêtre de toit ?",
              "Oui, une déclaration préalable, systématiquement : l'aspect extérieur change. Et "
              "des distances s'appliquent par rapport à la limite du voisin quand la fenêtre crée "
              "une vue."),
             ("Et pour remplacer une fenêtre existante ?",
              "Si les dimensions et l'aspect sont identiques, en général non. Dès que la taille ou "
              "la teinte change, oui."),
             ("Ma fenêtre de toit fuit, faut-il la changer ?",
              "Rarement. Dans la grande majorité des cas c'est le raccord à la couverture ou la "
              "condensation autour du cadre. Nous cherchons dans cet ordre avant de proposer un "
              "remplacement."),
             ("Volet roulant ou store intérieur ?",
              "Le volet extérieur est nettement plus efficace contre la chaleur d'été, et il se "
              "pose sans surcoût de main-d'œuvre si c'est fait en même temps."),
             ("Sur quelle pente peut-on poser ?",
              "La plupart des modèles demandent entre 15 et 90 degrés. En dessous il existe des "
              "solutions spécifiques, plus coûteuses.")],
    ),
    dict(
        slug="bardage",
        pitch="Habillage de pignon, de sous-face et de façade en bois ou en composite.",
        nav="Bardage",
        h1=("<em>Bardage</em> et", "habillage de pignon"),
        title="Bardage et habillage de pignon (27)",
        desc="Pose de bardage bois ou composite, habillage de pignon et de sous-face à "
             "Nonancourt, Dreux et Verneuil. Ventilation respectée. Devis gratuit.",
        hero="rive-de-toiture-debord-termine.webp",
        heroalt="Débord de toiture et habillage de rive terminés sur un pavillon",
        lead="Le bardage protège une façade exposée et rattrape un pignon fatigué sans le "
             "reprendre en maçonnerie. C'est un travail de couvreur autant que de façadier : "
             "tout se joue sur la ventilation et le raccord au toit.",
        specs=[("Pignon", "Habillage complet d'un mur exposé, souvent au nord ou à l'ouest."),
               ("Sous-face", "Habillage du dessous de débord de toit, en PVC ou en bois."),
               ("Ossature", "Tasseaux et contre-lattage pour créer la lame d'air ventilée."),
               ("Finitions", "Bavettes, profils d'angle, arrêts, raccords aux menuiseries."),
               ("Isolation", "Possible derrière le bardage, en isolation par l'extérieur.")],
        alerte_t="Quand un bardage devient la bonne réponse",
        alerte=["Un pignon exposé aux pluies d'ouest qui reste humide et se dégrade.",
                "Un enduit qui cloque, se décolle ou se fissure sur toute une façade.",
                "Une envie d'isoler par l'extérieur sans toucher à l'intérieur.",
                "Une sous-face de débord abîmée, où les oiseaux entrent dans les combles.",
                "Une extension à raccorder visuellement au bâtiment existant."],
        mat_t="Les matériaux et ce qu'ils impliquent",
        mat=[("Bois massif",
              "Douglas, mélèze, red cedar. Le plus chaleureux, et le seul qui grise naturellement "
              "sans entretien si l'essence est bien choisie. Il travaille avec l'humidité : la "
              "pose doit lui laisser du jeu."),
             ("Bois composite",
              "Aspect bois, sans entretien et sans variation dimensionnelle notable. Plus cher à "
              "l'achat, mais on ne le retouche jamais. Bon choix sur un pignon difficile d'accès."),
             ("PVC et cellulaire",
              "Le plus économique, surtout en sous-face de débord où il est presque invisible. "
              "Sur une grande façade visible, l'aspect est moins convaincant."),
             ("Le point qui compte plus que le matériau",
              "La lame d'air ventilée derrière le bardage. Sans elle, l'humidité reste piégée "
              "contre le mur et le bardage devient un piège au lieu d'une protection. C'est ce "
              "qu'on regarde en premier sur un devis concurrent.")],
        prix_t="Ce qui fait varier le prix",
        prix=["**La surface** et la hauteur, qui décident de l'échafaudage.",
              "**Le matériau** retenu, du PVC au bois massif il y a un facteur trois.",
              "**Le sens de pose** : à claire-voie, à recouvrement, à rainure et languette.",
              "**Les points singuliers** : angles, tableaux de fenêtres, raccords au toit.",
              "**L'isolation** ajoutée derrière, si vous en profitez pour la traiter."],
        budget="Le bardage se chiffre au mètre carré posé, échafaudage compris. Nous venons "
               "mesurer et nous vous montrons deux options de matériau chiffrées, plutôt qu'un "
               "seul devis à prendre ou à laisser.",
        faq=[("Faut-il une autorisation pour un bardage ?",
              "Oui, une déclaration préalable : l'aspect extérieur change. En secteur protégé, "
              "le matériau et la teinte peuvent être imposés."),
             ("Le bois demande-t-il de l'entretien ?",
              "Si vous acceptez qu'il grise, non. Si vous voulez conserver la teinte d'origine, "
              "il faut un saturateur tous les deux à quatre ans selon l'exposition."),
             ("Peut-on barder seulement un pignon ?",
              "Oui, c'est même le cas le plus fréquent : on traite le mur le plus exposé et on "
              "laisse le reste en enduit."),
             ("Bardage et isolation extérieure, c'est la même chose ?",
              "Non, mais l'un permet l'autre. L'isolant se pose contre le mur, le bardage vient "
              "par-dessus avec sa lame d'air."),
             ("Qui pose le bardage, un couvreur ou un façadier ?",
              "Les deux le font. L'avantage du couvreur, c'est le raccord au toit, aux débords et "
              "aux rives, qui est précisément l'endroit où les bardages prennent l'eau.")],
    ),
]

# ───────────────────────────────────────────────────────────── communes ────
VILLES = [
    dict(photo="couvreur-nonancourt-longere-tuile-neuve.webp", photoalt="Longère couverte à neuf en tuile à Nonancourt",
         slug="couvreur-nonancourt", ville="Nonancourt", cp="27320", dep="Eure", km=None,
         title="Couvreur à Nonancourt (27320) · WM Couverture",
         desc="WM Couverture est installée aux Maisons Rouges à Nonancourt. Rénovation de "
              "toiture, charpente, zinguerie et démoussage dans le bourg et les hameaux alentour.",
         intro="C'est notre commune. L'atelier est aux Maisons Rouges, et une bonne partie de "
               "nos chantiers tient dans un rayon de dix minutes.",
         bati="Le bourg mêle des maisons anciennes en brique et silex, couvertes en tuile plate "
              "de pays, et des pavillons plus récents en tuile mécanique. Dans la campagne "
              "autour, ce sont surtout des longères et des corps de ferme, avec de grandes "
              "surfaces de rampant et des charpentes qui ont parfois plus d'un siècle.",
         enjeu="La vallée de l'Avre est humide et les versants nord verdissent vite. Sur les "
               "toits anciens, deux points reviennent tout le temps : l'absence d'écran de "
               "sous-toiture, et des solins de cheminée jamais repris.",
         focus=[("Réfection de longère", "Grandes surfaces, charpente ancienne, tuile plate à "
                 "respecter quand le PLU l'impose."),
                ("Démoussage", "Les versants nord de la vallée reverdissent en trois ou quatre ans."),
                ("Dépannage rapide", "Nous sommes sur place : c'est ici que nous intervenons le "
                 "plus vite.")],
         autour=["La Madeleine-de-Nonancourt", "Muzy", "Saint-Rémy-sur-Avre", "Illiers-l'Évêque",
                 "Tillières-sur-Avre", "Brezolles"],
         faq=[("Vous intervenez dans les hameaux autour de Nonancourt ?",
               "Oui, y compris sur les corps de ferme isolés. L'accès et la place pour "
               "l'échafaudage sont même souvent plus simples qu'en centre-bourg."),
              ("Peut-on passer vous voir à l'atelier ?",
               "Appelez avant : nous sommes le plus souvent sur les toits. Un rendez-vous chez "
               "vous est de toute façon plus utile, nous voyons directement la toiture.")]),

    dict(photo="couvreur-dreux-maison-de-ville-toiture.webp", photoalt="Maison de ville rénovée à Dreux, couverture et façade reprises",
         slug="couvreur-dreux", ville="Dreux", cp="28100", dep="Eure-et-Loir", km=13,
         title="Couvreur à Dreux (28100) · Toiture, zinguerie · WM",
         desc="Couvreur à Dreux et dans le Drouais : rénovation de toiture, charpente, "
              "gouttières, démoussage et dépannage. Entreprise familiale basée à 13 km, à Nonancourt.",
         intro="Dreux est à un quart d'heure de l'atelier. C'est la ville où nous intervenons le "
               "plus souvent après Nonancourt.",
         bati="Le centre ancien aligne des maisons de ville étroites, à pente forte, souvent "
              "couvertes en ardoise, avec des toitures mitoyennes et des accès difficiles depuis "
              "la rue. Les quartiers pavillonnaires construits des années soixante aux années "
              "quatre-vingt sont, eux, en tuile mécanique, avec des charpentes industrielles et "
              "des combles souvent aménagés.",
         enjeu="En centre-ville, la vraie contrainte est logistique : échafaudage sur trottoir, "
               "protection des mitoyens, évacuation des gravats. Nous en tenons compte dans le "
               "devis plutôt que de le découvrir en cours de chantier. Près du centre historique, "
               "l'aspect de la couverture peut aussi être encadré : nous le vérifions avant de chiffrer.",
         focus=[("Toiture mitoyenne", "Reprise d'un seul versant, raccord soigné sur le voisin, "
                 "solin de mitoyen refait."),
                ("Ardoise", "Pose au crochet sur les fortes pentes du centre ancien."),
                ("Pavillon des années 70", "Tuile mécanique en fin de vie, charpente saine, "
                 "chantier rapide.")],
         autour=["Vernouillet", "Saint-Rémy-sur-Avre", "Anet", "Brezolles",
                 "Châteauneuf-en-Thymerais", "Nogent-le-Roi"],
         faq=[("Vous posez l'échafaudage sur le trottoir à Dreux ?",
               "Quand la maison donne sur la rue, oui, avec une autorisation d'occupation du "
               "domaine public demandée en mairie. Nous nous en occupons et le délai est chiffré "
               "dans le devis."),
              ("Faut-il rester en ardoise sur une maison du centre ?",
               "Souvent oui, surtout aux abords des monuments. Nous regardons ce que le PLU "
               "autorise avant de vous proposer une solution.")]),

    dict(photo="refection-toiture-pavillon-terminee.webp", photoalt="Pavillon de Vernouillet dont la toiture vient d'être refaite",
         slug="couvreur-vernouillet", ville="Vernouillet", cp="28500", dep="Eure-et-Loir", km=15,
         title="Couvreur à Vernouillet (28500) · Toiture · WM Couverture",
         desc="Couvreur à Vernouillet, dans l'agglomération de Dreux : réfection de toiture, "
              "zinguerie, démoussage et dépannage. Entreprise familiale de Nonancourt, à 15 km.",
         intro="Vernouillet prolonge Dreux au sud. C'est un secteur très pavillonnaire, où les "
               "toitures ont souvent le même âge d'une rue à l'autre.",
         bati="La commune s'est largement construite entre les années soixante et les années "
              "quatre-vingt-dix : maisons individuelles en tuile mécanique, charpentes "
              "industrielles en fermettes, combles parfois aménagés après coup. On y trouve "
              "aussi des immeubles et des équipements plus récents, souvent en toiture-terrasse.",
         enjeu="Sur ces maisons, la couverture d'origine arrive au bout de son cycle. Le problème "
               "n'est presque jamais la charpente, qui est saine, mais l'absence d'écran de "
               "sous-toiture et la ventilation des combles quand ils ont été isolés sans précaution.",
         focus=[("Réfection de pavillon", "Chantier court, charpente conservée, écran de "
                 "sous-toiture ajouté."),
                ("Isolation des combles", "Traitée en même temps que la couverture, par l'extérieur."),
                ("Gouttières", "Remplacement du PVC d'origine, souvent déformé, par du zinc.")],
         autour=["Dreux", "Anet", "Saint-Rémy-sur-Avre", "Nogent-le-Roi",
                 "Châteauneuf-en-Thymerais", "Brezolles"],
         faq=[("Mes voisins ont le même toit que moi, peut-on grouper ?",
               "Oui, et c'est souvent intéressant : l'échafaudage et le déplacement se "
               "partagent. Parlez-en à vos voisins avant que nous passions chiffrer."),
              ("Ma charpente est en fermettes, cela change quoi ?",
               "Elle se contrôle vite et se reprend rarement. En revanche on ne peut pas y "
               "toucher pour aménager les combles sans étude, et nous vous le dirons franchement.")]),

    dict(photo="rive-de-toiture-debord-termine.webp", photoalt="Rive de toiture terminée sur un pavillon de Saint-Rémy-sur-Avre",
         slug="couvreur-saint-remy-sur-avre", ville="Saint-Rémy-sur-Avre", cp="28380",
         dep="Eure-et-Loir", km=4,
         title="Couvreur à Saint-Rémy-sur-Avre (28380) · WM Couverture",
         desc="Couvreur à Saint-Rémy-sur-Avre, à 4 km de notre atelier de Nonancourt. Réfection "
              "de toiture, zinguerie, démoussage et dépannage d'urgence.",
         intro="Saint-Rémy est la commune voisine, à quatre kilomètres. Nous y passons presque "
               "chaque semaine.",
         bati="Le bâti porte la marque du passé industriel de la vallée : maisons de bourg "
              "alignées, anciens logements ouvriers en brique, et lotissements pavillonnaires "
              "plus récents. Beaucoup de toitures en tuile mécanique posées dans les mêmes "
              "années arrivent aujourd'hui au bout de leur cycle en même temps.",
         enjeu="Sur ces maisons mitoyennes, reprendre un seul versant demande de soigner la "
               "jonction avec le voisin. C'est faisable, à condition de traiter proprement le "
               "solin et la rive. En fond de vallée, l'humidité accélère aussi la mousse.",
         focus=[("Maison de bourg", "Versant unique, raccord mitoyen, zinguerie refaite au droit "
                 "de la limite."),
                ("Démoussage", "Fond de vallée humide, reprise de la mousse plus rapide qu'ailleurs."),
                ("Urgence", "Quatre kilomètres depuis l'atelier : nous sommes là très vite.")],
         autour=["Nonancourt", "La Madeleine-de-Nonancourt", "Dreux", "Muzy",
                 "Saint-Georges-Motel", "Illiers-l'Évêque"],
         faq=[("Mon toit touche celui du voisin, comment fait-on ?",
               "Nous reprenons le solin et la rive au droit de la limite, et nous laissons le "
               "raccord étanche des deux côtés. Le devis précise ce qui est fait sur la limite."),
              ("Vous intervenez vite en cas de fuite ?",
               "C'est l'une des communes les plus proches de l'atelier. En journée, nous sommes "
               "généralement sur place dans l'heure ou deux.")]),

    dict(photo="corps-de-ferme-pierre-depose-couverture.webp", photoalt="Corps de ferme en pierre près d'Anet pendant la dépose de la couverture",
         slug="couvreur-anet", ville="Anet", cp="28260", dep="Eure-et-Loir", km=22,
         title="Couvreur à Anet (28260) · Toiture, zinguerie · WM Couverture",
         desc="Couvreur à Anet et dans la vallée de l'Eure : réfection de couverture, charpente, "
              "gouttières et démoussage. Entreprise familiale basée à Nonancourt.",
         intro="Anet et la vallée de l'Eure sont à une vingtaine de minutes. Nous y intervenons "
               "sur du bâti ancien comme sur du pavillon.",
         bati="Autour du château, le bâti ancien mêle pierre, brique et tuile plate, avec des "
              "toitures à forte pente et des lucarnes travaillées. En s'écartant du bourg, on "
              "retrouve des maisons de vallée et des pavillons en tuile mécanique, plus simples "
              "à traiter mais souvent mal ventilés en sous-toiture.",
         enjeu="Près de l'Eure, l'humidité ambiante accélère la mousse et fatigue les bois de "
               "charpente en pied de versant. C'est le premier endroit que nous regardons. "
               "Aux abords du château, l'aspect de la couverture est encadré : il faut le "
               "vérifier avant tout chiffrage.",
         focus=[("Bâti ancien", "Tuile plate, forte pente, lucarnes et noues à reprendre une par une."),
                ("Pied de versant", "Contrôle des bois d'about, souvent attaqués par l'humidité."),
                ("Zinguerie", "Chéneaux encaissés et descentes en zinc sur les maisons de caractère.")],
         autour=["Ivry-la-Bataille", "Ézy-sur-Eure", "Saint-Georges-Motel", "Bueil",
                 "Garennes-sur-Eure", "Dreux"],
         faq=[("Y a-t-il des contraintes près du château d'Anet ?",
               "Oui, le secteur protégé impose souvent le matériau et l'aspect. Nous vérifions "
               "en mairie avant de chiffrer, pour éviter un refus de déclaration préalable."),
              ("Vous travaillez la tuile plate ancienne ?",
               "Oui. C'est plus long qu'en tuile mécanique parce qu'il y a beaucoup plus de "
               "pièces au mètre carré, et c'est chiffré en conséquence.")]),

    dict(photo="pose-fenetre-de-toit-velux.webp", photoalt="Fenêtre de toit posée sur une couverture à Ivry-la-Bataille",
         slug="couvreur-ivry-la-bataille", ville="Ivry-la-Bataille", cp="27540", dep="Eure", km=24,
         title="Couvreur à Ivry-la-Bataille (27540) · WM Couverture",
         desc="Couvreur à Ivry-la-Bataille et dans la vallée de l'Eure : rénovation de toiture, "
              "charpente, gouttières et démoussage. Entreprise familiale de Nonancourt.",
         intro="Ivry-la-Bataille est au nord-est de notre secteur, dans la vallée de l'Eure. "
               "Nous y montons régulièrement, souvent pour du bâti ancien.",
         bati="Le bourg est resserré le long de la rivière : maisons anciennes en pierre et "
              "brique, toitures en tuile plate, pignons mitoyens et ruelles étroites. Sur les "
              "coteaux, les constructions sont plus récentes et couvertes en tuile mécanique.",
         enjeu="La proximité de l'Eure entretient une humidité permanente. Les mousses reviennent "
               "vite, les bois de rive travaillent, et les chéneaux encaissés des maisons "
               "anciennes se bouchent plus souvent qu'ailleurs. Dans les ruelles, l'accès "
               "conditionne une bonne partie du prix.",
         focus=[("Chéneau encaissé", "Purge, remise en pente et ressoudure du zinc."),
                ("Toiture de bourg", "Accès étroit, échafaudage réduit, protection des mitoyens."),
                ("Démoussage", "Bord de rivière : passage plus fréquent que la moyenne.")],
         autour=["Ézy-sur-Eure", "Anet", "Garennes-sur-Eure", "Bueil", "Saint-Georges-Motel",
                 "Marcilly-sur-Eure"],
         faq=[("L'accès est étroit dans le bourg, est-ce un problème ?",
               "Non, mais cela change le devis. Nous adaptons l'échafaudage et l'évacuation, et "
               "nous le disons dès la visite plutôt que de le découvrir le premier jour."),
              ("Pourquoi mon toit reverdit-il si vite ?",
               "En fond de vallée, l'air reste humide et les versants nord ne sèchent jamais "
               "complètement. Un passage tous les trois ans est plus réaliste qu'un tous les cinq ans.")]),

    dict(photo="charpente-auvent-chene-maison-pierre.webp", photoalt="Charpente en chêne d'un auvent à Verneuil d'Avre et d'Iton",
         slug="couvreur-verneuil-avre-iton", ville="Verneuil d'Avre et d'Iton", cp="27130",
         dep="Eure", km=20,
         title="Couvreur à Verneuil d'Avre et d'Iton (27130) · WM",
         desc="Couvreur à Verneuil d'Avre et d'Iton : rénovation de toiture, charpente, tuile "
              "plate et ardoise, zinguerie, démoussage. Entreprise familiale de Nonancourt.",
         intro="Verneuil est à une vingtaine de kilomètres par la nationale. Le bâti ancien y est "
               "très présent, et il demande de la méthode.",
         bati="Le centre médiéval concentre des maisons à pans de bois, des toitures en tuile "
              "plate de petit format et de l'ardoise sur les édifices les plus hauts. Les pentes "
              "sont fortes, les lucarnes nombreuses, et les charpentes anciennes réservent "
              "souvent des surprises une fois la couverture déposée.",
         enjeu="Sur ce bâti, on ne remplace pas une tuile plate par de la mécanique sans y "
               "réfléchir : le poids, le pureau et l'aspect changent, et le secteur sauvegardé "
               "encadre ce qui est autorisé. Nous chiffrons les deux options quand cela se justifie.",
         focus=[("Tuile plate", "Petit format, beaucoup de pièces au mètre carré, pose lente et soignée."),
                ("Charpente ancienne", "Contrôle pièce par pièce, remplacement ciblé plutôt que dépose."),
                ("Ardoise", "Sur les pignons hauts et les édifices à forte pente.")],
         autour=["Tillières-sur-Avre", "Breteuil", "Nonancourt", "Conches-en-Ouche",
                 "Brezolles", "Damville"],
         faq=[("Puis-je passer de la tuile plate à la tuile mécanique ?",
               "Parfois, hors secteur protégé. Cela allège la charpente et coûte moins cher, "
               "mais l'aspect change beaucoup. Nous vous montrons les deux avant de décider."),
              ("Que se passe-t-il si la charpente est plus abîmée que prévu ?",
               "Nous vous appelons avant de continuer, photos à l'appui, et nous chiffrons la "
               "reprise en avenant. Pas de surprise sur la facture finale.")]),

    dict(photo="couvreur-nonancourt-longere-tuile-neuve.webp", photoalt="Longère de la vallée de l'Avre couverte à neuf près de Tillières",
         slug="couvreur-tillieres-sur-avre", ville="Tillières-sur-Avre", cp="27570",
         dep="Eure", km=11,
         title="Couvreur à Tillières-sur-Avre (27570) · WM Couverture",
         desc="Couvreur à Tillières-sur-Avre : réfection de toiture, charpente, gouttières et "
              "démoussage. Entreprise familiale installée à Nonancourt, à 11 km.",
         intro="Tillières est à une dizaine de kilomètres en remontant l'Avre. C'est un secteur "
               "de maisons anciennes et de longères.",
         bati="Le bourg garde un noyau ancien en pierre et brique, avec des toitures en tuile "
              "plate et quelques ardoises. Autour, la campagne est faite de longères, de "
              "dépendances et de corps de ferme, souvent avec de grandes surfaces de rampant et "
              "des charpentes de belle facture.",
         enjeu="Sur les longères, le mètre carré de rampant grimpe vite et l'état de la charpente "
               "décide de la moitié du budget. C'est pour cela que nous montons voir avant de "
               "chiffrer, plutôt que d'estimer depuis une photo.",
         focus=[("Longère", "Grande surface, faîtage long, souvent plusieurs corps de bâtiment."),
                ("Dépendance", "Bac acier ou tuile selon l'usage, chantier économique."),
                ("Démoussage", "Vallée de l'Avre : versants nord verts en quelques années.")],
         autour=["Nonancourt", "Verneuil d'Avre et d'Iton", "Muzy", "Brezolles",
                 "Illiers-l'Évêque", "Damville"],
         faq=[("Vous couvrez aussi les dépendances et les granges ?",
               "Oui. Sur un bâtiment non habité, le bac acier revient beaucoup moins cher que la "
               "tuile et se pose en quelques jours."),
              ("Peut-on faire le chantier en deux fois ?",
               "Sur une longère, oui : nous traitons un corps de bâtiment, puis l'autre. Cela "
               "étale la dépense sans laisser la maison à découvert.")]),

    dict(photo="toiture-tuile-brune-fenetre-de-toit.webp", photoalt="Toiture en tuile avec fenêtre de toit à Brezolles",
         slug="couvreur-brezolles", ville="Brezolles", cp="28270", dep="Eure-et-Loir", km=14,
         title="Couvreur à Brezolles (28270) · Toiture · WM Couverture",
         desc="Couvreur à Brezolles et dans le Thymerais : rénovation de toiture, charpente, "
              "gouttières et démoussage. Entreprise familiale de Nonancourt, à 14 km.",
         intro="Brezolles est à un quart d'heure au sud. Le bourg et les villages du Thymerais "
               "font partie de notre secteur habituel.",
         bati="Le bourg aligne des maisons anciennes en brique et silex, couvertes en tuile plate "
              "ou mécanique, avec quelques toitures en ardoise. La campagne du Thymerais est "
              "faite de fermes et de dépendances aux grandes toitures simples.",
         enjeu="Le plateau est plus venté que la vallée. Les tuiles de rive et les faîtages se "
               "descellent plus souvent, et c'est la première chose que nous contrôlons après un "
               "coup de vent. Les fermes isolées demandent aussi de prévoir l'accès des engins.",
         focus=[("Faîtage et rives", "Rescellement après coup de vent, closoir ventilé posé à sec."),
                ("Grande toiture agricole", "Surfaces simples, chantier rapide, bac acier possible."),
                ("Réfection de bourg", "Tuile plate ou mécanique selon ce qu'autorise le PLU.")],
         autour=["Nonancourt", "Dreux", "Châteauneuf-en-Thymerais", "Tillières-sur-Avre",
                 "Verneuil d'Avre et d'Iton", "Senonches"],
         faq=[("Le vent a descellé mon faîtage, c'est urgent ?",
               "Oui. Un faîtage descellé se soulève au coup de vent suivant et emporte les tuiles "
               "voisines. Nous passons le rescellement en priorité."),
              ("Vous montez sur les bâtiments agricoles ?",
               "Oui, y compris sur les grandes toitures de hangar. Il nous faut simplement un "
               "accès dégagé pour l'échafaudage ou la nacelle.")]),

    dict(photo="echafaudage-bache-maison-de-ville.webp", photoalt="Échafaudage bâché sur une maison de ville à Nogent-le-Roi",
         slug="couvreur-nogent-le-roi", ville="Nogent-le-Roi", cp="28210",
         dep="Eure-et-Loir", km=30,
         title="Couvreur à Nogent-le-Roi (28210) · WM Couverture",
         desc="Couvreur à Nogent-le-Roi et dans la vallée de l'Eure : réfection de toiture, "
              "charpente, zinguerie et démoussage. Entreprise familiale de Nonancourt.",
         intro="Nogent-le-Roi marque la limite est de notre secteur, à une trentaine de "
               "kilomètres. Nous nous y déplaçons pour les chantiers de rénovation.",
         bati="Le centre ancien mêle pierre, brique et pans de bois, avec des toitures en tuile "
              "plate et des pentes marquées. Les extensions plus récentes, le long de la vallée "
              "de l'Eure, sont en tuile mécanique sur charpente industrielle.",
         enjeu="Comme partout dans la vallée, l'humidité et les arbres accélèrent la mousse. Sur "
               "le bâti ancien du centre, l'enjeu est surtout de conserver l'aspect tout en "
               "remettant une sous-toiture correcte, ce qui suppose de déposer complètement.",
         focus=[("Réfection complète", "Dépose, écran de sous-toiture, repose à l'identique."),
                ("Zinguerie de bourg", "Chéneaux, descentes et raccords sur mitoyen."),
                ("Entretien annuel", "Purge des gouttières et contrôle après l'automne.")],
         autour=["Dreux", "Vernouillet", "Anet", "Châteauneuf-en-Thymerais",
                 "Bueil", "Garennes-sur-Eure"],
         faq=[("Vous venez jusqu'à Nogent-le-Roi pour un petit dépannage ?",
               "Pour une fuite, oui. Pour une purge de gouttière seule, nous essayons de la "
               "grouper avec un autre chantier du secteur pour ne pas vous facturer le trajet."),
              ("Peut-on garder l'aspect d'origine du toit ?",
               "Oui. Nous reposons à l'identique quand la tuile est récupérable, en ajoutant "
               "l'écran de sous-toiture qui manquait.")]),

    dict(photo="refection-toiture-pavillon-terminee.webp", photoalt="Toiture entièrement refaite sur une maison de Breteuil",
         slug="couvreur-breteuil", ville="Breteuil", cp="27160", dep="Eure", km=32,
         title="Couvreur à Breteuil (27160) · Toiture · WM Couverture",
         desc="Couvreur à Breteuil et dans le pays d'Ouche : rénovation de toiture, charpente, "
              "zinguerie et démoussage. Entreprise familiale installée à Nonancourt.",
         intro="Breteuil est à l'ouest de notre secteur, à une trentaine de kilomètres. Nous y "
               "intervenons surtout pour des rénovations complètes.",
         bati="Le bourg et les villages alentour comptent beaucoup de maisons anciennes en brique "
              "et silex, avec des toitures en tuile plate et de longues charpentes. Les "
              "constructions récentes sont en tuile mécanique sur fermettes.",
         enjeu="Le pays d'Ouche est boisé et humide : les toits verdissent plus vite qu'ailleurs "
               "et les feuilles bouchent les gouttières chaque automne. Sur les maisons "
               "anciennes, la charpente mérite un vrai contrôle avant de décider du budget.",
         focus=[("Rénovation complète", "Dépose, contrôle de charpente, couverture et zinguerie neuves."),
                ("Démoussage", "Secteur boisé : mousse et feuilles reviennent chaque année."),
                ("Gouttières", "Pose de crapaudines et purge d'automne.")],
         autour=["Verneuil d'Avre et d'Iton", "Conches-en-Ouche", "Damville",
                 "Tillières-sur-Avre", "Nonancourt", "Évreux"],
         faq=[("Vous vous déplacez jusqu'à Breteuil pour un devis ?",
               "Oui, et il reste gratuit. Nous groupons simplement la visite avec un autre "
               "rendez-vous du secteur quand c'est possible."),
              ("Mes gouttières se bouchent chaque automne, que faire ?",
               "Des crapaudines à l'entrée des descentes et une purge annuelle. C'est peu cher "
               "et cela évite les débordements qui abîment la façade.")]),

    dict(photo="couvreur-dreux-maison-de-ville-toiture.webp", photoalt="Maison de faubourg à Évreux avec toiture et façade reprises",
         slug="couvreur-evreux", ville="Évreux", cp="27000", dep="Eure", km=35,
         title="Couvreur à Évreux (27000) · Toiture, zinguerie · WM",
         desc="Couvreur à Évreux : rénovation de toiture, charpente, zinguerie et démoussage. "
              "Entreprise familiale de Nonancourt, 14 ans d'expérience, devis gratuit.",
         intro="Évreux est la limite nord de notre secteur, à environ trente-cinq kilomètres. "
               "Nous nous y déplaçons pour les chantiers de rénovation complète.",
         bati="La ville mêle des quartiers reconstruits après-guerre, souvent en tuile mécanique "
              "et en ardoise, des maisons de faubourg plus anciennes en brique et silex, et des "
              "lotissements récents en périphérie. Les surfaces sont variées et les accès en "
              "général plus simples qu'en centre médiéval.",
         enjeu="Sur les toitures de la reconstruction, la question qui revient est l'isolation. "
               "Refaire la couverture est le seul moment où l'on peut traiter correctement "
               "l'écran de sous-toiture et les rampants par l'extérieur. Autant en profiter.",
         focus=[("Toiture d'après-guerre", "Couverture en fin de vie, sous-toiture absente, "
                 "isolation à reprendre."),
                ("Maison de faubourg", "Brique et silex, tuile plate, lucarnes à reprendre."),
                ("Toiture-terrasse", "Étanchéité et isolation sur les extensions et garages.")],
         autour=["Conches-en-Ouche", "Damville", "Breteuil", "Garennes-sur-Eure",
                 "Marcilly-sur-Eure", "Nonancourt"],
         faq=[("Vous intervenez vraiment jusqu'à Évreux ?",
               "Oui, pour les chantiers de rénovation. Pour un simple dépannage, nous vous le "
               "dirons franchement si un couvreur plus proche est plus pertinent."),
              ("Peut-on isoler par l'extérieur en refaisant le toit ?",
               "Oui, c'est le moment idéal : on pose l'isolant sur les chevrons sans perdre de "
               "hauteur sous plafond. Nous le chiffrons en option sur le devis.")]),
]

# ────────────────────────────────────────────────────────────── guides ─────
# Contenu informatif : ce que les gens cherchent AVANT de chercher un couvreur.
# Chaque guide s'ouvre sur une reponse courte : c'est ce passage que les moteurs
# generatifs citent, et ce que Google remonte en extrait.
GUIDES = [
    dict(
        slug="prix-refection-toiture",
        cle="Un toit ne se mesure pas au sol. Il se mesure en rampant.",
        img="couvreur-pose-tuiles-refection.webp", imgalt="Couvreur posant des tuiles neuves sur les liteaux d'une toiture en réfection",
        nav="Prix d'une réfection de toiture",
        title="Prix d'une réfection de toiture au m2",
        desc="Une réfection de toiture coûte 100 à 300 € le m² de rampant selon les comparateurs. Ce qui fait varier ce prix, et comment comparer deux devis.",
        h1=("Prix d'une <em>réfection</em>", "de toiture : comment ça se calcule"),
        court="Les comparateurs nationaux situent une réfection de toiture entre "
              "<b>100 et 300 € le mètre carré de rampant</b> en 2026, et de 150 à 500 € quand "
              "l'isolation ou la charpente entrent dans le chantier. Attention au piège : ce prix "
              "s'applique à la <b>surface de rampant</b>, la surface réelle des pans du toit, "
              "pas à la surface au sol de la maison, qui est toujours plus petite.",
        estim=True,
        sections=[
            ("Les fourchettes publiées, et ce qu'elles valent",
             ["Voici ce qu'annoncent les principaux comparateurs français en 2026, pour une "
              "réfection de toiture par un professionnel, hors cas particuliers.",
              "<b>Réfection simple</b>, dépose et couverture neuve : de 100 à 200 € le mètre carré "
              "de rampant selon LaPrimeEnergie, de 130 à 260 € selon illiCO travaux, de 120 à "
              "300 € selon La Maison des Travaux.",
              "<b>Réfection avec isolation</b> : de 150 à 450 € le mètre carré. "
              "<b>Avec reprise de charpente</b> en plus : jusqu'à 500 €.",
              "<b>Charpente et couverture ensemble</b>, sur du neuf : de 180 à 250 € le mètre "
              "carré selon helloArtisan. <b>Toiture en zinc</b> : de 150 à 300 € selon Camif "
              "Habitat.",
              "<b>Ces chiffres ne sont pas nos tarifs.</b> Ce sont des moyennes nationales, tous "
              "matériaux et toutes régions confondus. Elles vous servent à savoir si un devis est "
              "dans le marché ou complètement à côté, rien de plus. Notre prix à nous sort d'une "
              "visite sur votre toit, pas d'un tableau.",
              "Et surtout : un écart de 100 à 500 € au mètre carré, c'est un facteur cinq. "
              "Autrement dit, la fourchette ne vous dit presque rien tant que vous ne savez pas "
              "ce qui, chez vous, fait pencher la balance. C'est l'objet de la suite."]),
            ("Réparer ou refaire : comment trancher",
             ["La question se pose dès qu'un devis de réfection dépasse ce que vous imaginiez. "
              "Trois critères suffisent à décider.",
              "<b>L'âge et l'homogénéité.</b> Si la couverture a le même âge partout et dépasse "
              "quarante ans, réparer revient à repousser de deux ou trois ans un chantier qui "
              "coûtera pareil, plus l'échafaudage payé deux fois.",
              "<b>L'état de la tuile elle-même.</b> Une tuile qui se casse quand on la manipule, "
              "ou qui reste humide plusieurs jours après la pluie, est poreuse. On ne répare pas "
              "un toit dont le matériau est en fin de vie, on le remplace.",
              "<b>Ce qu'il y a dessous.</b> S'il n'y a pas d'écran de sous-toiture et que vous "
              "comptez isoler les combles un jour, autant tout faire au même moment. Poser "
              "l'écran suppose de déposer, et déposer deux fois n'a aucun sens.",
              "À l'inverse, si la couverture est saine et que le problème vient d'un solin, d'une "
              "noue ou d'une dizaine de tuiles, réparez. Nous vous le dirons franchement plutôt "
              "que de vendre une réfection dont vous n'avez pas besoin."]),
            ("Pourquoi la surface au sol ne suffit pas",
             ["Une maison de 100 m² au sol n'a jamais 100 m² de toit. Le toit est incliné, donc "
              "chaque pan est plus long que sa projection au sol. Plus la pente est forte, plus "
              "l'écart grandit.",
              "À 30 degrés, comptez environ 15 % de surface en plus. À 45 degrés, plus de 40 %. "
              "C'est la première raison pour laquelle deux devis peuvent sembler incohérents : "
              "ils ne parlent pas de la même surface.",
              "Le calculateur ci-dessus fait la conversion. Il donne un ordre de grandeur, pas "
              "un métré : un vrai relevé se fait sur place, avec les débords, les lucarnes et "
              "les noues."]),
            ("Les postes qui composent un devis",
             ["<b>La dépose.</b> Retirer l'ancienne couverture, la trier, l'évacuer en déchetterie "
              "professionnelle. Ce poste dépend du matériau en place et de l'accès. Une toiture "
              "amiantée relève d'une entreprise agréée et change complètement le budget.",
              "<b>L'échafaudage.</b> Souvent sous-estimé. Sur une maison de plain-pied avec du "
              "terrain autour, il est simple. En centre-ville, il faut une autorisation "
              "d'occupation du domaine public, un montage plus long et une protection des "
              "passants.",
              "<b>La charpente.</b> Contrôlée une fois la couverture déposée. Un bon devis la "
              "chiffre séparément, en indiquant un prix unitaire par pièce remplacée, pour que "
              "vous sachiez à quoi vous vous engagez.",
              "<b>L'écran de sous-toiture.</b> Absent sur presque toutes les toitures d'avant les "
              "années 80. C'est lui qui protège quand une tuile bouge. Le poser suppose de "
              "déposer entièrement, donc c'est maintenant ou jamais.",
              "<b>La couverture.</b> Le matériau, mais aussi le nombre de pièces au mètre carré. "
              "Une tuile plate demande trois à quatre fois plus de manipulations qu'une tuile "
              "mécanique.",
              "<b>La zinguerie.</b> Rives, faîtage, solins de cheminée, gouttières. Refaire le "
              "toit sans reprendre la zinguerie n'a pas de sens : c'est elle qui décide où part "
              "l'eau."]),
            ("Ce qui fait vraiment varier le prix d'une maison à l'autre",
             ["<b>La complexité du toit.</b> Un rectangle à deux pans coûte beaucoup moins cher au "
              "mètre carré qu'un toit à quatre pans avec trois lucarnes, deux cheminées et une "
              "noue. Chaque point singulier ajoute de la découpe et de la zinguerie.",
              "<b>L'accès.</b> Camion au pied du chantier ou brouettage à trente mètres, ce n'est "
              "pas le même chantier.",
              "<b>Les contraintes d'urbanisme.</b> En secteur protégé, le matériau et la teinte "
              "peuvent être imposés. Cela ne se négocie pas et cela se chiffre.",
              "<b>La saison.</b> Un chantier posé en plein hiver prend plus de jours à surface "
              "égale, à cause des intempéries."]),
            ("Comment comparer deux devis honnêtement",
             ["Demandez que la <b>surface de rampant</b> figure sur le devis. Sans elle, vous "
              "comparez des totaux, pas des prix.",
              "Vérifiez que la <b>dépose et l'évacuation</b> sont incluses, et pas renvoyées à une "
              "ligne « à définir ».",
              "Vérifiez que <b>l'échafaudage</b> est chiffré. Un devis qui l'oublie n'est pas moins "
              "cher, il est incomplet.",
              "Regardez si <b>l'écran de sous-toiture</b> est prévu, et lequel. Un HPV n'a pas le "
              "même prix ni la même durée qu'un film bas de gamme.",
              "Demandez le <b>prix unitaire de reprise de charpente</b>, pour ne pas découvrir un "
              "avenant surprise au milieu du chantier.",
              "Exigez l'<b>attestation d'assurance décennale</b> en cours de validité. C'est votre "
              "seule protection pendant dix ans."]),
        ],
        faq=[("Le devis d'un couvreur est-il payant ?",
              "Chez nous, non : le déplacement et le chiffrage sont gratuits, sans engagement. "
              "Certaines entreprises facturent un diagnostic détaillé, ce doit être annoncé avant."),
             ("Faut-il refaire tout le toit ou seulement un versant ?",
              "Si un seul versant est en cause et que l'autre est sain, on peut n'en refaire qu'un. "
              "Sur une couverture homogène qui a le même âge partout, tout refaire coûte moins cher "
              "au mètre carré que revenir deux fois."),
             ("Peut-on étaler le paiement ?",
              "Oui. Nous acceptons le règlement en plusieurs fois sur les gros chantiers, calé sur "
              "l'avancement et écrit sur le devis."),
             ("Combien de temps dure une couverture neuve ?",
              "Quarante à cinquante ans pour une tuile mécanique bien posée, davantage pour "
              "l'ardoise. Un démoussage tous les trois à cinq ans allonge nettement cette durée."),
             ("Quel est le prix pour refaire une toiture de 100 m² ?",
              "Attention, 100 m² au sol font environ 115 à 140 m² de rampant selon la pente. Sur "
              "la base des fourchettes publiées, cela place le chantier entre 12 000 et 40 000 € "
              "selon le matériau, la complexité du toit et l'état de la charpente. C'est un ordre "
              "de grandeur national, pas un devis."),
             ("Quel est le prix à l'heure d'un couvreur ?",
              "La profession chiffre au mètre carré ou au forfait, pas à l'heure, sauf pour un "
              "dépannage. Une entreprise qui ne sait vous répondre qu'à l'heure sur une réfection "
              "n'a probablement pas pris les mesures."),
             ("Quel est le revêtement de toiture le moins cher ?",
              "Le bac acier, de loin, mais il ne convient pas à toutes les maisons ni à tous les "
              "règlements d'urbanisme. Le comparatif complet est dans notre guide sur le choix du "
              "matériau."),
             ("Comment savoir si un couvreur est sérieux ?",
              "Quatre vérifications : une attestation d'assurance décennale en cours de validité, "
              "un devis détaillé ligne par ligne avec la surface de rampant, un numéro SIRET "
              "vérifiable, et des avis récents. Méfiez-vous de tout acompte demandé avant devis "
              "écrit.")],
        cta=("Faire chiffrer votre toiture", "renovation-toiture"),
    ),
    dict(
        slug="fuite-toiture-que-faire",
        cle="La tache au plafond n'est presque jamais sous la fuite.",
        img="toiture-alteree-lichens.webp", imgalt="Toiture ancienne altérée, couverte de lichens",
        nav="Fuite de toiture : que faire",
        title="Fuite de toiture : que faire en urgence",
        desc="Les bons gestes en cas de fuite de toiture, comment limiter les dégâts avant "
             "l'arrivée du couvreur, et d'où viennent les infiltrations le plus souvent.",
        h1=("Fuite de toiture :", "<em>que faire</em> en urgence"),
        court="Coupez l'électricité de la pièce touchée, écartez les meubles, posez un récipient, "
              "et <b>percez le plafond au point le plus bas si l'eau s'accumule</b> : mieux vaut "
              "un trou de dix centimètres qu'un plafond qui s'effondre. Ne montez pas sur le toit "
              "sous la pluie. Appelez un couvreur pour une mise hors d'eau, la réparation "
              "définitive viendra ensuite.",
        estim=False,
        sections=[
            ("Après la réparation : ce qu'il reste à faire",
             ["Le toit est réparé, mais l'eau qui est entrée est encore là. C'est la deuxième "
              "moitié du problème, et celle qu'on néglige le plus.",
              "<b>Ouvrez et ventilez.</b> Un isolant en laine gorgé d'eau ne sèche pas tout seul "
              "sous un plafond fermé. S'il a été mouillé, il a perdu son pouvoir isolant et il "
              "faut le remplacer, pas le laisser sécher en espérant.",
              "<b>Surveillez le bois.</b> Une charpente mouillée une fois ne pourrit pas. Une "
              "charpente humide pendant des semaines, oui, et les champignons lignivores "
              "s'installent sans bruit. Un contrôle quelques mois plus tard vaut la peine.",
              "<b>Attendez avant de repeindre.</b> Refaire le plafond sur un support encore humide "
              "garantit une auréole qui revient. Comptez plusieurs semaines de séchage, davantage "
              "en hiver."]),
            ("Les cinq gestes, dans l'ordre",
             ["<b>1. Coupez l'électricité de la zone.</b> L'eau qui coule le long d'un plafond "
              "atteint souvent un point lumineux ou une gaine avant d'être visible.",
              "<b>2. Dégagez et protégez.</b> Meubles, tapis, appareils. Une bâche plastique coûte "
              "moins cher qu'un parquet.",
              "<b>3. Récupérez l'eau.</b> Un seau, et une ficelle tendue depuis le point de chute "
              "jusque dans le seau si l'eau éclabousse.",
              "<b>4. Percez si le plafond gonfle.</b> Une poche d'eau dans un placo finit toujours "
              "par lâcher d'un coup. Un trou volontaire au point bas évite l'effondrement.",
              "<b>5. Photographiez tout.</b> Avant de nettoyer. Votre assurance en aura besoin."]),
            ("Ce qu'il ne faut surtout pas faire",
             ["<b>Monter sur le toit sous la pluie ou dans le vent.</b> Une tuile mouillée est une "
              "patinoire, et c'est chaque année la cause de chutes graves.",
              "<b>Colmater au mastic depuis l'intérieur.</b> Cela déplace le problème sans le "
              "régler, et cela masque le point d'entrée pour celui qui viendra chercher.",
              "<b>Attendre que ça sèche.</b> Une infiltration qui a mouillé un isolant le laisse "
              "gorgé d'eau pendant des semaines. Le bois de charpente autour travaille et pourrit."]),
            ("D'où viennent les fuites, dans l'ordre de fréquence",
             ["<b>Le solin de cheminée.</b> C'est la première cause. Le mastic sèche, se rétracte, "
              "et l'eau passe entre la maçonnerie et la couverture. La tache au plafond apparaît "
              "souvent à plusieurs mètres du conduit, parce que l'eau court le long d'un chevron "
              "avant de tomber.",
              "<b>Une tuile déplacée.</b> Un coup de vent soulève une tuile, la suivante ne "
              "recouvre plus. Sans écran de sous-toiture, l'eau tombe directement dans les combles.",
              "<b>La noue.</b> L'angle rentrant entre deux versants concentre toute l'eau du toit. "
              "Encrassée ou percée, elle déborde sous la couverture au premier gros orage.",
              "<b>Les pénétrations.</b> Sortie de VMC, chatière, passage d'antenne, fenêtre de "
              "toit : chaque trou dans la couverture est un point à contrôler.",
              "<b>La gouttière.</b> Une gouttière bouchée déborde vers l'arrière, sous la première "
              "rangée de tuiles, et mouille le mur et le bas de charpente."]),
            ("Ce que couvre l'assurance",
             ["Pour un <b>événement climatique</b> (tempête, grêle, poids de la neige), la garantie "
              "s'applique le plus souvent, sous conditions de contrat. Déclarez vite, en général "
              "dans les cinq jours ouvrés.",
              "Pour une <b>usure normale</b>, non : l'assurance ne finance pas l'entretien. Une "
              "toiture en fin de vie reste à votre charge.",
              "Les <b>dégâts intérieurs</b> (plafond, peinture, mobilier) relèvent de la garantie "
              "dégâts des eaux, indépendamment de la réparation du toit.",
              "Dans tous les cas, gardez la facture de la mise hors d'eau : elle fait partie des "
              "mesures conservatoires, et elle est en général prise en charge."]),
        ],
        faq=[("Vous intervenez la nuit pour une fuite ?",
              "Oui, l'astreinte est ouverte 24 h/24. En pleine nuit et sous la pluie, monter est "
              "dangereux : nous protégeons l'intérieur, puis nous bâchons dès que c'est praticable."),
             ("Combien de temps tient une bâche ?",
              "Une bâche posée correctement, lestée et fixée, tient plusieurs semaines. Ce n'est "
              "pas une réparation : elle vous laisse le temps de décider au calme."),
             ("La tache au plafond est loin de la cheminée, est-ce quand même elle ?",
              "Très souvent, oui. L'eau suit la pente d'un chevron ou d'un liteau avant de tomber. "
              "C'est pour cela que la recherche de fuite se fait sur le toit."),
             ("Faut-il refaire tout le toit après une fuite ?",
              "Pas forcément. Si la couverture est saine et que la cause est ponctuelle, une "
              "réparation suffit. Nous vous le disons franchement plutôt que de vendre une "
              "réfection dont vous n'avez pas besoin.")],
        cta=("Appeler pour une urgence", "depannage-toiture"),
    ),
    dict(
        slug="demoussage-toiture-frequence",
        cle="La mousse ne salit pas la tuile. Elle la fait éclater.",
        img="tuiles-mousse-vegetation.webp", imgalt="Tuiles envahies de mousse et de végétation",
        nav="Démousser son toit : quand et comment",
        title="Démoussage de toiture : quand et comment",
        desc="À quelle fréquence démousser une toiture, quelle méthode, faut-il un hydrofuge. "
             "Les risques de la haute pression mal dosée et le bon rythme d'entretien.",
        h1=("Démousser son toit :", "<em>quand</em> et comment"),
        court="Dans une région humide comme la vallée de l'Avre, comptez un <b>démoussage tous les "
              "trois à cinq ans</b> et un contrôle visuel chaque année. La mousse retient l'eau "
              "contre la tuile, la gèle en hiver et la fait éclater. C'est l'entretien le moins "
              "cher du bâtiment, et celui qui repousse le plus loin une réfection complète.",
        estim=False,
        sections=[
            ("Ce qu'un démoussage ne règle pas",
             ["Un toit propre n'est pas forcément un toit sain, et c'est une confusion qui coûte "
              "cher au moment de la revente.",
              "<b>Une tuile poreuse reste poreuse.</b> Le nettoyage retire la mousse, il ne "
              "reconstitue pas le matériau. Si la tuile est arrivée en fin de vie, le démoussage "
              "améliore l'aspect quelques années, pas l'étanchéité.",
              "<b>Un solin fendu reste fendu.</b> C'est la première cause de fuite, et aucun "
              "traitement de surface ne la corrige. C'est pour cela que nous contrôlons les points "
              "singuliers pendant le passage : autant repérer le problème quand on est déjà là.",
              "<b>Une charpente attaquée reste attaquée.</b> Le démoussage se voit depuis la rue, "
              "l'état des bois non. Si votre maison a plus de cinquante ans et que personne n'est "
              "monté dans les combles depuis longtemps, faites regarder."]),
            ("Pourquoi la mousse abîme vraiment un toit",
             ["La mousse n'est pas qu'un problème d'aspect. Elle se comporte comme une éponge posée "
              "sur la couverture : elle retient l'eau au contact de la tuile au lieu de la laisser "
              "ruisseler.",
              "En hiver, cette eau gèle. Elle augmente de volume dans les micro-fissures de la "
              "tuile et les élargit. Après quelques cycles de gel et dégel, la tuile éclate en "
              "surface, devient poreuse, et absorbe encore plus d'eau. Le phénomène s'auto-entretient.",
              "En parallèle, les fragments de mousse descendent avec la pluie et bouchent les "
              "gouttières. Une gouttière bouchée déborde vers l'arrière et mouille le mur, le bas "
              "de charpente et les fondations."]),
            ("À quelle fréquence, selon votre situation",
             ["<b>Tous les trois ans</b> si votre toit est au nord, à l'ombre d'arbres, ou en fond "
              "de vallée. C'est le cas de beaucoup de maisons entre Nonancourt et Ivry-la-Bataille.",
              "<b>Tous les cinq ans</b> si le toit est dégagé, bien exposé et sans végétation "
              "proche.",
              "<b>Un contrôle visuel chaque année</b> dans tous les cas, idéalement en fin "
              "d'automne, quand les feuilles sont tombées. Depuis le sol, aux jumelles, cela prend "
              "dix minutes."]),
            ("Comment se passe un démoussage correct",
             ["<b>D'abord regarder.</b> Une couverture déjà poreuse ou fendue ne se nettoie pas à "
              "la même pression qu'une tuile saine. Sur certaines toitures anciennes, on travaille "
              "à la brosse et au traitement, sans jet.",
              "<b>Le nettoyage.</b> Toujours dans le sens de la pente, jamais sous la tuile, à une "
              "pression adaptée au matériau. Une haute pression mal dosée décape l'engobe, cette "
              "fine couche qui protège la tuile, et accélère le vieillissement au lieu de le freiner.",
              "<b>Le traitement anti-mousse.</b> Pulvérisé sur toute la surface après le nettoyage. "
              "Il continue d'agir plusieurs semaines et tue les racines que le jet n'a pas "
              "emportées. Sans lui, la mousse revient deux fois plus vite.",
              "<b>Les gouttières et les abords.</b> Purge des chéneaux et des descentes dans la "
              "foulée, puis nettoyage au sol. Les résidus ne doivent pas rester dans le jardin."]),
            ("L'hydrofuge : utile ou pas",
             ["Un hydrofuge est un produit qui limite l'absorption d'eau par la tuile. Sur une "
              "<b>couverture saine</b>, il ralentit la reprise de la mousse et fait gagner quelques "
              "années entre deux passages. C'est un vrai plus.",
              "Sur une <b>tuile déjà poreuse ou fendue</b>, il masque le problème au lieu de le "
              "régler. Il donne un bel aspect quelques mois, et la couverture continue de se "
              "dégrader dessous.",
              "Méfiez-vous des hydrofuges colorés vendus comme une seconde jeunesse : ils "
              "repeignent un toit fatigué. Si l'on vous propose un hydrofuge sans avoir monté "
              "regarder l'état des tuiles, changez d'interlocuteur."]),
        ],
        faq=[("La haute pression abîme-t-elle les tuiles ?",
              "Mal dosée, oui : elle décape l'engobe et rend la tuile poreuse. Bien dosée et "
              "orientée dans le sens de la pente, non."),
             ("Peut-on démousser soi-même ?",
              "Techniquement oui, mais c'est la première cause de chute domestique grave. Une "
              "toiture mouillée ne pardonne pas, et un démoussage professionnel coûte moins cher "
              "qu'une semaine d'arrêt."),
             ("Faut-il être présent le jour de l'intervention ?",
              "Non, du moment que nous avons accès au terrain et à un point d'eau. Nous envoyons "
              "les photos avant et après."),
             ("Le produit est-il dangereux pour les plantes ?",
              "Nous bâchons les massifs sensibles et nous rinçons les abords. Les produits "
              "professionnels sont prévus pour un usage en toiture habitée.")],
        cta=("Faire démousser votre toit", "demoussage-toiture"),
    ),
    dict(
        slug="aides-renovation-toiture",
        cle="Refaire un toit, c'est de l'entretien. L'isoler, c'est de la rénovation énergétique.",
        img="toits-village-normand-aides.webp", imgalt="Toits d'ardoise et cheminées de brique d'un bourg normand",
        nav="Aides et TVA pour refaire son toit",
        title="Aides et TVA pour refaire sa toiture",
        desc="TVA à 5,5 % ou 10 %, MaPrimeRénov', CEE, éco-PTZ : les dispositifs qui existent "
             "pour une rénovation de toiture, et ce qui conditionne leur obtention.",
        h1=("Aides et TVA", "pour <em>refaire son toit</em>"),
        court="Une réfection de toiture chez un particulier bénéficie d'une <b>TVA réduite</b> : "
              "10 % pour des travaux d'entretien ou d'amélioration dans un logement de plus de "
              "deux ans, et 5,5 % lorsque les travaux relèvent de la rénovation énergétique, "
              "typiquement l'isolation de la toiture. Les aides publiques, elles, portent presque "
              "toujours sur l'<b>isolation</b>, pas sur la couverture seule.",
        estim=False,
        sections=[
            ("Le cas du logement loué et de la copropriété",
             ["<b>Si vous louez le logement</b>, les travaux d'isolation restent à votre charge de "
              "propriétaire, et ils sont déductibles de vos revenus fonciers au régime réel. "
              "Certaines aides sont ouvertes aux bailleurs, parfois avec un engagement de "
              "modération du loyer ou de durée de location.",
              "<b>En copropriété</b>, la toiture est une partie commune : la décision se prend en "
              "assemblée générale, pas seule. Il existe des dispositifs pensés pour les "
              "copropriétés, mais ils supposent un vote et souvent un accompagnement.",
              "Dans les deux cas, le devis doit être établi au nom de la personne ou de la "
              "structure qui demande l'aide. Une facture au mauvais nom fait tomber le dossier."]),
            ("La distinction qui change tout : couverture ou isolation",
             ["C'est le point que presque personne ne comprend au départ. <b>Refaire une couverture "
              "n'est pas un geste de rénovation énergétique.</b> Remplacer des tuiles usées par des "
              "tuiles neuves n'améliore pas la performance thermique du logement, donc cela "
              "n'ouvre pas droit aux aides énergie.",
              "<b>Isoler la toiture, si.</b> Isolation des combles perdus, isolation sous rampants, "
              "isolation par l'extérieur au moment de la dépose : ce sont des gestes reconnus, et "
              "ce sont eux qui déclenchent les dispositifs.",
              "D'où le bon réflexe : si votre toiture doit être refaite, c'est le moment de traiter "
              "l'isolation en même temps. C'est le seul moment où l'on peut le faire par "
              "l'extérieur sans perdre de hauteur sous plafond, et c'est ce qui rend le chantier "
              "éligible."]),
            ("La TVA réduite, l'avantage le plus simple à obtenir",
             ["<b>TVA à 10 %</b> pour les travaux d'entretien, d'amélioration ou de transformation "
              "d'un logement achevé depuis plus de deux ans. Une réfection de couverture entre "
              "dans ce cadre.",
              "<b>TVA à 5,5 %</b> pour les travaux de rénovation énergétique et les travaux "
              "induits qui leur sont indissociablement liés. L'isolation de la toiture en fait "
              "partie.",
              "Dans les deux cas, c'est l'entreprise qui applique le taux directement sur la "
              "facture. Vous n'avez rien à avancer ni à réclamer : il vous suffit de signer une "
              "attestation confirmant l'ancienneté et l'usage du logement."]),
            ("Les dispositifs à connaître",
             ["<b>MaPrimeRénov'.</b> Aide de l'État versée par l'Anah, réservée aux gestes de "
              "rénovation énergétique et conditionnée aux revenus du foyer. Elle suppose de passer "
              "par une entreprise qualifiée pour le geste concerné.",
              "<b>Les CEE, certificats d'économies d'énergie.</b> Financés par les fournisseurs "
              "d'énergie, cumulables avec MaPrimeRénov'. Ils portent eux aussi sur l'isolation.",
              "<b>L'éco-prêt à taux zéro.</b> Un prêt sans intérêts pour financer des travaux de "
              "rénovation énergétique, utile quand l'aide ne couvre qu'une partie du chantier.",
              "<b>Les aides locales.</b> Département, intercommunalité, parfois la commune. Elles "
              "sont peu connues et rarement cumulées avec le reste par oubli. Renseignez-vous "
              "auprès de votre mairie."]),
            ("Les trois pièges à éviter",
             ["<b>Signer avant l'accord.</b> Pour la plupart des aides, le devis doit être signé "
              "après le dépôt de la demande. Un chantier commencé trop tôt n'est plus éligible.",
              "<b>Le démarchage téléphonique.</b> Le démarchage pour la rénovation énergétique est "
              "interdit. Une entreprise qui vous appelle pour vous proposer une isolation "
              "subventionnée est déjà hors la loi : ne signez rien.",
              "<b>L'offre à un euro.</b> Les offres miracles se sont soldées par des isolations "
              "bâclées et des dossiers refusés. Un chantier correct a un prix, l'aide en enlève "
              "une partie, elle ne le rend pas gratuit."]),
            ("Où vérifier, parce que les règles bougent",
             ["Les montants, les plafonds de revenus et les conditions changent au moins une fois "
              "par an. Ne vous fiez à aucun site commercial, y compris celui-ci, pour un chiffre "
              "précis.",
              "Les deux sources fiables sont <b>france-renov.gouv.fr</b>, le service public de la "
              "rénovation de l'habitat, et votre <b>conseiller France Rénov'</b> local, qui est "
              "gratuit et indépendant. Un rendez-vous avec lui avant de signer fait souvent gagner "
              "plusieurs milliers d'euros."]),
        ],
        faq=[("Refaire ma toiture ouvre-t-il droit à MaPrimeRénov' ?",
              "La couverture seule, non. L'isolation réalisée en même temps, oui, sous conditions "
              "de revenus et de qualification de l'entreprise."),
             ("Quel taux de TVA sur mon devis ?",
              "10 % pour une réfection de couverture dans un logement de plus de deux ans, 5,5 % "
              "sur la partie isolation et les travaux qui en découlent directement."),
             ("Faut-il une entreprise RGE ?",
              "Pour les aides à la rénovation énergétique, oui : la qualification est exigée pour "
              "le geste concerné. Pour une réfection de couverture financée sans aide, non."),
             ("Peut-on cumuler plusieurs aides ?",
              "MaPrimeRénov' et les CEE se cumulent en général, et l'éco-PTZ peut financer le "
              "reste à charge. Votre conseiller France Rénov' monte le plan complet gratuitement.")],
        cta=("Parler de votre projet", "renovation-toiture"),
    ),
    dict(
        slug="declaration-prealable-toiture",
        cle="À l'identique, on ne déclare pas. Dès que l'aspect change, on déclare.",
        img="mairie-declaration-prealable-toiture.webp", imgalt="Mairie de village avec sa toiture d'ardoise, où se dépose la déclaration préalable",
        nav="Faut-il une autorisation",
        title="Refaire son toit : quelle autorisation ?",
        desc="Quand une déclaration préalable est obligatoire pour des travaux de toiture, ce que "
             "change un secteur protégé, et les délais à prévoir avant le chantier.",
        h1=("Refaire son toit :", "faut-il une <em>autorisation</em> ?"),
        court="Une <b>déclaration préalable de travaux</b> est obligatoire dès que l'aspect "
              "extérieur du bâtiment change : nouveau matériau, nouvelle teinte, ajout d'une "
              "fenêtre de toit ou d'une lucarne. Une réfection strictement à l'identique en est "
              "en principe dispensée, sauf en secteur protégé où la règle est plus stricte. Le "
              "délai d'instruction est d'un mois, porté à deux mois près d'un monument historique.",
        estim=False,
        sections=[
            ("Lotissement, copropriété, voisinage",
             ["<b>En lotissement</b>, un règlement peut imposer une teinte ou un matériau au-delà "
              "de ce que demande la commune. Il s'applique en plus du PLU, pas à la place. "
              "Relisez-le avant de choisir votre tuile.",
              "<b>En copropriété</b>, la toiture est une partie commune. Vous ne pouvez pas la "
              "faire refaire de votre seule initiative, même si la fuite est chez vous. Le "
              "syndic doit être saisi, et la dépense votée en assemblée.",
              "<b>Côté voisinage</b>, poser une fenêtre de toit crée une vue. Des distances "
              "légales s'appliquent par rapport à la limite séparative, et un châssis mal placé "
              "peut devoir être déposé. Cela se vérifie avant, pas après."]),
            ("Les cas où la déclaration est obligatoire",
             ["<b>Vous changez de matériau.</b> Passer de la tuile plate à la tuile mécanique, de "
              "l'ardoise au bac acier : l'aspect change, la déclaration est due.",
              "<b>Vous changez de teinte.</b> Même en restant sur le même matériau. Un rouge "
              "flammé n'est pas un brun vieilli.",
              "<b>Vous ajoutez une ouverture.</b> Fenêtre de toit, lucarne, chien-assis. Là, "
              "l'obligation est systématique, et les vues sur le voisin peuvent être encadrées.",
              "<b>Vous isolez par l'extérieur.</b> L'épaisseur ajoutée surélève la couverture et "
              "modifie les débords : cela se voit depuis la rue, donc cela se déclare."]),
            ("Le cas particulier des secteurs protégés",
             ["Aux abords d'un monument historique, dans un site patrimonial remarquable ou dans "
              "un site classé, l'<b>architecte des bâtiments de France</b> donne son avis. Le "
              "délai d'instruction passe à deux mois et l'avis peut imposer un matériau, un "
              "format, une teinte.",
              "Cela concerne directement plusieurs communes de notre secteur : les abords du "
              "château d'Anet, le centre ancien de Verneuil d'Avre et d'Iton, une partie du centre "
              "de Dreux.",
              "Ce n'est pas un obstacle, c'est un délai à intégrer. Le vrai risque est de lancer "
              "le chantier sans déclaration : la mairie peut faire arrêter les travaux et exiger "
              "une remise en état."]),
            ("Comment ça se passe concrètement",
             ["<b>1.</b> Retirez ou téléchargez le formulaire de déclaration préalable, le "
              "cerfa 13703. Il se dépose en mairie ou en ligne sur le guichet numérique de votre "
              "commune.",
              "<b>2.</b> Joignez le plan de situation, un plan de masse, des photos du bâtiment et "
              "de son environnement, et le descriptif des travaux. Notre devis sert de base au "
              "descriptif.",
              "<b>3.</b> Comptez un mois d'instruction, deux en secteur protégé. Sans réponse au "
              "terme du délai, l'absence d'opposition vaut accord, mais demandez un certificat.",
              "<b>4.</b> Affichez l'autorisation sur le terrain, visible depuis la rue, pendant "
              "toute la durée du chantier. C'est ce panneau qui fait courir le délai de recours "
              "des tiers."]),
            ("Ce que nous faisons de notre côté",
             ["Nous vous disons dès la visite si votre commune impose quelque chose, et nous "
              "vérifions le règlement d'urbanisme avant de vous proposer un matériau. Rien de plus "
              "désagréable qu'un devis signé sur une solution qui sera refusée.",
              "Nous fournissons le descriptif technique dont vous avez besoin pour le dossier. "
              "Le dépôt reste à votre nom, parce que c'est vous le propriétaire, mais vous n'avez "
              "pas à inventer le contenu."]),
        ],
        faq=[("Une réfection à l'identique est-elle dispensée ?",
              "En principe oui, hors secteur protégé. Mais « à l'identique » signifie même "
              "matériau, même format, même teinte. Au moindre doute, un appel à la mairie coûte "
              "cinq minutes."),
             ("Combien de temps est valable l'autorisation ?",
              "Trois ans, prorogeable. Les travaux doivent commencer dans ce délai et ne pas être "
              "interrompus plus d'un an."),
             ("Que risque-t-on sans déclaration ?",
              "Un arrêt de chantier, une amende, et dans les cas extrêmes une remise en état à vos "
              "frais. Cela ressort aussi à la revente, lors de l'examen du dossier."),
             ("La déclaration est-elle payante ?",
              "Non, le dépôt est gratuit. Seuls des travaux créant de la surface peuvent générer "
              "une taxe d'aménagement, ce qui n'est pas le cas d'une réfection de couverture.")],
        cta=("Demander conseil sur votre projet", "renovation-toiture"),
    ),
    dict(
        slug="choisir-materiau-couverture",
        cle="C'est la pente qui choisit le matériau, pas le catalogue.",
        img="tuiles-anciennes-patinees.webp", imgalt="Tuiles anciennes patinées par le temps",
        nav="Quelle tuile choisir",
        title="Quelle tuile ou ardoise choisir",
        desc="Tuile mécanique, tuile plate, ardoise, bac acier, zinc : durée de vie, pente "
             "minimale, poids et contraintes. Comment choisir la couverture de sa maison.",
        h1=("Quelle <em>couverture</em>", "choisir pour son toit"),
        court="Le choix se fait sur trois critères, dans cet ordre : ce que le <b>PLU de votre "
              "commune autorise</b>, la <b>pente de votre toit</b>, et enfin le budget. Une tuile "
              "plate demande au moins 35 degrés de pente, une tuile mécanique 25 à 30, un bac "
              "acier peut descendre à 5. Le goût vient en dernier, parce que les deux premiers "
              "critères éliminent souvent la moitié des options.",
        estim=False,
        sections=[
            ("La pente commande, pas l'envie",
             ["Chaque matériau a une pente minimale en dessous de laquelle l'eau remonte par "
              "capillarité entre les éléments. Ce n'est pas une préférence de poseur, c'est une "
              "règle de mise en œuvre.",
              "<b>Bac acier :</b> à partir de 5 degrés environ. C'est le seul matériau vraiment "
              "utilisable sur les toits très plats.",
              "<b>Ardoise :</b> à partir de 22 degrés en pose au crochet, plus selon l'exposition "
              "au vent et la longueur de rampant.",
              "<b>Tuile mécanique à emboîtement :</b> 25 à 30 degrés selon le modèle et la région.",
              "<b>Tuile plate :</b> 35 degrés au minimum, souvent 40 dans une zone ventée comme "
              "le plateau du Thymerais.",
              "Si votre toit fait 28 degrés, la tuile plate est hors jeu, quoi qu'en dise le "
              "voisin. Changer la pente suppose de refaire la charpente, ce qui n'a de sens que "
              "dans une rénovation lourde."]),
            ("Ce que le PLU peut vous imposer",
             ["Le plan local d'urbanisme peut fixer le matériau, la teinte, parfois le nombre "
              "d'ondes au mètre carré. En secteur protégé, l'architecte des bâtiments de France "
              "ajoute son avis, et cet avis s'impose.",
              "Concrètement, dans notre secteur : les abords du château d'Anet, le centre médiéval "
              "de Verneuil d'Avre et d'Iton, une partie du centre ancien de Dreux. Ailleurs, le "
              "règlement de lotissement peut aussi restreindre le choix.",
              "Le réflexe qui évite un refus de déclaration : appeler le service urbanisme avant "
              "de choisir, pas après avoir signé. Nous le faisons systématiquement avant de "
              "chiffrer une <a href=\"{PRE}renovation-toiture/\">rénovation de toiture</a>."]),
            ("Les matériaux, un par un",
             ["<b>Tuile mécanique en terre cuite.</b> Le standard sur les pavillons du secteur. "
              "Environ 13 pièces au mètre carré, pose rapide, quarante à cinquante ans de durée "
              "de vie. Bon rapport prix, aspect, entretien.",
              "<b>Tuile plate de pays.</b> Le matériau du bâti ancien de la vallée de l'Avre. "
              "Petit format, environ 60 pièces au mètre carré, donc beaucoup plus de main-d'œuvre. "
              "Très belle, très durable, nettement plus chère à poser.",
              "<b>Ardoise naturelle.</b> Cent ans et plus si la pose est bonne. Fréquente sur les "
              "maisons de ville à forte pente de Dreux et d'Évreux. Coût élevé à l'achat, mais le "
              "coût annualisé est souvent le plus bas de tous.",
              "<b>Ardoise en fibres-ciment.</b> L'aspect de l'ardoise pour un tiers du prix, avec "
              "une durée de vie de trente à quarante ans. Un compromis honnête quand le budget ne "
              "suit pas.",
              "<b>Bac acier.</b> Léger, rapide, économique. Parfait sur une dépendance, un garage, "
              "un hangar agricole. Sur une maison d'habitation, il faut prévoir une isolation "
              "acoustique sérieuse, sinon la pluie s'entend.",
              "<b>Zinc.</b> Pour les toits à faible pente, les lucarnes, les parties courbes et "
              "toute la <a href=\"{PRE}zinguerie-gouttieres/\">zinguerie</a>. Durée de vie "
              "excellente, mise en œuvre technique."]),
            ("Le poids, le critère qu'on oublie",
             ["Une charpente ancienne a été dimensionnée pour le matériau posé à l'époque. Passer "
              "d'une tuile plate lourde à une tuile mécanique plus légère ne pose aucun problème. "
              "L'inverse, si.",
              "Ordre de grandeur : une tuile plate pèse deux fois plus au mètre carré qu'une tuile "
              "mécanique, et six à huit fois plus qu'un bac acier. Sur une grande longère, la "
              "différence se compte en tonnes.",
              "C'est pour cela que le contrôle de charpente se fait une fois la couverture déposée, "
              "et que le matériau se décide en connaissance de cause, pas sur catalogue."]),
        ],
        faq=[("Peut-on mélanger deux matériaux sur la même maison ?",
              "Oui, c'est courant : ardoise sur le corps principal, zinc sur une lucarne ou une "
              "faible pente. Le PLU encadre parfois la combinaison."),
             ("La tuile en béton, ça vaut la terre cuite ?",
              "Elle coûte moins cher et se pose pareil, mais elle se salit plus vite et vieillit "
              "moins bien esthétiquement. Sur une maison qu'on garde longtemps, la terre cuite "
              "reste le meilleur calcul."),
             ("Combien de temps dure vraiment une ardoise ?",
              "Une ardoise naturelle d'Espagne ou d'Angers bien posée dépasse le siècle. Ce sont "
              "les crochets et la zinguerie qui lâchent avant elle."),
             ("Puis-je poser du bac acier sur ma maison pour économiser ?",
              "Techniquement souvent oui, mais vérifiez d'abord le PLU, et prévoyez l'isolation "
              "acoustique. Beaucoup de gens le regrettent au premier orage."),
             ("Et si ma charpente ne supporte pas le matériau voulu ?",
              "On renforce, ce qui se chiffre, ou on choisit plus léger. Nous vous donnons les "
              "deux options chiffrées plutôt qu'un seul devis à prendre ou à laisser.")],
        cta=("Faire chiffrer votre couverture", "renovation-toiture"),
    ),
    dict(
        slug="isolation-toiture-par-exterieur",
        cle="Le bon moment pour isoler, c'est quand la couverture est déjà déposée.",
        img="combles-avant-isolation-sous-rampants.webp", imgalt="Combles dégagés avant pose de l'isolation sous rampants",
        nav="Isoler sa toiture",
        title="Isoler sa toiture : dedans ou dehors",
        desc="Combles perdus, sous rampants ou sarking par l'extérieur : quelle isolation de toiture choisir, quand la faire et les pièges de ventilation.",
        h1=("Isoler sa toiture :", "<em>dedans</em> ou dehors"),
        court="Si votre toiture doit être refaite, isolez <b>par l'extérieur</b>, au moment de la "
              "dépose : c'est le seul moment où c'est possible sans perdre de hauteur sous "
              "plafond, et sans vider les combles. Si la couverture est saine et que vos combles "
              "ne sont pas aménagés, soufflez de l'isolant sur le plancher : c'est dix fois moins "
              "cher et presque aussi efficace.",
        estim=False,
        sections=[
            ("Trois situations, trois réponses",
             ["<b>Combles perdus, couverture saine.</b> On souffle de la laine sur le plancher des "
              "combles. Intervention d'une journée, coût faible, gain thermique important. C'est "
              "de loin le meilleur rapport efficacité sur prix du bâtiment.",
              "<b>Combles aménagés, couverture saine.</b> Isolation sous rampants, par l'intérieur. "
              "On perd quelques centimètres sous plafond et il faut refaire les finitions, mais "
              "on ne touche pas au toit.",
              "<b>Couverture à refaire.</b> Isolation par l'extérieur, dite sarking : l'isolant se "
              "pose sur les chevrons, sous la couverture neuve. Zéro perte de hauteur, aucun pont "
              "thermique au droit des chevrons, et les combles restent habitables pendant les "
              "travaux. C'est la meilleure solution technique, et elle n'est accessible qu'au "
              "moment d'une <a href=\"{PRE}renovation-toiture/\">réfection</a>."]),
            ("Pourquoi le moment compte plus que la méthode",
             ["Poser un isolant par l'extérieur suppose de déposer la couverture. Si vous le faites "
              "seul, vous payez deux fois la dépose, la repose et l'échafaudage.",
              "En le faisant au moment où la toiture est de toute façon à refaire, le surcoût se "
              "limite à l'isolant, au pare-vapeur et aux chevrons de surélévation. La différence "
              "est considérable.",
              "C'est aussi ce qui rend le chantier éligible aux dispositifs d'aide, puisque "
              "l'isolation est un geste de rénovation énergétique alors que la couverture seule "
              "n'en est pas un. Le détail est dans notre "
              "<a href=\"{PRE}guides/aides-renovation-toiture/\">guide sur les aides et la TVA</a>."]),
            ("La ventilation, l'erreur la plus fréquente",
             ["Un toit isolé sans lame d'air ventilée pourrit. La vapeur d'eau qui monte de la "
              "maison se condense au contact de la sous-toiture froide, mouille l'isolant, et "
              "attaque les bois de charpente. Le désordre met deux à cinq ans à se voir, et il "
              "coûte plus cher que l'isolation elle-même.",
              "Les trois points à exiger sur un devis : un <b>écran de sous-toiture HPV</b>, une "
              "<b>lame d'air continue</b> maintenue par du contre-lattage, et des <b>entrées d'air "
              "en bas de pente</b> avec une sortie en faîtage.",
              "Beaucoup d'isolations posées lors des campagnes à un euro ont sauté ces trois "
              "points. Si vous avez fait isoler vos combles il y a quelques années et que vous "
              "voyez des taches sombres sur les chevrons, faites regarder."]),
            ("Ce qui change vraiment sur la facture",
             ["Un toit non isolé représente une part importante des déperditions d'une maison, "
              "parce que la chaleur monte. C'est le poste où l'on gagne le plus vite.",
              "Mais l'isolation ne rattrape pas une couverture qui prend l'eau, et un isolant "
              "humide ne isole plus rien. L'ordre est toujours le même : d'abord l'étanchéité du "
              "toit, ensuite l'isolation, ensuite la ventilation. Inverser cet ordre est le moyen "
              "le plus sûr de perdre son argent."]),
        ],
        faq=[("Quelle épaisseur d'isolant faut-il ?",
              "Cela dépend de l'isolant et de la performance visée. Retenez surtout que la "
              "résistance thermique compte plus que l'épaisseur brute, et qu'elle est notée sur "
              "le devis."),
             ("Laine de verre, laine de bois ou polyuréthane ?",
              "La laine de verre reste le meilleur rapport prix sur performance. La laine de bois "
              "est plus agréable en confort d'été. Le polyuréthane isole plus à épaisseur égale, "
              "ce qui est utile en sarking pour ne pas trop surélever le toit."),
             ("Peut-on isoler soi-même les combles perdus ?",
              "Le soufflage demande une machine et de la méthode pour ne pas boucher les entrées "
              "d'air. Et une pose par un professionnel qualifié conditionne les aides."),
             ("Faut-il isoler si on ne chauffe pas les combles ?",
              "Oui, on isole le plancher des combles perdus. C'est justement le cas le plus simple "
              "et le moins cher."),
             ("L'isolation par l'extérieur fait-elle monter le toit ?",
              "De quelques centimètres, oui. Il faut adapter les rives, les solins et parfois la "
              "sortie de cheminée. C'est prévu au devis.")],
        cta=("Parler isolation et toiture", "renovation-toiture"),
    ),
    dict(
        slug="toiture-tempete-assurance",
        cle="Ne pas protéger aggrave le dommage, et peut réduire l'indemnisation.",
        img="ciel-orage-sur-toitures.webp", imgalt="Ciel d'orage au-dessus de toitures de maisons",
        nav="Tempête : assurance et démarches",
        title="Toiture et tempête : les démarches",
        desc="Tuiles arrachées, faîtage descellé, arbre tombé : que couvre l'assurance, dans "
             "quel délai déclarer, quelles preuves fournir et comment se passe l'expertise.",
        h1=("Toiture et <em>tempête</em> :", "les démarches, dans l'ordre"),
        court="Déclarez à votre assurance dans les <b>cinq jours ouvrés</b>, et faites poser une "
              "<b>mise hors d'eau</b> tout de suite : ne pas protéger aggrave le dommage et peut "
              "réduire l'indemnisation. Photographiez avant de toucher à quoi que ce soit, gardez "
              "les tuiles cassées, et conservez la facture du bâchage, qui fait partie des mesures "
              "conservatoires prises en charge.",
        estim=False,
        sections=[
            ("Les six premières heures",
             ["<b>1. Sécurisez.</b> Personne sous la zone, périmètre au sol si des tuiles peuvent "
              "encore tomber. Coupez l'électricité de la pièce si de l'eau entre.",
              "<b>2. Photographiez tout.</b> Le toit depuis le sol, les tuiles au sol, les dégâts "
              "intérieurs, l'eau. Datées. C'est votre dossier.",
              "<b>3. Appelez un couvreur pour une mise hors d'eau.</b> Pas pour réparer, pour "
              "protéger. Notre <a href=\"{PRE}depannage-toiture/\">astreinte est ouverte "
              "24 h/24</a>.",
              "<b>4. Déclarez.</b> Cinq jours ouvrés en général, deux jours pour un vol, dix jours "
              "après publication d'un arrêté de catastrophe naturelle.",
              "<b>5. Ne jetez rien.</b> Les tuiles cassées et les éléments arrachés sont des "
              "preuves. L'expert peut vouloir les voir."]),
            ("Ce que l'assurance couvre, et ce qu'elle ne couvre pas",
             ["<b>Couvert dans la plupart des contrats multirisque habitation :</b> les dommages "
              "causés par un vent dépassant un certain seuil, la chute d'arbre, la grêle, le poids "
              "de la neige. Les dégâts intérieurs consécutifs relèvent de la garantie dégâts des "
              "eaux.",
              "<b>Non couvert :</b> l'usure. Une toiture en fin de vie dont quelques tuiles "
              "s'envolent au premier coup de vent sera souvent requalifiée en défaut d'entretien. "
              "C'est la raison la plus fréquente de refus.",
              "<b>Le point qui fâche :</b> beaucoup de contrats exigent un entretien régulier de "
              "la toiture. Une facture de "
              "<a href=\"{PRE}demoussage-toiture/\">démoussage</a> de moins de trois ans est "
              "un argument concret face à un expert qui invoque le défaut d'entretien."]),
            ("L'expertise, comment ça se passe",
             ["L'assureur mandate un expert au-delà d'un certain montant. Il vient constater, "
              "chiffre les dommages et détermine la cause.",
              "Vous avez le droit d'être assisté. Un devis détaillé établi par un couvreur avant "
              "sa visite pèse lourd : il donne une base chiffrée que l'expert doit discuter, au "
              "lieu de partir de son propre barème.",
              "Si le montant proposé ne couvre pas la remise en état à l'identique, vous pouvez "
              "demander une contre-expertise. Elle est parfois prise en charge par la garantie "
              "protection juridique de votre contrat, que peu de gens pensent à mobiliser."]),
            ("Le piège des démarcheurs après tempête",
             ["Après chaque épisode venteux, des équipes tournent dans les villages et sonnent aux "
              "portes en annonçant qu'elles ont vu des tuiles déplacées depuis la route.",
              "Le schéma est toujours le même : un acompte important demandé tout de suite, des "
              "travaux commencés sans devis détaillé, une entreprise injoignable ensuite. Il n'y a "
              "aucune garantie décennale derrière.",
              "La règle simple : ne signez jamais dans la minute, ne versez jamais un acompte sans "
              "devis écrit, et demandez l'attestation d'assurance décennale en cours de validité. "
              "Une entreprise locale sérieuse comprendra très bien la demande."]),
        ],
        faq=[("Dans quel délai déclarer un dégât de tempête ?",
              "Cinq jours ouvrés en général à compter de la constatation. Dix jours après la "
              "publication d'un arrêté de catastrophe naturelle."),
             ("Dois-je attendre l'expert pour bâcher ?",
              "Non, surtout pas. Protéger fait partie de vos obligations. Photographiez avant, "
              "gardez la facture du bâchage."),
             ("Mon voisin a reçu mes tuiles, qui paie ?",
              "En cas d'événement climatique, chacun déclare à son assureur. La responsabilité "
              "n'est engagée que si un défaut d'entretien est démontré."),
             ("L'assurance peut-elle refuser pour vétusté ?",
              "Oui, et c'est fréquent. Un entretien documenté, factures à l'appui, est votre "
              "meilleure défense."),
             ("Faut-il accepter le premier chiffrage de l'expert ?",
              "Pas nécessairement. Un devis de couvreur détaillé et, si besoin, une "
              "contre-expertise permettent de discuter.")],
        cta=("Faire mettre hors d'eau", "depannage-toiture"),
    ),
    dict(
        slug="entretien-toiture-annuel",
        cle="Un contrôle par an, c'est ce qui coûte le moins cher sur la vie du toit.",
        img="cheminees-toiture-controle.webp", imgalt="Cheminées en brique sur une toiture en tuile, sous un ciel nuageux",
        nav="Entretenir sa toiture",
        title="Entretien de toiture : le calendrier annuel",
        desc="Que vérifier sur son toit et à quelle saison : gouttières, solins, tuiles, mousse. "
             "Le calendrier d'entretien qui évite les réfections prématurées.",
        h1=("Entretenir sa toiture :", "le <em>calendrier</em> annuel"),
        court="Deux rendez-vous par an suffisent : une <b>purge des gouttières en fin d'automne</b>, "
              "quand les feuilles sont tombées, et un <b>contrôle visuel au printemps</b>, après "
              "les coups de vent de l'hiver. Ajoutez un <b>démoussage tous les trois à cinq ans</b>. "
              "C'est le programme le moins cher qui existe pour repousser une réfection complète.",
        estim=False,
        sections=[
            ("Automne : les gouttières, sans exception",
             ["C'est l'intervention qui évite le plus de dégâts pour le moins d'argent. Une "
              "gouttière pleine de feuilles déborde vers l'arrière, sous la première rangée de "
              "tuiles, et mouille le mur, la sablière et le bas de charpente.",
              "Le bon moment est fin novembre ou début décembre, une fois les arbres nus. Un seul "
              "passage suffit si vous n'avez pas d'arbres au-dessus du toit, deux sinon.",
              "Profitez-en pour faire vérifier les descentes et les crapaudines. Une descente "
              "bouchée en hiver gèle, se fend, et se remplace au printemps."]),
            ("Printemps : le tour d'horizon",
             ["Après l'hiver, faites le tour de la maison, de préférence aux jumelles depuis le "
              "jardin. Vous cherchez cinq choses.",
              "<b>Des tuiles déplacées ou cassées</b>, surtout en rive et en bas de pente.",
              "<b>Le faîtage</b> : des joints qui s'effritent, une tuile faîtière qui bouge.",
              "<b>Les solins de cheminée</b> : du mastic sec, une fissure entre la maçonnerie et "
              "la couverture. Première cause de fuite, de loin.",
              "<b>La mousse</b> : sur le versant nord et sous les arbres. Si elle est visible "
              "depuis le sol, il est temps d'agir.",
              "<b>Les traces intérieures</b> : montez dans les combles avec une lampe. Une auréole "
              "sur un chevron raconte une infiltration même si le plafond en dessous est sec."]),
            ("Tous les trois à cinq ans : le démoussage",
             ["Dans la vallée de l'Avre et le pays d'Ouche, comptez trois ans sur un versant nord "
              "ombragé, cinq ans sur un toit dégagé et bien exposé.",
              "Ce n'est pas de l'esthétique. La mousse retient l'eau contre la tuile, la gèle en "
              "hiver et la fait éclater en surface. Une tuile qui devient poreuse absorbe encore "
              "plus d'eau, et le phénomène s'accélère tout seul.",
              "Le détail de la méthode et le débat sur l'hydrofuge sont dans notre "
              "<a href=\"{PRE}guides/demoussage-toiture-frequence/\">guide sur le démoussage</a>."]),
            ("Ce que l'entretien vous fait vraiment gagner",
             ["Une toiture entretenue tient facilement dix à quinze ans de plus qu'une toiture "
              "laissée à elle-même. Rapporté au coût d'une réfection complète, le calcul n'est pas "
              "discutable.",
              "Il y a un second effet, moins connu : les contrats d'assurance habitation exigent "
              "souvent un entretien régulier. En cas de sinistre, des factures d'entretien "
              "récentes coupent court à l'argument du défaut d'entretien. Voir notre "
              "<a href=\"{PRE}guides/toiture-tempete-assurance/\">guide tempête et assurance</a>.",
              "Enfin, l'entretien est le moment où l'on repère un solin fatigué ou trois tuiles "
              "fendues. Réparés à ce stade, ce sont deux heures de travail. Découverts par une "
              "tache au plafond, c'est un plafond, un isolant et parfois un chevron."]),
        ],
        faq=[("Puis-je monter moi-même sur mon toit ?",
              "Le contrôle se fait très bien depuis le sol, aux jumelles. Monter sur une toiture "
              "est la première cause de chute domestique grave, et une tuile humide ne pardonne pas."),
             ("À quelle saison faire les travaux d'entretien ?",
              "Gouttières en fin d'automne, contrôle au printemps, démoussage au printemps ou en "
              "début d'automne, hors gel et hors grosse chaleur."),
             ("Existe-t-il un contrat d'entretien ?",
              "Nous fonctionnons au passage, sans abonnement. Nous notons simplement la date de "
              "votre dernier passage pour vous rappeler quand cela redevient utile."),
             ("Un toit récent a-t-il besoin d'entretien ?",
              "Les gouttières, oui, dès la première année. Le démoussage, pas avant plusieurs "
              "années, mais le contrôle annuel reste utile."),
             ("Combien de temps prend un contrôle complet ?",
              "Une heure environ pour une maison courante, gouttières comprises si elles sont "
              "accessibles.")],
        cta=("Programmer un passage", "demoussage-toiture"),
    ),
    dict(
        slug="poser-fenetre-de-toit",
        cle="Le point critique n'est pas la fenêtre. C'est son raccord à la couverture.",
        img="pose-fenetre-de-toit-velux.webp", imgalt="Fenêtre de toit posée dans une couverture en tuile",
        nav="Poser une fenêtre de toit",
        title="Poser une fenêtre de toit",
        desc="Fenêtre de toit ou lucarne, autorisation, raccordement à la couverture : ce qu'il faut vérifier avant de faire percer son toit.",
        h1=("Poser une <em>fenêtre</em>", "de toit sans le regretter"),
        court="Une fenêtre de toit demande une <b>déclaration préalable en mairie</b> dans tous "
              "les cas, et elle doit respecter des <b>distances par rapport à la limite du "
              "voisin</b> quand elle crée une vue. Techniquement, le point critique n'est pas la "
              "fenêtre mais son <b>raccordement à la couverture</b> : c'est là que naissent la "
              "quasi-totalité des infiltrations.",
        estim=False,
        sections=[
            ("Le raccordement, tout se joue là",
             ["Une fenêtre de toit est un trou volontaire dans une couverture. Ce qui la rend "
              "étanche, c'est le raccord, appelé costière ou kit de raccordement, adapté au "
              "matériau et à sa hauteur d'onde.",
              "Un raccord prévu pour de la tuile mécanique posé sur de l'ardoise fuit. Un raccord "
              "au bon modèle mais mal relevé en partie haute fuit aussi, dès la première pluie "
              "poussée par le vent.",
              "Deuxième point critique : la <b>collerette pare-vapeur</b> côté intérieur et le "
              "<b>raccord à l'écran de sous-toiture</b>. Sans eux, la condensation s'accumule dans "
              "l'isolant autour du châssis et vous croirez à une fuite alors que c'est de la "
              "vapeur d'eau."]),
            ("Fenêtre de toit ou lucarne",
             ["<b>La fenêtre de toit</b> suit la pente. Elle coûte beaucoup moins cher, se pose en "
              "une journée, et apporte plus de lumière à surface égale parce qu'elle regarde le "
              "ciel.",
              "<b>La lucarne</b> est une petite construction verticale. Elle coûte plusieurs fois "
              "plus cher, demande de la charpente et de la zinguerie, mais elle crée de la hauteur "
              "utilisable sous plafond et une vue horizontale.",
              "En secteur protégé, le choix ne vous appartient pas toujours : certaines communes "
              "imposent la lucarne côté rue et tolèrent la fenêtre de toit côté jardin."]),
            ("L'autorisation et le voisinage",
             ["Une déclaration préalable est obligatoire, sans exception, puisque l'aspect "
              "extérieur change. Le détail de la procédure est dans notre "
              "<a href=\"{PRE}guides/declaration-prealable-toiture/\">guide sur les "
              "autorisations d'urbanisme</a>.",
              "S'ajoute la question des vues. Le code civil fixe des distances minimales entre une "
              "ouverture créant une vue et la limite séparative. Une fenêtre posée trop près peut "
              "devoir être déposée, même des années plus tard.",
              "Le cas particulier des combles : si vous transformez des combles en pièce "
              "habitable, vous créez de la surface de plancher, ce qui peut faire basculer le "
              "dossier vers un permis de construire et générer une taxe d'aménagement."]),
            ("Le bon moment pour la poser",
             ["Si votre toiture doit être refaite, posez la fenêtre pendant le chantier. "
              "L'échafaudage est déjà là, la couverture est déposée, le raccord se fait "
              "proprement dans la foulée et le surcoût se limite au matériel et à quelques heures.",
              "Sur une toiture en place, c'est parfaitement faisable, cela prend une journée par "
              "châssis. On dépose localement, on adapte les liteaux, on pose la costière, on "
              "reprend la couverture autour.",
              "Ce qu'il ne faut pas faire : poser une fenêtre de toit sur une couverture en fin de "
              "vie. Vous investissez dans un châssis neuf qu'il faudra redéposer dans trois ans "
              "quand le toit sera refait."]),
        ],
        faq=[("Combien de temps prend la pose ?",
              "Une journée par châssis sur une toiture existante, moins si c'est fait pendant une "
              "réfection."),
             ("Faut-il une autorisation pour remplacer une fenêtre de toit existante ?",
              "Si les dimensions et l'aspect sont identiques, en général non. Dès que la taille "
              "ou la teinte change, oui."),
             ("Ma fenêtre de toit fuit, est-ce le châssis ?",
              "Rarement. Dans la grande majorité des cas, c'est le raccord à la couverture ou la "
              "condensation autour du cadre. Nous cherchons dans cet ordre."),
             ("Peut-on poser une fenêtre de toit sur toutes les pentes ?",
              "La plupart des modèles demandent entre 15 et 90 degrés. En dessous, il existe des "
              "solutions spécifiques, plus chères."),
             ("Volet roulant ou store intérieur ?",
              "Le volet extérieur est nettement plus efficace contre la chaleur d'été, et il "
              "s'installe au moment de la pose sans surcoût de main-d'œuvre.")],
        cta=("Demander un devis fenêtre de toit", "renovation-toiture"),
    ),
    dict(
        slug="quand-refaire-sa-toiture",
        cle="Un toit ne prévient pas. Il donne des signes pendant des années.",
        img="corps-de-ferme-pierre-depose-couverture.webp",
        imgalt="Corps de ferme en pierre dont la couverture est en cours de dépose",
        nav="Quand refaire sa toiture",
        title="Quand faut-il refaire sa toiture ?",
        desc="Les signes qui disent qu'une toiture arrive en fin de vie, la durée de vie réelle "
             "de chaque matériau, et comment savoir si une réparation suffit encore.",
        h1=("Quand faut-il <em>refaire</em>", "sa toiture ?"),
        court="Une couverture se remplace quand les réparations deviennent plus fréquentes que "
              "les années qui la séparent de sa fin de vie théorique. Concrètement : "
              "<b>des tuiles qui se cassent à la manipulation, un litelage qui ne tient plus les "
              "clous, de la lumière visible depuis les combles</b>. À l'inverse, quelques tuiles "
              "déplacées après un coup de vent ne justifient pas une réfection, et un couvreur "
              "honnête vous le dira.",
        estim=False,
        sections=[
            ("Les signes qui ne trompent pas",
             ["<b>La tuile casse quand on la soulève.</b> C'est le test le plus parlant. Une terre "
              "cuite saine se manipule. Une tuile gélive, poreuse d'avoir gelé et dégelé cinquante "
              "hivers, se fend entre les doigts. Si le couvreur en casse trois pour en déplacer "
              "dix, la couverture est finie.",
              "<b>Les liteaux ne tiennent plus.</b> Sous la couverture, les tuiles reposent sur des "
              "liteaux cloués. Quand le bois s'effrite et que les pointes ne mordent plus, on ne "
              "peut plus reposer une tuile correctement. Réparer devient impossible.",
              "<b>On voit le jour depuis les combles.</b> Montez dans les combles par temps sec et "
              "regardez vers le haut sans lampe. Des points lumineux signifient des trous, et "
              "chaque trou laissera passer la pluie battante.",
              "<b>Les mousses reviennent en deux ans.</b> Un démoussage tient normalement trois à "
              "cinq ans. Si la mousse revient bien plus vite, c'est que la tuile est devenue "
              "poreuse et retient l'eau : elle ne sèche plus.",
              "<b>La ligne de faîtage ondule.</b> Vu de la rue, un faîtage qui n'est plus droit ou "
              "un versant qui se creuse signalent un problème de charpente, pas de couverture. "
              "C'est plus grave, et ça ne se règle pas en changeant des tuiles."]),
            ("Combien de temps dure une couverture, matériau par matériau",
             ["Ces durées sont des ordres de grandeur admis dans le métier. L'exposition compte "
              "autant que le matériau : un versant nord humide vieillit deux fois plus vite qu'un "
              "versant sud ventilé.",
              "<b>Tuile de terre cuite :</b> 40 à 60 ans pour une tuile mécanique, souvent plus "
              "pour une tuile plate de pays bien posée. Beaucoup de toits anciens de la vallée de "
              "l'Avre dépassent le siècle.",
              "<b>Ardoise naturelle :</b> 75 à 100 ans, parfois davantage. Ce sont souvent les "
              "crochets ou les clous qui lâchent avant la pierre.",
              "<b>Ardoise fibrociment :</b> 30 à 50 ans. Attention : posée avant 1997, elle peut "
              "contenir de l'amiante, et sa dépose relève alors d'une procédure encadrée.",
              "<b>Bac acier :</b> 30 à 50 ans selon le traitement et l'épaisseur. La corrosion part "
              "des perçages et des découpes.",
              "<b>Zinc :</b> 50 à 80 ans en couverture, moins en gouttière où l'eau stagne."]),
            ("Réparer ou refaire : comment trancher",
             ["La question n'est pas l'âge du toit, c'est le rapport entre ce que coûte la "
              "réparation et ce qu'elle achète de tranquillité.",
              "<b>Réparer se défend</b> quand la cause est ponctuelle et identifiée : un solin de "
              "cheminée, une noue percée, une dizaine de tuiles déplacées par le vent sur une "
              "couverture saine par ailleurs.",
              "<b>Refaire s'impose</b> quand les interventions se répètent sur des points "
              "différents. Trois réparations en deux ans à des endroits sans rapport, c'est le "
              "matériau qui lâche partout en même temps, pas un accident.",
              "<b>Le calcul honnête :</b> si la réparation coûte le quart d'une réfection et ne "
              "garantit que deux ou trois ans, elle est chère. Si elle coûte un dixième et tient "
              "dix ans, elle est excellente. Demandez cette estimation de durée, par écrit."]),
            ("Ce qui pousse à décider maintenant plutôt que dans cinq ans",
             ["<b>La charpente.</b> Tant que l'eau n'est pas entrée durablement, la charpente est "
              "saine et la réfection ne touche que la couverture. Une fois que les pannes ont "
              "travaillé et que les champignons s'y sont mis, le chantier change de nature et de "
              "prix.",
              "<b>L'isolation.</b> Refaire un toit est le seul moment où l'isolation par "
              "l'extérieur est envisageable sans surcoût de dépose. Faire les deux séparément "
              "coûte nettement plus cher que les faire ensemble.",
              "<b>Les aides.</b> Les dispositifs d'aide à la rénovation changent chaque année et "
              "ne vont pas en s'élargissant. Ce qui est éligible aujourd'hui ne le sera pas "
              "forcément dans trois ans.",
              "Cela dit, personne ne devrait refaire un toit qui tient encore. Le rôle du couvreur "
              "est de vous dire combien d'années il reste, pas de vous vendre un chantier."]),
        ],
        faq=[("Un couvreur peut-il vraiment estimer les années qui restent ?",
              "Approximativement, oui, en montant. L'état des tuiles à la manipulation, celui des "
              "liteaux et la porosité du matériau donnent une fourchette honnête. Personne ne peut "
              "donner une date, et méfiez-vous de qui le prétend."),
             ("Mon toit a 50 ans mais ne fuit pas. Dois-je m'inquiéter ?",
              "Pas nécessairement. Une couverture peut dépasser largement sa durée théorique si "
              "elle est bien ventilée et entretenue. Un contrôle tous les ans suffit, et il coûte "
              "beaucoup moins cher qu'une réfection anticipée."),
             ("Peut-on refaire un seul versant ?",
              "Oui, et c'est fréquent : le versant nord se dégrade plus vite. Le rendu sera "
              "différent entre les deux pans pendant quelques années, le temps que la tuile neuve "
              "patine. Certains PLU l'interdisent en secteur protégé."),
             ("La réfection peut-elle attendre l'été ?",
              "Si le toit est hors d'eau, oui, et c'est même souvent préférable pour la logistique. "
              "Si l'eau entre, non : chaque hiver passé avec une infiltration abîme la charpente.")],
        cta=("Faire contrôler l'état du toit", "renovation-toiture"),
    ),
    dict(
        slug="demarchage-toiture-arnaque",
        cle="Un couvreur sérieux ne sonne pas à votre porte pour vous vendre un toit.",
        img="echafaudage-bache-maison-de-ville.webp",
        imgalt="Échafaudage bâché sur une maison de ville pendant des travaux de toiture",
        nav="Démarchage toiture : les pièges",
        title="Démarchage toiture : reconnaître l'arnaque",
        desc="Comment repérer une entreprise de toiture qui démarche, quels signaux doivent vous "
             "arrêter, et ce que dit la loi sur le démarchage à domicile et le droit de rétractation.",
        h1=("Démarchage toiture :", "<em>reconnaître</em> l'arnaque"),
        court="La toiture est l'un des secteurs les plus touchés par le démarchage abusif. Le "
              "schéma est presque toujours le même : quelqu'un passe « par hasard », a vu « un "
              "problème » depuis la rue, propose un diagnostic gratuit immédiat, monte, redescend "
              "avec des photos alarmantes, et fait signer le jour même avec un acompte. "
              "<b>Un professionnel installé n'a pas besoin de sonner chez vous.</b>",
        estim=False,
        sections=[
            ("Les sept signaux qui doivent vous arrêter",
             ["<b>1. Il est venu sans que vous l'appeliez.</b> C'est le premier et le plus simple. "
              "Une entreprise qui a du travail ne fait pas du porte-à-porte.",
              "<b>2. Il a vu le problème depuis la rue.</b> On ne diagnostique pas une toiture "
              "depuis un trottoir. On voit une mousse, éventuellement une tuile déplacée. Pas une "
              "charpente, pas un écran de sous-toiture, pas une fuite.",
              "<b>3. Il veut monter tout de suite.</b> Une fois sur le toit, seul, il contrôle ce "
              "que vous verrez sur les photos. Des tuiles cassées peuvent l'avoir été en montant.",
              "<b>4. L'offre expire aujourd'hui.</b> « J'ai une équipe dans le secteur cette "
              "semaine », « le prix est valable si vous signez maintenant ». Aucun prix honnête "
              "n'a besoin d'urgence pour être accepté.",
              "<b>5. Il demande un acompte immédiat.</b> Surtout en liquide, ou par un virement "
              "qu'il vous fait faire devant lui.",
              "<b>6. Le devis est vague.</b> « Réfection toiture : 14 000 € ». Sans surface, sans "
              "matériau, sans détail des postes. Un devis qui ne se vérifie pas ne s'engage à rien.",
              "<b>7. Il parle d'aides ou de « 1 € ».</b> Aucun dispositif public ne finance une "
              "toiture à un euro. C'est le marqueur le plus fiable d'une arnaque."]),
            ("Ce que dit la loi, et qui joue pour vous",
             ["<b>Quatorze jours de rétractation.</b> Pour un contrat conclu à votre domicile suite "
              "à un démarchage, vous disposez d'un délai de quatorze jours pour vous rétracter, "
              "sans motif et sans pénalité. Le professionnel doit vous remettre un formulaire de "
              "rétractation : son absence est déjà une infraction.",
              "<b>Aucun paiement avant sept jours.</b> Dans le cadre d'un démarchage à domicile, le "
              "professionnel n'a pas le droit d'encaisser quoi que ce soit avant l'expiration d'un "
              "délai de sept jours. Un acompte exigé sur-le-champ est illégal.",
              "<b>Le devis engage.</b> Signé, il vaut contrat. Mais un devis qui ne mentionne ni "
              "les surfaces, ni les matériaux, ni le détail des postes est inopposable dans les "
              "faits : vous ne pouvez pas prouver ce qui était promis, et eux non plus.",
              "Ces règles existent précisément parce que le secteur a été massivement abusé. "
              "Utilisez-les sans état d'âme."]),
            ("Les cinq vérifications qui prennent dix minutes",
             ["<b>Le SIRET.</b> Demandez-le, puis tapez-le sur l'annuaire des entreprises de "
              "l'État. Vous verrez la date de création, l'activité déclarée et l'adresse. Une "
              "entreprise de couverture créée il y a trois mois à six cents kilomètres mérite des "
              "questions.",
              "<b>L'assurance décennale.</b> Demandez l'attestation, avec l'année en cours et "
              "l'activité « couverture » explicitement mentionnée. Une attestation périmée ou pour "
              "une autre activité ne vous couvre pas.",
              "<b>L'adresse réelle.</b> Cherchez-la sur une carte. Un atelier, un dépôt, quelque "
              "chose de physique. Une boîte postale ou une adresse de domiciliation n'est pas un "
              "bon signe pour des travaux lourds.",
              "<b>Les avis, et leur ancienneté.</b> Vingt avis excellents déposés la même semaine "
              "ne valent rien. Des avis étalés sur des années, avec des réponses de l'entreprise, "
              "valent beaucoup.",
              "<b>Des chantiers dans le secteur.</b> Demandez deux adresses de chantiers récents "
              "à proximité. Un artisan local en a toujours."]),
            ("Si vous avez déjà signé",
             ["<b>Dans les quatorze jours :</b> envoyez votre rétractation en recommandé avec "
              "accusé de réception. Pas besoin de justifier. Conservez la preuve d'envoi.",
              "<b>Si des travaux ont commencé :</b> la rétractation reste valable, mais cela se "
              "complique. Faites constater l'état par un tiers, photographiez tout, et ne payez "
              "rien de plus.",
              "<b>Si vous avez payé :</b> signalez à la répression des fraudes via la plateforme "
              "SignalConso, et déposez plainte si la somme est importante. Prévenez votre banque "
              "immédiatement en cas de paiement par carte.",
              "<b>Dans tous les cas :</b> faites établir un devis par une entreprise locale que "
              "vous aurez choisie. Vous saurez alors si le prix annoncé avait un rapport avec la "
              "réalité, et ce document vous servira."]),
        ],
        faq=[("Un couvreur peut-il proposer un diagnostic gratuit ?",
              "Oui, et beaucoup le font, nous compris : la visite et le devis sont gratuits. La "
              "différence est que vous l'avez appelé. Le problème n'est pas la gratuité, c'est "
              "l'initiative du contact et l'urgence fabriquée."),
             ("Comment savoir si les photos qu'on me montre sont bien de mon toit ?",
              "Demandez des photos larges qui montrent l'environnement : une cheminée reconnaissable, "
              "la maison voisine, un arbre. Un gros plan de tuile cassée peut venir de n'importe où."),
             ("On me dit que ma charpente est attaquée. Comment vérifier ?",
              "Une charpente se contrôle depuis les combles, pas depuis le toit. Montez-y vous-même "
              "avec une lampe : le bois attaqué se creuse à la pointe d'un tournevis et laisse "
              "de la sciure. Demandez toujours un deuxième avis avant un traitement de charpente."),
             ("Faut-il se méfier de toutes les entreprises qui viennent de loin ?",
              "Pas systématiquement, mais posez la question du service après-vente. La décennale "
              "dure dix ans : si un problème apparaît dans huit ans, qui reviendra ?")],
        cta=("Demander un devis à une entreprise locale", "renovation-toiture"),
    ),
    dict(
        slug="hydrofuge-toiture-utile",
        cle="L'hydrofuge protège une tuile saine. Il ne sauve pas une tuile morte.",
        img="demoussage-toiture-mousse-echafaudage.webp",
        imgalt="Toiture envahie de mousse en cours de démoussage depuis un échafaudage",
        nav="Hydrofuge : utile ou pas",
        title="Hydrofuge de toiture : utile ou inutile ?",
        desc="Ce que fait réellement un traitement hydrofuge sur une toiture, quand il a du sens, "
             "quand il n'en a aucun, et pourquoi il est si souvent vendu au mauvais moment.",
        h1=("Hydrofuge de toiture :", "<em>utile</em> ou inutile ?"),
        court="Un hydrofuge est une résine qui empêche l'eau de pénétrer dans la tuile. Appliqué "
              "après un démoussage sur une couverture encore saine, il ralentit réellement le "
              "retour des mousses et le vieillissement. Appliqué sur une tuile déjà poreuse et "
              "gélive, <b>il ne répare rien et masque l'état réel du toit</b>. C'est pour ça qu'il "
              "figure en tête des prestations vendues par démarchage.",
        estim=False,
        sections=[
            ("Ce que fait un hydrofuge, physiquement",
             ["Une tuile de terre cuite n'est pas étanche : elle est poreuse. L'eau y pénètre de "
              "quelques millimètres, puis s'évapore. Ce cycle est normal et la tuile est conçue "
              "pour ça.",
              "Le problème vient quand la porosité augmente avec l'âge. La tuile retient plus "
              "d'eau, plus longtemps. Elle sèche moins vite, donc les mousses s'y installent. Et "
              "surtout, l'eau retenue gèle en hiver : en gelant elle gonfle, et elle fait éclater "
              "la tuile de l'intérieur. C'est le phénomène de gélivité.",
              "<b>L'hydrofuge forme un film qui empêche l'eau d'entrer</b>, tout en laissant la "
              "vapeur sortir. L'eau perle et glisse au lieu de s'infiltrer. Sur une tuile encore "
              "en bon état, c'est efficace et cela repousse le vieillissement.",
              "Il existe en incolore, qui ne change rien à l'aspect, et en coloré, qui redonne une "
              "teinte homogène. Le coloré est un produit de finition, pas de protection "
              "supplémentaire."]),
            ("Quand il a du sens, et quand il n'en a aucun",
             ["<b>Il a du sens</b> sur une couverture de quinze à trente ans, saine, qui vient "
              "d'être démoussée, sur un versant exposé au nord ou à l'ombre d'arbres. Là, il "
              "allonge réellement l'intervalle entre deux démoussages.",
              "<b>Il n'a aucun sens</b> sur une tuile déjà gélive, qui s'effrite ou se casse à la "
              "manipulation. La résine se pose sur un matériau qui part en morceaux : elle "
              "n'empêchera ni l'éclatement ni les fuites. Elle donne seulement au toit un bel "
              "aspect pendant deux ans.",
              "<b>Il n'a aucun sens non plus</b> sur une ardoise naturelle, qui n'est pas poreuse. "
              "Se le faire proposer sur de l'ardoise est un signal d'alarme sur la compétence ou "
              "l'honnêteté de l'interlocuteur.",
              "<b>Il ne remplace jamais un démoussage.</b> Appliqué sur des mousses, il les "
              "emprisonne sous le film. Le résultat est pire que rien."]),
            ("Pourquoi on vous le propose si souvent",
             ["Un hydrofuge coûte peu cher en matière et se pose vite. Il transforme visuellement "
              "un toit en une journée, surtout en version colorée. Et son efficacité réelle ne se "
              "constate qu'au bout de plusieurs années, quand l'entreprise n'est plus joignable.",
              "C'est exactement le profil d'une prestation vendue par démarchage : impressionnant "
              "tout de suite, invérifiable à long terme.",
              "Cela ne veut pas dire que le produit est mauvais. Il est bon, au bon moment, sur le "
              "bon support. Cela veut dire qu'il faut se demander <b>pourquoi</b> on vous le "
              "propose, et exiger que l'état réel de la tuile soit constaté avant.",
              "Le test est simple, et vous pouvez l'exiger : demandez qu'on descende deux tuiles "
              "du toit et qu'on les manipule devant vous. Si elles se cassent, l'hydrofuge n'est "
              "pas la réponse à votre problème."]),
            ("Combien de temps ça tient",
             ["Les fabricants annoncent généralement huit à dix ans pour un hydrofuge de qualité "
              "correctement appliqué. Dans les faits, l'exposition décide : un versant plein sud "
              "perd son film plus vite qu'un versant abrité.",
              "Le traitement ne se renouvelle pas indéfiniment. À chaque application, il faut "
              "nettoyer d'abord, et chaque nettoyage use un peu la tuile.",
              "Un cycle raisonnable sur une couverture saine : démoussage tous les trois à cinq "
              "ans, hydrofuge une fois sur deux ou trois. Pas à chaque passage.",
              "Si l'on vous propose un hydrofuge chaque année, ou un hydrofuge sans démoussage "
              "préalable, la prestation n'est pas dimensionnée pour votre toit."]),
        ],
        faq=[("L'hydrofuge coloré, c'est de la peinture ?",
              "Non. Une peinture forme un film opaque qui empêche la tuile de respirer et finit par "
              "s'écailler. Un hydrofuge coloré est une résine microporeuse teintée : la vapeur "
              "sort, l'eau n'entre pas. La différence de longévité est considérable."),
             ("Peut-on l'appliquer soi-même ?",
              "Techniquement oui, mais le produit s'applique sur un toit, ce qui reste l'endroit "
              "d'où l'on tombe. Et une application irrégulière laisse des zones non protégées "
              "invisibles depuis le sol."),
             ("Ça change quelque chose pour l'eau de pluie récupérée ?",
              "Oui, et c'est à signaler. La plupart des fabricants déconseillent la récupération "
              "d'eau de pluie pour un usage alimentaire ou potager dans les mois qui suivent "
              "l'application. Demandez la fiche technique du produit posé."),
             ("Mon toit a 45 ans, l'hydrofuge peut-il le sauver ?",
              "Non. À cet âge, la question est de savoir combien d'années il reste à la couverture. "
              "Un hydrofuge sur une tuile en fin de vie est une dépense qui repousse la décision "
              "sans changer l'échéance.")],
        cta=("Faire évaluer l'état de la tuile", "demoussage-toiture"),
    ),
    dict(
        slug="prix-demoussage-toiture",
        cle="On paie la surface, l'accès et l'état. Rarement le produit.",
        img="avant-refection-toiture-longere-mousse.webp",
        imgalt="Toiture de longère envahie par la mousse avant démoussage",
        nav="Prix d'un démoussage",
        title="Prix d'un démoussage de toiture au m2",
        desc="Ce que coûte un démoussage de toiture selon les comparateurs, ce qui fait varier la "
             "facture, et comment lire un devis de démoussage sans se faire surprendre.",
        h1=("Prix d'un <em>démoussage</em>", "de toiture"),
        court="Les comparateurs nationaux situent un démoussage de toiture entre <b>10 et 25 € le "
              "mètre carré de rampant</b> en 2026, traitement anti-mousse compris, et jusqu'à 40 € "
              "avec un hydrofuge. Comme pour une réfection, ce prix s'applique à la surface réelle "
              "des pans du toit, pas à la surface au sol de la maison.",
        estim=True,
        sections=[
            ("Ce qui fait vraiment varier le prix",
             ["<b>L'accès, avant tout.</b> Une maison de plain-pied entourée de pelouse se traite "
              "à l'échelle. Une maison de ville mitoyenne, sans recul et avec du stationnement "
              "devant, demande un échafaudage ou une nacelle. C'est souvent le premier poste de "
              "la facture, et il n'a rien à voir avec la toiture.",
              "<b>La pente.</b> Au-delà d'une certaine inclinaison, on ne circule plus sur le toit "
              "sans dispositif de sécurité. Cela change le temps passé et le matériel.",
              "<b>L'épaisseur du tapis végétal.</b> Une fine pellicule verte se traite par "
              "pulvérisation. Un tapis de mousse de plusieurs centimètres demande un passage "
              "mécanique préalable, donc du temps et de l'évacuation.",
              "<b>Le matériau.</b> Une tuile mécanique plate se nettoie vite. Une tuile canal, une "
              "ardoise ou une petite tuile plate de pays demandent beaucoup plus de précaution : "
              "on ne passe pas la même pression.",
              "<b>Ce qu'on fait en plus.</b> Nettoyage des gouttières, évacuation des déchets, "
              "reprise de quelques tuiles au passage. Ces postes doivent être écrits, pas sous-entendus."]),
            ("Ce que doit contenir un devis de démoussage",
             ["<b>La surface traitée, en rampant.</b> Avec le calcul, ou au moins les dimensions. "
              "Un devis qui annonce un forfait sans surface ne se compare à rien.",
              "<b>La méthode de nettoyage.</b> Basse pression, moyenne pression, brossage. La "
              "haute pression sur de la tuile ancienne enlève la mousse <b>et</b> l'engobe qui "
              "protège la tuile : le toit est propre et plus fragile qu'avant.",
              "<b>Le produit de traitement, nommé.</b> Un anti-mousse curatif agit dans le temps, "
              "sur plusieurs semaines. « Traitement anti-mousse » sans plus de précision ne dit "
              "pas s'il s'agit d'un produit rémanent ou d'un rinçage.",
              "<b>Le sort des déchets.</b> Une toiture démoussée produit des sacs de mousse. Qui "
              "les évacue, et est-ce compris ?",
              "<b>Les gouttières.</b> Elles se remplissent pendant l'opération. Si leur nettoyage "
              "n'est pas au devis, elles resteront bouchées."]),
            ("Les pièges de prix les plus fréquents",
             ["<b>Le prix au mètre carré au sol.</b> Un toit à deux pans fait environ 1,3 à 1,5 fois "
              "la surface au sol qu'il couvre. Annoncer un prix au sol permet d'afficher un tarif "
              "attractif qui gonflera à la facture.",
              "<b>Le forfait « maison ».</b> « Démoussage maison : 900 € ». Sans surface ni "
              "méthode, ce chiffre ne veut rien dire et ne se compare à aucun autre devis.",
              "<b>L'hydrofuge présenté comme inclus.</b> Vérifiez s'il s'agit d'un vrai hydrofuge "
              "ou d'un simple rinçage. Et demandez-vous s'il est utile sur votre toiture : voir "
              "notre page sur le sujet.",
              "<b>Le supplément de dernière minute.</b> « On a trouvé douze tuiles cassées. » Cela "
              "arrive vraiment, c'est même fréquent. Mais le devis doit prévoir un prix unitaire "
              "de remplacement à l'avance, pas une négociation depuis l'échafaudage."]),
            ("Est-ce que ça vaut le coup ?",
             ["Un démoussage n'embellit pas seulement. La mousse retient l'eau contre la tuile, "
              "l'empêche de sécher, et accélère la gélivité. Elle bouche aussi les gouttières et "
              "finit par faire déborder l'eau contre la façade.",
              "Sur une couverture saine, c'est l'entretien le moins cher rapporté à ce qu'il "
              "préserve : quelques centaines d'euros tous les trois à cinq ans contre plusieurs "
              "milliers pour une réfection anticipée.",
              "Sur une couverture en fin de vie, en revanche, c'est de l'argent dépensé sur un toit "
              "qu'il faudra refaire. Un couvreur honnête vous dira lequel des deux cas est le vôtre "
              "avant de chiffrer.",
              "Les prix cités ici viennent de comparateurs nationaux. Ils donnent un ordre de "
              "grandeur pour lire un devis, pas un prix pour votre toit : seule une visite permet "
              "de le chiffrer."]),
        ],
        faq=[("Tous les combien faut-il démousser ?",
              "Un contrôle chaque année, un démoussage tous les trois à cinq ans selon "
              "l'exposition. Les versants nord et les toits sous les arbres reverdissent plus vite."),
             ("Le karcher abîme-t-il vraiment la tuile ?",
              "Sur une tuile ancienne, oui. La haute pression enlève l'engobe, la couche de "
              "surface qui limite la porosité. Le toit paraît plus propre et vieillit plus vite. "
              "On adapte la pression au matériau et à son état."),
             ("Peut-on démousser en hiver ?",
              "Oui hors période de gel, mais le traitement agit moins vite quand il fait froid. "
              "Le printemps et l'automne sont les meilleures périodes."),
             ("Faut-il être présent pendant l'intervention ?",
              "Non, mais c'est mieux au début et à la fin : pour voir l'état constaté avant, et "
              "les photos après. Nous remettons systématiquement des photos avant et après.")],
        cta=("Demander un devis de démoussage", "demoussage-toiture"),
    ),
    dict(
        slug="gouttieres-quel-materiau",
        cle="La gouttière tombe en panne avant le toit, et elle abîme la façade d'abord.",
        img="zinguerie-souche-zinc-toiture.webp",
        imgalt="Souche de cheminée habillée en zinc sur une toiture",
        nav="Gouttières : quel matériau",
        title="Gouttières : zinc, aluminium ou PVC ?",
        desc="Les différences réelles entre gouttières en zinc, en aluminium et en PVC : durée de "
             "vie, coût, entretien, et ce qui convient à une maison ancienne.",
        h1=("Gouttières : <em>zinc</em>,", "aluminium ou PVC ?"),
        court="Le zinc dure le plus longtemps et vieillit bien, l'aluminium ne rouille pas et se "
              "pose en continu sans soudure, le PVC coûte le moins cher et se dilate le plus. "
              "Sur une maison ancienne, <b>le zinc reste la référence</b>, et c'est souvent ce que "
              "le PLU impose en secteur protégé.",
        estim=False,
        sections=[
            ("Les trois matériaux, sans complaisance",
             ["<b>Le zinc.</b> Cinquante à quatre-vingts ans. Il se soude, donc il se répare "
              "localement sans tout changer. Il se patine en gris mat, ce qui va bien à la pierre "
              "et à la brique. En contrepartie il coûte plus cher, demande un vrai savoir-faire de "
              "zingueur, et il n'aime pas le contact avec le cuivre, qui le corrode.",
              "<b>L'aluminium.</b> Trente à cinquante ans. Son gros avantage est la pose en "
              "continu : la gouttière est profilée sur place, à la longueur exacte, sans joint ni "
              "soudure sur toute la façade. Donc rien qui fuit aux raccords. Il se laque dans "
              "toutes les teintes. Il se déforme en revanche sous un choc, et une réparation "
              "locale est plus difficile.",
              "<b>Le PVC.</b> Quinze à trente ans. Peu cher, léger, facile à poser. Mais il se "
              "dilate fortement avec la chaleur, ce qui fatigue les joints, et il devient cassant "
              "avec les UV : au bout de vingt ans, il se fend au moindre coup. Il convient à une "
              "dépendance, un garage, un abri. Sur une maison, c'est un choix de court terme."]),
            ("Ce qui compte autant que le matériau",
             ["<b>La pente.</b> Une gouttière n'est pas horizontale : elle descend vers la "
              "descente, de quelques millimètres par mètre. Trop peu, l'eau stagne et les feuilles "
              "s'accumulent. Trop, elle déborde au débit fort. C'est un réglage, et c'est là que "
              "se voit le travail.",
              "<b>Le dimensionnement.</b> Une gouttière trop petite pour la surface de toit "
              "qu'elle reçoit débordera à chaque gros orage, quel que soit son matériau. Le calcul "
              "se fait sur la surface en projection et la pluviométrie locale.",
              "<b>Les crochets.</b> Leur espacement et leur fixation décident de la tenue dans le "
              "temps. Des crochets trop espacés laissent la gouttière se déformer sous le poids de "
              "l'eau et de la neige.",
              "<b>La descente.</b> Son diamètre et son nombre comptent autant que la gouttière. "
              "Une seule descente pour une longue façade crée un point de saturation."]),
            ("Les signes qu'il faut intervenir",
             ["<b>Une trace verte ou noire sur la façade, sous la gouttière.</b> C'est de l'eau qui "
              "passe en continu par une fissure ou un joint. La façade s'abîme avant que vous ne "
              "voyiez la gouttière fuir.",
              "<b>De l'eau qui déborde par l'arrière.</b> Signe d'un engorgement ou d'une pente "
              "inversée. L'eau part alors sous la première rangée de tuiles et mouille le bas de "
              "charpente : c'est le cas le plus sournois.",
              "<b>Des végétaux qui poussent dedans.</b> Il y a assez de terre accumulée pour "
              "germer, donc assez pour bloquer l'écoulement.",
              "<b>Un affaissement visible.</b> Regardez la ligne depuis la rue. Un ventre au milieu "
              "signale des crochets qui lâchent.",
              "<b>Des gouttes qui gèlent en stalactites.</b> Joli, et mauvais signe : l'eau stagne "
              "au lieu de s'écouler."]),
            ("Réparer ou remplacer",
             ["Sur du zinc, la réparation locale a du sens : une soudure sur une fissure ou un "
              "raccord reprend proprement, et le reste de la gouttière a encore des décennies "
              "devant lui.",
              "Sur du PVC vieilli, non. Un élément qui casse signifie que les autres sont au même "
              "stade de fragilisation. Réparer revient à revenir tous les six mois.",
              "Sur de l'aluminium en continu, une déformation ponctuelle peut se redresser, mais "
              "une perforation demande généralement de reprendre la longueur.",
              "Dans tous les cas, si la gouttière doit être déposée et que la couverture arrive en "
              "fin de vie, il vaut mieux attendre et faire les deux ensemble : on ne monte qu'une "
              "fois l'échafaudage."]),
        ],
        faq=[("Peut-on mettre du zinc sur une maison récente ?",
              "Bien sûr. Le zinc n'est pas réservé à l'ancien. Il se pose sur tout, et sa longévité "
              "en fait souvent le choix le plus économique sur la durée de vie de la maison."),
             ("Les protections anti-feuilles, ça marche ?",
              "Partiellement. Elles réduisent les gros débris mais laissent passer les aiguilles de "
              "résineux et les particules fines, qui finissent par former un tapis sous la grille, "
              "plus difficile à retirer. Sous des arbres, elles aident ; ailleurs, elles servent peu."),
             ("Tous les combien nettoyer ses gouttières ?",
              "Une fois par an, à l'automne après la chute des feuilles. Deux fois si la maison est "
              "sous des arbres. C'est l'entretien le moins cher et le plus rentable du bâtiment."),
             ("Le PLU peut-il imposer un matériau ?",
              "Oui, en secteur protégé ou en périmètre de monument historique. Le zinc est alors "
              "souvent exigé, le PVC blanc généralement refusé. Cela se vérifie avant de commander.")],
        cta=("Faire chiffrer des gouttières", "zinguerie-gouttieres"),
    ),
    dict(
        slug="charpente-signes-faiblesse",
        cle="La charpente ne fuit pas. Elle plie, et on ne la regarde jamais.",
        img="charpente-ancienne-sous-toiture.webp",
        imgalt="Charpente ancienne en bois vue depuis les combles",
        nav="Charpente : les signes de faiblesse",
        title="Charpente : reconnaître les signes de faiblesse",
        desc="Comment contrôler soi-même l'état d'une charpente depuis les combles, quels signes "
             "imposent un avis professionnel, et ce que coûte l'attente.",
        h1=("Charpente : les <em>signes</em>", "qui doivent alerter"),
        court="Une charpente se contrôle depuis les combles, pas depuis le toit, et vous pouvez "
              "faire le premier examen vous-même avec une lampe et un tournevis. Les trois signes "
              "à chercher : <b>du bois qui se creuse à la pointe, de la sciure fraîche au sol, et "
              "une ligne de toit qui n'est plus droite vue de la rue</b>.",
        estim=False,
        sections=[
            ("Le contrôle que vous pouvez faire vous-même",
             ["Montez dans les combles par temps sec, avec une lampe puissante et un tournevis fin. "
              "Comptez vingt minutes.",
              "<b>Le test du tournevis.</b> Appuyez la pointe sur le bois, sans forcer, à plusieurs "
              "endroits : pieds de chevrons, abouts de pannes, zones sous les cheminées. Un bois "
              "sain résiste. Un bois attaqué s'enfonce comme du carton et se creuse.",
              "<b>Cherchez la sciure.</b> De petits tas de sciure fine au sol ou sur les entraits "
              "signalent une activité d'insectes en cours. De la sciure ancienne, tassée et grise, "
              "signale une attaque passée, éventuellement arrêtée.",
              "<b>Repérez les trous.</b> Des trous de sortie ronds de deux à trois millimètres "
              "indiquent des vrillettes ou des capricornes. Frais, ils sont clairs à l'intérieur.",
              "<b>Touchez.</b> Un bois humide au toucher, ou noirci, ou qui sent le champignon, "
              "signale une infiltration active ou récente. C'est le signe le plus urgent."]),
            ("Ce qui se voit depuis la rue",
             ["Reculez de vingt mètres et regardez la ligne de faîtage, puis les versants, de "
              "préférence en lumière rasante le matin ou le soir.",
              "<b>Un faîtage qui ondule ou qui se creuse en son milieu</b> signale des pannes qui "
              "fléchissent. C'est structurel, et ça ne se corrige pas en changeant des tuiles.",
              "<b>Un versant bombé ou creusé par endroits</b> indique des chevrons qui ont perdu "
              "leur rectitude, souvent parce qu'ils ont été mouillés durablement.",
              "<b>Un débord de toit qui plonge</b> à une extrémité signale des abouts de chevrons "
              "pourris : c'est la zone la plus exposée, au contact de la gouttière.",
              "Attention à ne pas confondre : beaucoup de charpentes anciennes ont toujours eu un "
              "léger mouvement, pris il y a un siècle et parfaitement stable depuis. Ce qui "
              "inquiète, c'est une déformation qui évolue."]),
            ("Les trois causes, par ordre de gravité",
             ["<b>L'eau.</b> De loin la première. Une infiltration qui dure quelques semaines ne "
              "fait rien. La même sur des années fait pourrir le bois et installe des champignons "
              "lignivores, dont la mérule, qui se propage sans lumière et attaque très vite. Une "
              "fuite réparée à temps protège la charpente.",
              "<b>Les insectes à larves xylophages.</b> Capricornes et vrillettes creusent "
              "l'intérieur du bois en laissant la surface intacte. C'est pour ça que le test du "
              "tournevis compte plus que l'aspect. Un traitement curatif existe et fonctionne s'il "
              "est fait par un professionnel, avec injection.",
              "<b>La surcharge.</b> Plus rare, mais réelle : une couverture lourde posée sur une "
              "charpente dimensionnée pour un matériau léger, ou une isolation ajoutée sans "
              "vérification. Une charpente de fermettes industrielles ne se modifie jamais sans "
              "calcul : couper un seul élément peut déséquilibrer tout l'ensemble."]),
            ("Ce que coûte l'attente",
             ["Une charpente prise à temps se répare par greffe : on remplace la partie abîmée, on "
              "renforce, on traite. Le chantier reste circonscrit et l'ossature d'origine est "
              "conservée.",
              "La même charpente laissée deux hivers de plus avec de l'eau qui entre demande la "
              "dépose de la couverture, le remplacement de pièces maîtresses, parfois un étaiement. "
              "L'écart de coût se compte en multiples, pas en pourcentages.",
              "Et le point qui change tout : <b>tant que la couverture est encore bonne, on ne "
              "touche pas au toit pour reprendre la charpente</b>. Une fois qu'il faut déposer, on "
              "additionne deux chantiers.",
              "C'est la raison pour laquelle nous regardons systématiquement les combles quand nous "
              "venons pour autre chose. C'est vingt minutes, et c'est souvent là que se joue le "
              "vrai sujet."]),
        ],
        faq=[("Un traitement de charpente en bombe, ça sert à quelque chose ?",
              "Sur une attaque superficielle et limitée, un peu. Sur une infestation installée, non : "
              "le produit doit être injecté en profondeur après sondage et bûchage des parties "
              "attaquées. Méfiez-vous de qui propose un traitement sans avoir sondé."),
             ("Comment savoir si l'attaque est encore active ?",
              "La sciure fraîche, claire et fine, est le meilleur indice. Vous pouvez aussi nettoyer "
              "une zone, la marquer, et revenir voir quelques semaines plus tard s'il y a de "
              "nouveaux dépôts."),
             ("La mérule, c'est vraiment si grave ?",
              "Oui. C'est un champignon qui se développe dans l'obscurité et l'humidité, traverse "
              "les maçonneries et dégrade le bois très rapidement. Sa présence doit être traitée "
              "par une entreprise spécialisée, et elle est déclarable dans certains départements."),
             ("Peut-on isoler une charpente attaquée ?",
              "Non, et c'est une erreur fréquente. Isoler enferme le bois, supprime la ventilation "
              "et masque l'évolution. On traite, on vérifie que c'est arrêté, puis on isole.")],
        cta=("Faire contrôler la charpente", "charpente"),
    ),
    dict(
        slug="ecran-sous-toiture",
        cle="C'est la deuxième peau. On ne la voit jamais, et c'est elle qui sauve les combles.",
        img="couvreur-nonancourt-pose-ecran-sous-toiture.webp",
        imgalt="Pose d'un écran de sous-toiture sur une charpente avant la couverture",
        nav="L'écran de sous-toiture",
        title="Écran de sous-toiture : à quoi ça sert",
        desc="Ce que fait un écran de sous-toiture, pourquoi les toits anciens n'en ont pas, et "
             "s'il est possible d'en poser un sans déposer toute la couverture.",
        h1=("L'écran de <em>sous-toiture</em>,", "la deuxième peau du toit"),
        court="Une couverture n'est pas étanche : elle est <b>imperméable au ruissellement, pas au "
              "vent</b>. Sous une pluie battante poussée par le vent, de l'eau passe entre les "
              "tuiles. L'écran de sous-toiture est la membrane posée sous les tuiles qui récupère "
              "cette eau et la conduit jusqu'à la gouttière. La plupart des toits d'avant 1980 "
              "n'en ont pas.",
        estim=False,
        sections=[
            ("Ce qu'il fait, et ce qu'il ne fait pas",
             ["<b>Il évacue l'eau qui passe.</b> Neige poudreuse soufflée sous les tuiles, pluie "
              "horizontale, tuile légèrement déplacée : l'eau tombe sur l'écran, glisse le long de "
              "la pente et rejoint la gouttière sans jamais toucher l'isolant ni la charpente.",
              "<b>Il arrête les poussières et les insectes.</b> Une couverture sans écran laisse "
              "passer de la poussière, des feuilles, des insectes et parfois des rongeurs dans les "
              "combles.",
              "<b>Il sécurise pendant le chantier.</b> Une toiture déposée et re-couverte en "
              "plusieurs jours reste protégée la nuit.",
              "<b>Il ne remplace pas la couverture.</b> Un écran exposé au soleil se dégrade en "
              "quelques mois. Ce n'est pas une solution de secours durable.",
              "<b>Il ne règle pas une fuite ponctuelle.</b> Une noue percée ou un solin ouvert "
              "laissent entrer bien plus d'eau qu'un écran ne peut en évacuer."]),
            ("Respirant ou non : le choix qui compte",
             ["<b>L'écran HPV, hautement perméable à la vapeur</b>, laisse la vapeur d'eau sortir "
              "des combles tout en bloquant l'eau liquide. Il se pose directement sur l'isolant, "
              "sans lame d'air au-dessus. C'est le standard actuel en rénovation isolée.",
              "<b>L'écran non respirant</b>, moins cher, impose une lame d'air ventilée de deux "
              "centimètres entre lui et l'isolant. Sans cette lame d'air, la vapeur qui monte des "
              "pièces se condense sous l'écran et mouille l'isolant en permanence. C'est l'erreur "
              "la plus coûteuse qu'on voit en rénovation.",
              "Le point à retenir : <b>un écran non respirant posé au contact de l'isolant crée "
              "exactement le dégât qu'il était censé éviter</b>. Si votre devis mentionne un écran, "
              "demandez lequel et comment il est posé.",
              "Les entrées d'air en bas de toit et les sorties en faîtage font partie du système. "
              "Un écran posé sans ventilation correcte ne fonctionne pas."]),
            ("Peut-on en poser un sans tout déposer ?",
             ["<b>Par l'extérieur : c'est la seule méthode propre.</b> L'écran se pose sur les "
              "chevrons, sous les liteaux. Il faut donc déposer les tuiles et les liteaux. "
              "Autrement dit, cela se fait au moment d'une réfection, pas isolément.",
              "<b>Par l'intérieur : possible, avec des réserves.</b> On agrafe des bandes entre "
              "les chevrons depuis les combles. C'est moins continu, les recouvrements sont "
              "moins fiables, et le travail est pénible. Cela dépanne, ce n'est pas équivalent.",
              "<b>Ce qui ne marche pas :</b> glisser un film sous les tuiles sans déposer. Les "
              "recouvrements ne sont pas tenus, l'eau passe aux jonctions, et on ne peut pas "
              "raccorder correctement en bas de pente.",
              "Concrètement : si votre couverture tient encore dix ans, attendez la réfection. Si "
              "elle est en fin de vie, l'écran est compris dans le chantier et ne représente qu'un "
              "faible pourcentage du total."]),
            ("Est-ce obligatoire ?",
             ["Il n'existe pas d'obligation générale de poser un écran de sous-toiture en "
              "rénovation. Les règles de l'art, elles, le recommandent systématiquement en neuf et "
              "en réfection complète, et certains documents techniques l'imposent selon la zone "
              "climatique, la pente et le matériau.",
              "En pratique, aucun couvreur sérieux ne refait une couverture sans écran aujourd'hui. "
              "Le surcoût est modeste rapporté au chantier, et l'absence d'écran est ce qui "
              "transforme une tuile déplacée en dégât des eaux.",
              "<b>Un point qui a des conséquences :</b> si un sinistre survient et que la pose "
              "s'écarte des règles de l'art, la garantie décennale peut être discutée. Un devis de "
              "réfection sans écran devrait vous faire poser des questions.",
              "Sur les maisons anciennes de la vallée de l'Avre, l'absence d'écran est la règle et "
              "non l'exception. C'est le premier point que nous regardons quand nous montons."]),
        ],
        faq=[("Mon toit n'a pas d'écran et ne fuit pas. Faut-il s'inquiéter ?",
              "Non. Des millions de toits fonctionnent ainsi depuis un siècle. L'écran est une "
              "sécurité supplémentaire, pas une condition d'étanchéité. Il devient important dès "
              "qu'on isole les combles, parce qu'un isolant mouillé ne sèche plus."),
             ("Est-ce qu'un écran remplace une isolation ?",
              "Pas du tout, ce sont deux fonctions différentes. L'écran gère l'eau, l'isolant gère "
              "la chaleur. Ils travaillent ensemble, et l'écran protège l'isolant."),
             ("Combien de temps dure un écran de sous-toiture ?",
              "Un écran de qualité, protégé du soleil par la couverture, dure aussi longtemps que "
              "la couverture elle-même. On le remplace au chantier suivant."),
             ("Peut-on poser un écran sur une couverture en ardoise ?",
              "Oui, le principe est le même. Sur ardoise clouée sur voligeage plein, la question de "
              "la ventilation se pose différemment et demande une étude au cas par cas.")],
        cta=("Parler de la réfection du toit", "renovation-toiture"),
    ),
    dict(
        slug="nettoyer-toiture-soi-meme",
        cle="Chaque année, des gens meurent en tombant d'un toit qu'ils nettoyaient.",
        img="couvreur-wm-couverture-sur-le-toit.webp",
        imgalt="Couvreur travaillant en sécurité sur le faîtage d'un pavillon",
        nav="Nettoyer sa toiture soi-même",
        title="Nettoyer sa toiture soi-même : les risques",
        desc="Ce qu'on peut raisonnablement faire soi-même sur une toiture, ce qu'il ne faut pas "
             "tenter, et les erreurs de nettoyage qui abîment durablement la tuile.",
        h1=("Nettoyer sa toiture <em>soi-même</em> :", "ce qu'il faut savoir"),
        court="Certaines choses se font sans risque depuis le sol ou une échelle stable : vider une "
              "gouttière accessible, dégager des feuilles, observer. <b>Monter sur les pans du toit "
              "n'en fait pas partie.</b> Une tuile humide ou moussue est une patinoire, et la chute "
              "de hauteur reste la première cause d'accident grave dans le bâtiment.",
        estim=False,
        sections=[
            ("Ce que vous pouvez faire sans danger",
             ["<b>Observer, régulièrement.</b> Depuis le sol, avec des jumelles si besoin, en "
              "lumière rasante. Vous repérerez une tuile déplacée, une ligne qui bouge, une zone "
              "qui verdit plus que les autres. C'est l'entretien le plus utile et il ne coûte rien.",
              "<b>Vider une gouttière accessible</b> depuis une échelle stable, posée sur sol "
              "plat, avec quelqu'un qui la tient, et sans jamais se pencher au-delà de la largeur "
              "de l'échelle. Si vous devez vous étirer, descendez et déplacez l'échelle.",
              "<b>Dégager les abords.</b> Couper une branche qui frotte la couverture ou qui "
              "déverse ses feuilles dans la gouttière évite une grande partie du problème.",
              "<b>Contrôler les combles.</b> C'est là que le vrai diagnostic se fait, au sec et de "
              "plain-pied. Une lampe suffit.",
              "<b>Photographier après une tempête.</b> Depuis le sol, sous plusieurs angles. Ces "
              "photos serviront à l'assurance et au couvreur."]),
            ("Ce qu'il ne faut pas tenter",
             ["<b>Marcher sur les tuiles.</b> Outre le risque de chute, on casse ce sur quoi on "
              "marche, et les fissures ne se voient pas tout de suite. On répare ensuite des dégâts "
              "qu'on a soi-même créés.",
              "<b>Le nettoyeur haute pression.</b> C'est l'erreur la plus répandue. La pression "
              "enlève la mousse et, avec elle, l'engobe : la couche de surface cuite qui limite la "
              "porosité de la tuile. Le toit est éclatant pendant un an, puis il se remousse plus "
              "vite qu'avant et devient gélif. Sur une tuile ancienne, c'est irréversible.",
              "<b>Pulvériser sous la pluie ou par grand vent.</b> Le produit part avant d'agir, et "
              "il se disperse dans le jardin et le potager.",
              "<b>La javel.</b> Elle blanchit la mousse sans la tuer en profondeur, elle attaque "
              "les joints et le zinc des gouttières, et elle finit dans le sol.",
              "<b>Monter seul.</b> Si quelque chose arrive, personne ne le sait."]),
            ("Les erreurs de produit et de méthode",
             ["<b>Rincer un anti-mousse curatif.</b> Un produit rémanent est fait pour rester et "
              "agir plusieurs semaines : la mousse noircit, meurt et part avec la pluie. Le rincer "
              "le lendemain, c'est payer un produit et le jeter.",
              "<b>Traiter sans avoir enlevé le gros.</b> Sur un tapis de mousse épais, le produit "
              "n'atteint jamais la tuile. Il faut d'abord retirer mécaniquement, puis traiter.",
              "<b>Travailler du bas vers le haut.</b> On descend toujours : sinon on repasse sur ce "
              "qui est déjà traité et on le lessive.",
              "<b>Oublier les gouttières.</b> Tout ce qui est décroché du toit y finit. Une "
              "gouttière bouchée après nettoyage déborde vers l'arrière et mouille le bas de "
              "charpente : on a créé un problème en en réglant un autre."]),
            ("Le vrai calcul",
             ["Un démoussage professionnel sur une maison de taille courante représente quelques "
              "centaines d'euros, tous les trois à cinq ans. Rapporté à l'année, c'est peu.",
              "En face : le coût d'un échafaudage ou d'une nacelle loués, le produit, une journée "
              "de travail, et un risque de chute que rien ne compense.",
              "Sans compter ce qui ne se voit pas tout de suite : une tuile décapée au karcher "
              "perd des années de durée de vie, et quelques tuiles fissurées sous les pas se "
              "révèlent au premier gros orage.",
              "Nous ne disons pas ça pour vendre un démoussage. Nous le disons parce que nous "
              "sommes régulièrement appelés pour réparer des toits abîmés par un nettoyage bien "
              "intentionné, et que la réparation coûte plus cher que le démoussage évité."]),
        ],
        faq=[("Existe-t-il des produits anti-mousse à pulvériser depuis le sol ?",
              "Oui, avec une lance télescopique, et ils fonctionnent sur une mousse naissante. Sur "
              "un tapis installé, la pulvérisation seule ne suffit pas : il faut un passage "
              "mécanique préalable."),
             ("Et si je loue une nacelle ?",
              "Cela règle le risque de chute mais pas le reste : le choix de la pression, la "
              "connaissance du matériau, la gestion des tuiles fragiles. Et une nacelle louée coûte "
              "une part importante du prix d'un démoussage complet."),
             ("Quand faut-il le faire ?",
              "Printemps ou automne, hors gel et hors forte chaleur. Un traitement appliqué juste "
              "avant une période pluvieuse modérée agit bien."),
             ("Le démoussage abîme-t-il la toiture ?",
              "Mal fait, oui, beaucoup. Bien fait, non : on adapte la pression au matériau, on ne "
              "décape pas, et on remplace les tuiles fragilisées au passage.")],
        cta=("Faire démousser par un professionnel", "demoussage-toiture"),
    ),
    dict(
        slug="toiture-copropriete",
        cle="Le toit est commun. La décision aussi, et c'est là que tout se joue.",
        img="couvreur-dreux-maison-de-ville-toiture.webp",
        imgalt="Toiture de maison de ville mitoyenne à Dreux",
        nav="Toiture en copropriété",
        title="Toiture en copropriété : qui paie quoi",
        desc="Comment se décide et se répartit une réfection de toiture en copropriété, ce qui "
             "relève des parties communes, et ce qu'il faut préparer avant l'assemblée générale.",
        h1=("Toiture en <em>copropriété</em> :", "qui décide, qui paie"),
        court="La toiture est une <b>partie commune</b> : sa réfection se vote en assemblée "
              "générale et se répartit entre tous les copropriétaires selon les tantièmes, y "
              "compris ceux du rez-de-chaussée. Les fenêtres de toit privatives et l'intérieur des "
              "combles aménagés font exception et restent à la charge de leur propriétaire.",
        estim=False,
        sections=[
            ("Ce qui est commun, ce qui ne l'est pas",
             ["<b>Commun :</b> la charpente, la couverture, l'écran de sous-toiture, la zinguerie, "
              "les gouttières et descentes, les souches de cheminée dans leur partie extérieure, "
              "l'étanchéité des terrasses.",
              "<b>Privatif :</b> l'intérieur d'un comble aménagé, le revêtement de plafond, "
              "l'isolation posée par un copropriétaire dans son lot, et le plus souvent les "
              "fenêtres de toit qui n'éclairent qu'un lot.",
              "<b>La zone grise :</b> une fenêtre de toit est privative pour son entretien courant, "
              "mais son raccordement à la couverture touche une partie commune. En pratique, c'est "
              "le règlement de copropriété qui tranche, et il faut le lire avant de débattre.",
              "Le point qui surprend le plus : <b>un copropriétaire du rez-de-chaussée participe "
              "au financement du toit</b>, au prorata de ses tantièmes, exactement comme celui du "
              "dernier étage. C'est la règle des parties communes."]),
            ("Comment la décision se prend",
             ["<b>Les travaux d'entretien et de réparation</b> — reprendre un solin, remplacer des "
              "tuiles, nettoyer les gouttières — se votent à la majorité simple des "
              "copropriétaires présents ou représentés.",
              "<b>Les travaux d'amélioration</b> — ajouter une isolation, changer de matériau de "
              "couverture, transformer l'aspect — relèvent d'une majorité renforcée, celle de tous "
              "les copropriétaires.",
              "<b>L'urgence fait exception.</b> Le syndic peut engager seul les travaux nécessaires "
              "à la sauvegarde de l'immeuble, comme une mise hors d'eau après une tempête, et il "
              "en rend compte à l'assemblée suivante. Il ne peut pas, en revanche, lancer une "
              "réfection complète sous couvert d'urgence.",
              "En pratique, une réfection de toiture se prépare un an à l'avance : diagnostic, "
              "devis multiples, inscription à l'ordre du jour, vote, puis appels de fonds."]),
            ("Ce qu'il faut préparer avant l'assemblée",
             ["<b>Un diagnostic écrit et indépendant du devis.</b> L'état réel de la couverture et "
              "de la charpente, avec des photos. C'est ce qui évite le débat entre « on peut encore "
              "attendre » et « c'est urgent ».",
              "<b>Trois devis comparables.</b> Comparables veut dire : même surface annoncée, même "
              "matériau, mêmes postes. Trois devis qui ne décrivent pas le même chantier ne se "
              "comparent pas, et c'est la source principale des reports de vote.",
              "<b>Le plan de financement.</b> Fonds de travaux disponible, échéancier des appels, "
              "et éventuels dispositifs d'aide mobilisables par la copropriété.",
              "<b>Les contraintes d'urbanisme.</b> En centre ancien ou en périmètre protégé, "
              "l'avis des services du patrimoine peut imposer un matériau et rallonger le délai de "
              "plusieurs mois. Le savoir avant le vote évite de revoter."]),
            ("Les points qui font perdre du temps",
             ["<b>Le désaccord sur l'urgence.</b> Il se règle avec un diagnostic, pas avec des "
              "arguments. Faites monter un professionnel et demandez un écrit.",
              "<b>Les devis incomparables.</b> Imposez la même trame à tous : surface en rampant, "
              "matériau, écran, zinguerie, échafaudage, évacuation. Chaque poste chiffré à part.",
              "<b>L'échafaudage et les accès.</b> Sur une maison de ville, le stationnement, "
              "l'emprise sur le trottoir et l'autorisation de voirie sont des sujets à part "
              "entière, à anticiper et à chiffrer.",
              "<b>Les lots du dernier étage.</b> Ce sont eux qui subissent les infiltrations, et "
              "eux qui poussent au vote. Documenter les dégâts avec des dates aide plus qu'insister.",
              "Nous chiffrons les copropriétés avec un devis décomposé poste par poste, "
              "précisément pour qu'il puisse être lu en assemblée par des gens qui ne sont pas du "
              "métier."]),
        ],
        faq=[("Un copropriétaire peut-il refuser de payer ?",
              "Non. Une fois les travaux votés régulièrement, la dépense s'impose à tous selon les "
              "tantièmes, y compris à ceux qui ont voté contre."),
             ("Qui paie si une fuite abîme un appartement ?",
              "La réparation du toit relève de la copropriété. Les dégâts intérieurs relèvent de "
              "l'assurance du copropriétaire, avec un recours possible vers celle de l'immeuble."),
             ("Peut-on faire poser une fenêtre de toit seul ?",
              "Non, pas sans autorisation de l'assemblée : percer la couverture touche une partie "
              "commune et modifie l'aspect extérieur. Le vote est nécessaire même si le lot est privatif."),
             ("Le syndic peut-il choisir l'entreprise seul ?",
              "Il propose, l'assemblée choisit. Le vote porte en général sur une entreprise "
              "identifiée et un montant, pas sur un blanc-seing.")],
        cta=("Faire chiffrer une toiture d'immeuble", "renovation-toiture"),
    ),
    dict(
        slug="duree-chantier-toiture",
        cle="Ce qui prend du temps, ce n'est presque jamais la pose.",
        img="renovation-toiture-charpente-liteaux-neufs.webp",
        imgalt="Charpente et liteaux neufs posés sur une toiture en cours de rénovation",
        nav="Combien de temps dure le chantier",
        title="Combien de temps dure une réfection de toiture",
        desc="Les durées réelles d'un chantier de toiture selon son ampleur, ce qui les allonge, "
             "et comment se passe le déroulement au quotidien pour les habitants.",
        h1=("Combien de <em>temps</em>", "dure un chantier de toiture"),
        court="Sur une maison de taille courante, une réfection complète demande en général "
              "<b>une à deux semaines de présence sur le chantier</b>, hors intempéries. Mais entre "
              "la signature et la fin, comptez plutôt deux à quatre mois : le délai vient de "
              "l'autorisation d'urbanisme, de l'approvisionnement et du planning, pas de la pose.",
        estim=False,
        sections=[
            ("Les durées réelles, par type de chantier",
             ["<b>Remplacement de quelques tuiles, reprise d'un solin :</b> une demi-journée à une "
              "journée. Souvent sans échafaudage si l'accès le permet.",
              "<b>Démoussage complet :</b> une à deux journées selon la surface et l'accès, plus "
              "le temps d'action du traitement, qui se fait tout seul ensuite.",
              "<b>Reprise de zinguerie, gouttières d'une façade :</b> une à deux journées.",
              "<b>Réfection d'un versant :</b> trois à cinq jours de présence.",
              "<b>Réfection complète d'une maison courante :</b> une à deux semaines. Avec "
              "isolation par l'extérieur, comptez une semaine de plus.",
              "<b>Reprise de charpente :</b> variable, de deux jours pour une greffe à plusieurs "
              "semaines si l'ossature est largement touchée.",
              "Ces durées s'entendent hors intempéries. Une toiture ouverte ne se travaille ni sous "
              "la pluie ni par vent fort : c'est une question de sécurité, pas de confort."]),
            ("Ce qui allonge vraiment les délais",
             ["<b>L'autorisation d'urbanisme.</b> Une déclaration préalable prend un mois "
              "d'instruction, deux si le bien est en périmètre de monument historique. C'est "
              "souvent le premier poste de délai, et il court avant tout le reste.",
              "<b>L'approvisionnement.</b> Une tuile courante est disponible. Une tuile de pays, un "
              "modèle imposé par le PLU ou un coloris particulier peuvent demander plusieurs "
              "semaines de fabrication.",
              "<b>L'échafaudage.</b> Sa location, son montage et l'éventuelle autorisation de "
              "voirie en ville ajoutent des jours à chaque extrémité du chantier.",
              "<b>La saison.</b> Le printemps et l'été sont pleins. Un chantier signé en février "
              "démarre souvent plus vite qu'un chantier signé en juin.",
              "<b>Les surprises de dépose.</b> On découvre l'état réel de la charpente en enlevant "
              "la couverture. C'est pour cela qu'un devis sérieux prévoit une ligne pour les "
              "reprises éventuelles, avec un prix unitaire convenu à l'avance."]),
            ("Comment ça se passe pour vous, au quotidien",
             ["<b>Le bruit.</b> La dépose est la phase la plus bruyante, et c'est la première. Elle "
              "dure un à deux jours. Ensuite, c'est le bruit d'un chantier normal.",
              "<b>La poussière.</b> Beaucoup, à la dépose, surtout si les combles sont ouverts. "
              "Protéger ce qui s'y trouve et fermer la trappe change tout.",
              "<b>L'accès.</b> L'échafaudage occupe le pourtour. Prévoyez de dégager les abords et "
              "de déplacer les véhicules pour toute la durée.",
              "<b>Habiter sur place.</b> C'est la règle : on ne déménage pas pour une réfection de "
              "toiture. Le logement reste hors d'eau chaque soir, c'est la responsabilité de "
              "l'entreprise.",
              "<b>Les horaires.</b> Une journée de couvreur commence tôt, surtout l'été. Prévenir "
              "les voisins avant le démarrage évite bien des tensions."]),
            ("Ce qui doit figurer au planning",
             ["<b>Une date de démarrage, pas une saison.</b> « Courant printemps » n'engage "
              "personne. Une semaine de démarrage, oui.",
              "<b>La durée prévisionnelle de présence</b>, distincte du délai global.",
              "<b>Le moment de l'échafaudage :</b> montage et démontage, avec les dates.",
              "<b>Les points d'arrêt :</b> les moments où vous pouvez constater avant que la suite "
              "recouvre. Le contrôle de charpente avant pose de l'écran, par exemple.",
              "<b>Le nettoyage et l'évacuation.</b> Une réfection produit des tonnes de gravats. Qui "
              "les évacue, quand, et est-ce compris ?",
              "Nous donnons une semaine de démarrage et une durée de présence, et nous prévenons "
              "s'il y a du retard. Un chantier reporté parce qu'il pleut, cela arrive à tout le "
              "monde ; ne pas prévenir, non."]),
        ],
        faq=[("Peut-on faire refaire un toit en hiver ?",
              "Oui, hors gel et hors vent fort. Les journées sont plus courtes, donc le chantier "
              "s'étale, mais le travail est le même. Les plannings sont souvent plus disponibles."),
             ("Et s'il pleut pendant le chantier ?",
              "On ne laisse jamais un toit ouvert le soir : la zone en cours est bâchée ou "
              "l'écran est posé. La pluie décale la pose, elle ne met pas la maison en danger."),
             ("Faut-il être présent tous les jours ?",
              "Non. Il est utile d'être là au démarrage, aux points d'arrêt convenus et à la "
              "réception. Le reste du temps, l'accès au terrain suffit."),
             ("Le délai annoncé est-il contractuel ?",
              "La date de démarrage et la durée figurent au devis et engagent. Les intempéries "
              "constituent une cause de suspension reconnue, à condition d'être signalées.")],
        cta=("Parler du planning d'un chantier", "renovation-toiture"),
    ),
    dict(
        slug="assurance-decennale-couvreur",
        cle="Ce n'est pas une garantie sur les tuiles. C'est une garantie sur l'étanchéité.",
        img="refection-toiture-pavillon-terminee.webp",
        imgalt="Réfection de toiture de pavillon terminée",
        nav="La garantie décennale",
        title="Garantie décennale : ce qu'elle couvre vraiment",
        desc="Ce que couvre et ne couvre pas la garantie décennale d'un couvreur, comment vérifier "
             "l'attestation, et ce qu'il faut conserver pour pouvoir l'actionner.",
        h1=("Garantie <em>décennale</em> :", "ce qu'elle couvre vraiment"),
        court="La décennale couvre pendant dix ans les dommages qui <b>compromettent la solidité de "
              "l'ouvrage ou le rendent impropre à sa destination</b>. Sur un toit, cela veut dire "
              "concrètement : l'eau qui entre. Elle ne couvre ni l'usure, ni l'esthétique, ni ce "
              "qui n'a pas été fait faute d'avoir été prévu au devis.",
        estim=False,
        sections=[
            ("Les trois garanties, qui ne durent pas pareil",
             ["<b>La garantie de parfait achèvement : un an.</b> Elle couvre toutes les réserves "
              "signalées à la réception, et tous les désordres apparus dans l'année, quels qu'ils "
              "soient. C'est la plus large, et la plus courte.",
              "<b>La garantie de bon fonctionnement : deux ans.</b> Elle porte sur les éléments "
              "d'équipement dissociables, c'est-à-dire ce qui peut s'enlever sans abîmer "
              "l'ouvrage : une fenêtre de toit, un conduit, un élément de ventilation.",
              "<b>La garantie décennale : dix ans.</b> Elle porte sur les désordres qui touchent la "
              "solidité ou rendent le bien impropre à son usage. Une infiltration en fait partie, "
              "par définition.",
              "Les trois courent <b>à compter de la réception des travaux</b>, pas de la facture ni "
              "de la fin du chantier. C'est pourquoi le procès-verbal de réception, daté et signé, "
              "est le document le plus important du dossier."]),
            ("Ce qui est couvert, ce qui ne l'est pas",
             ["<b>Couvert :</b> une infiltration due à un défaut de pose, un écran mal raccordé, "
              "un solin mal exécuté, une couverture qui se soulève au vent parce qu'elle n'était "
              "pas correctement fixée, une charpente qui fléchit après une reprise mal calculée.",
              "<b>Non couvert :</b> l'usure normale, un événement climatique exceptionnel, un "
              "défaut d'entretien, des travaux réalisés ensuite par quelqu'un d'autre, et les "
              "désordres purement esthétiques comme une différence de teinte entre deux lots de "
              "tuiles.",
              "<b>La zone discutée :</b> ce qui n'était pas au devis. Si l'écran de sous-toiture "
              "n'a pas été posé parce qu'il n'était pas prévu, ce n'est pas un défaut d'exécution. "
              "D'où l'importance d'un devis détaillé : il définit ce à quoi l'entreprise s'engage.",
              "<b>Un point souvent ignoré :</b> la décennale suit l'ouvrage, pas le propriétaire. "
              "Si vous vendez, l'acheteur bénéficie du reliquat. Les factures et le procès-verbal "
              "de réception font partie des documents à transmettre."]),
            ("Vérifier l'attestation en trois minutes",
             ["<b>L'année en cours.</b> Une attestation est annuelle. Celle de l'an dernier ne "
              "prouve rien sur aujourd'hui. Demandez celle de l'exercice en cours, avant le "
              "démarrage.",
              "<b>L'activité déclarée.</b> Elle doit mentionner explicitement la couverture, et la "
              "charpente si le chantier en comporte. Une décennale « maçonnerie » ne couvre pas un "
              "toit.",
              "<b>Le nom et le SIRET.</b> Ils doivent correspondre exactement à ceux du devis. Une "
              "attestation au nom d'une autre société est un signal d'alerte.",
              "<b>Les montants et les exclusions.</b> Elles sont au dos, et elles se lisent. "
              "Certains contrats plafonnent par chantier.",
              "<b>En cas de doute :</b> l'assureur figure sur l'attestation. Un appel suffit à "
              "confirmer qu'un contrat est bien en cours. C'est rare, et c'est légitime."]),
            ("Ce qu'il faut garder pour pouvoir l'actionner",
             ["<b>Le devis signé</b>, avec le détail des postes. C'est lui qui définit ce qui "
              "devait être fait.",
              "<b>Le procès-verbal de réception</b>, daté et signé des deux parties, avec les "
              "réserves éventuelles. C'est le point de départ des trois garanties.",
              "<b>La facture acquittée.</b>",
              "<b>L'attestation d'assurance</b> de l'année du chantier, pas celle d'après.",
              "<b>Les photos.</b> Avant, pendant, après. Nous en remettons systématiquement, et "
              "elles servent bien plus souvent qu'on ne le croit : pour l'assurance, pour une "
              "vente, ou simplement pour savoir ce qu'il y a sous les tuiles dans dix ans.",
              "Rangez l'ensemble au même endroit. Le jour où cela sert, c'est en général plusieurs "
              "années plus tard et par quelqu'un d'autre que vous."]),
        ],
        faq=[("L'entreprise a disparu. La décennale joue-t-elle encore ?",
              "Oui, elle est portée par l'assureur, pas par l'entreprise. C'est précisément à ça "
              "qu'elle sert. Il faut l'attestation de l'année du chantier pour identifier l'assureur, "
              "d'où l'importance de la conserver."),
             ("Faut-il une assurance dommages-ouvrage ?",
              "Elle est légalement obligatoire pour le maître d'ouvrage, même particulier. En "
              "pratique elle est peu souscrite en rénovation. Son intérêt : elle indemnise vite, "
              "sans attendre la recherche de responsabilité."),
             ("Un devis sans mention d'assurance est-il valable ?",
              "Le devis reste valable, mais l'assurance décennale doit figurer sur les devis et "
              "factures avec l'assureur et la zone couverte. Son absence est une irrégularité."),
             ("Une réparation ponctuelle est-elle couverte dix ans ?",
              "Si elle relève de l'étanchéité, oui, dans les mêmes conditions. Une reprise de solin "
              "qui refuit deux ans après relève de la décennale.")],
        cta=("Demander un devis détaillé", "renovation-toiture"),
    ),
    dict(
        slug="isolation-combles-perdus",
        cle="C'est le mètre carré isolé le moins cher de toute la maison.",
        img="combles-avant-isolation-sous-rampants.webp",
        imgalt="Combles non isolés vus sous les rampants avant travaux",
        nav="Isoler des combles perdus",
        title="Isolation des combles perdus : quelle méthode",
        desc="Souffler, dérouler ou insuffler : les méthodes d'isolation des combles perdus, leurs "
             "épaisseurs, et les points de vigilance qui décident du résultat.",
        h1=("Isoler des <em>combles perdus</em> :", "quelle méthode choisir"),
        court="Un tiers environ des déperditions d'une maison mal isolée part par le toit, et les "
              "combles perdus sont l'endroit le plus simple et le moins cher à traiter. Deux "
              "méthodes dominent : <b>le soufflage de flocons</b>, rapide et adapté aux combles "
              "difficiles d'accès, et <b>le déroulage de rouleaux</b>, plus régulier quand le "
              "plancher est accessible.",
        estim=False,
        sections=[
            ("Les trois méthodes, et quand les choisir",
             ["<b>Le soufflage.</b> Des flocons — laine de verre, laine de roche, ouate de "
              "cellulose — projetés à la machine sur le plancher des combles. C'est rapide, cela "
              "atteint tous les recoins, et c'est la seule solution praticable quand les combles "
              "sont encombrés de fermettes serrées. L'épaisseur doit être repérée par des piges "
              "graduées laissées en place.",
              "<b>Le déroulage.</b> Des rouleaux posés en deux couches croisées, la seconde "
              "perpendiculaire à la première pour supprimer les ponts thermiques aux jonctions. "
              "Cela demande un accès correct et un plancher praticable. Le résultat est très "
              "régulier et il reste visitable.",
              "<b>L'insufflation.</b> Des flocons injectés sous pression dans un volume fermé. "
              "Elle sert surtout pour les rampants ou les caissons, rarement pour des combles "
              "perdus classiques.",
              "Sur des combles perdus accessibles, le déroulage est souvent préférable. Sur des "
              "fermettes industrielles serrées, le soufflage s'impose."]),
            ("Les épaisseurs, et ce qu'elles valent",
             ["La performance se mesure en résistance thermique, notée R : plus elle est élevée, "
              "mieux c'est. Les dispositifs d'aide exigent généralement <b>R ≥ 7 m²·K/W</b> en "
              "combles perdus.",
              "Concrètement, cela représente environ <b>30 à 40 cm</b> de laine, selon le matériau "
              "et sa conductivité. Une isolation ancienne de 10 cm, courante dans les maisons des "
              "années soixante-dix, est très loin du compte.",
              "Attention à la confusion entre épaisseur posée et épaisseur finale : les flocons "
              "soufflés se tassent. Un isolant soufflé doit être posé avec une surépaisseur qui "
              "tient compte de ce tassement, et les piges permettent de le contrôler plus tard.",
              "Surisoler par-dessus un ancien isolant est possible et souvent pertinent, à "
              "condition que l'ancien soit sec, sain et non tassé en croûte. S'il a été mouillé, il "
              "faut le retirer."]),
            ("Les points qui décident du résultat",
             ["<b>La trappe d'accès.</b> Une trappe non isolée dans un plafond isolé à 35 cm, c'est "
              "un trou dans la couverture thermique. Elle doit être isolée et étanche à l'air.",
              "<b>Les spots encastrés.</b> Chaque spot perce le plafond et la barrière d'étanchéité "
              "à l'air. Ils doivent être protégés par des capots adaptés, sous peine de risque "
              "d'échauffement et de fuite d'air chaud humide dans l'isolant.",
              "<b>La ventilation.</b> Isoler sans ventiler crée de la condensation. Les entrées "
              "d'air en bas de pente ne doivent jamais être bouchées par l'isolant : on pose des "
              "déflecteurs pour garder le passage libre.",
              "<b>Le pare-vapeur.</b> Côté chauffé, il empêche la vapeur d'eau des pièces de migrer "
              "dans l'isolant. Son absence ou sa pose du mauvais côté est l'erreur classique, et "
              "elle se paie en isolant mouillé.",
              "<b>L'état de la couverture.</b> Isoler sous une toiture qui fuit revient à poser une "
              "éponge. On vérifie le toit avant, systématiquement."]),
            ("Combles perdus ou aménageables : la distinction qui change tout",
             ["<b>Combles perdus :</b> le volume sous toiture n'est pas habitable, souvent à cause "
              "d'une hauteur insuffisante ou de fermettes en W. On isole <b>le plancher</b>, donc "
              "le plafond de l'étage en dessous. C'est peu cher, très efficace, et rapide.",
              "<b>Combles aménagés ou aménageables :</b> le volume est habitable. Il faut isoler "
              "<b>les rampants</b>, c'est-à-dire sous la pente, ce qui est plus complexe, plus cher "
              "et prend de la hauteur sous plafond.",
              "La confusion coûte cher : isoler les rampants d'un comble qu'on n'habitera jamais "
              "revient à chauffer un volume inutile, pour un prix bien supérieur.",
              "Si la couverture doit de toute façon être refaite, la question se repose : isoler "
              "par l'extérieur devient possible, et c'est le seul moment où cela se fait sans "
              "surcoût de dépose.",
              "Nous regardons systématiquement les combles quand nous intervenons sur un toit. "
              "C'est souvent là que se trouve le gisement d'économie le plus simple."]),
        ],
        faq=[("Peut-on isoler soi-même des combles perdus ?",
              "Le déroulage est techniquement accessible. Les points délicats sont la trappe, les "
              "spots, la ventilation en bas de pente et le pare-vapeur — et ce sont eux qui "
              "décident du résultat. Le soufflage demande une machine."),
             ("Faut-il retirer l'ancien isolant ?",
              "Pas s'il est sec, sain et non tassé : on surisole par-dessus. S'il a été mouillé, "
              "s'il est en vrac tassé ou s'il abrite des rongeurs, on retire."),
             ("L'isolation peut-elle abîmer la charpente ?",
              "Indirectement, oui, si elle bloque la ventilation ou si la vapeur d'eau s'y condense. "
              "Une charpente saine et ventilée ne craint rien ; une charpente enfermée dans un "
              "isolant humide travaille."),
             ("Combien de temps ça prend ?",
              "Une journée pour une maison courante en soufflage, un peu plus en déroulage. C'est "
              "le chantier le plus court et le plus rentable du bâtiment.")],
        cta=("Faire chiffrer l'isolation", "isolation-toiture"),
    ),
]

# Seconde image de chaque prestation, pour couper le mur de texte a mi-page.
# Jamais celle du hero, et toujours le sujet de la page.
BANDS = {
 "renovation-toiture":  ("apres-refection-toiture-longere-tuile-neuve.webp",
   "Longère entièrement recouverte en tuile neuve",
   "Une réfection menée jusqu'au bout",
   "Dépose complète, écran de sous-toiture, liteaunage, couverture neuve. Le toit repart pour quarante ans."),
 "zinguerie-gouttieres": ("tuile-neuve-rive-zinguee-detail.webp",
   "Détail d'une rive zinguée sur une couverture neuve",
   "C'est la zinguerie qui décide où part l'eau",
   "Une descente bouchée ou un solin fendu suffit à abîmer un mur en deux hivers."),
 "demoussage-toiture":  ("tuiles-mousse-vegetation.webp",
   "Tuiles envahies de mousse et de végétation",
   "La mousse retient l'eau contre la tuile",
   "Elle gèle, elle fait éclater la terre cuite, et le problème finit dans la charpente."),
 "depannage-toiture":   ("ciel-orage-sur-toitures.webp",
   "Ciel d'orage au-dessus des toitures",
   "Une toiture qui prend l'eau n'attend pas lundi",
   "Nous mettons d'abord hors d'eau, puis nous revenons faire la réparation au calme."),
 "charpente":           ("charpente-auvent-chene-maison-pierre.webp",
   "Charpente d'auvent en chêne sur une maison en pierre",
   "La charpente porte tout le reste",
   "On ne la voit qu'une fois la couverture déposée, et c'est là que se joue une bonne partie du budget."),
 "isolation-toiture":   ("renovation-toiture-charpente-liteaux-neufs.webp",
   "Écran de sous-toiture et liteaux neufs posés sur une charpente",
   "Le bon moment pour isoler, c'est pendant la réfection",
   "L'échafaudage est déjà là, la couverture est déposée : l'isolation ne coûte jamais aussi peu."),
 "recherche-de-fuite":  ("toiture-alteree-lichens.webp",
   "Toiture ancienne altérée par les lichens",
   "La tache au plafond n'est presque jamais sous la fuite",
   "L'eau circule sur la charpente avant de tomber. On cherche le point d'entrée, pas le point d'arrivée."),
 "fenetre-de-toit":     ("toiture-tuile-brune-fenetre-de-toit.webp",
   "Fenêtre de toit posée dans une couverture en tuile brune",
   "Une fenêtre de toit, c'est d'abord un raccord",
   "Le châssis se pose vite. Ce qui tient dans le temps, c'est le raccord à la couverture."),
 "bardage":             ("corps-de-ferme-pierre-depose-couverture.webp",
   "Pignon d'un corps de ferme en pierre pendant la dépose de la couverture",
   "Le pignon prend la pluie avant le reste",
   "Un bardage bien posé protège le mur et se raccorde proprement à la couverture."),
}

# Bandeaux des pages communes : quatre vues du secteur, en rotation, pour ne
# pas reservir la photo deja utilisee en haut de la page.
BANDS_VILLE = [
 ("toitures-tuile-lucarnes.webp", "Toitures en tuile et lucarnes alignées"),
 ("toits-village-normand-aides.webp", "Toits d'ardoise et cheminées de brique d'un bourg normand"),
 ("apres-refection-toiture-longere-tuile-neuve.webp", "Longère recouverte en tuile neuve"),
 ("couvreur-nonancourt-longere-tuile-neuve.webp", "Longère avec une couverture neuve en tuile rouge"),
]

ETAPES = [
    ("Vous appelez", "Nous prenons les premiers éléments au téléphone et nous vous donnons un ordre "
                     "de grandeur avant même de nous déplacer."),
    ("Nous venons voir", "Nous montons sur le toit si c'est nécessaire. C'est la seule façon de "
                         "chiffrer juste, et c'est gratuit."),
    ("Vous recevez le devis", "Détaillé ligne par ligne, sans poste flou. Vous savez ce que vous "
                              "payez et ce que vous ne payez pas."),
    ("Nous fixons une date", "Et nous la tenons. Si la météo nous décale, vous êtes prévenu, pas "
                             "mis devant le fait accompli."),
    ("Le chantier est rendu net", "Gravats évacués, abords balayés. Nous faisons le tour avec vous "
                                  "avant de partir."),
]

# ──────────────────────────────────────────────────────────── gabarits ─────
def av(rel):
    """Empreinte de contenu pour la feuille de style et le script.

    Le cache de Cloudflare garde le CSS et le JS une semaine. Sans empreinte,
    un visiteur revenu apres un deploiement recoit le NOUVEAU html avec son
    ANCIEN css : le 08/09/2026 le hero s'est retrouve sans style, image dans
    le flux et texte pousse hors de l'ecran. Une nouvelle version doit donner
    une nouvelle URL.
    """
    import hashlib
    full = os.path.join(ROOT, rel)
    try:
        return rel + "?v=" + hashlib.sha1(open(full, "rb").read()).hexdigest()[:10]
    except OSError:
        return rel


def version_assets():
    """Applique l'empreinte a toutes les pages, index.html compris."""
    import glob as _glob
    vers = {r: av(r) for r in ("assets/style.css", "assets/fonts.css", "assets/app.js")}
    pages = ([os.path.join(ROOT, "index.html"), os.path.join(ROOT, "404.html"),
              os.path.join(ROOT, "mentions-legales.html")]
             + _glob.glob(os.path.join(ROOT, "*", "index.html"))
             + _glob.glob(os.path.join(ROOT, "*", "*", "index.html")))
    n = 0
    for page in pages:
        if not os.path.exists(page):
            continue
        html = open(page, encoding="utf-8").read()
        out = html
        for rel, versioned in vers.items():
            # on repart toujours de l'URL nue : sinon les empreintes s'empilent
            out = re.sub(re.escape(rel) + r'\?v=[0-9a-f]+', rel, out)
            out = out.replace(rel, versioned)
        if out != html:
            open(page, "w", encoding="utf-8").write(out)
            n += 1
    print("empreintes posees sur %d pages" % n)


def head(title, desc, canon, jsonld, ogimg="couvreur-nonancourt-longere-tuile-neuve.webp"):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{DOMAIN}/{canon}">
<meta name="theme-color" content="#F4F1EA">
<meta name="color-scheme" content="only light">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{DOMAIN}/{canon}">
<meta property="og:image" content="{DOMAIN}/assets/img/{ogimg}">
<meta property="og:image:width" content="1600">
<meta property="og:image:alt" content="{title}">
<meta property="og:site_name" content="WM Couverture">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{DOMAIN}/assets/img/{ogimg}">
<link rel="preload" href="{PRE}assets/fonts/archivo-normal-800-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{PRE}assets/fonts/inter-tight-normal-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{PRE}assets/fonts.css">
<link rel="stylesheet" href="{PRE}assets/style.css">
<link rel="icon" href="{PRE}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{PRE}assets/favicon.svg">
<script async src="https://www.googletagmanager.com/gtag/js?id={ADS_GTAG}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('consent', 'default', {{
  ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
  analytics_storage: 'denied', wait_for_update: 500
}});
gtag('set', 'url_passthrough', true);
gtag('set', 'ads_data_redaction', true);
gtag('js', new Date());
gtag('config', '{ADS_GTAG}');
// app.js lit ces etiquettes : build.py reste le seul endroit qui les definit.
window.WM_CONV = {{devis:'{ADS_GTAG}/{ADS_CONV_DEVIS}', appel:'{ADS_GTAG}/{ADS_CONV_APPEL}'}};
</script>
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<a class="skip" href="#main\">Aller au contenu</a>
<div class="progress" aria-hidden="true"><span></span></div>
"""


def nav(active=""):
    def li(href, label, slug):
        cur = ' aria-current="page"' if slug == active else ''
        return f'<a href="{href}"{cur}>{label}</a>'
    services = "".join(
        ('<a href="' + PRE + s["slug"] + '/"' + (' aria-current="page"' if s["slug"] == active else "") + '>' + s["nav"] + '</a>')
        for s in SERVICES)
    villes = "".join(
        ('<a href="' + PRE + v["slug"] + '/"' + (' aria-current="page"' if v["slug"] == active else "") + '>' + v["ville"] + '</a>')
        for v in VILLES)
    guides_menu = "".join(
        ('<a href="' + PRE + "guides/" + g["slug"] + '/"' + (' aria-current="page"' if g["slug"] == active else "") + '>' + g["nav"] + '</a>')
        for g in GUIDES) + f'<a href="{PRE}guides/">Tous les guides</a>' 
    return f"""<header class="nav nav--solid" id="nav">
  <div class="nav__in">
    <a class="brand" href="{PRE}" aria-label="WM Couverture, accueil">{MARK}
      <span class="brand__txt"><strong>WM</strong> Couverture</span></a>
    <nav class="nav__links" aria-label="Navigation principale">
      <div class="drop">
        <button class="drop__btn" aria-expanded="false" aria-controls="dropS">Prestations
          <svg viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5 6 6.5l5-5"/></svg></button>
        <div class="drop__menu" id="dropS">{services}</div>
      </div>
      <div class="drop">
        <button class="drop__btn" aria-expanded="false" aria-controls="dropV">Communes
          <svg viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5 6 6.5l5-5"/></svg></button>
        <div class="drop__menu" id="dropV">{villes}</div>
      </div>
      <div class="drop">
        <button class="drop__btn" aria-expanded="false" aria-controls="dropG">Guides
          <svg viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5 6 6.5l5-5"/></svg></button>
        <div class="drop__menu" id="dropG">{guides_menu}</div>
      </div>
      {li(f"{PRE}#chantiers", "Chantiers", "")}
    </nav>
    <div class="nav__cta">
      <a class="tel-link" href="tel:{TEL_HREF}" data-track="call"><span class="dot" aria-hidden="true"></span>{TEL_TXT}</a>
      <a class="btn btn--dark btn--sm" href="#devis">Devis gratuit</a>
      <button class="burger" id="burger" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="drawer">
        <span></span><span></span></button>
    </div>
  </div>
</header>
<div class="drawer" id="drawer" hidden>
  <p class="drawer__t">Prestations</p>
  {"".join(f'<a href="{PRE}{s["slug"]}/">{s["nav"]}</a>' for s in SERVICES)}
  <p class="drawer__t">Communes</p>
  {"".join(f'<a href="{PRE}{v["slug"]}/">{v["ville"]}</a>' for v in VILLES)}
  <p class="drawer__t">Guides</p>
  {"".join(f'<a href="{PRE}guides/{g["slug"]}/">{g["nav"]}</a>' for g in GUIDES)}
  <a class="drawer__tel" href="tel:{TEL_HREF}" data-track="call">{TEL_TXT}</a>
</div>
"""


def crumb(label, extra=None):
    mid = ""
    if extra:
        mid = (f'<a href="{PRE}{extra[1]}">{extra[0]}</a>'
               '<span aria-hidden="true">/</span>')
    return f"""<nav class="crumb wrap" aria-label="Fil d'Ariane">
  <a href="{PRE}">Accueil</a><span aria-hidden="true">/</span>{mid}<span>{label}</span>
</nav>"""


def page_hero(eyebrow, h1a, h1b, lead, img, alt, urgent=False):
    """urgent : sur les pages ou le visiteur a un toit ouvert, le telephone
    passe en action principale. C'est l'appel qui convertit, pas le formulaire."""
    tel = (f'<a class="btn btn--dark" href="tel:{TEL_HREF}" data-track="call">{PHONE}{TEL_TXT}</a>'
           if urgent else
           f'<a class="btn btn--ghost" href="tel:{TEL_HREF}" data-track="call">{PHONE}{TEL_TXT}</a>')
    devis = ('<a class="btn btn--ghost" href="#devis">Demander un devis</a>' if urgent else
             '<a class="btn btn--dark" href="#devis">Demander mon devis gratuit</a>')
    cta = (tel + devis) if urgent else (devis + tel)
    return f"""<section class="phero">
  <div class="wrap phero__grid">
    <div>
      <p class="eyebrow reveal">{eyebrow}</p>
      <h1 class="reveal" data-d="1">{h1a}<br>{h1b}</h1>
      <p class="phero__lead reveal" data-d="2">{lead}</p>
      {hero_note()}
      <div class="phero__cta reveal" data-d="3">{cta}</div>
      <!-- Un clic paye atterrissait ici sans une seule preuve : ni les annees,
           ni les avis, ni les horaires. Meme bloc que la page d'accueil. -->
      <ul class="hero__trust phero__trust reveal" data-d="4">
        <li><b data-count="14">14</b> ans d'expérience</li>
        <li><b>7</b>j/7, de 8 h à 21 h</li>
      </ul>
    </div>
    <figure class="frame phero__img reveal" data-d="2">
      <img src="{PRE}assets/img/{img}" alt="{alt}" width="1600" height="1200" fetchpriority="high" decoding="async">
    </figure>
  </div>
</section>"""


def facts_row():
    """Reassurance juste sous le hero : la page d'accueil l'avait, les pages
    d'atterrissage des annonces non."""
    return """<section class="facts facts--slim">
  <div class="wrap">
    <ul class="facts__row">
      <li class="reveal"><b>{AVIS_TOTAL} avis, {note_fr()} sur 5</b><span>aucun avis en dessous de cinq étoiles</span></li>
      <li class="reveal"><b>Devis gratuit</b><span>nous venons mesurer et nous chiffrons</span></li>
      <li class="reveal" data-d="1"><b>Paiement en plusieurs fois</b><span>sur les gros chantiers</span></li>
      <li class="reveal" data-d="2"><b>7 j/7, 8 h à 21 h</b><span>et la nuit en cas de fuite</span></li>
    </ul>
  </div>
</section>"""


def mat_block(title, items, cls="deep"):
    rows = "".join(
        f'<div class="reveal" data-d="{min(i,3)}"><dt>{t}</dt><dd>{d}</dd></div>'
        for i, (t, d) in enumerate(items))
    return f"""<section class="{cls}">
  <div class="wrap deep__grid">
    <h2 class="reveal">{title}</h2>
    <dl class="mat">{rows}</dl>
  </div>
</section>"""


def prix_block(title, items, note):
    def fmt(x):
        while "**" in x:
            x = x.replace("**", "<b>", 1).replace("**", "</b>", 1)
        return x
    li = "".join(f'<li class="reveal" data-d="{min(i,3)}">{fmt(x)}</li>'
                 for i, x in enumerate(items))
    return f"""<section class="prix">
  <div class="wrap prix__grid">
    <div>
      <h2 class="reveal">{title}</h2>
      <p class="prix__note reveal" data-d="1">{note}</p>
      <a class="btn btn--dark reveal" data-d="2" href="#devis">Demander mon devis gratuit</a>
    </div>
    <ul class="prix__list">{li}</ul>
  </div>
</section>"""


def specs(items, cls="specs"):
    rows = "".join(f"<div><dt>{t}</dt><dd>{d}</dd></div>" for t, d in items)
    return f'<dl class="{cls} reveal">{rows}</dl>'


# Photo de carte par prestation. Depannage et recherche de fuite partageaient
# la meme image : cote a cote dans une grille, ca se voyait.
CARTE_IMG = {
 "renovation-toiture":   "renovation-toiture-charpente-liteaux-neufs.webp",
 "zinguerie-gouttieres": "zinguerie-souche-zinc-toiture.webp",
 "demoussage-toiture":   "demoussage-toiture-mousse-echafaudage.webp",
 "depannage-toiture":    "depannage-toiture-depose-tuiles-urgence.webp",
 "charpente":            "charpente-ancienne-sous-toiture.webp",
 "isolation-toiture":    "combles-avant-isolation-sous-rampants.webp",
 "recherche-de-fuite":   "toiture-alteree-lichens.webp",
 "fenetre-de-toit":      "pose-fenetre-de-toit-velux.webp",
 "bardage":              "rive-de-toiture-debord-termine.webp",
}


def services_grid():
    """Les neuf prestations en acces direct.

    L'accueil ne montrait que trois regroupements editoriaux : quelqu'un qui
    cherchait « recherche de fuite » ne la voyait nulle part, alors que la page
    existe. Genere depuis SERVICES pour ne plus jamais deriver.
    """
    cartes = []
    for i, x in enumerate(SERVICES):
        img = CARTE_IMG.get(x["slug"], x["hero"])
        cartes.append(
            f'<a class="scard reveal" data-d="{min(i % 3, 3)}" href="{PRE}{x["slug"]}/">'
            f'<img class="scard__img" src="{PRE}assets/img/{img}" alt="" '
            f'width="1600" height="1200" loading="lazy" decoding="async">'
            f'<span class="scard__in">'
            f'<span class="scard__t">{x["nav"]}</span>'
            f'<span class="scard__p">{x["pitch"]}</span>'
            f'<span class="scard__go">{ARROW}</span>'
            f'</span></a>')
    return f"""<section class="services" id="prestations">
  <div class="wrap">
    <header class="sec-head sec-head--center reveal">
      <p class="kicker"><span class="dot" aria-hidden="true"></span> Nos prestations</p>
      <h2>Neuf métiers, <em>un seul</em> toit</h2>
      <p>Du faîtage à la gouttière, en neuf comme en rénovation.
        Choisissez ce qui vous concerne, nous détaillons tout sur chaque page.</p>
    </header>
    <div class="scards">{"".join(cartes)}</div>
  </div>
</section>"""


def band(img, alt, kicker, phrase):
    """Bandeau photo pleine largeur qui coupe le mur de texte au milieu des pages
    interieures, et redonne un point d'appel a mi-parcours."""
    return f"""<section class="band reveal">
  <img class="band__bg" src="{PRE}assets/img/{img}" alt="{alt}"
       width="1680" height="720" loading="lazy" decoding="async">
  <div class="wrap band__in">
    <p class="band__k">{kicker}</p>
    <p class="band__p">{phrase}</p>
    <a class="btn btn--ghost btn--lg" href="tel:{TEL_HREF}" data-track="call">{PHONE}{TEL_TXT}</a>
  </div>
</section>"""


def slugify(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", re.sub(r"<[^>]+>", "", t))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")[:48]


def sommaire(sections):
    """Sur un guide de 6 000 px, le lecteur arrive de Google sans savoir ce que la
    page couvre. Le sommaire le lui dit et lui donne des points d'entree."""
    li = "".join('<li><a href="#%s">%s</a></li>' % (slugify(t), re.sub(r"<[^>]+>", "", t))
                 for t, _ in sections)
    return f"""<nav class="toc reveal" data-d="3" aria-label="Sommaire du guide">
  <p class="toc__t">Au sommaire</p>
  <ol class="toc__l">{li}</ol>
</nav>"""


def pullq(txt):
    """Une phrase mise au serif, en grand, pour casser une fois le rythme
    titre-a-gauche / texte-a-droite qui tient toute la page."""
    return f'<aside class="pullq reveal"><p>{txt}</p></aside>'


def etapes():
    li = "".join(
        f'<li class="reveal" data-d="{min(i,4)}"><span class="steps__n">{i+1:02d}</span>'
        f'<b>{t}</b><span class="steps__d">{d}</span></li>'
        for i, (t, d) in enumerate(ETAPES))
    return f"""<section class="steps">
  <div class="wrap">
    <h2 class="reveal">Comment <em>ça se passe</em></h2>
    <ol class="steps__list">{li}</ol>
  </div>
</section>"""


# ── rendu des avis facon Google ────────────────────────────────────────────
# Le visiteur doit reconnaitre d'un coup d'oeil que ce sont de vrais avis
# Google et pas des temoignages ecrits par l'agence. Trois signaux suffisent :
# le G quadricolore, les etoiles ambre de Google (#FBBC04) et le lien vers la
# fiche. Les conditions d'utilisation de Google imposent de toute facon
# l'attribution et le lien, donc ces signaux ne sont pas decoratifs.

G_LOGO = (
 '<svg class="g-logo" viewBox="0 0 48 48" aria-hidden="true">'
 '<path fill="#4285F4" d="M45.12 24.5c0-1.56-.14-3.06-.4-4.5H24v8.51h11.84c-.51 2.75-2.06 '
 '5.08-4.39 6.64v5.52h7.11c4.16-3.83 6.56-9.47 6.56-16.17z"/>'
 '<path fill="#34A853" d="M24 46c5.94 0 10.92-1.97 14.56-5.33l-7.11-5.52c-1.97 1.32-4.49 '
 '2.1-7.45 2.1-5.73 0-10.58-3.87-12.31-9.07H4.34v5.7C7.96 41.07 15.4 46 24 46z"/>'
 '<path fill="#FBBC05" d="M11.69 28.18C11.25 26.86 11 25.45 11 24s.25-2.86.69-4.18v-5.7H4.34'
 'C2.85 17.09 2 20.45 2 24s.85 6.91 2.34 9.88l7.35-5.7z"/>'
 '<path fill="#EA4335" d="M24 10.75c3.23 0 6.13 1.11 8.41 3.29l6.31-6.31C34.91 4.18 29.93 2 '
 '24 2 15.4 2 7.96 6.93 4.34 14.12l7.35 5.7c1.73-5.2 6.58-9.07 12.31-9.07z"/></svg>')

_ETOILE = ('<svg viewBox="0 0 20 19" aria-hidden="true"><path d="M10 0l2.9 6.2 6.6.9-4.8 4.8 '
           '1.2 6.9L10 15.5 4.1 18.8l1.2-6.9L.5 7.1l6.6-.9z"/></svg>')


def etoiles(note=5.0, taille="s"):
    """Cinq etoiles avec remplissage partiel. Le pourcentage est calcule ici et
    pas en CSS : une note de 4,6 doit remplir 92 % et non arrondir a 5."""
    pct = max(0.0, min(1.0, float(note) / 5.0)) * 100
    return (f'<span class="etoiles etoiles--{taille}" aria-hidden="true">'
            f'<span class="etoiles__vide">{_ETOILE * 5}</span>'
            f'<span class="etoiles__plein" style="width:{pct:.4g}%">{_ETOILE * 5}</span>'
            '</span>')


def avis_carte(a, i=0):
    """Une carte d'avis. La date est omise si on ne l'a pas : mieux vaut pas de
    date qu'une date inventee."""
    quand = f'<span class="gav__quand">{a["quand"]}</span>' if a.get("quand") else ""
    return (
     f'<figure class="gav reveal" data-d="{min(i, 4)}">'
     f'<header class="gav__h">'
     f'<span class="gav__pastille" aria-hidden="true">{a["initiale"]}</span>'
     f'<span class="gav__qui"><b>{a["auteur"]}</b>{quand}</span>'
     f'</header>'
     f'{etoiles(a.get("note", 5))}'
     f'<blockquote>{a["texte"]}</blockquote>'
     '</figure>')


def avis_bandeau(centre=False):
    """La note globale. C'est la seule partie qui doit absolument etre juste :
    elle vient d'avis.json, donc de l'API, jamais d'une saisie."""
    cls = " gnote--centre" if centre else ""
    return (
     f'<div class="gnote{cls} reveal">{G_LOGO}'
     f'<span class="gnote__chiffre">{note_fr()}</span>'
     f'{etoiles(AVIS_NOTE, "m")}'
     f'<span class="gnote__total">sur <b>{AVIS_TOTAL} avis</b> Google</span>'
     f'<a class="gnote__lien" href="{AVIS_FICHE}" target="_blank" rel="noopener nofollow">'
     f'Les lire sur Google{ARROW}</a></div>')


def bloc_avis(n=5, centre=True):
    cartes = "".join(avis_carte(a, i) for i, a in enumerate(AVIS[:n]))
    return f"""<section class="avis" id="avis">
  <div class="wrap">
    <header class="avis__head avis__head--center">
      <h2 class="reveal">Ce que disent <em>les clients</em></h2>
      {avis_bandeau(centre)}
    </header>
    <div class="gav__grid">{cartes}</div>
  </div>
</section>"""


def hero_note(sombre=False):
    """La note Google, placee juste avant les boutons d'appel a l'action.

    Elle etait en bas du hero, troisieme element d'une liste de trois, a poids
    egal avec les horaires. C'est pourtant la seule preuve du lot qui ne vienne
    pas de nous : 81 personnes l'ont ecrite, pas l'agence. Elle passe donc au
    moment ou le visiteur decide, juste avant « Devis gratuit ».

    Volontairement sans lien : sur la page ou atterrit la publicite, on
    n'ouvre pas une porte de sortie vers Google au moment de la decision. Le
    lien vers la fiche est plus bas, dans la section des avis."""
    cls = " hnote--sombre" if sombre else ""
    return (
     f'<p class="hnote{cls} reveal" data-d="2">{G_LOGO}'
     f'<span class="hnote__chiffre">{note_fr()}</span>'
     f'{etoiles(AVIS_NOTE, "m")}'
     f'<span class="hnote__txt"><b>{AVIS_TOTAL} avis</b> Google</span></p>')


def avis_vedette():
    """L'avis mis en exergue sur l'accueil. On prend le plus court qui reste
    substantiel : la citation en grand doit tenir sur trois lignes, et un avis
    de trois cents signes casse la mise en page. Choix automatique, donc il
    survit au remplacement des avis par les vrais."""
    candidats = [a for a in AVIS if 60 <= len(a["texte"]) <= 220] or AVIS
    return min(candidats, key=lambda a: len(a["texte"]))


def citation_html(a):
    """Met la derniere phrase en valeur. On ne reformule rien : on choisit
    seulement ou couper, sinon on ferait dire a un client ce qu'il n'a pas
    ecrit."""
    import re as _re
    phrases = [x.strip() for x in _re.split(r'(?<=[.!?])\s+', a["texte"].strip()) if x.strip()]
    if len(phrases) < 2:
        return a["texte"]
    return " ".join(phrases[:-1]) + f' <em>{phrases[-1]}</em>'


def avis_pair(a, b):
    """Version courte pour les pages internes : deux avis, meme habillage."""
    return f"""<section class="avis">
  <div class="wrap">
    <header class="avis__head avis__head--center">
      <h2 class="reveal">Ce que disent <em>les clients</em></h2>
      {avis_bandeau(True)}
    </header>
    <div class="gav__grid gav__grid--pair">{avis_carte(a, 0)}{avis_carte(b, 1)}</div>
  </div>
</section>"""


def maillage(current_slug):
    s = "".join(f'<li><a href="{PRE}{x["slug"]}/">{x["nav"]}<span>{ARROW}</span></a></li>'
                for x in SERVICES if x["slug"] != current_slug)
    v = "".join(f'<li><a href="{PRE}{x["slug"]}/">{x["ville"]}<span>{ARROW}</span></a></li>'
                for x in VILLES if x["slug"] != current_slug)
    return f"""<section class="mesh">
  <div class="wrap mesh__grid">
    <div><h2 class="reveal">Nos autres <em>prestations</em></h2><ul class="mesh__list reveal" data-d="1">{s}</ul></div>
    <div><h2 class="reveal">Nous intervenons <em>aussi à</em></h2><ul class="mesh__list reveal" data-d="1">{v}</ul></div>
  </div>
</section>"""


def faq_block(items):
    d = "".join(
        f'<details class="reveal" data-d="{min(i,4)}"><summary>{q}</summary><p>{a}</p></details>'
        for i, (q, a) in enumerate(items))
    return f"""<section class="faq">
  <div class="wrap faq__grid">
    <h2 class="reveal">Questions <em>fréquentes</em></h2>
    <div class="faq__list">{d}</div>
  </div>
</section>"""


def devis(titre, sous):
    return f"""<section class="devis" id="devis">
  <div class="wrap devis__grid">
    <div class="devis__l">
      <p class="eyebrow reveal">Devis gratuit</p>
      <h2 class="reveal" data-d="1">{titre}</h2>
      <p class="reveal" data-d="2">{sous}</p>
      <ul class="devis__coord">
        <li class="reveal"><span>Téléphone</span><a href="tel:{TEL_HREF}" data-track="call">{TEL_TXT}</a></li>
        <li class="reveal" data-d="1"><span>Atelier</span><a href="{MAPS}" target="_blank" rel="noopener">{ADDR}</a></li>
        <li class="reveal" data-d="2"><span>Horaires</span><b>Tous les jours, 8 h à 21 h<br>Dépannage 24 h/24</b></li>
      </ul>
    </div>
    <form class="form reveal" id="devisForm" method="POST" action="https://api.web3forms.com/submit" novalidate>
      <input type="hidden" name="access_key" value="{W3F_KEY}">
      <input type="hidden" name="subject" value="Nouvelle demande de devis · site WM Couverture">
      <input type="hidden" name="from_name" value="Site WM Couverture">
      <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
      <input type="hidden" name="page" id="f_page" value="">
      <div class="f-row">
        <div class="f"><input id="f_nom" name="nom" type="text" required autocomplete="name" placeholder=" "><label for="f_nom">Nom et prénom</label></div>
        <div class="f"><input id="f_tel" name="telephone" type="tel" required autocomplete="tel" inputmode="tel" placeholder=" "><label for="f_tel">Téléphone</label></div>
      </div>
      <div class="f-row">
        <div class="f"><input id="f_mail" name="email" type="email" autocomplete="email" placeholder=" "><label for="f_mail">E-mail (facultatif)</label></div>
        <div class="f"><input id="f_ville" name="ville" type="text" required placeholder=" "><label for="f_ville">Commune</label></div>
      </div>
      <fieldset class="f-chips">
        <legend>Ce dont vous avez besoin</legend>
        <label><input type="checkbox" name="besoin" value="Rénovation de toiture"><span>Rénovation</span></label>
        <label><input type="checkbox" name="besoin" value="Zinguerie / gouttières"><span>Zinguerie</span></label>
        <label><input type="checkbox" name="besoin" value="Démoussage"><span>Démoussage</span></label>
        <label><input type="checkbox" name="besoin" value="Urgence / fuite"><span>Urgence</span></label>
      </fieldset>
      <div class="f f--area"><textarea id="f_msg" name="message" rows="3" placeholder=" "></textarea><label for="f_msg">Décrivez en deux lignes (facultatif)</label></div>
      <button class="btn btn--dark btn--full" type="submit"><span class="btn__lbl">Envoyer ma demande</span><span class="btn__spin" aria-hidden="true"></span></button>
      <p class="form__note">Réponse le jour même en général. Vos coordonnées servent uniquement à vous rappeler.</p>
      <p class="form__msg" id="formMsg" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>"""


def foot():
    s = "".join(f'<a href="{PRE}{x["slug"]}/">{x["nav"]}</a>' for x in SERVICES)
    v = "".join(f'<a href="{PRE}{x["slug"]}/">{x["ville"]}</a>' for x in VILLES)
    g = "".join(f'<a href="{PRE}guides/{x["slug"]}/">{x["nav"]}</a>' for x in GUIDES)
    return f"""<footer class="foot">
  <div class="wrap foot__grid">
    <div class="foot__brand">
      <a class="brand brand--light" href="{PRE}">{MARK}<span class="brand__txt"><strong>WM</strong> Couverture</span></a>
      <p>Entreprise familiale de couverture, de père en fils.<br>Nonancourt, Eure, Normandie.</p>
      <div class="foot__cta">
        <a class="btn btn--brass" href="#devis">Devis gratuit</a>
        <a class="link-arrow link-arrow--light" href="tel:{TEL_HREF}" data-track="call">Nous appeler {ARROW}</a>
      </div>
    </div>
    <div class="foot__col"><h3>Prestations</h3>{s}</div>
    <div class="foot__col"><h3>Communes</h3>{v}</div>
    <div class="foot__col"><h3>Guides</h3>{g}</div>
    <div class="foot__col">
      <h3>Contact</h3>
      <a href="tel:{TEL_HREF}" data-track="call">{TEL_TXT}</a>
      <a href="{MAPS}" target="_blank" rel="noopener">577A les maisons rouges<br>27320 Nonancourt</a>
      <span>Tous les jours 8 h à 21 h<br>Dépannage 24 h/24</span>
    </div>
  </div>
  <div class="wrap foot__bar">
    <p>© <span id="year">2026</span> WM Couverture. Tous droits réservés.</p>
    <p><a href="{PRE}plan-du-site/">Plan du site</a> <span aria-hidden="true">·</span> <a href="{PRE}mentions-legales.html">Mentions légales</a> <span aria-hidden="true">·</span> <a href="{PRE}politique-de-confidentialite.html">Confidentialité</a></p>
  </div>
</footer>
<div class="callbar" id="callbar">
  <a class="callbar__tel" href="tel:{TEL_HREF}" data-track="call">{PHONE.replace(' class="ico"','')}Appeler</a>
  <a class="callbar__devis" href="#devis">Devis gratuit</a>
</div>
<script src="{PRE}assets/app.js" defer></script>
</body>
</html>"""


def ld_business():
    """Fiche LocalBusiness complete, reutilisee par @id sur toutes les pages."""
    villes = [v["ville"] for v in VILLES] + ZONE_PLUS
    area = ",".join('{"@type":"City","name":%s}' % jstr(x) for x in villes)
    offers = ",".join(
        '{"@type":"Offer","itemOffered":{"@type":"Service","name":%s,"url":"%s/%s/"}}'
        % (jstr(x["nav"]), DOMAIN, x["slug"]) for x in SERVICES)
    same = (',"sameAs":[%s]' % ",".join(jstr(u) for u in SAMEAS)) if SAMEAS else ""
    imgs = ",".join(f'"{DOMAIN}/assets/img/{f}"' for f in
                    ("couvreur-nonancourt-longere-tuile-neuve.webp", "couvreur-nonancourt-pose-ecran-sous-toiture.webp", "tuile-neuve-rive-zinguee-detail.webp"))
    return ('{"@type":["RoofingContractor","HomeAndConstructionBusiness"],'
            '"@id":"%s/#business","name":"WM Couverture",'
            '"alternateName":"WM Couverture Nonancourt",'
            '"description":"Entreprise familiale de couverture a Nonancourt (Eure) : renovation '
            'de toiture en tuile, ardoise et acier, charpente, zinguerie, gouttieres, isolation, '
            'nettoyage et demoussage. Depannage 24 h/24.",'
            '"telephone":"+33624592677","url":"%s/","image":[%s],"priceRange":"%s",'
            '"currenciesAccepted":"EUR","paymentAccepted":"Especes, cheque, virement",'
            '"foundingDate":"2012","knowsLanguage":"fr-FR"%s,'
            '"address":{"@type":"PostalAddress","streetAddress":"577A les maisons rouges",'
            '"postalCode":"27320","addressLocality":"Nonancourt","addressRegion":"Normandie",'
            '"addressCountry":"FR"},'
            '"geo":{"@type":"GeoCoordinates","latitude":%s,"longitude":%s},'
            '"hasMap":"%s",'
            '"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":'
            '["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],'
            '"opens":"08:00","closes":"21:00"}],'
            '"areaServed":[%s],'
            '"hasOfferCatalog":{"@type":"OfferCatalog","name":"Prestations de couverture",'
            '"itemListElement":[%s]}}'
            % (DOMAIN, DOMAIN, imgs, PRICE, same, GEO_LAT, GEO_LON, MAPS, area, offers))


# ────────────────────────────────────────────────────────────── rendus ─────
def render_service(s):
    canon = s["slug"] + "/"
    faq_ld = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (jstr(q), jstr(a)) for q, a in s["faq"])
    ld = ('{"@context":"https://schema.org","@graph":[' + ld_business() + ','
          '{"@type":"Service","name":%s,"serviceType":%s,"provider":{"@id":"%s/#business"},'
          '"areaServed":[%s],"url":"%s/%s"},'
          '{"@type":"FAQPage","mainEntity":[%s]},'
          '{"@type":"BreadcrumbList","itemListElement":['
          '{"@type":"ListItem","position":1,"name":"Accueil","item":"%s/"},'
          '{"@type":"ListItem","position":2,"name":%s}]}]}'
          % (jstr(s["nav"]), jstr(s["nav"]), DOMAIN,
             ",".join('{"@type":"City","name":%s}' % jstr(v["ville"]) for v in VILLES),
             DOMAIN, canon, faq_ld, DOMAIN, jstr(s["nav"])))

    alerte = "".join(f"<li>{x}</li>" for x in s["alerte"])
    return "".join([
        head(s["title"], s["desc"], canon, ld, s["hero"]),
        nav(s["slug"]),
        '<main id="main">',
        crumb(s["nav"]),
        page_hero("Prestation", s["h1"][0], s["h1"][1], s["lead"], s["hero"], s["heroalt"],
                  urgent=s["slug"] in ("depannage-toiture", "recherche-de-fuite")),
        facts_row(),
        f"""<section class="detail">
  <div class="wrap detail__grid">
    <div><h2 class="reveal">Ce que <em>nous faisons</em></h2>{specs(s["specs"], "specs specs--wide")}</div>
    <div class="detail__alert">
      <h2 class="reveal">{s["alerte_t"]}</h2>
      <ul class="ticks reveal" data-d="1">{alerte}</ul>
      <a class="link-arrow reveal" data-d="2" href="#devis">Faire chiffrer{ARROW}</a>
    </div>
  </div>
</section>""",
        (band(*BANDS[s["slug"]]) if s["slug"] in BANDS else ""),
        mat_block(s["mat_t"], s["mat"]),
        prix_block(s["prix_t"], s["prix"], s["budget"]),
        etapes(),
        avis_pair(AVIS[0], AVIS[2]),
        faq_block(s["faq"]),
        maillage(s["slug"]),
        devis("Dites-nous ce qu'il <em>se passe</em> là-haut",
              "Décrivez la situation en deux lignes, nous rappelons pour caler une visite."),
        "</main>",
        foot(),
    ])


# ── reperes locaux verifies ────────────────────────────────────────────────
# Nos pages de commune n'etaient uniques qu'a 36 % : 496 mots sur 802 etaient
# identiques d'une commune a l'autre. C'est exactement le defaut des pages
# generiques de nos concurrents, et le seuil attendu pour une page de lieu
# est 60 %. Ce bloc ajoute des faits REELS et differents pour chaque commune,
# jamais du remplissage : distance mesuree depuis l'atelier, population de
# l'INSEE, et l'administration qui traite reellement le dossier.
#
# Source : API Geo du gouvernement (geo.api.gouv.fr), relevee le 18/09/2026.
# Distances a vol d'oiseau converties en distance routiere par le facteur
# 1,3 usuel en zone rurale, puis en duree a 55 km/h de moyenne.
REPERES = _json.loads(pathlib.Path(__file__).resolve().parent.joinpath(
    "communes-data.json").read_text(encoding="utf-8"))

# L'Architecte des Batiments de France est saisi par departement : un chantier
# a Dreux ne depend pas du meme service qu'un chantier a Evreux. C'est une
# information que le proprietaire cherche vraiment, et qu'aucune page
# generique ne donne.
UDAP = {
    "27": ("l'UDAP de l'Eure", "Évreux"),
    "28": ("l'UDAP d'Eure-et-Loir", "Chartres"),
}


# ── ce que seul l'artisan sait ─────────────────────────────────────────────
# Les pages de commune plafonnent a ~413 mots d'editorial, alors que le seuil
# d'une page de lieu principale est 600. Le manque ne peut pas etre comble par
# du texte genere : il se verrait, et ce serait exactement le defaut des pages
# generiques des concurrents. Il vient d'un entretien avec Wesley.
#
# Ce bloc lit communes-terrain.json et ne s'affiche QUE pour les communes
# renseignees. Un champ vide n'invente rien.
_TERRAIN = _json.loads((pathlib.Path(__file__).resolve().parent /
                        "communes-terrain.json").read_text(encoding="utf-8"))["communes"]


def terrain_bloc(nom_ville):
    d = _TERRAIN.get(nom_ville) or {}
    champs = [
        ("Les toits d'ici", d.get("toits", "").strip()),
        ("Ce qui revient le plus", d.get("defaut", "").strip()),
        ("Un chantier de la commune", d.get("chantier", "").strip()),
    ]
    champs = [(h, txt) for h, txt in champs if txt]
    if not champs:
        return ""
    repere = (d.get("repere") or "").strip()
    corps = "".join(
        f'<div class="terrain__i reveal" data-d="{i+1}"><h3>{h}</h3><p>{txt}</p></div>'
        for i, (h, txt) in enumerate(champs))
    fin = f'<p class="terrain__p reveal" data-d="4">{repere}</p>' if repere else ""
    return f"""<section class="terrain">
  <div class="wrap">
    <p class="eyebrow reveal">De notre expérience</p>
    <h2 class="reveal" data-d="1">Sur les toits <em>de {nom_ville}</em></h2>
    <div class="terrain__g">{corps}</div>
    {fin}
  </div>
</section>"""


def reperes_bloc(ville, nom_ville):
    """Faits verifies propres a la commune.

    Premiere version : un gabarit a variables, ou seuls les chiffres
    changeaient. Elle a fait BAISSER l'unicite des pages, c'est-a-dire
    exactement le defaut reproche aux pages generiques des concurrents.
    Celle-ci branche le texte sur trois axes reels (eloignement, taille,
    departement), pour que les phrases elles-memes different et pas
    seulement les noms.

    Source : API Geo du gouvernement, relevee le 18/09/2026. Distance a vol
    d'oiseau x1,3 (facteur routier usuel en zone rurale), 55 km/h de moyenne.
    """
    d = REPERES.get(nom_ville)
    if not d:
        return ""
    km = round(d["km"] * 1.3)
    mn = max(5, round(km / 55 * 60 / 5) * 5)
    pop = d["pop"] or 0
    hab = f"{pop:,}".replace(",", " ")
    udap, chef_lieu = UDAP.get(d["dep"], ("", ""))
    meme_dep = d["dep"] == "27"

    # 1. l'eloignement change ce qu'on peut promettre
    if km <= 4:
        trajet = ("L'atelier est dans la commune. C'est ici que nous intervenons le plus "
                  "vite, et souvent le jour même quand il y a de l'eau qui rentre.")
    elif km <= 15:
        trajet = (f"{km} km depuis l'atelier des Maisons Rouges, environ {mn} minutes. "
                  "C'est dans notre rayon quotidien : passer voir un toit ne nous "
                  "demande pas d'organiser une journée.")
    else:
        trajet = (f"{km} km depuis l'atelier, environ {mn} minutes de route. Nous y "
                  "allons régulièrement, mais nous groupons les visites : comptez "
                  "quelques jours pour un rendez-vous de devis, immédiat en urgence.")

    # 2. la taille change le bati et donc le travail
    if pop < 3000:
        bati = ("Sur une commune de cette taille, le bâti est surtout ancien et isolé : "
                "longères, corps de ferme, dépendances. Les surfaces de rampant sont "
                "grandes et les charpentes ont souvent plus d'un siècle.")
    elif pop < 15000:
        bati = ("Le bourg mélange de l'ancien à reprendre et des pavillons des années "
                "soixante-dix à quatre-vingt-dix, dont les couvertures arrivent "
                "justement en fin de vie.")
    else:
        bati = ("Sur une ville de cette taille, nous voyons de tout : centre ancien "
                "contraint, lotissements pavillonnaires, et copropriétés où la "
                "décision se prend en assemblée. Le devis doit être lisible par des "
                "gens qui ne sont pas du métier.")

    # 3. le departement change l'administration qui tranche
    if meme_dep:
        admin = (f"{nom_ville} est dans l'Eure, notre département. La déclaration "
                 f"préalable se dépose à la mairie ; en périmètre de monument "
                 f"historique, c'est {udap} à {chef_lieu} qui donne l'avis.")
    else:
        admin = (f"{nom_ville} est en Eure-et-Loir, de l'autre côté de l'Avre. Les "
                 f"règles d'urbanisme ne sont pas celles de l'Eure : le dossier part "
                 f"à la mairie, et en périmètre de monument historique c'est "
                 f"{udap} à {chef_lieu} qui tranche, avec deux mois d'instruction.")

    return f"""<section class="reperes">
  <div class="wrap">
    <h2 class="reveal">{nom_ville} <em>en pratique</em></h2>
    <dl class="reperes__l reveal" data-d="1">
      <div><dt>Depuis l'atelier</dt><dd>{km} km, {mn} min</dd></div>
      <div><dt>Habitants</dt><dd>{hab}</dd></div>
      <div><dt>Département</dt><dd>{d["dep_nom"]} ({d["dep"]})</dd></div>
    </dl>
    <p class="reperes__p reveal" data-d="2">{trajet} {bati}</p>
    <p class="reperes__p reveal" data-d="3">{admin} Nous montons le dossier avec
      vous, et nous le disons avant de commencer, pas après : voir le
      <a href="{PRE}guides/declaration-prealable-toiture/">guide des autorisations</a>.</p>
  </div>
</section>"""

# ── pages prestation x commune ─────────────────────────────────────────────
# L'axe qui capte « demoussage toiture Dreux », une recherche differente de
# « couvreur Dreux ». C'est aussi l'endroit exact ou l'on derape : une page
# par combinaison possible, c'est une page satellite, et Google sanctionne
# tout le domaine, pas seulement les pages fautives.
#
# Garde-fous appliques :
#   · le modele local-service fixe l'alerte a 30 pages de lieu et l'ARRET a
#     50. Nous en avons 12, on en ajoute 8, soit 20. On reste sous l'alerte.
#   · une page n'existe que si la combinaison a une realite : les quatre
#     communes les plus peuplees, les deux prestations les plus demandees.
#   · chaque page porte du texte ECRIT pour elle, pas un gabarit a variables.
#     Le seuil d'une page de zone desservie est 500 mots et 40 % d'unicite.
PAIRES = [
 dict(svc="demoussage-toiture", ville="couvreur-dreux",
      nav="Démoussage à Dreux",
      title="Démoussage de toiture à Dreux (28100)",
      desc="Démoussage et nettoyage de toiture à Dreux : maisons de ville, pavillons et "
           "couvertures anciennes. Visite et devis gratuits, entreprise installée à 13 km.",
      h1=("Démoussage de <em>toiture</em>", "à Dreux"),
      img="demoussage-toiture-mousse-echafaudage.webp",
      imgalt="Démoussage d'une toiture envahie de mousse depuis un échafaudage",
      pourquoi=["Dreux est bâtie dans une cuvette, au confluent de la Blaise et de l'Eure, et "
                "l'humidité y stagne plus longtemps qu'en plateau. Les versants nord des maisons "
                "du centre reverdissent vite, d'autant que beaucoup sont mitoyennes et n'ont "
                "aucun ensoleillement direct d'un côté.",
                "L'autre facteur est l'âge du bâti. Le centre ancien et les quartiers des années "
                "soixante-dix portent des tuiles qui ont déjà largement perdu leur engobe. Une "
                "tuile poreuse retient l'eau, sèche mal, et devient un support idéal pour la "
                "mousse : le cycle s'accélère tout seul."],
      surplace=["Sur les maisons de ville mitoyennes, le sujet n'est pas le produit, c'est "
                "l'accès. Pas de recul devant, du stationnement, parfois un jardin arrière "
                "inaccessible depuis la rue. Nous chiffrons l'échafaudage ou la nacelle "
                "séparément pour que vous sachiez ce que vous payez.",
                "Sur les pavillons des quartiers pavillonnaires, c'est plus simple et souvent "
                "traitable à l'échelle, ce qui change nettement la facture.",
                "Ce que nous voyons le plus souvent à Dreux : des gouttières pleines de terre "
                "végétale, dans lesquelles poussent des plantes. Elles se vident au passage, "
                "sinon tout ce qu'on décroche du toit vient les boucher."],
      faq=[("Faut-il un échafaudage pour une maison de ville à Dreux ?",
            "Souvent oui, dès qu'il n'y a pas de recul ou que la hauteur dépasse un étage. Nous "
            "le disons à la visite et nous le chiffrons à part : c'est fréquemment le premier "
            "poste de la facture, et il n'a rien à voir avec la toiture elle-même."),
           ("Vous intervenez dans les quartiers ou seulement au centre ?",
            "Partout sur la commune, ainsi qu'à Vernouillet, Sainte-Gemme-Moronval et "
            "Cherisy. Dreux est à un quart d'heure de l'atelier, c'est dans notre rayon "
            "quotidien.")]),

 dict(svc="demoussage-toiture", ville="couvreur-evreux",
      nav="Démoussage à Évreux",
      title="Démoussage de toiture à Évreux (27000)",
      desc="Démoussage et nettoyage de toiture à Évreux et dans son agglomération. "
           "Traitement anti-mousse, gouttières comprises, devis gratuit après visite.",
      h1=("Démoussage de <em>toiture</em>", "à Évreux"),
      img="tuiles-mousse-vegetation.webp",
      imgalt="Tuiles anciennes envahies de mousse et de végétation",
      pourquoi=["Évreux s'étend sur les coteaux de l'Iton, et l'exposition change complètement "
                "d'un quartier à l'autre. Les maisons adossées aux versants boisés, côté "
                "Navarre ou vers la forêt, reçoivent des feuilles toute l'automne et gardent "
                "l'humidité : elles se remoussent deux fois plus vite que celles du plateau.",
                "C'est aussi la ville la plus éloignée de notre zone habituelle. Nous y allons "
                "régulièrement, mais nous groupons les interventions : pour un démoussage, "
                "c'est sans conséquence, ce n'est pas une urgence."],
      surplace=["Le bâti d'Évreux est le plus varié de notre secteur : centre reconstruit "
                "d'après-guerre, faubourgs anciens, grands lotissements des années soixante-dix "
                "et quatre-vingt. Chacun demande une approche différente, et surtout une "
                "pression différente.",
                "Sur les toitures d'après-guerre en tuile mécanique, le piège est la "
                "sur-pression : ces tuiles sont souvent minces et la haute pression les décape "
                "sans qu'on s'en aperçoive tout de suite. Nous adaptons, systématiquement.",
                "Sur les maisons proches de la forêt, le démoussage seul ne suffit pas "
                "longtemps : il faut aussi dégager les branches qui surplombent, sinon le toit "
                "reverdit en deux ans."],
      faq=[("Vous vous déplacez vraiment jusqu'à Évreux ?",
            "Oui, régulièrement. C'est à 38 km de l'atelier, environ quarante minutes. Comptez "
            "quelques jours d'attente pour un rendez-vous de devis, parce que nous groupons les "
            "déplacements sur ce secteur."),
           ("Le démoussage tient combien de temps ici ?",
            "Trois à cinq ans sur une maison dégagée, parfois deux seulement sous les arbres ou "
            "sur un versant nord permanent. Nous vous le disons à la visite plutôt que de "
            "promettre la même durée partout.")]),

 dict(svc="demoussage-toiture", ville="couvreur-vernouillet",
      nav="Démoussage à Vernouillet",
      title="Démoussage de toiture à Vernouillet (28500)",
      desc="Démoussage de toiture à Vernouillet : pavillons, maisons de plain-pied et "
           "couvertures des années 70-90. Nettoyage, traitement et gouttières. Devis gratuit.",
      h1=("Démoussage de <em>toiture</em>", "à Vernouillet"),
      img="toiture-alteree-lichens.webp",
      imgalt="Toiture ancienne altérée et couverte de lichens",
      pourquoi=["Vernouillet est largement pavillonnaire, et c'est une bonne nouvelle pour le "
                "démoussage : beaucoup de maisons de plain-pied ou à un étage, dégagées sur "
                "leurs quatre côtés, accessibles à l'échelle. Le poste échafaudage, qui plombe "
                "les factures en centre-ville, disparaît souvent ici.",
                "En revanche, le parc date en grande majorité des années soixante-dix à "
                "quatre-vingt-dix. Ces couvertures en tuile mécanique arrivent aujourd'hui "
                "autour de cinquante ans : c'est l'âge où la porosité augmente nettement et où "
                "la mousse s'installe pour de bon."],
      surplace=["Sur ce type de toiture, le vrai enjeu du démoussage n'est pas l'esthétique, "
                "c'est de savoir si la tuile est encore récupérable. Nous en descendons deux "
                "et nous les manipulons devant vous : si elles se cassent entre les doigts, un "
                "démoussage est de l'argent dépensé sur un toit à refaire, et nous le disons.",
                "Quand la couverture est encore saine, c'est au contraire le moment idéal : un "
                "démoussage suivi d'un hydrofuge sur une tuile de cet âge peut repousser la "
                "réfection de plusieurs années.",
                "Les lotissements de Vernouillet ont souvent des toitures identiques sur toute "
                "une rue. Quand plusieurs voisins font en même temps, l'échafaudage et le "
                "déplacement se partagent : cela vaut la peine d'en parler entre vous."],
      faq=[("Mes voisins ont le même toit, peut-on grouper ?",
            "Oui, et c'est fréquent dans les lotissements. Le déplacement et parfois le matériel "
            "se mutualisent. Dites-le-nous à la visite, nous chiffrons en conséquence."),
           ("Comment savoir si mon toit vaut encore un démoussage ?",
            "En montant et en manipulant deux tuiles. Une tuile saine se déplace, une tuile "
            "gélive se fend. C'est le seul test qui vaille, et il se fait devant vous.")]),

 dict(svc="demoussage-toiture", ville="couvreur-verneuil-avre-iton",
      nav="Démoussage à Verneuil",
      title="Démoussage de toiture à Verneuil d'Avre et d'Iton",
      desc="Démoussage de toiture à Verneuil d'Avre et d'Iton : centre ancien, tuile plate et "
           "ardoise. Nettoyage adapté au matériau, traitement anti-mousse. Devis gratuit.",
      h1=("Démoussage de <em>toiture</em>", "à Verneuil d'Avre et d'Iton"),
      img="tuiles-anciennes-patinees.webp",
      imgalt="Tuiles anciennes patinées par le temps sur une toiture",
      pourquoi=["Verneuil a un centre ancien dense, avec des maisons à pans de bois, de la "
                "petite tuile plate et de l'ardoise. Ce n'est pas le même travail que sur un "
                "pavillon : sur de la petite tuile plate de pays, chaque élément est fragile et "
                "la circulation sur le toit doit être limitée au strict nécessaire.",
                "Une partie du centre se trouve en périmètre de monument historique. Cela ne "
                "concerne pas un simple nettoyage, mais cela compte dès qu'il faut remplacer des "
                "tuiles au passage : le modèle et la teinte peuvent être imposés."],
      surplace=["Sur l'ardoise, le démoussage se pense autrement. L'ardoise n'est pas poreuse : "
                "les mousses s'accrochent en surface et aux crochets, pas dans la matière. On "
                "nettoie plus doucement, et l'hydrofuge n'a aucun intérêt — s'il vous est "
                "proposé sur de l'ardoise, posez des questions.",
                "Sur la petite tuile plate, le risque est mécanique : on en casse en marchant. "
                "Nous travaillons depuis des échelles de couvreur réparties, pas en circulant "
                "librement, et nous prévoyons toujours un petit stock de tuiles de "
                "remplacement au devis.",
                "Verneuil est à 32 km de l'atelier. Nous y groupons les visites, ce qui décale "
                "un rendez-vous de devis de quelques jours."],
      faq=[("Peut-on démousser une toiture en ardoise ?",
            "Oui, mais différemment : nettoyage doux, sans haute pression, et sans hydrofuge, "
            "qui ne sert à rien sur un matériau non poreux. Le risque principal est de "
            "desceller des crochets."),
           ("Ma maison est en secteur protégé, cela change-t-il quelque chose ?",
            "Pas pour le nettoyage lui-même. Cela compte si des tuiles doivent être remplacées : "
            "le modèle et la teinte peuvent être imposés, et il faut alors s'approvisionner en "
            "conséquence.")]),

 dict(svc="renovation-toiture", ville="couvreur-dreux",
      nav="Rénovation de toiture à Dreux",
      title="Rénovation de toiture à Dreux (28100)",
      desc="Réfection de toiture à Dreux : dépose, contrôle de charpente, écran de sous-toiture "
           "et couverture neuve en tuile, ardoise ou acier. Devis détaillé poste par poste.",
      h1=("Rénovation de <em>toiture</em>", "à Dreux"),
      img="couvreur-dreux-maison-de-ville-toiture.webp",
      imgalt="Toiture de maison de ville mitoyenne à Dreux",
      pourquoi=["Refaire un toit à Dreux pose deux questions que l'on ne rencontre pas en "
                "campagne : l'accès et l'urbanisme. En centre ancien, l'échafaudage empiète "
                "souvent sur le trottoir ou la chaussée, ce qui demande une autorisation de "
                "voirie et modifie le planning.",
                "Côté urbanisme, Dreux relève d'Eure-et-Loir : la déclaration préalable se "
                "dépose à la mairie, et une partie du centre se trouve en périmètre de monument "
                "historique. Le dossier passe alors devant l'architecte des Bâtiments de France "
                "à Chartres, ce qui allonge l'instruction à deux mois et peut imposer un "
                "matériau ou une teinte."],
      surplace=["Sur une maison mitoyenne, la dépose demande une organisation différente : on "
                "ne peut pas ouvrir largement et laisser le chantier en l'état. On avance par "
                "sections, et le logement est hors d'eau chaque soir.",
                "Les raccords avec les voisins sont le point technique de ces toitures : "
                "solins, noues communes, murs de refend qui dépassent en pignon. C'est là que "
                "les fuites apparaissent, et c'est ce que nous regardons en premier à la visite.",
                "Nous chiffrons poste par poste — dépose, évacuation, charpente, écran, "
                "couverture, zinguerie, échafaudage — précisément pour que vous puissiez "
                "comparer avec un autre devis ligne à ligne. Un prix global ne se compare à rien."],
      faq=[("Faut-il une autorisation pour refaire un toit à Dreux ?",
            "Une déclaration préalable, oui, dès lors que l'aspect extérieur change — et changer "
            "de tuile change l'aspect. Comptez un mois d'instruction, deux en périmètre de "
            "monument historique. Nous montons le dossier avec vous."),
           ("Combien de temps dure le chantier sur une maison de ville ?",
            "Une à deux semaines de présence pour une maison courante, hors intempéries, plus le "
            "montage et le démontage de l'échafaudage. Le délai global depuis la signature est "
            "plutôt de deux à quatre mois, à cause de l'autorisation et de l'approvisionnement.")]),

 dict(svc="renovation-toiture", ville="couvreur-evreux",
      nav="Rénovation de toiture à Évreux",
      title="Rénovation de toiture à Évreux (27000)",
      desc="Réfection complète de toiture à Évreux : charpente contrôlée, écran de "
           "sous-toiture, couverture neuve. Entreprise familiale de l'Eure, devis détaillé.",
      h1=("Rénovation de <em>toiture</em>", "à Évreux"),
      img="refection-toiture-pavillon-terminee.webp",
      imgalt="Réfection de toiture de pavillon terminée",
      pourquoi=["Évreux est dans l'Eure, notre département. Cela simplifie une partie du "
                "dossier : la déclaration préalable se dépose à la mairie et, en périmètre de "
                "monument historique, c'est l'unité départementale de l'architecture et du "
                "patrimoine de l'Eure qui donne l'avis, à Évreux même.",
                "Le parc immobilier de la ville comporte beaucoup de constructions "
                "d'après-guerre et des grands lotissements des années soixante-dix. Ces "
                "couvertures arrivent aujourd'hui en fin de vie toutes en même temps, souvent "
                "sans écran de sous-toiture."],
      surplace=["Sur ces maisons, la réfection est l'occasion unique de rattraper deux retards "
                "d'un coup : poser l'écran de sous-toiture qui n'a jamais existé, et isoler. "
                "Faire les deux séparément coûte nettement plus cher, parce que l'échafaudage et "
                "la dépose se paient deux fois.",
                "La charpente de ces constructions est généralement saine, sauf aux abouts de "
                "chevrons en bas de pente, là où la gouttière a débordé pendant des années. "
                "C'est la reprise la plus fréquente, et elle se chiffre à l'avance si on la "
                "constate à la visite.",
                "Évreux est à 38 km, environ quarante minutes. Pour un chantier de plusieurs "
                "jours, la distance ne change rien à l'organisation : l'équipe reste sur place "
                "la journée."],
      faq=[("Vous prenez des chantiers complets jusqu'à Évreux ?",
            "Oui. Pour une réfection, la distance n'est pas un obstacle : l'équipe reste sur "
            "place toute la journée. C'est pour les petites interventions que l'éloignement "
            "compte."),
           ("Peut-on isoler en même temps que la réfection ?",
            "C'est même le meilleur moment, et le seul où l'isolation par l'extérieur est "
            "possible sans surcoût de dépose. Nous chiffrons les deux séparément pour que vous "
            "voyiez ce que coûte réellement l'isolation.")]),

 dict(svc="renovation-toiture", ville="couvreur-vernouillet",
      nav="Rénovation de toiture à Vernouillet",
      title="Rénovation de toiture à Vernouillet (28500)",
      desc="Réfection de toiture à Vernouillet : pavillons et maisons des années 70-90. "
           "Dépose, écran de sous-toiture, couverture neuve. Devis détaillé poste par poste.",
      h1=("Rénovation de <em>toiture</em>", "à Vernouillet"),
      img="renovation-toiture-charpente-liteaux-neufs.webp",
      imgalt="Charpente et liteaux neufs sur une toiture en cours de rénovation",
      pourquoi=["Vernouillet est un cas d'école : un parc pavillonnaire massivement construit "
                "entre 1970 et 1990, avec des couvertures en tuile mécanique qui atteignent "
                "toutes leur limite en même temps. Beaucoup de ces toits n'ont jamais eu d'écran "
                "de sous-toiture, parce que ce n'était pas la pratique à l'époque.",
                "Conséquence concrète : une tuile déplacée par le vent ne pardonne pas. L'eau "
                "tombe directement dans les combles, sur l'isolant, et le propriétaire ne s'en "
                "aperçoit qu'à la tache au plafond, parfois des mois plus tard."],
      surplace=["Sur ces maisons, la réfection est simple techniquement : charpente en fermettes "
                "industrielles généralement saine, pentes régulières, accès dégagé. C'est ce qui "
                "permet un chantier court et un prix maîtrisé.",
                "Le point de vigilance est la fermette elle-même : on ne coupe jamais un élément "
                "d'une charpente industrielle sans calcul, même pour passer un conduit ou "
                "aménager. Chaque pièce participe à l'équilibre de l'ensemble.",
                "L'autre sujet est l'isolation des combles perdus, presque toujours en place "
                "mais presque toujours sous-dimensionnée : dix centimètres posés à l'époque, "
                "contre trente à quarante attendus aujourd'hui. La réfection est le moment de "
                "regarder."],
      faq=[("Ma maison date de 1978, faut-il tout refaire ?",
            "Pas forcément. À cet âge, certaines couvertures sont encore saines et d'autres sont "
            "finies. Le test se fait en manipulant des tuiles : si elles cassent, c'est terminé. "
            "Nous le faisons devant vous et nous le disons franchement."),
           ("Peut-on garder la charpente ?",
            "Dans l'immense majorité des cas de ce parc, oui. Les fermettes sont saines, sauf "
            "aux abouts si l'eau a coulé longtemps. On contrôle pendant la dépose et on reprend "
            "ponctuellement si besoin.")]),

 dict(svc="renovation-toiture", ville="couvreur-anet",
      nav="Rénovation de toiture à Anet",
      title="Rénovation de toiture à Anet (28260)",
      desc="Réfection de toiture à Anet : bâti ancien, tuile plate et ardoise, contraintes de "
           "secteur patrimonial. Dépose, charpente, couverture neuve. Devis détaillé.",
      h1=("Rénovation de <em>toiture</em>", "à Anet"),
      img="corps-de-ferme-pierre-depose-couverture.webp",
      imgalt="Corps de ferme en pierre dont la couverture est en cours de dépose",
      pourquoi=["Anet est une commune où le patrimoine pèse sur les chantiers de toiture. Le "
                "château et ses abords créent un périmètre dans lequel tout changement d'aspect "
                "extérieur passe devant l'architecte des Bâtiments de France, à Chartres pour "
                "l'Eure-et-Loir.",
                "Concrètement, cela veut dire que le matériau n'est pas toujours un choix libre. "
                "Le modèle de tuile, sa teinte, parfois le type de zinguerie peuvent être "
                "imposés. Et l'instruction passe d'un à deux mois : c'est à intégrer au "
                "calendrier dès le départ, pas à découvrir après la signature."],
      surplace=["Le bâti ancien d'Anet demande des matériaux qui ne sont pas toujours en stock. "
                "Une petite tuile plate de pays dans une teinte précise peut représenter "
                "plusieurs semaines de fabrication. Nous le vérifions avant de donner une date "
                "de démarrage, pas après.",
                "Les charpentes y sont souvent anciennes et de belle facture. Quand elles sont "
                "saines, elles se conservent et se reprennent ponctuellement : il serait absurde "
                "de remplacer du chêne centenaire encore sain par du résineux neuf.",
                "Anet est à 24 km de l'atelier, environ vingt-cinq minutes. Nous y intervenons "
                "régulièrement, ainsi qu'à Ivry-la-Bataille et Saint-Georges-Motel."],
      faq=[("Le château impose-t-il vraiment des contraintes à toute la commune ?",
            "Pas à toute la commune, mais à un périmètre autour. Il faut vérifier si votre "
            "parcelle y est : cela se demande en mairie, et c'est la première chose à faire "
            "avant de choisir un matériau."),
           ("Peut-on conserver la charpente ancienne ?",
            "Presque toujours, si elle est saine. Le chêne ancien est souvent de meilleure "
            "qualité que ce qui se pose aujourd'hui. On sonde pendant la dépose et on reprend "
            "seulement ce qui doit l'être.")]),
]


def render_paire(pr):
    """Page prestation x commune. Reutilise les blocs de conversion du site et
    n'ajoute que du texte ecrit pour cette combinaison precise."""
    svc = next(x for x in SERVICES if x["slug"] == pr["svc"])
    v = next(x for x in VILLES if x["slug"] == pr["ville"])
    slug = f'{pr["svc"]}-{v["ville"].lower().replace(" ", "-").replace("'", "-")}'
    slug = (slug.replace("é", "e").replace("è", "e").replace("ê", "e")
                .replace("î", "i").replace("ô", "o").replace("à", "a").replace("--", "-"))
    canon = slug + "/"
    d = REPERES.get(v["ville"], {})
    km = round(d.get("km", 0) * 1.3) if d else None

    ld = ('{"@context":"https://schema.org","@graph":[' + ld_business() + ','
          '{"@type":"Service","name":%s,"serviceType":%s,'
          '"provider":{"@id":"%s/#business"},"areaServed":{"@type":"City","name":%s},'
          '"url":"%s/%s"},'
          '{"@type":"WebPage","name":%s,"url":"%s/%s","about":{"@id":"%s/#business"}},'
          '{"@type":"BreadcrumbList","itemListElement":['
          '{"@type":"ListItem","position":1,"name":"Accueil","item":"%s/"},'
          '{"@type":"ListItem","position":2,"name":%s,"item":"%s/%s/"},'
          '{"@type":"ListItem","position":3,"name":%s,"item":"%s/%s"}]},'
          '{"@type":"FAQPage","mainEntity":[%s]}]}'
          % (jstr(pr["nav"]), jstr(svc["nav"]), DOMAIN, jstr(v["ville"]), DOMAIN, canon,
             jstr(pr["title"]), DOMAIN, canon, DOMAIN,
             DOMAIN,
             jstr(svc["nav"]), DOMAIN, svc["slug"],
             jstr(pr["nav"]), DOMAIN, canon,
             ",".join('{"@type":"Question","name":%s,"acceptedAnswer":'
                      '{"@type":"Answer","text":%s}}' % (jstr(q), jstr(a))
                      for q, a in pr["faq"])))

    pourquoi = "".join(f"<p>{x}</p>" for x in pr["pourquoi"])
    surplace = "".join(f"<p>{x}</p>" for x in pr["surplace"])
    autres = "".join(
        f'<li><a href="{PRE}{x["slug"]}/">{x["nav"]}<span>{ARROW}</span></a></li>'
        for x in SERVICES if x["slug"] != svc["slug"])
    trajet = ("dans la commune de l'atelier" if not km or km <= 4
              else f"à {km} km de l'atelier")

    return "".join([
        head(pr["title"] + " · WM Couverture", pr["desc"], canon, ld, pr["img"]),
        "<main id=\"main\">",
        f"""<section class="phero">
  <div class="wrap phero__grid">
    <div>
      <p class="eyebrow reveal">{svc["nav"]} <span aria-hidden="true">·</span> {v["ville"]}</p>
      <h1 class="reveal" data-d="1">{pr["h1"][0]}<br>{pr["h1"][1]}</h1>
      <p class="phero__lead reveal" data-d="2">{pr["pourquoi"][0][:210]}…</p>
      {hero_note()}
      <div class="phero__cta reveal" data-d="3">
        <a class="btn btn--dark" href="#devis">Demander mon devis gratuit</a>
        <a class="btn btn--ghost" href="tel:{TEL_HREF}" data-track="call">{PHONE}{TEL_TXT}</a></div>
      <ul class="hero__trust phero__trust reveal" data-d="4">
        <li><b data-count="14">14</b> ans d'expérience</li>
        <li><b>7</b>j/7, de 8 h à 21 h</li>
      </ul>
    </div>
    <figure class="frame phero__img reveal" data-d="2">
      <img src="{PRE}assets/img/{pr["img"]}" alt="{pr["imgalt"]}" width="1600" height="1200" fetchpriority="high" decoding="async">
    </figure>
  </div>
</section>""",
        crumb(pr["nav"]),
        f"""<section class="detail">
  <div class="wrap detail__grid">
    <div><p class="eyebrow reveal">Pourquoi ici</p>
      <h2 class="reveal" data-d="1">{svc["nav"]} <em>à {v["ville"]}</em></h2></div>
    <div class="detail__t reveal" data-d="1">{pourquoi}</div>
  </div>
</section>""",
        f"""<section class="detail detail--alt">
  <div class="wrap detail__grid">
    <div><p class="eyebrow reveal">Sur place</p>
      <h2 class="reveal" data-d="1">Ce que nous <em>trouvons</em> sur ces toits</h2></div>
    <div class="detail__t reveal" data-d="1">{surplace}</div>
  </div>
</section>""",
        reperes_bloc(v, v["ville"]),
        terrain_bloc(v["ville"]),
        band(pr["img"], pr["imgalt"], f'{svc["nav"]} à {v["ville"]}',
             f'Un toit à voir {trajet} : nous nous déplaçons et le devis est gratuit.'),
        avis_pair(AVIS[0], AVIS[2]),
        faq_block(pr["faq"] + v["faq"][:2]),
        f"""<section class="mesh">
  <div class="wrap mesh__grid">
    <div><h2 class="reveal">Nos autres <em>prestations</em></h2>
      <ul class="mesh__list reveal" data-d="1">{autres}</ul></div>
    <div><h2 class="reveal">En savoir plus</h2>
      <ul class="mesh__list reveal" data-d="1">
        <li><a href="{PRE}{svc["slug"]}/">{svc["nav"]}, en détail<span>{ARROW}</span></a></li>
        <li><a href="{PRE}{v["slug"]}/">Couvreur à {v["ville"]}<span>{ARROW}</span></a></li>
      </ul></div>
  </div>
</section>""",
        devis(f'{svc["nav"]} <em>à {v["ville"]}</em> ?',
              "Décrivez la situation en deux lignes, nous rappelons pour caler une visite."),
        "</main>",
        foot(),
    ]), slug


def render_ville(v):
    canon = v["slug"] + "/"
    dist = ("notre atelier" if v["km"] is None else f"à {v['km']} km de l'atelier")
    dist_p = ("dans la commune de l'atelier" if v["km"] is None
              else f"à {v['km']} km de l'atelier")
    autour = "".join(f"<li>{c}</li>" for c in v["autour"])
    # on tourne sur quatre vues du secteur, en evitant celle deja en haut de page
    bi = [x for x in BANDS_VILLE if x[0] != v["photo"]]
    bimg, balt = bi[[x["slug"] for x in VILLES].index(v["slug"]) % len(bi)]
    svc = "".join(
        f'<li><a href="{PRE}{x["slug"]}/"><b>{x["nav"]}</b><span>{x["pitch"]}</span>{ARROW}</a></li>'
        for x in SERVICES)
    ld = ('{"@context":"https://schema.org","@graph":[' + ld_business() + ','
          '{"@type":"WebPage","name":%s,"url":"%s/%s","about":{"@id":"%s/#business"}},'
          '{"@type":"BreadcrumbList","itemListElement":['
          '{"@type":"ListItem","position":1,"name":"Accueil","item":"%s/"},'
          '{"@type":"ListItem","position":2,"name":%s}]}]}'
          % (jstr("Couvreur à " + v["ville"]), DOMAIN, canon, DOMAIN, DOMAIN,
             jstr("Couvreur à " + v["ville"])))
    return "".join([
        head(v["title"], v["desc"], canon, ld, v["photo"]),
        nav(v["slug"]),
        '<main id="main">',
        crumb("Couvreur à " + v["ville"]),
        page_hero(f'{v["ville"]} · {v["cp"]} · {dist}', "Couvreur à", f'<em>{v["ville"]}</em>',
                  v["intro"], v["photo"], v["photoalt"]),
        facts_row(),
        f"""<section class="detail">
  <div class="wrap detail__grid">
    <div>
      <h2 class="reveal">Le bâti <em>de {v["ville"]}</em></h2>
      <p class="detail__p reveal" data-d="1">{v["bati"]}</p>
      <p class="detail__p reveal" data-d="2">{v["enjeu"]}</p>
    </div>
    <div class="detail__alert">
      <h2 class="reveal">Autour de {v["ville"]}</h2>
      <p class="detail__p reveal" data-d="1">Nous nous déplaçons aussi dans les communes voisines :</p>
      <ul class="ticks reveal" data-d="2">{autour}</ul>
      <a class="link-arrow reveal" data-d="3" href="#devis">Demander un devis{ARROW}</a>
    </div>
  </div>
</section>""",
        f"""<section class="svc">
  <div class="wrap">
    <h2 class="reveal">Ce que nous faisons <em>à {v["ville"]}</em></h2>
    <ul class="svc__list">{svc}</ul>
  </div>
</section>""",
        mat_block(f'Ce que nous faisons le plus <em>à {v["ville"]}</em>', v["focus"], "deep deep--alt"),
        reperes_bloc(v, v["ville"]),
        terrain_bloc(v["ville"]),
        band(bimg, balt, f'Couvreur à {v["ville"]}',
             f'Un toit à voir {dist_p}, un devis à faire chiffrer : nous nous déplaçons.'),
        etapes(),
        avis_pair(AVIS[1], AVIS[3]),
        faq_block(v["faq"]),
        maillage(v["slug"]),
        devis(f'Un toit à voir <em>à {v["ville"]}</em> ?',
              "Décrivez la situation en deux lignes, nous rappelons pour caler une visite."),
        "</main>",
        foot(),
    ])


def jstr(x):
    return '"' + x.replace('\\', '\\\\').replace('"', '\\"').replace("\n", " ") + '"'



def estimateur():
    return """<section class="calc">
  <div class="wrap calc__grid">
    <div class="calc__intro">
      <h2 class="reveal">Calculez la <em>surface</em> de votre toit</h2>
      <p class="reveal" data-d="1">Donnez l'emprise au sol de la partie couverte et la pente.
        Vous obtenez la surface de rampant, celle sur laquelle un couvreur chiffre.
        C'est un ordre de grandeur, pas un métré.</p>
    </div>
    <form class="calc__form reveal" data-d="1" id="calc" novalidate>
      <div class="f-row">
        <div class="f"><input id="c_l" type="number" min="1" step="0.1" inputmode="decimal" placeholder=" ">
          <label for="c_l">Longueur au sol (m)</label></div>
        <div class="f"><input id="c_w" type="number" min="1" step="0.1" inputmode="decimal" placeholder=" ">
          <label for="c_w">Largeur au sol (m)</label></div>
      </div>
      <fieldset class="f-chips">
        <legend>Pente du toit</legend>
        <label><input type="radio" name="pente" value="1.05"><span>Faible, 18°</span></label>
        <label><input type="radio" name="pente" value="1.15" checked><span>Courante, 30°</span></label>
        <label><input type="radio" name="pente" value="1.24"><span>Marquée, 36°</span></label>
        <label><input type="radio" name="pente" value="1.41"><span>Forte, 45°</span></label>
      </fieldset>
      <fieldset class="f-chips">
        <legend>Couverture envisagée</legend>
        <label><input type="radio" name="mat" value="13" checked><span>Tuile mécanique</span></label>
        <label><input type="radio" name="mat" value="60"><span>Tuile plate</span></label>
        <label><input type="radio" name="mat" value="22"><span>Ardoise</span></label>
      </fieldset>
      <output class="calc__out" id="calcOut" aria-live="polite"></output>
      <a class="btn btn--dark btn--full" href="#devis">Faire chiffrer cette surface</a>
      <p class="form__note">Aucune donnée n'est envoyée : le calcul se fait dans votre navigateur.</p>
    </form>
  </div>
</section>"""


def render_guide(g):
    global PRE
    PRE = "../../"
    canon = "guides/" + g["slug"] + "/"
    faq_ld = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (jstr(q), jstr(a)) for q, a in g["faq"])
    ld = ('{"@context":"https://schema.org","@graph":[' + ld_business() + ','
          '{"@type":"Article","headline":%s,"description":%s,"inLanguage":"fr-FR",'
          '"url":"%s/%s","isAccessibleForFree":true,'
          '"author":{"@id":"%s/#business"},"publisher":{"@id":"%s/#business"},'
          '"about":{"@type":"Thing","name":"Toiture"}},'
          '{"@type":"FAQPage","mainEntity":[%s]},'
          '{"@type":"BreadcrumbList","itemListElement":['
          '{"@type":"ListItem","position":1,"name":"Accueil","item":"%s/"},'
          '{"@type":"ListItem","position":2,"name":"Guides","item":"%s/guides/"},'
          '{"@type":"ListItem","position":3,"name":%s}]}]}'
          % (jstr(g["title"]), jstr(g["desc"]), DOMAIN, canon, DOMAIN, DOMAIN,
             faq_ld, DOMAIN, DOMAIN, jstr(g["nav"])))

    blocs = ['<section class="prose__s reveal" id="%s"><h2>%s</h2><div class="prose__b">%s</div></section>'
             % (slugify(t), t, "".join("<p>%s</p>" % x.replace("{PRE}", PRE) for x in ps))
             for t, ps in g["sections"]]
    # la phrase cle vient couper le rythme titre-a-gauche / texte-a-droite
    if g.get("cle") and len(blocs) > 2:
        blocs.insert(len(blocs) // 2, pullq(g["cle"]))
    secs = "".join(blocs)
    svc = next(x for x in SERVICES if x["slug"] == g["cta"][1])
    autres = "".join(
        f'<li><a href="{PRE}guides/{x["slug"]}/">{x["nav"]}<span>{ARROW}</span></a></li>'
        for x in GUIDES if x["slug"] != g["slug"])

    out = "".join([
        head(g["title"] + " · WM Couverture", g["desc"], canon, ld),
        nav(g["slug"]),
        '<main id="main">',
        crumb(g["nav"], extra=("Guides", "guides/")),
        f"""<section class="ghero">
  <div class="wrap">
    <p class="eyebrow reveal">Guide</p>
    <h1 class="reveal" data-d="1">{g["h1"][0]}<br>{g["h1"][1]}</h1>
    <div class="answer reveal" data-d="2">
      <p class="answer__t">En bref</p>
      <p>{g["court"]}</p>
    </div>
    {sommaire(g["sections"])}
  </div>
</section>""",
        (f'<div class="wrap"><figure class="frame frame--wide gimg reveal">'
         f'<img src="{PRE}assets/img/{g["img"]}" alt="{g["imgalt"]}" '
         f'width="1680" height="720" loading="lazy" decoding="async"></figure></div>'
         if g.get("img") else ""),
        estimateur() if g.get("estim") else "",
        f'<div class="wrap prose">{secs}</div>',
        f"""<section class="local">
  <div class="wrap local__in">
    <div>
      <p class="eyebrow reveal">Vous êtes dans le secteur ?</p>
      <h2 class="reveal" data-d="1">Nous intervenons dans <em>l'Eure et le Drouais</em></h2>
      <p class="reveal" data-d="2">Atelier à Nonancourt, déplacements jusqu'à Évreux et au sud de
        Dreux. Devis gratuit, réponse le jour même en général.</p>
    </div>
    <ul class="local__villes reveal" data-d="1">{"".join(f'<li><a href="{PRE}{x["slug"]}/">{x["ville"]}</a></li>' for x in VILLES[:8])}</ul>
  </div>
</section>""",
        f"""<div class="wrap"><p class="byline reveal">Écrit par l'équipe de WM Couverture,
          couvreurs à Nonancourt depuis 2011. Ce guide décrit notre pratique de terrain dans
          l'Eure et le Drouais. Il ne remplace pas une visite : chaque toit a ses particularités.</p></div>""",
        faq_block(g["faq"]),
        f"""<section class="gcta">
  <div class="wrap gcta__in">
    <div>
      <h2 class="reveal">{g["cta"][0]}</h2>
      <p class="reveal" data-d="1">{svc["pitch"]} Devis gratuit, réponse le jour même en général.</p>
    </div>
    <div class="gcta__btn reveal" data-d="2">
      <a class="btn btn--brass btn--lg" href="{PRE}{svc["slug"]}/">{svc["nav"]}</a>
      <a class="link-arrow link-arrow--light" href="tel:{TEL_HREF}" data-track="call">{TEL_TXT}{ARROW}</a>
    </div>
  </div>
</section>""",
        f"""<section class="mesh">
  <div class="wrap mesh__grid mesh__grid--3">
    <div><h2 class="reveal">Les autres <em>guides</em></h2><ul class="mesh__list reveal" data-d="1">{autres}</ul></div>
    <div><h2 class="reveal">Nos <em>prestations</em></h2><ul class="mesh__list reveal" data-d="1">{"".join(f'<li><a href="{PRE}{x["slug"]}/">{x["nav"]}<span>{ARROW}</span></a></li>' for x in SERVICES)}</ul></div>
    <div><h2 class="reveal">Où nous <em>intervenons</em></h2><ul class="mesh__list reveal" data-d="1">{"".join(f'<li><a href="{PRE}{x["slug"]}/">{x["ville"]}<span>{ARROW}</span></a></li>' for x in VILLES[:6])}</ul></div>
  </div>
</section>""",
        devis("Une question sur <em>votre toit</em> ?",
              "Décrivez la situation en deux lignes, nous rappelons pour fixer une visite."),
        "</main>",
        foot(),
    ])
    PRE = "../"
    return out


def render_plan():
    global PRE
    PRE = "../"
    def col(titre, items):
        li = "".join(f'<li><a href="{PRE}{u}">{t}</a></li>' for t, u in items)
        return f'<div><h2 class="reveal">{titre}</h2><ul class="plan__list">{li}</ul></div>'
    ld = ('{"@context":"https://schema.org","@graph":[' + ld_business() + ','
          '{"@type":"WebPage","name":"Plan du site","url":"%s/plan-du-site/"}]}' % DOMAIN)
    return "".join([
        head("Plan du site · WM Couverture, couvreur à Nonancourt",
             "Toutes les pages du site WM Couverture : prestations de couverture, communes "
             "d'intervention autour de Nonancourt et guides pratiques sur la toiture.",
             "plan-du-site/", ld),
        nav("plan-du-site"),
        '<main id="main">',
        crumb("Plan du site"),
        """<section class="ghero"><div class="wrap">
          <p class="eyebrow reveal">Plan du site</p>
          <h1 class="reveal" data-d="1">Toutes les <em>pages</em></h1></div></section>""",
        f"""<section class="plan"><div class="wrap plan__grid">
          {col("Prestations", [(x["nav"], x["slug"] + "/") for x in SERVICES])}
          {col("Communes", [("Couvreur à " + x["ville"], x["slug"] + "/") for x in VILLES])}
          {col("Guides", [(x["nav"], "guides/" + x["slug"] + "/") for x in GUIDES]
               + [("Tous les guides", "guides/")])}
          {col("Le site", [("Accueil", ""), ("Mentions légales", "mentions-legales.html")])}
        </div></section>""",
        "</main>",
        foot(),
    ])


def render_404():
    global PRE
    PRE = ""
    body = "".join([
        head("Page introuvable · WM Couverture",
             "Cette page n'existe pas ou plus. Retrouvez nos prestations de couverture et nos "
             "communes d'intervention autour de Nonancourt.", "404.html", "{}"),
        nav(""),
        '<main id="main">',
        f"""<section class="ghero">
  <div class="wrap">
    <p class="eyebrow">Erreur 404</p>
    <h1>Cette page <em>n'existe pas</em></h1>
    <p class="ghero__lead">Elle a peut-être changé d'adresse lors de la refonte du site.
      Voici par où reprendre, ou appelez-nous directement au {TEL_TXT}.</p>
    <p class="phero__cta" style="margin-top:28px">
      <a class="btn btn--dark" href="{PRE}">Retour à l'accueil</a>
      <a class="btn btn--ghost" href="tel:{TEL_HREF}" data-track="call">{PHONE}{TEL_TXT}</a></p>
  </div>
</section>""",
        f"""<section class="mesh">
  <div class="wrap mesh__grid">
    <div><h2>Nos <em>prestations</em></h2><ul class="mesh__list">{"".join(f'<li><a href="{PRE}{x["slug"]}/">{x["nav"]}<span>{ARROW}</span></a></li>' for x in SERVICES)}</ul></div>
    <div><h2>Nos <em>communes</em></h2><ul class="mesh__list">{"".join(f'<li><a href="{PRE}{x["slug"]}/">{x["ville"]}<span>{ARROW}</span></a></li>' for x in VILLES[:6])}</ul></div>
  </div>
</section>""",
        "</main>",
        foot(),
    ])
    body = body.replace('<meta name="theme-color"', '<meta name="robots" content="noindex,follow">\n<meta name="theme-color"')
    PRE = "../"
    return body


def render_hub():
    global PRE
    PRE = "../"
    canon = "guides/"
    # La page vendait dix guides sans montrer une seule image, alors que chacun
    # a deja son bandeau. Premier guide en vedette, les neuf autres en lignes
    # illustrees : un index de magazine, pas une grille de cartes.
    f = GUIDES[0]
    vedette = f"""<a class="hubfeat reveal" href="{PRE}guides/{f["slug"]}/">
      <figure class="hubfeat__img"><img src="{PRE}assets/img/{f["img"]}" alt="{f["imgalt"]}"
        width="1680" height="720" loading="lazy" decoding="async"></figure>
      <div class="hubfeat__txt">
        <p class="hubfeat__k">À lire en premier</p>
        <h2>{f["nav"]}</h2>
        <p class="hubfeat__d">{f["desc"]}</p>
        <span class="link-arrow">Lire le guide {ARROW}</span>
      </div>
    </a>"""
    items = "".join(
        f'<li class="reveal" data-d="{min(i, 3)}"><a href="{PRE}guides/{g["slug"]}/">'
        f'<img class="hubrow__img" src="{PRE}assets/img/{g["img"]}" alt="{g["imgalt"]}" '
        f'width="1680" height="720" loading="lazy" decoding="async">'
        f'<span class="hubrow__t"><b>{g["nav"]}</b><span>{g["desc"]}</span></span>{ARROW}</a></li>'
        for i, g in enumerate(GUIDES[1:]))
    ld = ('{"@context":"https://schema.org","@graph":[' + ld_business() + ','
          '{"@type":"CollectionPage","name":"Guides toiture","url":"%s/guides/",'
          '"inLanguage":"fr-FR","about":{"@id":"%s/#business"}},'
          '{"@type":"BreadcrumbList","itemListElement":['
          '{"@type":"ListItem","position":1,"name":"Accueil","item":"%s/"},'
          '{"@type":"ListItem","position":2,"name":"Guides"}]}]}'
          % (DOMAIN, DOMAIN, DOMAIN))
    return "".join([
        head("Guides toiture : prix, fuite, démoussage · WM Couverture",
             "Nos guides pour comprendre un devis de toiture, réagir à une fuite, entretenir "
             "son toit et connaître les aides. Écrits par un couvreur de l'Eure.", canon, ld),
        nav("guides"),
        '<main id="main">',
        crumb("Guides"),
        """<section class="ghero">
  <div class="wrap">
    <p class="eyebrow reveal">Guides</p>
    <h1 class="reveal" data-d="1">Comprendre <em>votre toit</em><br>avant de signer</h1>
    <p class="ghero__lead reveal" data-d="2">Ce que nous expliquons tous les jours en clientèle,
      écrit noir sur blanc. Sans jargon et sans vendre.</p>
  </div>
</section>""",
        f"""<section class="hub">
  <div class="wrap">
    <div class="hub__intro">
      <p class="reveal">Un devis de toiture est difficile à lire quand on n'est pas du métier,
        et c'est souvent là que les gens se font avoir : sur une surface annoncée au sol plutôt
        qu'en rampant, sur un échafaudage oublié, sur une aide promise qui n'existait pas pour
        ce type de travaux.</p>
      <p class="reveal" data-d="1">Ces guides reprennent ce que nous expliquons chaque semaine
        chez nos clients. Ils sont écrits par des couvreurs qui montent sur les toits de l'Eure
        depuis quatorze ans, pas par un rédacteur.</p>
    </div>
    {vedette}
    <ul class="svc__list hub__list hub__list--img">{items}</ul>
  </div>
</section>""",
        devis("Une question sur <em>votre toit</em> ?",
              "Décrivez la situation en deux lignes, nous rappelons pour fixer une visite."),
        "</main>",
        foot(),
    ])


# ─────────────────────────────────────────────────────────────── écrit ─────
def typo(t):
    """Typographie francaise : espaces insecables avant les ponctuations doubles
    et a l'interieur des guillemets, pour eviter les rejets en debut de ligne."""
    t = t.replace(" »", "\u00a0»").replace("« ", "«\u00a0")
    for c in (":", ";", "!", "?", "%"):
        t = t.replace(" " + c, "\u00a0" + c)
    return t.replace("\u00a0:", "\u00a0:")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if path.endswith(".html"):
        content = typo(content)
    open(path, "w").write(content)


def main():
    pages = []
    for s in SERVICES:
        write(os.path.join(ROOT, s["slug"], "index.html"), render_service(s))
        pages.append((s["slug"] + "/", "0.9"))
    for v in VILLES:
        write(os.path.join(ROOT, v["slug"], "index.html"), render_ville(v))
        pages.append((v["slug"] + "/", "0.8"))
    for pr in PAIRES:
        html, slug = render_paire(pr)
        write(os.path.join(ROOT, slug, "index.html"), html)
        pages.append((slug + "/", "0.75"))

    write(os.path.join(ROOT, "404.html"), render_404())
    write(os.path.join(ROOT, "plan-du-site", "index.html"), render_plan())
    pages.append(("plan-du-site/", "0.3"))
    write(os.path.join(ROOT, "guides", "index.html"), render_hub())
    pages.append(("guides/", "0.7"))
    for g in GUIDES:
        write(os.path.join(ROOT, "guides", g["slug"], "index.html"), render_guide(g))
        pages.append((f'guides/{g["slug"]}/', "0.7"))

    import datetime
    today = datetime.date.today().isoformat()
    import glob as _g, os as _o
    imgs = sorted(_o.path.basename(f) for f in _g.glob(_o.path.join(ROOT, "assets", "img", "*.webp")))
    img_tags = "".join(
        f'\n    <image:image><image:loc>{DOMAIN}/assets/img/{f}</image:loc></image:image>'
        for f in imgs[:40])
    urls = "".join(f"  <url><loc>{DOMAIN}/{p}</loc><lastmod>{today}</lastmod>"
                   f"<changefreq>monthly</changefreq><priority>{pr}</priority></url>\n"
                   for p, pr in pages)
    write(os.path.join(ROOT, "sitemap.xml"),
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
          '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
          f'  <url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq>'
          f'<priority>1.0</priority>{img_tags}\n  </url>\n{urls}</urlset>\n')

    # Les crawlers IA sont autorises explicitement : ChatGPT et Perplexity
    # citent les artisans locaux, et 3 des 5 premiers facteurs de visibilite IA
    # sont lies aux citations.
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User",
            "ClaudeBot", "Claude-User", "Google-Extended", "Applebot", "Applebot-Extended",
            "Bingbot", "CCBot", "meta-externalagent"]
    write(os.path.join(ROOT, "robots.txt"),
          "User-agent: *\nAllow: /\n\n"
          + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
          + f"Sitemap: {DOMAIN}/sitemap.xml\n")

    # llms.txt : resume lisible par les moteurs generatifs
    llm = [f"# WM Couverture", "",
           "> Entreprise familiale de couverture installee aux Maisons Rouges a Nonancourt "
           "(27320), dans l'Eure. Toiture, charpente, zinguerie, isolation, nettoyage et "
           "demoussage. 14 ans d'experience, depannage 24 h/24, devis gratuit.", "",
           "- Telephone : 06 24 59 26 77",
           "- Adresse : 577A les maisons rouges, 27320 Nonancourt, France",
           "- Horaires : tous les jours de 8 h a 21 h, depannage 24 h/24",
           "- Zone : Eure (27) et Eure-et-Loir (28), autour de Nonancourt, Dreux, "
           "Verneuil d'Avre et d'Iton et Evreux", "",
           "## Prestations", ""]
    llm += [f"- [{x['nav']}]({DOMAIN}/{x['slug']}/) : {x['pitch']}" for x in SERVICES]
    llm += ["", "## Communes", ""]
    llm += [f"- [Couvreur a {x['ville']}]({DOMAIN}/{x['slug']}/) : {x['ville']} ({x['cp']}, "
            f"{x['dep']})" + (f", a {x['km']} km de l'atelier" if x["km"] else ", siege de l'entreprise")
            for x in VILLES]
    llm += ["", "## Guides", ""]
    llm += [f"- [{x['nav']}]({DOMAIN}/guides/{x['slug']}/) : {x['desc']}" for x in GUIDES]
    llm += ["", "## Autres communes desservies", "", ", ".join(ZONE_PLUS), ""]
    write(os.path.join(ROOT, "llms.txt"), "\n".join(llm))

    # anciennes URLs WordPress indexées -> nouvelles pages
    R = [("/qui-sommes-nous-trvaux-de-toiture-nonancourt/", "/#maison"),
         ("/couvertures-charpentes-nonancourt/",            "/renovation-toiture/"),
         ("/zinguerie-isolation-nonancourt/",               "/zinguerie-gouttieres/"),
         ("/nettoyage-nonancourt/",                         "/demoussage-toiture/"),
         ("/photos-travaux-de-toiture-nonancourt/",         "/#chantiers"),
         ("/contact-travaux-de-toiture-nonancourt/",        "/#devis")]
    write(os.path.join(ROOT, "_redirects"),
          "".join(f"{a}  {b}  301\n" for a, b in R))
    write(os.path.join(ROOT, ".htaccess"),
          "RewriteEngine On\n"
          + "".join(f'RewriteRule ^{a.strip("/")}/?$ {b} [R=301,L]\n' for a, b in R)
          + "\nErrorDocument 404 /404.html\n"
          "\n<IfModule mod_headers.c>\n"
          "  Header always set X-Content-Type-Options nosniff\n"
          "  Header always set X-Frame-Options SAMEORIGIN\n"
          "  Header always set Referrer-Policy strict-origin-when-cross-origin\n"
          "  <FilesMatch \"\\.(woff2|avif|webp)$\">\n"
          "    Header set Cache-Control \"public, max-age=31536000, immutable\"\n"
          "  </FilesMatch>\n"
          "</IfModule>\n")

    sync_home()
    print(f"{len(SERVICES)} services + {len(VILLES)} communes + {len(GUIDES)} guides + 1 hub")
    print("sitemap.xml, robots.txt, llms.txt, _redirects, .htaccess")
    version_assets()


def bloc_gtag():
    """La balise Google Ads, identique a celle que head() pose sur les pages
    generees. L'accueil et les mentions legales s'editant a la main, elle est
    reinjectee ici a chaque build : sans ca, la page la plus importante du
    site, celle ou atterrit la publicite, ne compte aucune conversion."""
    return (
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={ADS_GTAG}"></script>\n'
        '<script>\n'
        'window.dataLayer = window.dataLayer || [];\n'
        'function gtag(){dataLayer.push(arguments);}\n'
        "gtag('consent', 'default', {\n"
        "  ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',\n"
        "  analytics_storage: 'denied', wait_for_update: 500\n"
        '});\n'
        "gtag('set', 'url_passthrough', true);\n"
        "gtag('set', 'ads_data_redaction', true);\n"
        "gtag('js', new Date());\n"
        f"gtag('config', '{ADS_GTAG}');\n"
        '// app.js lit ces etiquettes : build.py reste le seul endroit qui les definit.\n'
        f"window.WM_CONV = {{devis:'{ADS_GTAG}/{ADS_CONV_DEVIS}', appel:'{ADS_GTAG}/{ADS_CONV_APPEL}'}};\n"
        '</script>')


def poser_gtag(html):
    """Remplace le bloc s'il est deja la, l'insere avant le JSON-LD sinon."""
    import re
    bloc = bloc_gtag()
    motif = re.compile(
        r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=[^"]*"></script>\s*'
        r'<script>.*?</script>', re.S)
    if motif.search(html):
        return motif.sub(lambda _: bloc, html, count=1)
    if '<script type="application/ld+json">' in html:
        return html.replace('<script type="application/ld+json">',
                            bloc + '\n<script type="application/ld+json">', 1)
    # Les mentions legales n'ont pas de JSON-LD : </head> existe partout.
    return html.replace('</head>', bloc + '\n</head>', 1)


def sync_home():
    """L'accueil s'edite a la main, sauf les ilots regeneres ici : le JSON-LD,
    l'index des communes, la grille des prestations et le pied de page."""
    global PRE
    import re
    path = os.path.join(ROOT, "index.html")
    html = open(path).read()

    faq_home = [
        ("Le devis est-il vraiment gratuit ?",
         "Oui. Nous venons voir le toit, nous montons si besoin, et nous vous remettons un prix "
         "detaille. Sans engagement."),
        ("Peut-on payer en plusieurs fois ?",
         "Oui. L'echelonnement suit l'avancement du chantier, et il est ecrit sur le devis."),
        ("Vous intervenez la nuit ?",
         "Oui, pour les urgences. Nous mettons d'abord hors d'eau, puis nous revenons faire la "
         "reparation definitive au calme."),
        ("Tuile, ardoise ou acier : vous faites les trois ?",
         "Oui, plus la charpente, la zinguerie, l'isolation et le bardage. Nous ne sous-traitons "
         "pas la couverture."),
        ("Tous les combien faut-il demousser ?",
         "Un controle chaque annee, un demoussage tous les trois a cinq ans. C'est ce qui coute "
         "le moins cher sur la vie du toit."),
    ]
    faq_ld = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (jstr(q), jstr(a)) for q, a in faq_home)
    ld = ('{"@context":"https://schema.org","@graph":[' + ld_business() + ','
          '{"@type":"WebSite","@id":"%s/#site","url":"%s/","name":"WM Couverture",'
          '"inLanguage":"fr-FR","publisher":{"@id":"%s/#business"}},'
          '{"@type":"WebPage","@id":"%s/#home","url":"%s/","isPartOf":{"@id":"%s/#site"},'
          '"about":{"@id":"%s/#business"},"name":"Couvreur a Nonancourt (27) et Dreux (28)"},'
          '{"@type":"FAQPage","mainEntity":[%s]}]}'
          % (DOMAIN, DOMAIN, DOMAIN, DOMAIN, DOMAIN, DOMAIN, DOMAIN, faq_ld))
    html = re.sub(r'<script type="application/ld\+json">.*?</script>',
                  '<script type="application/ld+json">%s</script>' % ld, html, count=1, flags=re.S)

    # index des communes : lien vers la page dediee quand elle existe
    linked = {v["ville"]: v["slug"] for v in VILLES}
    order = [v["ville"] for v in VILLES] + ZONE_PLUS_ACCENTS
    li = "".join(
        (f'<li><a href="{linked[c]}/">{c}</a></li>' if c in linked else f'<li>{c}</li>')
        for c in order)
    html = re.sub(r'<ol class="zone__index([^"]*)"([^>]*)>.*?</ol>',
                  lambda m: f'<ol class="zone__index{m.group(1)}"{m.group(2)}>\n        {li}\n      </ol>',
                  html, count=1, flags=re.S)

    # barre de navigation et tiroir : l'accueil en gardait une copie figee a
    # quatre prestations sur neuf et six communes sur douze, alors que nav()
    # les genere depuis les donnees. Meme derive que le pied de page.
    keep, PRE = PRE, ""
    barre = nav()
    PRE = keep
    # nav() sert les pages internes : fond opaque au repos et marque pointant
    # vers la racine. L'accueil veut la barre transparente sur la photo et un
    # retour en haut de page.
    barre = barre.replace('class="nav nav--solid"', 'class="nav"', 1)
    barre = barre.replace('<a class="brand" href=""', '<a class="brand" href="#top"', 1)
    # nav() ne connait pas les ancres propres a l'accueil : on les remet
    # derriere « Chantiers », sinon « La maison » et « Avis » disparaissent.
    barre = re.sub(r'(<a href="#chantiers"[^>]*>Chantiers</a>)',
                   r'\1<a href="#maison">La maison</a><a href="#avis">Avis</a>',
                   barre, count=1)
    i = html.index('<header class="nav')
    j = html.index('<main id="main">')
    html = html[:i] + barre.strip() + "\n\n" + html[j:]

    # prestations : la grille des neuf services, regeneree pour rester en phase
    keep, PRE = PRE, ""
    grille = services_grid()
    PRE = keep
    html = re.sub(r'<section class="services".*?</section>',
                  lambda m: grille, html, count=1, flags=re.S)

    # pied de page : regenere depuis foot() pour qu'il ne derive plus quand on
    # ajoute une prestation, une commune ou un guide (il en manquait cinq).
    keep, PRE = PRE, ""
    footer = foot()
    PRE = keep
    footer = footer[:footer.index("</footer>") + len("</footer>")]
    html = re.sub(r'<footer class="foot">.*?</footer>',
                  lambda m: footer, html, count=1, flags=re.S)
    # La section avis et la citation viennent d'avis.json : le nombre d'avis
    # ne doit exister qu'a un seul endroit, sinon il se perime par morceaux.
    html = re.sub(r'<section class="avis" id="avis">.*?</section>',
                  lambda m: bloc_avis(), html, count=1, flags=re.S)
    v = avis_vedette()
    html = re.sub(r'(<blockquote class="reveal">\s*<span class="quote__mark"[^>]*>[^<]*</span>).*?(</blockquote>)',
                  lambda m: m.group(1) + "\n      " + citation_html(v) + "\n    " + m.group(2),
                  html, count=1, flags=re.S)
    html = re.sub(r'(<p class="quote__by reveal" data-d="1">)[^<]*(<span>)',
                  lambda m: m.group(1) + v["auteur"] + " " + m.group(2),
                  html, count=1)

    # La note Google remonte avant les boutons, et quitte la liste du bas :
    # la repeter deux fois dans le meme ecran l'affaiblit au lieu de l'appuyer.
    html = re.sub(r'\s*<p class="hnote[^"]*"[^>]*>.*?</p>', "", html, flags=re.S)
    html = re.sub(r'(</p>\s*)(<div class="hero__cta)',
                  lambda m: "</p>\n\n    " + hero_note(sombre=True) + "\n\n    " + m.group(2),
                  html, count=1, flags=re.S)
    html = re.sub(r'\s*<li><span class="stars stars--big"[^>]*>.*?avis Google</li>',
                  "", html, count=1, flags=re.S)

    # Le lien carte de l'accueil pointait encore sur l'ancienne adresse alors
    # que le texte affichait la bonne : l'un ouvrait Route de Saint-Remy,
    # l'autre annoncait les maisons rouges.
    html = re.sub(r'https://www\.google\.com/maps/search/\?api=1&query=[^"]*',
                  lambda m: MAPS.replace("&", "&"), html)

    # Derniere mention du nombre d'avis ecrite en dur dans l'accueil.
    html = re.sub(r'<b>\d+ avis, [\d,]+ sur 5</b>',
                  lambda m: f'<b>{AVIS_TOTAL} avis, {note_fr()} sur 5</b>', html)

    html = poser_gtag(html)
    open(path, "w").write(html)

    # Les mentions legales s'editent aussi a la main. Faible trafic, mais un
    # visiteur qui y passe puis appelle doit etre compte comme les autres.
    for nom in ("mentions-legales.html", "politique-de-confidentialite.html"):
        f = os.path.join(ROOT, nom)
        if not os.path.exists(f):
            continue
        contenu_f = open(f).read()
        open(f, "w").write(poser_gtag(contenu_f))

    ml = os.path.join(ROOT, "mentions-legales.html")
    if False:
        # Lire AVANT d'ouvrir en ecriture : en une seule expression, Python
        # evalue open(ml, "w") d'abord, ce qui vide le fichier, et la lecture
        # qui suit ne renvoie plus rien.
        contenu = open(ml).read()
        open(ml, "w").write(poser_gtag(contenu))


if __name__ == "__main__":
    main()
