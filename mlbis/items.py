"""Les items du monde.

Deux familles, et une seule porte la logique.

  - le contenu d'origine des tresors et des pieces d'attaque, 728
    exemplaires pour 728 locations. Tout est filler : recevoir un
    champignon n'ouvre aucune porte
  - les neuf capacites, seuls items de progression. Elles n'existent
    dans le pool que si l'option `shuffle_abilities` est active, et
    elles y prennent la place d'autant d'items filler

POURQUOI LES CAPACITES ET RIEN D'AUTRE. Un item n'est de progression que
si une `access_rule` le lit. Les capacites sont les seules dont on sache
a la fois qu'elles ouvrent des passages et qu'on puisse les retirer au
joueur, mesure du 7 aout 2026. Declarer un consommable comme progression
ne changerait rien au placement et donnerait une fausse impression de
logique.

Les identifiants des capacites sont attribues APRES la plage des items
d'origine, jamais melanges a eux : ajouter une capacite ne doit pas
decaler l'identifiant d'un champignon dans une seed deja distribuee.
"""
from typing import Dict, List

from BaseClasses import Item, ItemClassification

from .data import BASE_ID, CAPABILITIES, VANILLA_ITEMS

GAME_NAME = "Mario & Luigi Bowser's Inside Story"

# Plage distincte de celle des locations, par lisibilite : les deux
# espaces d'identifiants sont separes cote Archipelago, mais les
# confondre rend les journaux illisibles.
ITEM_BASE = BASE_ID + 0x10000

VICTORY = "Victory"

NOMS_CAPACITES: List[str] = [nom for nom, _, _ in CAPABILITIES]
VARIABLE_DE_CAPACITE: Dict[str, int] = {nom: var for nom, var, _ in CAPABILITIES}
ZONE_DE_CAPACITE: Dict[str, str] = {nom: zone for nom, _, zone in CAPABILITIES}


class MLBISItem(Item):
    game: str = GAME_NAME


item_name_to_id: Dict[str, int] = {
    nom: ITEM_BASE + i for i, nom in enumerate(sorted(VANILLA_ITEMS))
}
_apres_vanilla = ITEM_BASE + len(VANILLA_ITEMS)
for _i, _nom in enumerate(sorted(NOMS_CAPACITES)):
    item_name_to_id[_nom] = _apres_vanilla + _i


def classification(nom: str) -> ItemClassification:
    """Progression pour une capacite, filler pour tout le reste."""
    if nom in VARIABLE_DE_CAPACITE:
        return ItemClassification.progression
    return ItemClassification.filler
