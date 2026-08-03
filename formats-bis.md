# Formats internes de BIS

Détail des structures confirmées. Sorti de `CLAUDE.md` le 2 août 2026
pour le garder sous son seuil de 220 lignes. `CLAUDE.md` n'en conserve
que le résumé et pointe ici. Toute nouvelle structure confirmée vient
dans ce fichier ; seule la conséquence pratique remonte dans `CLAUDE.md`.

Étiquettes de statut identiques à celles de `CLAUDE.md` : **Vérifié**
avec fichier et ligne, **Hypothèse**, **À tester**.

Les adresses tirées de `inf.gg/mlbis/manual` valent pour la release NA
`CLJE`, sauf mention contraire du manuel, donc pour notre ROM. Celle-ci
est **confirmée par une deuxième source indépendante** depuis le 3 août
2026 : son SHA-256 `9126963d…eef4f1` figure dans la section Known ROMs du
manuel, sous `CLJE` North America, *not signed*, 128 Mo. Il concordait
déjà avec `randoglobin/main.py` lignes 189 à 196.

## Fichier de sauvegarde

**Vérifié**, source `vendor/Cheatoglobin/cheatoglobin/window.py` :

| Élément | Valeur | Ligne |
|---|---|---|
| Magie | `MLRPG3`, 6 octets en tête de fichier | 97 |
| Slot 1 | offset `0x0010` | 105 |
| Slot 2 | offset `0x0FE8` | 105 |
| Stats des 3 personnages | `slot + 0x0000`, `0x1C` octets chacun | 113 |
| Inventaire | `slot + 0x0054` | 125 |
| Variables globales | `slot + 0x0124`, 8 octets | 142 |
| Checksum | `0xFFFF - (somme de 761 u16 mod 0xFFFF)` en `u16` à `slot + 0x5F2` | 219-221 |
| Copie de secours | `0x5F4` octets répliqués à `slot + 0x7EC` | 226-229 |

Le détail de l'inventaire, ligne 125 à 137 : compte de pièces sur
4 octets, 26 compteurs d'objets, 7 octets sans effet observé, 127
compteurs d'équipement, 1 octet de champ de bits des badges, 3 octets
inconnus, 4 octets de compteur de jeu en frames, 4 octets inconnus,
2 jauges de badge en `u16`, 6 octets inconnus, 20 octets de données
Broque Madame et nœuds de défi, 2 octets inconnus.

Zone non documentée : de `slot + 0x012C` à `slot + 0x05F2`, soit
1222 octets sur lesquels Cheatoglobin ne dit rien. C'est là que doivent
vivre les flags de trésors.

### Sérialisation du bloc des registres globaux, ex-hypothèse H2

**Vérifié par décompilation**, montrée le 3 août 2026 sur le Discord
MnL-Modding par yx (8y8x), auteur du manuel et de `mlbis-dumper`. La
fonction `FUN_overlay_d_129__0206f1f4`, cas 5, enchaîne cinq copies :

```
memCopy32unk(VAR_ARRAY_UNK_2xxx,  param_1 + 0x15c, 8)
memCopy32unk(VAR_ARRAY_UNK_Dxxx,  param_1 + 0x164, 0x88)
memCopy32unk(VAR_ARRAY_gbi_Exxx,  param_1 + 0x1ec, 0x200)
memCopy32unk(VAR_ARRAY_gby_6xxx,  param_1 + 0x3ec, 0x98)
memCopy32unk(&DAT_02056360,       param_1 + 0x484, 0xe)
```

Même ordre et mêmes tailles que le bloc en RAM. En calant sur l'ancre de
Cheatoglobin, `2xxx` à `slot + 0x0124`, il vient `param_1 = slot - 0x38`,
et les cinq offsets se traduisent ainsi :

| Offset dans le slot | Plage | Taille | Décompilé |
|---|---|---|---|
| `slot + 0x0124` | `2xxx` | `0x08` | `param_1 + 0x15c` |
| `slot + 0x012C` | `Dxxx` | `0x88` | `param_1 + 0x164` |
| `slot + 0x01B4` | `Exxx` | `0x200` | `param_1 + 0x1ec` |
| `slot + 0x03B4` | `6xxx` | `0x98` | `param_1 + 0x3ec` |
| `slot + 0x044C` | sans identifiant | `0x0E` | `param_1 + 0x484` |
| `slot + 0x045A` | fin | — | — |

**Les flags de trésors sont donc à `slot + 0x01B4 + N // 8`**, bit
`N % 8`, dans la zone que Cheatoglobin laissait non documentée.

### Confirmé par la mesure, `run11`

Sauvegarde faite en jeu le 3 août 2026 avec le seul trésor 546 ramassé,
puis dump. Les cinq tableaux sont aux cinq offsets prédits, avec les
bonnes tailles :

| Tableau | RAM | Sauvegarde | Résultat |
|---|---|---|---|
| `2xxx` | `0x056038` | `slot + 0x0124` | identique |
| `Dxxx` | `0x056040` | `slot + 0x012C` | identique |
| `Exxx` | `0x0560C8` | `slot + 0x01B4` | un octet d'écart, voir plus bas |
| `6xxx` | `0x0562C8` | `slot + 0x03B4` | identique |
| anonyme | `0x056360` | `slot + 0x044C` | identique |

`tools/compare_block.py` a trouvé l'empreinte à deux endroits, `0x0208`
et `0x09F4`. Le premier place le tableau à `slot 1 + 0x01B4`. Le second
tombe sur la **copie de secours**, `slot + 0x7EC + 0x01B4`, identique à
la principale, ce qui confirme au passage l'offset `0x7EC` de
Cheatoglobin. Le décalage de `0x38` déduit du décompilé était donc juste.

### Tampon de sauvegarde en RAM, **Vérifié**

Trouvé le 3 août 2026 en cherchant dans `Main RAM` l'image de
l'inventaire lue dans la `SRAM` du `run11`. Occurrence **unique** dans
les 4 Mo.

```
tampon de slot en Main RAM : 0x058F94, absolu 02058F94
param_1 du décompilé       : 0x058F5C, absolu 02058F5C  (tampon - 0x38)
```

Le tampon reproduit la structure d'un slot : inventaire à `+0x0054`,
tableau `Exxx` à `+0x01B4`, ce dernier octet pour octet identique à ce
qui part en `SRAM`, bit surnuméraire compris.

**Attention, ce n'est pas l'état de jeu vivant.** Le compteur en tête
d'inventaire reste à zéro du `run06` au `run10` pendant que des pièces
sont ramassées, et ne se remplit qu'au `run11`, après la sauvegarde. Le
tampon n'est peuplé qu'au moment de sauvegarder. Y écrire hors de ce
moment ne changerait rien à la partie et serait probablement écrasé.

Son intérêt est ailleurs : c'est là qu'on pourra observer l'écriture du
bit `0xEB3F` et trancher son origine.

**Non trouvé, à ne pas refaire tel quel** : l'inventaire vivant, celui
que lit et écrit le jeu en cours de partie. Ce qui a été tenté sur les
dumps `run06` à `run11`, qui encadrent la récolte des dix pièces du bloc
546, et qui n'a rien donné :

- image de l'inventaire de la sauvegarde cherchée dans `Main RAM` :
  une seule occurrence, le tampon ci-dessus
- compteur suivant la récolte pièce par pièce, `+8` puis `+9` entre
  `run08`, `run09` et `run10`, en `u16` et `u32` alignés : aucun
- crédit unique de `+10` entre `run07` et `run10`, en `u8`, `u16` et
  `u32`, dans `Main RAM`, `Shared WRAM` et `ARM7 WRAM` : 44 offsets,
  tous écartés. Le seul dans le BSS, `0x056810`, vaut `0` à deux dumps
  et `0xFFFF` en poids fort à d'autres : donnée volatile, pas un
  compteur

Deux pistes restent, dans l'ordre de coût : relever le nombre de pièces
à l'écran pour disposer d'une ancre, ou passer par l'outil RAM Search de
BizHawk, qui filtre sur plusieurs pas successifs là où un diff n'en
compare que deux. À noter aussi que `Instruction TCM` et `Data TCM` ne
sont pas dumpés par `tools/dump_ram.lua`.

### La sauvegarde n'est pas une copie fidèle de la RAM

Un seul écart sur les 906 octets, mais il compte. À `Exxx + 0x167`, la
sauvegarde porte `0x80` là où la RAM est à `0x00`, et l'est restée dans
les six dumps `run06` à `run11`. Il s'agit de l'index 2879, variable
`0xEB3F`, dans la plage histoire.

Deux explications tiennent, **non tranchées** : la routine écrit ce bit
directement dans le tampon de sauvegarde, ou bien le jeu le lève pendant
la boîte de dialogue et le rabaisse avant notre dump. Un dump pris
pendant le dialogue de sauvegarde départagerait les deux.

**Piège** : écrire dans la sauvegarde en y recopiant la RAM telle quelle
effacerait ce bit. À traiter le jour où on touchera au `.sav`, en même
temps que le checksum et la copie de secours.

À noter, la sérialisation ne copie pas le bloc entier : `5xxx` et `Cxxx`,
qui précèdent `2xxx` en RAM, ne figurent pas dans ces cinq copies.

Le code de sauvegarde vit dans les overlays **0, 127 et 129**, et non
dans le seul overlay 0 que retenait le manuel.

## Table des trésors, `Treasure/TreasureInfo.dat`

**Vérifié**, dump du 2 août 2026 avec `tools/dump_treasure.py` et
`tools/analyse_treasure.py` sur la ROM figée.

- 8704 octets, entrées de 12 octets, 725 entrées dans le fichier
- Première entrée entièrement nulle à l'index 685, ce qui borne la table
- Sur ces 685, 38 ont un `item` à 0 et sont ignorées par Randoglobin
- **647 entrées exploitables** : 281 blocs `?`, 197 haricots, 149 blocs
  brique (types 4 et 7 confondus), 20 touffes d'herbe

Structure d'une entrée, six `u16` little-endian :

| Octets | Contenu | Statut |
|---|---|---|
| 0-1 | bitfield | Vérifié |
| 2-3 | `item` | Vérifié |
| 4-5 | identifiant unique du trésor | Hypothèse |
| 6-7 | X | Hypothèse |
| 8-9 | Y | Hypothèse |
| 10-11 | Z | Hypothèse |

Bitfield, source `vendor/Randoglobin/randoglobin/data_classes.py`
lignes 38 à 43 : bit 0 `is_last_entry_in_room`, bits 1 à 4
`treasure_type`, bits 5 à 9 `max_hits`, bits 10 à 14 `quantity`.

`treasure_type` : 0 haricot, 1 bloc `?`, 4 et 7 bloc brique, 5 touffe
d'herbe. Source `vendor/Randoglobin/randoglobin/treasure.py` lignes 328
à 331.

Ce qui fonde l'hypothèse sur les octets 4-5 :

- Valeurs de 0 à 757, 665 distinctes sur 685 entrées
- La seule valeur répétée est 0, et uniquement sur des entrées de
  bourrage à `item` nul. Toutes les autres sont uniques
- L'ordre ne suit pas celui du fichier, donc ce n'est pas l'index
- Randoglobin ne lit jamais ce champ, il ne décode que les 4 premiers
  octets

### Ordre des identifiants, **Vérifié** par `tools/analyse_geographie.py`

Analyse de bureau du 3 août 2026, sans ROM ni émulateur. Elle décide du
choix des cibles de tous les tests en jeu.

**Les identifiants ne suivent pas la géographie.** Toute plage de 64
identifiants se disperse sur l'ensemble de la carte : la plage 0 à 63
touche les salles 0 à 237, la plage 128 à 191 les salles 16 à 182. Il est
donc inutile d'espérer couvrir une plage d'identifiants en restant dans
une zone.

**Mais ils sont groupés par salle en local**, ce qui sauve les tests :

- 184 salles sur 269 ont des identifiants entièrement contigus
- 603 des 646 écarts entre identifiants consécutifs valent 1
- 85 salles sont éclatées en deux paquets ou plus, par exemple la salle
  15 qui porte `31, 34, 35, 36` puis `256, 257, 258, 260`

Le facteur d'ordre visible est le **type de trésor**, en gros et non en
détail : la plage 0 à 63 est à 89 % des blocs `?`, la plage 192 à 255 à
75 % des haricots, la plage 384 à 447 à 76 % des blocs brique. Les salles
éclatées s'expliquent bien par une salle contenant plusieurs types.

Conséquences pratiques :

- Une salle unique fournit plusieurs identifiants consécutifs sans
  déplacement. C'est ce qui a rendu la salle 258 si commode, avec
  `544` à `547`
- Les 85 salles éclatées sont les **meilleures cibles de falsification** :
  elles permettent d'allumer des bits non adjacents sans bouger
- Choisir chaque cible de test dans `locations_bis.csv`, jamais par
  plage d'identifiants

Ce qui fonde l'hypothèse coordonnées sur les octets 6 à 11 : plages
24-1816, 52-1604 et 0-920, très majoritairement multiples de 8, et le
troisième champ n'a que 71 valeurs distinctes, ce qui ressemble à une
hauteur.

## Commandes de script

Sorti de `CLAUDE.md` le 3 août 2026 pour le maintenir sous son seuil de
220 lignes. Rien de tout ceci ne sert avant qu'on touche aux scripts.

**Vérifié** :

- La table des commandes de script vit dans `overlay_0006.bin` à
  l'offset `0x014b08` une fois décompressé. Source : commentaire dans
  `cutscene_code/bisdocs.py` du dépôt MnL-Modding/BIS-docs
- Les commandes `0x0000` à `0x0046` incluses sont communes à tous les
  dialectes de script. Source : BIS-docs, page Getting started
- `0x0043 Get Item Amount` prend un item ID et retourne la quantité
  possédée. `0x0044 Add Items` prend un item ID et une quantité, et
  retourne le nombre réellement ajouté. Source : sortie de
  `bisdocs.py`, entrées 0043 et 0044
- Randoglobin injecte du code ARM custom, il embarque `bis.asm` et un
  binaire pour la cible `armv5te-none-eabi` dans
  `randoglobin/files/bis.zip`, ce qui prouve que ce chemin est
  praticable sur BIS

**Périmé, ne pas s'y fier** : la copie de la doc des commandes présente
sur le Google Drive de MnL-Modding date de septembre 2024. Régénérer
depuis `cutscene_code/bisdocs.py` du dépôt BIS-docs.

## Domaines mémoire BizHawk pour le NDS

**Vérifié** le 3 août 2026, relevé dans la console Lua de BizHawk 2.10
sur la ROM du projet. Répond à la question laissée ouverte par
`reference-mlss.md` : les domaines GBA `EWRAM` et `IWRAM` de Superstar
Saga n'existent pas ici.

| Domaine | Taille |
|---|---|
| `Main RAM` | 4 194 304, soit 4 Mo, confirmé au `run06` |
| `Shared WRAM` | 32 768 |
| `ARM7 WRAM` | 65 536 |
| `SRAM` | 8 192 |
| `ROM` | 134 217 728 |
| `Instruction TCM` | 32 768 |
| `Data TCM` | 16 384 |
| `ARM9 BIOS` | 4 096 |
| `ARM7 BIOS` | 16 384 |
| `Firmware` | 131 072 |
| `ARM9 System Bus` | 0 |
| `ARM7 System Bus` | 0 |
| `Waterbox PageData` | 308 958 |

**Piège vérifié** : `memory.getmemorydomainlist()` est indexée **à partir
de 0** sur ce cœur, contrairement aux tableaux d'octets renvoyés par
`memory.read_bytes_as_array` qui sont indexés à partir de 1. Une boucle
`for i = 1, #liste` saute silencieusement `Main RAM` et retourne une
liste plausible mais amputée.

**Vérifié** le 3 août 2026 : le domaine `SRAM` **est** le fichier de
sauvegarde. Ses 8192 octets contiennent tout juste les 8136 octets
qu'occupe la structure décrite plus haut, jusqu'à
`0x0FE8 + 0x7EC + 0x5F4`. Une sauvegarde faite en jeu au `run11` y a bien
écrit les cinq tableaux de registres et leur copie de secours. La
sauvegarde est donc lisible et modifiable en direct, sans passer par un
fichier `.sav` sur le disque.

## Tables de texte, noms d'objets et de zones

**Vérifié** par inspection le 2 août 2026, pas par déduction. Méthode
reprise de `vendor/Randoglobin/randoglobin/main.py` lignes 960 à 1000 :
`LanguageTable.from_bytes`, puis `.text_tables[i].entries`, chaque
entrée se terminant par `0xFF` et se décodant en `BIS_ENCODING`.

`text_tables` mélange des objets `TextTable` et des `bytes` bruts selon
l'index, donc toujours tester le type avant d'accéder à `.entries`.
Source `vendor/mnllib.py/mnllib/bis/text.py` lignes 100 à 107.

Index de langue, **relevés et non devinés** :

| Fichier | `is_dialog` | Anglais | Français | Espagnol |
|---|---|---|---|---|
| Tables d'objets | `False` | 2 | 3 | 6 |
| `mfset_EMesPlace.dat` | `True` | `0x44` | `0x45` | `0x48` |

Attention, l'anglais est la table **2** et non 1 comme la valeur de
langue de `constants.py` le laisse croire.

Pas entre deux objets, différent selon la table :

| Type | Fichier | Entrées | Pas | Objets |
|---|---|---|---|---|
| 1 attaque | `BData/mfset_AItmN.dat` | 29 | 1 | 29 |
| 2 consommable | `BData/mfset_UItmN.dat` | 78 | 3 | 26 |
| 3 badge | `BData/mfset_BadgeN.dat` | 26 | 3 | 9 |
| 4 équipement | `BData/mfset_WearN.dat` | 420 | 3 | 140 |

Le pas de 3 vient des triplets singulier, pluriel, message « Full! ».
Les 26 consommables correspondent exactement aux 26 compteurs d'objets
de la sauvegarde, ce qui confirme les deux lectures l'une par l'autre.

`mfset_EMesPlace.dat` table `0x44` donne **32 zones**, index 0 valant
`----`. Elles se séparent en deux mondes : index 1 à 12 à l'extérieur,
de `Peach's Castle` à `Trash Pit`, et index 13 à 30 à l'intérieur de
Bowser, de `Funny Bone` à `Chest Station`. Index 31 `Challenge Node`.

## Champ de bits des trésors ramassés

**Vérifié** le 3 août 2026 par trois dumps de `Main RAM` pris avant tout,
après un premier bloc `?`, puis après un second de la même salle.
Protocole et outils dans `tools/dump_ram.lua` et
`tools/cherche_champ_bits.py`.

Un seul octet a changé dans toute la plage `0x056038` à `0x0561D1`, soit
410 octets de zéros continus :

| Adresse `Main RAM` | run01 | run02 | run03 |
|---|---|---|---|
| `0x05610C` | `0x00` | `0x01` | `0x03` |

Acquis :

- Les trésors ramassés sont bien suivis par un **champ de bits**, un bit
  par trésor, dans une zone creuse de la RAM principale
- **Les bits sont rangés LSB en premier** : le premier bloc frappé a mis
  le bit 0, le second le bit 1
- Les deux bits sont **adjacents**, donc les deux trésors ont des
  identifiants consécutifs, cohérent avec deux trésors d'une même salle
- Le flag **monte et reste**, il n'est pas remis à zéro

### Adresse de base, **Vérifié**

```
base = 0x0560C8 dans Main RAM, soit l'adresse absolue 020560C8
bit du trésor d'identifiant N  ->  octet 0x0560C8 + N // 8, bit N % 8
```

**Vérifié**, source `inf.gg/mlbis/manual` section IDs > Registers, lue le
3 août 2026 : cette adresse n'héberge pas une structure dédiée aux
trésors. C'est le **tableau de bits global des variables de script
`Exxx`**, 4096 bits soit `0x200` octets, de `020560C8` à `020562C8`. Les
flags de trésors en occupent les **index bas**.

Nos 758 identifiants tiennent donc dans les **95 premiers octets** du
tableau, `0x0560C8` à `0x056126` inclus, soit moins d'un cinquième de sa
taille. Ce fichier présentait auparavant ces 95 octets comme la taille de
la structure, ce qui était faux ; le chiffre reste juste comme portion
utile et sert à dimensionner les lectures du client.

Le manuel ajoute que le jeu traite `Exxx` et `Fxxx` comme **une seule
plage continue indexée par `id & 0x1fff`**.

**Contradiction relevée dans le manuel, non tranchée** : `id & 0x1fff`
produit des index de 0 à 8191, alors que `Exxx` n'est déclaré qu'à 4096
éléments. Les index 4096 et au-dessus, c'est-à-dire les variables
`Fxxx`, tomberaient hors des `0x200` octets, donc dans le tableau `6xxx`
à `020562C8`. Sans conséquence pour les trésors, qui restent sous
l'index 758, mais **toute écriture à un index élevé est en terrain non
sûr** tant que ce point n'est pas éclairci.

Le rang du bit **est** l'identifiant des octets 4-5 de
`TreasureInfo.dat`. Confirmé le 3 août 2026 par cinq dumps successifs
sur les quatre blocs de la salle 258, identifiants 544 à 547, tous logés
dans l'octet `0x05610C` :

| Dump | Octet | Bits | Identifiants |
|---|---|---|---|
| `run01` | `0x00` | — | aucun |
| `run02` | `0x01` | 0 | 544 |
| `run03` | `0x03` | 0,1 | 544, 545 |
| `run04` | `0x0B` | 0,1,3 | 544, 545, 547 |
| `run05` | `0x0F` | 0,1,2,3 | 544, 545, 546, 547 |

Ce qui rend la preuve solide plutôt que seulement cohérente : les blocs
ont été frappés **dans l'ordre inverse** de la prédiction, 547 avant
546. Le bit 3 s'allume donc avant le bit 2. Les bits suivent les
identifiants de la table, pas l'ordre des actions du joueur, ce qui
exclut un simple compteur de ramassages.

Entre `run04` et `run05`, un seul octet a changé dans un rayon de
512 octets autour du champ.

**L'identifiant vaut l'index**, mesuré sur les identifiants 544 à 547 :
`0x05610C = 0x0560C8 + 68` et `68 × 8 = 544`. Extrapolé aux 754 autres,
et appuyé depuis le 3 août 2026 par la base `0xE000` annoncée pour les
trésors, voir « Découpage du tableau `Exxx` » plus bas. La variable de
script d'un trésor est donc `0xE000 + identifiant`.

### Instant où le flag tombe, **Vérifié**

Mesuré le 3 août 2026 sur l'identifiant 546, `quantity = 0` et
`max_hits = 10`, soit une pièce par saut dans une fenêtre de quelques
secondes. Cinq dumps depuis un savestate vierge :

| Dump | `0x05610C` | État du bloc |
|---|---|---|
| `run06` | `0x00` | avant tout, témoins 544, 545 et 547 à zéro |
| `run07` | `0x00` | bloc frappé, émulateur mis en pause aussitôt |
| `run08` | `0x04` | première pièce prise, neuf encore disponibles |
| `run09` | `0x04` | avant-dernière pièce |
| `run10` | `0x04` | bloc épuisé |

**Le bit monte dès la première pièce, pas à l'épuisement.** Une
`location` est donc validée au premier coup, et les coups suivants ne
touchent plus au tableau : aucun autre octet des `0x200` ne change entre
`run06` et `run10`.

Second acquis, apporté par le `run07` : le bit ne monte pas à l'instant
du coup mais quelques frames plus tard. **Il suit l'attribution de
l'objet, pas la frappe du bloc.** Sans conséquence pour un client qui
interroge la mémoire en boucle, mais ne pas supposer les deux
simultanés.

**Rappel utile** : le domaine `SRAM` n'a pas bougé d'un octet pendant
l'expérience. Le jeu n'écrit dans la sauvegarde qu'au moment d'une
sauvegarde explicite, le champ de bits vit d'abord en RAM de travail.

## Registres globaux et plan mémoire de l'ARM9

**Vérifié** ligne par ligne, source `inf.gg/mlbis/manual`, sections
IDs > Registers et le plan mémoire, lues le 3 août 2026. Adresses
relevées sur la release NA `CLJE`, celle du projet.

Les variables de script ne sont pas éparpillées : elles vivent dans un
bloc de six tableaux contigus, en tête du BSS de l'ARM9.

| Adresse | Plage | Contenu | Taille |
|---|---|---|---|
| `02055FE4` | `5xxx` | tableau de `s32`, 16 éléments | `0x40` |
| `02056024` | `Cxxx` | tableau de `s32`, 5 éléments | `0x14` |
| `02056038` | `2xxx` | champ de bits, 64 éléments | `0x08` |
| `02056040` | `Dxxx` | tableau de bits, 1088 éléments | `0x88` |
| `020560C8` | `Exxx` | tableau de bits, 4096 éléments | `0x200` |
| `020562C8` | `6xxx` | tableau de `s8`, 152 éléments | `0x98` |
| `02056360` | — | sans identifiant, usage inconnu du manuel | `0x0E` |
| `0205636E` | — | fin du bloc | — |

La **contiguïté est une déduction arithmétique**, pas une affirmation du
manuel : chaque fin colle exactement au début suivant, ce qui la valide.
Bloc de 906 octets, `0x38A`, commençant 4 octets après le début du BSS.

**Hypothèse sur `Dxxx`**, avancée le 3 août 2026 par yx, qui précise ne
pas l'avoir testée : ce seraient les bascules des cartes de terrain, du
genre « l'eau de la pompe s'active quand la variable `0x216` est vraie ».
L'argument est un rapprochement de capacités, les cartes de terrain
utilisant 1026 registres de bascule pour 1088 bits disponibles dans
`Dxxx`. Marc y ajoute les salles de la minicarte à dévoiler. Rien de
mesuré, mais deux sources concordantes.

Plan mémoire, **Vérifié**, même source :

| Élément | Plage |
|---|---|
| segment ARM9 chargé à | `02004000`, point d'entrée `02004800` |
| BSS ARM9 | `02055FE0` à `02063B00` |
| BSS ITCM | `01FF93C0` à `01FFA580` |
| BSS DTCM | `027E00E0` à `027E1200` |
| ITCM copié depuis | `02055FE0` à `020573A0`, `0x13C0` |
| DTCM copié depuis | `020573A0` à `02057480`, `0xE0` |
| segment ARM7 chargé à | `02380000`, non compressé |

Deux conséquences, l'une pratique et l'autre explicative :

- `020560C8` est **dans le BSS de l'ARM9**, donc à une adresse fixe pour
  toute la partie, hors de la zone des overlays et hors du heap. Le
  client pourra lire là sans se soucier de la salle chargée. Remplace
  l'hypothèse précédente sur le placement
- Le BSS de l'ARM9 **écrase l'image d'origine du code ITCM et DTCM**,
  dont la source recouvre justement `02055FE0` à `020573A0`. C'est ce
  qui explique les 410 octets de zéros continus observés au `run05` :
  cette zone est de la mémoire remise à zéro, pas du code

Heaps, **Vérifié**, gérés par `Heap::init_heaps` d'après le manuel :

| Heap | Plage | Rôle |
|---|---|---|
| 0 | `021277C0` à `023E0000` | mémoire principale |
| 1 | `01FFA580` à `02000000` | ITCM |
| 2 | `027E1200` à `027E2780` | DTCM |
| 3 | `027FF000` à `027FFC00` | non documenté |

Overlays, **Vérifié**, même source :

| Overlay | Contenu |
|---|---|
| 0, 127, 129 | `clMesWinEff` et **code de sauvegarde**. Les overlays 127 et 129 ont été signalés par yx le 3 août 2026, le manuel ne citait que le 0. La sérialisation des registres est dans le 129 |
| 1 | initialisation de la partie |
| 2 à 7 | `field`, sans description dans le manuel |
| 8 et au-delà | combat |
| 138 et 139 | DSProtect |

L'overlay 0 porte le code de sauvegarde : c'est là qu'il faudra chercher
si la prédiction de sérialisation H2 tombe à côté. La case vide des
overlays 2 à 7 est partiellement remplie par BIS-docs, qui place la
table des commandes de script dans `overlay_0006.bin`.

## Variables de script

**Vérifié** : les flags de progression sont des variables de script.
`Variables[0x200E]` vaut 0 tant que le Bloc Aspirateur n'est pas acquis.
Source `vendor/Randoglobin/randoglobin/mnlscript_skips.py` ligne 1568,
commentaire explicite.

**Vérifié** : un acteur de script porte un champ encodant
`(variable << 16) + index_de_subroutine`, ce qui conditionne son
comportement à une variable. Source même fichier, ligne 535.

**Vérifié**, ce qui était une hypothèse jusqu'au 3 août 2026 : les
variables `0x2000` à `0x203F` sont bien **64 flags d'un bit tenant dans
8 octets**. Deux sources indépendantes le disent, chacune de son côté :

- en RAM, à `02056038`, source `inf.gg/mlbis/manual` section
  IDs > Registers
- dans la sauvegarde, à `slot + 0x0124`, où Cheatoglobin lit exactement
  8 octets nommés `var_2xxx` et les manipule au bit près
  (`window.py` ligne 144, `save_file_tab.py` lignes 48 et 55)

Reste une déduction et non un fait lu : que ces deux emplacements
portent **la même donnée**, l'un étant la sérialisation de l'autre.
Aucune des deux sources ne décrit la copie. Toutes les variables `0x2xxx`
vues dans Randoglobin sont inférieures à `0x2040`, ce qui est cohérent
avec 64 éléments.

**Trésors hors `TreasureInfo.dat`**, c'est-à-dire coffres de quête,
récompenses de PNJ et boutiques. Marc, le 3 août 2026 : ce sont des flags
de cinématique, traités comme des flags d'histoire ordinaires, et **ils
ne se reconnaissent pas à leur plage**. Il n'y a donc pas de table à
dumper, il faut passer par `mnlscript`, sa sortie, et la façon dont
Randoglobin s'en sert pour remplacer les scripts du jeu. C'est le seul
des trois chantiers restants qui demande de comprendre les scripts.
Référence donnée dans la foulée :
`mnl-modding.github.io/BIS-docs/scripting/fevent_commands.txt`.

Plages de variables vues dans Randoglobin, par fréquence décroissante :
`0xEAxx`, `0xEBxx`, `0x90xx`, `0xA0xx`, `0x60xx`, `0x30xx`, `0xE9xx`,
`0xE7xx`, `0x10xx`, `0xE8xx`, `0x20xx`, `0x50xx`, `0xC0xx`, `0xB0xx`,
`0xD0xx`. Leur sémantique respective n'est pas documentée.

### Découpage du tableau `Exxx`, ex-hypothèse H3

**Source communautaire**, Marc (ThePurpleAnon) sur le Discord
MnL-Modding, le 3 août 2026. Les flags de trésors, d'ennemis vaincus et
d'histoire vivent tous dans `Exxx`, à des bases distinctes :

| Base | Contenu | Index |
|---|---|---|
| `0xE000` | trésors | 0 à 1023 |
| `0xE400` | ennemis vaincus | 1024 à 1791 |
| `0xE700` | histoire | 1792 et au-delà |

Il précise ne pas avoir cherché de subdivision plus fine au-delà de
`0xE700`. Aucune ligne de code n'accompagne l'affirmation, donc elle
reste au rang d'une source communautaire, mais elle est corroborée par
trois observations indépendantes :

- nos trésors s'arrêtent à l'index 757, bien sous la frontière 1024
- la base `0xE000` implique index = identifiant, ce que nos dumps
  mesurent directement sur les identifiants 544 à 547
- les plages `0xE7xx` à `0xEBxx` relevées dans Randoglobin tombent
  toutes au-dessus de `0xE700`, donc du côté histoire

**Conséquence pour H1** : la variable de script d'un trésor est bien
`0xE000 + identifiant`. Le trésor 544 est `0xE220`, le 757 est `0xE2F5`.
Il reste qu'aucun script lu ne référence de `0xE2xx`, ce qui s'explique
si les trésors sont gérés par le moteur et non par les scripts.

**Mesure à l'appui de ce découpage**, relevée le 3 août 2026 en relisant
`run05` au-delà des 95 octets des trésors, avant que la réponse de Marc
n'arrive. Le tableau ne portait que quatre octets non nuls sur `0x200` :

| Offset | Valeur | Index | Variables sous H1 |
|---|---|---|---|
| `+0x044` | `0x0F` | 544 à 547 | nos quatre trésors |
| `+0x10A` | `0xE0` | 2133 à 2135 | `0xE855` à `0xE857` |
| `+0x10B` | `0x0F` | 2136 à 2139 | `0xE858` à `0xE85B` |
| `+0x152` | `0x08` | 2707 | `0xEA93` |

Les quatre octets se répartissent exactement selon le découpage annoncé :
un seul du côté trésors, sous l'index 1024, et les trois autres au-delà
de `0xE700`, donc du côté histoire. Aucun bit allumé dans la plage des
ennemis, sans qu'on sache si c'est significatif ou propre à ce savestate,
qui ne portait aucun trésor ramassé non plus.

Observation faite avant que la réponse de Marc n'arrive, ce qui lui donne
la valeur d'une prédiction rencontrée après coup plutôt que d'une lecture
orientée. Elle porte sur un seul dump, elle ne remplace pas une preuve.

## Écarté

`EObjSave/EObjSave.dat` ne contient aucun état de sauvegarde malgré son
nom, seulement des palettes graphiques. Source
`vendor/Randoglobin/randoglobin/palette.py` lignes 743 à 778.
