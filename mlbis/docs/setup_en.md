# Setup Guide for Mario & Luigi: Bowser's Inside Story

## Required Software

- BizHawk **2.10**, from [TASVideos](https://tasvideos.org/BizHawk/ReleaseHistory). Later releases are not supported by
  this world; the Archipelago connector is tested against 2.10.
- The Archipelago client, from the
  [Archipelago releases page](https://github.com/ArchipelagoMW/Archipelago/releases).
- Your own copy of Mario & Luigi: Bowser's Inside Story for Nintendo DS, North American release, pre-DSi revision.
  Archipelago will not provide one.

The ROM is never modified, so no patching step is needed and no patched copy is produced.

### Checking your ROM

This world targets one revision and one only. Its SHA-256 is:

```
9126963d6c6b6f81a9a666ba766e223781ff286634486e2a56d07a4c82eef4f1
```

The client also checks the cartridge header when it connects, and refuses anything whose internal title is not
`MARIO&LUIGI3` with game code `CLJE`. If the client says the ROM is not recognised, you are on another revision.

## Configuring BizHawk

Once BizHawk 2.10 is installed:

1. Open BizHawk and go to `Config > Customize`. On the Advanced tab, set the Lua Core to **Lua+LuaInterface**, then
   restart BizHawk. Without this the connector script cannot run.
2. Under `Config > Hotkeys > General`, clear the binding for `Open Lua Console` if you want to avoid opening it by
   accident, or leave it as is.

## Generating and hosting a game

Create your config file from the [player options page](../player-options), then generate a seed and host it as with any
other Archipelago game.

## Connecting

1. Start BizHawk 2.10 and load your ROM.
2. Open `Tools > Lua Console`, then `Ctrl+O`, and open `data/lua/connector_bizhawk_generic.lua` from your Archipelago
   installation. Open it **from that folder**: the script resolves its modules and its socket library relative to the
   working directory, and it will fail elsewhere.
3. Start the BizHawk Client from the Archipelago Launcher. It should report `Connected to BizHawk`.
4. In the client, type `/connect <address>:<port>`, then your slot name when asked.
5. Load your save file in game, or start a new one.

Checks you had already collected before connecting are sent as soon as you connect: the client reads the game's own
treasure flags rather than keeping its own list, so nothing is lost by connecting late.

## Playing

Play normally. Blocks, bean patches and attack pieces report themselves as you collect them, and items sent to you are
written into the game within a second or so.

If abilities are shuffled, expect the game to hand you an ability during a cutscene and the client to take it back
immediately afterwards. That is the intended behaviour: you keep an ability when the multiworld sends it, not when the
story would have given it.

## Finishing

Your run completes on its own when the ninth ability reaches you. If you would rather play the story to its end, type
`/bis_goal` in the client whenever you decide the run is over, for instance once Dark Bowser is down.

## Known issues

- Reloading a savestate can desynchronise items that use counters, since the delivered-item index lives on the server.
  Abilities are unaffected, they are recomputed from scratch on every pass.
- Two instances of BizHawk on the same ROM share one save file and will overwrite each other.
