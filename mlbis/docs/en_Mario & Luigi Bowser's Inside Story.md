# Mario & Luigi: Bowser's Inside Story

## Where is the options page?

The [player options page for this game](../player-options) contains all the options you need to configure and export a
config file.

## What does randomization do to this game?

Every treasure the game hides in a block, a bean patch or a patch of grass becomes a check, and so does every attack
piece scattered through the ten Special Attack sets. There are 725 of them. What comes out of a block is no longer what
the game put there: it is whatever the multiworld decided, and it may belong to another player entirely.

Nine abilities are shuffled into the item pool as well: the hammer, Spin Jump, Drill Bros, Sliding Haymaker, Body Slam,
Spike Ball, the Vacuum Block, Blue Shell Blocks and Air Vents. The game still hands them to you at the usual moment in
the story, and the client takes them straight back if the multiworld has not sent them yet. You keep an ability the
moment it is found, wherever it was found, and not before.

The ROM itself is never modified. Everything happens in memory while you play, which means no patching step and no
patched copy to keep around.

## What is the goal?

Gather all nine shuffled abilities. Since they are scattered across the multiworld, the road there depends on where
they landed, and the last area of the game is only reachable in logic once you hold them all.

The goal is not "defeat Dark Bowser", and that is a deliberate limitation rather than a design choice: the game does
not appear to leave a usable flag when the final battle is won, so a client cannot tell that it happened. If that flag
is ever found, finishing the story will be offered as a goal option.

## What items and locations get shuffled?

Locations are the 647 usable entries of the game's treasure table and the 78 attack pieces whose flag is known. Items
are the vanilla contents of those treasures, coins, consumables and gear, plus the nine abilities, which replace nine
of the smallest coin rewards so that the counts still match.

## Which items can be in another player's world?

Any of them. Coins, mushrooms, wearables, attack pieces and abilities can all be found by someone else.

## What does another world's item look like in this game?

There is no special sprite for it. A block opens as usual and the client tells you what came out; the item itself is
handed to whoever it belongs to.

## When the player receives an item, what happens?

Coins are added to the wallet, consumables and gear land in the inventory, and abilities are turned on. Nothing is
announced in game: the client window is where you read what arrived.

## Known limits of this version

The access logic works at the granularity of a named area, never of an individual block, and the order of those areas
comes from a walkthrough rather than from the game's data. Six of the sixteen areas carry a low-confidence rank. A seed
is playable, but it is not yet guaranteed to be completable in every layout.

Reloading a savestate desynchronises the delivered-item index, which lives on the server. Abilities are immune to this
by design, counters are not.
