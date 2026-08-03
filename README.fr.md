# APWorld Archipelago pour Mario & Luigi : Voyage au Centre de Bowser

Travail de recherche en vue d'un monde [Archipelago](https://archipelago.gg)
pour *Mario & Luigi : Voyage au Centre de Bowser* (Nintendo DS, 2009).
Aucun monde n'existe à ce jour pour ce jeu.

*[English version](README.md)*

## État : faisabilité, et elle est acquise

**Aucune ligne d'APWorld n'est encore écrite.** Ce dépôt contient de la
recherche, des tables de données extraites, et les outils qui les
produisent.

La question qui bloquait tout le projet s'énonçait simplement et
n'avait de réponse dans aucune source disponible : **comment le jeu
retient-il qu'un trésor a déjà été ramassé ?** Sans ça, impossible de
marquer une `location` Archipelago comme validée, et aucun monde n'est
constructible.

Cette question a maintenant sa réponse.

### Le champ de bits des trésors

Les trésors ramassés sont suivis par des bits dans la RAM principale du
NDS :

```
trésor d'identifiant N  ->  octet 020560C8 + N/8, bit N%8   (LSB en premier)
```

Cette adresse n'héberge pas une structure dédiée aux trésors. C'est le
tableau de bits global des variables de script `Exxx`, 4096 éléments,
`0x200` octets, nommé par le [manuel de 8y8x](https://inf.gg/mlbis/manual).
Les trésors en occupent les index bas : les identifiants 0 à 757 tiennent
dans les 95 premiers octets. Le tableau vit dans le BSS de l'ARM9, donc à
adresse fixe pour toute la partie, hors des overlays et hors des heaps.

Le rang du bit est l'identifiant stocké dans les octets 4-5 de chaque
entrée de `Treasure/TreasureInfo.dat` — un champ que le randomizer
existant ne lit jamais.

Vérifié sur les quatre blocs d'une même salle, identifiants 544 à 547,
tous logés dans l'octet `0x05610C`, au fil de cinq dumps successifs :

| Dump | Octet | Bits allumés | Identifiants |
|---|---|---|---|
| 1 | `0x00` | — | aucun |
| 2 | `0x01` | 0 | 544 |
| 3 | `0x03` | 0, 1 | 544, 545 |
| 4 | `0x0B` | 0, 1, 3 | 544, 545, 547 |
| 5 | `0x0F` | 0, 1, 2, 3 | 544, 545, 546, 547 |

Les deux derniers blocs ont été frappés dans l'ordre inverse, si bien
que le bit 3 s'allume avant le bit 2. Les bits suivent les identifiants
de la table et non l'ordre des actions du joueur, ce qui écarte
l'explication concurrente d'un compteur séquentiel de ramassages.

### À quel moment le flag tombe

Un bloc peut tenir plusieurs coups : l'identifiant 546 donne une pièce
par saut, dix fois. Mesuré sur cinq dumps de plus, depuis un savestate
vierge :

| Dump | Octet `0x05610C` | État du bloc |
|---|---|---|
| `run06` | `0x00` | avant tout |
| `run07` | `0x00` | bloc frappé, pause immédiate |
| `run08` | `0x04` | première pièce prise, neuf disponibles |
| `run09` | `0x04` | avant-dernière pièce |
| `run10` | `0x04` | bloc épuisé |

**Le bit monte à la première pièce et non à l'épuisement**, donc une
`location` est validée dès le premier coup. Le `run07` ajoute un détail
utile : le bit ne monte pas à l'instant de la frappe mais quelques frames
plus tard. Il suit l'*attribution* de l'objet, pas le coup porté au bloc.

## Contenu

| Chemin | Contenu |
|---|---|
| `data/locations_bis.csv` | 685 entrées de trésor décodées : identifiant, type, objet nommé, quantité, salle, coordonnées |
| `data/noms_items.csv` | 204 noms d'objets extraits de la ROM |
| `data/noms_zones.csv` | Les 32 zones nommées du jeu |
| `tools/` | Extraction ROM, dump de RAM, analyse de diff |
| `formats-bis.md` | Toutes les structures confirmées, avec fichier et ligne |
| `reference-mlss.md` | Dépouillement du monde Superstar Saga livré avec Archipelago |
| `CLAUDE.md` | Mémoire du projet : décisions figées, contraintes, questions ouvertes |
| `JOURNAL.md` | Journal daté, y compris les impasses et les bugs |

### Échelle

647 entrées de trésor exploitables : 281 blocs `?`, 197 haricots,
149 blocs brique, 20 touffes d'herbe, réparties sur 272 salles et
32 zones nommées. À titre de comparaison, le monde Superstar Saga
déclare 634 `location` : les deux jeux sont à la même échelle.

## Conventions de preuve

Toute affirmation de ce dépôt porte l'une de trois étiquettes, et la
règle est tenue de bout en bout :

- **Vérifié** — lu dans du code source ou mesuré, cité avec fichier et
  ligne
- **Hypothèse** — déduit d'un autre jeu ou d'un motif, pas encore
  confirmé
- **À tester** — rien ne permet de trancher

Sans source au niveau du fichier et de la ligne, c'est une hypothèse,
pas un fait. Une adresse mémoire plausible mais fausse coûte des heures
de debug.

## Reproduire les résultats

Il faut votre propre ROM, obtenue légalement. L'analyse statique vise
une révision précise :

- Mario & Luigi Bowser's Inside Story, NDS, région NA, pre-DSi
- SHA-256 `9126963d6c6b6f81a9a666ba766e223781ff286634486e2a56d07a4c82eef4f1`

```
py -3.13 -m venv venv
venv\Scripts\python.exe -m pip install ndspy .\vendor\mnllib.py
venv\Scripts\python.exe tools\extract_names.py
venv\Scripts\python.exe tools\build_location_table.py
```

Pour la mesure en direct, ouvrir `tools/dump_ram.lua` dans la console
Lua de BizHawk **2.10 exactement** — le connecteur Lua d'Archipelago
refuse les versions antérieures à 2.7.0 et avertit au-delà de 2.10 —
puis comparer les dumps avec `tools/cherche_champ_bits.py`.

Deux outils aident à lire ce qui en sort. `tools/treasure_bit.py` traduit
un identifiant de trésor en adresse et rang de bit, et inversement.
`tools/compare_block.py` cherche le tableau de la RAM dans un dump de la
sauvegarde. Les 95 octets qui portent les flags, pour les dix dumps, sont
publiés dans `data/preuve_champ_bits.txt` : les dumps de 4 Mo eux-mêmes
ne le sont pas, mais ce fichier suffit à contrôler le résultat.

## Au sujet de la ROM

**Aucune ROM n'est présente dans ce dépôt, et aucune ne sera fournie.**
Le `.gitignore` exclut les `.nds`, `.7z`, `.zip` et les fichiers de
sauvegarde. Toutes les tables de `data/` sont régénérées depuis une ROM
locale que vous fournissez vous-même, rien n'est saisi à la main.

## Remerciements et sources

Ce travail repose entièrement sur la recherche communautaire
antérieure. **[SOURCES.md](SOURCES.md) recense chaque source avec son
URL, le commit exact consulté, sa licence, et ce qui en a été tiré.**

- La communauté [MnL-Modding](https://github.com/MnL-Modding) et son
  [Discord](https://discord.gg/rhJ6HGyymJ) — Randoglobin pour les
  tables de trésors et d'objets, Cheatoglobin pour la structure de
  sauvegarde, `mnllib` pour les formats internes, BIS-docs pour les
  commandes de script
- Le [manuel de 8y8x](https://inf.gg/mlbis/manual), en CC0 — il met un
  nom sur le tableau `Exxx` que nous avions localisé à la mesure, donne
  le bloc des registres globaux et le plan mémoire de l'ARM9, et
  confirme de son côté la révision de ROM visée ici
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago), et en
  particulier son `worlds/mlss` intégré, le monde Superstar Saga, qui
  avait déjà résolu ce type de problème pour le premier jeu de la série

Randoglobin et Cheatoglobin sont sous GPL-3.0-or-later. Ils ont été
**lus pour comprendre**, et des faits en ont été tirés — offsets,
formats de fichiers, dispositions de champs. **Aucun code n'a été
recopié.** En réutiliser le code imposerait la GPL à l'APWorld obtenu.
`mnllib` est en LGPL-3.0 et *est* utilisé comme dépendance, ce que sa
licence autorise.

Si vous estimez qu'une partie de ce dépôt reproduit votre code au lieu
de reformuler un fait qui en a été appris, ouvrez une issue et elle
sera retirée.

## Licence

[MIT](LICENSE) pour le travail original de ce dépôt — les outils, la
documentation et les tables qu'ils produisent. Elle ne peut pas couvrir
le jeu lui-même : les noms et identifiants de `data/` sont extraits
d'une ROM commerciale et restent la propriété de leurs ayants droit.
Les projets tiers gardent leurs propres licences, recensées dans
[SOURCES.md](SOURCES.md).
