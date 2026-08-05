"""De l'item Archipelago a l'ecriture memoire.

Comme bitfield.py, ce module ne depend de rien : ni d'Archipelago, ni de
BizHawk, ni meme du reste du monde. Il transforme un nom d'item en une
ecriture a faire, et rien d'autre. C'est verifiable sur un dump, sans
emulateur et sans serveur, et tools/test_client.py le fait.

C'est pour cela que la table de correspondance est passee en argument au
lieu d'etre importee : data.py est genere, il n'a aucune dependance, et
un test peut le charger seul.

Les quatre categories du pool sont etablies, chacune par une mesure en
jeu et non par une deduction.

    coins        u32 a 02056400                            Verifie
    consumable   octet a 02056406 + index                  Verifie
    gear         octet a 02056427 + identifiant - 1        Verifie
    attack_piece bit du champ 2xxx a 02056038              Verifie

Verifie pour les consommables, 4 aout 2026 : un Nut ecrit a
02056406 + 7 apparait au menu et se consomme normalement, et l'index 7
est celui du Nut dans data/noms_items.csv. Recoupement independant au
run13. Detail dans formats-bis.md.

Verifie pour les capacites, 5 aout 2026 : le bit de Fire Flower, 0x2019,
leve a la main dans une partie ou l'attaque n'etait pas debloquee. Elle
apparait au menu Bros Attacks, se selectionne et se joue entierement,
demonstration comprise. Le jeu n'a pas besoin que sa cinematique
d'apprentissage ait eu lieu, ce qui est exactement le cas que produit un
randomizer.

Verifie pour l'equipement, 5 aout 2026 : 1 ecrit au compteur d'index 4
fait apparaitre Heart Wear, qui porte l'identifiant 5. Le compteur d'un
equipement est donc a 02056427 + identifiant - 1, et les 127 compteurs
couvrent les identifiants 1 a 127. Trois recoupements : l'inventaire
mesure au run51 se lit alors « deux Thin Wear et un Shabby Shell », soit
une tenue par frere et la carapace de depart ; l'identifiant 0 est
« No gear », qui n'a pas a etre stocke ; et le dernier compteur tombe a
020564A5, exactement devant le champ de bits des badges.

Toutes les ecritures sont des lectures-modifications-ecritures : le jeu
tient la valeur courante et nous n'en gardons pas de copie. Une copie
qui deriverait du jeu serait pire qu'aucune copie.
"""
from typing import Dict, List, Mapping, NamedTuple, Optional, Set, Tuple

DOMAINE = "Main RAM"

# Offsets dans Main RAM, absolu = 0x02000000 + offset.
COMPTEUR_PIECES = 0x056400
BASE_CONSOMMABLES = 0x056406
NB_CONSOMMABLES = 26

# Les compteurs d'equipement couvrent les identifiants 1 a 127, donc
# l'index vaut identifiant - 1. L'identifiant 0 est « No gear » et le
# 128 « Rental Shell », une carapace pretee par l'histoire ; ni l'un ni
# l'autre ne se stocke, et aucun des deux n'est dans le pool.
BASE_EQUIPEMENT = 0x056427
NB_EQUIPEMENTS = 127
DECALAGE_EQUIPEMENT = 1

# Champ 2xxx, 64 drapeaux importants, 8 octets. Le bit de la variable
# 0x2000 + N est a l'octet N // 8, bit N % 8.
BASE_FLAGS = 0x056038
NB_FLAGS = 64

# Autorise l'usage des Bros Attacks en general, independamment de
# l'attaque elle-meme. Nomme « bros attacks block » par
# randoglobin/patch.py:342, qui le force a 1 pour la meme raison que nous.
#
# **Hypothese** sur sa necessite : dans la partie de test il valait deja
# 1, le Green Shell ayant ete debloque normalement. Rien ne prouve encore
# qu'une attaque livree soit inutilisable sans lui. On le leve quand
# meme : le poser a 1 alors qu'il l'est deja ne coute rien, l'oublier
# couterait une attaque muette.
AUTORISATION_BROS = 0x200B

# Plafonds. Aucun des deux n'est mesure, ce sont des bornes de prudence.
# 999 est la seule valeur de pieces qu'on ait ecrite et vue adoptee par le
# jeu, le 3 aout 2026. Le vrai maximum n'est pas connu, donc un joueur
# deja a 999 ne recevra rien de plus : limite assumee et visible plutot
# que debordement silencieux.
PLAFOND_PIECES = 999
PLAFOND_CONSOMMABLE = 99
PLAFOND_EQUIPEMENT = 99

CATEGORIES_ETABLIES: Set[str] = {"coins", "consumable", "gear", "attack_piece"}

Table = Mapping[str, Tuple[str, int]]


class Ecriture(NamedTuple):
    """Une ecriture a faire, en lecture-modification-ecriture.

    Deux operations seulement, parce que le jeu n'en demande pas plus :
    ajouter a un compteur, ou lever un bit dans un champ.
    """

    adresse: int
    taille: int
    operation: str          # 'ajout' ou 'bit'
    valeur_operande: int    # increment, ou masque du bit
    plafond: int
    libelle: str

    def valeur(self, actuel: int) -> int:
        """Valeur a ecrire, connaissant celle que le jeu porte."""
        if self.operation == "bit":
            return actuel | self.valeur_operande
        return min(actuel + self.valeur_operande, self.plafond)


def ecriture_de_flag(variable: int, libelle: str) -> Ecriture:
    """Lever le bit d'une variable 0x2xxx du champ des drapeaux importants."""
    n = variable - 0x2000
    if not 0 <= n < NB_FLAGS:
        raise ValueError(f"variable {variable:#06x} hors du champ 2xxx")
    return Ecriture(
        BASE_FLAGS + n // 8, 1, "bit", 1 << (n % 8), 0xFF, libelle
    )


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
        return Ecriture(COMPTEUR_PIECES, 4, "ajout", valeur, PLAFOND_PIECES, nom)
    if categorie == "consumable":
        if not 0 <= valeur < NB_CONSOMMABLES:
            raise ValueError(
                f"{nom} : index de consommable {valeur} hors des "
                f"{NB_CONSOMMABLES} compteurs"
            )
        return Ecriture(
            BASE_CONSOMMABLES + valeur, 1, "ajout", 1, PLAFOND_CONSOMMABLE, nom
        )
    if categorie == "gear":
        index = valeur - DECALAGE_EQUIPEMENT
        if not 0 <= index < NB_EQUIPEMENTS:
            raise ValueError(
                f"{nom} : identifiant d'equipement {valeur} sans compteur, "
                f"les compteurs couvrent 1 a {NB_EQUIPEMENTS}"
            )
        return Ecriture(
            BASE_EQUIPEMENT + index, 1, "ajout", 1, PLAFOND_EQUIPEMENT, nom
        )
    return None


def seuils_de_lot(table: Table, exemplaires: Mapping[str, int]) -> Dict[str, int]:
    """Combien de pieces d'un lot Archipelago peut livrer, par item.

    Le jeu demande dix pieces pour debloquer une attaque, mais neuf lots
    sur dix seulement sont completement cartographies : le Jump Helmet
    n'a que deux `location` et le Super Bouncer six. Le seuil est donc le
    nombre d'exemplaires reellement dans le pool, sinon ces deux attaques
    seraient inatteignables par Archipelago seul.

    Consequence assumee : elles se debloquent plus vite que les autres.
    Le jour ou les 22 pieces manquantes seront mesurees, le seuil
    remontera a dix partout sans changer une ligne de code.
    """
    return {
        nom: exemplaires[nom]
        for nom, (categorie, _) in table.items()
        if categorie == "attack_piece" and nom in exemplaires
    }


def livraison_de_lot(nom: str, table: Table) -> List[Ecriture]:
    """Les ecritures qui debloquent l'attaque d'un lot de pieces.

    A n'appeler que lorsque le seuil du lot est atteint. Deux ecritures :
    l'attaque elle-meme, et l'autorisation generale des Bros Attacks.
    """
    entree = table.get(nom)
    if entree is None or entree[0] != "attack_piece":
        raise ValueError(f"{nom} n'est pas une piece d'attaque")
    return [
        ecriture_de_flag(AUTORISATION_BROS, "Bros Attacks autorisees"),
        ecriture_de_flag(entree[1], nom.removesuffix(" Piece")),
    ]


def couverture(table: Table) -> Dict[str, int]:
    """Nombre de noms d'item par categorie de livraison."""
    compte: Dict[str, int] = {}
    for categorie, _ in table.values():
        compte[categorie] = compte.get(categorie, 0) + 1
    return compte
