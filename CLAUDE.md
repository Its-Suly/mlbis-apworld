# Projet APWorld BIS

Développement d'un APWorld Archipelago pour Mario & Luigi : Voyage au
Centre de Bowser, version NDS de 2009. Faisabilité acquise : lecture des
checks, écriture d'items et sauvegarde vérifiées. Le monde vit dans
`mlbis/` : 647 `location`, 16 `region`, un client BizHawk en lecture
seule, **validé en jeu le 4 août 2026**, les checks remontent au serveur.
Tests `tools/test_generation.py` et `tools/test_client.py`.

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

**Vérifié** dans les fichiers `LICENSE` des dépôts, le 3 août 2026.
Détail et attributions dans `SOURCES.md`.

- Randoglobin et Cheatoglobin : **GPL-3.0-or-later**. Les lire est
  libre, en recopier du code imposerait la GPL à l'APWorld
- `mnllib.py` : **LGPL-3.0**, donc utilisable comme dépendance sans
  contaminer l'APWorld. C'est déjà le cas dans `tools/extract_names.py`
- BIS-docs : **GPL-3.0** pour le code, **CC BY-SA 4.0** pour la
  documentation, qui impose l'attribution
- Archipelago : **MIT**

Signaler l'implication dès qu'il est question de réutiliser plutôt que
de s'inspirer.

## Contraintes d'empaquetage APWorld

Cinq pièges dont le message d'erreur ne pointe pas vers la vraie cause,
dans `empaquetage-apworld.md`. À relire avant le premier empaquetage.

## Piège de logique connu

Si une règle d'accès de transition dépend de l'accessibilité d'une
autre région, enregistrer une condition indirecte avec
`multiworld.register_indirect_condition`. Archipelago n'évalue chaque
transition qu'une fois pendant le parcours du graphe, et une transition
évaluée trop tôt sera considérée comme infranchissable sans jamais être
réévaluée. Ce cas est probable sur BIS, où l'accès d'un duo dépend
souvent de la progression de l'autre.

## Particularités du jeu

- Deux équipes, Mario-Luigi et Bowser, avec inventaires et capacités
  distincts. Plusieurs structures à suivre, pas une seule
- **Écrire un compteur d'inventaire pendant un combat est sans risque et
  survit à la sortie**, vérifié le 4 août 2026. Les cinématiques ne sont
  pas testées : y écrire reste à considérer comme dangereux

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
- Une ou deux lignes par acquis, avec l'étiquette de statut et la
  source au niveau du fichier et de la ligne
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
- **Inventaire vivant** à `02056400` : pièces en `u32`, consommable `N`
  à `02056406 + N`, équipement `M` à `02056427 + M`. `slot + 0x0054 + X`
  correspond à `02056400 + X + 2`. **Livrer un objet est acquis**,
  4 août 2026 : un Nut écrit à `02056406 + 7` apparaît au menu et se
  consomme normalement, un seul octet touché sur les 164 du bloc.
  Pièces de même, 999 écrit puis sauvegardé
- **Identifiants de location**, à figer avant la première seed publiée :
  `BASE_ID = 0xB15000`, location d'un trésor = `BASE_ID + identifiant`,
  qui est aussi son rang de bit dans `Exxx`. `BASE_ID + 1024` et au-delà
  réservés aux locations hors `TreasureInfo.dat`
- **Écarté** : `EObjSave/EObjSave.dat` ne contient que des palettes,
  pas d'état de sauvegarde
- **Zones** : 32 nommées dans `mfset_EMesPlace.dat`, table `0x44` pour
  l'anglais, dont **16 portent des trésors**. La chaîne trésor → carte →
  zone est établie, `tools/build_salles_zones.py`. Notre découpage en
  salles est en bijection avec les cartes du jeu. Ce sont les `region`

### Tables déjà extraites, dans `data/`

Régénérables par `tools/extract_names.py` puis
`tools/build_location_table.py`, dans le venv `venv/` de la racine.

- `locations_bis.csv` : les 685 entrées de trésor décodées, avec
  identifiant, type, objet nommé, quantité, salle et coordonnées
- `noms_items.csv` : 191 objets. L'identifiant indexe une table de
  l'arm9 décompressé, pas la table de texte. Corrigé le 4 août 2026
- `noms_zones.csv` : les 32 zones

## Non résolu

**Le point bloquant est levé, et vérifié.** Les trésors ramassés sont
suivis par les index bas du tableau de bits `Exxx` des variables de
script, 4096 bits, `0x200` octets à `020560C8` en `Main RAM` :

```
bit du trésor d'identifiant N  ->  octet 020560C8 + N // 8, bit N % 8
```

Le tableau vit dans le BSS de l'ARM9, `02055FE0` à `02063B00`, donc à
adresse fixe quelle que soit la salle chargée. Sur un bloc multi-coups,
le bit monte dès la **première** pièce, pas à l'épuisement. Vérifié par
dix dumps du 3 août 2026 et par `inf.gg/mlbis/manual`. Détail dans
`formats-bis.md`.

Restent ouverts, plus rien de bloquant :

- Recevoir les items côté client : `client.py:72` est encore à
  `items_handling = 0b000`, et l'index du dernier item reçu ira dans le
  `DataStorage` du serveur, pas dans la sauvegarde
- Aucune `access_rule` : `mlbis/__init__.py:65` ne pose que la condition
  de victoire, les 16 `region` sont reliées sans exigence
- Trésors hors `TreasureInfo.dat` : boutiques énumérables par
  `MDataShopBuyList.dat`, quêtes à qualifier à la main. **Aucun script ne
  touche `0xE000-0xE3FF`**, donc trancher par breakpoint sur `020560C8`
