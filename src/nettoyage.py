"""Nettoyage du fichier NASA POWER (Ouagadougou, 1981-2025).

Lit data/raw (jamais modifié) et écrit :
  - data/processed/nasa_power_propre.csv
  - docs/journal_de_nettoyage.csv
Usage : python src/nettoyage.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
BRUT = RACINE / "data" / "raw" / "nasa_power_ouagadougou_1981_2025.csv"
PROPRE = RACINE / "data" / "processed" / "nasa_power_propre.csv"
JOURNAL = RACINE / "docs" / "journal_de_nettoyage.csv"

VARIABLES = ["T2M", "T2M_MAX", "T2M_MIN", "RH2M", "WS2M", "PRECTOTCORR"]
CODE_MANQUANT = -999
MAX_TROU = 2  # jours : on ne comble que les trous courts

journal = []


def noter(etape, defaut, decision, lignes):
    journal.append({"etape": etape, "defaut": defaut,
                    "decision": decision, "lignes_concernees": int(lignes)})


def combler(s, max_trou=MAX_TROU):
    """Interpole seulement les trous d'au plus max_trou jours."""
    manque = s.isna()
    groupe = (manque != manque.shift()).cumsum()
    taille = manque.groupby(groupe).transform("sum")
    remplie = s.interpolate(limit_area="inside")
    return s.where(~(manque & (taille <= max_trou)), remplie)


def main():
    # 1. Lecture en texte : on voit les données telles qu'elles sont
    df = pd.read_csv(BRUT, dtype=str)
    df = df.rename(columns={df.columns[0]: "date"})  # 1re colonne sans nom
    noter(1, "Première colonne sans nom (« Unnamed: 0 »)",
          "Renommée « date »", len(df))

    # 2. Dates
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    n_dates = df["date"].isna().sum()
    noter(2, "Dates non reconnues",
          "Lignes écartées" if n_dates else "Aucune : format AAAA-MM-JJ partout", n_dates)
    df = df.dropna(subset=["date"])

    # 3. Nombres
    for c in VARIABLES:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 4. Codes -999 -> valeurs manquantes
    n999 = int((df[VARIABLES] == CODE_MANQUANT).sum().sum())
    df[VARIABLES] = df[VARIABLES].replace(CODE_MANQUANT, np.nan)
    noter(4, "Codes -999 (valeurs manquantes NASA)",
          "Remplacés par NaN" if n999 else "Aucun code -999 trouvé", n999)

    # 5. Doublons de date
    n_dbl = int(df["date"].duplicated().sum())
    df = df.drop_duplicates("date").sort_values("date")
    noter(5, "Dates en double",
          "Une seule ligne conservée" if n_dbl else "Aucun doublon", n_dbl)

    # 6. Continuité du calendrier
    calendrier = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    absents = len(calendrier.difference(pd.DatetimeIndex(df["date"])))
    df = df.set_index("date").reindex(calendrier).rename_axis("date")
    noter(6, "Jours absents du calendrier",
          "Lignes recréées (valeurs vides)" if absents else "Calendrier complet", absents)

    # 7. Validité physique (on n'utilise PAS l'IQR pour supprimer :
    #    un pic de chaleur est un événement réel, c'est la cible)
    regles = {
        "T2M_MIN > T2M_MAX": df["T2M_MIN"] > df["T2M_MAX"],
        "T2M hors [T2M_MIN, T2M_MAX]": (df["T2M"] > df["T2M_MAX"]) | (df["T2M"] < df["T2M_MIN"]),
        "RH2M hors [0, 100]": (df["RH2M"] < 0) | (df["RH2M"] > 100),
        "PRECTOTCORR < 0": df["PRECTOTCORR"] < 0,
        "WS2M < 0": df["WS2M"] < 0,
    }
    n_inval = 0
    for masque in regles.values():
        k = int(masque.sum())
        n_inval += k
        if k:
            df.loc[masque, VARIABLES] = np.nan
    noter(7, "Valeurs physiquement impossibles (5 règles)",
          "Mises à NaN" if n_inval else "Aucune violation", n_inval)

    # 8. Valeurs extrêmes : signalées (IQR), conservées
    q1, q3 = df["T2M_MAX"].quantile([.25, .75])
    e = q3 - q1
    n_ext = int(((df["T2M_MAX"] < q1 - 1.5 * e) | (df["T2M_MAX"] > q3 + 1.5 * e)).sum())
    noter(8, "T2M_MAX signalées par la règle de l'IQR",
          "Examinées et conservées : températures plausibles, événements réels", n_ext)

    # 9. Manquants : on ne comble que les trous courts
    avant = int(df[VARIABLES].isna().sum().sum())
    for c in VARIABLES:
        df[c + "_origine_vide"] = df[c].isna()
        df[c] = combler(df[c])
    apres = int(df[VARIABLES].isna().sum().sum())
    noter(9, "Valeurs manquantes",
          f"Trous <= {MAX_TROU} jours interpolés ; plus longs laissés vides", avant)
    noter(10, "Manquants restants", "À signaler dans le rapport", apres)

    PROPRE.parent.mkdir(exist_ok=True)
    df.reset_index().to_csv(PROPRE, index=False)
    JOURNAL.parent.mkdir(exist_ok=True)
    pd.DataFrame(journal).to_csv(JOURNAL, index=False)
    print(pd.DataFrame(journal).to_string(index=False))
    print("\nÉcrit :", PROPRE.name, df.shape)


if __name__ == "__main__":
    main()
