"""Les locations du monde.

Deux familles, une seule regle :

  - 647 tresors de Treasure/TreasureInfo.dat, rangs 0 a 757
  - 81 blocs de pieces d'attaque, rangs 1792 a 2081

L'identifiant Archipelago d'une location vaut BASE_ID plus le rang de son
bit dans le tableau Exxx a 020560C8. Pour un tresor ce rang est
l'identifiant des octets 4-5 de TreasureInfo.dat, pour une piece
d'attaque c'est le numero de sa variable moins 0xE000. Un identifiant de
location se lit donc directement comme un index de bit, sans table
intermediaire, quelle que soit la famille.

Manquent encore, dans la reserve BASE_ID + 1024 : boutiques et quetes.
Et 22 pieces d'attaque dont la variable n'est pas connue, dont les dix du
Yoo Who Cannon qui sont octroyees d'un bloc et ne sont donc pas des
locations. Detail dans formats-bis.md.
"""
from typing import Dict

from BaseClasses import Location

from .data import BASE_ID, LOCATIONS

GAME_NAME = "Mario & Luigi Bowser's Inside Story"


class MLBISLocation(Location):
    game: str = GAME_NAME


location_name_to_id: Dict[str, int] = {
    nom: BASE_ID + rang for rang, nom, _, _ in LOCATIONS
}

# nom de location -> item qui s'y trouve dans le jeu d'origine
VANILLA_PLACEMENT: Dict[str, str] = {nom: item for _, nom, item, _ in LOCATIONS}

# nom de location -> rang du bit dans Exxx
LOCATION_TO_BIT: Dict[str, int] = {nom: rang for rang, nom, _, _ in LOCATIONS}

# nom de location -> zone nommee du jeu, donc region
ZONE_DE_LOCATION: Dict[str, str] = {nom: zone for _, nom, _, zone in LOCATIONS}
