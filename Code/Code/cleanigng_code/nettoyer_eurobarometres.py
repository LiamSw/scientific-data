# -*- coding: utf-8 -*-
"""Harmonisation prudente des microdonnées GESIS Eurobaromètre 2005, 2009, 2014.

Source d'entrée: archives .dta ou .sav OFFICIELLES, non modifiées, placées dans data/raw/.
La fonction échoue si des colonnes cruciales sont introuvables ou ambiguës.
Nous n'inventons ni données ni pondérations.
"""
from __future__ import annotations
import json
import re
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = PROJECT_ROOT / "datas" / "datas" / "inequalities_in_aviation"
RAW = DATA_ROOT / "raw" / "eurobarometre"
OUT = DATA_ROOT / "processed"
WAVES={
  2005:{'id':'ZA4234','dossier':'ZA4234_2005','air':'v108','profession':'v371','education':'v365'},
  2009:{'id':'ZA4972','dossier':'ZA4972_2009','air':'v390','profession':'v136','education':None},
  2014:{'id':'ZA5930','dossier':'ZA5930_2014','air':'qa1_4','profession':'d15a','education':None,'poids':'w1'},
}
# Ensembles d'États membres à la date de l'enquête. Royaume-Uni inclus.
EU28=set('AT BE BG CY CZ DE DK EE ES FI FR GB GR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK'.split())
EU25=EU28-{'BG','RO','HR'}
EU27=EU28-{'HR'}


def extraire_archives(dossier):
    """Extrait seulement les fichiers d'analyse lisibles, sans effacer les ZIP d'origine."""
    for archive in dossier.rglob('*.zip'):
        with zipfile.ZipFile(archive) as z:
            candidates=[x for x in z.infolist() if not x.is_dir() and x.filename.lower().endswith(('.sav','.dta'))]
            for info in candidates:
                # Empêche les chemins traversants contenus dans des archives ZIP
                destination=(dossier/info.filename).resolve()
                if not destination.is_relative_to(dossier.resolve()):
                    continue
                if destination.exists(): continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, destination.open('wb') as dst:
                    import shutil
                    shutil.copyfileobj(src, dst)


def charger_microdonnees(annee):
    cfg=WAVES[annee]
    dossier=RAW/cfg['dossier']
    dossier.mkdir(parents=True,exist_ok=True)
    extraire_archives(dossier)
    fichiers=sorted(dossier.rglob('*.dta'))+sorted(dossier.rglob('*.sav'))
    # Une seule base de répondants par vague: si plusieurs, choix manuel obligatoire.
    if not fichiers:
        raise FileNotFoundError(f'Eurobaromètre {annee} : aucun .dta ou .sav dans {dossier}. Télécharge la microdonnée officielle GESIS (connexion gratuite).')
    # archives peuvent contenir plusieurs formats -> choisir dta si une seule; ignorer les doublons sav
    dta=[p for p in fichiers if p.suffix.lower()=='.dta']
    sav=[p for p in fichiers if p.suffix.lower()=='.sav']
    candidats=dta if dta else sav
    if len(candidats)!=1:
        raise ValueError(f'Plusieurs fichiers {candidats} pour {annee}. Ne conserve que la bonne microdonnée dans ce dossier.')
    fichier=candidats[0]
    if fichier.suffix.lower()=='.dta':
        with pd.io.stata.StataReader(fichier, convert_categoricals=False) as reader:
            df=reader.read()
            labels=reader.variable_labels()  # labels descriptifs des variables
            labels_valeurs=reader.value_labels()
            # Pour obtenir la correspondance variable -> table de valeurs labelisées, chercher dans les métadonnées via pyreadstat si possible.
        try:
            import pyreadstat
            _,meta=pyreadstat.read_dta(str(fichier),metadataonly=True)
            var_valeurs=getattr(meta,'variable_value_labels',{}) or {}
        except ImportError:
            var_valeurs={}
    else:
        try: import pyreadstat
        except ImportError as e:
            raise ImportError('Un fichier .sav nécessite: pip install pyreadstat (ou télécharge la version .dta depuis GESIS).') from e
        df,meta=pyreadstat.read_sav(str(fichier),apply_value_formats=False)
        labels=dict(zip(meta.column_names,meta.column_labels))
        var_valeurs=getattr(meta,'variable_value_labels',{}) or {}
    df.columns=[str(c).lower() for c in df.columns]
    labels={str(k).lower():str(v or '') for k,v in labels.items()}
    var_valeurs={str(k).lower():v for k,v in var_valeurs.items()}
    return df,labels,var_valeurs,fichier


def trouver_colonne(df,labels,annee,role,config=None):
    """Détection par libellé, jamais en devinant une variable QA1 qui ne serait pas l'avion."""
    config=config or {}
    explicite=config.get(str(annee),{}).get(role)
    if explicite:
        if str(explicite).lower() not in df.columns: raise ValueError(f'Colonne configurée inexistante {role}: {explicite}')
        return str(explicite).lower()
    ident=WAVES[annee].get(role)
    if ident and ident in df.columns:
        lab=labels.get(ident,'')
        garde={'air':r'\bAIR\b', 'profession':r'\bD\.?15\s?A\b|OCCUPATION OF RESPONDENT',
               'education':r'\bD\.?8\b|AGE EDUCATION'}[role]
        if lab and not re.search(garde,lab,re.I):
            raise ValueError(f'Variable {ident} inattendue pour {role}: {lab}. Vérifie ton codebook.')
        return ident
    candidats=[]
    for c in df.columns:
        label=labels.get(c,'')
        if role=='air':
            # Tous les champs doivent mentionner la question QA1/QG1/QB1 ET "AIR"
            ok=bool(re.search(r'\bAIR\b',label,re.I) and re.search(r'Q[ABG]\s*[. ]?1|TRANSPORT SERV USED',label,re.I))
        elif role=='profession':
            ok=bool(re.search(r'\bD\.?15\s?A\b|OCCUPATION OF RESPONDENT',label,re.I) and not re.search(r'LAST JOB|D15B',label,re.I))
        else:
            ok=bool(re.search(r'\bD\.?8\b|AGE EDUCATION',label,re.I) and not re.search(r'RECODED|D8R|GROUP',label,re.I))
        if ok: candidats.append(c)
    if len(candidats)!=1:
        partie=[(c,labels.get(c,'')) for c in df.columns if re.search('AIR|EDUCATION|OCCUPATION|D15A|QA1|QG1|QB1',labels.get(c,''),re.I)]
        raise ValueError(f'Impossible de choisir UNIQUEMENT la colonne {role} de {annee}: {candidats}. Candidats à examiner : {partie[:28]}. Ajoute la correspondance à cleaning code/config_variables.json.')
    return candidats[0]


def trouver_country(df, labels, config, annee):
    explicite=config.get(str(annee),{}).get('pays')
    if explicite: return explicite.lower()
    for c in ['v7','nation','country','country_iso','pays']:
        if c in df.columns: return c
    cand=[c for c in df.columns if re.search(r'NATION - ALL SAMPLES ISO|COUNTRY ISO',labels.get(c,''),re.I)]
    if len(cand)!=1: raise ValueError(f'Colonne pays non trouvée. Candidats: {cand}')
    return cand[0]


def trouver_weight(df,labels,config,annee):
    explicite=config.get(str(annee),{}).get('poids') or WAVES[annee].get('poids')
    if explicite:
        if explicite.lower() not in df.columns: raise ValueError(f'Poids absent: {explicite}')
        return explicite.lower()
    if 'v8' in df.columns and re.search(r'WEIGHT|W1',labels.get('v8',''),re.I): return 'v8'
    cands=[c for c in df.columns if re.search(r'\bW1\b.*WEIGHT|WEIGHT RESULT FROM TARGET',labels.get(c,''),re.I)]
    if len(cands)!=1: raise ValueError(f'Poids W1 non identifié ({cands}). Configuration requise; jamais de poids fictifs.')
    return cands[0]


def normaliser_pays(raw, labels_value):
    def nettoyer(v):
        if pd.isna(v):return None
        # v7 (GESIS) distingue DE-E/DE-W et GB-GBN/GB-NIR
        s=str(labels_value.get(v,v)).strip().upper().replace('_','-')
        aliases={'EL':'GR','UK':'GB','CZECH REPUBLIC':'CZ','GREECE':'GR','UNITED KINGDOM':'GB','GERMANY':'DE'}
        if s in aliases:return aliases[s]
        if s.startswith('DE-') or s.startswith('GERMANY'):return 'DE'
        if s.startswith('GB-') or s.startswith('UNITED KINGDOM'):return 'GB'
        m=re.match(r'^([A-Z]{2})(?:\b|[- ])',s)
        if m:return aliases.get(m.group(1),m.group(1))
        # accepte noms en anglais si présents dans les labels
        names={'AUSTRIA':'AT','BELGIUM':'BE','BULGARIA':'BG','CYPRUS':'CY','CZECHIA':'CZ','DENMARK':'DK',
               'ESTONIA':'EE','SPAIN':'ES','FINLAND':'FI','FRANCE':'FR','CROATIA':'HR','HUNGARY':'HU',
               'IRELAND':'IE','ITALY':'IT','LITHUANIA':'LT','LUXEMBOURG':'LU','LATVIA':'LV',
               'MALTA':'MT','NETHERLANDS':'NL','POLAND':'PL','PORTUGAL':'PT','ROMANIA':'RO',
               'SWEDEN':'SE','SLOVENIA':'SI','SLOVAKIA':'SK'}
        return names.get(s)
    return raw.map(nettoyer)


def codes_numeriques(serie, valuemap=None):
    """Valeurs archivées GESIS sont numériques (pas des noms affichés)."""
    s=pd.to_numeric(serie,errors='coerce')
    if s.notna().sum()==0 and serie.notna().any():
        raise ValueError('Les colonnes sont des étiquettes textuelles: utilise le .dta/.sav officiel non converti.')
    return s


def classifier_education(s):
    # GESIS archive D8: 97 pas d'études, 98 études en cours, 99 sans réponse;
    # valeurs manquantes propres au codebook 96 outlier. Seules les fins d'études valides sont classées.
    x=codes_numeriques(s)
    cat=pd.Series(pd.NA,index=s.index,dtype='string')
    cat.loc[x.between(2,15)]='≤ 15 ans'
    cat.loc[x.between(16,19)]='16–19 ans'
    cat.loc[x.between(20,65)]='≥ 20 ans'
    return cat


def classifier_profession(s):
    x=codes_numeriques(s)
    g=pd.Series(pd.NA,index=s.index,dtype='string')
    # D15a avec codes 1–18, tel que documenté dans les questionnaires GESIS.
    g.loc[x.isin([7,10,11,12])]='Cadres / prof. sup.'
    g.loc[x.isin([13,14,15])]='Employés / services'
    g.loc[x.isin([16,17,18])]='Ouvriers / encadrement'
    g.loc[x.isin([5,6,8,9])]='Indépendants hors prof. lib.'
    # les inactifs [1,2,3,4] exclus des taux PAR MÉTIER
    return g


def classifier_air(s):
    v=codes_numeriques(s)
    uniques=set(v.dropna().astype(int).unique().tolist())
    if not uniques.issubset({0,1,9,99}):
        raise ValueError(f'Question avion non binaire: {sorted(uniques)}. Vérification requise.')
    return v.where(v.isin([0,1]))


def nettoyage_vague(annee,config):
    df, labels, value_labels, source=charger_microdonnees(annee)
    roles={r:trouver_colonne(df,labels,annee,r,config) for r in ['air','profession','education']}
    roles['pays']=trouver_country(df,labels,config,annee)
    roles['poids']=trouver_weight(df,labels,config,annee)
    if len(set(roles.values()))!=len(roles):raise ValueError(f'Variables en doublon: {roles}')
    p=normaliser_pays(df[roles['pays']], value_labels.get(roles['pays'],{}))
    w=pd.to_numeric(df[roles['poids']],errors='coerce')
    air=classifier_air(df[roles['air']])
    educ=classifier_education(df[roles['education']])
    prof=classifier_profession(df[roles['profession']])
    out=pd.DataFrame({'annee':annee,'pays':p,'avion':air,'profession':prof,'education':educ,'poids':w})
    # pays hors UE explicitement exclus, poids positifs et réponse valide à la question transport.
    elig={2005:EU25,2009:EU27,2014:EU28}[annee]
    out=out.loc[out['pays'].isin(elig) & out['poids'].gt(0) & out['avion'].isin([0,1])].copy()
    if out.empty:raise ValueError(f'{annee} : aucun répondant éligible; colonnes/pays/poids à vérifier ({roles})')
    if out['pays'].nunique()<18: raise ValueError(f'{annee}: seuls {out.pays.nunique()} pays reconnus; vérifie le codage de v7 et les données.')
    audit={'vague':annee,'fichier':str(source),'colonnes':roles,'observations_valides_avion':len(out),
           'pays_reconnus':sorted(out.pays.unique().tolist()),
           'exclus_education':int(out.education.isna().sum()),'exclus_profession':int(out.profession.isna().sum())}
    return out,audit


def moyenne_ponderee(df):
    return 100*np.average(df['avion'].to_numpy(float),weights=df['poids'].to_numpy(float))


def taux_groupes(data,col):
    selection=data.dropna(subset=[col])
    result=[]
    for (year,pays,cat),g in selection.groupby(['annee','pays',col],observed=True):
        n=len(g)
        # Seuil purement descriptif, pas une garantie de précision statistique.
        if n<30: continue
        result.append({'annee':int(year),'pays':pays,'categorie':str(cat),'taux_pct':moyenne_ponderee(g),
                       'n_non_pondere':n,'somme_poids':g.poids.sum()})
    return pd.DataFrame(result)


def nettoyer():
    config_path=Path(__file__).resolve().parent/'config_variables.json'
    config=json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else {}
    OUT.mkdir(parents=True, exist_ok=True)
    donnees=[]; audits=[]
    for annee in WAVES:
        a,b=nettoyage_vague(annee,config)
        donnees.append(a);audits.append(b)
    all_data=pd.concat(donnees,ignore_index=True)
    # Produit uniquement des agrégats anonymes, jamais une copie modifiée des microdonnées.
    occupation=taux_groupes(all_data,'profession')
    education=taux_groupes(all_data,'education')
    global_by_country=taux_groupes(all_data.assign(groupe='Tous'),'groupe')
    if education.empty or occupation.empty:raise ValueError('Pas de catégories avec suffisamment de réponses valides')
    occupation.to_csv(OUT/'eurobarometre_professions_pays_2005_2009_2014.csv',index=False)
    education.to_csv(OUT/'eurobarometre_education_pays_2005_2009_2014.csv',index=False)
    global_by_country.to_csv(OUT/'eurobarometre_global_pays_2005_2009_2014.csv',index=False)
    (OUT/'audit_sources_eurobarometre.json').write_text(json.dumps(audits,indent=2,ensure_ascii=False),encoding='utf-8')
    return {'professions':occupation,'education':education,'global':global_by_country,'audit':audits}

if __name__=='__main__':
    sorties=nettoyer()
    for nom,tab in sorties.items():
        if isinstance(tab,pd.DataFrame):print(nom,tab.shape,'pays:',tab.pays.nunique() if 'pays' in tab else '-')
