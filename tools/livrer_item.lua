-- Livraison d'un objet dans l'inventaire vivant : la primitive dont un
-- APWorld a besoin pour donner un item au joueur.
--
-- Correspondance etablie le 3 aout 2026 sur les dumps run12 et run13,
-- voir formats-bis.md :
--   sauvegarde slot + 0x0054 + X   ->   Main RAM 0x056400 + X + 2
--   consommable N  ->  0x02056406 + N   (26 objets, 1 octet chacun)
--   equipement M   ->  0x02056427 + M   (127 emplacements)
--
-- API verifiee dans
-- vendor/Archipelago/data/lua/connector_bizhawk_generic.lua ligne 449.
--
-- ETAT DE JEU REQUIS. Sur le terrain, en marchant. Jamais en combat, en
-- dialogue ou en cinematique. Faire un savestate avant.
--
-- Usage : Tools > Lua Console, Ctrl+O sur ce fichier.
-- Modifier INDEX et QUANTITE ci-dessous pour changer de cible.

local BASE_CONSOMMABLES = 0x056406
local DOMAINE = "Main RAM"
local MAX_PAR_OBJET = 99   -- prudence : plafond suppose, jamais mesure

-- 0 Mushroom, 4 1-Up Mushroom, 6 Syrup Jar, 12 Nut, 16 Heart Bean.
-- Liste complete dans data/noms_items.csv, colonne id_item.
local INDEX = 4
local QUANTITE = 1
local NOM = "1-Up Mushroom"

local function lire(adr)
    return memory.read_bytes_as_array(adr, 1, DOMAINE)[1]
end

local function ecrire(adr, v)
    memory.write_bytes_as_array(adr, { v }, DOMAINE)
end

console.clear()
console.log("=== livrer_item.lua ===")

if INDEX < 0 or INDEX > 25 then
    console.log(string.format("INDEX %d hors des 26 consommables (0 a 25).", INDEX))
    return
end

local adresse = BASE_CONSOMMABLES + INDEX
local avant = lire(adresse)
local vise = avant + QUANTITE
if vise > MAX_PAR_OBJET then
    console.log(string.format("refus : %d + %d depasse le plafond de prudence %d.",
        avant, QUANTITE, MAX_PAR_OBJET))
    return
end

console.log(string.format("objet   : index %d, %s", INDEX, NOM))
console.log(string.format("adresse : 0x%05X en %s, absolu %08X",
    adresse, DOMAINE, 0x02000000 + adresse))
console.log(string.format("avant   : %d", avant))

ecrire(adresse, vise)
local apres = lire(adresse)

console.log(string.format("ecrit   : %d", vise))
console.log(string.format("relu    : %d", apres))

if apres == vise then
    console.log("\nL'ecriture a pris en memoire.")
    console.log("Verification qui compte : ouvrir le menu des objets en jeu.")
    console.log("Si l'objet y apparait, la livraison d'items fonctionne.")
    console.log("Puis sauvegarder et redumper pour confirmer cote sauvegarde.")
else
    console.log("\nECHEC : la relecture ne rend pas la valeur ecrite.")
end
