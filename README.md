# Prévision à court terme des pics de chaleur à Ouagadougou

Projet intégrateur — Master 1 Intelligence artificielle, Université Aube Nouvelle (2025-2026).
Équipe **Bangré** : OUEDRAOGO Eugène Golbert, BALIMA Hairatou, SAVADOGO Pengdwendé Faysal.
Enseignant : Dr NKUNA WA NKUNA Charles.

## But du projet

Prévoir la température maximale quotidienne (T2M_MAX) de J+1 à J+7 au point NASA POWER de Ouagadougou
et signaler les jours de « pic de chaleur » (T2M_MAX au-dessus du 95e centile calculé sur 1981-2015).
L'objectif est d'aider les acteurs de la santé à décider, en fin de semaine, s'ils publient une mise en garde
contre la chaleur pour la semaine suivante.

> ⚠️ **Outil pédagogique.** Ce n'est pas un bulletin météorologique officiel. L'absence d'alerte ne garantit
> pas l'absence de chaleur dangereuse.

## Données

| Élément | Valeur |
|---|---|
| Source | NASA POWER (Prediction Of Worldwide Energy Resources), données quotidiennes, https://power.larc.nasa.gov |
| Point | 12,37° N ; 1,52° O (Ouagadougou) |
| Période | 01/01/1981 au 31/12/2025, 16 436 jours |
| Variables | T2M, T2M_MAX, T2M_MIN (°C), RH2M (%), WS2M (m/s), PRECTOTCORR (mm/jour) |
| Date de téléchargement | _à compléter_ |
| Conditions d'utilisation | _à compléter après vérification sur le site de NASA POWER_ |

Le fichier brut est rangé dans `data/raw/` et n'est **jamais modifié**. Toute transformation passe par un script
de `src/` qui écrit dans `data/processed/`.

Découpage chronologique : entraînement 1981-2015, validation 2016-2020, test 2021-2025 (utilisé une seule fois, à la fin).

## Organisation du dépôt

```
README.md            présentation, installation, utilisation
requirements.txt     bibliothèques Python
.gitignore           fichiers à ne pas versionner
data/raw/            données brutes (jamais modifiées)
data/processed/      données préparées par les scripts
notebooks/           01_exploration.ipynb, 02_modele_reference.ipynb, ...
src/                 code réutilisable (.py)
tests/               tests automatiques (absence de fuite, format des prévisions)
models/              modèles entraînés
reports/             figures et rapports (J3, J5, rapport final)
docs/                plan de projet, contrat d'interface, journal de bord, comptes rendus
```

## Installation

```bash
git clone <adresse-du-depot>
cd <depot>
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS : source .venv/bin/activate)
pip install -r requirements.txt
```

## Règles de l'équipe

- On ne travaille jamais directement sur `main` : une branche par tâche du Kanban (ex. `T4-stats`).
- Toute modification passe par une pull request relue et fusionnée par un autre membre.
- Petits commits fréquents avec un message explicite ; `git pull` avant de commencer.
- Un notebook = un auteur ; sorties effacées avant commit ; le code partagé va dans `src/`.
- Pas de fichiers lourds, de mots de passe ni de clés d'API dans Git.
