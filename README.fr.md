# APWorld Archipelago pour Mario & Luigi : Voyage au Centre de Bowser

Un monde [Archipelago](https://archipelago.gg) pour *Mario & Luigi :
Voyage au Centre de Bowser* (Nintendo DS, 2009). Il n'en existait aucun
avant celui-ci.

*[English version](README.md)*

## État : ça marche, et ça a été joué

La boucle complète tourne, vérifiée en jeu et non déduite du code : les
checks sont détectés et envoyés, les objets reviennent et sont écrits
dans le jeu en cours, et l'objet d'un second joueur a traversé depuis un
autre monde, puis dans l'autre sens.

- **728 locations**, 647 entrées de trésor et 81 blocs de pièces
  d'attaque
- **Neuf capacités devenues des objets**, le marteau compris, mélangées
  dans le sac commun du multiworld
- **La ROM n'est jamais modifiée.** Tout passe par la mémoire pendant
  qu'on joue, donc pas d'étape de patch et pas de copie patchée à garder
- Empaqueté en `dist/mlbis.apworld`, qui génère une seed à lui seul
- Passe les 206 tests généraux d'Archipelago, plus deux suites à nous

Ce qui n'est **pas** réglé est la logique d'accès, et la section des
limites dit exactement jusqu'où lui faire confiance.

## Y jouer

Il faut BizHawk **2.10 exactement** et votre propre exemplaire du jeu.
Seule la machine qui génère la seed a besoin de l'apworld ; les joueurs
des autres jeux n'ont rien à prendre ici.

Les instructions complètes sont dans
[`mlbis/docs/setup_en.md`](mlbis/docs/setup_en.md). En bref : déposer
`mlbis.apworld` dans le dossier `custom_worlds` d'Archipelago, générer,
ouvrir `connector_bizhawk_generic.lua` **depuis son propre dossier**
dans la console Lua de BizHawk, puis lancer le client BizHawk.

### Options

| Option | Ce qu'elle décide |
|---|---|
| `shuffle_abilities` | les neuf capacités deviennent des objets à trouver |
| `safe_ability_placement` | les garde là où la logique est sûre |
| `goal` | `abilities` termine tout seul, `manual` vous donne `/bis_goal` |
| `filler_variety` | corrige les 27 % de haricots du sac d'origine |

## Comment ça marche

Trois faits mesurés portent tout le monde.

**L'identifiant d'un trésor est son rang de bit.** Les trésors ramassés
sont suivis dans le tableau de drapeaux `Exxx` à `020560C8` :

```
trésor d'identifiant N  ->  octet 020560C8 + N/8, bit N%8   (poids faible d'abord)
```

Cet identifiant vit dans les octets 4-5 de chaque entrée de
`Treasure/TreasureInfo.dat`, donc l'identifiant de location Archipelago
vaut `BASE_ID + rang de bit`, **sans aucune table de correspondance**.
Les pièces d'attaque utilisent le même tableau plus haut et ne demandent
aucun cas particulier. Le bit se pose au **premier** coup porté à un
bloc, pas à son épuisement, donc une location part dès que le joueur
voit quelque chose.

**Les objets se livrent en écrivant en mémoire.** Pièces à `02056400`,
consommables à `02056406 + index`, équipement à `02056427 + id - 1`,
tous vérifiés en jeu. Une valeur écrite est adoptée, affichée,
sauvegardée, et le jeu recalcule son propre checksum.

**Une capacité peut être retirée.** Abaisser son bit dans le champ
`2xxx` la reprend : le marteau disparaît de la commande de combat et
revient quand le bit remonte. C'est ce qui rend les capacités
échangeables sans patcher la ROM, puisque le jeu continue de les offrir
aux moments prévus et que le client les reprend aussitôt.

Chaque structure, avec la mesure qui l'a établie, est dans
[`formats-bis.md`](formats-bis.md).

## Les limites, dites franchement

**La logique d'accès raisonne au grain de la zone, et l'ordre de ces
zones vient d'un guide, pas du jeu.** Quatre tentatives pour le déduire
de la ROM ont échoué, chacune tuée par une mesure et chacune écrite pour
que personne ne les refasse. Pire, ce jeu fait revisiter ses zones, donc
un trésor d'un recoin tardif d'une zone précoce paraît accessible bien
trop tôt.

Ça ne met une partie en danger que si une capacité atterrit dans un
endroit inatteignable, d'où `safe_ability_placement`, actif par défaut :
les neuf capacités restent dans les cinq premières zones, la partie de
l'ordre qu'un guide énonce explicitement et qu'une vraie sauvegarde
confirme de son côté. Les objets ordinaires vont où ils veulent, en
trouver un tard ne coûte rien.

**Le but n'est pas « battre Dark Bowser ».** Plus de 800 000 commandes
de script ont été lues, terrain et combat compris, et la fin ne laisse
aucune marque qu'un client saurait reconnaître. Plutôt que de deviner
une adresse, la partie se termine soit quand les neuf capacités sont
réunies, soit quand le joueur tape `/bis_goal`.

**Jamais menée jusqu'au bout.** La boucle, le multiworld et la
reconnexion sont mesurés, mais aucune seed n'a été jouée jusqu'à la fin.
C'est la prochaine étape, et elle fournira aussi les deux mesures
manquantes.

## Ce qu'il y a ici

| Chemin | Contenu |
|---|---|
| `mlbis/` | le monde lui-même : locations, items, régions, options, client |
| `data/` | tables extraites de la ROM, toutes régénérables |
| `tools/` | extraction, dumps de RAM, analyse d'écarts, les trois suites de tests |
| `formats-bis.md` | chaque structure confirmée, avec fichier et ligne |
| `reference-mlss.md` | étude du monde Superstar Saga livré avec Archipelago |
| `CLAUDE.md` | mémoire du projet : décisions figées, contraintes, points ouverts |
| `JOURNAL.md` | journal daté, y compris les impasses et les bugs |

Trois suites de tests, depuis la racine du dépôt :

```
venv\Scripts\python.exe tools\test_generation.py    une seed sort
venv\Scripts\python.exe tools\test_client.py        bits, adresses, livraison
venv\Scripts\python.exe tools\test_archipelago.py   les 206 tests d'Archipelago
```

## Conventions de preuve

Chaque affirmation de ce dépôt porte une des trois étiquettes, et la
règle est tenue partout :

- **Vérifié** — lu dans le code source ou mesuré, cité avec fichier et
  ligne
- **Hypothèse** — déduit d'un autre jeu ou d'un motif, pas encore
  confirmé
- **À tester** — rien ne permet de trancher

Sans source au niveau du fichier et de la ligne, c'est une hypothèse et
non un fait. Une adresse plausible mais fausse coûte des heures de
debug, et ce dépôt garde les impasses qui le prouvent.

## Régénérer les tables

Il vous faut votre propre ROM, obtenue légalement. L'analyse statique
vise une révision et une seule :

- Mario & Luigi Bowser's Inside Story, NDS, Amérique du Nord, pre-DSi
- SHA-256 `9126963d6c6b6f81a9a666ba766e223781ff286634486e2a56d07a4c82eef4f1`

```
py -3.13 -m venv venv
venv\Scripts\python.exe -m pip install ndspy capstone .\vendor\mnllib.py
venv\Scripts\python.exe tools\extract_names.py
venv\Scripts\python.exe tools\build_location_table.py
venv\Scripts\python.exe tools\build_apworld_data.py
```

## À propos de la ROM

**Aucune ROM n'est incluse dans ce dépôt, et aucune ne sera fournie.**
Le `.gitignore` exclut `.nds`, `.7z`, `.zip` et les fichiers de
sauvegarde. Chaque table de `data/` est régénérée depuis une ROM locale
que vous fournissez ; rien n'a été saisi à la main.

## Crédits et sources

Ce travail repose entièrement sur des recherches communautaires
antérieures. **[SOURCES.md](SOURCES.md) liste chaque source avec son
URL, le commit exact consulté, sa licence, et ce qui en a été tiré.**

- La communauté [MnL-Modding](https://github.com/MnL-Modding) et son
  [Discord](https://discord.gg/rhJ6HGyymJ) — Randoglobin pour les tables
  de trésors et d'objets, Cheatoglobin pour la structure de sauvegarde,
  `mnllib` pour les formats internes, BIS-docs pour les commandes de
  script
- Le [manuel MLBIS de 8y8x](https://inf.gg/mlbis/manual), CC0, qui a
  nommé le tableau `Exxx` que nous avions localisé par la mesure, ainsi
  que le bloc de registres globaux et la carte mémoire de l'ARM9
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago), et en
  particulier son `worlds/mlss`, le monde Superstar Saga, qui avait déjà
  résolu cette classe de problème pour le premier jeu de la série

Randoglobin et Cheatoglobin sont en GPL-3.0-or-later. Ils ont été **lus
pour comprendre**, et des faits en ont été tirés : offsets, formats de
fichiers, dispositions de champs. **Aucun code n'a été recopié.**
Réutiliser leur code imposerait la GPL à l'APWorld. `mnllib` est en
LGPL-3.0 et *est* utilisé comme dépendance, ce que sa licence autorise.

Si vous estimez qu'une partie de ce dépôt reproduit votre code plutôt
que d'énoncer un fait appris de lui, ouvrez une issue et ce sera retiré.

## Licence

[MIT](LICENSE) pour le travail original ici : le monde, les outils, la
documentation et les tables qu'ils produisent. Elle ne peut pas couvrir
le jeu sous-jacent : les noms et identifiants de `data/` sont extraits
d'une ROM commerciale et restent la propriété de leurs ayants droit. Les
projets tiers gardent leurs licences, listées dans
[SOURCES.md](SOURCES.md).
