"""Etablit le bit Exxx de chaque piece d'attaque, par balayage de FEvent.

Lecture seule.

Point de depart, mesure du 5 aout 2026 : les dix pieces du Green Shell
sont les variables 0xE700 a 0xE709, et le ramassage met a jour un triplet
6xxx, 0x601B et 0x601C en champs de bits, 0x601D en compteur.

`data/bros_attacks.csv` donne la variable de pieces des dix attaques,
lue dans l'overlay 123. Le triplet est donc base, base+1, base+2.

Signature d'un bloc a piece, lue dans les scripts eux-memes et non
supposee. Une sous-routine de bloc contient exactement :

    commande 0x0020   base+k |= masque      (masque a un seul bit)
    commande 0x0008   Exxx   = 1            (une seule variable)

d'ou l'indice de la piece, sans ambiguite :

    piece = 5 * k + log2(masque)            k vaut 0 ou 1

Le compteur base+2 est ecrit ailleurs, par la sous-routine d'affichage,
avec des litteraux 1 a 10. Le confondre avec un champ de bits produisait
des faux positifs ; c'est pour ca qu'on filtre sur la commande 0x0020.

Un masque a plusieurs bits, typiquement 31, est un octroi en bloc : le
jeu donne cinq pieces d'un coup dans une cinematique. Le script les
compte a part, ce ne sont pas des `location`.

Les fichiers viennent de `vendor/BIS-docs/data`, deja au format attendu
par mnllib. Le script verifie d'abord que le `FEvent.dat` de BIS-docs est
octet pour octet celui de notre ROM, sinon il s'arrete : raisonner sur les
scripts d'une autre revision n'aurait aucun sens.

Temoin : le Green Shell doit rendre 0xE700 a 0xE709 dans l'ordre des
pieces 0 a 9. Si ce n'est pas le cas, la methode est fausse.

Sortie : data/pieces_attaque.csv, une ligne par piece.
"""
import csv
from collections import defaultdict
from pathlib import Path

import ndspy.rom
import mnllib
from mnllib.bis import FEventScriptManager

RACINE = Path(__file__).resolve().parent.parent
ROM = RACINE / "4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"
DATA_DIR = RACINE / "vendor" / "BIS-docs" / "data"

COMMANDE_SET = 0x0008     # bis_docs_commands.yml:80-86
COMMANDE_OR = 0x0020      # deduit des scripts, voir en-tete
NB_PIECES = 10
TEMOIN = ("Green Shell", [0xE700 + k for k in range(NB_PIECES)])

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

with open(RACINE / "data" / "bros_attacks.csv", encoding="utf-8") as f:
    attaques = list(csv.DictReader(f))

# variable de champ de bits -> (nom de l'attaque, moitie 0 ou 1)
champ_vers_attaque = {}
for a in attaques:
    base = int(a["var_pieces"], 16)
    champ_vers_attaque[base] = (a["nom"], 0)
    champ_vers_attaque[base + 1] = (a["nom"], 1)

manager = FEventScriptManager(DATA_DIR)
print(f"FEvent : {len(manager.fevent_chunks)} triples charges")


def un_seul_bit(n):
    return n > 0 and (n & (n - 1)) == 0


pieces = {}                       # (attaque, indice) -> (exxx, salles)
conflits = defaultdict(set)       # (attaque, indice) -> exxx vus
octrois = defaultdict(list)       # attaque -> (salle, moitie, masque)
nb_commandes = 0

for idx, triple in enumerate(manager.fevent_chunks):
    for script in triple[:2]:
        if script is None:
            continue
        sous_routines = list(script.subroutines)
        entete = getattr(script.header, "post_table_subroutine", None)
        if entete is not None:
            sous_routines.append(entete)
        for sub in sous_routines:
            ors, exxx = [], []
            for cmd in getattr(sub, "commands", []) or []:
                if not isinstance(cmd, mnllib.CodeCommand):
                    continue
                nb_commandes += 1
                rv = getattr(cmd, "result_variable", None)
                if not isinstance(rv, mnllib.Variable):
                    continue
                args = cmd.arguments or []
                if cmd.command_id == COMMANDE_OR and rv.number in champ_vers_attaque \
                        and len(args) == 1 and isinstance(args[0], int):
                    ors.append((rv.number, args[0]))
                elif cmd.command_id == COMMANDE_SET and 0xE000 <= rv.number <= 0xFFFF:
                    exxx.append(rv.number)

            for var, masque in ors:
                nom, moitie = champ_vers_attaque[var]
                if not un_seul_bit(masque):
                    octrois[nom].append((idx, moitie, masque))
                    continue
                if len(exxx) != 1:
                    conflits[(nom, -1)].add(idx)
                    continue
                indice = moitie * 5 + masque.bit_length() - 1
                cle = (nom, indice)
                # Une meme piece peut etre definie dans plusieurs chunks.
                # On garde toutes les salles plutot que la derniere vue.
                if cle in pieces:
                    if pieces[cle][0] != exxx[0]:
                        conflits[cle].add(pieces[cle][0])
                        conflits[cle].add(exxx[0])
                    pieces[cle][1].add(idx)
                else:
                    pieces[cle] = (exxx[0], {idx})

print(f"{nb_commandes} commandes parcourues, {len(pieces)} pieces identifiees")

lignes = []
print()
print(f"{'attaque':<16} {'trouvees':>8}  plage Exxx            rangs de bit      salles")
for a in attaques:
    nom = a["nom"]
    trouvees = [(i, *pieces[(nom, i)]) for i in range(NB_PIECES) if (nom, i) in pieces]
    if not trouvees:
        n_octrois = len(octrois.get(nom, []))
        note = f"octroi en bloc, {n_octrois} commande(s) a masque multiple" if n_octrois \
            else "aucune trace"
        print(f"{nom:<16} {0:>8}  {note}")
        continue
    bits = [t[1] for t in trouvees]
    salles = sorted(set().union(*(t[2] for t in trouvees)))
    ordonne = all(trouvees[j][1] < trouvees[j + 1][1] for j in range(len(trouvees) - 1))
    contigu = (max(bits) - min(bits) + 1) == len(bits) and ordonne
    print(f"{nom:<16} {len(trouvees):>8}  0x{min(bits):04X}..0x{max(bits):04X}"
          f"{'  ' if contigu else ' *'}      "
          f"{min(bits) - 0xE000}..{max(bits) - 0xE000}      "
          f"{len(salles)} salle(s) : {', '.join(f'0x{s:03X}' for s in salles[:6])}"
          f"{' ...' if len(salles) > 6 else ''}")
    for indice, exxx, ou in trouvees:
        lignes.append({
            "attaque": nom,
            "piece": indice,
            "variable": f"0x{exxx:04X}",
            "rang_bit": exxx - 0xE000,
            "salle": " ".join(f"0x{s:03X}" for s in sorted(ou)),
            "var_pieces": a["var_pieces"],
            "var_attaque": a["var_attaque"],
            "item_brut": a["item_brut"],
            "lot": a["zone_a"],
        })

print("\n* plage non contigue ou pieces manquantes")

print("\noctrois en bloc, masque a plusieurs bits :")
for nom, liste in sorted(octrois.items()):
    vus = sorted({(s, m, mo) for s, mo, m in liste})
    print(f"  {nom:<16} " + ", ".join(f"salle 0x{s:03X} moitie {mo} masque {m}"
                                      for s, m, mo in vus[:4])
          + (f"  ... {len(vus)-4} de plus" if len(vus) > 4 else ""))

if conflits:
    print("\nconflits, une meme piece vue avec deux variables :")
    for cle, vals in sorted(conflits.items()):
        if cle[1] >= 0:
            print(f"  {cle[0]} piece {cle[1]} : {[hex(v) for v in sorted(vals)]}")

nom_t, attendu = TEMOIN
obtenu = [pieces.get((nom_t, i), (None,))[0] for i in range(NB_PIECES)]
print()
if obtenu == attendu:
    print(f"temoin {nom_t} : les 10 pieces dans l'ordre, 0xE700 a 0xE709, "
          f"conforme a la mesure du 5 aout")
else:
    print(f"TEMOIN ECHOUE {nom_t} : obtenu {[hex(o) if o else None for o in obtenu]}")

(RACINE / "data").mkdir(exist_ok=True)
sortie = RACINE / "data" / "pieces_attaque.csv"
with open(sortie, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["attaque", "piece", "variable", "rang_bit",
                                      "salle", "var_pieces", "var_attaque",
                                      "item_brut", "lot"])
    w.writeheader()
    w.writerows(lignes)
print(f"\necrit : data/pieces_attaque.csv  ({len(lignes)} pieces)")
