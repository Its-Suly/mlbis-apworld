"""Les items du monde.

Le pool de depart est le contenu d'origine des tresors : un exemplaire
par tresor, soit 647 items pour 647 locations. Aucun item de progression
n'est encore declare, faute de logique : tout est filler sauf l'item
d'evenement Victory.

C'est volontaire. Declarer un item comme progression sans regle d'acces
qui l'utilise ne change rien au placement et donnerait une fausse
impression de logique.
"""
from typing import Dict

from BaseClasses import Item, ItemClassification

from .data import BASE_ID, VANILLA_ITEMS

GAME_NAME = "Mario & Luigi Bowser's Inside Story"

# Plage distincte de celle des locations, par lisibilite : les deux
# espaces d'identifiants sont separes cote Archipelago, mais les
# confondre rend les journaux illisibles.
ITEM_BASE = BASE_ID + 0x10000

VICTORY = "Victory"


class MLBISItem(Item):
    game: str = GAME_NAME


item_name_to_id: Dict[str, int] = {
    nom: ITEM_BASE + i for i, nom in enumerate(sorted(VANILLA_ITEMS))
}


def classification(nom: str) -> ItemClassification:
    """Tout est filler tant qu'aucune regle d'acces n'existe."""
    return ItemClassification.filler
