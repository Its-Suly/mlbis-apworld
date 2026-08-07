"""Client BizHawk : signale les checks au serveur et livre les items recus.

Ce que fait la boucle, a chaque passage :

    lire les 0x200 octets a 0x0560C8 dans le domaine Main RAM
    pour chaque bit allume de rang N : location BASE_ID + N
    livrer les items recus qui ne l'ont pas encore ete

Il n'y a **aucune table de correspondance** entre un bit et une
location, et c'est voulu : le rang du bit est a la fois l'identifiant du
tresor dans TreasureInfo.dat, ou le numero de variable d'une piece
d'attaque, et a BASE_ID pres l'identifiant de location. C'est ce que MLSS
n'a pas, et qui lui coute une reconstruction d'adresse par pointeurs et
soustractions a chaque check (Client.py:225-238).

Le tableau est lu en entier, donc la plupart des bits allumes ne
correspondent a rien : drapeaux d'ennemis vaincus, drapeaux d'histoire.
Ils sont ecartes par l'intersection avec ctx.server_locations, qui est
la seule liste faisant autorite.

LES DEUX SORTES DE LIVRAISON. Elles n'ont pas la meme nature, et les
traiter pareil serait une erreur.

  - Les compteurs, pieces d'or, consommables, equipement. Le joueur les
    consomme, donc la memoire ne dit pas ce qui a deja ete livre. Il faut
    un index, et il vit dans le DataStorage du serveur.
  - Les capacites, un bit du champ 2xxx. Le bit ne redescend jamais.
    L'etat a atteindre se deduit entierement de ctx.items_received et de
    la memoire, donc **aucun index n'est necessaire** : on relit, on
    compare, on ecrit ce qui manque. Une livraison rejouee est sans
    effet, ce qui rend cette moitie insensible aux deconnexions.

DEFAUT CONNU DE L'INDEX. MLSS range le sien dans la RAM du jeu,
`Client.py:158`, ce qui le garde synchrone avec la sauvegarde : recharger
un savestate rejoue les items. Le notre est cote serveur, donc un
rechargement de savestate laisse le serveur croire des items livres que
le jeu n'a plus. C'est le prix assume de ne rien ecrire dans une zone de
sauvegarde qu'on ne comprend pas. La moitie « capacites » n'a pas ce
defaut.

Sources des adresses : formats-bis.md, sections « Champ de bits des
tresors ramasses », « Les 78 pieces dont on connait la variable » et
« Adresses utiles, la primitive de livraison d'items ». Verifie par les
dumps du 3 au 5 aout 2026.
"""
from typing import TYPE_CHECKING, Dict, List, Set

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

from .bitfield import CHAMP_TAILLE, CHAMP_TRESORS, DOMAINE, locations_du_champ
from .data import BASE_ID, ITEM_DELIVERY, VANILLA_ITEMS
from .delivery import (
    Ecriture,
    ecritures_capacites,
    livraison_de,
    livraison_de_lot,
    seuils_de_lot,
)
from .items import VARIABLE_DE_CAPACITE, item_name_to_id
from .locations import GAME_NAME

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

# En-tete de cartouche NDS : titre interne sur 12 octets a 0x00, code de
# jeu sur 4 a 0x0C. Notre revision figee est CLJE, Amerique du Nord.
ENTETE_TAILLE = 0x10
TITRE_ATTENDU = b"MARIO&LUIGI3"
CODE_ATTENDU = b"CLJE"

# identifiant d'item -> nom, pour retrouver la livraison depuis le reseau
NOM_PAR_ID: Dict[int, str] = {i: nom for nom, i in item_name_to_id.items()}

SEUILS = seuils_de_lot(ITEM_DELIVERY, VANILLA_ITEMS)


class MLBISClient(BizHawkClient):
    game = GAME_NAME
    # Verifie le 4 aout 2026 : emu.getsystemid() repond "NDS" sur le
    # coeur NDS de BizHawk 2.10. Aucun monde NDS n'est livre avec
    # Archipelago 0.6.8, il n'y avait donc pas de precedent a copier.
    system = "NDS"

    local_checked_locations: Set[int]
    cle_index: str
    index_local: int

    def __init__(self) -> None:
        super().__init__()
        self.local_checked_locations = set()
        self.cle_index = ""
        # Copie locale de l'index, avancee des que l'ecriture est faite.
        # Le serveur ne renvoie sa valeur qu'au tour suivant, et la boucle
        # repasse avant : sans ce garde-fou, le meme item serait livre
        # plusieurs fois.
        self.index_local = 0
        # Faux tant que la seed n'a pas dit le contraire. C'est le sens
        # sur : une seed generee sans melange des capacites laisse le jeu
        # les octroyer, et les abaisser retirerait au joueur le marteau
        # que rien ne lui rendrait.
        self.melange_capacites = False

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
        # 0b111 : items de depart, les notres, et ceux des autres. Les 95
        # items du pool ont tous une adresse d'ecriture verifiee.
        ctx.items_handling = 0b111
        ctx.want_slot_data = True
        return True

    def on_package(self, ctx: "BizHawkClientContext", cmd: str, args: dict) -> None:
        if cmd == "Connected":
            # ctx.team et ctx.slot sont poses avant cet appel,
            # CommonClient.py:1005-1006 puis 1123.
            self.cle_index = f"mlbis_livres_{ctx.team}_{ctx.slot}"
            self.index_local = 0
            ctx.set_notify(self.cle_index)
            slot_data = args.get("slot_data") or {}
            self.melange_capacites = bool(slot_data.get("shuffle_abilities"))

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        if ctx.server is None or ctx.slot is None:
            return

        try:
            lu = await bizhawk.read(
                ctx.bizhawk_ctx, [(CHAMP_TRESORS, CHAMP_TAILLE, DOMAINE)]
            )
        except bizhawk.RequestFailedError:
            return

        # Une location inconnue du serveur n'est pas une erreur, c'est le
        # cas courant : le champ couvre 4096 bits pour 725 locations, et
        # les drapeaux d'histoire y sont nombreux des le debut de partie.
        a_envoyer = (
            locations_du_champ(lu[0], BASE_ID)
            - self.local_checked_locations
        ) & set(ctx.server_locations)

        if a_envoyer:
            self.local_checked_locations |= a_envoyer
            await ctx.send_msgs(
                [{"cmd": "LocationChecks", "locations": sorted(a_envoyer)}]
            )

        await self.livrer_capacites(ctx)
        await self.livrer_compteurs(ctx)

    # --- livraison ----------------------------------------------------

    async def appliquer(
        self, ctx: "BizHawkClientContext", ecritures: List[Ecriture]
    ) -> bool:
        """Lire, modifier, ecrire. Vrai si tout est passe.

        Une ecriture par appel, sequentielle : le jeu peut modifier la
        meme adresse entre la lecture et l'ecriture, et grouper ne
        reduirait pas ce risque, seulement la lisibilite.
        """
        for e in ecritures:
            try:
                brut = (await bizhawk.read(
                    ctx.bizhawk_ctx, [(e.adresse, e.taille, DOMAINE)]
                ))[0]
                actuel = int.from_bytes(brut, "little")
                nouveau = e.valeur(actuel)
                if nouveau == actuel:
                    continue
                await bizhawk.write(
                    ctx.bizhawk_ctx,
                    [(e.adresse, list(nouveau.to_bytes(e.taille, "little")), DOMAINE)],
                )
            except bizhawk.RequestFailedError:
                return False
        return True

    async def livrer_capacites(self, ctx: "BizHawkClientContext") -> None:
        """Lever les bits 2xxx que les items recus impliquent.

        Sans index et sans etat local : le bit ne redescend jamais, donc
        l'etat vise se recalcule a chaque passage. Rejouer est sans effet.
        """
        recues: Dict[str, int] = {}
        for item in ctx.items_received:
            nom = NOM_PAR_ID.get(item.item)
            if nom in SEUILS:
                recues[nom] = recues.get(nom, 0) + 1

        ecritures: List[Ecriture] = []
        for nom, compte in recues.items():
            if compte >= SEUILS[nom]:
                ecritures.extend(livraison_de_lot(nom, ITEM_DELIVERY))

        # Les capacites, l'autre moitie sans index. Elles sont posees ou
        # RETIREES selon ce que le serveur a envoye : sans patch de ROM,
        # le jeu octroie le marteau au moment prevu, et c'est ici qu'il
        # est repris. Retrait Verifie en jeu le 7 aout 2026.
        if self.melange_capacites:
            noms_recus = {
                NOM_PAR_ID.get(item.item) for item in ctx.items_received
            }
            ecritures.extend(ecritures_capacites(
                {n for n in noms_recus if n in VARIABLE_DE_CAPACITE},
                ITEM_DELIVERY,
                VARIABLE_DE_CAPACITE,
            ))

        if ecritures:
            await self.appliquer(ctx, ecritures)

    async def livrer_compteurs(self, ctx: "BizHawkClientContext") -> None:
        """Livrer les items a compteur qui n'ont pas encore ete livres.

        L'index est cote serveur. Il n'avance que si l'ecriture a
        reellement eu lieu, donc une lecture BizHawk qui echoue fait
        retenter au passage suivant au lieu de perdre l'item.
        """
        if not self.cle_index:
            return
        index = max(ctx.stored_data.get(self.cle_index) or 0, self.index_local)
        if index >= len(ctx.items_received):
            return

        livres = 0
        for item in ctx.items_received[index:]:
            nom = NOM_PAR_ID.get(item.item)
            if nom is None:
                # Item d'un autre monde recu par erreur, ou pool modifie
                # entre la seed et le client. On ne devine pas.
                break
            ecriture = livraison_de(nom, ITEM_DELIVERY)
            if ecriture is not None and not await self.appliquer(ctx, [ecriture]):
                break
            # Une piece d'attaque n'a pas d'ecriture propre : c'est le lot
            # complet qui compte, et livrer_capacites s'en charge.
            livres += 1

        if livres:
            self.index_local = index + livres
            await ctx.send_msgs([{
                "cmd": "Set",
                "key": self.cle_index,
                "default": 0,
                "want_reply": True,
                "operations": [{"operation": "replace", "value": index + livres}],
            }])
