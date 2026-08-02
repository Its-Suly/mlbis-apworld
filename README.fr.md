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

Les trésors ramassés sont suivis par un champ de bits dans la RAM
principale du NDS :

```
trésor d'identifiant N  ->  octet 0x0560C8 + N/8, bit N%8   (LSB en premier)
champ de 0x0560C8 à 0x056126, 95 octets, 758 identifiants
```

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
