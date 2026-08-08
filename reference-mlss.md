# L'APWorld Superstar Saga comme modèle

Découvert le 2 août 2026. `vendor/Archipelago/worlds/mlss` est livré
dans le cœur d'Archipelago 0.6.8, donc il était sur le disque depuis le
clone du 27 juillet sans qu'on le sache.

Superstar Saga est le premier Mario & Luigi, BIS le troisième, même
studio AlphaDream. C'est le précédent le plus proche qui existe.

Tout ce qui suit est **Vérifié**, lu dans le code à l'emplacement
indiqué. Les adresses citées sont **celles de Superstar Saga sur GBA**
et ne valent rien pour BIS : autre console, autre plan mémoire, autre
processeur. Ce qui se transpose, c'est la structure du code, pas les
nombres.

## Taille du monde

| Fichier | Lignes |
|---|---|
| `Data.py` | 5705 |
| `Locations.py` | 1192 |
| `Rules.py` | 809 |
| `Names/LocationName.py` | 559 |
| `Rom.py` | 434 |
| `Regions.py` | 335 |
| `Options.py` | 337 |
| `Client.py` | 290 |
| `Items.py` | 198 |
| `__init__.py` | 182 |
| `StateLogic.py` | 172 |

Environ 10 200 lignes au total. `Locations.py` déclare 634 locations.
BIS en a 647 candidates rien qu'en trésors : les deux jeux sont à la
même échelle, ce qui rend la comparaison légitime de bout en bout.

## Le point qui nous intéresse le plus : la détection des blocs

`Client.py` ligne 93 lit **59 octets à `0x4564` en EWRAM**, soit
472 bits. Puis lignes 217 à 223 :

- boucle sur chaque octet, puis sur chacun de ses 8 bits
- `flag_id = byte_i * 8 + (j + 1)`
- `find_key(roomCount, flag_id)` convertit cet identifiant global en
  couple salle + numéro de trésor dans la salle, `roomCount`
  (`Locations.py` ligne 887) donnant le nombre de trésors par salle
- lignes 225 à 234, l'identifiant est résolu en pointeur ROM via un
  tableau de salles à `ROOM_ARRAY_POINTER = 0x51FA00`

**Autrement dit : un bit par trésor, dans un champ de bits contigu,
indexé par un identifiant séquentiel.** C'est très exactement la
structure supposée pour BIS à partir du champ octets 4-5 de
`TreasureInfo.dat`.

Nuance à ne pas gommer : MLSS lit la **RAM de travail** en cours de
partie, pas le fichier de sauvegarde. La correspondance avec
l'hypothèse BIS, qui porte sur le `.sav`, reste à établir. Ce que MLSS
prouve, c'est que le studio a employé ce motif ; pas qu'il l'a employé
au même endroit dans BIS.

## Architecture générale

- ROM patchée plus client BizHawk. `Client.py` ligne 21 hérite de
  `BizHawkClient`, `patch_suffix = ".apmlss"`
- Le monde s'appuie sur `worlds/_bizhawk`, le même connecteur
  générique dont `MEMOIRE.md` fixe la contrainte de version d'émulateur
- **Réception d'un item** : le client écrit l'identifiant de l'objet à
  l'adresse EWRAM `0x3057`, du code ASM injecté le lit en boucle,
  donne l'objet, puis remet l'adresse à zéro. Le client utilise
  `guarded_write` en vérifiant que l'adresse vaut bien `0x0` avant
  d'écrire, sinon il réessaie plus tard. `Client.py` lignes 134 à 162
- Ce motif de poignée de main évite d'écrire pendant que le jeu n'est
  pas prêt. C'est la réponse concrète à la contrainte de `MEMOIRE.md`
  sur les écritures en combat ou en cinématique
- **Garde-fou d'identité** : le client relit une signature `MLSSAP` à
  l'adresse `0x3060` et abandonne le tour si elle ne correspond pas
  (lignes 111, 116, 181). Protection contre une ROM non patchée ou un
  état mémoire non initialisé

Pour BIS, Randoglobin injecte déjà du code ARM custom et embarque une
chaîne `armv5te-none-eabi`, donc ce chemin est praticable.

## Logique et règles

`StateLogic.py` est un fichier de petites fonctions
`nom(state, player)` renvoyant un booléen, une par capacité :
`canDig`, `canMini`, `canDash`, `canCrash`, `hammers`, `super`,
`ultra`, `castleTown`, `fungitown`, et une par boutique. `Rules.py` les
compose.

Détail transposable tel quel : une capacité n'est pas un objet unique
mais une **combinaison**. `canDig` exige le Green Goblet **et** les
Hammers, `canDash` exige le Red Pearl Bean **et** Firebrand
(`StateLogic.py` lignes 4 à 18). Les marteaux se comptent :
`super` vaut `state.has("Hammers", player, 2)`, `ultra` en exige 3.
C'est le motif à reprendre pour les capacités de duo de BIS.

## Le piège des conditions indirectes est réel

`MEMOIRE.md` avertit sur `register_indirect_condition`. MLSS l'appelle
**onze fois** dans `Regions.py`, lignes 150, 174 à 177, 191 à 193, 203,
204 et 218, toutes sur des régions de type « Flag » qui conditionnent
l'accès à des boutiques. Ce n'est pas un piège théorique et on a ici un
exemple qui fonctionne.

## Ce qui ne se transpose pas

- Toute adresse mémoire. GBA contre NDS
- Les domaines mémoire `EWRAM` et `IWRAM` passés à `bizhawk.read` sont
  ceux de la GBA. Le NDS expose d'autres noms de domaines, à relever
  dans BizHawk avant d'écrire la moindre ligne de client
- Le format de patch et le code ASM, écrits pour la GBA

## Décisions d'architecture, étudiées le 4 août 2026

### La forme à copier

**Vérifié.** Le triplet `(adresse, masque de bit, id de location)` de
`nonBlock` (`Locations.py:776+`), testé par `flag_byte & mask != 0`
(`Client.py:179-184`), est la structure minimale d'un flag lu à la volée.
Chez nous elle se réduit à `(index de bit Exxx, id de location)`, notre
champ à `020560C8` étant déjà un tableau de bits homogène.

**Vérifié.** MLSS ne sépare pas ses locations « hors bloc » dans un
fichier à part : les 600 `LocationData` sont toutes dans `Locations.py`.
La forme à retenir est un **champ descripteur dans la `LocationData`**,
pas des listes parallèles.

**Vérifié, esprit à copier.** `Client.py:93` lit 59 octets et
`sum(roomCount.values()) = 472 = 59 × 8` exactement, en bijection avec
`flag_id = octet × 8 + rang`. Aucun trou, aucun bourrage. Notre champ
`Exxx` a la même propriété, en mieux : il est indexé **directement** par
l'identifiant de `TreasureInfo.dat`.

### La machinerie à ne pas reproduire

**Vérifié.** MLSS reconstruit l'adresse d'un flag depuis un couple
(salle, rang) par soustraction cumulative, lit un pointeur 32 bits en ROM
à `0x51FA00 + (salle-1)*4`, le masque avec `0xFFFFFF`, lit un octet
d'en-tête, décale de 2 de plus s'il est non nul, puis ajoute
`rang*8 + 1` (`Client.py:16, 225-238`), plus un remapping de 16 haricots.

Nous n'avons besoin d'aucune de ces étapes. **C'est un avantage net à ne
pas gaspiller en réintroduisant une indirection.**

### L'identifiant de location est l'offset ROM, et ça ne se transpose pas

**Vérifié.** L'id Archipelago d'une location MLSS **est** l'offset ROM où
l'item sera écrit, sans `base_id`. Chaîne complète : `Locations.py:6-10`
et `81+` → `1159-1192` → `__init__.py:68` → `Regions.py:303` avec
`BaseClasses.py:1485-1489` → `Rom.py:334-340` → `375-403` →
`Files.py:507-508`. 600 locations, ids de `0x1E9403` à `0x3C06A2`.

**Ça ne marche que parce que la cible est un fichier ROM plat.** Sur NDS
l'écriture vise un fichier du système de fichiers du `.nds`, pas un
offset absolu stable. Le raccourci reste possible avec l'identifiant
unique 0-757 de `TreasureInfo.dat`, mais **il ne couvre pas les locations
hors table**. Il faudra leur choisir une plage, et **cette plage devient
un contrat gelé dès la première seed publiée**.

### Deux descripteurs, pas un

**Tombée après vérification, et c'était très tentant** : l'idée que
`itemType` encode la nature du point d'injection, 0 pour un bloc, 1 pour
un script de cutscene, 3 pour une boutique. Faux. `itemType` ne
sélectionne que **l'encodage de l'écriture** dans `item_inject`
(`Rom.py:370-403`) : 1 octet brut, ou 2 octets à quartets permutés, ou
1 octet après remapping. `Locations.py:428` met « Shop Chuckolator Flag »
en type 3 quand les « Pants Shop » juste en dessous sont en type 2, selon
la famille d'objets vendue et non selon la table.

Sur 78 tuples `nonBlock`, 47 pointent vers du type 1 et 23 vers du
type 2 ; inversement 16 locations de type 1 ne sont pas dans `nonBlock`.
Seule implication qui tienne : aucune entrée de `nonBlock` ne pointe vers
du type 0.

**À en tirer pour BIS : prévoir deux descripteurs séparés par location**,
un pour l'encodage de l'écriture, un pour la source du flag de
validation. Ce sont deux axes orthogonaux.

### MLSS ne répond pas à notre question sur l'état du jeu

`Client.py:99, 111, 116-117` lit 6 octets à `0x3060` et les compare à
`"MLSSAP"`, avec `return` si écart. **Hypothèse** : c'est un témoin de
présence du patch, écrit par `data/basepatch.bsdiff`, aucun fichier de
`worlds/mlss` ne l'écrit. Vu son voisinage avec le bloc de travail AP,
c'est plus vraisemblablement un contrôle d'initialisation qu'un garde-fou
d'état.

**Autrement dit MLSS n'a rien qui protège contre une écriture pendant un
combat ou une cinématique.** Notre contrainte reste entière et sans
modèle.

### Un piège de conception à connaître

`Locations.py:807-813` donne aux 7 récompenses de café sept bits
distincts, et `Client.py:207-212` réattribue pourtant le k-ième flag
rencontré à `eReward[k-1]`. Le bit identifie *quelle* récompense, alors
qu'Archipelago veut numéroter *le rang* d'obtention. Cas réel de flag
partagé : `Locations.py:777-778`, Farm Mole 1 et 2 sur le même
`(0x434B, 0x1)`.

La question « le flag identifie-t-il la location ou le rang d'obtention »
se pose **location par location**, pas globalement.
