from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Resolve data and output paths from this script's folder.
PROJECT_ROOT = Path(__file__).resolve().parent
PROCESSED = PROJECT_ROOT / "data_avion_structure_et_sources" / "data" / "processed"
FIGURES = PROJECT_ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

PROFESSIONS_FILE = PROCESSED / "eurobarometre_professions_pays_2005_2009_2014.csv"
EDUCATION_FILE = PROCESSED / "eurobarometre_education_pays_2005_2009_2014.csv"
WORLD_BANK_FILE = PROCESSED / "passagers_banque_mondiale.csv"

# Fail clearly if the prepared input tables are not available.
missing_files = [
    path
    for path in (PROFESSIONS_FILE, EDUCATION_FILE, WORLD_BANK_FILE)
    if not path.is_file()
]
if missing_files:
    missing = ", ".join(str(path) for path in missing_files)
    raise FileNotFoundError(f"Missing cleaned data files: {missing}")

professions = pd.read_csv(PROFESSIONS_FILE)
education = pd.read_csv(EDUCATION_FILE)
world_bank = pd.read_csv(WORLD_BANK_FILE)

EU28 = set(
    "AT BE BG CY CZ DE DK EE ES FI FR GB GR HR HU IE IT LT LU LV MT NL PL "
    "PT RO SE SI SK".split()
)
EU25 = EU28 - {"BG", "RO", "HR"}

OCCUPATION_LABELS = {
    "Cadres / prof. sup.": "Managers and professionals",
    "Employés / services": "Employees and service workers",
    "Ouvriers / encadrement": "Manual workers and supervisors",
    "Indépendants hors prof. lib.": "Self-employed (excluding liberal professionals)",
}
EDUCATION_LABELS = {
    "≤ 15 ans": "≤ 15 years",
    "16–19 ans": "16–19 years",
    "≥ 20 ans": "≥ 20 years",
}

GREEN = "#136A61"
BLUE = "#2B6493"
PURPLE = "#86559B"
ORANGE = "#C08A34"
PALETTE = [GREEN, BLUE, PURPLE, ORANGE]

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.labelsize": 11,
        "figure.dpi": 125,
        "savefig.dpi": 220,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def save_figure(fig: plt.Figure, name: str) -> None:
    """Save each plot in both raster and vector formats, then display it."""
    fig.savefig(FIGURES / f"{name}.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIGURES / f"{name}.svg", bbox_inches="tight")
    plt.show()
    plt.close(fig)


def median_country_rates_across_waves(
    data: pd.DataFrame, groups: list[str], countries: set[str]
) -> pd.DataFrame:
    """Summarize rates for countries observed in all three survey years."""
    data = data.loc[data["pays"].isin(countries)].copy()
    records = []

    for group in groups:
        group_data = data.loc[data["categorie"] == group]
        country_sets = [
            set(group_data.loc[group_data["annee"] == year, "pays"])
            for year in (2005, 2009, 2014)
        ]
        common_countries = set.intersection(*country_sets)
        if not common_countries:
            continue

        for year in (2005, 2009, 2014):
            rates = group_data.loc[
                (group_data["annee"] == year)
                & group_data["pays"].isin(common_countries),
                "taux_pct",
            ].to_numpy(dtype=float)
            records.append(
                {
                    "categorie": group,
                    "annee": year,
                    "mediane": np.median(rates),
                    "q1": np.percentile(rates, 25),
                    "q3": np.percentile(rates, 75),
                    "nb_pays": len(common_countries),
                }
            )

    return pd.DataFrame(records)


def plot_occupational_access() -> None:
    """Draw Figure 1: air-travel use by occupational group."""
    occupation_groups = [
        "Cadres / prof. sup.",
        "Employés / services",
        "Ouvriers / encadrement",
        "Indépendants hors prof. lib.",
    ]
    summary = median_country_rates_across_waves(
        professions, occupation_groups, EU25
    )
    if summary.empty:
        raise ValueError(
            "No countries have comparable occupation data for all three survey waves."
        )

    fig, axes = plt.subplots(2, 2, figsize=(12.8, 8.5), sharex=True, sharey=True)
    for index, (axis, group) in enumerate(zip(axes.flat, occupation_groups)):
        group_summary = summary.loc[summary["categorie"] == group].sort_values(
            "annee"
        )
        if group_summary.empty:
            axis.set_visible(False)
            continue

        # Show the interquartile range around the median national rate.
        years = group_summary["annee"].to_numpy(dtype=float)
        axis.fill_between(
            years,
            group_summary["q1"].to_numpy(dtype=float),
            group_summary["q3"].to_numpy(dtype=float),
            color=PALETTE[index],
            alpha=0.16,
            linewidth=0,
        )
        axis.plot(
            group_summary["annee"],
            group_summary["mediane"],
            marker="o",
            markersize=8,
            linewidth=2.7,
            color=PALETTE[index],
        )

        # Label each year with its median rate.
        for _, row in group_summary.iterrows():
            axis.annotate(
                f'{row["mediane"]:.1f} %',
                (row["annee"], row["mediane"]),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                color=PALETTE[index],
            )

        country_count = int(group_summary["nb_pays"].iloc[0])
        axis.set_title(
            f"{OCCUPATION_LABELS[group]} (n={country_count} countries)",
            loc="left",
            fontsize=12,
        )
        axis.grid(axis="y", alpha=0.2)
        axis.set_xticks([2005, 2009, 2014])
        axis.set_xlim(2003, 2016)
        axis.set_ylim(0, 100)

    for axis in axes[:, 0]:
        axis.set_ylabel("Respondents who flew (%)")

    fig.suptitle(
        "Access to air travel by occupational group, 2005–2014",
        fontsize=16,
        x=0.05,
        ha="left",
    )
    fig.text(
        0.05,
        0.02,
        "Median national rates — band: 25th to 75th percentiles across countries.",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0.045, 1, 0.95))
    save_figure(fig, "01_professions_evolution_eurobarometre")


def plot_eu_passenger_traffic() -> None:
    """Draw Figure 3: annual air-passenger traffic in the European Union."""
    europe = world_bank.loc[
        (world_bank["zone"] == "EUU") & world_bank["passagers"].notna()
    ].sort_values("annee")
    if europe.empty:
        raise ValueError("No available data for the European Union (EUU).")

    fig, axis = plt.subplots(figsize=(12.7, 5.4))
    passenger_millions = europe["passagers"] / 1e6

    # Plot annual passenger totals and highlight the COVID-19 period.
    axis.plot(
        europe["annee"],
        passenger_millions,
        color=BLUE,
        linewidth=2.8,
    )
    axis.scatter(
        europe["annee"],
        passenger_millions,
        color=BLUE,
        s=11,
        zorder=3,
    )
    axis.axvspan(2019.5, 2021.5, color="#D9DFE7", alpha=0.65, zorder=0)
    axis.set_ylim(bottom=0)
    axis.text(
        2020.5,
        axis.get_ylim()[1] * 0.85,
        "COVID-19",
        color="#525969",
        ha="center",
        fontsize=9,
    )

    axis.set_ylabel("Passengers carried (millions)")
    axis.set_xlabel("Year")
    axis.set_title(
        "Evolution of air passenger traffic in the European Union "
        f"({int(europe['annee'].min())}–{int(europe['annee'].max())})",
        loc="left",
    )
    axis.grid(axis="y", alpha=0.2)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save_figure(fig, "03_european_union_air_passenger_traffic")


def plot_education_heatmap() -> None:
    """Draw Figure 4: education-related air-travel use across EU28 countries."""
    education_groups = ["≤ 15 ans", "16–19 ans", "≥ 20 ans"]
    education_2014 = education.loc[
        education["annee"].eq(2014) & education["pays"].isin(EU28)
    ].copy()
    if education_2014.empty:
        raise ValueError("No 2014 education data are available for the heatmap.")

    # Keep every EU28 country visible, including countries with missing values.
    matrix = education_2014.pivot(
        index="pays", columns="categorie", values="taux_pct"
    ).reindex(columns=education_groups)
    matrix = matrix.reindex(sorted(EU28))

    # Sort countries by the gap between the highest and lowest education groups.
    gaps = matrix["≥ 20 ans"] - matrix["≤ 15 ans"]
    matrix = matrix.loc[gaps.sort_values(ascending=False, na_position="last").index]

    country_names = {
        "AT": "Austria",
        "BE": "Belgium",
        "BG": "Bulgaria",
        "CY": "Cyprus",
        "CZ": "Czechia",
        "DE": "Germany",
        "DK": "Denmark",
        "EE": "Estonia",
        "ES": "Spain",
        "FI": "Finland",
        "FR": "France",
        "GB": "United Kingdom",
        "GR": "Greece",
        "HR": "Croatia",
        "HU": "Hungary",
        "IE": "Ireland",
        "IT": "Italy",
        "LT": "Lithuania",
        "LU": "Luxembourg",
        "LV": "Latvia",
        "MT": "Malta",
        "NL": "Netherlands",
        "PL": "Poland",
        "PT": "Portugal",
        "RO": "Romania",
        "SE": "Sweden",
        "SI": "Slovenia",
        "SK": "Slovakia",
    }

    fig, axis = plt.subplots(figsize=(9.7, 14.3))
    values = matrix.to_numpy(dtype=float)
    masked_values = np.ma.masked_invalid(values)
    color_map = plt.get_cmap("YlGnBu").copy()
    color_map.set_bad("#F1F2F4")
    image = axis.imshow(
        masked_values,
        cmap=color_map,
        vmin=0,
        vmax=100,
        aspect="auto",
    )

    axis.set_xticks(
        np.arange(3),
        [EDUCATION_LABELS[group] for group in education_groups],
    )
    axis.set_yticks(
        np.arange(len(matrix)),
        [country_names[code] for code in matrix.index],
    )
    axis.tick_params(length=0)

    # Label observed rates; mark missing country/group combinations with a dash.
    for row_index in range(len(matrix)):
        for column_index in range(3):
            value = values[row_index, column_index]
            if np.isfinite(value):
                axis.text(
                    column_index,
                    row_index,
                    f"{value:.0f} %",
                    ha="center",
                    va="center",
                    fontsize=8.9,
                    color="white" if value >= 60 else "#183B4A",
                )
            else:
                axis.text(
                    column_index,
                    row_index,
                    "—",
                    ha="center",
                    va="center",
                    fontsize=12,
                    color="#858B96",
                )

    axis.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    axis.set_yticks(np.arange(-0.5, len(matrix), 1), minor=True)
    axis.grid(which="minor", color="white", linewidth=2.2)
    axis.tick_params(which="minor", length=0)
    axis.set_title(
        "Air-travel use and age at the end of full-time education\n"
        "28 EU member states — 2014",
        loc="left",
        fontsize=15,
        pad=18,
    )
    colorbar = fig.colorbar(image, ax=axis, shrink=0.66, pad=0.04)
    colorbar.set_label("Respondents who used air travel (%)")
    fig.text(
        0.12,
        0.015,
        "GESIS / Eurobarometer 82.1, QA1 + D8; weighted using W1. "
        "—: insufficient or missing observations.",
        fontsize=8.5,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save_figure(fig, "04_heatmap_education_28_pays_2014")


def main() -> None:
    plot_occupational_access()
    plot_eu_passenger_traffic()
    plot_education_heatmap()


if __name__ == "__main__":
    main()
