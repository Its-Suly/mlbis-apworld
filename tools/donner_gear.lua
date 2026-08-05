-- Donne le meilleur equipement des trois personnages.
--
-- Double usage. Pour le joueur, avancer plus vite dans la partie de
-- test. Pour le projet, c'est la premiere livraison d'equipement en
-- volume : quatorze compteurs d'un coup au lieu du seul compteur 4 qui a
-- servi a etablir le decalage le 5 aout 2026.
--
-- ADRESSES, Verifie. Compteur d'un equipement d'identifiant I :
--   0x056427 + I - 1, un octet, 127 compteurs pour les identifiants
--   1 a 127. Mesure : 1 ecrit au compteur 4 fait apparaitre Heart Wear,
--   qui porte l'identifiant 5. Detail dans formats-bis.md.
--
-- STATISTIQUES. Lues dans
-- vendor/Cheatoglobin/cheatoglobin/constants.py:114, GPL-3.0, lu et non
-- recopie. Les 129 noms de cette table recoupent notre propre extraction
-- de la ROM, data/noms_items.csv, sur 128 sur 129 : seul l'identifiant 0
-- differe par son libelle, « None » contre « No gear ».
--
-- LES FRERES EN RECOIVENT DEUX. Mario et Luigi portent chacun le leur, et
-- l'inventaire ne distingue pas a qui appartient une piece.
--
-- CE QUI N'EST PAS DONNE, ET POURQUOI. Les 21 accessoires des freres,
-- type 11, n'ont aucune statistique dans la table : leur effet est
-- special et n'est ecrit nulle part que nous ayons lu. Deduire l'effet
-- d'un nom serait exactement ce que la regle du projet interdit, et le
-- « Challenge Medal » montre le risque : son nom suggere une difficulte
-- accrue, donc l'inverse du service rendu.
--
-- ETAT DE JEU. Savestate avant, terrain, hors dialogue.
-- Usage : Tools > Lua Console, Ctrl+O sur ce fichier.

local BASE_EQUIPEMENT = 0x056427
local DOMAINE = "Main RAM"
local NB_COMPTEURS = 127
local PLAFOND = 99

-- { identifiant, quantite, nom, effet }
local A_DONNER = {
    -- Freres : deux exemplaires, un par frere.
    {  16, 2, "A-OK Wear",       "HP+30 SP+10 POW+20 DEF+150 SPEED+20 STACHE+20" },
    {  37, 2, "DX POW Gloves",   "POW x1.2" },
    {  49, 2, "DX POW Boots",    "POW x1.2" },
    {  19, 2, "Deluxe HP Socks", "HP x1.3" },
    {  21, 2, "DX SP Socks",     "SP x1.3, si tu preferes les Bros Attacks" },

    -- Bowser : un exemplaire, il est seul.
    {  90, 1, "Ironclad Shell",  "DEF +300, le plus defensif" },
    {  92, 1, "King Shell",      "SP+20 POW+20 DEF+260, le plus complet" },
    { 105, 1, "Power Fangs X",   "POW x1.2" },
    { 107, 1, "Special Fangs X", "SP x1.4" },
    {  94, 1, "Power Band +",    "POW x1.2" },
    { 102, 1, "Block Band",      "DEF x1.2" },
    {  91, 1, "Block Ring",      "DEF x1.3" },
    { 126, 1, "Safety Ring",     "HP x1.2" },
}

local function lire(adr)
    return memory.read_bytes_as_array(adr, 1, DOMAINE)[1]
end

console.clear()
console.log("=== donner_gear.lua ===")

local ecrits, ignores, refuses = 0, 0, 0

for _, entree in ipairs(A_DONNER) do
    local ident, quantite, nom, effet = entree[1], entree[2], entree[3], entree[4]
    local index = ident - 1

    if index < 0 or index >= NB_COMPTEURS then
        console.log(string.format("REFUS %-16s identifiant %d sans compteur", nom, ident))
        refuses = refuses + 1
    else
        local adresse = BASE_EQUIPEMENT + index
        local avant = lire(adresse)
        local vise = avant + quantite
        if vise > PLAFOND then
            console.log(string.format("REFUS %-16s %d + %d depasse %d",
                nom, avant, quantite, PLAFOND))
            refuses = refuses + 1
        elseif avant >= quantite then
            console.log(string.format("deja  %-16s x%d, rien a faire", nom, avant))
            ignores = ignores + 1
        else
            memory.write_bytes_as_array(adresse, { math.floor(vise) }, DOMAINE)
            local apres = lire(adresse)
            if apres == vise then
                console.log(string.format("+%d    %-16s id %3d, compteur %3d, %s",
                    quantite, nom, ident, index, effet))
                ecrits = ecrits + 1
            else
                console.log(string.format("ECHEC %-16s ecrit %d, relu %d", nom, vise, apres))
                refuses = refuses + 1
            end
        end
    end
end

console.log(string.format("\n%d livre(s), %d deja present(s), %d refuse(s)",
    ecrits, ignores, refuses))
console.log("\nA verifier a l'ecran : menu, section equipement.")
console.log("Les frusques des freres apparaissent en double, une par frere.")
console.log("Bowser garde les siennes meme s'il n'est pas encore jouable.")
console.log("\nPenser a EQUIPER : le compteur ne fait que poser l'objet dans")
console.log("l'inventaire, il ne le porte pas.")
