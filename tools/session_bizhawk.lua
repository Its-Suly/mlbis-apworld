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
-- OU CE FICHIER DOIT TOURNER. Dans vendor\Archipelago\data\lua, pas
-- ici. Le connecteur resout ses quatre require et le chemin de sa DLL
-- socket a partir du repertoire courant, socket.lua:44-47, et ces
-- fichiers vivent tous dans data\lua. Lance depuis tools\, il meurt sur
-- "module 'lua_5_3_compat' not found" alors que le journal survit :
-- session a moitie vivante, client qui attend BizHawk sans fin, mesure
-- le 7 aout 2026. tools/jouer.cmd copie donc ce fichier dans data\lua
-- avant de le passer a BizHawk.
--
-- Usage normal : lance par tools/jouer.cmd, jamais a la main.
-- A la main : Tools > Lua Console, Ctrl+O sur la copie, celle qui est
-- dans vendor\Archipelago\data\lua.

-- Les chemins se deduisent de l'emplacement de ce fichier, pour qu'aucun
-- nom d'utilisateur ni dossier d'installation ne soit ecrit en dur.
-- Copie par jouer.cmd dans vendor\Archipelago\data\lua, ce fichier est
-- donc a quatre niveaux sous la racine du projet.
local function parent(chemin)
    return chemin:match("^(.*)[/\\][^/\\]*$")
end

local ok, source = pcall(function()
    return debug.getinfo(1, "S").source
end)
local LUA = ok and source and parent(source:sub(2))   -- ...\data\lua
local AP = LUA and parent(parent(LUA))                -- ...\vendor\Archipelago
local RACINE = AP and parent(parent(AP))              -- la racine du projet
if not RACINE then
    console.log("ARRET : impossible de deduire les chemins depuis "
                .. "l'emplacement de ce script.")
    return
end

-- Garde-fou. Un fichier temoin ouvert en relatif repond a la seule
-- question qui compte, et remplace une trace NLua de quatorze lignes
-- par une phrase qui dit quoi faire.
local temoin = io.open("lua_5_3_compat.lua", "r")
if temoin == nil then
    console.log("ARRET : le repertoire courant n'est pas " .. AP .. "\\data\\lua")
    console.log("Le connecteur n'y trouverait ni ses modules ni sa DLL socket.")
    console.log("Passer par tools\\jouer.cmd, qui copie ce fichier au bon endroit.")
    return
end
temoin:close()

-- Lu par journal_capacites.lua. Sans ca, le journal atterrirait dans le
-- repertoire de travail de BizHawk.
JOURNAL_CHEMIN = RACINE .. "\\journal_capacites.txt"

console.log("=== session_bizhawk.lua ===")
console.log("journal : " .. JOURNAL_CHEMIN)

dofile(RACINE .. "\\tools\\journal_capacites.lua")

console.log("connecteur Archipelago, la boucle demarre ici")
dofile(AP .. "\\data\\lua\\connector_bizhawk_generic.lua")
