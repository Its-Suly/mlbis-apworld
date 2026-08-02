"""Compare deux dumps de RAM produits par tools/dump_ram.lua.

Usage :
    venv\\Scripts\\python.exe tools\\diff_ram.py dumps\\dump_01.bin dumps\\dump_02.bin

Repond a une seule question : quels bits ont change entre les deux dumps.
Si un bloc a ete frappe entre les deux et que l'hypothese du champ de bits
tient, on doit voir un tres petit nombre de bits basculer de 0 a 1.
"""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def charger(chemin):
    data = Path(chemin).read_bytes()
    print(f"{chemin} : {len(data)} octets")
    return data


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 1

    a = charger(sys.argv[1])
    b = charger(sys.argv[2])
    if len(a) != len(b):
        print(f"\nATTENTION : tailles differentes, {len(a)} contre {len(b)}. "
              "Comparaison bornee au plus court.")
    taille = min(len(a), len(b))

    octets_differents = [i for i in range(taille) if a[i] != b[i]]
    print(f"\noctets differents : {len(octets_differents)} sur {taille} "
          f"({100 * len(octets_differents) / taille:.3f} %)")

    if not octets_differents:
        print("\nAucune difference. Le dump n'a probablement pas ete refait "
              "apres l'action, ou les deux fichiers sont identiques.")
        return 0

    # Bits passes de 0 a 1 : c'est ce qu'on attend d'un flag « ramasse »
    montees = []
    descentes = []
    for i in octets_differents:
        change = a[i] ^ b[i]
        for j in range(8):
            if change & (1 << j):
                if b[i] & (1 << j):
                    montees.append((i, j))
                else:
                    descentes.append((i, j))

    print(f"bits 0 -> 1 : {len(montees)}")
    print(f"bits 1 -> 0 : {len(descentes)}")

    # Zones contigues, pour separer le bruit (position du joueur, timers,
    # animations) d'un eventuel champ de flags isole
    zones = []
    debut = octets_differents[0]
    precedent = debut
    for i in octets_differents[1:]:
        if i - precedent > 64:
            zones.append((debut, precedent))
            debut = i
        precedent = i
    zones.append((debut, precedent))

    print(f"\nzones contigues de changement (regroupees a moins de 64 octets) : {len(zones)}")
    isolees = [(d, f) for d, f in zones if f - d < 16]
    print(f"dont zones etroites, moins de 16 octets : {len(isolees)}")
    print("\nles 40 premieres zones :")
    for d, f in zones[:40]:
        n = sum(1 for i in octets_differents if d <= i <= f)
        marque = "  <-- etroite" if f - d < 16 else ""
        print(f"  0x{d:06X} a 0x{f:06X}  ({f - d + 1:5d} octets, {n:4d} differents){marque}")

    if len(montees) <= 64:
        print("\nbits passes de 0 a 1, avec leur rang si le champ commencait a "
              "l'octet de la zone :")
        for i, j in montees:
            print(f"  octet 0x{i:06X} bit {j}   a=0x{a[i]:02X} b=0x{b[i]:02X}")

    print("\nPour la suite : si une zone etroite contient exactement un ou deux "
          "bits montes, c'est le candidat. Refaire un troisieme dump apres un "
          "second bloc de la meme salle : les deux rangs de bits doivent differer "
          "de la meme valeur que les identifiants des deux tresors dans "
          "data/locations_bis.csv.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
