-- Bascule un bit du champ des capacites et dit son nouvel etat.
--
-- POURQUOI. On sait poser une capacite, Verifie le 5 aout 2026 sur le
-- Fire Flower. On ne sait pas si le jeu supporte d'en **perdre** une.
-- La question decide de tout : sans patch de ROM, le jeu octroie le
-- marteau au moment prevu, que le serveur l'ait envoye ou non. Si le
-- client peut abaisser le bit, une capacite devient un vrai `item` ; si
-- le jeu casse, il faudra patcher la ROM ou renoncer.
--
-- USAGE. Tools > Lua Console, Ctrl+O sur ce fichier. Il bascule le bit
-- choisi ci-dessous, ecrit l'etat dans la console, puis s'arrete.
-- Le relancer remet le bit dans son etat precedent.
--
-- Adresse Verifiee, champ 2xxx de 8 octets a 02056038, formats-bis.md.
-- Le bit de la variable 0x20NN est l'octet NN // 8, bit NN % 8.

local VARIABLE = 0x2001          -- HAMMER, le plus visible en jeu
local BASE = 0x056038            -- champ 2xxx, offset dans Main RAM
local DOMAINE = "Main RAM"

local n = VARIABLE - 0x2000
local adresse = BASE + math.floor(n / 8)
local masque = 1
for _ = 1, n % 8 do masque = masque * 2 end   -- pas d'operateur ^, il rend
                                              -- un flottant et l'ecriture
                                              -- leve une InvalidCastException

local avant = memory.read_u8(adresse, DOMAINE)
local etait_leve = math.floor(avant / masque) % 2 == 1
local apres
if etait_leve then
    apres = avant - masque
else
    apres = avant + masque
end

memory.write_u8(adresse, apres, DOMAINE)
local relu = memory.read_u8(adresse, DOMAINE)

console.log(string.format("variable 0x%04X, octet 0x%06X", VARIABLE, adresse))
console.log(string.format("  avant %02X, ecrit %02X, relu %02X", avant, apres, relu))
console.log(etait_leve and "  bit ABAISSE : la capacite devrait disparaitre"
                       or "  bit LEVE : la capacite devrait revenir")
console.log("  relancer ce script remet l'etat precedent")
