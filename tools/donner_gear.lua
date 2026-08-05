-- Donne TOUT l'equipement du jeu, deux exemplaires de chaque.
--
-- Deux exemplaires couvrent Mario et Luigi, qui portent chacun le leur et
-- que l'inventaire ne distingue pas. Bowser est seul, son deuxieme
-- exemplaire ne sert a rien mais ne coute rien non plus, et une regle
-- unique vaut mieux qu'une exception a retenir.
--
-- Double usage. Pour le joueur, avancer sans se soucier du materiel.
-- Pour le projet, c'est la livraison d'equipement a pleine echelle : le
-- decalage avait ete etabli sur un seul compteur le 5 aout 2026, celui-ci
-- ecrit les 127.
--
-- ADRESSES, Verifie. Compteur d'un equipement d'identifiant I :
--   0x056427 + I - 1, un octet, 127 compteurs pour les identifiants
--   1 a 127. Mesure : 1 ecrit au compteur 4 fait apparaitre Heart Wear,
--   qui porte l'identifiant 5. Detail dans formats-bis.md.
--
-- CE QUI RESTE DEHORS, et ce n'est pas un choix : l'identifiant 0,
-- « No gear », et le 128, « Rental Shell », n'ont pas de compteur. Le
-- bloc s'arrete a 020564A5, juste devant le champ de bits des badges.
--
-- IDEMPOTENT. Le script porte chaque compteur A deux, il n'ajoute pas
-- deux. Le relancer ne fait rien, et il ne touche pas aux compteurs qui
-- valent deja deux ou plus.
--
-- ATTENTION AUX PIEGES A L'EQUIPEMENT. Tout arrive dans l'inventaire, y
-- compris ce dont personne ici ne connait l'effet : les 21 accessoires
-- des freres n'ont aucune statistique dans les tables lues, et un nom
-- comme « Challenge Medal » suggere une difficulte accrue plutot qu'une
-- aide. Poser un objet dans l'inventaire est sans effet ; l'equiper, non.
-- Dans le doute, ne pas equiper ce qu'on ne connait pas.
--
-- ETAT DE JEU. Savestate avant, terrain, hors dialogue.
-- Usage : Tools > Lua Console, Ctrl+O sur ce fichier.
--
-- Les noms se lisent dans data/noms_items.csv, colonne id_item : le
-- compteur N correspond a l'identifiant N + 1.

local BASE_EQUIPEMENT = 0x056427
local DOMAINE = "Main RAM"
local NB_COMPTEURS = 127
local QUANTITE = 2

local function lire(adr)
    return memory.read_bytes_as_array(adr, 1, DOMAINE)[1]
end

console.clear()
console.log("=== donner_gear.lua, tout l'equipement ===")

-- Etat avant, pour pouvoir dire ce que le joueur possedait deja.
local deja = {}
for M = 0, NB_COMPTEURS - 1 do
    local v = lire(BASE_EQUIPEMENT + M)
    if v ~= 0 then
        table.insert(deja, string.format("compteur %d x%d", M, v))
    end
end
if #deja == 0 then
    console.log("compteurs non nuls avant : aucun")
else
    console.log("compteurs non nuls avant : " .. table.concat(deja, ", "))
end

local ecrits, intacts, echecs = 0, 0, 0
for M = 0, NB_COMPTEURS - 1 do
    local adresse = BASE_EQUIPEMENT + M
    local avant = lire(adresse)
    if avant >= QUANTITE then
        intacts = intacts + 1
    else
        memory.write_bytes_as_array(adresse, { QUANTITE }, DOMAINE)
        if lire(adresse) == QUANTITE then
            ecrits = ecrits + 1
        else
            echecs = echecs + 1
            console.log(string.format("ECHEC compteur %d, relu %d", M, lire(adresse)))
        end
    end
end

console.log(string.format("\n%d compteur(s) portes a %d, %d deja au moins a %d, %d echec(s)",
    ecrits, QUANTITE, intacts, QUANTITE, echecs))

-- Controle de debordement : le compteur suivant le dernier appartient au
-- champ de bits des badges. S'il a bouge, l'adresse de fin est fausse.
local apres_bloc = lire(BASE_EQUIPEMENT + NB_COMPTEURS)
console.log(string.format("octet suivant le bloc, 0x%05X : %d  (champ des badges, doit etre inchange)",
    BASE_EQUIPEMENT + NB_COMPTEURS, apres_bloc))

console.log("\nA verifier a l'ecran : menu, section equipement des freres,")
console.log("puis celle de Bowser. Tout doit y etre, en double.")
console.log("Le script pose les objets, il ne les equipe pas.")
