"""APWorld Archipelago pour Mario & Luigi : Voyage au Centre de Bowser.

Ce qui est vrai ici et le restera :
  - 728 locations : 647 tresors de Treasure/TreasureInfo.dat et 81 blocs
    de pieces d'attaque
  - l'identifiant d'une location est BASE_ID + le rang de son bit dans le
    tableau Exxx a 020560C8, quelle que soit la famille
  - la ROM n'est pas patchee. Tout passe par la memoire, en lecture pour
    les checks et en ecriture pour les items

Ce qui est provisoire, et pourquoi :
  - la logique gate les regions sur neuf capacites, mais l'ORDRE des
    zones vient d'un guide, pas d'une mesure. `data/ordre_zones.csv`
    porte la confiance ligne par ligne et six rangs sur seize sont
    marques faibles. Une seed est jouable, elle n'est pas garantie
  - le prerequis d'un tresor particulier reste inconnu : la logique est
    au grain de la zone, jamais du bloc
"""
from collections import Counter
from typing import Any, Dict

from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld, World

from .client import MLBISClient  # noqa: F401  enregistre le client BizHawk
from .data import LOCATIONS, VANILLA_ITEMS
from .items import (
    MLBISItem,
    NOMS_CAPACITES,
    VICTORY,
    classification,
    item_name_to_id,
)
from .locations import GAME_NAME, VANILLA_PLACEMENT, location_name_to_id
from .options import MLBISOptions
from .regions import FIN, create_regions


class MLBISWeb(WebWorld):
    theme = "grass"
    # Les deux documents exiges par docs/adding games.md:104-105 d'un
    # monde fusionne : une fiche de jeu nommee {langue}_{jeu}.md et un
    # guide d'installation. Le second doit etre declare ici, sinon il
    # n'apparait pas sur le site.
    tutorials = [Tutorial(
        tutorial_name="Setup Guide",
        description="A guide to setting up Mario & Luigi: Bowser's Inside Story for Archipelago.",
        language="English",
        file_name="setup_en.md",
        link="setup/en",
        authors=["Sussuly"],
    )]


class MLBISWorld(World):
    """
    Mario et Luigi explorent le corps de Bowser pendant que Bowser
    lui-meme arpente le royaume. Deux equipes, deux inventaires, une
    seule aventure.
    """

    game = GAME_NAME
    web = MLBISWeb()
    options_dataclass = MLBISOptions
    options: MLBISOptions

    item_name_to_id = item_name_to_id
    location_name_to_id = location_name_to_id

    def create_regions(self) -> None:
        create_regions(self)

    def create_item(self, name: str) -> MLBISItem:
        return MLBISItem(
            name, classification(name), item_name_to_id[name], self.player
        )

    def create_items(self) -> None:
        # Un item par location, celui qui s'y trouve dans le jeu d'origine :
        # le contenu du tresor, ou une piece de l'attaque du lot. Le compte
        # tombe juste par construction, les deux listes sortent du meme
        # tableau.
        pool = [VANILLA_PLACEMENT[nom] for _, nom, _, _ in LOCATIONS]

        if self.options.shuffle_abilities:
            # Les capacites s'ajoutent au pool, donc autant d'items
            # d'origine doivent en sortir : Archipelago exige un item par
            # location. Ce sont les pieces d'or de plus petite valeur qui
            # partent, l'item dont la perte se remarque le moins.
            #
            # Le tri est deterministe et ne depend pas de la seed : deux
            # generations de la meme YAML doivent donner le meme pool.
            sortants = sorted(
                (i for i, nom in enumerate(pool) if nom.endswith(" Coins")),
                key=lambda i: (int(pool[i].split(" ", 1)[0]), i),
            )[:len(NOMS_CAPACITES)]
            if len(sortants) < len(NOMS_CAPACITES):
                raise Exception(
                    f"pas assez d'items filler a retirer : {len(sortants)} "
                    f"pour {len(NOMS_CAPACITES)} capacites"
                )
            for i, nom in zip(sortants, sorted(NOMS_CAPACITES)):
                pool[i] = nom

        variete = int(self.options.filler_variety)
        if variete:
            # Le sac d'origine est desequilibre parce que le jeu l'est :
            # 197 emplacements de haricot, donc 197 haricots sur 728
            # items, dont 109 Heart Bean. Un item sur quatre recu en est
            # un. On redistribue une part des exemplaires dupliques.
            #
            # Deux garde-fous. Le tirage passe par self.random, donc deux
            # generations de la meme YAML donnent le meme sac. Et un nom
            # n'est jamais reduit a zero : un item qui disparaitrait du
            # pool disparaitrait aussi des seeds ou quelqu'un l'attend.
            compte = Counter(pool)
            candidats = [i for i, nom in enumerate(pool)
                         if nom not in NOMS_CAPACITES and compte[nom] > 1]
            self.random.shuffle(candidats)
            noms_filler = sorted(n for n in VANILLA_ITEMS if n not in NOMS_CAPACITES)
            for i in candidats[:len(candidats) * variete // 100]:
                ancien = pool[i]
                if compte[ancien] <= 1:
                    continue
                nouveau = self.random.choice(noms_filler)
                compte[ancien] -= 1
                compte[nouveau] += 1
                pool[i] = nouveau

        for nom in pool:
            self.multiworld.itempool.append(self.create_item(nom))

    def set_rules(self) -> None:
        self.multiworld.completion_condition[self.player] = (
            lambda state: state.has(VICTORY, self.player)
        )

    def fill_slot_data(self) -> Dict[str, Any]:
        # Le client doit savoir si les capacites sont melangees : sinon
        # il abaisserait des bits que le jeu vient d'octroyer et que
        # personne ne rendrait. Absent, le client suppose non melange.
        return {
            "shuffle_abilities": int(bool(self.options.shuffle_abilities)),
            # 1 = le joueur declare la fin lui-meme avec /bis_goal. Le
            # client ne doit alors rien conclure tout seul.
            "manual_goal": int(self.options.goal == 1),
        }
