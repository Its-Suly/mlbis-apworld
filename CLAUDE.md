# Projet APWorld BIS

Développement d'un APWorld Archipelago pour Mario & Luigi : Voyage au
Centre de Bowser, version NDS de 2009. Phase actuelle : faisabilité.
Rien n'est encore écrit.

## Version de ROM, figée

Ne jamais raisonner sur une autre version.

- Mario & Luigi Bowser's Inside Story, NDS, région NA, révision pre-DSi
- SHA-256 `9126963d6c6b6f81a9a666ba766e223781ff286634486e2a56d07a4c82eef4f1`
- Vérifiée le 27 juillet 2026 contre les références de
  `randoglobin/main.py` lignes 189 à 196
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

Randoglobin est sous GPL-3.0-or-later. Le lire pour comprendre est
libre. En recopier du code imposerait la GPL à l'APWorld. Signaler
l'implication dès qu'il est question de réutiliser plutôt que de
s'inspirer.

## Contraintes d'empaquetage APWorld

Erreurs classiques dont le message ne pointe pas vers la vraie cause.

- Le fichier `.apworld` doit être entièrement en minuscules
- Le zip doit contenir un dossier au nom exactement identique au zip
- Imports internes au monde en relatif (`from .options import ...`)
- Imports vers le cœur d'Archipelago en absolu
  (`from worlds.AutoWorld import World`)
- L'empaquetage passe par le composant Build APWorlds du launcher, qui
  ajoute lui-même `version` et `compatible_version`. Ne jamais les
  écrire à la main

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

Ce fichier fait environ 175 lignes au 27 juillet 2026. S'il dépasse
220 lignes, le signaler et proposer ce qui peut en sortir plutôt que
de continuer à ajouter.

## Sources, du plus fiable au moins fiable

1. Doc Archipelago : `world api.md`, `apworld specification.md`,
   `apworld_dev_faq.md`, `network protocol.md`
2. Code d'un APWorld NDS existant, par exemple Pokémon Mystery Dungeon
   Explorers of Sky ou Pokémon Black and White
3. Écosystème MnL-Modding : Randoglobin pour les tables d'objets,
   Cheatoglobin pour la structure de sauvegarde, mnllib et mnlscript
   pour les formats internes
4. Documentation MnL-Modding, https://mnl-modding.github.io/BIS-docs/
5. Discussions communautaires, à traiter comme des pistes

## Acquis à ne pas redécouvrir

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
  `randoglobin/files/bis.zip`
- La copie de la doc des commandes présente sur le Google Drive de
  MnL-Modding date de septembre 2024 et est périmée. Régénérer depuis
  `cutscene_code/bisdocs.py` du dépôt BIS-docs

## Non résolu

Comment le jeu retient qu'un bloc a déjà été frappé. Aucune source
consultée à ce jour ne documente les flags de progression ni la
structure de sauvegarde. C'est le point bloquant de la faisabilité.
