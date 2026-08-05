"""De l'item Archipelago a l'ecriture memoire.

Comme bitfield.py, ce module ne depend de rien : ni d'Archipelago, ni de
BizHawk, ni meme du reste du monde. Il transforme un nom d'item en une
ecriture a faire, et rien d'autre. C'est verifiable sur un dump, sans
emulateur et sans serveur, et tools/test_client.py le fait.

C'est pour cela que la table de correspondance est passee en argument au
lieu d'etre importee : data.py est genere, il n'a aucune dependance, et
un test peut le charger seul.

Deux categories sont etablies, deux ne le sont pas. Ce module refuse net
ce qui n'est pas etabli plutot que d'ecrire a une adresse plausible. Une
adresse plausible mais fausse coute des heures.

    coins        u32 a 02056400                            Verifie
    consumable   octet a 02056406 + index                  Verifie
    gear         emplacement d'equipement                  NON ETABLI
    attack_piece variable de deblocage dans le champ 2xxx  NON ETABLI

Verifie pour les consommables, 4 aout 2026 : un Nut ecrit a
02056406 + 7 apparait au menu et se consomme normalement, et l'index 7
est celui du Nut dans data/noms_items.csv. Recoupement independant au
run13. Detail dans formats-bis.md.

Toutes les ecritures sont des lectures-modifications-ecritures : le jeu
tient la valeur courante et nous n'en gardons pas de copie. Une copie
qui deriverait du jeu serait pire qu'aucune copie.
"""
from typing import Dict, Mapping, NamedTuple, Optional, Set, Tuple

DOMAINE = "Main RAM"

# Offsets dans Main RAM, absolu = 0x02000000 + offset.
COMPTEUR_PIECES = 0x056400
BASE_CONSOMMABLES = 0x056406
NB_CONSOMMABLES = 26

# Plafonds. Aucun des deux n'est mesure, ce sont des bornes de prudence.
# 999 est la seule valeur de pieces qu'on ait ecrite et vue adoptee par le
# jeu, le 3 aout 2026. Le vrai maximum n'est pas connu, donc un joueur
# deja a 999 ne recevra rien de plus : limite assumee et visible plutot
# que debordement silencieux.
PLAFOND_PIECES = 999
PLAFOND_CONSOMMABLE = 99

CATEGORIES_ETABLIES: Set[str] = {"coins", "consumable"}

Table = Mapping[str, Tuple[str, int]]


class Ecriture(NamedTuple):
    """Une ecriture a faire, en lecture-modification-ecriture."""

    adresse: int
    taille: int
    increment: int
    plafond: int
    libelle: str

    def valeur(self, actuel: int) -> int:
        """Valeur a ecrire, connaissant celle que le jeu porte."""
        return min(actuel + self.increment, self.plafond)


def livraison_de(nom: str, table: Table) -> Optional[Ecriture]:
    """L'ecriture qui livre cet item, ou None si le chemin n'est pas etabli.

    None n'est pas une erreur, c'est l'etat de la connaissance. L'appelant
    doit traiter l'item comme en attente, pas comme perdu.
    """
    entree = table.get(nom)
    if entree is None:
        return None

    categorie, valeur = entree
    if categorie == "coins":
        return Ecriture(COMPTEUR_PIECES, 4, valeur, PLAFOND_PIECES, nom)
    if categorie == "consumable":
        if not 0 <= valeur < NB_CONSOMMABLES:
            raise ValueError(
                f"{nom} : index de consommable {valeur} hors des "
                f"{NB_CONSOMMABLES} compteurs"
            )
        return Ecriture(
            BASE_CONSOMMABLES + valeur, 1, 1, PLAFOND_CONSOMMABLE, nom
        )
    return None


def couverture(table: Table) -> Dict[str, int]:
    """Nombre de noms d'item par categorie de livraison."""
    compte: Dict[str, int] = {}
    for categorie, _ in table.values():
        compte[categorie] = compte.get(categorie, 0) + 1
    return compte
