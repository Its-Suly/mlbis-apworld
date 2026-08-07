"""Ou le jeu octroie chaque capacite, par balayage de FEvent.

Lecture seule.

CE QUE CA REMPLACE. Les `access_rule` demandent de savoir quelle capacite
s'obtient dans quelle zone. Le mesurer en jouant, c'est finir le jeu,
soit des dizaines d'heures. Les capacites sont des variables `2xxx`, et
les scripts qui les posent sont dans `FEvent`, avec la salle pour
adresse. La meme donnee se lit donc en quelques secondes.

METHODE, ce qui est lu et ce qui est deduit.

  - Les 48 variables `0x2000` a `0x2030` sont ecrites par une seule
    commande, `0x0008`, avec un argument entier. **Mesure** de ce
    balayage, aucune autre forme n'apparait dans les 534 548 commandes.
  - Une ecriture a 1 est un octroi, une ecriture a 0 un retrait. Le cas
    `FIRE_BREATH_DISABLED` se lit donc a l'envers, ce que la partie du
    7 aout 2026 a confirme : le bit retombe quand Bowser retrouve son
    souffle.
  - Trois chunks, 0, 1 et 2, ecrivent 20, 27 et 46 variables. Aucune
    salle ne donne vingt capacites : ce sont des initialisations ou des
    scripts de debug. Ils sont ecartes du resultat et affiches a part
    plutot que passes sous silence.

L'INDEX DE CHUNK EST L'INDEX DE CARTE. `FEvent` porte 681 chunks et la
ROM 0x2A9 = 681 cartes. Le compte seul ne prouverait rien, d'ou le
temoin ci-dessous.

TEMOIN, deux sources qui ne se citent pas. `data/bros_attacks.csv` vient
de l'overlay 123 et donne le lot de pieces de chaque Bros Attack, donc sa
zone : Snack Basket dans Dimble, Spin Pipe dans Plack, Magic Window dans
Castle. Le balayage, lui, ne sait rien des lots. Si la salle ou le script
octroie l'attaque tombe dans la zone du lot, la correspondance chunk vers
carte tient. Sinon le resultat est faux et le script le dit.

Chaine carte -> zone reprise de `tools/build_salles_zones.py`, sans son
filtre sur les tresors : ici les salles interessantes sont souvent des
cartes de cinematique, qui n'en portent aucun.

Sortie : data/capacites_fevent.csv, une ligne par variable.
"""
import csv
import struct
from collections import defaultdict
from pathlib import Path

import ndspy.rom
import mnllib
from mnllib.bis import FEventScriptManager
from mnllib.bis.consts import ImportantFlags

RACINE = Path(__file__).resolve().parent.parent
ROM = RACINE / "4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"
DATA_DIR = RACINE / "vendor" / "BIS-docs" / "data"
SORTIE = RACINE / "data" / "capacites_fevent.csv"

# Offsets de la chaine carte -> zone, sources dans build_salles_zones.py
NB_CARTES = 0x2A9
MAP_METADATA = 0x000098A0     # overlay 3
MAP_ICON_DATA = 0x0000864C    # overlay 129
NB_ICONES = 0x23
ZONE_DEFAUT = 0xA             # interieur du lac Blubble

BAS, HAUT = 0x2000, 0x2030
CMD_SET = 0x0008              # bis_docs_commands.yml:80-86
CMD_LIT = 0x0002              # commande qui lit une variable en argument
SEUIL_FOURRE_TOUT = 8         # variables distinctes au-dela desquelles un
                              # chunk n'est plus une salle de jeu

rom = ndspy.rom.NintendoDSRom.fromFile(str(ROM))

fevent_rom = rom.getFileByName("FEvent/FEvent.dat")
fevent_docs = (DATA_DIR / "data" / "FEvent" / "FEvent.dat").read_bytes()
if fevent_rom != fevent_docs:
    raise SystemExit(
        f"FEvent.dat differe : ROM {len(fevent_rom)} octets, BIS-docs "
        f"{len(fevent_docs)}. Revisions differentes, balayage abandonne."
    )
print(f"recoupement : FEvent.dat identique entre la ROM et BIS-docs, "
      f"{len(fevent_rom)} octets")

# ----------------------------------------------------------------- zones
overlays = rom.loadArm9Overlays([3, 129])
ov3 = overlays[3].data
ov129 = overlays[129].data

noms_zones = {}
with open(RACINE / "data" / "noms_zones.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        noms_zones[int(r["index"])] = r["nom"]

icones = []
for k in range(NB_ICONES):
    off = MAP_ICON_DATA + k * 12
    icones.append((int.from_bytes(ov129[off:off + 2], "little"),
                   struct.unpack("<HHH", ov129[off + 4:off + 10])))


def zone_de_carte(j):
    meta = struct.unpack("<III", ov3[MAP_METADATA + j * 12:MAP_METADATA + j * 12 + 12])
    select_map = (meta[0] >> 2) & 0x3FF
    for index_zone, couverts in icones:
        if select_map in couverts:
            return noms_zones.get(index_zone, f"?{index_zone}")
    return noms_zones.get(ZONE_DEFAUT, "?")


zone_par_carte = {j: zone_de_carte(j) for j in range(NB_CARTES)}

# ---------------------------------------------------------------- noms
noms = {0x2000 + f.value.bit_length() - 1: f.name for f in ImportantFlags}

# --------------------------------------------------------------- balayage
manager = FEventScriptManager(DATA_DIR)
nb_chunks = len(manager.fevent_chunks)
print(f"FEvent : {nb_chunks} chunks, ROM : {NB_CARTES} cartes", end="")
print("  (comptes egaux)" if nb_chunks == NB_CARTES else "  ** COMPTES DIFFERENTS **")

ecritures = defaultdict(list)      # var -> [(chunk, valeur)]
lectures = defaultdict(set)        # var -> {chunk}
par_chunk = defaultdict(set)       # chunk -> {var ecrites}
nb_commandes = 0

for idx, triple in enumerate(manager.fevent_chunks):
    for script in triple[:2]:
        subs = list(getattr(script, "subroutines", []) or [])
        entete = getattr(getattr(script, "header", None), "post_table_subroutine", None)
        if entete is not None:
            subs.append(entete)
        for sub in subs:
            for cmd in getattr(sub, "commands", []) or []:
                if not isinstance(cmd, mnllib.CodeCommand):
                    continue
                nb_commandes += 1
                rv = getattr(cmd, "result_variable", None)
                if isinstance(rv, mnllib.Variable) and BAS <= rv.number <= HAUT:
                    if cmd.command_id != CMD_SET:
                        raise SystemExit(
                            f"commande 0x{cmd.command_id:04X} inattendue sur "
                            f"0x{rv.number:04X}, chunk {idx} : la forme unique "
                            f"suppose par ce script n'est plus vraie"
                        )
                    args = cmd.arguments or []
                    val = args[0] if args and isinstance(args[0], int) else None
                    ecritures[rv.number].append((idx, val))
                    par_chunk[idx].add(rv.number)
                for a in (cmd.arguments or []):
                    if isinstance(a, mnllib.Variable) and BAS <= a.number <= HAUT:
                        lectures[a.number].add(idx)

print(f"{nb_commandes} commandes parcourues, {len(ecritures)} variables ecrites")

fourre_tout = sorted(c for c, v in par_chunk.items() if len(v) >= SEUIL_FOURRE_TOUT)
print(f"\nchunks fourre-tout ecartes, {SEUIL_FOURRE_TOUT} variables ou plus :")
for c in fourre_tout:
    print(f"  chunk {c:>4} : {len(par_chunk[c])} variables, zone {zone_par_carte.get(c, '?')}")

# ---------------------------------------------------------------- resultat
lignes = []
for var in sorted(ecritures):
    poses = sorted({c for c, v in ecritures[var] if v == 1 and c not in fourre_tout})
    retires = sorted({c for c, v in ecritures[var] if v == 0 and c not in fourre_tout})
    lignes.append({
        "variable": f"0x{var:04X}",
        "nom": noms.get(var, "sans nom dans mnllib"),
        "nb_salles_octroi": len(poses),
        "salles_octroi": " ".join(str(c) for c in poses),
        "zones_octroi": " | ".join(sorted({zone_par_carte.get(c, "?") for c in poses})),
        "salles_retrait": " ".join(str(c) for c in retires),
        "zones_retrait": " | ".join(sorted({zone_par_carte.get(c, "?") for c in retires})),
        "nb_ecritures_total": len(ecritures[var]),
        "nb_salles_qui_la_lisent": len(lectures.get(var, ())),
    })

largeur = max(len(l["nom"]) for l in lignes)
print(f"\n{'var':<8} {'nom':<{largeur}}  octroi")
for l in lignes:
    if l["nb_salles_octroi"] == 0:
        detail = "aucun script, octroi par le code ARM ou par les chunks ecartes"
    else:
        detail = f"{l['nb_salles_octroi']} salle(s) : {l['salles_octroi']}  -> {l['zones_octroi']}"
    if l["salles_retrait"]:
        detail += f"   | retrait : {l['salles_retrait']} -> {l['zones_retrait']}"
    print(f"{l['variable']:<8} {l['nom']:<{largeur}}  {detail}")

# ---------------------------------------------------------------- temoin
print("\nTEMOIN, la salle d'octroi doit tomber dans la zone du lot de pieces")
with open(RACINE / "data" / "bros_attacks.csv", encoding="utf-8") as f:
    attaques = list(csv.DictReader(f))

verdicts = []
for a in attaques:
    var = int(a["var_attaque"], 16)
    poses = sorted({c for c, v in ecritures.get(var, []) if v == 1 and c not in fourre_tout})
    if not poses:
        print(f"  {a['nom']:<16} aucun script d'octroi, sans avis")
        continue
    prefixe = a["zone_a"].split()[0]        # "Plack Pieces" -> "Plack"
    zones = {zone_par_carte.get(c, "?") for c in poses}
    ok = any(prefixe.lower() in z.lower() for z in zones)
    verdicts.append(ok)
    print(f"  {a['nom']:<16} lot {a['zone_a']:<16} salle(s) {poses} "
          f"-> {', '.join(sorted(zones)):<24} {'concorde' if ok else '** DISCORDE **'}")

if verdicts:
    print(f"  {sum(verdicts)}/{len(verdicts)} concordent")

# --------------------------------------------- comparaison aux guides
print("\nCOMPARAISON a data/progression_hypothese.csv, guides en ligne")
with open(RACINE / "data" / "progression_hypothese.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        var = int(r["variable"], 16)
        poses = sorted({c for c, v in ecritures.get(var, []) if v == 1 and c not in fourre_tout})
        retires = sorted({c for c, v in ecritures.get(var, []) if v == 0 and c not in fourre_tout})
        cibles = poses or retires
        zones = sorted({zone_par_carte.get(c, "?") for c in cibles})
        etat = "concorde" if r["zone_obtention"] in zones else "diverge"
        if not cibles:
            etat = "sans script"
        print(f"  {r['capacite']:<18} guide {r['zone_obtention']:<16} "
              f"balayage {', '.join(zones) if zones else '-':<28} {etat}")

SORTIE.parent.mkdir(exist_ok=True)
with open(SORTIE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
    w.writeheader()
    w.writerows(lignes)
print(f"\necrit : {SORTIE.relative_to(RACINE)}  ({len(lignes)} variables)")
