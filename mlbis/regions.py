"""Le decoupage en regions.

ETAT PROVISOIRE, ET IL FAUT SAVOIR POURQUOI. Tout tient dans une seule
region, sans aucune regle d'acces.

La raison n'est pas la paresse : `data/locations_bis.csv` porte un numero
de salle reconstruit par le bit is_last_entry_in_room, donc un simple
regroupement dans l'ordre du fichier. Les 32 zones nommees de
mfset_EMesPlace.dat sont une autre numerotation, et **la correspondance
entre les deux n'est pas etablie**. Inventer un decoupage maintenant
reviendrait a inventer une donnee, ce que le projet s'interdit.

Le jour ou salle -> zone sera etabli, ce fichier deviendra le vrai
decoupage en regions, et c'est la que les access_rule s'accrocheront.
"""
from BaseClasses import ItemClassification, Region

from .items import MLBISItem, VICTORY
from .locations import MLBISLocation, location_name_to_id

MENU = "Menu"
MONDE = "Bowser's Inside Story"
FIN = "Defeat Dark Bowser"


def create_regions(world) -> None:
    menu = Region(MENU, world.player, world.multiworld)
    monde = Region(MONDE, world.player, world.multiworld)

    for nom, code in location_name_to_id.items():
        monde.locations.append(MLBISLocation(world.player, nom, code, monde))

    # Location d'evenement : elle n'a pas d'identifiant et ne compte pas
    # comme un check. Elle porte l'item qui declare la partie gagnee.
    fin = MLBISLocation(world.player, FIN, None, monde)
    fin.place_locked_item(
        MLBISItem(VICTORY, ItemClassification.progression, None, world.player)
    )
    monde.locations.append(fin)

    world.multiworld.regions.append(menu)
    world.multiworld.regions.append(monde)
    menu.connect(monde)
