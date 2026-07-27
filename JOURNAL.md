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
