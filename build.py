#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les pages internes de wm-couverture.fr (services + communes),
le sitemap, le robots.txt et les règles de redirection 301.

    python3 build.py

L'accueil (index.html) n'est PAS généré : il s'édite à la main.
Les pages produites ne s'éditent jamais directement, elles sont écrasées.
"""
import os, re, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
PRE = "../"   # prefixe vers la racine, ajuste selon la profondeur de la page

# ─────────────────────────────────────────────────────────── constantes ────
TEL_TXT   = "06 24 59 26 77"
TEL_HREF  = "+33624592677"
DOMAIN    = "https://www.wm-couverture.fr"
ADDR      = "Route de Saint-Remy, 27320 Nonancourt"
W3F_KEY   = "REMPLACER_PAR_VOTRE_CLE_WEB3FORMS"
MAPS      = "https://www.google.com/maps/search/?api=1&query=Route+de+Saint-Remy+27320+Nonancourt"
# Coordonnees a caler EXACTEMENT sur l'epingle de la fiche Google avant mise en ligne.
GEO_LAT   = "48.76950"
GEO_LON   = "1.20870"
PRICE     = "$$"
# URL de la fiche Google, du Facebook, etc. Laisser vide tant qu'on ne les a pas :
# une URL fausse dans sameAs fait plus de mal que pas de sameAs du tout.
SAMEAS    = []
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

AVIS = [
    ("André Y.", "Un grand merci à Monsieur Mouche pour son approche commerciale et son sens du "
                 "service. Pour une réparation de gouttières et une fuite de cheminée, une réalisation "
                 "de devis ultra rapide, suivie d'une intervention dans un délai très court."),
    ("Joy L.",   "Nous sommes très satisfaits de leur travail. Entreprise sérieuse et ponctuelle. "
                 "C'est comme si nous avions un toit neuf."),
    ("Abiba B.", "Super travail. Très professionnel et surtout tout est bien expliqué. On comprend "
                 "tout, même si on n'est pas du métier."),
    ("Anne D.",  "Efficacité, professionnalisme, qualité du travail, devis rapide. Je recommande "
                 "sans hésiter WM Couverture."),
]

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
        h1=("Zinguerie <em>&amp;</em> gouttières", "dans l'Eure et le Drouais"),
        title="Zinguerie et gouttières · Nonancourt, Dreux · WM Couverture",
        desc="Pose et réparation de gouttières, chéneaux, descentes et solins à Nonancourt, Dreux et Anet. Nettoyage de chéneaux, isolation. Devis gratuit.",
        hero="zinguerie-descente-gouttiere-zinc.webp",
        heroalt="Descente de gouttière en zinc le long d'un débord de toiture",
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
        h1=("Nettoyage <em>&amp;</em> démoussage", "de toiture dans l'Eure"),
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
         desc="WM Couverture est installée route de Saint-Remy à Nonancourt. Rénovation de "
              "toiture, charpente, zinguerie et démoussage dans le bourg et les hameaux alentour.",
         intro="C'est notre commune. L'atelier est route de Saint-Remy, et une bonne partie de "
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
        img="chantier-charpente-ecran-sous-toiture.webp", imgalt="Chantier de réfection : charpente et écran de sous-toiture posés",
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
        img="tuiles-neuves-alignees.webp", imgalt="Tuiles neuves alignées sur une couverture refaite",
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
        img="toiture-tuile-rouge-motif.webp", imgalt="Toiture en tuile rouge, motif régulier",
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
        img="toiture-tuile-lumiere-rasante.webp", imgalt="Toiture en tuile éclairée en lumière rasante",
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
        img="tuiles-mousse-vegetation.webp", imgalt="Mousse installée sur une couverture mal entretenue",
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


def page_hero(eyebrow, h1a, h1b, lead, img, alt):
    return f"""<section class="phero">
  <div class="wrap phero__grid">
    <div>
      <p class="eyebrow reveal">{eyebrow}</p>
      <h1 class="reveal" data-d="1">{h1a}<br>{h1b}</h1>
      <p class="phero__lead reveal" data-d="2">{lead}</p>
      <div class="phero__cta reveal" data-d="3">
        <a class="btn btn--dark" href="#devis">Demander mon devis gratuit</a>
        <a class="btn btn--ghost" href="tel:{TEL_HREF}" data-track="call">{PHONE}{TEL_TXT}</a>
      </div>
    </div>
    <figure class="frame phero__img reveal" data-d="2">
      <img src="{PRE}assets/img/{img}" alt="{alt}" width="1600" height="1200" fetchpriority="high" decoding="async">
    </figure>
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


def avis_pair(a, b):
    def q(n, t):
        return (f'<figure class="avis__q reveal"><blockquote>{t}</blockquote>'
                f'<figcaption>{n} <span>avis Google</span></figcaption></figure>')
    return f"""<section class="avis">
  <div class="wrap">
    <header class="avis__head"><h2 class="reveal">Ce que disent <em>les clients</em></h2>
      <p class="reveal" data-d="1"><span class="stars stars--big" aria-hidden="true">★★★★★</span>
        Cinq avis publiés sur notre fiche Google.</p></header>
    <div class="avis__grid avis__grid--pair">{q(*a)}{q(*b)}</div>
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
      <input type="hidden" name="subject" value="Nouvelle demande de devis · wm-couverture.fr">
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
      <a href="{MAPS}" target="_blank" rel="noopener">Route de Saint-Remy<br>27320 Nonancourt</a>
      <span>Tous les jours 8 h à 21 h<br>Dépannage 24 h/24</span>
    </div>
  </div>
  <div class="wrap foot__bar">
    <p>© <span id="year">2026</span> WM Couverture. Tous droits réservés.</p>
    <p><a href="{PRE}plan-du-site/">Plan du site</a> <span aria-hidden="true">·</span> <a href="{PRE}mentions-legales.html">Mentions légales</a></p>
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
            '"foundingDate":"2011","knowsLanguage":"fr-FR"%s,'
            '"address":{"@type":"PostalAddress","streetAddress":"Route de Saint-Remy",'
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
        page_hero("Prestation", s["h1"][0], s["h1"][1], s["lead"], s["hero"], s["heroalt"]),
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


def render_ville(v):
    canon = v["slug"] + "/"
    dist = ("notre atelier" if v["km"] is None else f"à {v['km']} km de l'atelier")
    autour = "".join(f"<li>{c}</li>" for c in v["autour"])
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

    secs = "".join(
        '<section class="prose__s reveal"><h2>%s</h2><div class="prose__b">%s</div></section>'
        % (t, "".join("<p>%s</p>" % x.replace("{PRE}", PRE) for x in ps))
        for t, ps in g["sections"])
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
        head("Plan du site · WM Couverture",
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
    items = "".join(
        f'<li class="reveal" data-d="{min(i,3)}"><a href="{PRE}guides/{g["slug"]}/">'
        f'<b>{g["nav"]}</b><span>{g["desc"]}</span>{ARROW}</a></li>'
        for i, g in enumerate(GUIDES))
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
    <ul class="svc__list hub__list">{items}</ul>
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
           "> Entreprise familiale de couverture installee route de Saint-Remy a Nonancourt "
           "(27320), dans l'Eure. Toiture, charpente, zinguerie, isolation, nettoyage et "
           "demoussage. 14 ans d'experience, depannage 24 h/24, devis gratuit.", "",
           "- Telephone : 06 24 59 26 77",
           "- Adresse : Route de Saint-Remy, 27320 Nonancourt, France",
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


def sync_home():
    """L'accueil s'edite a la main, sauf deux ilots regeneres ici :
    le JSON-LD et l'index des communes (pour que le maillage reste juste)."""
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
    open(path, "w").write(html)


if __name__ == "__main__":
    main()
