-- Premiere ecriture en memoire du projet : le compteur de pieces.
--
-- Cible : Main RAM 0x056400, absolu 02056400, u32 little-endian.
-- Trouvee le 3 aout 2026 sur les dumps run06 a run12, voir formats-bis.md.
--
-- API d'ecriture verifiee dans
-- vendor/Archipelago/data/lua/connector_bizhawk_generic.lua ligne 449 :
--   memory.write_bytes_as_array(adresse, tableau, domaine)
-- Le tableau est indexe a partir de 1, comme en lecture.
--
-- ETAT DE JEU REQUIS. A lancer sur le terrain, en marchant, jamais
-- pendant un combat, un dialogue ou une cinematique. Le compteur de
-- pieces est la cible la moins dangereuse qu'on connaisse : il n'est ni
-- un pointeur, ni un index, ni une taille. Une valeur fausse donne un
-- affichage faux, pas un saut dans le vide.
--
-- Faire un savestate AVANT de lancer ce script.
--
-- Usage : Tools > Lua Console, Ctrl+O sur ce fichier.

local ADRESSE = 0x056400
local DOMAINE = "Main RAM"
local NOUVELLE_VALEUR = 999

local function lire_u32()
    local o = memory.read_bytes_as_array(ADRESSE, 4, DOMAINE)
    return o[1] + o[2] * 256 + o[3] * 65536 + o[4] * 16777216
end

local function ecrire_u32(v)
    local o = {}
    o[1] = v % 256
    o[2] = math.floor(v / 256) % 256
    o[3] = math.floor(v / 65536) % 256
    o[4] = math.floor(v / 16777216) % 256
    memory.write_bytes_as_array(ADRESSE, o, DOMAINE)
end

console.clear()
console.log("=== ecrire_pieces.lua ===")

local avant = lire_u32()
console.log(string.format("avant  : %d pieces  (0x%05X, %s)", avant, ADRESSE, DOMAINE))

ecrire_u32(NOUVELLE_VALEUR)

local apres = lire_u32()
console.log(string.format("ecrit  : %d", NOUVELLE_VALEUR))
console.log(string.format("relu   : %d", apres))

if apres == NOUVELLE_VALEUR then
    console.log("\nL'ecriture a pris en memoire.")
    console.log("Ca ne prouve pas encore que le JEU l'utilise.")
    console.log("Suite : marcher quelques pas, sauvegarder en jeu, puis")
    console.log("relancer dump_ram.lua. Si la sauvegarde porte la valeur,")
    console.log("c'est que le jeu l'a bien adoptee comme sienne.")
else
    console.log("\nECHEC : la relecture ne rend pas la valeur ecrite.")
    console.log("Soit le domaine est en lecture seule, soit le jeu a")
    console.log("reecrit par-dessus dans la meme frame.")
end
