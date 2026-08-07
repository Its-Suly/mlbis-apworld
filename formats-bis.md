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

## Inventaire vivant

**Vérifié** le 3 août 2026, dumps `run06` à `run12`.

```
compteur de pièces : Main RAM 0x056400, absolu 02056400, u32
```

C'est la **première adresse d'état de jeu vivant** trouvée dans ce
projet, par opposition au tampon de sauvegarde. Elle se lit et se suit en
temps réel :

| Dump | Pièces | État |
|---|---|---|
| `run06` | 0 | départ |
| `run08` | 1 | première pièce du bloc 546 |
| `run10` | 2 | bloc 546 épuisé |
| `run12` | 9 | après les blocs 544, 545 et 547, qui valent 1, 5 et 1 |

Sur les 4 Mo, seuls deux `u32` montent d'exactement 7 entre `run11` et
`run12` : celui-ci et son image dans le tampon de sauvegarde.

L'adresse tombe juste après le bloc des registres globaux, qui finit à
`0205636E`, ce qui est cohérent avec une zone de données de partie.

### Correspondance avec la sauvegarde, **Vérifié**

Le format vivant reprend celui de la sauvegarde décalé de 2 octets après
le `u32` de pièces :

```
sauvegarde slot + 0x0054 + X   ->   Main RAM 0x056400 + X + 2
```

Testée sur les 204 octets de l'inventaire du `run13`, la règle est
**exacte de `X = 0x04` à `X = 0xA3`**, soit les 26 compteurs d'objets et
les 127 compteurs d'équipement, sans une seule discordance. Les autres
décalages, de 0 à 8, laissent tous au moins 38 octets discordants.

À partir de `X = 0xA4` la correspondance cesse, ce qui est attendu :
c'est là que commencent le champ de bits des badges, le compteur de
temps de jeu en frames et les jauges, données volatiles qui ont changé
entre l'instant de la sauvegarde et celui du dump.

Adresses utiles, **la primitive de livraison d'items** :

| Contenu | Adresse absolue | Taille |
|---|---|---|
| pièces | `02056400` | `u32` |
| 26 compteurs de consommables | `02056406 + N` | 1 octet chacun |
| 127 compteurs d'équipement | `02056427 + I - 1` | 1 octet chacun |

**Décalage de l'équipement, Vérifié** le 5 août 2026,
`tools/livrer_equipement.lua`. Le compteur d'un équipement est à
`02056427 + identifiant - 1`, et les 127 compteurs couvrent les
identifiants 1 à 127. Mesure : `1` écrit au compteur d'index 4 fait
apparaître **Heart Wear**, qui porte l'identifiant 5.

Le test avait été construit pour être discriminant plutôt que
confirmatoire : les deux hypothèses de décalage donnaient deux tenues de
frères différentes au même index, donc le nom affiché tranchait à lui
seul, sans interprétation.

Trois recoupements indépendants, tous obtenus après coup :

- l'inventaire du `run51` se lit alors « deux `Thin Wear` et un
  `Shabby Shell` », une tenue par frère et la carapace de départ de
  Bowser. Sous l'autre décalage il se lisait « deux `No gear` et un
  `Challenge Medal` », ce qui n'a aucun sens en début de partie
- l'identifiant 0 est `No gear` et le 128 `Rental Shell`, une carapace
  prêtée par l'histoire. Ni l'un ni l'autre ne se stocke, ce qui explique
  les 129 objets pour 127 compteurs
- le dernier compteur tombe à `020564A5`, soit exactement devant le champ
  de bits des badges à `020564A6`. Le bloc se ferme sans reste

Contrôle de cohérence au `run13` : deux compteurs non nuls seulement,
`3` à l'index 0 et `1` à l'index 16, soit trois `Mushroom` et un
`1-Up Mushroom`. Un inventaire de début de partie plausible.

Ce contrôle a d'abord été écrit « trois `Mushroom` et un `Heart Bean` »,
sur la foi d'un `data/noms_items.csv` alors faux. Les offsets, eux, ne
dépendaient pas du nom : la cartographie tient, seule l'étiquette était
fausse.

### Écriture validée, **Vérifié**

Premier test d'écriture du projet, le 3 août 2026, `tools/ecrire_pieces.lua`,
dumps `run12` et `run13`. État de jeu : sur le terrain, en marchant, hors
combat et hors dialogue.

999 écrit à `02056400` à la place de 9, puis quelques pas, puis
sauvegarde en jeu.

| Contrôle | Valeur |
|---|---|
| RAM `0x056400` | 999 |
| Affichage à l'écran | 999, vu par le joueur |
| Sauvegarde `slot + 0x0054` | 999 |
| Copie de secours `slot + 0x7EC + 0x0054` | 999 |
| Témoin trésors `0x05610C` | `0x0F`, intact |
| Reste du tableau `Exxx` | aucun octet modifié |

Ce que ça établit, et c'est le point qui débloque la livraison d'items :
**le jeu ne subit pas la valeur écrite, il l'adopte.** Il l'affiche, la
sérialise dans la sauvegarde et dans sa copie de secours, et recalcule
lui-même le checksum. Aucun effet de bord observé sur les structures
voisines.

Ce que ça n'établit pas :

- La livraison d'un **objet** au sens d'Archipelago. Seul le compteur de
  pièces est cartographié ; les 26 compteurs d'objets de l'inventaire
  vivant ne le sont pas encore
- La **sûreté selon l'état du jeu**. Le test a eu lieu sur le terrain.
  Rien ne dit qu'écrire pendant un combat ou une cinématique soit sans
  risque, et `CLAUDE.md` impose de le supposer dangereux

### Comportement pendant un combat, **Vérifié**

Quatorze dumps le 4 août 2026, `run14` à `run27`, couvrant menu de
commandes, attaque, défense, menus des deux frères, fin de combat et
retour au terrain.

| Champ | Pendant le combat |
|---|---|
| 26 compteurs d'objets, `+0x06` | **partagés et vivants** |
| Compteur de pièces, `+0x00` | figé, crédité à la sortie seulement |
| 127 compteurs d'équipement, `+0x27` | inchangés, non sollicités |

**Les objets ne passent pas par une copie de combat.** Un champignon
consommé pendant le combat fait tomber le compteur `+0x06` de 9 à 8 dans
la seconde, dans la structure du terrain. Écrire un compteur d'objet
pendant un combat prend donc effet immédiatement, et l'objet est
utilisable dans le combat en cours.

Les pièces suivent un autre chemin : 948 pendant six dumps de combat,
puis 952 au retour. Elles sont accumulées ailleurs et appliquées à la
sortie. **Mais le crédit s'ajoute, il ne remplace pas**, vérifié le
4 août 2026 par deux essais :

| Essai | Avant | Écrit en combat | Après le combat |
|---|---|---|---|
| 1 | 932 | 999 | **1003**, soit 999 + 4 de butin |
| 2 | 944 | 999 | **999**, ce combat n'ayant rapporté aucune pièce |

Au second essai le joueur a gagné un champignon, et le compteur `+0x06`
est passé de 8 à 9 : le butin en objets s'ajoute lui aussi sans écraser.

**Confirmation à l'écran**, rapportée par le joueur et plus forte que le
dump : pendant le combat, l'affichage montrait déjà 999 pièces. Le
combat lit donc le compteur du terrain **en direct** pour l'afficher ;
seule l'accumulation du butin est différée à la sortie.

**Conclusion, et c'était le dernier inconnu technique du projet : une
écriture faite pendant un combat prend effet et survit à sa sortie**,
pour les objets comme pour les pièces. Aucun témoin d'état de jeu n'est
nécessaire pour livrer un item.

**Non testé** : les cinématiques et les dialogues. Le risque paraît
faible, on écrit des compteurs et non des structures, mais rien n'a été
mesuré et ça ne s'écrit donc pas comme un fait.

**Hypothèse abandonnée, notée pour ne pas la refaire** : « le combat
travaille sur sa propre copie de l'inventaire ». Elle venait d'un dump
où le compteur d'objet n'avait pas bougé — parce qu'aucun objet n'avait
été consommé. Une prémisse non vérifiée, encore. Le contre-test a
demandé trois dumps.

**Conséquence pour le client** : pas besoin de témoin d'état de jeu, ni
pour un objet ni pour des pièces. Une recherche d'octet discriminant
terrain / combat sur dix dumps de terrain et huit de combat laissait
38 candidats sans moyen de choisir entre eux. Elle est abandonnée, et
c'est une bonne nouvelle : un mauvais choix se serait payé par un
plantage rare et irreproductible.

### Ce que cette mesure corrige

Le bloc 546 n'a jamais rapporté 10 pièces, il en a rapporté **2**. Les
pièces sortent du bloc et doivent être touchées au sol ; les autres sont
retombées sans être ramassées. `max_hits = 10` décrit la capacité du
bloc, pas ce que le joueur encaisse.

Trois recherches antérieures avaient échoué parce qu'elles cherchaient
des deltas de `+8`, `+9` puis `+10`, déduits de cette prémisse fausse.
La méthode différentielle était bonne, la quantité supposée ne l'était
pas. Ne pas déduire d'un `max_hits` ce qui n'a pas été mesuré.

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

### L'identifiant d'un objet n'indexe pas la table de texte

**Vérifié** le 4 août 2026, et **ça invalide une lecture faite le 2 août**.

L'identifiant indexe une table d'enregistrements de l'**arm9 décompressé**,
et c'est cet enregistrement qui porte le numéro de chaîne. Source
`vendor/Randoglobin/randoglobin/treasure.py` lignes 135 à 142 :

```
item      = (type << 12) | id
pointeurs = 4 mots à l'offset 0x000145C0 de l'arm9 décompressé  (main.py:1169)
adresse   = pointeur - 0x2004000
record    = adresse + id * [24, 24, 16, 32][type - 1]
string_id = u16 en tête du record
nom       = entrées_de_texte[string_id]     (pluriel à string_id + 1, ligne 162)
```

**Piège** : l'arm9 doit être décompressé, sinon l'offset `0x145C0`
n'existe pas. Le brut fait 219 452 octets, le décompressé 341 144.
Méthode `main.py:391`, `ndspy.codeCompression.decompress`.

| Type | Table arm9 | Pas | Objets | Source du compte |
|---|---|---|---|---|
| 1 attaque | `0x4EA68` | 24 | 28 | borne `string_id` |
| 2 consommable | `0x4E7F8` | 24 | 26 | Cheatoglobin `ITEM_DATA` |
| 3 badge | `0x4E6F8` | 16 | 8 | Cheatoglobin `BADGE_NAMES` |
| 4 équipement | `0x4FB30` | 32 | 129 | Cheatoglobin `GEAR_DATA` |

Les 26 consommables se recoupent trois fois : `constants.py` ligne 85,
les 26 compteurs de la sauvegarde, et l'écart entre deux tables de
l'arm9, `(0x4EA68 - 0x4E7F8) / 24 = 26`.

Le pas de 3 des triplets singulier / pluriel / « Full! » est réel dans la
table de **texte**, mais il ne donne pas l'identifiant. La version
précédente de ce fichier en tirait `id = position // pas`, ce qui était
faux : voir « Ce que cette correction a coûté » ci-dessous.

Contrôle de cohérence, corrigé : l'équipement d'identifiant 0 est
`No gear`, l'emplacement vide, et non le premier vêtement. Les 26
consommables se rangent par familles — Champignons 0 à 3, Pilons 4 à 6,
Noix 7 à 10, Sirops 11 à 14, 1-Up 16 et 17, Haricots 20 à 22 — là où
l'ancienne lecture les éparpillait.

### Ce que cette correction a coûté

**396 noms sur 685** changent dans `data/locations_bis.csv`, et **129 sur
129** dans les équipements de `data/noms_items.csv`. Le fichier passe de
204 à 191 objets, les 13 en trop étant des identifiants qui n'existaient
pas.

Ce qui n'a **pas** bougé, et c'est ce qui limite les dégâts : aucun
identifiant de trésor, aucun type, aucun montant, aucune coordonnée. Le
défaut vivait dans la seule colonne `nom_item`, parce que
`tools/build_location_table.py` ligne 72 calcule `id_item = item & 0xFFF`
directement depuis la ROM et ne demandait à `noms_items.csv` qu'un
libellé.

Ce qui a permis de le voir : les 26 compteurs de consommables de la
sauvegarde correspondaient bien à 26 objets, ce qui donnait l'illusion
d'une lecture confirmée. Le compte était juste, l'ordre ne l'était pas.
**Un décompte qui tombe juste ne valide pas la bijection qui va avec.**

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

## Salle, carte et zone, la correspondance est établie

**Vérifié** le 4 août 2026 par `tools/build_salles_zones.py`. C'est ce
qui manquait pour avoir de vraies `region`.

La chaîne est celle que Randoglobin utilise pour nommer ses trouvailles,
`treasure.py` lignes 396 à 425, offsets dans `main.py` lignes 1035, 1036,
1046, 1089 et 1169 à 1172, structure dans `data_classes.py` lignes 89
à 97. Base NA :

```
pour chaque carte j de 0 à 0x2A8, soit 681 cartes :
  overlay 3   [0x19FD0 + j*20 + 16]   -> treasure_index, 0xFFFFFFFF si aucun
  overlay 4   [0x4AA30 + 4 + ti*4]    -> début et fin dans TreasureInfo.dat
  overlay 3   [0x098A0 + j*12]        -> select_map = (u32[0] >> 2) & 0x3FF
  overlay 129 [0x0864C + k*12 + 4]    -> 3 u16 ; si select_map y figure,
                                          le u16 à +0 indexe les noms de zone
  sinon, zone 0xA
```

Le repli sur la zone `0xA` n'est pas arbitraire : l'intérieur du lac
Blubble est la seule zone absente de l'écran de sélection de fichier,
d'où viennent ces chaînes. Commentaire explicite `treasure.py:424`.

Un trésor d'index `i` appartient à la carte `j` si
`début <= i*12 < fin`.

**Résultat** : 278 cartes sur 681 portent des trésors, et les 647 trésors
exploitables se répartissent sur **16 zones nommées** sur 32.

| Zone | Trésors | Zone | Trésors |
|---|---|---|---|
| Peach's Castle | 117 | Cavi Cape | 21 |
| Bowser Castle | 66 | Pump Works | 20 |
| Dimble Wood | 65 | Bowser Path | 19 |
| Toad Town | 64 | Bumpsy Plains | 17 |
| Plack Beach | 56 | Tunnel | 11 |
| Energy Hold | 54 | Trash Pit | 11 |
| Airway | 51 | Tower of Yikk | 3 |
| Blubble Lake | 50 | Flab Zone | 22 |

### Ce que la mesure a appris en plus

**Notre découpage en salles était déjà le bon.** Le regroupement par le
bit `is_last_entry_in_room`, fait le 2 août sans rien savoir des cartes,
est en **bijection** avec le découpage en cartes du jeu : 265 salles pour
265 cartes, aucune salle vers deux cartes, aucune carte vers deux salles.

**Réserve** : 13 trésors sur 685 sont revendiqués par deux cartes, deux
d'entre eux par trois. Des plages qui se chevauchent.
`build_location_table.py` retient la plage la plus petite, donc la carte
la plus spécifique, ce qui est un choix et non une lecture.

`data/locations_bis.csv` porte désormais les colonnes `carte` et `zone`,
et **les 647 trésors exploitables ont tous une zone**.

**Vérifié en jeu** le 4 août 2026 : les trésors 549 à 555, que la table
place en `Trash Pit`, ont été ramassés par le joueur alors qu'il se
trouvait effectivement dans la Fosse à Ordures. La correspondance ne
repose donc plus seulement sur une lecture d'overlay.

## Trésors hors `TreasureInfo.dat`

Coffres de quête, récompenses de PNJ, achats en boutique. Établi le
4 août 2026 par balayage complet de `FEvent.dat`, chunks 0 et 1 des 681
triples, overlays 3 et 6 chargés : **538 508 commandes**, zéro warning,
zéro octet non parsé. L'index 2 du triple est une `LanguageTable`
(`vendor/mnllib.py/mnllib/bis/managers.py:34`), pas un script.

### Le résultat est négatif, et c'est ce qui oriente la suite

**Vérifié** : aucune commande de script ne référence jamais une variable
de `0xE000` à `0xE3FF`, ni en `result_variable` ni en argument. Or c'est
la plage des trésors. Les seules variables `Exxx` écrites le sont
exclusivement par la commande `0x0008 Set`
(`vendor/BIS-docs/cutscene_code/bis_docs_commands.yml:80-86`) : 338
valeurs distinctes entre `0xE400` et `0xE552`, 1072 entre `0xE700` et
`0xEDB4`, sur 53 622 écritures.

**Les scripts ne posent donc pas les flags de trésor par variable.**

Ce que ça ne prouve pas : qu'ils ne déclenchent jamais l'acquisition d'un
trésor. Une commande passant un identifiant littéral à un handler ARM qui
ferait `bitfield[id/8] |= 1<<(id%8)` serait invisible à cette méthode. Ça
colle avec le fait que Randoglobin patche l'overlay 4 pour les trésors.

**Conséquence pratique** : étendre le balayage de `FEvent` ne donnera
rien de plus. Ce qui trancherait est un **breakpoint d'écriture BizHawk
sur `020560C8`**, puis la remontée au code appelant.

Non couvert par le balayage : les scripts de combat
(`BattleScriptManager`, `managers.py:228`), les MAI et SAI non
chargeables par mnllib, et les tables de données que sont les boutiques
et `TreasureInfo.dat`.

### Ce qui est énumérable par programme, et ce qui ne l'est pas

**Vérifié.** Randoglobin connaît trois familles d'emplacements :

| Famille | Mécanisme | Volume |
|---|---|---|
| `TreasureInfo.dat` | table de données, parcourue en entier, `treasure.py:308-339` | 647 exploitables |
| Boutiques | **fichier de données** `MData/MDataShopBuyList.dat`, `data_classes.py:99-126`, versé au même pool par `treasure.py:341-355` | 64 emplacements, 8 boutiques |
| Récompenses de quête | **quatre couples salle / sous-routine écrits en dur**, `treasure.py:357-390` | 32 checks |

Les boutiques sont donc énumérables sans travail manuel. Les récompenses
de quête ne le sont pas : `mnlscript_sidequests.py` code en dur `0x028D`,
`0x0128`, `0x0129`, `0x0287`, et 21 `room_id` en dur au total sur les
modules `mnlscript_*.py`. **Le seul randomizer BIS existant a buté sur le
même mur et l'a contourné à la main.** Pas d'avance gratuite, mais pas
non plus de découpage existant auquel se conformer.

Restent hors de son pool : objets clés, soins et capacités, désactivés
par `setEnabled(False)` (`treasure.py:760-783`) ; Challenge Node,
Cholesteroad, Broque Madame, Final Rank et Birdley, commentés
(`treasure.py:556-578`, `604-608`).

### Les commandes de don, recensées

**Vérifié** dans `FEvent.dat` : 318 × `0x0044 Add Items`, 131 ×
`0x0041 Add Coins`, 5 × `0x0043 Get Item Amount`. Noms dans
`bis_docs_commands.yml:490-507`.

**Aucun des 318 `0x0044` n'a d'identifiant d'objet en variable** : tous
littéraux, donc résolubles statiquement, sans émulation. C'est le point
directement exploitable.

Mais 349 de ces commandes se concentrent dans les salles `0x0000`,
`0x0001` et `0x0002`, dont les tables de langue ne contiennent que
« no need to translate ». Salles de développement selon toute
vraisemblance — **aucune source ne les nomme ainsi**, c'est une
inférence. Hors de ces trois salles il reste 105 commandes, réparties sur
46 sous-routines et 42 salles, et elles arrivent en lots : la salle
`0x0128` sous-routine 28 en porte 9 d'affilée.

Formulation à retenir : le balayage énumère les commandes de don de façon
reproductible, ce qui **réduit le travail manuel à une quarantaine de
sous-routines à qualifier**, mais ne le remplace pas.

### Attribuer un flag à chaque don ne marche pas localement

**Vérifié.** Sur les 100 dons hors salles de développement, chercher
« une seule variable `Exxx` testée par `0x0002` puis posée par `0x0008`
dans la même sous-routine » n'attribue un flag certain qu'à **5** dons.
En relâchant à « une seule `Exxx` posée, sans exiger le test », on monte
à 25. Les trois quarts restent non résolus dans les deux cas.

Sur les 318 sites `0x0044`, **244 ne contiennent aucune commande `Exxx`**.
La garde vit chez l'appelant, pas sur place.

Exemple complet, salle `0x028D` chunk 0 sous-routine `0x12`, le seul
motif propre observé :

```
cmd[4]  0x0002(0x00, V[0xEAB9], 0x0, 0x00, 0x165)   saute si le flag est deja pose
cmd[5]  0x0008(0x1) -> V[0xEAB9]                    pose le flag
cmd[34] 0x0044(0x4066, 0x1)                         donne Block Band
```

Deux pièges dans ce seul exemple. Les offsets de saut sont relatifs à la
**fin** de la commande (`bis_docs_commands.yml:34-39`). Et le flux n'est
pas linéaire : `cmd[19] 0x0049` « Start Thread Here and Jump » fait
sauter le thread principal par-dessus `cmds[20..32]`, si bien qu'une
lecture naïve croirait `cmd[34]` inatteignable.

**Le flag est posé avant le don.** Une `location` validée sur ce flag
sera signalée un peu avant que le joueur voie l'objet.

### Noms officiels des plages de variables

**Source communautaire**, document de nommage transmis le 4 août 2026.
Il porte des noms de développeurs, donc il vient vraisemblablement d'un
symbole ou d'une doc interne, mais rien ne l'établit formellement.

| Plage | Nom | Sens |
|---|---|---|
| `3xxx` | `frg` | field register |
| `4xxx` | `brg` | battle register |
| `5xxx` | `urg` | universal register |
| `6xxx` | `gby` | global byte |
| `9xxx` | `grg` | global register |
| `Axxx` | `lrg` | local register |
| `Bxxx` | `lbi` | local bitflag |
| `Cxxx` | `mrg` | message register |
| `Exxx` | `gbi` | **global bitflag** |

`1xxx`, `2xxx` et `Dxxx` restent sans nom dans ce document.

Décomposition : `l` local, `g` global, `u` universal, `f` field,
`b` battle, `m` message ; suffixes `bi` bitflag, `by` byte, `rg`
register.

**Ce que ça corrige.** Nos notes s'appuyaient sur `mnllib/bis/consts.py`,
dont les noms sont des suppositions de son auteur. Le document officiel
le contredit : `3xxx` et `4xxx` ne sont pas un bloc `SPECIAL` unique mais
les registres de terrain et de combat, `Axxx` est `lrg` et non `LOCAL2`,
`Bxxx` est `lbi` et non `STACK_BITFIELD`.

**Le point qui nous concerne.** `Exxx` est un **unique tableau de
drapeaux globaux**, sans subdivision dans le moteur. Le découpage
trésors / ennemis / histoire est donc une convention d'usage des
développeurs et non une structure. Ça explique qu'aucun code ne
matérialise les frontières `0xE400` et `0xE700`, et ça conforte notre
lecture du tableau comme un champ de bits plat.

Les exemples fournis, `E9A9`, `EAA3`, `EB18`, `EB19`, `EB32`, `EB88`,
`EBF2` à `EBF4`, tombent tous au-dessus de `0xE700`. Nos deux octets non
nuls du `run05`, index 2133 à 2139 et 2707, valent `0xE855` et `0xEA93`
sous la même base : même voisinage.

Détail sans usage technique mais qui date le code : les noms `gby` et
`gbi` portent les initiales de leur auteur, `sk` Shunsuke Kobayashi,
`cf` Chihiro Fujioka, `dg` Daisuke Goto.

### États de jeu numérotés, piste à suivre

**Source communautaire**, capture d'écran du 22 juin 2026 transmise le
4 août. Le jeu a des états numérotés, et deux sont connus :

- état `9` : écran blanc, overlays 0, 127 et 129
- état `A` : écran de sauvegarde, pavé désactivé, mêmes overlays

Ça explique au passage pourquoi le code de sauvegarde vit dans ces trois
overlays, relevé plus haut sans qu'on sache pourquoi ils allaient
ensemble.

**Non trouvé** : où ce numéro d'état se lit en mémoire. Sans intérêt pour
livrer un objet, puisque l'écriture est sûre en toute circonstance
mesurée, mais ce serait le bon outil pour trancher le cas des
cinématiques, seul état encore non testé.

### Pièces d'attaque, triplement suivies

**Vérifié** le 4 août 2026, quinze dumps `run32` à `run46`, set Green
Shell dans la zone de départ, neuf pièces sur dix ramassées une par une.

Les blocs à pièces d'attaque sont **absents de `TreasureInfo.dat`** : la
table ne connaît que cinq types de trésor et quatre types de contenu,
aucun ne les décrit. Les 38 entrées `vide` sont toutes des touffes
d'herbe de Dimble Wood et Bumpsy Plains, donc pas une échappatoire.

Le jeu suit les pièces à **trois endroits redondants**, tous d'accord à
chacun des quinze dumps.

| Support | Adresse | Contenu |
|---|---|---|
| Bit `Exxx` | variable `0xE700 + k`, bit `1792 + k` | une pièce `k` |
| Champ de bits `6xxx` | `0x601B` bits 0 à 4 | pièces 0 à 4 |
| Champ de bits `6xxx` | `0x601C` bits 0 à 4 | pièces 5 à 9 |
| Compteur `6xxx` | `0x601D` | nombre de pièces, 0 à 9 mesuré |

La correspondance est exacte dans les deux sens. Au `run44`, `0x601C`
vaut `00001001`, soit les pièces 5 et 8, et `Exxx` porte exactement
`E700, E701, E702, E703, E704, E705, E708`. Le ramassage n'est pas
ordonné, et les trois supports suivent le même désordre.

En Main RAM, `0x601D` est à `020562E5`, soit `020562C8 + 0x1D`.

**Ce que ça change.** Une pièce d'attaque est une `location` de première
classe, lisible par le mécanisme que le client utilise déjà, un bit dans
le tableau `Exxx`. Rien de neuf à écrire côté client sinon **élargir la
fenêtre de lecture** : `mlbis/client.py` lit 95 octets, soit les bits 0 à
759, et le bit 1792 tombe à l'octet 224. La convention
`location = BASE_ID + rang de bit` tient sans exception, et 1792 est bien
au-delà des 1024 réservés aux locations hors `TreasureInfo.dat`.

**Ce que ça corrige.** Marc donnait `0xE700` comme début de la plage
histoire. Les dix premières variables de cette plage sont des pièces
d'attaque. La frontière est juste, son étiquette est trop étroite.

**Piège écarté par la mesure.** `02056024`, base du tableau `Cxxx`, suit
la même suite 0 à 9 et survit aux dix filtres. C'est le registre de
message, celui qui affiche le compte à l'écran. Il est écarté sur un
critère déjà vérifié et non sur une intuition : la fonction de
sauvegarde ne recopie que `2xxx`, `Dxxx`, `Exxx`, `6xxx` et la plage
anonyme. `Cxxx` n'est pas sauvegardé, donc il ne peut pas porter l'état.

### Les bits survivent au déblocage, et le déblocage a sa propre marque

**Vérifié** le 5 août 2026, cinq dumps `run47` à `run51` pris en chaîne :
avant le saut, à la réception de la dixième pièce, à l'annonce de
l'étoile, pendant le combat qui suit, après le combat une fois la porte
ouverte.

Les dix bits `0xE700` à `0xE709` sont levés et **aucun ne retombe**, ni
au déblocage, ni pendant le combat, ni après. `0x601B` et `0x601C`
valent `00011111` chacun, `0x601D` vaut 10, du `run48` au `run51`.
La question qui décidait de tout est réglée dans le bon sens : **une
pièce d'attaque est une `location` utilisable**.

La dixième pièce est `0xE709`, pas `0xE708`. La note du 4 août parlait
de neuf bits parce que neuf pièces seulement avaient été ramassées.

Deux bits montent au moment exact de l'annonce, et à ce moment seulement,
dans le champ `2xxx` :

| Variable | Bit | Nom mnllib | Source |
|---|---|---|---|
| `0x200B` | 11 | `BROS_ATTACKS` | `mnllib/bis/consts.py:60` |
| `0x2010` | 16 | `BROS_ATTACK_GREEN_SHELL` | `mnllib/bis/consts.py:65` |

`0x200B` est nommé « bros attacks block » par
`vendor/randoglobin/randoglobin/patch.py:342`, qui le force à 1 pour
débloquer l'usage des Bros Attacks. Le `2xxx` est sauvegardé, à
`slot + 0x0124`, donc ces bits portent bien l'état durable.

**Conséquence majeure, au-delà des pièces.** Le champ `2xxx` est
l'énumération `ImportantFlags` de mnllib, `consts.py:46-93` : marteau,
Mini Mario, Drill Bros, Spin Jump, badges, vacuum, les dix Bros Attacks,
les six Brawl Attacks, sept améliorations de boutique. **Livrer une
capacité, c'est lever un bit dans huit octets à `02056038`**, sans
toucher à l'inventaire. C'est le chemin d'item le plus simple du projet.

Ce qui rend la correspondance solide : `ImportantFlags` n'est utilisé
nulle part ailleurs dans mnllib, donc rien ne la teste chez eux. Mais la
table de la ROM la recoupe sur **10 sur 10** pour les Bros Attacks, voir
plus bas, et deux bits ont été mesurés en jeu. Ce n'est plus une
affirmation de la communauté.

### Écrire dans `2xxx` marche, **Vérifié**

Le 5 août 2026, `tools/livrer_capacite.lua`. Bit `0x2019`, Fire Flower,
levé à la main dans une partie où l'attaque n'était pas débloquée.
Octet `0205603B`, `00` vers `02`, un seul octet touché sur les huit.

Résultat à l'écran, testé par le joueur : l'attaque **apparaît** au menu
Bros Attacks, se **sélectionne**, et se **joue entièrement, y compris sa
démonstration**. Le jeu n'exige pas que la cinématique d'apprentissage
ait eu lieu.

C'est exactement le cas qu'un randomizer produit à chaque seed, et il
passe. Quarante capacités deviennent livrables par une seule primitive,
un bit dans huit octets, sans compteur ni index ni quantité.

Deux réserves honnêtes. `0x200B`, qui autorise les Bros Attacks en
général, valait déjà 1 dans la partie de test : rien ne prouve encore
qu'il soit nécessaire, et `mlbis/delivery.py` le lève par précaution.
Et un seul des quarante bits a été écrit ; les autres partagent le
mécanisme, pas la mesure.

Premier essai mort sur une erreur de Lua qui vaut d'être notée :
l'opérateur `^` rend toujours un flottant, `2^1` vaut `2.0`, et
`memory.write_bytes_as_array` lève une `InvalidCastException` dessus. Une
table de puissances entières règle le cas. Rien n'avait été écrit.

Deux autres changements, notés sans être compris :

- `Cxxx` mot 0 monte 7, 8, 9, 10 et mot 1 descend 3, 2, 1, 0. Pièces
  ramassées et pièces restantes, l'affichage. Confirme que `Cxxx` est le
  registre de message et non un état
- `0xD3FB`, un bit `Dxxx`, monte à l'ouverture de la porte, après le
  combat. `0xD3FA` était monté à la neuvième pièce. Non expliqué

### Les dix Bros Attacks, table de l'overlay 123

**Vérifié** le 5 août 2026, `tools/extract_bros_attacks.py`, sortie
`data/bros_attacks.csv`. Table à l'offset `0x000304D4` de l'overlay 123,
10 entrées de 18 octets, structure lue dans
`vendor/randoglobin/randoglobin/special.py:26`, offsets NA dans
`main.py:1196-1197`.

| Attaque | Item | Pièces | Déblocage | SP | Lot |
|---|---|---|---|---|---|
| Green Shell | `0x1000` | `0x601B` | `0x2010` | 3 | Trash Pieces |
| Fire Flower | `0x1001` | `0x6000` | `0x2019` | 4 | Pump Pieces |
| Jump Helmet | `0x1002` | `0x6006` | `0x2016` | 6 | Flab Pieces |
| Yoo Who Cannon | `0x1003` | `0x6010` | `0x2012` | 7 | Toad Pieces |
| Super Bouncer | `0x1004` | `0x600A` | `0x2017` | 7 | Energy Pieces |
| Mighty Meteor | `0x1005` | `0x600D` | `0x2018` | 8 | Clinic Pieces |
| Spin Pipe | `0x1006` | `0x6003` | `0x2011` | 10 | Plack Pieces |
| Snack Basket | `0x1007` | `0x6012` | `0x201A` | 14 | Dimble Pieces |
| Magic Window | `0x1008` | `0x6018` | `0x201B` | 18 | Castle Pieces |
| Falling Star | `0x1010` | `0x6015` | `0x2013` | 20 | Peach Pieces |

Les dix variables de déblocage sont exactement les dix
`BROS_ATTACK_*` de `ImportantFlags`, dans le même ordre de bits. Deux
sources indépendantes, la ROM et mnllib, qui ne se citent pas.

Le triplet d'une attaque est base, base+1 en champs de bits de 5 bits,
base+2 en compteur. Vérifié pour le Green Shell par la mesure et par les
scripts ; les bases se chevauchent entre `0x6010` et `0x6012`, donc
**ne pas supposer le triplet** pour Yoo Who Cannon.

Le nom du lot vient de `MData/mfset_MenuMes.dat`, table 2 pour l'anglais.
Il donne la zone du set, ce que la salle du script ne donne pas.

### Les 78 pièces dont on connaît la variable

**Vérifié** le 5 août 2026, `tools/pieces_attaque_fevent.py`, sortie
`data/pieces_attaque.csv`. Balayage des 534 548 commandes de `FEvent`,
fichiers de `vendor/BIS-docs/data` dont l'identité octet pour octet avec
notre ROM est vérifiée par le script avant tout traitement.

Signature d'un bloc à pièce, lue dans les scripts et non supposée :

```
commande 0x0020   base+k |= masque      masque a un seul bit
commande 0x0008   Exxx   = 1            une seule variable
piece = 5 * k + log2(masque)
```

Témoin : le Green Shell rend `0xE700` à `0xE709` dans l'ordre des pièces
0 à 9, ce que les dumps mesurent indépendamment.

| Attaque | Pièces trouvées | Variables |
|---|---|---|
| Green Shell | 10 | `0xE700` à `0xE709` |
| Spin Pipe | 10 | `0xE76C` à `0xE775` |
| Mighty Meteor | 10 | `0xE7C4` à `0xE7CD` |
| Snack Basket | 10 | `0xE7FE` à `0xE807` |
| Falling Star | 10 | `0xE80E` à `0xE817` |
| Magic Window | 10 | `0xE818` à `0xE821` |
| Fire Flower | 10 | `0xE757` à `0xE75E`, plus `0xE749` et `0xE754` |
| Super Bouncer | 6 | `0xE7B4` à `0xE7B9` |
| Jump Helmet | 2 | `0xE781` et `0xE783` |
| Yoo Who Cannon | 0 | octroi en bloc |

**Le Fire Flower interdit de deviner le reste.** Sa pièce 3 est `0xE749`
et sa pièce 6 est `0xE754`, hors de la plage contiguë de ses huit autres
pièces. L'ordre des bits ne suit ni la géographie ni l'indice, donc
combler les trous par arithmétique produirait des variables fausses.

Le Yoo Who Cannon n'est pas une chasse : l'unique sous-routine qui écrit
`0x6010` et `0x6011` fait `|= 31` sur les deux, salle `0x0CF`. Les dix
pièces sont données d'un coup, ce ne sont pas des `location`.

Les 12 pièces manquantes, Jump Helmet 8 et Super Bouncer 4, ne sont ni
dans `FEvent` ni dans les scripts de combat, 268 161 commandes
parcourues, zéro écriture sur une variable de pièces. Aucun masque n'est
calculé à l'exécution, la recherche a été faite. Elles viennent donc
d'ailleurs, minijeu ou code ARM. **À mesurer en jeu**, c'est la méthode
qui a déjà réglé le reste.

**Salle inexploitable.** Les sous-routines de bloc sont dupliquées dans
13 ou 18 chunks de `FEvent` selon le groupe d'attaques. La salle ne peut
pas servir à assigner une `region` ; le nom du lot le peut.

**Fenêtre de lecture du client.** La dernière pièce connue est
`0xE821`, rang 2081, soit l'octet `2081 // 8 = 260`, bit 1. Le client
lit 95 octets, il lui en faut **261**. La valeur de 225 notée le 4 août
suffisait pour le rang 1792 seulement. Lire les `0x200` octets entiers
du tableau coûte moins cher que de recalculer cette borne à chaque
nouvelle famille de `location`.

## Vocabulaire de la progression

**Vérifié** comme lecture de source, le 5 août 2026 :
`vendor/Randoglobin/randoglobin/data_classes.py:11-35` déclare la liste
des prérequis d'un trésor. Son auteur a laissé un commentaire à côté :
il s'est aperçu après coup que la structure ne servirait pas à son
usage, et l'a gardée « comme ressource pour plus tard ». **Le tableau
n'est jamais rempli.** Ce qu'on en tire est donc le vocabulaire, pas la
donnée.

Onze de ces prérequis tombent sur un bit du champ `2xxx`, donc sur
quelque chose qu'on sait lire et écrire :

| Prérequis Randoglobin | Variable | Nom mnllib |
|---|---|---|
| `ml_req_mini_mario` | `0x2000` | `MINI_MARIO` |
| `ml_req_hammer` | `0x2001` | `HAMMER` |
| `ml_req_spin_jump` | `0x2002` | `SPIN_JUMP` |
| `ml_req_drill` | `0x2003` | `DRILL_BROS` |
| `kp_req_flame` | `0x2004` | `FIRE_BREATH_DISABLED`, inversé |
| `kp_req_slide_punch` | `0x2005` | `SLIDING_HAYMAKER` |
| `kp_req_body_slam` | `0x2006` | `BODY_SLAM` |
| `kp_req_spike_ball` | `0x2007` | `SPIKE_BALL` |
| `kp_req_vacuum` | `0x200E` | `VACUUM` |
| `ml_req_snack_basket` | `0x201A` | `BROS_ATTACK_SNACK_BASKET` |
| `ml_req_blue_shell` | `0x2025` | `BLUE_SHELL_BLOCKS` |

Sans correspondance : `ml_req_balloon`, et les prérequis d'objet
d'histoire `req_stingler`, `req_banzai_bill`, les trois clés et les trois
remèdes. Ce sont probablement des drapeaux `Exxx` de la plage histoire,
**à tester**.

Deux entrées de plus, `ml_has_access` et `kp_has_access`, disent que
chaque trésor appartient à une équipe. Notre découpage en `region` n'en
tient pas compte pour l'instant.

**Ce que ça ne donne pas** : quelle zone exige quoi. Aucune de nos
sources de code ne le porte.

### Où chaque capacité s'obtient, **Hypothèse**

Un guide en ligne n'est pas une source de code, mais `CLAUDE.md` classe
les discussions communautaires comme des **pistes à vérifier**, pas comme
rien. Croisées avec ce qu'on lit en mémoire, elles deviennent des
hypothèses testables. Table dans `data/progression_hypothese.csv`, une
ligne par capacité avec sa source.

Trois recoupements donnent du crédit à ces sources, et ils ont été faits
avant de s'en servir :

- Super Mario Wiki attribue les dix lots de pièces d'attaque à dix
  zones. Notre extraction de l'overlay 123 donne exactement les mêmes,
  **dix sur dix**, y compris les deux que nous avions étiquetées
  hypothèse, `Castle Pieces` pour Bowser's Castle et `Clinic Pieces` pour
  la clinique de Toad Town
- les quatre zones citées comme lieux d'acquisition qui ne sont pas des
  `region` chez nous, `Flame Pipe`, `Nerve Cluster`, `Joint Tower` et
  `Lumbar Nook`, existent toutes les quatre dans la table de 32 noms de
  la ROM. Une source qui inventerait un nom de zone échouerait ici
- `FIRE_BREATH_DISABLED` est nommé à l'envers dans mnllib, et le guide
  dit que Bowser **récupère** son souffle après le Scutlet. Les deux
  concordent : le bit doit retomber, pas monter. C'est aussi la seule
  ligne de la table dont le sens est inversé, et il valait mieux le voir
  maintenant qu'en écrivant une `access_rule`

**Réserve sur l'ordre des zones.** Deux pages du même wiki donnent deux
séquences qui ne coïncident pas sur la place de Flab Zone et de Bowser's
Castle. L'ordre reste donc non tranché, et il ne faut pas le figer dans
une `access_rule` en l'état.

**Ce qui manque encore entièrement** : le prérequis d'un trésor
particulier. Savoir que le Spin Jump s'obtient dans Flab Zone ne dit pas
quel bloc de Dimble Wood l'exige.

### La mesure qui tranche

`tools/journal_capacites.lua` tourne pendant une partie normale et note
chaque changement du champ `2xxx`, horodaté par le nombre de trésors déjà
ramassés. Une partie jouée produit l'ordre réel d'acquisition, ce qui
confirme ou casse la table ci-dessus au lieu de la remplacer.
`tools/etat_capacites.py --journal` met les noms dessus.

### Où chaque capacité est octroyée, lu dans les scripts, **Vérifié**

7 août 2026, `tools/capacites_fevent.py`, sortie
`data/capacites_fevent.csv`. Ce que la partie jouée aurait donné en
trente heures, les scripts le donnent en quelques secondes.

**Forme unique.** Les 48 variables `0x2000` à `0x2030` sont écrites par
une seule commande, `0x0008`, avec un argument entier, sur les 534 548
commandes de `FEvent`. Le script s'arrête s'il rencontre une autre
commande sur ces variables plutôt que de l'ignorer : c'est cette
hypothèse-là qui porte tout le reste.

**L'index de chunk `FEvent` est l'index de carte.** `FEvent` porte 681
chunks, la ROM `0x2A9` = 681 cartes. Le compte seul ne prouverait rien,
d'où le témoin : `data/bros_attacks.csv` vient de l'overlay 123 et donne
le lot de pièces de chaque attaque, donc sa zone, sans rien savoir des
scripts. Trois attaques sur quatre tombent dans la zone de leur lot, Spin
Pipe dans Plack Beach, Snack Basket dans Dimble Wood, Magic Window dans
Bowser's Castle. La quatrième, Mighty Meteor, est donnée à Toad Town pour
un lot `Clinic Pieces` : la clinique de Toadley **est** dans Toad Town,
ce sont deux zones nommées séparément, pas une contradiction.

**Trois chunks fourre-tout, écartés.** Les chunks 0, 1 et 2 posent 20, 27
et 46 variables. Aucune salle ne donne vingt capacités, ce sont des
initialisations ou du debug. Ils sont exclus du résultat et affichés à
part plutôt que passés sous silence.

**Résultat.** 38 variables sur 48 ont au moins une salle d'octroi, 29
n'en ont qu'une seule. Les 10 sans script sont les attaques débloquées
par le compte de pièces, Green Shell, Fire Flower, Jump Helmet, Super
Bouncer, Falling Star et Yoo Who Cannon comprises : leur déblocage vit
dans le code de l'overlay 123, pas dans un script.

Les capacités qui décideront des `access_rule` :

| variable | nom | salle | zone |
|---|---|---|---|
| `0x2000` | MINI_MARIO | 13 | Pump Works, mais c'est un état, voir plus bas |
| `0x2001` | HAMMER | 539 | Trash Pit |
| `0x2002` | SPIN_JUMP | 104 | Flab Zone |
| `0x2003` | DRILL_BROS | 229 | Energy Hold |
| `0x2005` | SLIDING_HAYMAKER | 50 | Dimble Wood |
| `0x2006` | BODY_SLAM | 324 | Tower of Yikk |
| `0x2007` | SPIKE_BALL | 414 | Peach's Castle |
| `0x200C` | BADGES | 184 | Flab Zone |
| `0x200E` | VACUUM | 61 | Plack Beach |
| `0x2025` | BLUE_SHELL_BLOCKS | 207 | Toad Town |
| `0x202D` | AIR_VENTS | 298 | Toad Town |

`MINI_MARIO` et `HAMMER` sont aussi reposés dans les chunks 51 et 73 de
Dimble Wood, tous deux ensemble. Une restitution après une séquence qui
les retire, **hypothèse**, à ne pas confondre avec l'octroi initial.

**Deux mondes, deux zones pour un même moment, hypothèse.** Le balayage
et les guides divergent sur quatre lignes, et trois s'expliquent de la
même façon : le drapeau est posé dans la salle où se trouve **Bowser**,
pas dans celle où les frères combattent à l'intérieur de lui. Le guide
place Sliding Haymaker au Nerve Cluster, le script le pose à Dimble Wood ;
Body Slam à Joint Tower contre Tower of Yikk. Les deux disent vrai sur
des moitiés différentes. Pour une `access_rule`, c'est la salle du script
qui compte, puisque c'est elle qui déclenche.

La quatrième divergence n'en est pas une : Spike Ball est donné dans
Peach's Castle, et le guide dit lui-même que le forage part du jardin du
château vers Lumbar Nook.

**Ce que le balayage ne donne pas.** 32 des 48 variables ne sont jamais
lues par un script. `HAMMER` et `SPIN_JUMP` sont lus zéro fois : aucun
bloc ne teste une capacité dans `FEvent`, donc le prérequis d'un trésor
vit dans le code ARM. Les plus lues sont des états de terrain, pas des
capacités : `ENERGY_HOLD_BOO_RAY` dans 36 salles, `AIRWAY_FROZEN` 24,
`PUMP_WORKS_FLOODED` 22. Deux exceptions utiles, `AIR_VENTS` lu dans 15
salles et `BLUE_SHELL_BLOCKS` dans 11, sont des prérequis de passage
lisibles directement.

### Le balayage et la partie jouée tombent d'accord, **Vérifié**

Le 7 août 2026, une partie jouée avec `journal_capacites.lua` a produit
des acquisitions réelles. Deux coïncidences que rien n'a arrangées :

- le journal note `0x202E` levé **et** `0x2030` retombé au même instant,
  après 12 trésors. Le balayage désigne un seul chunk qui fait
  exactement cette paire, le 507, à Cavi Cape
- le journal note `SHOP_UPGRADE_1` et `COUNTERATTACK_SHELL` acquis
  ensemble après 22 trésors. Le balayage les pose dans les chunks 57 et
  53, deux salles voisines

`0x2030`, que mnllib ne nomme pas, est donc un drapeau d'avant le menu
étoile de Bowser, retiré au moment où ce menu apparaît.

Le journal a aussi confirmé l'inversion annoncée : `FIRE_BREATH_DISABLED`
**retombe** en cours de partie, après 22 trésors. Ce n'est pas une
capacité qu'on livre en levant un bit, c'est la seule qu'il faudra livrer
en l'abaissant.

Enfin, il sépare deux familles que le nom seul ne distinguait pas.
`PUMP_WORKS_FLOODED` et `BLOOPERS_WET` montent et redescendent plusieurs
fois par heure de jeu : ce sont des états de terrain, ils ne doivent
jamais devenir des `item`. Ceux qui ne redescendent jamais sont les
capacités livrables.

**`MINI_MARIO` est un état, pas un déblocage, Vérifié en jeu.** Le bit
monte puis retombe après 15 trésors, remonte après 19. Témoignage du
joueur le 7 août 2026 : la capacité est débloquée une fois pour toutes,
puis **il active et désactive la forme miniature lui-même** pour
progresser. `0x2000` dit donc « Mario est actuellement miniature ».

Conséquence pour la logique, à ne pas rater : ce bit **ne peut pas
servir de prérequis**. Une `access_rule` qui le lirait serait vraie ou
fausse selon la forme de Mario à l'instant du test. Le déblocage se lit
ailleurs, sans doute dans un drapeau d'histoire `0xE7xx`, et reste **à
trouver**. Le chunk 13 de Pump Works, qui pose le bit la première fois,
est le bon endroit où chercher le drapeau voisin.

La même prudence vaut pour toute capacité dont le bit sert aussi d'état.
Le journal en jouant est le seul moyen de les repérer : un balayage
statique ne distingue pas un octroi d'un basculement.

### Le code ARM est lisible, et par où y entrer, **Vérifié**

7 août 2026. Tout ce qui reste inconnu vit dans le code ARM, et la
question n'était pas de savoir le lire mais d'y entrer. Deux mesures
suffisent à répondre.

**Les adresses connues sont dans les pools littéraux.** Le code ARM
charge ses constantes 32 bits depuis des mots posés après la fonction, ce
qui rend une adresse cherchable telle quelle, quatre octets en petit
boutiste. Résultat sur la ROM : `0x02056038`, le champ des capacités, en
six endroits, dont trois dans l'arm9 et deux dans l'overlay 129 ;
`0x020560C8`, le tableau `Exxx`, en treize endroits, dont l'overlay 4 qui
est celui des trésors.

En revanche `0x02056400`, les pièces, et `0x02056427`, l'équipement, n'y
apparaissent **pas** : ces deux-là sont atteints par un décalage depuis
un pointeur, pas par une constante. Une recherche d'adresse ne les
trouvera jamais.

**La carte des stockages de variables**, lue dans les pools de la plage
`0x02005840` à `0x02005D00`, qui est la primitive d'accès aux variables :

| adresse | ce qu'on en sait |
|---|---|
| `0x02055FE4` | non identifié |
| `0x02056024` | non identifié |
| `0x02056038` | champ `2xxx`, les capacités, **connu** |
| `0x02056040` | champ de bits, juste après les capacités |
| `0x020560C8` | tableau `Exxx`, **connu** |
| `0x020562C8` | exactement `0x020560C8 + 0x200`, donc la fin du tableau |
| `0x02056360` | non identifié |
| `0x020564BC` | non identifié |
| `0x020564CC` | non identifié |

La ligne `0x020562C8` vaut à elle seule le détour : elle **confirme par
le code** que le tableau `Exxx` fait bien `0x200` octets, ce qui n'était
jusque-là qu'une borne de prudence choisie le 5 août.

**La forme du lecteur de bit**, à `0x020059B8`, se lit sans effort :

```
lsr  r2, r0, #5          index / 32
ldr  r1, [r1, r2, lsl #2]   le mot correspondant
and  r0, r0, #0x1f       index % 32
lsr  r0, r1, r0
and  r0, r0, #1          le bit
```

C'est exactement l'arithmétique que notre `bitfield.py` applique, écrite
par les développeurs du jeu.

**Outil** : `ndspy` pour extraire arm9 et les 141 overlays, `capstone`
pour désassembler, mode ARM et non Thumb. Installé dans le venv de la
racine le 7 août 2026.

### Le type d'un trésor dit le côté du jeu, pas le prérequis, **Vérifié**

Hypothèse tentante : un bloc brique se casse au marteau, donc le type
dirait la capacité exigée, et la logique passerait au grain du bloc sans
lire d'ARM.

Elle est fausse, et c'est le joueur qui l'a vue en une phrase : à Plack
Beach, c'est **Bowser** qui se déplace, pas les frères. Le marteau est un
outil des frères. La table confirme d'un coup :

| | bloc `?` | bloc brique | haricot | touffe d'herbe |
|---|---|---|---|---|
| dans Bowser | 133 | **0** | 25 | 0 |
| monde extérieur | 148 | **144** | 172 | 20 |

Zéro bloc brique à l'intérieur du corps, 144 dehors. Le type encode donc
de quel côté du jeu se trouve le trésor, ce que la zone disait déjà.
Aucune information nouvelle pour la logique, et un test en jeu évité.

À noter pour ne pas répéter une erreur écrite ici puis corrigée le même
jour : les haricots **ne sont pas** absents de l'intérieur, il y en a 25,
dans Energy Hold et Airway.

### Le marteau confirme un nom, **Vérifié**

Au `run51`, les onze prérequis lisaient zéro. Cohérent avec un début de
partie, mais **preuve faible** : une correspondance fausse lirait zéro
tout pareil.

Le `run52`, pris après que le joueur a récupéré le marteau, tranche.
`0x2001` est levé, et **aucun autre** prérequis n'a bougé. Le nom
`HAMMER` de mnllib n'est plus une déclaration que personne n'utilise, il
est confirmé par l'observation, et avec lui la correspondance
bit → capacité pour toute la plage.

Deux acquis annexes au même dump :

- `0x2019`, le Fire Flower écrit à la main la veille, est **toujours
  levé** après une session de jeu normale. Un bit posé par nous survit au
  jeu comme un bit posé par le jeu
- les 127 compteurs d'équipement valent tous exactement 2 après
  `tools/donner_gear.lua`, et l'octet du champ des badges juste après le
  bloc, `020564A6`, est resté à zéro. La primitive tient à 127 écritures
  sans déborder d'un octet

### Une plage de 80 bits qui monte d'un coup, **non expliqué**

Entre les deux dumps, 88 bits `Exxx` montent et **aucun ne retombe**,
alors qu'aucun trésor n'a été ramassé. Quatre-vingts d'entre eux forment
une plage contiguë, `0xEEE1` à `0xEF30`.

Deux raisons de le noter plutôt que de l'oublier. Cette plage est
au-dessus de `0xEDB4`, la borne haute des écritures de variables trouvées
dans `FEvent` : elle vient donc du code ARM, pas d'un script. Et un bloc
contigu de 80 sent la structure indexée, du genre de celles qui portent
des `location` : boutiques et quêtes restent le dernier chantier de
locations hors table.

Aucune de nos familles connues ne compte 80 éléments. **À tester**, en
prenant deux dumps encadrant un achat en boutique.

**Test fait le 7 août 2026, la piste boutique tombe.** `run53` avant tout
achat, `run54` après un Picnic Wear à 30 pièces, `run55` après des
Starched Socks à 250, sans bouger de la boutique ni ramasser quoi que ce
soit. Les 80 bits sont déjà tous levés au `run53` et **aucun ne bouge**.

Le compte des stocks achève l'hypothèse : `MData/MDataShopBuyList.dat`
porte 8 boutiques, 64 articles en stock final et 435 entrées tous états
confondus. Ni 80 ni rien qui s'en approche.

Ce qu'on sait maintenant de la plage : elle est passée de 0 à 80 entre le
`run51` et le `run52` du 5 août, c'est-à-dire pendant la séquence qui va
du Green Shell au marteau, et elle n'a plus bougé depuis. Le voisinage
s'est étoffé de son côté : au `run55`, la zone `0xEE20` à `0xEF30` porte
95 bits levés, 15 épars en dessous de `0xEE60` plus le bloc contigu.
Aucun n'est une pièce d'attaque, qui vont de `0xE700` à `0xE821`.

Reste **non expliqué**, et le prochain test utile n'est plus la boutique
mais une paire de dumps serrée autour d'un événement d'histoire.

### Une boutique ne laisse aucun drapeau, **Vérifié**

Même mesure, autre question, et le résultat est plus important que celui
qu'on cherchait.

Un achat change exactement deux choses dans l'état connu : le compteur de
pièces, `1434` puis `1404` puis `1154`, soit les 30 et les 250 annoncés,
et le compteur d'équipement de l'objet acheté, identifiant 2 pour Picnic
Wear de 3 à 4, identifiant 24 pour Starched Socks de 2 à 3. **Aucun bit
`Exxx`, aucun bit `2xxx`.**

Tout le reste qui bouge entre les dumps se situe au-dessus de
`0x0564B4`, hors du bloc d'inventaire, et porte des valeurs comme
`0x03808178`, des adresses de Shared WRAM. C'est une zone de travail à
pointeurs, pas de l'état de joueur.

**Conséquence pour l'APWorld.** Un achat en boutique ne peut pas être
une `location` détectée par un drapeau, puisqu'il n'en laisse aucun. Les
deux voies restantes sont de surveiller le compteur de l'objet, fragile
puisqu'un objet s'obtient aussi ailleurs et se consomme, ou de patcher la
ROM. Randoglobin a choisi le patch, `main.py:899-909` parle d'un
`shop_patch` et de trois options `rando_ishop`, `rando_gshop`,
`rando_bshop` : il randomise **ce que la boutique vend** au lieu de faire
de l'achat un check. C'est en GPL-3.0, donc à lire et non à recopier.

### Découpage `Exxx` selon mnllib

`vendor/mnllib.py/mnllib/bis/consts.py:96-109` déclare douze plages,
dont `TREASURE range(0xE000, 0xE400)`, `ENEMY range(0xE400, 0xE700)` et
`STORY range(0xE700, 0x10000)`. Les entiers simples sont étendus en
`range(X, (X|0x0FFF)+1)` par `utils.py:22-28`.

À corriger dans nos notes : `STORY` va jusqu'à `0xFFFF` et non `0xEFFF`,
ce qui est cohérent avec `Exxx` et `Fxxx` traités comme un seul tableau.

**Ne pas promouvoir cette source.** Il serait tentant d'y voir du code
plutôt qu'une affirmation Discord, donc plus fiable. Trois raisons de ne
pas le faire : mnllib vient de la même communauté, `VariableType` n'est
importé ni utilisé nulle part ailleurs dans la bibliothèque donc rien ne
casserait si les bornes étaient fausses, et le jumeau Dream Team marque
`TREASURE` et `ENEMY` d'un `# TODO` (`mnllib/dt/consts.py:90-91`).
Surtout, **aucune occurrence de `560C8` dans mnllib** : rien n'y relie
ces identifiants de variables au champ de bits de la Main RAM. Ce pont
reste **à tester**.

## Écarté

`EObjSave/EObjSave.dat` ne contient aucun état de sauvegarde malgré son
nom, seulement des palettes graphiques. Source
`vendor/Randoglobin/randoglobin/palette.py` lignes 743 à 778.
