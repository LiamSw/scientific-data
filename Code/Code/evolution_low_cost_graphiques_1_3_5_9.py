from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

# Les CSV doivent être placés dans le dossier « data », à côté de ce script.
BASE = Path(__file__).resolve().parent
DATA = BASE / 'data'
FIG = BASE / 'figures'
FIG.mkdir(exist_ok=True)

sns.set_theme(style='whitegrid', context='talk')
plt.rcParams.update({
    'figure.figsize': (11.5, 5.7),
    'savefig.dpi': 210,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.constrained_layout.use': True,
})

COLORS = {
    'Low-cost': '#169D92',
    'Mainline': '#344B79',
    'Regional': '#9F86C0',
    'Other': '#BEC5CE',
    'Ryanair Group': '#168D81',
    'easyJet': '#D97131',
}


def save_figure(fig, name):
    # Export PNG et SVG, puis affichage du graphique.
    fig.savefig(FIG / f'{name}.png', dpi=210, bbox_inches='tight')
    fig.savefig(FIG / f'{name}.svg', bbox_inches='tight')
    plt.show()


# Chargement des données utiles aux quatre graphiques.
segments = pd.read_csv(DATA / 'eurocontrol_segments_2024_2025.csv')
operators = pd.read_csv(DATA / 'eurocontrol_operators_2019_2025.csv')
routes = pd.read_csv(DATA / 'airport_routes_1993_2019_observed.csv')


# Figure 1 : évolution de la part des low-cost (1998–2025).
# Données annuelles regroupées par source
lcc_full = pd.read_csv(
    DATA / 'eurocontrol_lcc_annual_1998_2025_by_source.csv'
)

fig, ax = plt.subplots(figsize=(12, 5.5))

share_color = COLORS['Low-cost']

source_groups = [
    'snapshot_1998_2018',
    'standard_inputs_2019_2022',
    'prr_2024_2025'
]

for index, group in enumerate(source_groups):
    subset = lcc_full[
        lcc_full['source_group'] == group
    ].sort_values('year')

    ax.plot(
        subset['year'],
        subset['lcc_share_pct'],
        color=share_color,
        linewidth=2.5,
        marker='o',
        markersize=5,
        label='Low-cost share' if index == 0 else '_nolegend_'
    )

# Affichage des pourcentages pour certaines années
annotation_offsets = {
    1998: (0, 13),
    2000: (0, 13),
    2005: (0, 13),
    2010: (0, 13),
    2015: (0, 13),
    2018: (-12, 14),
    2019: (12, 14),
    2022: (0, 14),
    2024: (-10, 15),
    2025: (10, 15)
}

for year, offset in annotation_offsets.items():
    row = lcc_full[lcc_full['year'] == year].iloc[0]

    ax.annotate(
        f"{row['lcc_share_pct']:.1f}%",
        (year, row['lcc_share_pct']),
        xytext=offset,
        textcoords='offset points',
        ha='center',
        fontsize=9,
        color=share_color
    )

# Délimitations des différentes sources de données
for index, year in enumerate([2018, 2019, 2022, 2024]):
    ax.axvline(
        year,
        color='#A6ADB4',
        linestyle='--',
        linewidth=1.1,
        alpha=0.8,
        zorder=1,
        label='Dataset boundaries' if index == 0 else '_nolegend_'
    )

# Année 2023 absente des données
ax.axvspan(2022.5, 2023.5, color='gray', alpha=0.10)
ax.text(2023, 12, 'No annual data\n(2023)', ha='center', va='center', fontsize=9, color='#65727D')

ax.set(
    xlabel='Year',
    ylabel='Share of European IFR flights (%)',
    title='The rise of low-cost airlines in Europe (1998–2025)'
)

ax.set_xticks([2000, 2005, 2010, 2015, 2020, 2025])
ax.set_xlim(1997, 2026.5)
ax.set_ylim(0, 42)

ax.legend(loc='upper left', fontsize=9)

save_figure(fig, '01_lcc_market_share_1998_2025_complete')


# Figure 3 : part des segments de marché en 2025.
d=segments.query('year==2025').sort_values('share_pct')
pal=[COLORS.get(x, '#BBC5D0') for x in d.segment]
fig,ax=plt.subplots(figsize=(11,6.5))
bar=ax.barh(d.segment,d.share_pct,color=pal)
for b in bar:
    ax.text(b.get_width()+.35,b.get_y()+b.get_height()/2,f'{b.get_width():.1f}%',va='center',fontsize=11)
ax.set_xlim(0,43)
ax.set(xlabel='Share of all IFR flights (%)',ylabel='',title='2025: low-cost is the largest market segment')
ax.grid(False)
save_figure(fig,'03_market_segments_2025')


# Figure 5 : évolution du nombre de vols par compagnie (2019–2025).
selection=['Ryanair Group','easyJet Group','Wizz Air Group','Turkish Airlines Group',
           'Lufthansa Airlines','Air France Group','Vueling','Norwegian Group']
p=operators[operators.airline.isin(selection)].sort_values('daily_2025',ascending=True)
fig,ax=plt.subplots(figsize=(11.6,7))
for r in p.itertuples():
    c=COLORS['Low-cost'] if r.category_for_chart=='Low-cost' else COLORS['Mainline']
    ax.plot([2019,2025],[r.daily_2019_derived,r.daily_2025],color=c,lw=2.6,alpha=.82)
    ax.scatter([2019,2025],[r.daily_2019_derived,r.daily_2025],color=c,s=50)
    label_y = r.daily_2025 + {'easyJet Group':95,'Turkish Airlines Group':-95, 'Lufthansa Airlines':40, 'Air France Group':-40}.get(r.airline,0)
    ax.text(2025.15,label_y,f'{r.airline}  ({r.delta_2025_vs_2019:+,}/day)',color=c,va='center',fontsize=10)
ax.set(xlim=(2018.2,2031),ylim=(0,3550),xticks=[2019,2025],ylabel='Average daily flights',title='Airline operators: change in flight activity (2019 → 2025)')
ax.grid(axis='x',visible=False)
ax.legend(handles=[Line2D([0],[0],color=COLORS['Low-cost'],lw=3,label='Low-cost'),
                   Line2D([0],[0],color=COLORS['Mainline'],lw=3,label='Mainline')],loc='upper left',fontsize=10)
fig.text(.01,-.03,'Source: EUROCONTROL PRR 2025, Fig. 2-12. 2019 derived as 2025 minus reported absolute change. Colors classify selected operators.',fontsize=9)
save_figure(fig,'05_airline_growth_slope_2019_2025')

# Figure 9 : évolution des liaisons origine–destination déclarées (1993–2019).
fig,ax=plt.subplots(figsize=(11.7,5.3))
ax.plot(routes.year,routes.observed_route_pairs,color=COLORS['Mainline'],marker='o',ms=3,lw=2.8)
ax.set(xlabel='Year',ylabel='Number of origin–destination pairs with reported positive traffic',
       title='Reported airport connections over time (exploratory, 1993–2019)')
ax.set_ylabel(ax.get_ylabel(), fontsize=11)
save_figure(fig,'09_airport_connection_coverage_1993_2019')
