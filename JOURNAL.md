# Journal du projet APWorld BIS

## 8 août 2026, le multiworld tourne pour de vrai

Trou rappelé par l'utilisateur : la boucle avait toujours été validée en
solo. Un item venu d'un autre monde, jamais.

Testable sans deuxième humain, parce qu'Archipelago livre `apquest`, un
monde de démonstration dont le client Python contient le jeu entier. Une
seed à deux slots, l'utilisateur tenant les deux rôles.

Le tirage a bien fait les choses : six objets du Compagnon dans nos
blocs, et **le marteau, un de nos neuf items de progression, dans son
Bottom Left Chest**. Aucune des six locations concernées n'était déjà
cochée dans la sauvegarde, donc rien ne partait par accident à la
connexion.

Résultat : coffre ouvert dans APQuest, marteau arrivé dans BIS. La chaîne
complète tient, un objet trouvé dans un jeu, expédié par le serveur,
écrit dans la mémoire d'un autre. Deux clients sur le même serveur, rien
n'a bronché.

Le sens inverse était contraint par une chose apprise la veille : les six
blocs porteurs d'un objet du Compagnon sont soit dans des zones non
atteintes, soit des touffes d'herbe, et l'herbe n'existe que dans le
monde de Bowser. Aucun n'était accessible avec les frères.

Fait avec Bowser dans Dimble Wood, et le journal du serveur donne les
quatre lignes qui closent le sujet :

```
Compagnon sent Hammer to TestBIS (Bottom Left Chest)
TestBIS sent Supersyrup Jar to TestBIS (Dimble Wood - Brick 77)
TestBIS sent 100 Coins to TestBIS (Dimble Wood - Grass 70)
TestBIS sent Sword to Compagnon (Dimble Wood - Grass 598)
```

Les trois routages possibles y sont : d'un autre monde vers nous, de nous
vers nous, de nous vers un autre monde. **Le multiworld est acquis.**

Confirmation gratuite dans la deuxième ligne : `Brick 77` cassée par
**Bowser**. Les blocs brique sont bien de son côté, ce que la table
disait la veille et que personne n'avait vu faire.

### La reconnexion, quatre exigences en un test

Le joueur avait ouvert tous les coffres d'APQuest, donc plus aucun objet
à nous n'y attendait. Contretemps devenu opportunité : la console du
serveur sait créer un objet, `MultiServer.py:2400`, ce qui déclenche un
cas qu'`adding games.md` exige de supporter et qu'on n'avait jamais
provoqué, un item **sans location d'origine**.

Protocole : client fermé, `/send TestBIS Super Mushroom` côté serveur,
deux touffes coupées en jeu, puis reconnexion.

Quatre résultats d'un coup. Les checks ramassés client fermé partent à la
reconnexion, `Grass 650` et `Grass 655`, exigence dure jamais vérifiée.
L'objet arrivé pendant l'absence est livré. L'objet créé par la console
est géré. Et surtout **les pièces n'ont pas bougé** : l'index côté
serveur ne rejoue rien.

Ce qui reste défectueux est un cas distinct, et il ne faut pas les
confondre : recharger un **savestate** ramène le jeu en arrière sans que
le serveur le sache. La reconnexion, elle, tient.

### Le sac était monotone, et le jeu en est la cause

Remarque du joueur : il recevait un nombre anormal de haricots. Mesure :
197 des 725 items en sont, soit 27 % du sac, dont 109 Heart Bean à eux
seuls. Ce n'est pas un défaut de livraison, c'est le jeu, qui compte 197
emplacements de haricot.

D'où l'option `filler_variety`, de 0 à 100, qui redistribue cette part
des exemplaires dupliqués sur tous les autres noms. À 80, les haricots
tombent à 7 % et l'item le plus fréquent passe de 109 exemplaires à 23.
Le sac reste à 725, aucun nom n'est réduit à zéro, et le tirage passe par
le générateur de la seed. Défaut par défaut à 0 : changer ce qu'une seed
contient se demande, ne s'impose pas.

### Les 12 pièces manquantes étaient cachées par notre propre filtre

Parti pour lire l'ARM, j'ai commencé par le moins cher des trois
chantiers, et il n'a pas demandé une ligne d'assembleur.

Jump Helmet 8 et Super Bouncer 4 étaient portées depuis trois jours comme
« absentes de `FEvent`, à mesurer en jeu ». Elles y étaient. Notre
scanner exigeait un masque à un seul bit, en supposant qu'un masque
multiple soit un octroi de cinématique. Un bloc peut simplement rendre
quatre pièces d'un coup, et il porte alors son drapeau.

Jump Helmet se lit d'un coup d'œil une fois le filtre levé : `0b00001`,
`0b11110`, `0b01111`, `0b10000`, quatre blocs, quatre drapeaux, une
partition exacte des dix pièces. Et `0xE780` et `0xE782` tombent
précisément dans les trous relevés le 5 août.

Deux filtres restaient nécessaires, tous deux appuyés sur une mesure déjà
faite : écarter les chunks 0, 1 et 2, et écarter toute entrée qui
**recouvre** des pièces déjà couvertes, ce qui élimine les cinématiques à
masque 31 de Magic Window, Spin Pipe et Mighty Meteor. Le critère n'est
pas la valeur du masque mais le recouvrement, puisqu'un vrai bloc
partitionne.

81 blocs pour 90 pièces, le monde passe à **728 locations**.

Leçon à garder : un « à mesurer en jeu » vieux de trois jours mérite
d'être rouvert avant d'aller chercher plus loin. Ce n'est pas la ROM qui
cachait la donnée, c'est une hypothèse de notre outil, écrite dans son
en-tête et jamais remise en cause.

### Un plafond qui confisquait

Trouvé en préparant le test, pas en jouant. La partie portait 1154
pièces et notre plafond vaut 999, valeur de prudence et non maximum
mesuré. Livrer 50 pièces calculait `min(1204, 999)` et aurait **retiré
155 pièces** au joueur. Corrigé en `max(actuel, min(...))`, le plafond
écrête sans confisquer, et le test le vérifie à 1154.

## 7 août 2026, le raccourci ne démarrait rien, et il l'affirmait

Reprise deux jours après la boucle complète. Première utilisation réelle
de `tools/jouer.cmd` : le client reste sur `Awaiting connection to BizHawk
before authenticating`.

### Un script écrit après le test qu'il était censé rejouer

`jouer.cmd` a été committé le 5 août à 19h22, huit minutes après le test
réussi de 19h14. Il n'avait donc jamais tourné en entier, et son message
de commit, « One desktop shortcut starts a whole instrumented play
session », affirmait précisément ce qui n'avait pas été vérifié.

La différence avec le 5 août tient en un dossier. Ce jour-là le
connecteur était ouvert à la main depuis `vendor\Archipelago\data\lua` ;
le raccourci, lui, charge `tools\session_bizhawk.lua`, qui le `dofile`
depuis ailleurs.

### Le diagnostic avant la trace, et ce que la trace ajoute

Symptôme utile : le journal des capacités écrivait normalement pendant
que le client attendait. Deux moitiés du même script Lua, une vivante,
une morte, donc l'échec était dans le chargement du connecteur et non
dans BizHawk.

Hypothèse posée avant de demander quoi que ce soit, en lisant
`connector_bizhawk_generic.lua:288-290` et surtout `socket.lua:44-47`,
qui construit le chemin de sa DLL avec `io.popen("cd")`, c'est-à-dire le
répertoire courant. Quatre `require` et une DLL, tous relatifs.

La trace demandée à l'utilisateur confirme, `module 'lua_5_3_compat' not
found`, et apprend une chose que je n'avais pas : `package.path` est
construit sur le dossier de BizHawk, plus l'entrée `.\`. C'est donc bien
le répertoire courant qui décide, et lui seul.

Ce que la trace ne dit pas, et que je n'ai pas tranché : si ce répertoire
vient du script chargé ou du processus qui lance BizHawk. Les deux
lectures expliquent l'erreur. Plutôt que de choisir au jugé, le correctif
couvre les deux, une copie dans `data\lua` et un `/D` sur le même
dossier.

### Correctif, et un garde-fou qui parle

`jouer.cmd` copie `tools\session_bizhawk.lua` dans `data\lua` à chaque
lancement et démarre BizHawk là. La source reste dans `tools`, seul
fichier suivi par git, `vendor/` étant ignoré ; recloner Archipelago ne
casse rien.

`session_bizhawk.lua` refuse maintenant de démarrer s'il n'ouvre pas un
fichier témoin en relatif, et dit quoi faire en une ligne au lieu d'une
trace NLua de quatorze. Commit `4b812d4`. **Non exercé** : la validation
viendra au prochain lancement du raccourci, et cette fois elle sera faite
avant d'écrire qu'il marche.

La session en cours a été débloquée à chaud, sans rien relancer, par un
`Ctrl+O` sur le connecteur depuis `data\lua`. La partie était déjà
chargée et le journal déjà vivant.

### Invalid Slot, réglé par deux lectures et non par des essais

Quatre tentatives de nom refusées. Deux sources ont suffi : le serveur
imprime le nom qu'il a reçu, `Test Bis`, `Test Bis2`, `TestBis`,
`TESTBIS` ; et le `slot_info` du multidata, lu en dépliant
`seeds/AP_14089154938208861744.zip`, donne `TestBIS`. La comparaison
respecte la casse.

Rien à corriger dans le projet, mais l'écart entre un nom choisi par un
script et un nom retapé à la main est un piège gratuit. À voir si une
prochaine seed ne mérite pas un nom insensible à la casse.

### Ce qui tourne au moment d'écrire

Connecteur, client, serveur et partie du 5 août, avec ses 22 items déjà
reçus rechargés depuis l'`.apsave`. La mesure de progression commence,
journal en marche.

### Une question qui a recadré toute la suite

« Ce que tu m'as demandé prend combien de temps ? » Réponse honnête :
trente heures, puisque « joue et le journal mesurera la progression »
veut dire finir le jeu. J'avais présenté une partie entière comme
l'étape suivante sans jamais poser le chiffre.

Ce que la question a débloqué : la même donnée est dans les scripts. Les
capacités sont des variables `2xxx`, `FEvent` dit qui les pose et dans
quelle salle, et `tools/pieces_attaque_fevent.py` savait déjà lire tout
ça pour les `Exxx`. Trente heures de manette contre quelques secondes de
balayage.

Le journal ne devient pas inutile pour autant, il devient gratuit : il
tourne pendant qu'on joue et sert de contre-épreuve.

### Le balayage, en deux explorations avant l'outil

Rien n'a été supposé de la forme des données. Première exploration :
quelles commandes touchent un `2xxx`. Réponse nette, une seule, `0x0008`,
avec un entier, sur 534 548 commandes. L'outil final s'arrête si une
autre apparaît, plutôt que de l'ignorer.

Deuxième exploration, sur un détail qui clochait : les premières
écritures du marteau tombaient dans les chunks 1 et 2, ce qui ne
ressemble pas à une salle. Les chunks 0, 1 et 2 posent 20, 27 et 46
variables. Des initialisations, écartées et affichées à part.

Sans ces deux détours, l'outil aurait produit un tableau où le marteau
s'obtient au chunk 1, et rien n'aurait signalé l'erreur.

`tools/capacites_fevent.py`, sortie `data/capacites_fevent.csv` :
38 variables sur 48 ont une salle d'octroi, 29 une seule. La chaîne
carte vers zone de `build_salles_zones.py` a été reprise sans son filtre
sur les trésors, parce que les salles de cinématique n'en portent aucun
et que ce sont justement celles-là qui octroient.

### Le témoin, et la discordance qui n'en était pas

`bros_attacks.csv` vient de l'overlay 123 et donne la zone du lot de
pièces de chaque attaque, sans rien savoir des scripts. Trois attaques
sur quatre tombent dans la zone de leur lot. La quatrième, Mighty Meteor,
donne Toad Town pour un lot `Clinic Pieces` : la clinique de Toadley est
dans Toad Town, ce sont deux zones nommées séparément.

C'est ce témoin qui autorise à dire que l'index de chunk `FEvent` est
l'index de carte. Le compte égal, 681 et 681, n'aurait pas suffi.

### Deux coïncidences que rien n'a arrangées

La partie jouée entre-temps a servi de contre-épreuve, et elle est
tombée juste deux fois.

Le journal note `0x202E` levé et `0x2030` retombé au même instant, après
12 trésors. Le balayage désigne un seul chunk qui fait exactement cette
paire, le 507. Au passage, `0x2030`, que mnllib ne nomme pas, est donc un
drapeau d'avant le menu étoile.

Le journal note `SHOP_UPGRADE_1` et `COUNTERATTACK_SHELL` acquis
ensemble après 22 trésors ; le balayage les pose dans les chunks 57 et
53, deux salles voisines.

Et la prédiction du 5 août sur `FIRE_BREATH_DISABLED` est confirmée par
la mesure : le bit **retombe** en jouant. C'est la seule capacité qu'il
faudra livrer en abaissant un bit.

### Ce que les guides avaient dit à moitié

Quatre divergences entre le balayage et `progression_hypothese.csv`, dont
trois s'expliquent d'un coup : le drapeau est posé dans la salle où se
trouve **Bowser**, pas dans celle où les frères combattent à l'intérieur
de lui. Sliding Haymaker au Nerve Cluster pour le guide, à Dimble Wood
pour le script. Les deux disent vrai sur des moitiés différentes.

J'avais eu tort d'écarter les guides le 5 août, j'aurais eu tort de les
prendre au mot aujourd'hui. Ils nomment le monde des frères, l'`access_rule`
a besoin de celui qui déclenche.

### Le test qui a décidé du projet, et il tenait en un bit

En préparant les capacités comme `item`, un problème est apparu qui
n'était dans aucune note : on ne patche pas la ROM, donc le jeu octroie
le marteau au moment prévu, que le serveur l'ait envoyé ou non. Mettre le
marteau dans la pool ne sert à rien s'il est donné gratuitement.

La seule parade à notre portée est que le client **abaisse** les bits non
reçus. Restait à savoir si le jeu supporte de perdre une capacité.

`tools/basculer_capacite.lua`, deux minutes de manipulation : bit `0x2001`
abaissé, le marteau disparaît de la commande de combat, bit remonté, il
revient. **Vérifié.** Tout le reste de la séance découle de cette
réponse ; si elle avait été non, la décision de faire des capacités des
items serait tombée avec elle.

### Trois hypothèses d'ordre, tombées en série

L'ordre des zones ne se lit nulle part, et il a fallu trois essais pour
en être sûr.

Le tableau des 32 noms de zones est dans un ordre qui n'est pas celui du
jeu, Peach's Castle en 1 et Dimble Wood en 2. Les index de carte se
chevauchent d'une zone à l'autre. Et les 89 fichiers de la ROM ne portent
aucune table de séquence.

Le troisième essai était le plus tentant : si les drapeaux d'histoire
étaient alloués dans l'ordre où l'histoire a été écrite, trier par numéro
de variable donnerait l'ordre. Balayage fait, résultat absurde, Airway en
premier et Cavi Cape en avant-dernier. Deux minutes pour l'écrire, deux
minutes pour le tuer, et le fichier produit a été retiré du dépôt :
`data/` ne doit contenir que ce qu'un script de `tools/` sait refaire.

Conclusion assumée : **l'ordre vient d'un guide**, pas de la ROM.
`data/ordre_zones.csv` le dit ligne par ligne, six rangs sur seize sont
marqués faibles.

### Le sens de l'erreur, choisi une fois pour toutes

Première version du générateur : pour une capacité posée dans plusieurs
zones, retenir la plus tardive. C'était l'erreur exactement à l'envers,
et le marteau l'a montré, attribué à Dimble Wood au lieu du Trash Pit.

Le raisonnement qui corrige. La règle dit qu'une zone de rang `r` exige
les capacités octroyées avant elle. Situer un octroi trop tôt **ajoute**
des exigences : le placement est plus contraint, le joueur ne l'est
jamais. Le situer trop tard en **retire**, et là un item nécessaire peut
atterrir derrière le mur qu'il ouvre. Une seule des deux erreurs bloque
une partie.

Corrigé en `min` au lieu de `max`, les neuf capacités retombent alors
exactement là où les guides les placent. Six recoupements sur les six que
les guides citent, dont Body Slam que le guide met à Blubble Lake et que
le balayage met à Tower of Yikk, la tour du lac.

Le même principe a tranché deux autres choix : Peach's Castle en fin de
chaîne bien qu'elle soit aussi le prologue, et la victoire qui exige les
neuf capacités alors que sa région n'en exige que huit.

### Ce qui tourne maintenant

Génération : six sphères de progression, le marteau seul accessible au
départ, puis Spin Jump, Vacuum et Drill Bros dans les zones qu'il ouvre.
C'est la première fois que le monde produit un vrai parcours.

Le client abaisse ce qui n'a pas été reçu, mais seulement si la seed le
dit : `fill_slot_data` porte `shuffle_abilities`, et le client suppose
**non** en son absence. Une seed d'avant aujourd'hui reste donc jouable
telle quelle, ce qui protège la partie en cours.

### Le retrait, vérifié une seconde fois et pour de bon

Seed neuve avec la logique, `AP_02053695854357871005`, jouée sur la
sauvegarde du jour. Prédiction écrite avant : 43 locations déjà cochées
partent à la connexion, le Vacuum Block est reçu parce que sa location
est déjà ramassée, les huit autres capacités sont reprises.

Observé : **le marteau a disparu, y compris dans le menu de combat.**
Le retrait ne marche donc pas seulement à la main dans un script Lua, il
marche par le client, automatiquement, sur huit capacités d'un coup.

La moitié positive, elle, n'a rien démontré : le joueur avait déjà le
vacuum par le jeu, donc rien ne distingue une pose du client d'un octroi
normal. Sans importance, la pose était acquise depuis le 5 août.

Un détail vaut mieux que la moitié ratée : le joueur a toujours son
souffle de feu. `0x2004` est justement la capacité qu'on a laissée hors
de la pool ce matin, sens inversé et salle d'octroi ambiguë. Le client
ne touche donc bien qu'aux neuf bits qu'il gère.

### Le joueur ne veut pas finir le jeu avant l'APWorld

Contrainte posée en fin de séance, et elle change la méthode : plus
question de mesurer la progression en jouant, sous peine de spoiler la
partie que l'APWorld est censé rendre intéressante.

Ce qui perd sa route de mesure : l'ordre des zones, les 12 pièces
d'attaque de Flab Zone et Energy Hold, et tout test au-delà de Dimble
Wood. Ce qui reste possible sans rien découvrir : tout test dans les
zones déjà traversées, ce qui a suffi pour celui d'aujourd'hui.

Deux pistes explorées dans la foulée. Le graphe des salles existe,
commande `0x011E` nommée par `bis_docs_commands.yml:649-652`, 1215
changements de salle et 938 arêtes, mais il ne porte que les transitions
de cinématique ; six liens inter-zones seulement en sortent, tous dans la
partie tardive de la table d'ordre, celle qui était marquée faible. Et
les 12 pièces ne sont pas dans la table des trésors : les 38 entrées
inexploitables sont toutes des touffes d'herbe vides.

Reste à chercher la table des sorties de carte, que ni Randoglobin ni
BIS-docs ne documentent.

### Deux documents, et une candidature qui n'aura pas lieu

L'utilisateur voulait savoir comment présenter le projet à Archipelago,
puis a décidé de le garder solo. Les deux documents exigés par
`adding games.md:104-105` ont été écrits quand même, parce qu'un guide
d'installation sert au projet avant de servir à une candidature. Il
contient d'ailleurs le piège du connecteur qui nous a coûté une heure ce
matin : ouvrir le script **depuis son dossier**.

En lisant leur doc, deux manques réels sont apparus, dont un dur.

### Le but du jeu, cherché puis redéfini

`adding games.md:33-34` exige que le client annonce la fin de partie. Le
nôtre ne l'a jamais fait, et la recherche du drapeau a échoué proprement.

Une seule commande `0x0195` de tout le jeu porte la transition `03`,
« final battle », au chunk 557. Belle piste, résultat négatif : les
variables `Exxx` écrites autour sont génériques, `0xE855` à `0xE85B` dans
les 681 chunks et `0xEB0E`/`0xEB0F` dans une centaine.

Plutôt que de deviner une adresse, le but a été redéfini sur ce qui se
mesure : **réunir les neuf capacités**, qui se lit dans `items_received`
sans aucune adresse mémoire, et qui est déjà la condition que la logique
impose à l'événement de fin. Rien ne peut diverger entre ce que le
placeur garantit et ce que le client observe.

C'est une limite assumée et écrite dans la doc du monde, pas un choix de
design déguisé.

### La table de révélation des cartes, fausse piste bien construite

Randoglobin nomme `0x605C` comme le déblocage des cartes de Bowser, et le
chunk 27 contient bien neuf sous-routines qui l'incrémentent de 2 à 10,
chacune avec deux autres arguments. J'ai cru tenir l'ordre des zones.

Ce qui l'a tuée : les valeurs du premier argument sont 30, 139, 134, 124,
126, 201, 165, 77, 134, toutes sous 256. Ce sont des **positions à
l'écran**, pas des numéros de carte. La traduction en zones que j'avais
produite ne voulait rien dire, et elle avait l'air parfaitement crédible,
avec Bowser Castle révélé en deuxième.

Deuxième fois de la journée qu'une hypothèse d'ordre tombe sur un détail
de format. L'ordre des zones vient toujours d'un guide.

### La suite générale d'Archipelago passe

206 tests sur onze modules, accessibilité, items, locations, identifiants,
noms, remplissage, options, manifeste. Notre monde y est inclus et rien
n'échoue. `tools/test_archipelago.py` rejoue l'ensemble, en réinstallant
la copie d'abord, parce que tester la copie de la veille pendant qu'on
modifie la source est un faux positif qui coûte cher.

### Tenue des fichiers

`MEMOIRE.md` est **exactement à 220 lignes**, le plafond. Les deux acquis
du jour y tiennent en quatre lignes parce que le détail est parti dans
`formats-bis.md`, deux sections neuves. Le prochain ajout devra sortir
quelque chose ; le meilleur candidat reste la liste des tables de
`data/`, qui se lit aussi bien en ouvrant le dossier.

## 5 août 2026, la question qui décidait de tout, et ce qu'elle a ouvert

Séance ouverte sur une reprise, cinq dumps déjà pris par l'utilisateur
avant que je dise quoi que ce soit, et fermée sur trois acquis dont deux
n'étaient pas au programme.

### Les bits survivent, et la mesure était bien posée

`run47` à `run51`, la chaîne complète : avant le saut, à la dixième
pièce, à l'annonce de l'étoile, pendant le combat, après le combat porte
ouverte. Les dix bits `0xE700` à `0xE709` restent levés partout, `0x601D`
reste à 10. Rien ne retombe.

Ce qui rendait la mesure concluante, c'est qu'elle avait été préparée la
veille : la partie avait été laissée devant le dernier bloc, à neuf
pièces. Le protocole tenait en une phrase, et l'utilisateur a pris cinq
dumps là où j'en avais demandé deux, dont celui de la discussion et celui
de l'annonce. Ce sont précisément ces deux-là qui ont isolé le déblocage.

Détail que la veille avait raté : la dixième pièce est `0xE709`. La note
parlait de neuf bits parce que neuf pièces seulement avaient été
ramassées, et j'avais écrit la plage `0xE700` à `0xE708` comme si elle
était complète. Décrire un état partiel comme un résultat, c'est la même
faute que le `max_hits` du 3 août, en plus discret.

### Le vrai gain n'était pas la réponse, mais deux bits voisins

Entre `run48` et `run49`, deux octets seulement changent dans tout le
bloc de variables, et ils ne sont pas dans `Exxx` : `0x200B` et `0x2010`
montent dans le champ `2xxx`, au moment exact où l'étoile annonce le
Green Shell.

`mnllib` les nomme, `consts.py:60` et `:65`, `BROS_ATTACKS` et
`BROS_ATTACK_GREEN_SHELL`. Randoglobin nomme le premier de son côté,
`patch.py:342`, « bros attacks block ». La mesure et deux sources qui ne
se citent pas tombent d'accord sur les deux mêmes bits.

Ce que ça ouvre dépasse largement les pièces. `2xxx` est l'énumération
`ImportantFlags` : marteau, Drill Bros, Spin Jump, badges, vacuum, les
dix Bros Attacks, les améliorations de boutique. Quarante capacités dans
huit octets à `02056038`, sauvegardés. **Livrer une capacité, c'est
lever un bit.** Le chemin d'item le plus simple du projet est apparu par
la bande, en cherchant autre chose.

### Extraire plutôt que croire

`ImportantFlags` n'est utilisé nulle part ailleurs dans mnllib. Rien ne
le teste chez eux, donc rien ne garantit qu'il soit à jour. Plutôt que
de le prendre pour argent comptant ou de l'écarter, j'ai cherché ce que
la ROM en dit.

`special.py:26` de Randoglobin décrit une table de 10 Bros Attacks dans
l'overlay 123, avec pour chacune sa variable de pièces et sa variable de
déblocage. `tools/extract_bros_attacks.py` la lit. Les dix variables de
déblocage sont exactement les dix `BROS_ATTACK_*` de mnllib, dans le même
ordre. Dix sur dix.

Le script vérifie aussi que le pointeur arm9 de la table d'objets
d'attaque vaut bien l'offset annoncé par Randoglobin. Une ligne de
recoupement qui coûte deux minutes et qui, si elle avait échoué, aurait
évité de publier une table fausse.

Sortie bonus : les noms de lots, `Trash Pieces`, `Pump Pieces`. Ils
donnent la zone d'un set, ce que les scripts ne donnent pas.

### Le balayage, et trois versions dont deux fausses

Objectif : la variable `Exxx` des 100 pièces, pas seulement des dix
mesurées. Trois tentatives.

La première groupait par salle. Résultat inutilisable, une salle de
cinématique cite des dizaines de variables sans rien ramasser.

La deuxième descendait à la sous-routine, en exigeant qu'elle touche une
variable de pièces et pose un `Exxx`. Mieux, mais encore pollué : la
cinématique de déblocage lit le compteur. J'ai resserré sur l'écriture
plutôt que la lecture, sans que ça suffise.

La troisième a marché parce que j'ai arrêté de deviner la signature et
que je suis allé la lire. Un diagnostic de dix lignes sur la salle témoin
montre la structure exacte : commande `0x0020`, `base+k |= masque`, un
seul bit par bloc, masques 1, 2, 4, 8, 16. L'indice de la pièce se calcule,
il ne se suppose pas.

Même leçon que le 4 août sous une autre forme. Quand une question porte
sur ce que fait le jeu, faire faire au jeu ; quand elle porte sur ce que
fait un script, aller lire le script au lieu d'inférer sa forme.

### 78 pièces sur 100, et le trou est instructif

Six attaques rendent dix pièces contiguës. Le Fire Flower en rend dix
aussi, mais deux d'entre elles, `0xE749` et `0xE754`, sont hors de la
plage de ses huit autres.

Ce détail vaut mieux que les six plages propres : il interdit de combler
les trous par arithmétique. J'allais le faire pour le Jump Helmet, dont
on ne connaît que les pièces 0 et 9, et j'aurais produit huit variables
fausses avec l'air d'être juste.

Le Yoo Who Cannon n'est pas une chasse. Une seule sous-routine écrit ses
deux champs, `|= 31` sur chacun, salle `0x0CF`. Les dix pièces sont
données d'un coup, ce ne sont pas des `location`. Une absence qui
explique une absence.

Restent 12 pièces sans variable, Jump Helmet 8 et Super Bouncer 4.
Vérifié qu'elles ne sont ni dans `FEvent`, ni dans les 268 161 commandes
des scripts de combat, et qu'aucun masque n'est calculé à l'exécution.
Elles se mesureront en jeu.

### Écrire une capacité marche, et ça change le projet

Le dernier chemin d'écriture non testé était le champ `2xxx`. Bit
`0x2019` levé à la main, Fire Flower apparaît au menu Bros Attacks, se
sélectionne, et **se joue en entier, démonstration comprise**, sans que
sa cinématique d'apprentissage ait jamais eu lieu.

C'est exactement le cas qu'un randomizer produit à chaque seed, et le
jeu ne bronche pas. Quarante capacités, du marteau aux améliorations de
boutique, deviennent livrables par une seule primitive : un bit.

Le premier essai est mort sur une erreur de Lua qui mérite d'être
retenue. L'opérateur `^` rend toujours un flottant, `2^1` vaut `2.0`, et
`memory.write_bytes_as_array` lève une `InvalidCastException` dessus.
Le script précédent, `livrer_item.lua`, n'avait jamais rencontré le
problème parce que toutes ses valeurs venaient de lectures entières.
Rien n'avait été écrit, et le champ relu était identique au `run51`.

### L'équipement, ou construire un test qui répond seul

Dernier trou de la livraison, 57 exemplaires. Le `run51` donnait déjà la
réponse à qui la cherchait : deux compteurs non nuls, index 0 à deux
exemplaires et index 80 à un. Sous le décalage `identifiant - 1`, ça se
lit « deux Thin Wear et un Shabby Shell », une tenue par frère et la
carapace de départ. Sous l'autre, « deux No gear et un Challenge
Medal », ce qui n'a aucun sens.

Plutôt que de conclure là-dessus, j'ai construit le test pour qu'il soit
discriminant. Écrire au compteur 4 fait apparaître Heart Wear sous une
hypothèse et Fighter Wear sous l'autre, deux tenues de frères visibles
au même endroit. Le nom affiché tranchait à lui seul, sans que
j'interprète quoi que ce soit. Réponse : **Heart Wear**.

Deux recoupements sont tombés après coup, et c'est le bon ordre. Les
deux objets sans compteur sont `No gear` et `Rental Shell`, une carapace
prêtée par l'histoire, ce qui explique les 129 objets pour 127
compteurs. Et le dernier compteur tombe à `020564A5`, exactement devant
le champ des badges. Le bloc se ferme sans reste.

**725 exemplaires sur 725 sont livrables.** Le client passe à
`items_handling = 0b111`.

### Deux sortes de livraison, et une seule a besoin d'un index

En écrivant la boucle de réception, une distinction s'est imposée qui
n'était pas prévue.

Les compteurs se consomment, donc la mémoire ne dit pas ce qui a déjà
été livré : il faut un index. Les capacités sont des bits qui ne
redescendent jamais, donc l'état visé se déduit entièrement de
`items_received` et de la mémoire. **Cette moitié n'a besoin d'aucun
index**, se recalcule à chaque passage, et rejouer une livraison est
sans effet. Elle est insensible aux déconnexions par construction.

Correction d'une hypothèse du 4 août au passage : MLSS ne range pas son
index dans le `DataStorage`, il l'écrit dans la RAM du jeu,
`Client.py:158`. Le `DataStorage` ne lui sert que pour les flags
d'événement. Les deux choix n'ont pas le même défaut, et le nôtre est
écrit dans l'en-tête de `client.py` plutôt que laissé à découvrir : un
rechargement de savestate laissera le serveur croire des items livrés
que le jeu n'a plus.

Un piège évité de justesse, celui-là par relecture et non par test :
l'index du serveur ne revient qu'au tour suivant, et la boucle repasse
avant. Sans copie locale avancée dès l'écriture, chaque item aurait été
livré plusieurs fois.

### Les guides comme sources, après avoir eu tort de les écarter

J'avais écrit qu'un guide en ligne serait « exactement le genre
d'affirmation plausible que ce projet refuse ». L'utilisateur a fait
remarquer qu'on pouvait chercher la progression sur internet et la
croiser avec ce qu'on lit en mémoire. Il avait raison et j'avais tort :
`MEMOIRE.md` classe les discussions communautaires comme des **pistes à
vérifier**, pas comme rien. Croisées avec une mesure, elles deviennent
des hypothèses testables.

La différence entre les deux positions n'est pas la source, c'est le
croisement. Et le croisement a payé trois fois avant que je m'en serve :

- Super Mario Wiki attribue les dix lots de pièces d'attaque à dix
  zones, notre extraction de l'overlay 123 donne les mêmes, dix sur dix,
  y compris les deux étiquetées hypothèse la veille
- les quatre zones d'acquisition qui ne sont pas des `region` chez nous
  existent toutes dans la table de 32 noms de la ROM
- le guide dit que Bowser récupère son souffle de feu, mnllib nomme le
  bit `FIRE_BREATH_DISABLED`. Les deux concordent, et le bit doit donc
  retomber au lieu de monter. Seule ligne inversée de la table, et il
  valait mieux la voir maintenant qu'en écrivant une règle à l'envers

Ce qui reste non tranché est écrit comme tel : deux pages du même wiki
divergent sur la place de Flab Zone, et le prérequis d'un trésor donné
n'est nulle part.

### Le marteau, et un nom qui cesse d'être une déclaration

Question posée par l'utilisateur : faut-il recommencer la partie depuis
le début pour que le journal capture tout ? Non, et le raisonnement vaut
d'être noté. Tout ce qui est encore inconnu est devant lui ; ce qui est
derrière est la partie la mieux documentée ; et une sauvegarde avancée
teste mieux le client qu'une neuve, puisqu'elle remontera des centaines
de checks d'un coup à la connexion.

Le `run52`, pris juste après le marteau, vaut mieux qu'un redémarrage.
`0x2001` est levé et aucun autre prérequis n'a bougé. Jusque-là les onze
lisaient zéro, ce qui ne prouvait rien : une correspondance fausse lirait
zéro pareil. Un seul bit levé au bon moment fait basculer toute la
plage de « énumération que personne n'utilise » à « vérifié ».

Deux acquis gratuits dans le même dump. Le Fire Flower écrit à la main
la veille est toujours là après une session de jeu. Et les 127 compteurs
d'équipement valent tous exactement 2, l'octet des badges juste après le
bloc restant à zéro : la primitive tient à 127 écritures sans déborder.

### Quatre-vingts bits qui montent ensemble

88 bits `Exxx` montent entre les deux dumps, aucun ne retombe, et aucun
trésor n'a été ramassé. Quatre-vingts forment une plage contiguë,
`0xEEE1` à `0xEF30`.

Noté sans être compris, et pas oublié : la plage est au-dessus de
`0xEDB4`, borne haute des écritures de variables trouvées dans `FEvent`,
donc elle vient du code ARM. Un bloc contigu de 80 ressemble à une
structure indexée, et boutiques et quêtes sont justement le dernier
chantier de locations. Aucune de nos familles connues ne compte 80
éléments. Deux dumps encadrant un achat trancheraient.

### La boucle complète, et elle tient du premier coup

Serveur lancé, connecteur chargé, client connecté. Vingt et un checks
remontent immédiatement : les 11 trésors et les 10 pièces du Green Shell,
exactement ce que le `run52` mesurait, pas un de plus. Aucun des 125
drapeaux d'histoire levés n'est passé au travers du filtre par
`server_locations`.

Les noms sont lisibles côté serveur, `Trash Pit - Green Shell Piece 3`
à côté de `Peach's Castle - Block 544`. Une pièce d'attaque est
indiscernable d'un trésor pour Archipelago, ce qui était le but.

La preuve de la livraison ne pouvait pas venir du log serveur, qui ne
voit que ses envois. Elle tient dans un nombre : 396 pièces d'or
envoyées, 962 en poche, plafond à 999. Le compteur affiche **999**.

Le jeu détecte, le serveur reçoit, renvoie, le client écrit, le joueur
voit. C'est la première fois que la chaîne tourne entière, et elle a
tenu au premier essai sur une rafale de 21 items.

Ce qui a rendu ça possible sans debug, je crois, c'est d'avoir refusé
d'écrire une adresse plausible. Chaque catégorie de livraison avait été
mesurée separement avant d'etre branchee, et `delivery.py` rendait `None`
plutot qu'une adresse devinee tant que la mesure manquait.

### Une correction et une limite

Le client lit 95 octets de `Exxx`. La note du 4 août disait qu'il en
fallait 225 ; c'était le compte pour le rang 1792. La dernière pièce
connue est au rang 2081, octet 260. Autant lire les `0x200` octets du
tableau et ne plus recalculer cette borne.

Limite assumée : les sous-routines de bloc sont dupliquées dans 13 ou 18
chunks de `FEvent`. La salle ne peut pas servir à assigner une `region`
à une pièce. J'ai failli publier la colonne « salle » avec la dernière
salle rencontrée, ce qui aurait ressemblé à une donnée. Le script liste
maintenant toutes les salles et affiche leur nombre.

## 4 août 2026, soir, livrer un objet puis tomber sur mieux

Séance ouverte sur une question de reprise, « où on en était », et
fermée sur deux acquis dont un n'était pas au programme.

### Livrer un objet, mesuré au lieu d'être déduit

`tools/livrer_item.lua` existait depuis la veille et n'avait jamais
tourné. Un Nut écrit à `0205640D`, index 7, de 0 à 1.

Le `relu : 1` du script ne prouvait rien, la relecture passant par le
même chemin que l'écriture. Le `run31` l'a vérifié de l'extérieur, et
mieux : le diff du bloc inventaire contre `run30` ne montre que deux
octets, notre Nut et le compteur de pièces qui descend de 999 à 948 par
le jeu normal. Aucun des 25 autres compteurs d'objets, aucun des 127
emplacements d'équipement.

La preuve qui compte n'est toujours pas venue d'un dump. Le Nut est
apparu au menu et a été consommé. Comme pour les 999 pièces la veille,
c'est l'écran qui tranche.

### La question de la portée, posée puis reportée par les faits

Estimation demandée, environ 45 % du projet, avec un écart assumé entre
le risque levé, à peu près 85 %, et le travail fait. Le reste tient
surtout dans la logique et le pool d'items, chantier à 5 %.

L'arbitrage à rendre était la portée : treasure shuffle seul, ou
randomisation des attaques. Il n'a pas été rendu, et c'est très bien,
parce que l'utilisateur a signalé qu'il était planté devant un bloc à
pièces d'attaque. Une occasion de mesure vaut mieux qu'un arbitrage pris
sans données.

### Le protocole amélioré par le joueur, encore une fois

J'avais prévu quatre dumps. Il a expliqué le mécanisme, dix pièces à
collecter pour un lot, et cette information a changé la mesure du tout
au tout : une valeur qui suit 0, 1, 2, 3 sur quinze dumps n'a
pratiquement aucune chance d'être un homonyme, là où un simple 0 vers 1
en aurait eu des dizaines. Il a ensuite dumpé après chaque pièce sans
qu'on le lui demande, et un rechargement d'état au `run37` s'est vu dans
les données sous forme d'un retour à zéro net sur les trois supports.

Deuxième fois de la journée que la connaissance du jeu par le joueur
produit un meilleur protocole que le mien. La règle du 4 août au matin
tient : quand la question porte sur ce que fait le jeu, faire faire au
jeu.

### Trois supports redondants

Deux candidats seulement survivent aux dix filtres. `020562E5`, soit la
variable `6xxx` numéro `0x601D`, et `02056024`, base du tableau `Cxxx`.

Le second est le registre de message, celui qui affiche le compte à
l'écran. Il est écarté sans mesure supplémentaire, sur un fait déjà
vérifié : la fonction de sauvegarde recopie `2xxx`, `Dxxx`, `Exxx`,
`6xxx` et la plage anonyme, jamais `Cxxx`. Ce qui n'est pas sauvegardé
ne peut pas porter l'état d'une progression.

Le vrai résultat est ailleurs et n'était pas cherché. Neuf bits contigus
sont montés dans `Exxx`, `0xE700` à `0xE708`, un par pièce, plus deux
champs de bits `0x601B` et `0x601C` de cinq bits chacun. Les trois
supports sont d'accord dans le désordre du ramassage, ce qui interdit la
coïncidence.

**Une pièce d'attaque est donc une `location` ordinaire**, lisible par le
mécanisme déjà écrit. Le chantier « trésors hors `TreasureInfo.dat` »,
qu'on croyait devoir attaquer au désassembleur de scripts, se règle par
dix sauts dans un jeu.

### Ce qui reste en suspens, et il est important

La dixième pièce débloque l'attaque, et personne ne sait si les bits
`Exxx` survivent au déblocage ou si le lot est remis à zéro pour le
suivant. S'ils retombent, tout ce qui précède devient inutilisable comme
`location`. La partie est laissée devant le dernier bloc, neuf pièces
ramassées, deux dumps à prendre : un juste après le déblocage même en
plein combat, un après le combat sur le terrain.

## 4 août 2026, quand écrire, et la réponse est « quand on veut »

Seize dumps, `run14` à `run30`, pour répondre à la dernière question
technique du projet : à quel moment le client peut écrire sans risque.

La réponse est qu'il n'y a pas de moment interdit. Une écriture faite en
plein combat prend effet, s'affiche à l'écran, et survit à la sortie —
le crédit de fin de combat s'ajoute à la valeur courante au lieu de la
remplacer. Détail des mesures dans `formats-bis.md`.

### Deux hypothèses fausses, la même forme que la veille

J'ai d'abord conclu que le combat travaillait sur sa propre copie de
l'inventaire, parce qu'un compteur d'objet n'avait pas bougé. Il n'avait
pas bougé parce qu'aucun objet n'avait été consommé — l'utilisateur avait
oublié de manger le champignon. **Prémisse non mesurée, conclusion
fausse**, exactement comme le `max_hits` la veille.

J'ai aussi cherché un drapeau d'état terrain / combat pendant une heure.
Dix dumps de terrain et huit de combat laissaient 38 candidats, sans
aucun moyen de choisir. La recherche était bien menée et parfaitement
inutile : la bonne question n'était pas « le jeu est-il en combat » mais
« notre cible est-elle touchée », et celle-là se mesure directement.

### Ce que l'utilisateur a apporté

Sa liste de sous-états de combat, que j'avais jugée en partie superflue,
a produit les dumps qui ont tranché. Sa proposition d'écrire les pièces
en plein combat valait mieux que mon protocole : une réponse binaire en
deux minutes contre une heure de filtrage. Et la confirmation la plus
forte n'est pas venue d'un dump mais de l'écran, où l'affichage montrait
999 pendant le combat.

Règle à en tirer : quand une question porte sur ce que fait le jeu,
**faire faire au jeu** plutôt que comparer des images de sa mémoire.

### Une question éliminée plutôt que résolue

Il fallait mémoriser le nombre d'items déjà livrés, sinon une
reconnexion les redonnerait en double. J'allais écrire dans les 7 octets
que Cheatoglobin dit sans effet à `slot + 0x001E`, et demander à la
communauté s'ils sont vraiment libres.

Deux erreurs. On ne demande pas ce qu'on peut mesurer, et surtout le
besoin n'existait pas : Archipelago a un `DataStorage` côté serveur, que
MLSS utilise déjà pour ses flags. Le compteur y va, et **on n'écrit rien
dans une zone qu'on ne comprend pas**. La bonne réponse à une question
difficile est parfois de supprimer la question.

## 4 août 2026, la chaîne complète tourne

Première séance de test bout en bout. Serveur local, client BizHawk,
connecteur Lua, partie en cours.

```
Connected to BizHawk
Running handler for Mario & Luigi Bowser's Inside Story
...
TestBIS sent Flower Gloves to TestBIS (Trash Pit - Block 555)
```

`validate_rom` a lu l'en-tête de cartouche, reconnu `MARIO&LUIGI3` et
`CLJE`, et Archipelago a choisi notre client sur cette base. Les onze
trésors déjà ramassés sont remontés d'un coup à la connexion, puis le
bloc cassé pendant la séance est apparu en direct.

`emu.getsystemid()` répond bien `NDS`. L'hypothèse du client tombe.

### Deux pièges de séance, tous les deux hors du code

Le premier a coûté vingt minutes : **ouvrir un script dans la console Lua
de BizHawk ne le lance pas**. La case doit être cochée. Le connecteur
affichait « Looking for client... » en boucle alors qu'il ne tournait
pas, et le client affichait « Waiting to connect to BizHawk... » : deux
messages parfaitement cohérents avec un troisième acteur absent.

Le second : le client lancé depuis mon outil n'a jamais accroché, celui
lancé par l'utilisateur oui. Droits réseau, autorisation de pare-feu, ou
cloisonnement de mon côté — non tranché, et sans importance tant que la
règle pratique tient : **les processus qui doivent parler à l'émulateur,
c'est l'utilisateur qui les lance.**

### Le nom du slot est saisi à la main, et c'est normal

Notre client ne connaît pas son slot : dans un monde fini, il est inscrit
dans la ROM patchée à la génération. On ne patche rien encore.

## 4 août 2026, le client qui lit

`mlbis/client.py`, sous-classe de `BizHawkClient`. Il lit 95 octets à
`0x0560C8` dans `Main RAM` et signale au serveur chaque bit allumé.

Le gain de la convention d'identifiants se voit ici : la boucle n'a
**aucune table de correspondance** entre un bit et une `location`, parce
que l'identifiant de trésor est à la fois le rang du bit et, à `BASE_ID`
près, l'identifiant de location. MLSS, faute de cette propriété, refait
à chaque check une reconstruction d'adresse par pointeur en ROM et
soustractions cumulées, `Client.py` 225 à 238.

### Un défaut de conception corrigé en cours de route

Première version : tout dans `client.py`. Le test a échoué au premier
`import`, parce que charger `mlbis` tire `worlds.AutoWorld`, donc
Archipelago entier, absent du venv de la racine.

Le vrai problème n'était pas le venv. **La connaissance du plan mémoire
du jeu n'a aucune raison de dépendre du client.** Sortie dans
`mlbis/bitfield.py`, qui n'importe rien : ni Archipelago, ni le reste du
monde. Elle devient vérifiable sur un dump, sans émulateur et sans
serveur.

`tools/test_client.py` le fait, et passe :

```
run06 : 0 location    run08 : 1    run12 : 4    run13 : 4
correspondance id = BASE_ID + rang de bit : OK sur 647 locations
```

Les attendus ne sont pas inventés pour l'occasion : ce sont les mesures
déjà consignées dans `formats-bis.md`. Le test relit de vrais dumps.

### Deux choses volontairement absentes

`items_handling = 0b000` : le serveur ne nous envoie aucun item. On sait
écrire depuis le 3 août, mais **on ne sait pas quand c'est sûr**, et
`MEMOIRE.md` impose de tenir une écriture en combat ou en cinématique pour
dangereuse tant que rien ne prouve le contraire.

Aucune détection de fin de partie, faute d'un flag de victoire identifié.

### À vérifier, et c'est une supposition assumée

`system = "NDS"`. Aucun monde NDS n'est livré avec Archipelago 0.6.8,
donc aucun précédent à copier ; la valeur vient de `emu.getsystemid()`,
qu'il suffit d'afficher une fois dans la console Lua. Noté dans
`MEMOIRE.md` pour ne pas l'oublier au prochain lancement.

## 4 août 2026, les régions deviennent réelles

Le squelette n'avait qu'une seule `region` parce que la correspondance
salle → zone manquait. Elle ne manque plus.

La piste était dans la signature de `randomize_treasure` : Randoglobin
reçoit un `map_metadata_offset` et un `map_group_offset`. En remontant
son code de nommage, `treasure.py` 396 à 425, on obtient la chaîne
complète : overlay 3 pour le groupe de cartes et les métadonnées,
overlay 4 pour les plages d'octets dans `TreasureInfo.dat`, overlay 129
pour les icônes de l'écran de sélection de fichier, qui portent l'index
du nom de zone.

681 cartes, 278 portent des trésors, et les 647 trésors exploitables se
répartissent sur **16 zones nommées** : Peach's Castle 117, Bowser Castle
66, Dimble Wood 65, Toad Town 64, et ainsi de suite jusqu'à Tower of Yikk
avec 3.

### Le résultat qui fait plaisir

Le regroupement en salles fait le 2 août par le bit
`is_last_entry_in_room`, sans rien savoir des cartes du jeu, est en
**bijection** avec le découpage réel : 265 salles pour 265 cartes, aucune
ambiguïté dans les deux sens. On avait deviné juste sans le savoir, et on
peut maintenant le prouver.

Réserve consignée : 13 trésors sur 685 sont revendiqués par plusieurs
cartes, plages qui se chevauchent. La plus petite est retenue comme la
plus spécifique. C'est un choix, pas une lecture.

Conséquence immédiate : le monde passe de 1 à 16 `region`, et les noms de
`location` deviennent lisibles, `Pump Works - Block 0` au lieu de
`Block 0`. Fait maintenant plutôt que plus tard, parce que ces noms sont
un contrat gelé dès la première seed publiée.

Ce qui reste absent, et pour la même raison qu'avant : aucune
`access_rule`. Savoir qu'un trésor est dans Dimble Wood ne dit pas ce
qu'il faut pour y entrer. C'est le prochain chantier, et c'est celui qui
demande de connaître le jeu plutôt que de le désassembler.

## 4 août 2026, le squelette génère

Premier code d'APWorld du projet, dans `mlbis/`. Six fichiers, aucune
ligne de données saisie à la main : `tools/build_apworld_data.py`
fabrique `mlbis/data.py` depuis `locations_bis.csv`, lui-même régénéré
depuis la ROM.

Archipelago 0.6.8 le charge et sort une seed :

```
Mario & Luigi Bowser's Inside Story  : v0.0.0 | Items: 86 | Locations: 647
```

Contrôle que la seed n'est pas vide : `Block 0` contenait 100 pièces dans
le jeu d'origine, il porte autre chose après brassage.

Choix d'identifiants, posé maintenant parce qu'il devient un contrat gelé
dès la première seed publiée : `BASE_ID = 0xB15000`, et la location d'un
trésor vaut `BASE_ID + identifiant`. L'identifiant étant aussi le rang du
bit dans `Exxx`, **un identifiant de location se lit directement comme un
index de bit**, sans table de correspondance. Les identifiants 758 à 1023
restent libres, et le hors-table commencera à `BASE_ID + 1024`, ce qui
reproduit l'espace d'index du tableau `Exxx`.

Trois choses sont volontairement absentes, et il faut savoir pourquoi :

- **Une seule region.** Pas par paresse : `locations_bis.csv` porte un
  numéro de salle reconstruit dans l'ordre du fichier, et les 32 zones
  nommées sont une autre numérotation. La correspondance entre les deux
  n'est pas établie, et l'inventer serait inventer une donnée
- **Aucun item de progression.** Déclarer une progression sans
  `access_rule` qui l'utilise ne change rien au placement et donnerait
  une fausse impression de logique
- **Aucune option**, pour la même raison

`tools/test_generation.py` rend le test reproductible : il recopie
`mlbis/` dans `vendor/Archipelago/worlds/`, génère, et vérifie que le
monde a bien été listé. Vérifié en repartant d'un dossier effacé.

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

Piège rencontré : `%USERPROFILE%` est lui-même un dépôt Git, donc
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

Créé un raccourci de bureau qui ouvre le terminal de travail
directement dans le dossier du projet, avec une phrase de reprise
passée en argument, pour repartir sans renaviguer ni retaper.

Le prompt vit dans le champ Arguments du `.lnk`, stocké en UTF-16, donc
les accents survivent sans dépendre de la codepage d'un `.cmd`
intermédiaire. Relu après création, codepoints 249, 233 et 234 intacts.
Pas de script intermédiaire à maintenir.

Le raccourci est sur le bureau, hors du dépôt : rien à committer.

## 2 août 2026, dépouillement de Cheatoglobin et Randoglobin

Cheatoglobin cloné dans `vendor/`. Sa lecture donne d'un coup toute la
structure du fichier de sauvegarde, checksum et copie de secours
compris. Reporté dans `MEMOIRE.md`.

Piste suivie ensuite : `grep -rn "block"` dans Randoglobin, qui tombe
sur `mnlscript_skips.py:480`, `block_var = 0xE701 + i`. Fausse joie
partielle : c'est une réécriture custom d'une salle à énigme par
Randoglobin, pas le mécanisme générique du jeu. En revanche la ligne
535 montre qu'un acteur porte un champ `(variable << 16) + subroutine`,
ce qui est bien un mécanisme du moteur.

`EObjSave/EObjSave.dat` a l'air d'être de l'état de sauvegarde à cause
de son nom. Ce n'est que des palettes (`palette.py` 743 à 778). Noté
comme écarté dans `MEMOIRE.md` pour ne pas y revenir.

Le vrai gain est `Treasure/TreasureInfo.dat`, table d'entrées de
12 octets qui ressemble beaucoup à la liste des `location` d'un futur
APWorld.

`MEMOIRE.md` atteint 232 lignes, au-dessus du seuil de 220 qu'il se fixe
lui-même. À dégraisser à la prochaine occasion.

## 2 août 2026, dump de la table des trésors

Feu vert donné pour ouvrir la ROM en lecture. Rien n'a été écrit
dedans : `ndspy` charge en mémoire, aucun `saveToFile`.

Premier réflexe avant de lire quoi que ce soit : rehasher le `.nds`. Le
SHA-256 correspond exactement à celui figé dans `MEMOIRE.md`, malgré le
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

Dégraissage de `MEMOIRE.md` fait dans la foulée, en deux temps parce que
le premier essai a fini à 248 lignes, soit pire qu'avant : les acquis
ajoutés pesaient plus que la section retirée. Détail des formats sorti
dans `formats-bis.md`, contraintes d'empaquetage dans
`empaquetage-apworld.md`. `MEMOIRE.md` retombe à 195 lignes.

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

Détail noté dans `reference-mlss.md` plutôt que dans `MEMOIRE.md`, qui
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
effacerait ce bit. Le piège est noté dans `MEMOIRE.md` à côté du checksum
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

### Réglages de l'environnement rendus permanents

Les réglages du terminal de travail ont été fixés une fois pour toutes
dans un fichier local, non versionné, plutôt que retapés à chaque
session. Sans effet sur le projet lui-même.

### Tenue des fichiers

`MEMOIRE.md` est remonté à 219 lignes, à une du plafond. Trois lignes
seulement y ont été ajoutées, gagées par la compression de trois entrées
devenues redondantes avec `formats-bis.md`. Prochain candidat à la
sortie, noté dans le fichier lui-même : la section « Particularités du
jeu ».
