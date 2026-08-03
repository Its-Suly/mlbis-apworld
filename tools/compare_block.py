"""Cherche le tableau Exxx de la RAM dans le fichier de sauvegarde.

Teste l'hypothese H2 de formats-bis.md : la sauvegarde reprendrait le bloc
des registres globaux dans l'ordre de la RAM a partir de 2xxx, ce qui
placerait le tableau Exxx a slot + 0x01B4.

Deux mesures independantes, la seconde tranchant meme si la premiere
echoue parce que l'offset predit est faux :

1. comparaison a l'offset predit, dans chacun des deux slots
2. recherche du motif n'importe ou dans le dump SRAM

Piege traite : en debut de partie le bloc est presque entierement nul, et
un motif de zeros se retrouve partout. Le script mesure d'abord combien
d'octets sont non nuls et refuse de conclure si le motif ne discrimine
rien. Il cherche alors l'empreinte, c'est-a-dire la portion allant du
premier au dernier octet non nul, qui est courte mais distinctive.

Offsets de sauvegarde, verifies dans formats-bis.md, source Cheatoglobin :
magie MLRPG3 en tete, slot 1 a 0x0010, slot 2 a 0x0FE8.

Usage :
    venv\\Scripts\\python.exe tools\\compare_block.py \\
        dumps\\run05_Main_RAM.bin dumps\\run05_SRAM.bin
    ... --offset 0x01B4        offset teste dans le slot, defaut H2
    ... --pas-de-recherche     comparaison seule
"""
import argparse
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

BASE_EXXX = 0x0560C8        # offset du tableau dans le domaine Main RAM
TAILLE_EXXX = 0x200         # manuel : 4096 elements
ID_MAX = 757                # les tresors n'occupent que les index bas
TAILLE_TRESORS = 95         # octets couvrant les identifiants 0 a 757

SLOTS = {1: 0x0010, 2: 0x0FE8}
OFFSET_H2 = 0x01B4          # prediction H2 : slot + 0x01B4
SEUIL_DISCRIMINANT = 4      # en dessous, un motif ne prouve rien
SEUIL_SLOT_VIDE = 8         # octets non nuls sous lesquels un slot est vide


def bits_actifs(bloc, limite=None):
    actifs = []
    for i, octet in enumerate(bloc):
        if not octet:
            continue
        for j in range(8):
            if octet >> j & 1:
                n = i * 8 + j
                if limite is None or n <= limite:
                    actifs.append(n)
    return actifs


def toutes_occurrences(foin, aiguille):
    trouvees, depart = [], 0
    while True:
        i = foin.find(aiguille, depart)
        if i < 0:
            return trouvees
        trouvees.append(i)
        depart = i + 1


def situe(offset):
    """Exprime un offset SRAM en slot + delta quand c'est possible."""
    for numero, base in sorted(SLOTS.items(), key=lambda kv: -kv[1]):
        if offset >= base:
            return f"slot {numero} + 0x{offset - base:04X}"
    return "avant le slot 1"


def slot_vide(sram, base):
    """Un slot jamais sauvegarde ne prouve rien, ni dans un sens ni dans
    l'autre. Mesure sur les 0x5F4 octets couverts par le checksum."""
    return sum(1 for b in sram[base:base + 0x5F4] if b) <= SEUIL_SLOT_VIDE


def compare(bloc, sram, offset):
    print(f"Comparaison a l'offset predit slot + 0x{offset:04X}")
    for numero, base in SLOTS.items():
        debut = base + offset
        extrait = sram[debut:debut + TAILLE_EXXX]
        etiquette = f"  slot {numero}, SRAM 0x{debut:04X}"
        if len(extrait) < TAILLE_EXXX:
            print(f"{etiquette} : hors du dump, {len(extrait)} octets seulement")
            continue
        if slot_vide(sram, base):
            print(f"{etiquette} : SLOT VIDE, aucune partie sauvegardee. "
                  f"Le test ne peut rien prouver.")
            continue
        if extrait == bloc:
            print(f"{etiquette} : IDENTIQUE sur {TAILLE_EXXX} octets")
            continue
        if not any(extrait):
            print(f"{etiquette} : fenetre entierement nulle alors que le slot "
                  f"contient des donnees. Argument contre H2, a confirmer.")
            continue
        premier = next(i for i in range(TAILLE_EXXX) if extrait[i] != bloc[i])
        differents = sum(1 for i in range(TAILLE_EXXX) if extrait[i] != bloc[i])
        print(f"{etiquette} : different. Premier ecart a +0x{premier:03X}, "
              f"RAM 0x{bloc[premier]:02X} contre SRAM 0x{extrait[premier]:02X}, "
              f"{differents} octets differents au total")
    print()


def cherche(bloc, sram):
    non_nuls = sum(1 for o in bloc if o)
    print(f"Recherche du motif dans tout le dump SRAM ({len(sram)} octets)")
    print(f"  octets non nuls dans le bloc : {non_nuls} sur {TAILLE_EXXX}")

    if non_nuls == 0:
        print("  bloc entierement nul : aucune recherche ne peut rien prouver.")
        print("  Rejouer apres avoir ramasse au moins un tresor.")
        return

    occurrences = toutes_occurrences(sram, bloc)
    if occurrences:
        print(f"  motif complet trouve a : "
              f"{', '.join(f'0x{o:04X} ({situe(o)})' for o in occurrences)}")
    else:
        print("  motif complet de 0x200 octets : introuvable")

    premier = next(i for i, o in enumerate(bloc) if o)
    dernier = len(bloc) - 1 - next(i for i, o in enumerate(reversed(bloc)) if o)
    empreinte = bloc[premier:dernier + 1]
    print(f"  empreinte : {len(empreinte)} octets, du +0x{premier:03X} au "
          f"+0x{dernier:03X}, {empreinte.hex(' ')}")

    if non_nuls < SEUIL_DISCRIMINANT:
        print(f"  empreinte trop courte pour conclure, moins de "
              f"{SEUIL_DISCRIMINANT} octets non nuls. Une correspondance "
              f"serait du hasard.")

    trouvees = toutes_occurrences(sram, empreinte)
    if not trouvees:
        print("  empreinte : introuvable dans la SRAM")
        print("  Lecture : soit la sauvegarde ne contient pas ce tableau, "
              "soit elle le stocke sous une autre forme.")
        return
    for o in trouvees:
        depart = o - premier
        print(f"  empreinte a 0x{o:04X}, ce qui placerait le debut du "
              f"tableau a 0x{depart:04X} ({situe(depart)})")
        if depart >= 0:
            for numero, base in SLOTS.items():
                if depart - base == OFFSET_H2:
                    print(f"    correspond exactement a la prediction H2")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("main_ram", type=Path, help="dump du domaine Main RAM")
    p.add_argument("sram", type=Path, help="dump du domaine SRAM")
    p.add_argument("--offset", type=lambda v: int(v, 0), default=OFFSET_H2,
                   help="offset teste dans le slot, defaut 0x01B4 (H2)")
    p.add_argument("--pas-de-recherche", action="store_true",
                   dest="pas_de_recherche",
                   help="comparaison seule, sans recherche de motif")
    args = p.parse_args(argv)

    for chemin in (args.main_ram, args.sram):
        if not chemin.exists():
            raise SystemExit(f"introuvable : {chemin}")

    ram = args.main_ram.read_bytes()
    sram = args.sram.read_bytes()
    if len(ram) < BASE_EXXX + TAILLE_EXXX:
        raise SystemExit(
            f"{args.main_ram.name} fait {len(ram)} octets, trop court pour "
            f"contenir le tableau a 0x{BASE_EXXX:06X}. Est-ce bien un dump "
            f"du domaine Main RAM ?"
        )
    if sram[:6] != b"MLRPG3":
        print(f"attention : {args.sram.name} ne commence pas par MLRPG3, "
              f"ce n'est peut-etre pas un dump de la sauvegarde.\n")

    bloc = ram[BASE_EXXX:BASE_EXXX + TAILLE_EXXX]
    tresors = bits_actifs(bloc[:TAILLE_TRESORS], limite=ID_MAX)
    print(f"Bloc Exxx lu dans {args.main_ram.name}, "
          f"0x{BASE_EXXX:06X} a 0x{BASE_EXXX + TAILLE_EXXX:06X}")
    print(f"  tresors marques ramasses : "
          f"{tresors if tresors else 'aucun'}")
    print()

    compare(bloc, sram, args.offset)
    if not args.pas_de_recherche:
        cherche(bloc, sram)

    if all(slot_vide(sram, base) for base in SLOTS.values()):
        print()
        print("CONCLUSION : les deux slots sont vides, H2 n'est ni confirmee "
              "ni refutee.")
        print("Manip qui trancherait : en jeu, ramasser au moins un tresor, "
              "sauvegarder a un bloc de sauvegarde, puis redumper le domaine "
              "SRAM avec tools/dump_ram.lua et relancer ce script.")


if __name__ == "__main__":
    main()
