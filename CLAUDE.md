# Projet APWorld BIS

Développement d'un APWorld Archipelago pour Mario & Luigi : Voyage au
Centre de Bowser, version NDS de 2009. Phase actuelle : faisabilité.
Rien n'est encore écrit.

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

- **Python 3.13.** Intersection entre Archipelago, qui exige 3.11.9
  minimum et strictement moins de 3.14, et Randoglobin, qui exige 3.12
  minimum et strictement moins de 3.15
- **BizHawk 2.10 exactement.** Le connector Lua d'Archipelago
  (`data/lua/connector_bizhawk_generic.lua`, lignes 633 à 637) refuse
  les versions antérieures à 2.7.0 et avertit au-delà de 2.10. Ne pas
  installer la dernière version publiée

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

- Le jeu alterne entre Mario et Luigi dans le corps de Bowser, et
  Bowser à l'extérieur, avec des inventaires et capacités distincts. Il
  y a plusieurs structures à suivre, pas une seule
- Écrire en mémoire pendant un combat ou une cinématique est le moyen
  le plus sûr de faire planter la ROM. Toute proposition d'injection
  doit préciser dans quel état du jeu elle s'exécute et comment cet
  état est détecté

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

Ne pas écrire ici :

- Le récit de ce qui a été fait pendant une session
- Les pistes explorées sans conclusion
- Les erreurs de manipulation et leurs corrections
- Les commandes tapées

Tout ça va dans `JOURNAL.md` à la racine du projet, qui n'est pas
chargé automatiquement. Y écrire librement, en datant chaque entrée.
Le créer s'il n'existe pas.

Ce fichier fait 218 lignes au 3 août 2026, à deux lignes du plafond.
S'il dépasse 220 lignes, le signaler et proposer ce qui peut en sortir
plutôt que de continuer à ajouter. Premier candidat à la sortie : la
section « Particularités du jeu », vers `formats-bis.md`.

## Sources, du plus fiable au moins fiable

URL, commits consultés, licences et attributions : `SOURCES.md`.
Ordre de fiabilité à respecter :

1. **`vendor/Archipelago/worlds/mlss`**, l'APWorld Superstar Saga,
   livré dans le cœur d'Archipelago. Même série, même studio, BIS en
   est la suite directe. Modèle de référence pour l'architecture, la
   logique et les conventions. Dépouillé dans `reference-mlss.md`
2. Doc Archipelago : `world api.md`, `apworld specification.md`,
   `apworld_dev_faq.md`, `network protocol.md`
3. Code d'un APWorld NDS existant, Pokémon Mystery Dungeon Explorers of
   Sky ou Pokémon Black and White
4. Écosystème MnL-Modding, ses outils puis sa documentation, dont
   `inf.gg/mlbis/manual`, en CC0 donc réutilisable sans contrainte
5. Discussions communautaires, à traiter comme des pistes

## Acquis à ne pas redécouvrir

- **Commandes de script** : table dans `overlay_0006.bin`, plage
  commune, commandes d'objets `0x0043` et `0x0044`, injection ARM.
  Détail et sources dans `formats-bis.md`

### Structures confirmées, détail dans `formats-bis.md`

- **Sauvegarde** : magie `MLRPG3`, deux slots à `0x0010` et `0x0FE8`.
  Le slot porte un checksum sur ses `0x5F2` premiers octets et une
  copie de secours à `slot + 0x7EC`. **Toute écriture doit recalculer
  le checksum et répliquer la copie**, sinon le slot est rejeté
- **Locations candidates** : `Treasure/TreasureInfo.dat`, entrées de
  12 octets, **647 exploitables** dont 281 blocs `?` et 197 haricots.
  Les octets 4-5 portent un identifiant unique de 0 à 757, qui est le
  rang du bit de flag. Numéro de `location` naturel
- **Flags** : dans `Exxx`, les trésors partent de `0xE000`, les ennemis
  de `0xE400`, l'histoire de `0xE700`. Les `0x2xxx` sont 64 bits, à
  `02056038` en RAM et à `slot + 0x0124` dans la sauvegarde
- **Écarté** : `EObjSave/EObjSave.dat` ne contient que des palettes,
  pas d'état de sauvegarde
- **32 zones** nommées dans `mfset_EMesPlace.dat`, table `0x44` pour
  l'anglais. Index 1 à 12 dehors, 13 à 30 dans Bowser, 31 `Challenge
  Node`. Base naturelle du découpage en `region`

### Tables déjà extraites, dans `data/`

Régénérables par `tools/extract_names.py` puis
`tools/build_location_table.py`, dans le venv `venv/` de la racine.

- `locations_bis.csv` : les 685 entrées de trésor décodées, avec
  identifiant, type, objet nommé, quantité, salle et coordonnées
- `noms_items.csv` : 204 objets nommés, tous types confondus
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

- **Risque principal** : livrer un item dans le jeu qui tourne n'a
  jamais été testé. La détection est acquise, l'écriture non
- Le champ est recopié à `slot + 0x01B4`, d'après le décompilé de
  l'overlay 129 montré sur Discord. À confirmer par notre mesure
- Les flags des trésors hors `TreasureInfo.dat` sont des flags de
  cinématique, à lire via `mnlscript`, ce n'est pas une table à dumper
