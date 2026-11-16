# -*- coding: utf-8 -*-
"""Nettoyer l'export CSV original « Air transport, passengers carried ».

SOURCE : World Bank / ICAO — IS.AIR.PSGR. Aucune requête Internet.
- Les CSV bruts dans data/raw/banque_mondiale/ ne sont jamais modifiés.
- L'export officiel contient 4 lignes de métadonnées en tête, puis les colonnes.
- On conserve les séries WLD (monde) et EUU (Union européenne).
- On n'impute aucune valeur manquante et on ne crée aucune prévision.
"""
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = PROJECT_ROOT / "datas" / "datas" / "inequalities_in_aviation"
RAW = DATA_ROOT / "raw" / "banque_mondiale"
OUT = DATA_ROOT / "processed"
CODES = ("WLD", "EUU")
INDICATEUR = "IS.AIR.PSGR"


def nettoyer():
    candidats = sorted(RAW.glob("API_IS.AIR.PSGR*.csv"))
    if len(candidats) != 1:
        raise FileNotFoundError(
            "Attendu : un seul CSV principal 'API_IS.AIR.PSGR...csv' dans "
            f"{RAW}. Fichiers trouvés : {[p.name for p in candidats]}"
        )
    fichier = candidats[0]
    # Quatre lignes de présentation/metadata avant l'en-tête réel.
    donnees = pd.read_csv(fichier, skiprows=4, encoding="utf-8-sig", low_memory=False)
    requis = {"Country Name", "Country Code", "Indicator Code"}
    if not requis.issubset(donnees.columns):
        raise ValueError(f"En-têtes inattendus dans {fichier.name}: {list(donnees.columns)[:10]}")
    annees = sorted((col for col in donnees.columns if col.isdigit() and len(col) == 4), key=int)
    if not annees:
        raise ValueError("Aucune colonne d'année (ex. '1970') détectée.")
    base = donnees.loc[donnees["Country Code"].isin(CODES)].copy()
    if len(base) != len(CODES) or set(base["Country Code"]) != set(CODES):
        raise ValueError("Il faut exactement une ligne WLD et une ligne EUU dans l'export.")
    if not base["Indicator Code"].eq(INDICATEUR).all():
        raise ValueError("Indicateur incorrect : le fichier doit contenir IS.AIR.PSGR.")
    long = base.melt(
        id_vars=["Country Code", "Indicator Code"],
        value_vars=annees,
        var_name="annee", value_name="passagers",
    )
    long = long.rename(columns={"Country Code": "zone", "Indicator Code": "indicateur"})
    long["annee"] = long["annee"].astype(int)
    long["passagers"] = pd.to_numeric(long["passagers"], errors="coerce")
    long = long[["zone", "annee", "passagers", "indicateur"]]
    if long.duplicated(["zone", "annee"]).any():
        raise ValueError("Doublons détectés dans les années par zone.")
    long = long.sort_values(["zone", "annee"]).reset_index(drop=True)
    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / "passagers_banque_mondiale.csv"
    long.to_csv(destination, index=False)
    print("Source brute :", fichier.name)
    print("Fichier nettoyé :", destination)
    print("Périodes réellement renseignées :")
    print(long.dropna(subset=["passagers"]).groupby("zone")["annee"].agg(["min", "max", "count"]))
    return long


if __name__ == "__main__":
    nettoyer()
