-- Enregistre chaque capacite acquise pendant qu'on joue.
--
-- POURQUOI. Le monde n'a aucune `access_rule` : les 16 regions pendent
-- au Menu sans exigence. Pour en ecrire, il faut savoir quelle capacite
-- ouvre quelle zone, et cette donnee n'existe nulle part. Randoglobin a
-- declare le vocabulaire des prerequis, data_classes.py:11-35, puis a
-- laisse le tableau vide en notant qu'il servirait plus tard.
--
-- Plutot que de deduire la progression d'une memoire de joueur ou d'un
-- guide en ligne, ce script la mesure : il tourne pendant la partie et
-- note chaque changement du champ des capacites, avec le nombre de
-- tresors deja ramasses comme reperage temporel.
--
-- Une partie jouee normalement produit alors le tableau qui manque.
--
-- CE QU'IL SURVEILLE
--   champ 2xxx, 8 octets a 02056038          les capacites, Verifie
--   tableau Exxx, 0x200 octets a 020560C8    pour compter les tresors
--
-- Il n'ECRIT RIEN en memoire. Seul un fichier texte est produit, a cote
-- de BizHawk, journal_capacites.txt.
--
-- POURQUOI PAS DE NOMS ICI. Les 40 noms de capacites vivent dans
-- mnllib, en LGPL-3.0. L'utiliser comme dependance est libre, en
-- recopier une table dans notre depot est autre chose. Le journal note
-- donc le numero de variable, et
--     venv\Scripts\python.exe tools\etat_capacites.py --journal
-- y met les noms en important mnllib proprement.
--
-- COHABITATION. Le script passe par event.onframeend et ne boucle pas,
-- donc il tourne en meme temps que le connecteur Archipelago dans la
-- meme console Lua. Il ne controle l'etat qu'une fois par seconde, et il
-- ne vide pas la console pour ne pas effacer les messages du connecteur.
--
-- Usage : Tools > Lua Console, Ctrl+O sur ce fichier, puis jouer.

local BASE_FLAGS = 0x056038
local NB_FLAGS_OCTETS = 8
local BASE_EXXX = 0x0560C8
local NB_EXXX_OCTETS = 0x200
local DERNIER_TRESOR = 757
local DOMAINE = "Main RAM"
local PERIODE = 60          -- images entre deux controles

-- Chemin du journal. Par defaut a cote de BizHawk, mais le lanceur pose
-- JOURNAL_CHEMIN pour l'ecrire dans le projet : lance depuis un
-- raccourci, le repertoire courant est celui de l'emulateur et le
-- fichier finirait perdu au milieu de ses DLL.
local FICHIER = JOURNAL_CHEMIN or "journal_capacites.txt"

-- Puissances entieres : l'operateur ^ de Lua rend un flottant, ce qui a
-- deja coute un plantage le 5 aout 2026.
local P = { 1, 2, 4, 8, 16, 32, 64, 128 }

local precedent = nil
local compteur = 0

local function octets(base, taille)
    return memory.read_bytes_as_array(base, taille, DOMAINE)
end

local function bit_de(tableau, n)
    return math.floor(tableau[math.floor(n / 8) + 1] / P[(n % 8) + 1]) % 2
end

local function compter_tresors()
    local e = octets(BASE_EXXX, NB_EXXX_OCTETS)
    local n = 0
    for rang = 0, DERNIER_TRESOR do
        n = n + bit_de(e, rang)
    end
    return n
end

local fichier = io.open(FICHIER, "a")

local function noter(texte)
    console.log(texte)
    if fichier then
        fichier:write(texte .. "\n")
        fichier:flush()
    end
end

noter("=== journal_capacites.lua, nouvelle session ===")

local function controler()
    compteur = compteur + 1
    if compteur % PERIODE ~= 0 then
        return
    end

    local actuel = octets(BASE_FLAGS, NB_FLAGS_OCTETS)

    if precedent == nil then
        precedent = actuel
        local leves = {}
        for b = 0, 63 do
            if bit_de(actuel, b) == 1 then
                table.insert(leves, string.format("0x%04X", 0x2000 + b))
            end
        end
        noter(string.format("depart   %d tresor(s), deja acquis : %s",
            compter_tresors(),
            #leves > 0 and table.concat(leves, " ") or "rien"))
        return
    end

    local change = false
    for i = 1, NB_FLAGS_OCTETS do
        if actuel[i] ~= precedent[i] then change = true end
    end
    if not change then
        return
    end

    local tresors = compter_tresors()
    for b = 0, 63 do
        local avant, apres = bit_de(precedent, b), bit_de(actuel, b)
        if avant ~= apres then
            noter(string.format("%s  0x%04X  apres %d tresor(s)",
                apres == 1 and "ACQUIS" or "PERDU ", 0x2000 + b, tresors))
        end
    end
    precedent = actuel
end

event.onframeend(controler)
