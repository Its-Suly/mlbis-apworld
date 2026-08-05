"""APWorld Archipelago pour Mario & Luigi : Voyage au Centre de Bowser.

SQUELETTE. Ce monde genere une seed valide et ne fait rien d'autre : pas
de logique, pas de client, pas de patch de ROM. Il sert a valider
l'empaquetage et le branchement des donnees, rien de plus.

Ce qui est vrai ici et le restera :
  - 725 locations : 647 tresors de Treasure/TreasureInfo.dat et 78 pieces
    d'attaque
  - l'identifiant d'une location est BASE_ID + le rang de son bit dans le
    tableau Exxx a 020560C8, quelle que soit la famille

Ce qui est provisoire et attend une donnee manquante :
  - aucun item de progression, faute de logique
  - aucune option
"""
from typing import Any, Dict

from worlds.AutoWorld import WebWorld, World

from .client import MLBISClient  # noqa: F401  enregistre le client BizHawk
from .data import LOCATIONS
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
        # Un item par location, celui qui s'y trouve dans le jeu d'origine :
        # le contenu du tresor, ou une piece de l'attaque du lot. Le compte
        # tombe juste par construction, les deux listes sortent du meme
        # tableau.
        for _, nom_location, _, _ in LOCATIONS:
            self.multiworld.itempool.append(
                self.create_item(VANILLA_PLACEMENT[nom_location])
            )

    def set_rules(self) -> None:
        self.multiworld.completion_condition[self.player] = (
            lambda state: state.has(VICTORY, self.player)
        )

    def fill_slot_data(self) -> Dict[str, Any]:
        return {}
