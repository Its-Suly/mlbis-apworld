"""Les locations du monde.

Pour l'instant, uniquement les 647 tresors de Treasure/TreasureInfo.dat.
Les emplacements hors table (boutiques, recompenses de quete) viendront
plus tard, dans la plage reservee a partir de BASE_ID + 1024.

L'identifiant Archipelago d'une location vaut BASE_ID + l'identifiant du
tresor, celui des octets 4-5 de TreasureInfo.dat, qui est aussi le rang
du bit dans le tableau Exxx a 020560C8. Un identifiant de location se lit
donc directement comme un index de bit, sans table intermediaire.
"""
from typing import Dict

from BaseClasses import Location

from .data import BASE_ID, TREASURES

GAME_NAME = "Mario & Luigi Bowser's Inside Story"


class MLBISLocation(Location):
    game: str = GAME_NAME


location_name_to_id: Dict[str, int] = {
    nom: BASE_ID + identifiant for identifiant, nom, _, _ in TREASURES
}

# nom de location -> item qui s'y trouve dans le jeu d'origine
VANILLA_PLACEMENT: Dict[str, str] = {nom: item for _, nom, item, _ in TREASURES}

# nom de location -> identifiant de tresor, donc rang du bit dans Exxx
LOCATION_TO_BIT: Dict[str, int] = {
    nom: identifiant for identifiant, nom, _, _ in TREASURES
}

# nom de location -> zone nommee du jeu, donc region
ZONE_DE_LOCATION: Dict[str, str] = {nom: zone for _, nom, _, zone in TREASURES}
