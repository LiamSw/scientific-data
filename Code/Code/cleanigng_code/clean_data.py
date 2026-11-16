"""Nettoyage indépendant des données du projet « Aviation & justice climatique ».

Exécuter depuis le dossier du projet :
    python "cleaning code/clean_data.py"

Lit UNIQUEMENT data/raw/, écrit UNIQUEMENT data/processed/.
Le notebook ne lance jamais ce script et ne lit jamais les données brutes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = Path(__file__).resolve().parents[3] / "datas" / "datas" / "climate_justice" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)
ARTICLE_DOI = "https://doi.org/10.1016/j.gloenvcha.2020.102194"
IPCC_URL = "https://www.ipcc.ch/report/ar6/wg2/figures/summary-for-policymakers/figure-spm-2/"
OWID_URL = "https://ourworldindata.org/grapher/per-capita-co2-international-flights-adjusted"


def load_csv(name: str) -> pd.DataFrame:
    source = RAW / name
    if not source.is_file():
        raise FileNotFoundError(f"Fichier brut manquant : {source}")
    # utf-8-sig reconnaît aussi bien les fichiers avec que sans BOM.
    return pd.read_csv(source, encoding="utf-8-sig")


def clean_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les espaces sans transformer les valeurs manquantes en chaînes."""
    result = df.copy()
    for name in result.select_dtypes(include=["object", "string"]).columns:
        result[name] = result[name].map(
            lambda v: re.sub(r"\s+", " ", v).strip() if isinstance(v, str) else v
        )
        result[name] = result[name].replace("", pd.NA)
    return result


def check_columns(df: pd.DataFrame, expected: list[str], file_name: str) -> None:
    absent = set(expected) - set(df.columns)
    if absent:
        raise ValueError(f"{file_name} : colonnes absentes : {sorted(absent)}")


def convert_numbers(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for column in cols:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def check_unique(df: pd.DataFrame, cols: list[str], name: str) -> None:
    if df.duplicated(cols).any():
        sample = df.loc[df.duplicated(cols, keep=False), cols].head()
        raise ValueError(f"Doublons de clé dans {name}:\n{sample}")


def check_percent(df: pd.DataFrame, cols: list[str], name: str) -> None:
    for col in cols:
        invalid = df[col].notna() & ~df[col].between(0, 100)
        if invalid.any():
            raise ValueError(f"Pourcentage hors [0,100]: {name}/{col}")


def write(df: pd.DataFrame, name: str, info: dict, manifest: dict) -> None:
    df.to_csv(PROCESSED / name, index=False, encoding="utf-8-sig", na_rep="")
    manifest[name] = {"rows": len(df), "columns": df.columns.tolist(), **info}
    print(f"{name}: {len(df)} lignes, {df.shape[1]} colonnes")


def ipcc_confidence_group(value: object) -> str:
    if pd.isna(value):
        return "Not reported"
    value = str(value)
    exact = {"Very high", "High", "Medium", "Low", "Not assessed", "Not applicable",
             "Evidence limited; insufficient"}
    if value in exact:
        return value
    return "Qualified / combined"  # Ex. 'High to very high' ; ne pas les arrondir.


def ipcc_impact_group(value: object) -> str:
    if pd.isna(value):
        return "Not specified (ecosystem panel)"
    known = {
        "Increase in adverse impacts",
        "Increasing adverse and positive impacts",
        "Evidence limited; insufficient",
        "Not assessed",
        "Not applicable",
    }
    if value not in known:
        raise ValueError(f"Nouvelle modalité d'impact GIEC non reconnue : {value}")
    return str(value)


def main() -> None:
    manifest: dict = {"project": "Aviation and climate injustice", "cleaning_pipeline": "cleaning code/clean_data.py", "files": {}}
    output = manifest["files"]

    # Données agrégées estimées par Gössling & Humpe, 2018.
    regions = clean_string_columns(load_csv("aviation_emissions_regions_2018_article.csv"))
    check_columns(regions, ["region", "year", "rpk_global_share_pct", "rpk_per_capita",
                            "co2_commercial_passenger_mt", "co2_commercial_passenger_kg_per_capita"], "régions")
    regions = convert_numbers(regions, ["year", "rpk_global_share_pct", "rpk_per_capita",
                                       "co2_commercial_passenger_mt", "co2_commercial_passenger_kg_per_capita"])
    check_unique(regions, ["region", "year"], "régions")
    check_percent(regions, ["rpk_global_share_pct"], "régions")
    if not regions["year"].eq(2018).all():
        raise ValueError("L'article régional devrait porter sur 2018")
    if (regions["co2_commercial_passenger_mt"].dropna() < 0).any():
        raise ValueError("Émissions négatives inattendues")
    if regions["co2_commercial_passenger_kg_per_capita"].isna().sum() != 1:
        raise ValueError("Vérifier le manque attendu pour Rest of world")
    regions = regions.sort_values("region").reset_index(drop=True)
    write(regions, "article_regions_clean.csv", {
        "source": ARTICLE_DOI, "reference": "Tables 3 et 4", "year": 2018,
        "warning": "Estimations régionales. Rest of world : kg/habitant absent, non imputé."}, output)

    income = clean_string_columns(load_csv("aviation_participation_groupes_revenu_2018_article.csv"))
    required = ["income_country_group", "year", "population_million",
                "airline_passenger_movements_million", "passenger_movements_per_capita",
                "estimated_population_who_flew_pct", "estimated_unique_flyers_million"]
    check_columns(income, required, "groupes de revenu")
    income = convert_numbers(income, required[1:])
    check_unique(income, ["income_country_group", "year"], "groupes de revenu")
    check_percent(income, ["estimated_population_who_flew_pct"], "groupes de revenu")
    income_order = ["Low income", "Lower middle income", "Upper middle income", "High income"]
    income["income_country_group"] = pd.Categorical(income["income_country_group"], categories=income_order, ordered=True)
    if income["income_country_group"].isna().any():
        raise ValueError("Catégorie de revenu non reconnue")
    income = income.sort_values("income_country_group").reset_index(drop=True)
    income["income_country_group"] = income["income_country_group"].astype(str)
    write(income, "article_income_clean.csv", {"source": ARTICLE_DOI, "reference": "Table 2", "year": 2018,
          "warning": "Le % de voyageurs est modélisé, PAS directement mesuré; mouvements != voyageurs uniques."}, output)

    concentration = clean_string_columns(load_csv("aviation_concentration_emissions_2018_article.csv"))
    required = ["population_group", "year", "share_world_population_pct",
                "estimated_share_commercial_passenger_aviation_co2_pct", "estimate_status"]
    check_columns(concentration, required, "concentration")
    concentration = convert_numbers(concentration, required[1:4])
    check_unique(concentration, ["population_group", "year"], "concentration")
    check_percent(concentration, required[2:4], "concentration")
    if len(concentration) != 2 or abs(concentration["share_world_population_pct"].sum()-100) > 0.001:
        raise ValueError("Les deux groupes devraient représenter 100 % de la population")
    if abs(concentration["estimated_share_commercial_passenger_aviation_co2_pct"].sum()-100) > 0.001:
        raise ValueError("Les deux groupes devraient représenter 100 % des émissions")
    concentration = concentration.sort_values("share_world_population_pct").reset_index(drop=True)
    write(concentration, "article_concentration_clean.csv", {"source": ARTICLE_DOI, "reference": "Section 4.4", "year": 2018,
          "warning": "~1 % / ~50 % : estimation des auteurs ; 99 % / 50 % : complément arithmétique."}, output)

    # Classification catégorielle ; NE PAS fabriquer des scores d'intensité des effets.
    ipcc = clean_string_columns(load_csv("GIEC_AR6_WGII_SPM2_long_clean.csv"))
    check_columns(ipcc, ["figure", "region", "indicator", "impact", "confidence_in_attribution"], "GIEC")
    check_unique(ipcc, ["figure", "region", "indicator"], "GIEC")
    if not ipcc["figure"].isin(["SPM2a", "SPM2b"]).all():
        raise ValueError("Identifiant de panneau GIEC inattendu")
    ipcc["confidence_class"] = ipcc["confidence_in_attribution"].map(ipcc_confidence_group)
    ipcc["impact_class"] = ipcc["impact"].map(ipcc_impact_group)
    ipcc = ipcc.sort_values(["figure", "region", "indicator"]).reset_index(drop=True)
    write(ipcc, "ipcc_spm2_clean.csv", {"source": IPCC_URL, "reference": "IPCC AR6 WGII SPM.2 a,b (2022)",
         "warning": "La confiance dans l'attribution n'est PAS la sévérité des impacts. Valeurs vides préservées."}, output)

    # Donnée textuelle indépendante de la Figure SPM.2, dans le paragraphe B.2.4 du GIEC.
    # La valeur 1 est une BASE NORMALISÉE, pas un taux de mortalité réel mesuré.
    mortality_path = RAW / "ipcc_mortality_relative_2010_2020.csv"
    if mortality_path.is_file():
        mortality = clean_string_columns(load_csv(mortality_path.name))
        check_columns(mortality, ["group", "relative_mortality_index", "period", "status", "source_section"], "GIEC mortalité")
        mortality = convert_numbers(mortality, ["relative_mortality_index"])
        check_unique(mortality, ["group", "period"], "GIEC mortalité")
        if (mortality["relative_mortality_index"] < 0).any():
            raise ValueError("Indices de mortalité négatifs")
        if set(mortality["group"]) != {"Very low vulnerability", "Highly vulnerable"}:
            raise ValueError("Groupes de vulnérabilité inattendus")
        write(mortality, "ipcc_mortality_relative_clean.csv", {
            "source": "https://www.ipcc.ch/report/ar6/wg2/chapter/summary-for-policymakers/",
            "reference": "AR6 WGII SPM B.2.4 (2022)", "period": "2010–2020",
            "warning": "1=indice de référence normalisé; 15=rapport de mortalité publié. PAS des taux absolus de mortalité ni des décès attribués aux seules émissions de l'aviation."}, output)
    else:
        mortality_output = PROCESSED / "ipcc_mortality_relative_clean.csv"
        if mortality_output.exists():
            mortality_output.unlink()
        print(f"[Option] {mortality_path.name} absent de data/raw : graphique de mortalité non produit.")

    # OWID : métrique spécifique du CO2 des vols internationaux, ajustée au tourisme.
    owid = clean_string_columns(load_csv(
        "wordl-bank-per-capita-co2-international-flights-adjusted/"
        "per-capita-co2-international-flights-adjusted.csv"
    ))
    emissions_col = "Per capita CO₂ emissions from international flights, international tourism-adjusted"
    check_columns(owid, ["Entity", "Code", "Year", emissions_col, "World region according to OWID"], "OWID")
    owid = owid.rename(columns={
        "Entity": "entity", "Code": "iso3_or_owid", "Year": "year", emissions_col: "co2_international_kg_per_capita_adjusted",
        "World region according to OWID": "world_region"})
    owid = convert_numbers(owid, ["year", "co2_international_kg_per_capita_adjusted"])
    owid = owid.dropna(subset=["entity", "iso3_or_owid", "year", "co2_international_kg_per_capita_adjusted"])
    owid["year"] = owid["year"].astype("int64")
    owid["is_aggregate"] = owid["iso3_or_owid"].astype(str).str.startswith("OWID_")
    check_unique(owid, ["iso3_or_owid", "year"], "OWID")
    if (owid["co2_international_kg_per_capita_adjusted"] < 0).any():
        raise ValueError("OWID : émissions négatives")
    owid = owid.sort_values(["entity", "year"]).reset_index(drop=True)
    write(owid, "owid_international_aviation_clean.csv", {"source": OWID_URL, "years": [2013,2024],
          "unit": "kg CO2 par habitant", "warning": "Émissions des vols internationaux ajustées au tourisme; années incomplètes, différentes du périmètre des données de l'article."}, output)

    europe_2024 = owid.loc[(owid["year"] == 2024) & (owid["world_region"] == "Europe") & (~owid["is_aggregate"])].copy()
    europe_2024 = europe_2024.sort_values("co2_international_kg_per_capita_adjusted", ascending=False).reset_index(drop=True)
    write(europe_2024, "owid_europe_2024_available_clean.csv", {"source": OWID_URL, "year": 2024,
          "warning": f"Sous-ensemble disponible : {len(europe_2024)} pays, classement NON exhaustif de l'Europe."}, output)

    # Optionnel : si la base Eurostat de l'analyse précédente est fournie.
    eurostat_input = RAW / "europe_air_travel_2025_sans_faible_fiabilite.csv"
    target = PROCESSED / "eurostat_2025_vs_owid_2024_clean.csv"
    if eurostat_input.exists():
        eurostat = clean_string_columns(pd.read_csv(eurostat_input, encoding="utf-8-sig", dtype={"geo": "string"}))
        check_columns(eurostat, ["geo", "air_total_pct"], "Eurostat")
        eurostat["air_total_pct"] = pd.to_numeric(eurostat["air_total_pct"], errors="coerce")
        check_percent(eurostat, ["air_total_pct"], "Eurostat")
        if "included_in_strict_analysis" in eurostat.columns:
            valid = eurostat["included_in_strict_analysis"].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])
            eurostat = eurostat.loc[valid].copy()
        iso2to3 = {"AT":"AUT", "BE":"BEL", "BG":"BGR", "CY":"CYP", "DE":"DEU", "DK":"DNK",
            "EE":"EST", "EL":"GRC", "ES":"ESP", "FI":"FIN", "FR":"FRA", "HR":"HRV", "HU":"HUN",
            "IE":"IRL", "IT":"ITA", "LT":"LTU", "LU":"LUX", "LV":"LVA", "MT":"MLT", "NL":"NLD",
            "NO":"NOR", "PL":"POL", "PT":"PRT", "RO":"ROU", "RS":"SRB", "SE":"SWE", "SI":"SVN", "SK":"SVK"}
        eurostat["iso3_or_owid"] = eurostat["geo"].map(iso2to3)
        check_unique(eurostat, ["geo"], "Eurostat")
        eurostat = eurostat.dropna(subset=["iso3_or_owid", "air_total_pct"])
        merged = eurostat[["geo", "iso3_or_owid", "air_total_pct"]].merge(
            europe_2024[["iso3_or_owid", "entity", "co2_international_kg_per_capita_adjusted"]],
            on="iso3_or_owid", how="inner", validate="one_to_one")
        merged.insert(0,"year_aviation_participation",2025)
        merged.insert(1,"year_co2_adjusted",2024)
        write(merged, target.name, {"sources": ["Eurostat 2025 (fichier ajouté)", OWID_URL],
            "warning": "Deux années et deux définitions distinctes. Association exploratoire uniquement."}, output)
        print(f"Couverture Europe (intersection Eurostat/OWID) : {len(merged)} pays")
    else:
        if target.exists():
            target.unlink()  # Évite de garder un vieux résultat facultatif lors du nettoyage.
        print("[Option] Eurostat 2025 absent de data/raw : scatter Eurostat-OWID non préparé.")

    (PROCESSED / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nNettoyage terminé : aucune modification des fichiers dans data/raw/.")

if __name__ == "__main__":
    main()
