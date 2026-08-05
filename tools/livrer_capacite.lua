-- Livraison d'une capacite en levant un bit du champ 2xxx.
--
-- Si ca marche, c'est le chemin d'item le plus simple du projet : un
-- marteau, un Drill Bros, une Bros Attack, un badge, tous logent dans les
-- huit octets a 02056038. Aucun compteur, aucun index, aucune quantite.
--
-- CE CHEMIN N'A JAMAIS ETE ECRIT. Les bits ont ete vus monter par le jeu
-- lui-meme, mesure du 5 aout 2026, dumps run48 et run49 : 0x200B et
-- 0x2010 se levent au moment ou l'etoile annonce le Green Shell. Les
-- lire est verifie, les ecrire est exactement ce que ce script teste.
--
-- Adresses :
--   champ 2xxx, 64 bits, 8 octets, Main RAM 0x056038, absolu 02056038
--   bit N  ->  octet 0x056038 + N // 8, bit N % 8
--   variable 0x2000 + N
-- Source : formats-bis.md, table des plages de variables de script.
--
-- Les dix variables de deblocage viennent de notre propre extraction de
-- l'overlay 123, data/bros_attacks.csv, et non d'une source tierce.
--
-- ETAT DE JEU. Faire un savestate AVANT. Debloquer une attaque en avance
-- est un changement d'etat d'histoire ; rien ne dit que le jeu s'y
-- attende, et c'est justement ce qu'on mesure. Rester sur le terrain,
-- hors dialogue et hors cinematique.
--
-- Usage : Tools > Lua Console, Ctrl+O sur ce fichier.

local BASE_2XXX = 0x056038
local DOMAINE = "Main RAM"

-- Cible du test. Fire Flower est choisie parce qu'elle n'est pas encore
-- debloquee dans la partie en cours et qu'elle coute 4 SP, donc
-- utilisable tout de suite si elle apparait.
local VARIABLE = 0x2019
local NOM = "Fire Flower"

-- Les dix Bros Attacks, extraites de l'overlay 123 le 5 aout 2026.
local ATTAQUES = {
    [0x2010] = "Green Shell",
    [0x2011] = "Spin Pipe",
    [0x2012] = "Yoo Who Cannon",
    [0x2013] = "Falling Star",
    [0x2016] = "Jump Helmet",
    [0x2017] = "Super Bouncer",
    [0x2018] = "Mighty Meteor",
    [0x2019] = "Fire Flower",
    [0x201A] = "Snack Basket",
    [0x201B] = "Magic Window",
}
-- 0x200B autorise l'usage des Bros Attacks en general. Nomme
-- « bros attacks block » par randoglobin/patch.py:342, et mesure a 1
-- dans la partie en cours depuis le deblocage du Green Shell.
local AUTORISATION = 0x200B

-- Puissances de deux en ENTIERS. L'operateur ^ de Lua rend toujours un
-- flottant, et memory.write_bytes_as_array leve une InvalidCastException
-- sur un flottant, meme quand il vaut 2.0. Mesure du 5 aout 2026, le
-- premier essai de ce script est mort la.
local PUISSANCES = { 1, 2, 4, 8, 16, 32, 64, 128 }

local function lire_champ()
    return memory.read_bytes_as_array(BASE_2XXX, 8, DOMAINE)
end

local function bit_de(champ, variable)
    local n = variable - 0x2000
    -- read_bytes_as_array rend un tableau indexe a partir de 1.
    local octet = champ[math.floor(n / 8) + 1]
    return math.floor(octet / PUISSANCES[(n % 8) + 1]) % 2
end

console.clear()
console.log("=== livrer_capacite.lua ===")

local avant = lire_champ()
local ligne = ""
for i = 1, 8 do
    ligne = ligne .. string.format("%02X ", avant[i])
end
console.log("champ 2xxx avant : " .. ligne)

local presentes = {}
for variable, nom in pairs(ATTAQUES) do
    if bit_de(avant, variable) == 1 then
        table.insert(presentes, nom)
    end
end
table.sort(presentes)
if #presentes == 0 then
    console.log("attaques deja debloquees : aucune")
else
    console.log("attaques deja debloquees : " .. table.concat(presentes, ", "))
end
console.log(string.format("usage des Bros Attacks (0x200B) : %d",
    bit_de(avant, AUTORISATION)))

if bit_de(avant, VARIABLE) == 1 then
    console.log(string.format(
        "\n%s (0x%04X) est deja debloquee. Le test n'observerait rien.",
        NOM, VARIABLE))
    console.log("Choisir une autre VARIABLE dans la liste ci-dessus.")
    return
end

local n = VARIABLE - 0x2000
local index = math.floor(n / 8) + 1
local adresse = BASE_2XXX + math.floor(n / 8)
local masque = PUISSANCES[(n % 8) + 1]
local nouveau = math.floor(avant[index] + masque)

console.log(string.format("\ncible   : %s, variable 0x%04X, bit %d", NOM, VARIABLE, n))
console.log(string.format("adresse : 0x%05X en %s, absolu %08X, bit %d",
    adresse, DOMAINE, 0x02000000 + adresse, n % 8))
console.log(string.format("octet   : %02X -> %02X", avant[index], nouveau))

memory.write_bytes_as_array(adresse, { nouveau }, DOMAINE)

local apres = lire_champ()
if bit_de(apres, VARIABLE) ~= 1 then
    console.log("\nECHEC : la relecture ne rend pas le bit leve.")
    return
end

-- Un seul octet doit avoir change. Le controle est gratuit et il a deja
-- rattrape une erreur sur la livraison d'objet.
local touches = 0
for i = 1, 8 do
    if avant[i] ~= apres[i] then touches = touches + 1 end
end
console.log(string.format("relu    : bit leve, %d octet(s) modifie(s) sur 8", touches))

console.log("\nL'ecriture a pris en memoire. Ce qui tranche est a l'ecran :")
console.log("  1. entrer en combat")
console.log("  2. ouvrir le menu Bros Attacks de Mario")
console.log(string.format("  3. %s y figure-t-elle ?", NOM))
console.log("  4. si oui, l'utiliser : le jeu la joue-t-il jusqu'au bout ?")
console.log("\nPuis dumper, sauvegarder en jeu, redumper.")
console.log("Si l'attaque n'apparait pas, recharger le savestate : rien")
console.log("n'est perdu, et la reponse est tout aussi utile.")
