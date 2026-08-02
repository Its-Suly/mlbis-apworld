-- Dump de la RAM de travail depuis BizHawk 2.10.
--
-- Usage : ouvrir ce script dans Tools > Lua Console (Ctrl+O).
-- Il ecrit UN jeu de dumps puis s'arrete. Pour le suivant, refaire Ctrl+O
-- sur le meme fichier. Les fichiers sont numerotes automatiquement :
--   run01_Main_RAM.bin, run01_Shared_WRAM.bin, run01_ARM7_WRAM.bin
--   run02_...
--
-- API verifiee dans vendor/Archipelago/data/lua/connector_bizhawk_generic.lua
-- lignes 393 et 401 :
--   memory.getmemorydomainsize(domaine)
--   memory.read_bytes_as_array(adresse, taille, domaine)  -- table indexee a 1
-- Indexation a 1 des tableaux d'octets confirmee par data/lua/base64.lua ligne 61.
--
-- CORRECTION 3 aout 2026 : memory.getmemorydomainlist() est indexee a partir
-- de 0 sur le coeur NDS, pas de 1. La version precedente sautait la premiere
-- entree, qui est justement Main RAM. On balaie donc de 0 a #liste inclus.

local DOSSIER = [[C:\Users\sulyv\Documents\Projet BIS\dumps\]]
local CHUNK = 4096
-- SRAM fait 8192 octets, or la sauvegarde decrite par Cheatoglobin s'etend
-- jusqu'a 0x0FE8 + 0x7EC + 0x5F4 = 8136 octets. C'est tres probablement le
-- fichier de sauvegarde en direct. Il ne coute que 8 Ko, on le prend.
local VOULUS = { "Main RAM", "Shared WRAM", "ARM7 WRAM", "SRAM" }
local unpack = table.unpack or unpack

console.clear()
console.log("=== dump_ram.lua (corrige) ===")

-- 1. Lister les domaines, en balayant a partir de 0
local liste = memory.getmemorydomainlist()
local domaines = {}
for i = 0, #liste do
    local nom = liste[i]
    if nom ~= nil and nom ~= "" then
        local ok, taille = pcall(memory.getmemorydomainsize, nom)
        domaines[nom] = ok and taille or -1
        console.log(string.format("  [%d] %-20s %s", i, nom,
            ok and (taille .. " octets") or "(taille illisible)"))
    end
end

-- 2. Retenir ceux qu'on veut et qui existent vraiment
local cibles = {}
for _, nom in ipairs(VOULUS) do
    local taille = domaines[nom]
    if taille ~= nil and taille > 0 then
        cibles[#cibles + 1] = { nom = nom, taille = taille }
    else
        console.log("ABSENT ou vide, ignore : " .. nom)
    end
end
if #cibles == 0 then
    console.log("\nECHEC : aucun domaine voulu n'est disponible.")
    console.log("Copier la liste ci-dessus et la transmettre.")
    return
end

-- 3. Numero de run libre
local run = 1
while run < 100 do
    local f = io.open(string.format("%srun%02d_Main_RAM.bin", DOSSIER, run), "rb")
    if f == nil then break end
    f:close()
    run = run + 1
end

-- 4. Ecrire
console.log("")
for _, cible in ipairs(cibles) do
    local base = cible.nom:gsub("%s+", "_")
    local chemin = string.format("%srun%02d_%s.bin", DOSSIER, run, base)
    local f, err = io.open(chemin, "wb")
    if f == nil then
        console.log("ECHEC ouverture " .. chemin .. " : " .. tostring(err))
        console.log("Le dossier " .. DOSSIER .. " existe-t-il ?")
        return
    end
    local adresse = 0
    while adresse < cible.taille do
        local n = math.min(CHUNK, cible.taille - adresse)
        local octets = memory.read_bytes_as_array(adresse, n, cible.nom)
        f:write(string.char(unpack(octets, 1, n)))
        adresse = adresse + n
    end
    f:close()
    console.log(string.format("OK -> run%02d_%s.bin  (%d octets)", run, base, cible.taille))
end

console.log(string.format("\nRun %02d termine. Refaire Ctrl+O pour le suivant.", run))
