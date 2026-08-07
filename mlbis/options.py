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
    spots, so 197 of the 728 items are beans, and 109 of those are Heart
    Beans alone. Left alone, one item in four that reaches you is a bean.

    At 0 the pool is exactly what the game contains. Higher values take
    that share of the duplicated items and redraw them across every other
    filler name, so the same 728 items become more varied without any
    item name disappearing from the pool.
    """

    display_name = "Filler variety"
    range_start = 0
    range_end = 100
    default = 0


class SafeAbilityPlacement(Toggle):
    """Keep the shuffled abilities in the part of the map order we trust.

    The access logic works at the granularity of a named area, and the
    order of those areas comes from a walkthrough rather than from the
    game's data. Worse, this game sends you back through areas you have
    already seen, so a treasure in a late corner of an early area looks
    reachable long before it is.

    That only endangers a run when an ability lands somewhere you cannot
    actually get to. With this on, the nine abilities are confined to the
    first five areas, 213 of the 728 locations. Those five are the part
    of the order the walkthrough states outright, and a real save file
    independently confirms them: every location reached in the opening
    hours of a test playthrough sits in exactly those five.

    Turn it off for a wider spread, and expect to lean on !hint and on
    releasing items if a seed strands you.
    """

    display_name = "Safe ability placement"
    default = 1


@dataclass
class MLBISOptions(PerGameCommonOptions):
    shuffle_abilities: ShuffleAbilities
    safe_ability_placement: SafeAbilityPlacement
    filler_variety: FillerVariety
