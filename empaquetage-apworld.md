# Contraintes d'empaquetage APWorld

Sorti de `MEMOIRE.md` le 2 août 2026 pour le maintenir sous son seuil de
220 lignes. Ce contenu ne servira qu'au moment où le monde sera
réellement écrit et empaqueté, donc il n'a pas à occuper la mémoire
chargée à chaque session. `MEMOIRE.md` pointe vers ce fichier.

Erreurs classiques dont le message ne pointe pas vers la vraie cause.

- Le fichier `.apworld` doit être entièrement en minuscules
- Le zip doit contenir un dossier au nom exactement identique au zip
- Imports internes au monde en relatif (`from .options import ...`)
- Imports vers le cœur d'Archipelago en absolu
  (`from worlds.AutoWorld import World`)
- L'empaquetage passe par le composant Build APWorlds du launcher, qui
  ajoute lui-même `version` et `compatible_version`. Ne jamais les
  écrire à la main
