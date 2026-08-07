"""Les options du monde.

Une seule, et elle commande la logique entiere.
"""
from dataclasses import dataclass

from Options import PerGameCommonOptions, Range, Toggle


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


class FillerVariety(Range):
    """How much of the duplicated filler to redraw, as a percentage.

    The vanilla pool is lopsided because the game is: it has 197 bean
    spots, so 197 of the 725 items are beans, and 109 of those are Heart
    Beans alone. Left alone, one item in four that reaches you is a bean.

    At 0 the pool is exactly what the game contains. Higher values take
    that share of the duplicated items and redraw them across every other
    filler name, so the same 725 items become more varied without any
    item name disappearing from the pool.
    """

    display_name = "Filler variety"
    range_start = 0
    range_end = 100
    default = 0


@dataclass
class MLBISOptions(PerGameCommonOptions):
    shuffle_abilities: ShuffleAbilities
    filler_variety: FillerVariety
