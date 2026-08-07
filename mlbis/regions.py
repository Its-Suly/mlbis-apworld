"""Le decoupage en regions, et la logique d'acces.

Une region par zone nommee portant au moins un tresor, 16 au total, plus
le Menu. La correspondance tresor -> carte -> zone a ete etablie le
4 aout 2026, detail dans tools/build_salles_zones.py et formats-bis.md.

LA REGLE, EN UNE PHRASE. Une zone de rang r exige toutes les capacites
que le jeu d'origine octroie dans les zones de rang strictement
inferieur.

CE QUI LA JUSTIFIE. Le jeu d'origine demontre une chose et une seule :
on traverse les zones jusqu'a Z sans la capacite octroyee dans Z. Au
dela, on ne sait pas quel bloc exige quoi, parce que ce test vit dans le
code ARM et non dans les scripts : sur 48 variables, 32 ne sont jamais
lues par un script et le marteau zero fois. Donc on exige, par prudence.

LE SENS DE L'ERREUR EST CHOISI. Trop d'exigences restreint le placement
et ne bloque jamais le joueur ; il en manque une, et un item necessaire
peut atterrir derriere le mur qu'il ouvre. Partout ou il a fallu
trancher, c'est la version la plus exigeante qui a ete retenue : la zone
d'octroi la plus precoce d'une capacite, Peach's Castle en fin de chaine
parce qu'elle est visitee au prologue ET a la fin, et la victoire qui
exige les neuf capacites, y compris celle que personne n'exige.

CE QUE CES EXIGENCES SONT, ET CE QU'ELLES NE SONT PAS. Ce sont des
jalons de progression, pas des besoins physiques. Le jeu alterne deux
mondes : les freres a l'interieur de Bowser, Bowser dehors. Exiger le
marteau des freres pour entrer a Cavi Cape, ou Bowser se promene seul,
a l'air d'une erreur et n'en est pas une : dans la partie d'origine on
n'arrive a Cavi Cape qu'apres le Trash Pit, ou le marteau est donne.

Cette regle-la se lit donc « la partie a progresse jusque-la », et non
« il faut cet outil ici ». Retirer ces exigences au motif que Bowser ne
se sert pas d'un marteau **casserait la logique** : c'est la direction
qui bloque un joueur, celle qui ouvre une zone trop tot.

CE QUE CETTE LOGIQUE N'EST PAS. Une carte du jeu. Le rang des zones vient
d'un guide, `data/ordre_zones.csv` porte la confiance ligne par ligne, et
les rangs 11 a 16 sont marques faibles. Le journal de capacites, produit
en jouant, est ce qui les confirmera ou les cassera.

PAS DE CONDITION INDIRECTE. Chaque region pend au Menu avec une regle qui
ne lit que des items, jamais l'accessibilite d'une autre region. Le piege
decrit dans CLAUDE.md, une transition evaluee trop tot et jamais
reevaluee, ne se pose donc pas ici.
"""
from typing import Dict, List, Tuple

from BaseClasses import ItemClassification, Region

from .data import CAPABILITIES, ZONE_ORDER, ZONES
from .items import MLBISItem, VICTORY
from .locations import MLBISLocation, ZONE_DE_LOCATION, location_name_to_id

MENU = "Menu"
# Le but n'est pas la fin de l'histoire, faute de savoir la detecter : le
# drapeau de Dark Bowser vaincu n'est pas trouve, detail dans
# client.py:signaler_victoire. Reunir les neuf capacites se lit, lui,
# dans les items recus, sans aucune adresse memoire.
FIN = "Gather All Nine Abilities"
REGION_FIN = "Peach's Castle"


def prerequis_par_zone() -> Dict[str, Tuple[str, ...]]:
    """Zone -> capacites exigees pour y entrer, dans l'ordre des rangs."""
    rang_de_zone = {zone: rang for rang, zone, _ in ZONE_ORDER}
    acquises: List[Tuple[int, str]] = [
        (rang_de_zone[zone], nom) for nom, _, zone in CAPABILITIES
    ]
    return {
        zone: tuple(nom for rang, nom in sorted(acquises) if rang < rang_de_zone[zone])
        for zone in ZONES
    }


def create_regions(world) -> None:
    menu = Region(MENU, world.player, world.multiworld)
    world.multiworld.regions.append(menu)

    melange = bool(world.options.shuffle_abilities)
    prerequis = prerequis_par_zone() if melange else {zone: () for zone in ZONES}

    regions = {}
    for zone in ZONES:
        region = Region(zone, world.player, world.multiworld)
        regions[zone] = region
        world.multiworld.regions.append(region)
        exiges = prerequis[zone]
        if exiges:
            menu.connect(
                region,
                rule=lambda state, exiges=exiges: state.has_all(exiges, world.player),
            )
        else:
            menu.connect(region)

    for nom, code in location_name_to_id.items():
        region = regions[ZONE_DE_LOCATION[nom]]
        region.locations.append(MLBISLocation(world.player, nom, code, region))

    # Location d'evenement : pas d'identifiant, ne compte pas comme un
    # check. Elle porte l'item qui declare la partie gagnee.
    #
    # Elle exige les NEUF capacites, alors que sa region n'en exige que
    # huit : le Spike Ball est octroye dans Peach's Castle meme, donc
    # aucune region ne l'exige, et sans cette ligne il serait un item de
    # progression que rien ne rend necessaire.
    fin_region = regions[REGION_FIN]
    fin = MLBISLocation(world.player, FIN, None, fin_region)
    if melange:
        toutes = tuple(nom for nom, _, _ in CAPABILITIES)
        fin.access_rule = (
            lambda state, toutes=toutes: state.has_all(toutes, world.player)
        )
    fin.place_locked_item(
        MLBISItem(VICTORY, ItemClassification.progression, None, world.player)
    )
    fin_region.locations.append(fin)
