# Dictionnaire des variables (tâche T3)

Fichier : `data/raw/nasa_power_ouaga_1981_2025.csv` — NASA POWER, point 12,37° N ; 1,52° O (Ouagadougou),
du 01/01/1981 au 31/12/2025, 16 436 lignes. Une ligne = un jour.
Source des valeurs : réanalyse MERRA-2 (maille ½° × ⅝°, environ 55 × 68 km), agrégée par jour par NASA POWER.

## Colonnes du fichier brut

| Variable | Type | Unité | Signification | Min | Médiane | Max | Remarques |
|---|---|---|---|---|---|---|---|
| YEAR | Entier | année | Année du relevé | 1981 | — | 2025 | Combinée avec DOY pour former la date |
| DOY | Entier | jour | Jour de l'année (1 à 365 ou 366) | 1 | — | 366 | « Day Of Year » |
| T2M | Décimal | °C | Température moyenne de l'air à 2 m | 16,16 | 27,26 | 37,30 | Moyenne des 24 valeurs horaires |
| T2M_MAX | Décimal | °C | Température maximale de l'air à 2 m | 23,83 | 34,79 | 44,60 | **Cible** du projet ; maximum des 24 valeurs horaires |
| T2M_MIN | Décimal | °C | Température minimale de l'air à 2 m | 9,33 | 22,20 | 31,07 | Minimum des 24 valeurs horaires |
| RH2M | Décimal | % | Humidité relative à 2 m | 5,83 | 49,50 | 92,90 | Très basse en saison sèche (harmattan) |
| WS2M | Décimal | m/s | Vitesse du vent à 2 m | 0,38 | 1,64 | 4,84 | — |
| PRECTOTCORR | Décimal | mm/jour | Précipitations totales corrigées | 0,0 | 0,1 | 140,9 | 0 mm pour 43 % des jours ; corrigées avec des observations de pluie |

Valeur manquante : codée **-999** par NASA POWER (aucune dans ce fichier).

## Variables construites (prévues pour la préparation, `src/preparation.py`, tâche T11)

| Variable | Type | Unité | Définition | Remarques |
|---|---|---|---|---|
| date | Date | jour | YEAR + DOY convertis en date calendaire | Clé unique, aucun doublon |
| pic | Binaire | 0/1 | 1 si T2M_MAX > 40,94 °C | Seuil = 95e centile de 1981-2015 uniquement (pas de fuite) |
| doy_sin, doy_cos | Décimal | — | sin et cos de 2π × jour de l'année / 365,25 | Saisonnalité sans rupture au 31/12 |
| climatologie_tmax | Décimal | °C | Moyenne de T2M_MAX du même jour du calendrier, sur 1981-2015 | Référence « climatologie » |
| T2M_MAX_lag1 … lag7 | Décimal | °C | T2M_MAX des jours J-1 à J-7 | Toutes connues au soir du jour J |
| cible_h1 … cible_h7 | Décimal | °C | T2M_MAX des jours J+1 à J+7 | Sorties à prédire |

## Relations utiles (tâche T7, `src/exploration.py`, figures 4 et 5)

- **Corrélations avec T2M_MAX** : T2M 0,78 ; T2M_MIN 0,40 ; WS2M 0,25 ; PRECTOTCORR -0,37 ; RH2M -0,52.
  L'air humide et pluvieux de la saison des pluies fait baisser la température maximale.
- **Autocorrélation de T2M_MAX** : 0,86 à 1 jour, 0,71 à 7 jours, surtout à cause du cycle saisonnier.
- **Autocorrélation de l'anomalie** (T2M_MAX moins la moyenne du jour du calendrier) : 0,64 à 1 jour,
  0,44 à 2 jours, 0,27 à 7 jours. L'information propre au temps qu'il fait s'épuise en 2 à 3 jours :
  les horizons J+5 à J+7 seront proches de la climatologie (risque R2).
- **Conséquence pour les entrées** : décalages de T2M_MAX, T2M, T2M_MIN, RH2M et PRECTOTCORR ;
  WS2M est peu liée à la cible et sera testée sans priorité.
