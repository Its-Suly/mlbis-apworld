-- Session Lua complete pour une partie : journal + connecteur Archipelago.
--
-- BizHawk ne charge qu'un script par ligne de commande. Ce fichier en
-- charge deux, dans le seul ordre qui marche.
--
-- POURQUOI CET ORDRE. Le connecteur d'Archipelago se termine par
--     event.onframeend(tick)
--     while true do emu.frameadvance() end
-- soit une boucle infinie. Tout ce qui le suit ne serait jamais atteint.
-- Le journal, lui, enregistre son propre event.onframeend puis rend la
-- main aussitot. Charge en premier, il laisse le connecteur bloquer
-- ensuite, et les deux rappels se declenchent a chaque image : BizHawk
-- accepte plusieurs abonnes sur un meme evenement.
--
-- Charger le connecteur en premier laisserait le journal mort.
--
-- Usage normal : lance par tools/jouer.cmd, jamais a la main.
-- A la main : Tools > Lua Console, Ctrl+O sur ce fichier.

local RACINE = "C:\\Users\\sulyv\\Documents\\Projet BIS"
local AP = RACINE .. "\\vendor\\Archipelago"

-- Lu par journal_capacites.lua. Sans ca, le journal atterrirait dans le
-- repertoire de travail de BizHawk.
JOURNAL_CHEMIN = RACINE .. "\\journal_capacites.txt"

console.log("=== session_bizhawk.lua ===")
console.log("journal : " .. JOURNAL_CHEMIN)

dofile(RACINE .. "\\tools\\journal_capacites.lua")

console.log("connecteur Archipelago, la boucle demarre ici")
dofile(AP .. "\\data\\lua\\connector_bizhawk_generic.lua")
