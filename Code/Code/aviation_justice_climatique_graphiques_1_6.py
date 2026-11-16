from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# Dossiers du projet et fichiers déjà préparés par clean_data.py.
ROOT = Path(__file__).resolve().parent
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# Réglages visuels communs aux deux graphiques.
plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 300,
    "figure.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 15,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "font.size": 10,
    "grid.alpha": 0.15,
})
ORANGE = "#DB783F"
LIGHT = "#8EBAC6"


def save_chart(fig, base_name):
    # Enregistre chaque graphique en PNG haute résolution et en SVG, puis l'affiche.
    fig.savefig(FIGURES / f"{base_name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURES / f"{base_name}.svg", bbox_inches="tight")
    plt.show()


def main():
    # Charge uniquement les deux fichiers nécessaires aux graphiques 1 et 6.
    concentration = pd.read_csv(
        PROCESSED / "article_concentration_clean.csv", encoding="utf-8-sig"
    )
    owid = pd.read_csv(
        PROCESSED / "owid_international_aviation_clean.csv", encoding="utf-8-sig"
    )

    # Graphique 1 : concentration des émissions de CO₂ de l'aviation en 2018.
    top = concentration.loc[
        concentration["population_group"].str.startswith("Top")
    ].iloc[0]
    values = [
        float(top["share_world_population_pct"]),
        float(top["estimated_share_commercial_passenger_aviation_co2_pct"]),
    ]
    labels = ["Share of world population", "Share of aviation passenger CO₂"]

    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.barh([1, 0], values, height=0.55, color=[LIGHT, ORANGE])
    ax.set_yticks([1, 0], labels=labels)
    ax.set_xlim(0, 61)
    ax.set_xlabel("Share (%)")
    for y, v in zip([1, 0], values):
        ax.text(v + 1, y, f"≈{v:g}%", va="center", fontweight="bold", fontsize=13)
    ax.set_title(
        "A very small group accounts for about half of aviation CO₂",
        loc="left",
        pad=15,
    )
    ax.text(
        0,
        -0.36,
        "Top frequent flyers · Global estimates for 2018 · Gössling & Humpe (2020)",
        transform=ax.transAxes,
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout()
    save_chart(fig, "01_concentration_top_frequent_flyers_2018")

    # Graphique 6 : évolution des émissions par habitant des vols internationaux (OWID).
    agg = owid.loc[owid["is_aggregate"] == True].copy()
    series = agg.pivot(
        index="year",
        columns="entity",
        values="co2_international_kg_per_capita_adjusted",
    )
    series = series.reindex(
        columns=["Europe", "North America", "Asia", "South America", "Oceania", "Africa"]
    )

    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    for col in series:
        ax.plot(series.index, series[col], linewidth=2, marker="o", markersize=3.8, label=col)
    ax.axvline(2020, color="#999999", linestyle="--", linewidth=1)
    ax.text(2020.10, ax.get_ylim()[1] * 0.88, "2020", color="#777777", fontsize=9)
    ax.set_xlim(2013, 2024)
    ax.set_xticks(range(2013, 2025, 2))
    ax.set_ylabel("kg CO₂ per person (tourism-adjusted, international flights)")
    ax.set_title("International aviation CO₂ per capita, by region (OWID)", loc="left", pad=15)
    ax.legend(loc="upper left", frameon=False, ncol=3)
    ax.grid(axis="y", alpha=0.2)
    ax.text(
        0,
        -0.19,
        "OWID/OECD/UN Tourism · Africa series is not available for 2023–2024 · NOT comparable in scope to article 2018",
        transform=ax.transAxes,
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout()
    save_chart(fig, "06_owid_international_aviation_timeseries")


if __name__ == "__main__":
    main()
