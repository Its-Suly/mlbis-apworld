"""Le champ de bits des variables Exxx, et sa conversion en locations.

Ce module ne depend de rien : ni d'Archipelago, ni du reste du monde.
C'est deliberе. La connaissance du plan memoire du jeu est verifiable
sur un dump, sans emulateur et sans serveur, et tools/test_client.py le
fait. Tout ce qui a besoin d'Archipelago vit dans client.py.

Adresses etablies par les dumps du 3 au 5 aout 2026, detail dans
formats-bis.md section « Champ de bits des tresors ramasses ».

    bit de rang N  ->  octet 0x0560C8 + N // 8, bit N % 8

Le rang du bit EST l'identifiant des octets 4-5 de TreasureInfo.dat pour
un tresor, et le numero de variable moins 0xE000 pour une piece
d'attaque. L'identifiant de location vaut BASE_ID + ce rang dans les deux
cas. Aucune table intermediaire, par construction.
"""
from typing import Set

# Tableau de bits Exxx des variables de script, 4096 elements, 0x200
# octets. Adresse absolue 020560C8, soit cet offset dans Main RAM.
#
# On lit le tableau entier, et non la fenetre juste suffisante. Les
# tresors tiennent dans 95 octets, les pieces d'attaque poussent la borne
# a 261, et la prochaine famille de locations la deplacera encore. Une
# borne recalculee a chaque fois est une occasion de se tromper d'un
# octet ; 0x200 est la taille du tableau et ne bougera pas.
CHAMP_TRESORS = 0x0560C8
CHAMP_TAILLE = 0x200
DOMAINE = "Main RAM"


def locations_du_champ(champ: bytes, base_id: int) -> Set[int]:
    """Identifiants de location correspondant aux bits allumes.

    Les bits sont ranges LSB en premier, mesure du 3 aout 2026 : le
    premier bloc frappe a mis le bit 0, le second le bit 1.
    """
    trouvees = set()
    for octet_index, octet in enumerate(champ):
        if not octet:
            continue
        for bit in range(8):
            if octet >> bit & 1:
                trouvees.add(base_id + octet_index * 8 + bit)
    return trouvees
