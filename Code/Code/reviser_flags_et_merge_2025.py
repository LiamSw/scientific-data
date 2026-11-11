"""Nettoyage transparent de trois exports Eurostat 2025.

Crée deux tableaux pour analyses de sensibilite :
 - europe_air_travel_2025_avec_flags.csv (29 pays, tous les statuts conservés)
 - europe_air_travel_2025_sans_faible_fiabilite.csv (28 pays, exclusions `u` sur les variables utilisees)

À lancer dans le dossier des trois CSV bruts : python reviser_flags_et_merge_2025.py
Nécessite pandas.
"""

from pathlib import Path
import pandas as pd

# Dossier contenant les trois fichiers CSV
root = Path(r"C:\Users\desca\OneDrive - UCL\Erasmus cours - M2 Q1\scientific data visualization\final project\donnees_avion")

# Chargement des trois fichiers
air = pd.read_csv(root / "Persons by frequency of air travel in the last 12 months, household composition, degree of urbanisation and risk of poverty or social exclusion.csv", low_memory=False)

gini = pd.read_csv(root / "Gini coefficient of equivalised disposable income by age.csv", low_memory=False)

gdp = pd.read_csv(root / "Gross domestic product (GDP) and main components per capita - annual data.csv", low_memory=False)

# Dictionnaire utilisé par le reste du programme
raw = {
    'air': air,
    'gini': gini,
    'gdp': gdp
}

aggregates = {'EU', 'EU27_2020', 'EA', 'EA19', 'EA20', 'EA21'}


# 1. Valeurs comparables : meme annee, memes definitions. Les flags restent disponibles.
air = raw['air'].loc[
    (raw['air']['TIME_PERIOD'] == 2025) &
    (raw['air']['geo'].isin(aggregates) == False) &
    (raw['air']['deg_urb'] == 'TOTAL') &
    (raw['air']['hhcomp'] == 'TOTAL') &
    (raw['air']['frequenc'] == 'NM12') &
    (raw['air']['yn_arope'].isin(['TOTAL','YES_AROPE','NO_AROPE'])) &
    (raw['air']['unit'] == 'PC'),
    ['geo','yn_arope','OBS_VALUE','OBS_FLAG']
].copy()
assert not air.duplicated(['geo','yn_arope']).any(), 'Doublons dans la selection air'

# 2. Pourcentages : nombre de residents avec >= 1 vol = 100 - part sans vol
pcts = air.pivot(index='geo', columns='yn_arope', values='OBS_VALUE')
flags = air.pivot(index='geo', columns='yn_arope', values='OBS_FLAG').fillna('')
air_wide = pd.DataFrame({
    'geo': pcts.index,
    'air_total_pct': 100-pcts['TOTAL'],
    'air_arope_pct': 100-pcts['YES_AROPE'],
    'air_non_arope_pct': 100-pcts['NO_AROPE'],
    'flag_air_total': flags['TOTAL'],
    'flag_air_arope': flags['YES_AROPE'],
    'flag_air_non_arope': flags['NO_AROPE'],
}).reset_index(drop=True)
air_wide['social_gap_pp'] = air_wide['air_non_arope_pct']-air_wide['air_arope_pct']

# 3. Gini : GINI_HND est la seule modalite de statinfo dans cet export.
gini = raw['gini'].loc[
    (raw['gini']['TIME_PERIOD'] == 2025) &
    (raw['gini']['age'] == 'TOTAL') &
    (raw['gini']['statinfo'] == 'GINI_HND') &
    (~raw['gini']['geo'].isin(aggregates)),
    ['geo','OBS_VALUE','OBS_FLAG']
].rename(columns={'OBS_VALUE':'gini','OBS_FLAG':'flag_gini'})
assert not gini.duplicated('geo').any(), 'Doublons dans la selection Gini'

# 4. PIB : niveau du PIB (B1GQ) par habitant, unité PPS et non index UE=100.
gdp = raw['gdp'].loc[
    (raw['gdp']['TIME_PERIOD'] == 2025) &
    (raw['gdp']['na_item'] == 'B1GQ') &
    (raw['gdp']['unit'] == 'CP_PPS_EU27_2020_HAB') &
    (~raw['gdp']['geo'].isin(aggregates)),
    ['geo','OBS_VALUE','OBS_FLAG']
].rename(columns={'OBS_VALUE':'gdp_per_capita_pps','OBS_FLAG':'flag_gdp'})
assert not gdp.duplicated('geo').any(), 'Doublons dans la selection PIB'

# 5. Fusion par code pays. Un pays seulement si les 3 sources sont presentes.
merged = air_wide.merge(gini, on='geo', how='inner', validate='one_to_one')
merged = merged.merge(gdp, on='geo', how='inner', validate='one_to_one')
for key in ['air_total_pct','air_arope_pct','air_non_arope_pct','social_gap_pp','gini','gdp_per_capita_pps']:
    merged[key] = pd.to_numeric(merged[key], errors='coerce')
merged = merged.dropna(subset=['air_total_pct','air_arope_pct','air_non_arope_pct','gini','gdp_per_capita_pps'])
for key in ['air_total_pct','air_arope_pct','air_non_arope_pct']:
    assert merged[key].between(0,100).all(), f'Valeurs hors 0-100 : {key}'
assert merged['gini'].between(0,100).all()

# 6. Les flags sont des attributs de chaque statistique, pas du pays entier.
# N'exclure la valeur `u` que lorsqu'elle touche une variable effectivement analysee.
flagcols = ['flag_air_total','flag_air_arope','flag_air_non_arope','flag_gini','flag_gdp']
merged[flagcols] = merged[flagcols].fillna('')
merged['has_low_reliability_used'] = merged[flagcols].apply(
    lambda row: any('u' in str(val).lower() for val in row), axis=1
)
merged['included_in_strict_analysis'] = ~merged['has_low_reliability_used']

merged.sort_values('geo').to_csv(root / 'europe_air_travel_2025_avec_flags.csv', index=False)
strict = merged.loc[merged['included_in_strict_analysis']].sort_values('geo')
strict.to_csv(root / 'europe_air_travel_2025_sans_faible_fiabilite.csv', index=False)

print(f"Pays, toutes observations : {len(merged)}")
print(f"Pays, analyse stricte : {len(strict)}")
print('Pays exclus pour faible fiabilite :', merged.loc[~merged['included_in_strict_analysis'], 'geo'].tolist())
print('Les valeurs provisoires (p), estimees (e) et ruptures de serie (b) ont ete conservees et signalees.')
