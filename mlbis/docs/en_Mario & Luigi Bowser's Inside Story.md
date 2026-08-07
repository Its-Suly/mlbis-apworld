# Mario & Luigi: Bowser's Inside Story

## Where is the options page?

The [player options page for this game](../player-options) contains all the options you need to configure and export a
config file.

## What does randomization do to this game?

Every treasure the game hides in a block, a bean patch or a patch of grass becomes a check, and so does every attack
piece scattered through the ten Special Attack sets. There are 728 of them. What comes out of a block is no longer what
the game put there: it is whatever the multiworld decided, and it may belong to another player entirely.

Nine abilities are shuffled into the item pool as well: the hammer, Spin Jump, Drill Bros, Sliding Haymaker, Body Slam,
Spike Ball, the Vacuum Block, Blue Shell Blocks and Air Vents. The game still hands them to you at the usual moment in
the story, and the client takes them straight back if the multiworld has not sent them yet. You keep an ability the
moment it is found, wherever it was found, and not before.

The ROM itself is never modified. Everything happens in memory while you play, which means no patching step and no
patched copy to keep around.

## What is the goal?

Two ways to finish, and you choose which one you use.

The run completes on its own once you have gathered all nine shuffled abilities. Since they are scattered across the
multiworld, the road there depends on where they landed, and the last area of the game is only reachable in logic once
you hold them all.

Or you declare it finished yourself, with `/bis_goal` in the client. Type it when you beat Dark Bowser, or whenever
you consider the run over.

That second option exists because the game leaves no readable mark when the story ends: over 800,000 script commands
were read, field and battle alike, and the final fight writes nothing that distinguishes it. Rather than have the
client guess at a memory address it cannot justify, the decision is handed to you.

## What items and locations get shuffled?

Locations are the 647 usable entries of the game's treasure table and the 81 attack-piece blocks, three of which hand over four pieces at once. Items
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
comes from a walkthrough rather than from the game's data. Worse, this game sends you back through areas you have
already cleared, so a treasure in a late corner of an early area looks reachable long before it is.

That only strands a run when an ability lands somewhere you cannot yet get to, which is why **Safe ability placement**
is on by default: the nine abilities stay in the first five areas, 213 of the 728 locations, the part of the order the
walkthrough states outright and that a real save file independently confirms. Everything else is free to go anywhere,
since an ordinary item found late costs nothing.

With that option off, a seed is playable but not guaranteed. `!hint` and releasing items are the way out if one
strands you.

Reloading a savestate desynchronises the delivered-item index, which lives on the server. Abilities are immune to this
by design, counters are not.
