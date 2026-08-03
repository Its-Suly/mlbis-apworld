# Journal du projet APWorld BIS

## 4 août 2026, un workflow trouve une erreur dans notre propre travail

Deux chantiers de bureau lancés en parallèle pendant que l'utilisateur
jouait : l'écart entre 127 compteurs d'équipement et 140 noms extraits,
et les flags des trésors hors `TreasureInfo.dat`. Quatre agents
chercheurs, chaque affirmation ensuite confiée à un agent chargé de la
démolir plutôt que de la confirmer. 29 agents, 18 affirmations
survivantes, 6 réfutées.

Le résultat le plus utile n'était pas dans la question posée.

### Nos deux CSV publiés étaient faux

`tools/extract_names.py` faisait `noms[::pas]` et supposait que
l'identifiant d'un objet valait sa position dans la table de texte
divisée par le pas des triplets. Faux. L'identifiant indexe une table
d'enregistrements de l'**arm9 décompressé**, et c'est cet enregistrement
qui porte le numéro de chaîne.

Vérifié moi-même avant d'agir, dans le code puis sur la ROM, parce que le
rapport contredisait une affirmation que j'avais faite la veille :

- `treasure.py:137-141` — `item_id = item & 0xFFF`, `seek(pointeur -
  0x2004000)`, `seek(item_id * [24,24,16,32][type-1])`, `string_id = u16`
- `main.py:1169` — table de pointeurs à `0x000145C0` pour la base NA
- `treasure.py:162` — le pluriel est `string_id + 1`, donc la table de
  texte s'indexe bien par `string_id`

Dégâts : **396 noms sur 685** faux dans `locations_bis.csv`, **129 sur
129** pour les équipements. Ce qui n'a pas bougé : aucun identifiant,
aucun type, aucun montant, aucune coordonnée. Le défaut vivait dans la
seule colonne `nom_item`.

### Ce qui rendait l'erreur invisible

Le 2 août, on avait écrit que les 26 consommables correspondaient
exactement aux 26 compteurs de la sauvegarde, « ce qui confirme les deux
lectures l'une par l'autre ». Le compte était juste. L'ordre ne l'était
pas. **Un décompte qui tombe juste ne valide pas la bijection qui va
avec**, et c'est exactement le genre de faux positif que la règle du
projet sur les sources fichier-et-ligne existe pour éviter.

Corollaire personnel : j'ai écrit hier que l'inventaire du `run13`
contenait « 3 Champignons et 1 Haricot Cœur ». C'était `1-Up Mushroom`.
Le contrôle restait valide, l'étiquette non.

Corroboration de la correction, non cherchée : les 26 consommables se
rangent maintenant par familles — Champignons 0 à 3, Pilons 4 à 6, Noix
7 à 10, Sirops 11 à 14, 1-Up 16 et 17, Haricots 20 à 22. L'ancienne
lecture les éparpillait. Et l'équipement d'identifiant 0 est `No gear`,
l'emplacement vide, ce qui explique d'un coup le décalage de 1 sur les
129 équipements.

### Sur la méthode du workflow

Le passage adversarial a aussi produit une réfutation **fausse** : un
agent a « corrigé » un nom d'item en s'appuyant sur `noms_items.csv`,
c'est-à-dire sur le fichier que la même passe venait de prouver faux. La
relecture ROM a donné raison à l'énoncé d'origine. Un vérificateur qui
s'appuie sur une source déjà disqualifiée ne vérifie rien.

Trois comptes de Cheatoglobin ont servi de corroboration externe,
`constants.py` lignes 85, 114 et 264 : `ITEM_DATA` 26, `GEAR_DATA` 129,
`BADGE_NAMES` 8. Aucun code recopié, seulement des faits sur la ROM.

## 27 juillet 2026, installation de l'environnement

Exécution des phases 2 à 7 du plan `installation-apworld-bis.md`, en une
seule passe à la demande de l'utilisateur. Phase 1 déjà faite, phase 8
(dépôt distant GitHub) volontairement non exécutée.

### Outils

- Python 3.13.14 installé via `winget install --id Python.Python.3.13`.
  `py -3.13 --version` répond `Python 3.13.14`, pip 26.1.2.
  Python 3.12.10 reste installé et reste le défaut de `py`, d'où
  l'usage systématique de `py -3.13`.
- Git déjà présent en 2.45.2.windows.1. `winget install --id Git.Git`
  a tenté une mise à niveau vers 2.55.0.3, refusée faute d'élévation
  admin dans une session non interactive. Sans conséquence, aucune
  contrainte du projet ne porte sur la version de Git.
- Microsoft Visual C++ Redistributable x64 mis à jour en 14.51.36247.0,
  prérequis de BizHawk 2.10.

### Dépôt local

Piège rencontré : `C:\Users\sulyv` est lui-même un dépôt Git, donc
avant `git init` le dossier de travail appartenait à un dépôt couvrant
tout le profil utilisateur. Vérifié avant d'agir que ce dépôt parent ne
suivait aucun fichier sous `Documents\Projet BIS` et aucun `.nds` ni
`.7z` nulle part. Le `git init` local crée un dépôt imbriqué qui
masque le parent pour toute commande lancée depuis le projet.

Ordre respecté : `.gitignore` écrit avant tout `git add`. Contrôle
explicite avec `git check-ignore -v`, qui rattache le `.nds` à la règle
`.gitignore:2` (`*.nds`) et le `.7z` à `.gitignore:3` (`*.7z`).

Commit initial `f7b9688`, 3 fichiers, dépôt de 8,58 KiB.

Note : le motif `4171*/` du `.gitignore` vise un sous-dossier de ROM,
alors que le `.nds` et le `.7z` sont en réalité à la racine. Ce sont
`*.nds` et `*.7z` qui font le travail. Le motif est inoffensif mais ne
protège rien aujourd'hui.

### Dépôts tiers

Clonés dans `vendor/` : Archipelago (version 0.6.8), Randoglobin,
BIS-docs, mnllib.py. `mnllib.py` utilise git-lfs, environ 25 Mo
filtrés au clone.

### BizHawk

`BizHawk-2.10-win-x64.zip` récupéré depuis le tag `2.10` de
TASEmulators/BizHawk, pas la dernière version. Extrait dans
`bizhawk-2.10`. `EmuHawk.exe` porte `FileVersion 2.10.0.0` et
`ProductVersion 2.10+dd232820`. Émulateur non lancé, sa configuration
reste manuelle.

### Environnement Python d'Archipelago

Venv créé dans `vendor\Archipelago\venv` avec `py -3.13 -m venv venv`.
`ModuleUpdate.py` lancé avec `-y` pour éviter les invites, l'option
existe dans le script (lignes 160 à 168). Deuxième exécution
silencieuse, donc toutes les dépendances sont satisfaites.

Le script d'activation `Activate.ps1` n'a pas été utilisé, les
commandes passent directement par `venv\Scripts\python.exe`. Cela
évite de toucher à la politique d'exécution PowerShell de la machine.

`Launcher.py` non lancé : c'est une fenêtre graphique, pas vérifiable
depuis une session non interactive. Remplacé par un import de `Utils`
dans le venv, qui répond `Version(major=0, minor=6, build=8)`.

## 2 août 2026, raccourci de reprise sur le bureau

Créé `C:\Users\sulyv\Desktop\Claude Code - Projet BIS.lnk`, qui lance
`C:\Users\sulyv\.local\bin\claude.exe` (2.1.220.0) avec le répertoire de
travail `Documents\Projet BIS` et le prompt initial
`"Où nous étions nous arrêté ?"` passé en argument positionnel.

Le prompt vit dans le champ Arguments du `.lnk`, stocké en UTF-16, donc
les accents survivent sans dépendre de la codepage d'un `.cmd`
intermédiaire. Relu après création, codepoints 249, 233 et 234 intacts.
Pas de script intermédiaire à maintenir.

Le raccourci est sur le bureau, hors du dépôt : rien à committer.

## 2 août 2026, dépouillement de Cheatoglobin et Randoglobin

Cheatoglobin cloné dans `vendor/`. Sa lecture donne d'un coup toute la
structure du fichier de sauvegarde, checksum et copie de secours
compris. Reporté dans `CLAUDE.md`.

Piste suivie ensuite : `grep -rn "block"` dans Randoglobin, qui tombe
sur `mnlscript_skips.py:480`, `block_var = 0xE701 + i`. Fausse joie
partielle : c'est une réécriture custom d'une salle à énigme par
Randoglobin, pas le mécanisme générique du jeu. En revanche la ligne
535 montre qu'un acteur porte un champ `(variable << 16) + subroutine`,
ce qui est bien un mécanisme du moteur.

`EObjSave/EObjSave.dat` a l'air d'être de l'état de sauvegarde à cause
de son nom. Ce n'est que des palettes (`palette.py` 743 à 778). Noté
comme écarté dans `CLAUDE.md` pour ne pas y revenir.

Le vrai gain est `Treasure/TreasureInfo.dat`, table d'entrées de
12 octets qui ressemble beaucoup à la liste des `location` d'un futur
APWorld.

`CLAUDE.md` atteint 232 lignes, au-dessus du seuil de 220 qu'il se fixe
lui-même. À dégraisser à la prochaine occasion.

## 2 août 2026, dump de la table des trésors

Feu vert donné pour ouvrir la ROM en lecture. Rien n'a été écrit
dedans : `ndspy` charge en mémoire, aucun `saveToFile`.

Premier réflexe avant de lire quoi que ce soit : rehasher le `.nds`. Le
SHA-256 correspond exactement à celui figé dans `CLAUDE.md`, malgré le
`(M3)` du nom de fichier qui laissait planer un doute sur une release
multilingue modifiée. `idCode` `CLJE`, nom interne `MARIO&LUIGI3`.

Venv d'outillage créé à la racine dans `venv/`, déjà couvert par le
`.gitignore` existant. Seule dépendance : `ndspy`. Volontairement séparé
du venv d'Archipelago pour ne pas polluer ce dernier.

Deux scripts écrits, gardés dans `tools/` parce qu'ils sont
reproductibles et qu'on y reviendra : `dump_treasure.py` et
`analyse_treasure.py`.

Résultat : 647 entrées exploitables. Surtout, les 8 octets que
Randoglobin ignore ne sont pas du remplissage. Les octets 4-5 portent un
identifiant de 0 à 757, unique partout sauf sur les entrées de bourrage.
Les six derniers ressemblent à des coordonnées. C'est ce champ qui
donne un sens au test de diff de sauvegarde : on ne cherche plus « un
octet qui change », on cherche un bit à un rang prévisible.

Dégraissage de `CLAUDE.md` fait dans la foulée, en deux temps parce que
le premier essai a fini à 248 lignes, soit pire qu'avant : les acquis
ajoutés pesaient plus que la section retirée. Détail des formats sorti
dans `formats-bis.md`, contraintes d'empaquetage dans
`empaquetage-apworld.md`. `CLAUDE.md` retombe à 195 lignes.

## 2 août 2026, l'APWorld Superstar Saga était déjà sur le disque

Question de l'utilisateur : puisqu'un Archipelago de Superstar Saga
existe, est-ce qu'il ne servirait pas de modèle ? Réponse : oui, et
mieux que ça. `worlds/mlss` est livré **dans le cœur d'Archipelago**,
donc il dormait dans `vendor/` depuis le clone du 27 juillet. Personne
n'avait pensé à regarder la liste des mondes fournis.

Leçon de méthode à retenir : avant de chercher une source dehors,
inventorier ce qui a déjà été cloné.

Le monde fait 10 200 lignes et déclare 634 locations, contre 647 trésors
côté BIS. Même échelle, donc la comparaison tient de bout en bout.

Corroboration directe de l'hypothèse du jour : MLSS lit 59 octets de
flags et les parcourt bit à bit, un bit par trésor, indexé par un
identifiant séquentiel. C'est le motif supposé pour BIS. Attention
toutefois, MLSS lit la RAM de travail et pas le `.sav`, la corroboration
porte sur le motif et pas sur l'emplacement.

Détail noté dans `reference-mlss.md` plutôt que dans `CLAUDE.md`, qui
n'en garde qu'une ligne en tête de la liste des sources.

## 2 août 2026, la table des locations est décodée

Le test de diff attend l'utilisateur devant BizHawk, donc travail sur ce
qui ne dépend de personne : transformer les 647 trésors en table
exploitable.

Regroupement en salles par le bit `is_last_entry_in_room` : **272
salles**, dont 269 contiennent au moins un trésor, entre 1 et 10 chacune,
2,4 en moyenne.

Décodage du champ `item` : `item >> 12` donne le type d'après
`set_item_prices` (`treasure.py` 290 à 304), et les valeurs au-dessus de
`0xEFFF` sont des pièces dont le montant vaut
`[1,5,10,50,100][quantity] * max_hits` d'après `to_script_command`
(`data_classes.py` 83 à 87). Résultat : 365 consommables, 225 lots de
pièces, 57 équipements.

Extraction des noms : deux tâtonnements avant d'y arriver, notés parce
qu'ils coûteraient du temps à quelqu'un qui recommencerait.

1. `text_tables` ne contient pas que des `TextTable`, il mélange avec des
   `bytes` bruts selon l'index. Toute boucle naïve plante sur `.entries`.
2. L'anglais n'est pas la table 1 mais la **table 2**. La valeur de
   langue 1 de `constants.py` de Randoglobin n'est pas l'index de la
   table. Vérifié en comparant : table 2 `Mushroom`, table 3
   `Champignon`, table 6 `Champiñón`.

Le pas entre deux objets diffère par table, 1 pour les objets d'attaque
et 3 pour les autres à cause des triplets singulier / pluriel / `Full!`.
Recoupement satisfaisant : les 26 consommables trouvés correspondent
exactement aux 26 compteurs d'objets de la sauvegarde relevés chez
Cheatoglobin. Les deux lectures se confirment l'une l'autre.

Les 32 zones de `mfset_EMesPlace` se séparent d'elles-mêmes en deux
mondes, dehors puis dans Bowser, ce qui donne le découpage en `region`
sans avoir à l'inventer.

Trois CSV dans `data/`, trois scripts dans `tools/`. Tout est
régénérable depuis la ROM, rien n'est saisi à la main.

## 3 août 2026, le champ de bits des trésors est localisé

Séance de mesure avec l'utilisateur devant BizHawk. Trois dumps de
`Main RAM` : avant, après un premier bloc `?`, après un second de la
même salle.

Deux bugs dans mon script Lua au premier essai, tous les deux à noter :

1. `memory.getmemorydomainlist()` est indexée **à partir de 0** sur le
   cœur NDS, alors que les tableaux d'octets de `read_bytes_as_array`
   sont indexés à partir de 1. Ma boucle `for i = 1, #liste` sautait
   `Main RAM` sans rien signaler, et sortait une liste de 12 domaines
   parfaitement plausible mais amputée du seul qui comptait.
2. Ma logique de repli se verrouillait sur le premier domaine au lieu de
   garder le plus gros. Sans le premier bug elle n'aurait jamais servi,
   mais elle était fausse.

L'erreur qui aurait pu coûter cher est la première : elle produit un
résultat crédible. Sans le réflexe de se demander où était passée la RAM
principale d'une console qui en a 4 Mo, on partait sur `Shared WRAM`.

Bonne surprise en cours de route : le domaine `SRAM` fait 8192 octets,
et les huit premiers octets du dump sont `MLRPG3`. C'est le fichier de
sauvegarde accessible en direct, sans passer par le disque.

L'analyse par motifs a d'abord échoué : 3419 octets changés sur le
premier diff, 25 639 bits candidats sur le second. Chercher « un bit qui
bouge » ne discrimine rien dans 4 Mo de RAM.

Ce qui a marché : arrêter de chercher et **prédire**. Si le champ existe
à une base `A` indexée par l'identifiant du trésor, alors le bit est à
`A * 8 + id`. En croisant avec les paires de trésors partageant une
salle, plus la contrainte d'alignement sur l'octet, les 19 415 « bases
candidates » se sont révélées pointer toutes vers un seul et même octet.

Résultat : `0x05610C` passe de `0x00` à `0x01` puis `0x03`. Un seul
octet modifié dans 410 octets de zéros continus. Bits rangés LSB en
premier.

L'utilisateur ayant rapporté 1 pièce puis 5 pièces, une seule paire de
`locations_bis.csv` satisfait les trois contraintes, d'où la base
`0x0560C8`. Test de falsification proposé dans la foulée, avec
prédiction du contenu des deux blocs restants avant qu'ils soient
frappés.

## 3 août 2026, la prédiction tombe juste

`run04` et `run05` confirment sur toute la ligne : `0x00`, `0x01`,
`0x03`, `0x0B`, `0x0F`.

Le hasard heureux de la séance : l'utilisateur a frappé les deux derniers
blocs **dans l'ordre inverse** de ma prédiction. Le bit 3 s'allume donc
avant le bit 2. C'est ce qui transforme une cohérence en preuve, parce
que ça exclut l'explication concurrente d'un compteur qui remplirait les
bits au fil des ramassages. Les bits suivent la table, pas le joueur.

Une prédiction qui se vérifie dans le désordre vaut mieux que trois qui
se vérifient dans l'ordre.

Deuxième acquis, offert par une remarque de l'utilisateur plutôt que par
une mesure : le bloc de l'identifiant 546 redonne une pièce à chaque
saut dans une fenêtre de quelques secondes. Ça valide le décodage de
`max_hits` fait le matin même, `quantity = 0` et `max_hits = 10` se
lisant bien « 1 pièce, 10 fois ». Personne n'avait pensé à vérifier ce
point, il est tombé tout seul.

Nouvelle question ouverte dans la foulée, qui n'existait pas avant :
sur un bloc multi-coups, le flag tombe-t-il au premier coup ou à
l'épuisement ? Ça décide du moment où une `location` sera validée.

## 3 août 2026, le manuel de 8y8x met un nom sur notre adresse

Source apportée par l'utilisateur : `inf.gg/mlbis/manual`, par yx (8y8x),
l'auteur de `mlbis-dumper`. En CC0, donc réutilisable sans contrainte,
contrairement à Randoglobin. Vérifiée à la source avant d'être citée, pas
seulement reprise de l'extrait fourni : tous les chiffres correspondent.

Le manuel note « No AI used 💜 ». Aucune obligation n'en découle, la CC0
n'en impose aucune, mais ça vaut d'être su avant d'aller discuter avec
cette communauté.

### Ce que le manuel corrige

`020560C8` n'est pas une structure de trésors. C'est le tableau de bits
global des variables de script `Exxx`, 4096 bits, `0x200` octets. Nos
trésors n'en occupent que les 95 premiers octets. Nous décrivions donc
la portion utile comme si c'était la structure.

La formule passe d'extrapolée à vérifiée par une source externe. Deux
autres acquis tombent en même temps : les `0x2xxx` sont bien 64 bits, et
le tableau vit dans le BSS de l'ARM9, donc à adresse fixe. Ce dernier
point retire une inquiétude qu'on n'avait pas encore formulée, celle de
voir l'adresse bouger selon la salle chargée.

Le BSS écrase l'image d'origine du code ITCM et DTCM. C'est l'explication
des 410 octets de zéros continus du 3 août au matin, qui n'avaient jusque
là aucune raison d'être là.

### Contradiction relevée, non tranchée

`Exxx` est déclaré à 4096 éléments, soit `0x200` octets, mais le manuel
dit aussi que `Exxx` et `Fxxx` forment une plage continue indexée par
`id & 0x1fff`, ce qui produit des index jusqu'à 8191. Les index au-delà
de 4095 tomberaient dans le tableau `6xxx`. Sans effet sur les trésors,
qui s'arrêtent à 757, mais consigné plutôt qu'arbitré.

### Deux erreurs de ma part

1. Écrit dans `formats-bis.md` que les variables `0xEBxx` de Randoglobin
   dépassaient l'index 3071 et butaient sur cette contradiction. Faux :
   `0xEBFF & 0x1fff` vaut 3071, elles tiennent toutes dans le tableau.
   Corrigé dans la foulée
2. Lu à l'œil la position des octets non nuls dans une sortie hexa de
   271 octets, et annoncé `+0x14C` et `+0x152`. C'était `+0x10A`,
   `+0x10B` et `+0x152`. Recompté par script. Ne pas compter des offsets
   à l'œil dans un pavé hexadécimal, même court

### Un acquis offert par la seconde erreur

En recomptant proprement, le tableau ne portait que quatre octets non
nuls sur `0x200`. Les trois qui ne sont pas les nôtres allument les index
2133 à 2139 et 2707, soit `0xE855` à `0xE85B` et `0xEA93` sous H1. Ce
sont exactement des plages relevées dans Randoglobin, `0xEAxx` étant la
plus fréquente de toutes.

Autrement dit, le partage supposé du tableau entre trésors en bas et
scripts d'événements en haut s'observe directement dans le dump. Personne
ne l'avait cherché, il était dans les données depuis le matin. On n'avait
regardé que 95 octets sur 512.

### H2 n'est pas testable avec les dumps existants

`tools/compare_block.py` écrit pour trancher la sérialisation dans la
sauvegarde. Premier passage : « différent », premier écart à `+0x044`,
4 octets sur 512. Conclusion tentante et fausse.

Vérification faite, **les deux slots sont vides**, 2 octets non nuls
chacun sur `0x5F4`. Aucune partie n'a jamais été sauvegardée. La fenêtre
comparée est nulle parce qu'il n'y a rien dedans, pas parce que H2 est
fausse. Le script a été repris pour détecter ce cas et refuser de
conclure, plutôt que de rapporter un écart trompeur.

Un outil de mesure qui ne sait pas dire « je ne peux rien conclure » est
un piège à retardement. Celui-là le dit maintenant, et propose la manip
qui débloquerait la question.

### Les identifiants ne suivent pas la géographie

Analyse de bureau demandée avant de choisir les cibles des prochains
tests, `tools/analyse_geographie.py`. Réponse nette : toute plage de 64
identifiants se disperse sur toute la carte.

Le sauvetage est local. 184 salles sur 269 ont des identifiants contigus,
et 603 des 646 écarts consécutifs valent 1. Une salle donne donc
plusieurs identifiants consécutifs sans se déplacer, ce qui explique
après coup pourquoi la salle 258 avait si bien marché. Le facteur d'ordre
est le type de trésor, en gros : la plage 0 à 63 est à 89 % des blocs `?`.

Les 85 salles éclatées, celles qui portent deux paquets d'identifiants
éloignés, deviennent les meilleures cibles de falsification : elles
allument des bits non adjacents sans quitter la pièce.

### Le flag tombe à la première pièce

Séance de mesure enchaînée dans la foulée, sur le bloc 546, celui qui
donne dix pièces une par une. Cinq dumps, `run06` à `run10`.

Réponse : le bit monte **dès la première pièce**, et plus rien ne bouge
ensuite, ni à l'avant-dernière ni à l'épuisement. Une `location` sera
donc validée au premier coup. C'est le cas simple, celui qui évite au
client d'avoir à gérer un état partiel.

Deux choses valent d'être notées sur la méthode.

La première est que l'utilisateur a pris trois dumps là où j'en avais
demandé un, en découpant lui-même la fenêtre du bloc : première pièce
prise, avant-dernière, épuisement. Découpage meilleur que le mien, qui
n'aurait pas distingué « à la fermeture » de « à l'épuisement ».

La seconde est un acquis tombé du `run07`, pris en pause juste après la
frappe : le bit y est encore à zéro. Le flag ne suit donc pas le coup
mais l'attribution de l'objet, quelques frames plus tard. Sans effet sur
un client qui interroge en boucle, mais l'atomicité aurait été une
supposition raisonnable et fausse.

Point faible du protocole, à assumer : rien ne contrôle
automatiquement que le coup a porté. On ne connaît pas encore l'adresse
du compteur de pièces en `Main RAM`, seulement celle dans la sauvegarde,
qui ne bouge pas en direct. Un saut manqué aurait produit la même sortie
qu'un flag qui ne monte pas. Ici la suite des dumps lève le doute, le bit
finissant par monter, mais il faudra cette adresse tôt ou tard.

### La communauté répond, et H2 tombe juste

Message posté sur le Discord MnL-Modding avec une liste de questions.
Deux réponses le soir même, de yx (8y8x), l'auteur du manuel, et de Marc
(ThePurpleAnon).

Le gros morceau est une capture d'écran de Ghidra montrant la fonction de
sauvegarde, `FUN_overlay_d_129__0206f1f4` cas 5 : cinq `memCopy32unk` qui
écrivent `2xxx`, `Dxxx`, `Exxx`, `6xxx` et la plage anonyme, dans l'ordre
et aux tailles du bloc en RAM.

En calant sur l'ancre de Cheatoglobin, les cinq offsets se traduisent en
`slot + 0x0124`, `0x012C`, `0x01B4`, `0x03B4`, `0x044C`. **C'est
exactement ce que H2 prédisait, offset par offset.** Une prédiction posée
le matin sur un raisonnement d'ordre et de tailles, confirmée le soir par
du code décompilé qu'on n'avait pas.

Marc donne par ailleurs le découpage de `Exxx` : trésors à partir de
`0xE000`, ennemis de `0xE400`, histoire de `0xE700`. Ça valide H1, la
variable d'un trésor étant `0xE000 + identifiant`, et ça précise H3.

Détail qui fait plaisir : les trois octets non nuls repérés dans `run05`
en fin d'après-midi, aux index 2133 à 2139 et 2707, tombent tous au-delà
de `0xE700`, donc côté histoire. L'observation a précédé l'explication de
quelques heures.

Troisième acquis, moins agréable mais utile : les trésors hors
`TreasureInfo.dat` sont des flags de cinématique, indistinguables par
leur plage. Il n'y a pas de table à dumper, il faudra lire les scripts
avec `mnlscript`. C'est le seul chantier restant qui demande d'entrer
dans le langage de script.

### Une affirmation publiée, mise en doute puis confirmée

Marc conseille de lire le dernier commit de Randoglobin plutôt que la
release, et se dit sûr à 90 % que le dernier commit lit les 6 premiers
octets d'une entrée de trésor. Or nous publions dans le README que les
octets 4-5 ne sont jamais lus.

Vérifié plutôt que supposé : notre clone est déjà au dernier commit de
`main`, `b40481cb`, zéro commit de retard, et `from_treasure_info` y fait
`struct.unpack('<HH', data)`, soit 4 octets. L'affirmation tient. Il
visait peut-être une des branches `v0.1` ou `v0.2`.

Leçon générale : une remarque d'un contributeur mieux informé que nous
mérite d'être vérifiée, pas gobée ni écartée. Elle coûtait deux commandes.

### H2 vérifiée par la mesure, et un octet qui dépasse

Sauvegarde faite en jeu dans la foulée, avec le seul trésor 546 ramassé,
puis `run11`. Les cinq tableaux sont aux cinq offsets prédits, tailles
comprises. `compare_block.py` trouve l'empreinte à `0x0208`, soit
`slot 1 + 0x01B4`.

Bonus non demandé : l'empreinte apparaît une seconde fois, à `0x09F4`.
C'est la copie de secours, `slot + 0x7EC + 0x01B4`. L'offset `0x7EC` de
Cheatoglobin se trouve confirmé sans qu'on l'ait cherché, et la copie est
identique à la principale.

Le seul écart du bloc est un octet, et il vaut mieux qu'une confirmation
de plus : à `Exxx + 0x167` la sauvegarde porte `0x80` quand la RAM est à
`0x00`, dans les six dumps `run06` à `run11`. Index 2879, variable
`0xEB3F`, plage histoire.

Autrement dit, **la sauvegarde n'est pas une copie fidèle de la RAM**.
Soit la routine écrit ce bit directement dans le tampon, soit le jeu le
lève pendant la boîte de dialogue et le rabaisse avant le dump. Non
tranché ; un dump pris pendant le dialogue départagerait.

Ce que ça change concrètement : recopier la RAM dans la sauvegarde
effacerait ce bit. Le piège est noté dans `CLAUDE.md` à côté du checksum
et de la copie de secours, parce qu'il se manifestera au même moment.

Remarque de méthode. Le script avait été écrit le matin avec une
recherche de motif « au cas où la prédiction serait fausse ». Elle n'a
pas servi à rattraper une erreur, elle a servi à trouver la copie de
secours. Une sortie prévue pour un échec a payé sur un succès.

### La première adresse vivante, après trois échecs de ma faute

Chasse au compteur de pièces, pour tenir enfin une adresse d'état de jeu
et non de sauvegarde. Trois recherches successives, toutes négatives :
image de l'inventaire cherchée dans la RAM, delta `+8` puis `+9`, crédit
unique de `+10` sur trois domaines et trois tailles.

La quatrième a marché en changeant de prise : plutôt que de filtrer sur
des valeurs absolues supposées, filtrer sur le seul fait certain, le
`+7` des trois blocs 544, 545 et 547 dont on connaissait les montants par
`locations_bis.csv`. Deux `u32` seulement montent de 7 dans les 4 Mo :
`0x056400` et son image dans le tampon de sauvegarde.

`02056400`, `u32`. La série `0, 0, 1, 1, 2, 2, 9` sur les sept dumps ne
laisse aucun doute.

Ce que la mesure révèle est plus embarrassant : le bloc 546 n'a jamais
donné 10 pièces, il en a donné 2. Le joueur part de 0 et monte à 2. Les
pièces retombent au sol et il faut les toucher.

Donc mes trois échecs cherchaient des deltas qui n'ont jamais existé.
La méthode différentielle était juste depuis le début ; c'est la
quantité, que j'avais déduite de `max_hits = 10` sans la mesurer, qui
était fausse. Une prémisse non vérifiée a coûté trois recherches, et
elle venait de moi, pas d'une source.

Le réflexe qui a débloqué : chercher un delta connu plutôt qu'une valeur
supposée. Le delta venait d'une table extraite de la ROM, pas d'une
interprétation.

À noter aussi, le format vivant n'est pas celui de la sauvegarde : même
`u32` de pièces en tête, mais la suite décalée de 2 octets. La
correspondance champ par champ reste à faire.

### La première écriture, et elle traverse toute la chaîne

Dernier risque du projet, celui qu'on repoussait depuis le début : on
savait lire, on n'avait jamais écrit. Sans écriture, un APWorld détecte
qu'une `location` est validée mais ne peut rien livrer au joueur.

Cible choisie pour sa docilité : le compteur de pièces. Ni pointeur, ni
index, ni taille, donc une valeur fausse donne un affichage faux et pas
un plantage. Et surtout, c'est le seul champ dont on sache lire une
valeur de contrôle ailleurs, dans la sauvegarde.

999 écrit à `02056400` en marchant sur le terrain, puis quelques pas,
puis sauvegarde en jeu. Résultat au `run13` : 999 en RAM, 999 dans la
sauvegarde, 999 dans la copie de secours, témoin des trésors intact à
`0x0F`, et aucun autre octet du tableau `Exxx` modifié.

Le meilleur contrôle n'est pas venu d'un dump : l'utilisateur a **vu le
compteur passer à 999 à l'écran** au moment de sauvegarder. Le jeu ne
subit pas la valeur, il l'adopte, l'affiche, la sérialise et recalcule
son checksum lui-même.

Ce qui reste à faire, et qu'il ne faut pas confondre avec ce qui est
acquis : livrer un *objet* n'est pas livrer des pièces, et les
26 compteurs d'objets de l'inventaire vivant ne sont pas cartographiés.
Le test a eu lieu sur le terrain ; écrire pendant un combat ou une
cinématique reste supposé dangereux jusqu'à preuve du contraire.

### Ultracode et auto mode rendus permanents pour le projet

Demande de l'utilisateur : que le raccourci du bureau ouvre toujours une
session en ultracode, c'est-à-dire effort `xhigh` plus orchestration de
workflows, et en auto mode.

Réglages écrits dans `.claude/settings.local.json`, qui est couvert par
le gitignore global de la machine, `~/.config/git/ignore` ligne 3, donc
rien ne part sur GitHub :

```
effortLevel              xhigh
ultracode                true
skipWorkflowUsageWarning true
permissions.defaultMode  auto
```

Les 10 règles `allow` existantes ont été conservées, pas remplacées.

Subtilité qui a demandé un détour. Le schéma décrit `ultracode` comme
*session-scoped*, fourni « typiquement via `--settings` », donc rien ne
garantit qu'il soit lu depuis un fichier de projet. Plutôt que de créer
un second fichier, le raccourci passe désormais le fichier du projet
lui-même en `--settings`, ce qui le charge aussi dans le tier `flag`,
celui que la doc désigne. Un seul fichier à maintenir, deux tiers
couverts.

Le raccourci a été modifié en **préfixant** ses arguments existants, sans
retaper la chaîne accentuée. Relecture : codepoints 249, 233, 234, 233
intacts.

Un essai d'écrire un fichier de réglages dans `~/.claude/` a été refusé
par le classifieur d'auto mode, l'écriture sortant du projet. Le refus
était justifié et la solution retenue est meilleure.

### Tenue des fichiers

`CLAUDE.md` est remonté à 219 lignes, à une du plafond. Trois lignes
seulement y ont été ajoutées, gagées par la compression de trois entrées
devenues redondantes avec `formats-bis.md`. Prochain candidat à la
sortie, noté dans le fichier lui-même : la section « Particularités du
jeu ».
