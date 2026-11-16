# Per capita CO₂ emissions from international passenger flights, tourism-adjusted - Data package

This data package contains the data that powers the chart ["Per capita CO₂ emissions from international passenger flights, tourism-adjusted"](https://ourworldindata.org/grapher/per-capita-co2-international-flights-adjusted?v=1&csvType=full&useColumnShortNames=false&utm_source=chatgpt.com) on the Our World in Data website.

### Active Filters

A filtered subset of the full data was downloaded. The following filters were applied:

## CSV structure

Each row is an observation for an entity (usually a country or region) at a timepoint.

- "Entity" — the name of the entity, e.g. "United States".
- "Code" — our internal entity code. For most countries this is the [ISO alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code, e.g. "USA"; historical and other non-standard entities get a custom code.
- "Year" or "Day" — the timepoint. Annual data has a "Year" column holding an integer year; otherwise a "Day" column holds a date string in the form "YYYY-MM-DD".
- Every remaining column is a data column, each one a time series. Downloaded with the "full data" option each corresponds to one time series below; with "only selected data visible in the chart" they are transformed depending on the chart type, so the correspondence may be less direct.


## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc.

## How we process data at Our World in Data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stitch together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

Preparing this data involves several processing steps. Depending on the data, this can include standardizing country names and world region definitions, converting units, calculating derived indicators such as per capita measures, as well as adding or adapting metadata such as the name or the description given to an indicator.
[Read about our data pipeline](https://docs.owid.io/projects/etl/).

## Detailed information about each time series


### Per capita CO₂ emissions from international flights, international tourism-adjusted
International aviation emissions are allocated to the country of departure, then adjusted for tourism.
Last updated: March 11, 2025  
Next expected update: December 2026  
Date range: 2013–2024  
Unit: kilograms  
Source: OECD (2025); UN Tourism (2025); Population based on various sources (2024) – with minor processing by Our World in Data  

#### How to cite this data

OECD (2025); UN Tourism (2025); Population based on various sources (2024) – with minor processing by Our World in Data

#### What you should know about this data
This data isn’t seasonally adjusted—summer travel increases emissions, but the actual impact may be lower as Northern Hemisphere plants absorb more CO₂ during this time.

#### Notes on our processing step for this indicator
- CO₂ emission footprints do not necessarily reflect the amount of travel by locals in a given location. This is especially true if a country has high tourist volumes - much of the departures will result from travelers rather than local residents.

- We have therefore also calculated 'adjusted' aviation footprints by multiplying international CO₂ emissions by an adjustment factor.

- This adjustment factor is taken as the ratio between outbound and inbound tourist trips.

- A high ratio of outbound-to-inbound tourist trips indicates that a country receives less visitors than its residents travel abroad. This results in a relatively lower burden of emissions from international flights being allocated to the country whose residents don't travel internationally as frequently.


### World region according to OWID
Regions defined by Our World in Data, which are used in OWID charts and maps.
Last updated: January 1, 2023  
Date range: 2023–2023  
Source: Our World in Data  

#### How to cite this data

Our World in Data


## Sources

These are the sources behind the data in this package. Each time series above names the ones it draws on in its citation.

### OECD – Air transport CO2 emissions (experimental)

This database provides annual, quarterly and monthly estimates for carbon dioxide (CO2) emissions from commercial passenger, freight and general aviation flights. The emissions are estimated for 186 countries by the OECD, based on a consistent methodology across countries. From 2019, the estimates are compiled using Automatic Dependent Surveillance-Broadcast (ADS-B) flight data from the International Civil Aviation Organisation (ICAO).

The database provides measures of CO2 emissions on a territory basis, which is used for reporting in the UN Framework Convention on Climate Change (UNFCCC) inventories; and also on a residence basis, which is used to estimate the emissions of air transport (H51 in the International Standard Industrial Classification of All Economic Activities, or ISIC) in the Air Emission Accounts (AEAs).

Seven components of these CO2 emissions measures can be selected from the ‘Emissions ’ filter. In the tables, these are also shown with the letters A, B, C, D, E, F and G. The UNFCCC inventories and AEA air transport (ISIC H51) measures of CO2 emissions are calculated as:
Inventories: domestic aviation = A + C
Inventories: international aviation (memo item) = D + G
Air emissions accounts: air transport (ISIC H51) = A + B + D + E + F
Three categories of flight are shown on the database: total flights, passenger flights, and freight flights. General aviation (non-freight flights with fewer than 19 passengers such as agricultural planes and private jets) is included with passenger flights.

The estimation methodology is described in the OECD Working Paper CO2 Emissions from Air Transport - A Near-Real-Time Global Database for Policy Analysis. and in the note Air transport CO2 emissions methodology update.

Producer: OECD  
Published: 2025-02-25  
Retrieved on: 2025-03-11  
Retrieved from: https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_AIR_TRANSPORT%40DF_AIR_TRANSPORT&df[ag]=OECD.SDD.NAD.SEEA&dq=W%2BZWE%2BZMB%2BYEM%2BVNM%2BVEN%2BVUT%2BUZB%2BURY%2BARE%2BUKR%2BUGA%2BTUV%2BTKM%2BTUN%2BTTO%2BTON%2BTGO%2BTLS%2BTHA%2BTZA%2BTJK%2BSYR%2BTWN%2BSUR%2BSDN%2BLKA%2BSSD%2BZAF%2BSOM%2BSLB%2BSXM%2BSLE%2BSGP%2BSYC%2BSRB%2BSEN%2BSAU%2BSTP%2BSMR%2BWSM%2BVCT%2BLCA%2BKNA%2BRWA%2BRUS%2BROU%2BQAT%2BPHL%2BPER%2BPRY%2BPNG%2BPAN%2BPLW%2BPAK%2BOMN%2BMKD%2BNGA%2BNIU%2BNIC%2BNER%2BNRU%2BNPL%2BNAM%2BMMR%2BMOZ%2BMAR%2BMNE%2BMNG%2BMCO%2BMDA%2BFSM%2BMUS%2BMRT%2BMHL%2BMLT%2BMLI%2BMDV%2BMYS%2BMWI%2BMDG%2BMAC%2BLBY%2BLBR%2BLSO%2BLBN%2BLAO%2BKWT%2BKGZ%2BXKV%2BKIR%2BKEN%2BKAZ%2BJOR%2BJEY%2BJAM%2BIRQ%2BIDN%2BIRN%2BIND%2BHKG%2BHND%2BHTI%2BGUY%2BGNB%2BGIN%2BGTM%2BGRD%2BGHA%2BGEO%2BGMB%2BGAB%2BFJI%2BETH%2BSWZ%2BERI%2BGNQ%2BSLV%2BEGY%2BECU%2BDOM%2BDMA%2BCOD%2BDJI%2BPRK%2BCYP%2BCUB%2BHRV%2BCIV%2BCOK%2BCOG%2BCCK%2BCOM%2BCXR%2BCHN%2BTCD%2BCAF%2BCMR%2BKHM%2BCPV%2BBDI%2BBFA%2BBGR%2BBRN%2BBRA%2BBWA%2BBIH%2BBOL%2BBTN%2BBEN%2BBLZ%2BBLR%2BBRB%2BBGD%2BBHR%2BBHS%2BAZE%2BARM%2BARG%2BATG%2BAGO%2BDZA%2BALB%2BAFG%2BWXOECD%2BOECD%2BUSA%2BGBR%2BTUR%2BCHE%2BSWE%2BESP%2BSVN%2BSVK%2BPRT%2BPOL%2BNOR%2BNZL%2BNLD%2BMEX%2BLUX%2BLTU%2BLVA%2BKOR%2BJPN%2BITA%2BISR%2BIRL%2BISL%2BGRC%2BHUN%2BDEU%2BFIN%2BEST%2BDNK%2BCZE%2BCRI%2BCOL%2BCHL%2BBEL%2BCAN%2BAUT%2BAUS%2BFRA.M.....P.RES_TOTAL%2BTER_INT%2BTER_DOM%2BRES_ABROAD%2BNRES_TERR%2BNRES_INT_FROM%2BRES_INT_OUT%2BRES_INT_TO%2BRES_INT_FROM%2BNRES_DOM_IN%2BRES_DOM_OUT%2BRES_DOM_IN.&pd=2013-01%2C2024-12&to[TIME_PERIOD]=false&ly[cl]=TIME_PERIOD&ly[rw]=EMISSIONS_SOURCE%2CCOMBINED_UNIT_MEASURE%2CREF_AREA&vw=tb&format=csvfilewithlabels  
Direct download: https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD.SEEA,DSD_AIR_TRANSPORT@DF_AIR_TRANSPORT,/all?dimensionAtObservation=AllDimensions&format=csvfilewithlabels  
License: OECD Terms of Conditions (https://www.oecd.org/en/about/terms-conditions.html)  

Citation: OECD (2025). OECD Data Explorer. Air transport CO2 emissions (experimental).

### UN Tourism – UN Tourism Statistics Database

UN World Tourism Organization collects data from countries through annual questionnaires that follow the International Recommendations for Tourism Statistics (IRTS 2008) standard, a framework approved by the United Nations. The data covers various aspects of tourism, such as inbound tourism (including arrivals by region, main purpose, and mode of transport, as well as accommodation and tourism expenditure in the country), domestic tourism (including trips and accommodation), outbound tourism (including departures and tourism expenditure in other countries), tourism industries (such as accommodation in hotels and similar establishments), and employment (including the number of employees in tourism industries).

Producer: UN Tourism  
Published: 2025-12-29  
Retrieved on: 2026-01-21  
Retrieved from: https://www.untourism.int/tourism-statistics/tourism-statistics-database  
Direct download: https://pre-webunwto.s3.amazonaws.com/s3fs-public/2025-12/UN_Tourism_bulk_data_download_12_2025.zip  
License: © UNWTO, 92844/14/23 (https://www.unwto.org/copyright)  

Citation: "World Tourism Organization (2025). UN Tourism Statistics Database, Madrid. Data updated on 23 December 2025. More information: https://www.untourism.int/tourism-statistics/tourism-statistics-database"

### Various sources – Population

Our World in Data builds and maintains a long-run dataset on population by country, region, and for the world, based on various sources.

You can find more information on these sources and how our time series is constructed on this page: https://ourworldindata.org/population-sources

Producer: Various sources  
Published: 2024-07-15  
Retrieved on: 2026-10-22  
Retrieved from: https://ourworldindata.org/population-sources  
License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)  

Citation: The long-run data on population is based on various sources, described on this page: https://ourworldindata.org/population-sources

### Our World in Data – Regions

Producer: Our World in Data  

    