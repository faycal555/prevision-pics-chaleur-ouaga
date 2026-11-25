"""Exploration des données NASA POWER (jalon J3).

Usage : python src/exploration.py
Lit data/processed/, écrit les figures dans reports/figures/ et les chiffres
clés dans reports/chiffres_exploration.json.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
PROPRE = RACINE / "data" / "processed" / "nasa_power_ouaga_propre.csv"
FIG = RACINE / "reports" / "figures"
SORTIE = RACINE / "reports" / "chiffres_exploration.json"
VARIABLES = ["T2M", "T2M_MAX", "T2M_MIN", "RH2M", "WS2M", "PRECTOTCORR"]
PERIODES = {"entrainement": (1981, 2015), "validation": (2016, 2020), "test": (2021, 2025)}
MOIS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 150, "savefig.bbox": "tight"})
BLEU, ROUGE, GRIS = "#1F3A5F", "#C0392B", "#8A96A3"


def periode(annee):
    for nom, (a, b) in PERIODES.items():
        if a <= annee <= b:
            return nom


def main():
    df = pd.read_csv(PROPRE, parse_dates=["date"])
    df["annee"], df["mois"] = df["date"].dt.year, df["date"].dt.month
    df["periode"] = df["annee"].map(periode)
    FIG.mkdir(parents=True, exist_ok=True)
    c = {}

    # Structure et qualité
    c["lignes"], c["colonnes"] = int(len(df)), len(VARIABLES) + 1
    c["debut"], c["fin"] = str(df["date"].min().date()), str(df["date"].max().date())
    c["manquants"] = int(df[VARIABLES].isna().sum().sum())
    c["describe"] = df[VARIABLES].describe().round(2).to_dict()
    c["mediane_vs_moyenne_tmax"] = [round(df["T2M_MAX"].median(), 2), round(df["T2M_MAX"].mean(), 2)]
    q1, q3 = df["T2M_MAX"].quantile([0.25, 0.75])
    c["iqr_tmax_suspects"] = int(((df["T2M_MAX"] < q1 - 1.5 * (q3 - q1)) | (df["T2M_MAX"] > q3 + 1.5 * (q3 - q1))).sum())
    c["jours_sans_pluie_pct"] = round((df["PRECTOTCORR"] == 0).mean() * 100, 1)

    # Cible : seuil P95 sur l'entraînement seul
    train = df[df["periode"] == "entrainement"]
    seuil = float(train["T2M_MAX"].quantile(0.95))
    c["seuil_p95_entrainement"] = round(seuil, 2)
    c["seuil_p95_tout_fichier"] = round(float(df["T2M_MAX"].quantile(0.95)), 2)
    df["pic"] = (df["T2M_MAX"] > seuil).astype(int)
    c["part_pics_par_periode_pct"] = {p: round(df.loc[df["periode"] == p, "pic"].mean() * 100, 1) for p in PERIODES}
    c["nb_pics_par_periode"] = {p: int(df.loc[df["periode"] == p, "pic"].sum()) for p in PERIODES}
    c["pics_par_mois"] = df.groupby("mois")["pic"].sum().astype(int).to_dict()

    # Saisonnalité et tendance
    c["tmax_moyenne_par_mois"] = df.groupby("mois")["T2M_MAX"].mean().round(1).to_dict()
    annuel = df.groupby("annee")["T2M_MAX"].mean()
    pente = np.polyfit(annuel.index, annuel.values, 1)[0]
    c["tendance_tmax_c_par_decennie"] = round(pente * 10, 2)
    c["tmax_moyenne_par_periode"] = {p: round(df.loc[df["periode"] == p, "T2M_MAX"].mean(), 2) for p in PERIODES}

    # Durée des épisodes de pic (jours consécutifs)
    run = (df["pic"] != df["pic"].shift()).cumsum()
    episodes = df[df["pic"] == 1].groupby(run).size()
    c["episodes_pic"] = {"nombre": int(len(episodes)), "duree_moyenne_j": round(float(episodes.mean()), 1),
                         "duree_max_j": int(episodes.max())}

    # Relations : corrélations et autocorrélation de T2M_MAX
    corr = df[VARIABLES].corr().round(2)
    c["corr_avec_tmax"] = corr["T2M_MAX"].to_dict()
    c["autocorr_tmax"] = {k: round(df["T2M_MAX"].autocorr(k), 3) for k in range(1, 8)}
    anomalie = df["T2M_MAX"] - df.groupby(df["date"].dt.dayofyear)["T2M_MAX"].transform("mean")
    c["autocorr_anomalie_tmax"] = {k: round(anomalie.autocorr(k), 3) for k in range(1, 8)}
    # Persistance des pics : P(pic à J+h | pic à J)
    c["proba_pic_si_pic_J"] = {h: round(float(df["pic"].shift(-h)[df["pic"] == 1].mean()), 2) for h in (1, 3, 7)}

    # ---- Figures ----
    # 1. Distribution de T2M_MAX et seuil
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    ax.hist(df["T2M_MAX"], bins=60, color=BLEU, alpha=.85)
    ax.axvline(seuil, color=ROUGE, lw=1.5)
    ax.text(seuil + .2, ax.get_ylim()[1] * .9, f"P95 = {seuil:.2f} °C", color=ROUGE)
    ax.set(xlabel="T2M_MAX (°C)", ylabel="Nombre de jours", title="Distribution de la température maximale (1981-2025)")
    fig.savefig(FIG / "fig1_distribution_tmax.png"); plt.close(fig)

    # 2. Cycle saisonnier : moyenne mensuelle et nombre de pics
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    m = df.groupby("mois")["T2M_MAX"].agg(["mean", lambda s: s.quantile(.1), lambda s: s.quantile(.9)])
    ax.fill_between(range(1, 13), m.iloc[:, 1], m.iloc[:, 2], color=BLEU, alpha=.15, label="10e-90e centile")
    ax.plot(range(1, 13), m["mean"], color=BLEU, marker="o", ms=3, label="Moyenne")
    ax.axhline(seuil, color=ROUGE, ls="--", lw=1, label="Seuil P95")
    ax2 = ax.twinx()
    ax2.bar(range(1, 13), df.groupby("mois")["pic"].sum(), color=ROUGE, alpha=.25, width=.6)
    ax2.set_ylabel("Jours de pic", color=ROUGE); ax2.spines["top"].set_visible(False)
    ax.set_xticks(range(1, 13), MOIS); ax.set(ylabel="T2M_MAX (°C)", title="Cycle saisonnier et répartition des pics")
    ax.legend(loc="lower left", fontsize=7, frameon=False)
    fig.savefig(FIG / "fig2_saisonnalite.png"); plt.close(fig)

    # 3. Évolution annuelle : Tmax moyenne et part de jours de pic
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    part = df.groupby("annee")["pic"].mean() * 100
    couleurs = [GRIS if a <= 2015 else (BLEU if a <= 2020 else ROUGE) for a in part.index]
    ax.bar(part.index, part.values, color=couleurs)
    ax.axhline(5, color="black", lw=.8, ls=":")
    ax.set(ylabel="Jours de pic (%)", title="Part de jours de pic par an (gris : entraînement, bleu : validation, rouge : test)")
    ax.title.set_size(8.5)
    fig.savefig(FIG / "fig3_pics_par_an.png"); plt.close(fig)

    # 4. Autocorrélation de T2M_MAX et de son anomalie
    fig, ax = plt.subplots(figsize=(5.2, 2.4))
    h = range(1, 8)
    ax.plot(h, [c["autocorr_tmax"][k] for k in h], marker="o", color=BLEU, label="T2M_MAX brute")
    ax.plot(h, [c["autocorr_anomalie_tmax"][k] for k in h], marker="s", color=ROUGE, label="Anomalie (sans saison)")
    ax.set(xlabel="Décalage (jours)", ylabel="Autocorrélation", ylim=(0, 1), title="Mémoire de T2M_MAX d'un jour à l'autre")
    ax.legend(frameon=False, fontsize=7)
    fig.savefig(FIG / "fig4_autocorrelation.png"); plt.close(fig)

    # 5. Matrice de corrélation
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(6), VARIABLES, rotation=45, ha="right"); ax.set_yticks(range(6), VARIABLES)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=6.5,
                    color="white" if abs(corr.iloc[i, j]) > .6 else "black")
    ax.set_title("Corrélations entre variables")
    fig.colorbar(im, ax=ax, fraction=.046)
    fig.savefig(FIG / "fig5_correlations.png"); plt.close(fig)

    SORTIE.write_text(json.dumps(c, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in c.items() if k != "describe"}, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
