# Projet APWorld BIS

Développement d'un APWorld Archipelago pour Mario & Luigi : Voyage au
Centre de Bowser, version NDS de 2009. **La boucle complète tourne**,
validée en jeu le 5 août 2026 : 21 checks remontés, 21 items renvoyés,
vus à l'écran. Le monde vit dans `mlbis/` : **725 `location`**, 647
trésors et 78 pièces d'attaque, 16 `region`, et depuis le 7 août une
**logique**, neuf capacités en items de progression. Trois suites de
tests, `tools/test_generation.py`, `test_client.py`, et
`test_archipelago.py` qui passe les 206 tests généraux d'Archipelago.

## Version de ROM, figée

Ne jamais raisonner sur une autre version.

- Mario & Luigi Bowser's Inside Story, NDS, région NA, révision pre-DSi
- SHA-256 `9126963d6c6b6f81a9a666ba766e223781ff286634486e2a56d07a4c82eef4f1`
- Deux sources concordantes, `randoglobin/main.py` lignes 189 à 196 et
  `inf.gg/mlbis/manual` section Known ROMs. Le `.nds` de ce dossier a
  été rehashé le 2 août 2026 et correspond
- Non moddée

Tout offset, adresse ou structure se rapporte à cette révision. Si une
source parle d'une autre région, le signaler au lieu de transposer.

## Ne pas toucher à la ROM

- Ne jamais chercher, télécharger ou proposer de télécharger une ROM
- Ne pas copier, déplacer ou modifier le fichier `.nds` présent dans ce
  dossier sans demande explicite

## Règle la plus importante

Ne jamais inventer une adresse mémoire, un offset, un identifiant
d'item interne, une structure de sauvegarde ou un nom de fonction du
jeu. Une valeur plausible mais fausse coûte des heures de debug.

Étiqueter systématiquement ce qui est avancé :

- **Vérifié** : lu dans le code source ou la doc, avec fichier et ligne
- **Hypothèse** : déduit d'un autre jeu ou d'un pattern, à confirmer
- **À tester** : rien ne permet de trancher

Sans source précise au niveau du fichier et de la ligne, c'est une
hypothèse, pas un fait. Quand l'information manque, le dire et proposer
comment l'obtenir.

## Versions d'outils, non négociables

**Python 3.13** et **BizHawk 2.10 exactement**, jamais la dernière
version publiée. Le pourquoi de chaque borne est dans
`installation-apworld-bis.md`, il n'a pas à être relu à chaque session.

## Licences

**Vérifié** le 3 août 2026, détail et attributions dans `SOURCES.md`.
Randoglobin et Cheatoglobin **GPL-3.0-or-later**, les lire est libre mais
en recopier contaminerait l'APWorld ; `mnllib.py` **LGPL-3.0**, donc
utilisable comme dépendance, pas à recopier ; BIS-docs **GPL-3.0** et sa
doc **CC BY-SA 4.0**, qui impose l'attribution ; Archipelago **MIT**.
Signaler l'implication dès qu'il est question de réutiliser.

## Contraintes d'empaquetage APWorld

Cinq pièges dont le message d'erreur ne pointe pas vers la vraie cause,
dans `empaquetage-apworld.md`. À relire avant le premier empaquetage.

## Piège de logique connu

Si une règle d'accès lit l'accessibilité d'une autre région, enregistrer
`multiworld.register_indirect_condition` : Archipelago n'évalue chaque
transition qu'une fois, et une transition évaluée trop tôt reste
infranchissable sans être réévaluée. Nos règles actuelles ne lisent que
des items, donc le piège ne se pose pas encore.

## Méthode de travail

- Préférer la plus petite étape testable au plan complet
- Pour chaque hypothèse, proposer le test qui la ferait tomber, pas
  seulement celui qui la confirmerait
- Décrire concrètement les manipulations dans BizHawk ou dans le jeu,
  pas en principe
- Répondre en français, garder les termes techniques anglais tels quels
  (`region`, `access_rule`, `location`, `item`, `apworld`)

## Tenue de ce fichier

Ce fichier est la mémoire du projet, pas un journal. Il est relu à
chaque session, donc il doit rester court pour rester utile.

Le mettre à jour sans attendre qu'on le demande, dès qu'un de ces
événements se produit :

- Une adresse, un offset ou une structure est confirmée par un test
- Une décision est figée : version, choix technique, convention de
  nommage
- Une source se révèle périmée ou fausse
- Un point de la section « Non résolu » est résolu
- Une étape du projet est franchie et change ce qui est vrai

Comment le faire :

- Écrire dans la section qui convient, pas à la fin du fichier
- Une ou deux lignes par acquis, avec statut et source, fichier et ligne
- Retirer ce que le nouvel acquis rend faux, ne pas empiler
- Le signaler dans la réponse en montrant la ligne ajoutée

Ne pas écrire ici, mais dans `JOURNAL.md`, qui n'est pas chargé
automatiquement : le récit d'une session, les pistes sans conclusion, les
erreurs de manipulation et leurs corrections, les commandes tapées. Y
écrire librement, en datant chaque entrée.

Plafond de 220 lignes. S'il est dépassé, le signaler et proposer ce qui
peut en sortir plutôt que d'ajouter.

## Sources, du plus fiable au moins fiable

URL, commits consultés, licences et attributions : `SOURCES.md`.
Ordre de fiabilité à respecter, du plus sûr au moins sûr :
`vendor/Archipelago/worlds/mlss`, l'APWorld Superstar Saga livré dans le
cœur d'Archipelago, modèle de référence dépouillé dans
`reference-mlss.md` ; la doc Archipelago ; un APWorld NDS existant,
Pokémon Mystery Dungeon ou Black and White ; l'écosystème MnL-Modding,
ses outils puis sa documentation, dont `inf.gg/mlbis/manual` en CC0 ;
enfin les discussions communautaires, à traiter comme des pistes.

## Acquis à ne pas redécouvrir

- **Les capacités sont des `item`**, décidé le 7 août 2026. Marteau,
  Drill Bros, vacuum, Bros Attacks entrent dans la pool et se livrent par
  un bit. Deux conséquences : il faut de vraies `access_rule`, et
  `FIRE_BREATH_DISABLED` se livre en **abaissant** son bit, pas en le
  levant. `0x2000` est un état, pas un déblocage, il ne peut pas servir
  de prérequis : Mario prend la forme miniature où il veut, à volonté
- **Commandes de script** : table dans `overlay_0006.bin`, plage
  commune, commandes d'objets `0x0043` et `0x0044`, injection ARM.
  Détail et sources dans `formats-bis.md`

### Structures confirmées, détail dans `formats-bis.md`

- **Sauvegarde** : magie `MLRPG3`, deux slots à `0x0010` et `0x0FE8`.
  Le slot porte un checksum sur ses `0x5F2` premiers octets et une
  copie de secours à `slot + 0x7EC`. **Toute écriture doit recalculer
  le checksum et répliquer la copie**, sinon le slot est rejeté. Le
  tableau `Exxx` y est copié à `slot + 0x01B4`, mesuré. Ne pas y
  recopier la RAM telle quelle : la sauvegarde porte un bit de plus
- **Locations candidates** : `Treasure/TreasureInfo.dat`, entrées de
  12 octets, **647 exploitables** dont 281 blocs `?` et 197 haricots.
  Les octets 4-5 portent un identifiant unique de 0 à 757, qui est le
  rang du bit de flag. Numéro de `location` naturel
- **Flags** : dans `Exxx`, les trésors partent de `0xE000`, les ennemis
  de `0xE400`, l'histoire de `0xE700`. Les `0x2xxx` sont 64 bits, à
  `02056038` en RAM et à `slot + 0x0124` dans la sauvegarde
- **Capacités et Bros Attacks** : le champ `2xxx` est l'`ImportantFlags`
  de mnllib, `bis/consts.py:46-93`. Marteau, Drill Bros, badges, les dix
  Bros Attacks. **Livrer une capacité est acquis**, 5 août 2026 : le bit
  `0x2019` levé à `0205603B` fait apparaître Fire Flower au menu, elle se
  joue en entier, démonstration comprise, sans sa cinématique
  d'apprentissage. Les dix `0x2010` à `0x201B` recoupent la ROM sur 10/10
- **Retirer une capacité marche**, 7 août 2026, à la main puis **par le
  client en session réelle** : huit capacités non reçues reprises d'un
  coup, marteau absent jusque dans le menu de combat. C'est ce qui rend
  une capacité échangeable sans patcher la ROM
- **Où une capacité est octroyée**, 7 août 2026 : un script `FEvent`,
  commande `0x0008` valeur 1, et **l'index de chunk est l'index de
  carte**, 681 des deux côtés. 29 capacités ont une salle unique. Le
  drapeau est posé là où est **Bowser**, pas où combattent les frères
- **Écrire quand on veut** : en combat comme sur le terrain, l'écriture
  prend effet, s'affiche et survit, 4 août 2026. Cinématiques non testées
- **Inventaire vivant** à `02056400` : pièces en `u32`, consommable `N`
  à `02056406 + N`, équipement d'identifiant `I` à `02056427 + I - 1`,
  127 compteurs pour les identifiants 1 à 127. `slot + 0x0054 + X`
  correspond à `02056400 + X + 2`. **Livrer un objet est acquis** :
  un Nut à `02056406 + 7` le 4 août 2026, un Heart Wear au compteur 4
  le 5 août, tous deux vus au menu. Pièces de même, 999 sauvegardé
- **Identifiants de location**, à figer avant la première seed publiée :
  `BASE_ID = 0xB15000`, location d'un trésor = `BASE_ID + identifiant`,
  qui est aussi son rang de bit dans `Exxx`. `BASE_ID + 1024` et au-delà
  réservés aux locations hors `TreasureInfo.dat`
- **Zones** : 32 nommées dans `mfset_EMesPlace.dat`, table `0x44` pour
  l'anglais, dont **16 portent des trésors**. La chaîne trésor → carte →
  zone est établie, `tools/build_salles_zones.py`. Notre découpage en
  salles est en bijection avec les cartes du jeu. Ce sont les `region`

### Tables déjà extraites, dans `data/`

Régénérables par le script de `tools/` qui porte le même thème, dans le
venv `venv/` de la racine : `locations_bis.csv` les 685 entrées de
trésor, `noms_zones.csv` les 32 zones, `bros_attacks.csv` les 10
attaques, `pieces_attaque.csv` 78 pièces sur 100, `capacites_fevent.csv`
les 48 variables `2xxx` avec leur salle et leur zone d'octroi. Enfin
`noms_items.csv`, 191 objets, dont l'identifiant indexe une table de
l'arm9 décompressé et non la table de texte, corrigé le 4 août 2026.

## Non résolu

- **Le drapeau de fin d'histoire reste introuvable.** L'unique combat
  marqué `final battle`, chunk 557, n'écrit que des variables génériques.
  Le but est donc « réunir les neuf capacités », lu dans `items_received`
  sans adresse mémoire. Le vrai but attend une lecture du code ARM, dont
  l'entrée est trouvée : pools littéraux, `capstone`, `formats-bis.md`
- **Multiworld et reconnexion acquis**, 8 août 2026 : reçu d'un autre
  monde, envoyé vers lui, checks ramassés client fermé envoyés à la
  reconnexion, rien de redonné. **Reste** : une partie jouée dans la
  durée, et le rechargement d'un savestate, défectueux par construction
- Les `access_rule` existent depuis le 7 août : une zone de rang `r`
  exige les capacités octroyées avant elle, `data/ordre_zones.csv`.
  **L'ordre vient d'un guide**, rangs 11 à 16 marqués faibles, et le
  journal en jouant est ce qui les confirmera. Manque le prérequis d'un
  trésor donné : aucun bloc ne lit de capacité dans `FEvent`, c'est ARM
- 22 pièces d'attaque sans variable connue : Jump Helmet 8, Super
  Bouncer 4, Yoo Who Cannon 10 qui est octroyée d'un bloc et n'est donc
  pas une `location`. Absentes de `FEvent` et des scripts de combat, à
  mesurer en jeu
- Aucune `region` pour une pièce d'attaque : les sous-routines de bloc
  sont dupliquées dans 13 ou 18 chunks, la salle n'est pas exploitable.
  Le nom du lot, `Trash Pieces`, donne la zone du set
- Trésors hors `TreasureInfo.dat` : **un achat en boutique ne laisse
  aucun drapeau**, mesuré le 7 août 2026, donc il ne peut pas être une
  `location` sans patcher la ROM. Restent les quêtes
