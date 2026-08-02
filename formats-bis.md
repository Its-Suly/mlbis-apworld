# Formats internes de BIS

Détail des structures confirmées. Sorti de `CLAUDE.md` le 2 août 2026
pour le garder sous son seuil de 220 lignes. `CLAUDE.md` n'en conserve
que le résumé et pointe ici. Toute nouvelle structure confirmée vient
dans ce fichier ; seule la conséquence pratique remonte dans `CLAUDE.md`.

Étiquettes de statut identiques à celles de `CLAUDE.md` : **Vérifié**
avec fichier et ligne, **Hypothèse**, **À tester**.

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
| `Main RAM` | 4 Mo attendus, à confirmer |
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

**Hypothèse forte** : le domaine `SRAM` est le fichier de sauvegarde.
Ses 8192 octets contiennent tout juste les 8136 octets qu'occupe la
structure décrite plus haut, jusqu'à `0x0FE8 + 0x7EC + 0x5F4`. Si elle
se confirme, la sauvegarde est lisible en direct sans passer par un
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
base = 0x0560C8 dans Main RAM
bit du trésor d'identifiant N  ->  octet 0x0560C8 + N // 8, bit N % 8
champ = 95 octets, de 0x0560C8 a 0x056126, pour 758 identifiants
```

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

**À tester** : sur un bloc à `max_hits` supérieur à 1, le bit monte-t-il
au premier coup ou à l'épuisement du bloc ? L'identifiant 546 porte
`quantity = 0` et `max_hits = 10`, et le comportement observé en jeu est
bien une pièce par saut dans une fenêtre de quelques secondes, ce qui
valide le décodage de `max_hits`. Mais l'instant où le flag tombe reste
inconnu, et il détermine quand une `location` sera considérée comme
validée.

**Rappel utile** : le domaine `SRAM` n'a pas bougé d'un octet pendant
l'expérience. Le jeu n'écrit dans la sauvegarde qu'au moment d'une
sauvegarde explicite, le champ de bits vit d'abord en RAM de travail.

## Variables de script

**Vérifié** : les flags de progression sont des variables de script.
`Variables[0x200E]` vaut 0 tant que le Bloc Aspirateur n'est pas acquis.
Source `vendor/Randoglobin/randoglobin/mnlscript_skips.py` ligne 1568,
commentaire explicite.

**Vérifié** : un acteur de script porte un champ encodant
`(variable << 16) + index_de_subroutine`, ce qui conditionne son
comportement à une variable. Source même fichier, ligne 535.

**Hypothèse** : les variables `0x2000` à `0x203F` sont 64 flags d'un bit
stockés dans les 8 octets à `slot + 0x0124`. Cheatoglobin y lit
exactement 8 octets nommés `var_2xxx` et les manipule au bit près
(`window.py` ligne 144, `save_file_tab.py` lignes 48 et 55). Toutes les
variables `0x2xxx` vues dans Randoglobin sont inférieures à `0x2040`.

Plages de variables vues dans Randoglobin, par fréquence décroissante :
`0xEAxx`, `0xEBxx`, `0x90xx`, `0xA0xx`, `0x60xx`, `0x30xx`, `0xE9xx`,
`0xE7xx`, `0x10xx`, `0xE8xx`, `0x20xx`, `0x50xx`, `0xC0xx`, `0xB0xx`,
`0xD0xx`. Leur sémantique respective n'est pas documentée.

## Écarté

`EObjSave/EObjSave.dat` ne contient aucun état de sauvegarde malgré son
nom, seulement des palettes graphiques. Source
`vendor/Randoglobin/randoglobin/palette.py` lignes 743 à 778.
