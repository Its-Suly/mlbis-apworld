"""APWorld Archipelago pour Mario & Luigi : Voyage au Centre de Bowser.

SQUELETTE. Ce monde genere une seed valide et ne fait rien d'autre : pas
de logique, pas de client, pas de patch de ROM. Il sert a valider
l'empaquetage et le branchement des donnees, rien de plus.

Ce qui est vrai ici et le restera :
  - 647 locations, une par tresor de Treasure/TreasureInfo.dat
  - l'identifiant d'une location est BASE_ID + l'identifiant du tresor,
    qui est aussi le rang de son bit dans le tableau Exxx a 020560C8

Ce qui est provisoire et attend une donnee manquante :
  - une seule region, faute de correspondance salle -> zone nommee
  - aucun item de progression, faute de logique
  - aucune option
"""
from typing import Any, Dict

from worlds.AutoWorld import WebWorld, World

from .data import TREASURES
from .items import MLBISItem, VICTORY, classification, item_name_to_id
from .locations import GAME_NAME, VANILLA_PLACEMENT, location_name_to_id
from .options import MLBISOptions
from .regions import FIN, create_regions


class MLBISWeb(WebWorld):
    theme = "grass"


class MLBISWorld(World):
    """
    Mario et Luigi explorent le corps de Bowser pendant que Bowser
    lui-meme arpente le royaume. Deux equipes, deux inventaires, une
    seule aventure.
    """

    game = GAME_NAME
    web = MLBISWeb()
    options_dataclass = MLBISOptions
    options: MLBISOptions

    item_name_to_id = item_name_to_id
    location_name_to_id = location_name_to_id

    def create_regions(self) -> None:
        create_regions(self)

    def create_item(self, name: str) -> MLBISItem:
        return MLBISItem(
            name, classification(name), item_name_to_id[name], self.player
        )

    def create_items(self) -> None:
        # Un item par location, celui que le tresor contenait a l'origine.
        # Le compte tombe juste par construction : les deux listes sont
        # tirees du meme parcours de TreasureInfo.dat.
        for _, nom_location, _, _ in TREASURES:
            self.multiworld.itempool.append(
                self.create_item(VANILLA_PLACEMENT[nom_location])
            )

    def set_rules(self) -> None:
        self.multiworld.completion_condition[self.player] = (
            lambda state: state.has(VICTORY, self.player)
        )

    def fill_slot_data(self) -> Dict[str, Any]:
        return {}
