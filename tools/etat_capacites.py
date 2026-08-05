"""Lit l'etat des 64 drapeaux importants dans un dump, avec leurs noms.

Lecture seule, aucun acces a la ROM.

Le champ 2xxx porte les capacites : marteau, Mini Mario, Drill Bros,
souffle de feu, aspirateur, badges, Bros Attacks, ameliorations de
boutique. Ecrire un de ces bits livre la capacite, Verifie le 5 aout
2026 sur Fire Flower.

Les noms viennent de `mnllib.bis.consts.ImportantFlags`, importe comme
dependance et non recopie : mnllib est en LGPL-3.0, ce qui l'autorise.

A quoi ce script sert vraiment. Un dump pris a un moment connu de la
partie confronte le nom du drapeau a la realite du jeu. Si le marteau
est marque acquis alors que les freres ne l'ont pas, le nom est faux ou
notre lecture l'est. C'est la seule facon de valider une enumeration que
personne n'utilise, pas meme la bibliotheque qui la declare.

Deux usages :

    venv\\Scripts\\python.exe tools\\etat_capacites.py dumps\\run51_Main_RAM.bin
    venv\\Scripts\\python.exe tools\\etat_capacites.py --journal chemin\\journal_capacites.txt

Le second met les noms sur le journal produit en jouant par
tools/journal_capacites.lua, qui ne note que des numeros de variable :
recopier la table de noms de mnllib dans un fichier Lua du depot serait
en recopier du code LGPL, l'importer ici ne l'est pas.
"""
import re
import sys
from pathlib import Path

from mnllib.bis.consts import ImportantFlags

BASE_FLAGS = 0x056038
NB_OCTETS = 8

if len(sys.argv) < 2:
    raise SystemExit("usage : etat_capacites.py <dump.bin>... | --journal <fichier>")

# bit -> nom, depuis l'enumeration de mnllib
noms = {}
for drapeau in ImportantFlags:
    if drapeau.value and (drapeau.value & (drapeau.value - 1)) == 0:
        noms[drapeau.value.bit_length() - 1] = drapeau.name

if sys.argv[1] == "--journal":
    if len(sys.argv) < 3:
        raise SystemExit("--journal attend un chemin de fichier")
    journal = Path(sys.argv[2])
    if not journal.exists():
        raise SystemExit(f"introuvable : {journal}")
    for ligne in journal.read_text(encoding="utf-8", errors="replace").splitlines():
        def remplacer(m):
            variable = int(m.group(0), 16)
            nom = noms.get(variable - 0x2000, "sans nom dans mnllib")
            return f"{m.group(0)} {nom}"
        print(re.sub(r"0x2[0-9A-Fa-f]{3}", remplacer, ligne))
    sys.exit(0)

for chemin in sys.argv[1:]:
    p = Path(chemin)
    champ = p.read_bytes()[BASE_FLAGS:BASE_FLAGS + NB_OCTETS]
    valeur = int.from_bytes(champ, "little")

    print(f"\n=== {p.name} ===")
    print("octets : " + " ".join(f"{o:02X}" for o in champ))

    leves = [b for b in range(64) if valeur >> b & 1]
    print(f"{len(leves)} drapeau(x) leve(s) sur 64")
    for b in leves:
        nom = noms.get(b, "SANS NOM dans mnllib")
        print(f"  bit {b:>2}  variable 0x{0x2000 + b:04X}  {nom}")

    # Les capacites de progression, celles qui ouvriront des access_rule.
    # Vocabulaire pris a randoglobin/data_classes.py:11-35, une liste que
    # son auteur a laissee vide en notant qu'elle servirait plus tard.
    print("\n  capacites de progression, etat :")
    progression = [
        ("MINI_MARIO", "ml_req_mini_mario"),
        ("HAMMER", "ml_req_hammer"),
        ("SPIN_JUMP", "ml_req_spin_jump"),
        ("DRILL_BROS", "ml_req_drill"),
        ("BLUE_SHELL_BLOCKS", "ml_req_blue_shell"),
        ("BROS_ATTACK_SNACK_BASKET", "ml_req_snack_basket"),
        ("FIRE_BREATH_DISABLED", "kp_req_flame, inverse"),
        ("SLIDING_HAYMAKER", "kp_req_slide_punch"),
        ("BODY_SLAM", "kp_req_body_slam"),
        ("SPIKE_BALL", "kp_req_spike_ball"),
        ("VACUUM", "kp_req_vacuum"),
    ]
    for nom_flag, nom_rando in progression:
        drapeau = ImportantFlags[nom_flag]
        bit = drapeau.value.bit_length() - 1
        etat = "OUI" if valeur >> bit & 1 else "non"
        print(f"    {etat:>3}  0x{0x2000 + bit:04X}  {nom_flag:<26} {nom_rando}")
