"""Les options du monde.

Une seule, et elle commande la logique entiere.
"""
from dataclasses import dataclass

from Options import PerGameCommonOptions, Toggle


class ShuffleAbilities(Toggle):
    """Shuffle Bowser's and the bros' abilities into the item pool.

    On: the hammer, Drill Bros, the vacuum and six more become items.
    The client clears the ones you have not received yet, so the game
    giving you an ability at its usual moment no longer counts. Regions
    are then gated behind those abilities.

    Off: abilities stay where the game grants them, every region is open
    from the start, and the pool is exactly the vanilla contents. That is
    the behaviour that ran end to end on 5 August 2026.
    """

    display_name = "Shuffle abilities"
    default = 1


@dataclass
class MLBISOptions(PerGameCommonOptions):
    shuffle_abilities: ShuffleAbilities
