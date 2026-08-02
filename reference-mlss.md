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
  générique dont `CLAUDE.md` fixe la contrainte de version d'émulateur
- **Réception d'un item** : le client écrit l'identifiant de l'objet à
  l'adresse EWRAM `0x3057`, du code ASM injecté le lit en boucle,
  donne l'objet, puis remet l'adresse à zéro. Le client utilise
  `guarded_write` en vérifiant que l'adresse vaut bien `0x0` avant
  d'écrire, sinon il réessaie plus tard. `Client.py` lignes 134 à 162
- Ce motif de poignée de main évite d'écrire pendant que le jeu n'est
  pas prêt. C'est la réponse concrète à la contrainte de `CLAUDE.md`
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

`CLAUDE.md` avertit sur `register_indirect_condition`. MLSS l'appelle
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
