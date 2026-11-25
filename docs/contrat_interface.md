# Contrat d'interface — fichier de prévisions (B6)

Responsable : SAVADOGO Pengdwendé Faysal · Version 1 (jalon J2)

Le modèle écrit un fichier `data/processed/previsions.csv`. L'API et l'application web le lisent tel quel.
Toute modification de ce format passe par une pull request relue par les trois membres.

## Format

- Encodage UTF-8, séparateur `,`, point décimal `.`, une ligne d'en-tête.
- Une ligne = une prévision pour une date cible, émise un jour donné.
- Pour chaque date d'émission : exactement 7 lignes (horizons 1 à 7).

| Colonne | Type | Exemple | Signification |
|---|---|---|---|
| `date_emission` | date `AAAA-MM-JJ` | `2025-04-06` | Jour J : dernières données utilisées (soir du jour J) |
| `date_cible` | date `AAAA-MM-JJ` | `2025-04-08` | Jour prévu = `date_emission` + `horizon` |
| `horizon` | entier 1 à 7 | `2` | Nombre de jours entre émission et cible |
| `tmax_predite` | décimal (°C), 1 décimale | `41.8` | Température maximale prévue (T2M_MAX) |
| `seuil_pic` | décimal (°C), 2 décimales | `41.07` | 95e centile calculé sur 1981-2015 (valeur provisoire, recalculée en T6) |
| `alerte_pic` | entier 0 ou 1 | `1` | 1 si le modèle prévoit un jour de pic |
| `modele` | texte | `persistance` | Nom du modèle (`persistance`, `climatologie`, `regression_lineaire`, ...) |

## Exemple

```csv
date_emission,date_cible,horizon,tmax_predite,seuil_pic,alerte_pic,modele
2025-04-06,2025-04-07,1,41.6,41.07,1,persistance
2025-04-06,2025-04-08,2,41.6,41.07,1,persistance
```

## Règles

- `alerte_pic` vient de la décision du classifieur (seuil de décision réglé sur la validation). Ce n'est pas forcément `tmax_predite > seuil_pic`.
- Aucune valeur manquante : une prévision impossible n'est pas écrite.
- L'application affiche toujours `seuil_pic` en °C et l'avertissement « outil pédagogique, pas un bulletin météo officiel ».
