"""Client BizHawk : detecte les tresors ramasses et les signale au serveur.

LECTURE SEULE POUR L'INSTANT. Il ne recoit aucun item et n'ecrit rien en
memoire. L'ecriture est techniquement acquise, mesuree le 3 aout 2026,
mais le moment sur pour ecrire n'est pas defini : CLAUDE.md impose de
considerer une ecriture pendant un combat ou une cinematique comme
dangereuse tant que rien ne prouve le contraire. C'est le chantier
suivant, pas celui-ci.

Ce que fait la boucle, a chaque passage :

    lire 95 octets a 0x0560C8 dans le domaine Main RAM
    pour chaque bit allume d'index N : location BASE_ID + N

Il n'y a **aucune table de correspondance** entre un bit et une
location, et c'est voulu : l'identifiant d'un tresor dans
TreasureInfo.dat est a la fois son rang de bit dans le tableau Exxx et,
a BASE_ID pres, son identifiant de location. C'est ce que MLSS n'a pas,
et qui lui coute une reconstruction d'adresse par pointeurs et
soustractions a chaque check (Client.py:225-238).

Sources des adresses : formats-bis.md, section « Champ de bits des
tresors ramasses ». Verifie par treize dumps entre le 3 et le 4 aout
2026.
"""
from typing import TYPE_CHECKING, Set

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

from .bitfield import CHAMP_TAILLE, CHAMP_TRESORS, DOMAINE, locations_du_champ
from .data import BASE_ID
from .locations import GAME_NAME

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

# En-tete de cartouche NDS : titre interne sur 12 octets a 0x00, code de
# jeu sur 4 a 0x0C. Notre revision figee est CLJE, Amerique du Nord.
ENTETE_TAILLE = 0x10
TITRE_ATTENDU = b"MARIO&LUIGI3"
CODE_ATTENDU = b"CLJE"


class MLBISClient(BizHawkClient):
    game = GAME_NAME
    # A VERIFIER : chaine renvoyee par emu.getsystemid() sur le coeur
    # NDS de BizHawk 2.10. Aucun monde NDS n'est livre avec Archipelago
    # 0.6.8, donc pas de precedent a copier. Se controle en une ligne
    # dans la console Lua : print(emu.getsystemid())
    system = "NDS"

    local_checked_locations: Set[int]

    def __init__(self) -> None:
        super().__init__()
        self.local_checked_locations = set()

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        try:
            entete = (await bizhawk.read(ctx.bizhawk_ctx, [(0x00, ENTETE_TAILLE, "ROM")]))[0]
        except bizhawk.RequestFailedError:
            return False  # sera retente au passage suivant

        if not entete.startswith(TITRE_ATTENDU):
            return False
        if entete[0x0C:0x10] != CODE_ATTENDU:
            return False

        ctx.game = self.game
        # 0b000 : le serveur ne nous envoie aucun item. Passera a 0b111
        # quand le client saura les livrer sans risquer le plantage.
        ctx.items_handling = 0b000
        ctx.want_slot_data = True
        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        if ctx.server is None or ctx.slot is None:
            return

        try:
            lu = await bizhawk.read(
                ctx.bizhawk_ctx, [(CHAMP_TRESORS, CHAMP_TAILLE, DOMAINE)]
            )
        except bizhawk.RequestFailedError:
            return

        # Une location inconnue du serveur n'est pas une erreur : le champ
        # couvre 760 bits pour 647 tresors exploitables, et les
        # identifiants de bourrage restent a zero.
        a_envoyer = (
            locations_du_champ(lu[0], BASE_ID)
            - self.local_checked_locations
        ) & set(ctx.server_locations)

        if a_envoyer:
            self.local_checked_locations |= a_envoyer
            await ctx.send_msgs(
                [{"cmd": "LocationChecks", "locations": sorted(a_envoyer)}]
            )
