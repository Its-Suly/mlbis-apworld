-- Livraison d'un equipement, et test du decalage de la table.
--
-- C'est le dernier trou de la livraison d'items : 57 exemplaires du pool
-- sur 725. Tout le reste a une adresse verifiee.
--
-- LE PROBLEME. formats-bis.md compte 127 compteurs d'equipement a
-- 02056427, un octet chacun, quand la table de l'arm9 donne 129 objets.
-- Deux de plus, donc l'index du compteur n'est pas l'identifiant de
-- l'objet, et personne n'a mesure lequel des deux decalages est le bon.
--
-- CE QUE LE run51 SUGGERE. Deux compteurs non nuls seulement :
--   index  0  x2
--   index 80  x1
-- Sous l'hypothese decalage = identifiant - 1, ca donne deux Thin Wear et
-- un Shabby Shell : une tenue pour chaque frere et la carapace de depart
-- de Bowser. Un inventaire de debut de partie exact.
-- Sous l'hypothese decalage = identifiant, ca donne deux « No gear » et
-- un Challenge Medal, ce qui n'a aucun sens a ce stade.
--
-- CE QUE CE SCRIPT TRANCHE. Il ecrit 1 au compteur d'index 4, et le nom
-- qui apparait au menu repond tout seul :
--
--   « Heart Wear »   -> index = identifiant - 1   (hypothese du run51)
--   « Fighter Wear » -> index = identifiant
--   autre chose      -> aucune des deux, et le nom dit laquelle chercher
--
-- Les deux candidats sont des tenues des freres, donc visibles au meme
-- endroit. Aucun des deux n'est dans l'inventaire actuel, donc
-- l'apparition ne peut pas etre confondue avec un objet deja present.
--
-- ETAT DE JEU. Faire un savestate avant. Rester sur le terrain.
-- Une ecriture d'inventaire est verifiee sans risque depuis le 4 aout,
-- y compris en plein combat, mais le savestate ne coute rien.
--
-- Usage : Tools > Lua Console, Ctrl+O sur ce fichier.

local BASE_EQUIPEMENT = 0x056427
local DOMAINE = "Main RAM"
local NB_COMPTEURS = 127

local INDEX = 4
local CANDIDATS = "Heart Wear si decalage -1, Fighter Wear si decalage 0"

local function lire(adr)
    return memory.read_bytes_as_array(adr, 1, DOMAINE)[1]
end

console.clear()
console.log("=== livrer_equipement.lua ===")

-- Etat avant, pour que l'apparition soit lisible sans ambiguite.
local occupes = {}
for M = 0, NB_COMPTEURS - 1 do
    local v = lire(BASE_EQUIPEMENT + M)
    if v ~= 0 then
        table.insert(occupes, string.format("index %d x%d", M, v))
    end
end
if #occupes == 0 then
    console.log("compteurs non nuls avant : aucun")
else
    console.log("compteurs non nuls avant : " .. table.concat(occupes, ", "))
end

local adresse = BASE_EQUIPEMENT + INDEX
local avant = lire(adresse)
if avant ~= 0 then
    console.log(string.format(
        "\nle compteur %d vaut deja %d. Choisir un INDEX vide dans la liste.",
        INDEX, avant))
    return
end

console.log(string.format("\ncible   : compteur d'equipement %d", INDEX))
console.log(string.format("adresse : 0x%05X en %s, absolu %08X",
    adresse, DOMAINE, 0x02000000 + adresse))
console.log("attendu : " .. CANDIDATS)

memory.write_bytes_as_array(adresse, { 1 }, DOMAINE)
local apres = lire(adresse)
console.log(string.format("ecrit   : 1, relu %d", apres))

if apres ~= 1 then
    console.log("\nECHEC : la relecture ne rend pas la valeur ecrite.")
    return
end

console.log("\nL'ecriture a pris. Ce qui tranche est a l'ecran :")
console.log("  1. ouvrir le menu, section equipement des freres")
console.log("  2. QUEL NOM est apparu ? c'est la reponse entiere")
console.log("  3. l'equiper : le jeu accepte-t-il, la statistique bouge-t-elle ?")
console.log("\nDire aussi ce que Mario, Luigi et Bowser portaient DEJA :")
console.log("ca confirme la lecture des deux compteurs deja occupes.")
