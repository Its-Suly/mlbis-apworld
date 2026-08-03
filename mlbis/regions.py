"""Le decoupage en regions.

Une region par zone nommee du jeu, 16 au total, plus le Menu.

La correspondance tresor -> carte -> zone a ete etablie le 4 aout 2026
en lisant la chaine que Randoglobin utilise pour nommer ses trouvailles :
overlay 3 pour le groupe de cartes et les metadonnees, overlay 4 pour les
plages de TreasureInfo, overlay 129 pour les icones de l'ecran de
selection de fichier, qui portent l'index du nom de zone. Detail dans
tools/build_salles_zones.py et formats-bis.md.

AUCUNE REGLE D'ACCES. Toutes les regions pendent directement au Menu.
Le decoupage est reel, la logique ne l'est pas encore : savoir qu'un
tresor est dans Dimble Wood ne dit pas ce qu'il faut pour y entrer.
C'est le prochain chantier, et il demande de connaitre le jeu.
"""
from BaseClasses import ItemClassification, Region

from .data import ZONES
from .items import MLBISItem, VICTORY
from .locations import MLBISLocation, ZONE_DE_LOCATION, location_name_to_id

MENU = "Menu"
FIN = "Defeat Dark Bowser"
REGION_FIN = "Peach's Castle"


def create_regions(world) -> None:
    menu = Region(MENU, world.player, world.multiworld)
    world.multiworld.regions.append(menu)

    regions = {}
    for zone in ZONES:
        region = Region(zone, world.player, world.multiworld)
        regions[zone] = region
        world.multiworld.regions.append(region)
        # Sans regle d'acces, tout est joignable depuis le Menu.
        menu.connect(region)

    for nom, code in location_name_to_id.items():
        region = regions[ZONE_DE_LOCATION[nom]]
        region.locations.append(MLBISLocation(world.player, nom, code, region))

    # Location d'evenement : pas d'identifiant, ne compte pas comme un
    # check. Elle porte l'item qui declare la partie gagnee.
    fin_region = regions[REGION_FIN]
    fin = MLBISLocation(world.player, FIN, None, fin_region)
    fin.place_locked_item(
        MLBISItem(VICTORY, ItemClassification.progression, None, world.player)
    )
    fin_region.locations.append(fin)
