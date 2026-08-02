# Journal du projet APWorld BIS

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
