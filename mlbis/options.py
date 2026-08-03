"""Les options du monde.

Aucune option propre pour l'instant : en ajouter avant d'avoir une
logique produirait des reglages qui ne changent rien.
"""
from dataclasses import dataclass

from Options import PerGameCommonOptions


@dataclass
class MLBISOptions(PerGameCommonOptions):
    pass
