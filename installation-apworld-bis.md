# Plan d'installation, projet APWorld BIS (Windows)

Plan en 8 phases, la huitième étant optionnelle. **Exécuter une seule phase, puis s'arrêter et
attendre le feu vert avant de passer à la suivante.** Ne jamais
enchaîner deux phases sans validation explicite.

## Contexte

Machine Windows vierge. Objectif : préparer l'environnement pour
développer un APWorld Archipelago pour Mario & Luigi : Bowser's Inside
Story sur NDS. Le projet est en phase de faisabilité.

Les versions indiquées ne sont pas des suggestions. Elles viennent de
contraintes croisées lues dans les sources, et une erreur de version
coûte des heures de debug qui ne pointent pas vers leur cause.

## Règles permanentes

- Une phase, puis stop. Attendre la réponse avant de continuer
- Ne rien installer qui ne figure pas dans ce fichier
- Ne jamais chercher, télécharger ou proposer de télécharger une ROM
- Ne pas déplacer ni modifier le fichier `.nds`, sauf indication
  explicite en phase 1
- Ne pas installer Visual Studio Build Tools de façon préventive
- Ne pas prendre la dernière version de BizHawk, voir phase 5
- Si un identifiant winget ne résout pas, le signaler au lieu d'en
  inventer un
- Montrer la sortie réelle des commandes, pas un résumé

---

# Phase 1, rangement du dossier

Le dossier de travail, noté `%RACINE%` dans tout ce fichier, est celui
qui contient la ROM, `MEMOIRE.md` et les sous-dossiers `tools/` et
`mlbis/`. Aucun chemin absolu n'est écrit ici : les scripts déduisent
tous le leur de leur propre emplacement.

Actuellement les fichiers `MEMOIRE.md` et `installation-apworld-bis.md`
sont dans le sous-dossier de la ROM, ce qui empêche le chargement
automatique de `MEMOIRE.md`. Il doit être à la racine du dossier de
travail.

À faire :

- Remonter `MEMOIRE.md` et `installation-apworld-bis.md` à la racine de
  `Projet BIS`
- Laisser le fichier `.nds` où il est, dans son sous-dossier

Vérification :

```powershell
cd "%RACINE%"
Get-ChildItem
```

Attendu à la racine : les deux `.md` et le dossier de la ROM.

**STOP.** Montrer la sortie et attendre.

---

# Phase 2, Python 3.13 et Git

Deux installations, rien d'autre.

## Python 3.13

Contrainte croisée entre deux sources.

- Archipelago, `docs/running from source.md`, section General :
  3.11.9 minimum, strictement inférieur à 3.14, pas la version du
  Windows Store
- Randoglobin, `pyproject.toml`, champ `requires-python` : 3.12
  minimum, strictement inférieur à 3.15

L'intersection est 3.12 ou 3.13. On prend 3.13.

```powershell
winget search Python.Python.3.13
winget install --id Python.Python.3.13 --source winget
```

## Git

Requis par Archipelago pour installer certaines de ses dépendances.
Source : `docs/running from source.md`, section Optional: Git, dont le
texte contredit le titre.

```powershell
winget search Git.Git
winget install --id Git.Git --source winget
```

Vérification, dans un terminal neuf :

```powershell
py -3.13 --version
py -3.13 -m pip --version
git --version
```

Attendu : une version 3.13.x, un pip fonctionnel, une version de Git.

**STOP.** Montrer les trois sorties et attendre.

---

# Phase 3, gitignore et dépôt local

**L'ordre de cette phase est critique.** Le `.gitignore` doit exister
avant tout `git add`. Un fichier committé reste dans l'historique même
après suppression, et la ROM ne doit jamais y entrer.

## Créer le .gitignore

À la racine de `Projet BIS`, contenu exact :

```gitignore
# ROM et derives, ne jamais committer
*.nds
*.7z
*.zip
*.sav
*.srm
*.dsv
*.xdelta
4171*/

# Depots tiers, clones separement
vendor/

# Python
venv/
__pycache__/
*.pyc

# BizHawk
bizhawk-*/
```

## Initialiser et vérifier

```powershell
cd "%RACINE%"
git init
git status
```

**Ne pas faire de `git add` à cette étape.**

Vérification à faire soi-même avant de rendre la main : confirmer que
`git status` ne liste **ni** le fichier `.nds`, **ni** le dossier de la
ROM. Si l'un des deux apparaît, ne rien committer et le signaler.

**STOP.** Montrer la sortie complète de `git status` et attendre.

---

# Phase 4, premier commit

À faire seulement si la phase 3 est validée.

```powershell
git add .
git status
```

Confirmer une seconde fois que rien de lié à la ROM n'est en zone de
staging, puis :

```powershell
git commit -m "Contexte projet et plan d'installation"
git log --oneline
```

**STOP.** Montrer le log et attendre.

Note : pousser sur GitHub demande une authentification que seul
l'utilisateur peut faire, via `gh auth login`. Ne pas tenter de push
et ne pas proposer de le faire à cette phase.

---

# Phase 5, dépôts tiers en lecture

Ces clones servent à lire et comprendre. Ils vont dans `vendor/`, qui
est ignoré par Git, pour éviter des dépôts imbriqués.

```powershell
cd "%RACINE%"
mkdir vendor
cd vendor
git clone https://github.com/ArchipelagoMW/Archipelago.git
git clone https://github.com/MnL-Modding/Randoglobin.git
git clone https://github.com/MnL-Modding/BIS-docs.git
git clone https://github.com/MnL-Modding/mnllib.py.git
```

Licence, à ne pas perdre de vue : Randoglobin est sous
GPL-3.0-or-later. Le lire est libre, en recopier du code imposerait la
GPL à l'APWorld. Ces clones sont là pour comprendre, pas pour copier.

Vérification :

```powershell
Get-ChildItem
cd ..
git status
```

Attendu : quatre dossiers dans `vendor`, et un `git status` propre qui
ne mentionne pas `vendor`.

**STOP.** Montrer les deux sorties et attendre.

---

# Phase 6, BizHawk 2.10 précisément

**Ne pas prendre la dernière version publiée.**

Source : `data/lua/connector_bizhawk_generic.lua` du dépôt Archipelago,
lignes 633 à 637. Le script refuse BizHawk antérieur à 2.7.0, et
au-delà de 2.10 il affiche un avertissement conseillant de redescendre
en 2.10.

À faire :

- Aller sur la page des releases de TASEmulators/BizHawk, trouver le
  tag 2.10, récupérer `BizHawk-2.10-win-x64.zip`
- L'extraire dans `Projet BIS\bizhawk-2.10`
- Ne pas mélanger plusieurs versions de BizHawk dans un même dossier,
  c'est un avertissement explicite du projet

Prérequis Windows : depuis la version 2.10, seul le redistributable
Microsoft Visual C++ est nécessaire. Source : README de
TASEmulators/BizHawk, section Installing. L'ancien installateur
all-in-one ne sert que pour les versions antérieures.

```powershell
winget search Microsoft.VCRedist.2015+.x64
winget install --id Microsoft.VCRedist.2015+.x64 --source winget
```

Vérification : confirmer la présence de `EmuHawk.exe` dans
`bizhawk-2.10`, et que `git status` reste propre.

Ne pas lancer l'émulateur. Son démarrage et sa configuration sont
faits à la main par l'utilisateur.

**STOP.** Montrer la sortie et attendre.

---

# Phase 7, dépendances Python d'Archipelago

À faire seulement après validation des phases 1 à 6.

```powershell
cd "%RACINE%\vendor\Archipelago"
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
python ModuleUpdate.py
```

`ModuleUpdate.py` propose d'installer les modules manquants, il faut
valider. Le venv est recommandé par la doc parce qu'Archipelago exige
des versions précises de paquets Python.

Si PowerShell refuse d'exécuter le script d'activation, c'est la
politique d'exécution qui bloque. Le signaler et proposer une portée
limitée à la session, ne pas modifier la politique globale de la
machine.

Vérification :

```powershell
python Launcher.py
```

Attendu : la fenêtre du Launcher Archipelago s'ouvre.

**STOP.** C'est la fin du plan. Faire un bilan des sept phases, en
indiquant ce qui a réussi et ce qui a échoué.

---

# Phase 8, dépôt distant GitHub

**Phase optionnelle et à risque.** Ne la lancer que si les phases 1 à 7
sont validées et si l'utilisateur la demande explicitement.

Pousser est irréversible dans les faits. Une erreur locale se corrige
en supprimant `.git`, une erreur poussée expose à un takedown et à une
suspension de compte, dépôt privé ou non.

## Vérification préalable, obligatoire

Trois contrôles, dans cet ordre, avant toute création de dépôt.

```powershell
cd "%RACINE%"
git ls-files
git count-objects -vH
```

Critères de validation, à évaluer et à annoncer explicitement :

- `git ls-files` ne doit lister que des `.md`, le `.gitignore` et du
  code. Aucun `.nds`, aucun `.7z`, aucun `.zip`
- `size-pack` doit être de l'ordre de quelques dizaines de kilooctets.
  Si cette valeur dépasse un mégaoctet, quelque chose de binaire est
  dans l'historique

Attention : GitHub bloque les fichiers de plus de 100 Mo, ce qui
arrêterait le `.nds` de 128 Mo. Mais le `.7z` de 52 Mo passerait sans
alerte. Ne pas se reposer sur cette limite comme garde-fou.

Si l'un des deux critères échoue, **ne rien créer et ne rien pousser.**
Le signaler et s'arrêter.

**STOP.** Montrer les deux sorties et attendre la validation avant de
continuer.

## Authentification

Seul l'utilisateur peut la faire, elle passe par le navigateur.

```powershell
winget search GitHub.cli
winget install --id GitHub.cli --source winget
gh auth login
```

Après installation, ouvrir un terminal neuf. `gh auth login` doit être
lancé par l'utilisateur, qui suit le flux dans son navigateur.

Vérification :

```powershell
gh auth status
```

**STOP.** Attendre confirmation que l'authentification a réussi.

## Création et push

Le dépôt doit être **privé**. Rien dans ce projet n'a vocation à être
publié à ce stade.

```powershell
gh repo create apworld-bis --private --source=. --remote=origin
git push -u origin main
```

Si la branche locale s'appelle `master` et non `main`, adapter la
commande plutôt que de renommer la branche sans le dire.

Vérification :

```powershell
git remote -v
gh repo view --web
```

**STOP.** Fin de la phase.

---

# Ce qui reste manuel après ce plan

- La configuration de BizHawk dans ses menus : Lua Core, AutoSaveRAM,
  Run in background
- L'authentification GitHub via `gh auth login`, en phase 8
- Jouer, observer, relever

# Ce qu'on n'installe pas maintenant

Chaîne de compilation ARM, armips, Rust, Visual Studio Build Tools.
Randoglobin embarque un binaire compilé pour `armv5te-none-eabi`, donc
ce chemin existe, mais rien ne dit encore que ce projet en aura besoin.
Tant que ce n'est pas tranché, ne pas les installer.
