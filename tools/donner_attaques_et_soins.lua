-- Donne toutes les attaques speciales et fait le plein de consommables.
--
-- Deux primitives deja verifiees, appliquees en volume :
--   capacite  ->  un bit du champ 2xxx a 02056038      Verifie 5 aout
--   objet     ->  un compteur a 02056406 + index       Verifie 4 aout
--
-- CE QUI EST SUR ET CE QUI NE L'EST PAS. Les dix Bros Attacks viennent
-- de notre propre extraction de l'overlay 123, data/bros_attacks.csv,
-- recoupee sur dix sur dix par Super Mario Wiki. Le Fire Flower a ete
-- livre par ce chemin et joue en entier le 5 aout.
--
-- Les six Brawl Attacks de Bowser, elles, ne viennent que de
-- l'enumeration ImportantFlags de mnllib, bis/consts.py:75-81. Aucune
-- table de la ROM ne les confirme : randoglobin note « TO DO: randomize
-- bowser's special attacks too », donc personne n'a localise la leur.
-- **Hypothese**, et ce script est son test : si une Brawl Attack
-- n'apparait pas au menu de Bowser, la correspondance est fausse.
--
-- LES DEUX AUTORISATIONS. 0x200B pour les Bros Attacks, 0x200D pour les
-- Brawl Attacks. Randoglobin force les deux a 1 pour la meme raison que
-- nous, special.py:90-91, « let the bros use any special attacks they
-- have at any time just in case ».
--
-- LES CONSOMMABLES. Les 26 compteurs sont portes a 99, sauf les trois
-- entrees DUMMY, index 19, 24 et 25 de data/noms_items.csv, qui ne
-- correspondent a aucun objet. Le plafond de 99 n'est pas mesure, c'est
-- une borne de prudence ; si le menu affiche autre chose, le dire.
--
-- Les Drumsticks, index 4 a 6, sont les objets de Bowser et vivent dans
-- le meme bloc que ceux des freres.
--
-- ETAT DE JEU. Savestate avant, terrain, hors dialogue.
-- Usage : Tools > Lua Console, Ctrl+O sur ce fichier.

local BASE_FLAGS = 0x056038
local BASE_CONSOMMABLES = 0x056406
local NB_CONSOMMABLES = 26
local DOMAINE = "Main RAM"
local QUANTITE = 99

-- Puissances entieres : ^ rend un flottant et write_bytes_as_array le
-- refuse. Plantage du 5 aout 2026.
local P = { 1, 2, 4, 8, 16, 32, 64, 128 }

-- { variable, nom, source }
local CAPACITES = {
    { 0x200B, "usage des Bros Attacks",  "randoglobin patch.py:342" },
    { 0x200D, "usage des Brawl Attacks", "randoglobin special.py:91" },

    { 0x2010, "Green Shell",     "overlay 123" },
    { 0x2011, "Spin Pipe",       "overlay 123" },
    { 0x2012, "Yoo Who Cannon",  "overlay 123" },
    { 0x2013, "Falling Star",    "overlay 123" },
    { 0x2016, "Jump Helmet",     "overlay 123" },
    { 0x2017, "Super Bouncer",   "overlay 123" },
    { 0x2018, "Mighty Meteor",   "overlay 123" },
    { 0x2019, "Fire Flower",     "overlay 123" },
    { 0x201A, "Snack Basket",    "overlay 123" },
    { 0x201B, "Magic Window",    "overlay 123" },

    { 0x201C, "Goomba Storm",    "mnllib seul, HYPOTHESE" },
    { 0x201D, "Bob-omb Blitz",   "mnllib seul, HYPOTHESE" },
    { 0x201E, "Shy Guy Squad",   "mnllib seul, HYPOTHESE" },
    { 0x201F, "Koopa Corps",     "mnllib seul, HYPOTHESE" },
    { 0x2021, "Magikoopa Mob",   "mnllib seul, HYPOTHESE" },
    { 0x2022, "Broggy Bonker",   "mnllib seul, HYPOTHESE" },
}

-- Index de data/noms_items.csv, type consommable.
local DUMMY = { [19] = true, [24] = true, [25] = true }

local function lire(adr)
    return memory.read_bytes_as_array(adr, 1, DOMAINE)[1]
end

console.log("=== donner_attaques_et_soins.lua ===")

-- 1. Les attaques speciales.
local avant_flags = memory.read_bytes_as_array(BASE_FLAGS, 8, DOMAINE)
local ligne = ""
for i = 1, 8 do ligne = ligne .. string.format("%02X ", avant_flags[i]) end
console.log("champ 2xxx avant : " .. ligne)

local leves, presents = 0, 0
for _, entree in ipairs(CAPACITES) do
    local variable, nom, source = entree[1], entree[2], entree[3]
    local n = variable - 0x2000
    local adresse = BASE_FLAGS + math.floor(n / 8)
    local masque = P[(n % 8) + 1]
    local octet = lire(adresse)

    if math.floor(octet / masque) % 2 == 1 then
        console.log(string.format("deja   0x%04X  %-24s", variable, nom))
        presents = presents + 1
    else
        memory.write_bytes_as_array(adresse, { math.floor(octet + masque) }, DOMAINE)
        local relu = lire(adresse)
        if math.floor(relu / masque) % 2 == 1 then
            console.log(string.format("LEVE   0x%04X  %-24s  %s", variable, nom, source))
            leves = leves + 1
        else
            console.log(string.format("ECHEC  0x%04X  %-24s", variable, nom))
        end
    end
end

-- 2. Les consommables.
console.log("")
local pleins, deja = 0, 0
for n = 0, NB_CONSOMMABLES - 1 do
    if not DUMMY[n] then
        local adresse = BASE_CONSOMMABLES + n
        if lire(adresse) >= QUANTITE then
            deja = deja + 1
        else
            memory.write_bytes_as_array(adresse, { QUANTITE }, DOMAINE)
            if lire(adresse) == QUANTITE then
                pleins = pleins + 1
            else
                console.log(string.format("ECHEC consommable %d", n))
            end
        end
    end
end

console.log(string.format("%d capacite(s) levee(s), %d deja acquise(s)", leves, presents))
console.log(string.format("%d consommable(s) porte(s) a %d, %d deja pleins, 3 DUMMY ignores",
    pleins, QUANTITE, deja))

-- Controle : l'octet apres les 26 compteurs ne doit pas avoir bouge.
console.log(string.format("octet suivant les consommables, 0x%05X : %d",
    BASE_CONSOMMABLES + NB_CONSOMMABLES, lire(BASE_CONSOMMABLES + NB_CONSOMMABLES)))

console.log("\nA VERIFIER, et c'est le vrai test :")
console.log("  1. menu Bros Attacks de Mario : les dix y sont-elles ?")
console.log("  2. menu special de Bowser : les six Brawl Attacks y sont-elles ?")
console.log("     celles-la ne reposent que sur mnllib, une absence serait")
console.log("     une information et pas une panne")
console.log("  3. en jouer une de chaque, comme pour le Fire Flower")
