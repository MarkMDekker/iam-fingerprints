DOWNLOAD_AGAIN = False

SCENARIOS = ['C400-lin',
             'C80-gr5',
             'C160-gr5',
             'C0to400-lin',
             'C400-lin-LimBio',
             'C400-lin-LimCCS',
             'Current-Policies']

VARIABLES     = ['Emissions|Kyoto Gases',
                 'Emissions|CO2',
                 'Emissions|CO2|Energy and Industrial Processes',
                 'Emissions|CH4',
                 'Emissions|CO2|AFOLU',
                 'Emissions|Kyoto Gases|AFOLU',
                 'Emissions|CH4|AFOLU',
                 'Emissions|N2O|AFOLU',
                 
                 'Carbon Capture',
                 'Carbon Removal|Land Use',

                 'Land Cover',
                 'Land Cover|Cropland',
                 'Land Cover|Pasture',
                 'Land Cover|Built-Up Area',
                 'Land Cover|Forest',
                 'Land Cover|Other Land',
                 'Land Cover|Other Natural',

                 'Yield|Cropland|Cereals',
                 'Yield|Cropland|Energy Crops',
                 'Yield|Cropland|Oil Crops',
                 'Yield|Cropland|Other Crops',
                 'Yield|Cropland|Sugar Crops',

                 'Agricultural Production',
                 'Agricultural Production|Crops',
                 'Agricultural Production|Crops|Energy Crops',
                 'Agricultural Production|Livestock',

                 'Food Availability [per capita]',
                 'Food Availability|Crops [per capita]',
                 'Food Availability|Livestock [per capita]',
                 
                 'Primary Energy',
                 'Primary Energy|Coal',
                 'Primary Energy|Oil',
                 'Primary Energy|Gas',
                 'Primary Energy|Biomass',
                 'Primary Energy|Solar',
                 'Primary Energy|Wind',
                 'Primary Energy|Fossil',
                 'Primary Energy|Nuclear',
                 
                 'Final Energy',
                 'Final Energy|Industry',
                 'Final Energy|Transportation',
                 'Final Energy|Residential and Commercial',
                 
                 'Final Energy|Electricity',
                 'Final Energy|Industry|Electricity',
                 'Final Energy|Transportation|Electricity',
                 'Final Energy|Residential and Commercial|Electricity',
                 
                 'GDP|PPP',
                 'Price|Carbon',
                 'Price|Agriculture|Food Products [Index]',
                 
                 'Policy Cost|Additional Total Energy System Cost',
                 'Policy Cost|Area under MAC Curve',
                 'Policy Cost|Consumption Loss',
                 'Policy Cost|GDP Loss w/o Transfers']

COLORS = [
    "#4477AA",  # Blue
    "#EE6677",  # Red
    "#228833",  # Green
    "#CCBB44",  # Yellow
    "#66CCEE",  # Cyan
    "#AA3377",  # Purple
    "#EE7733",  # Orange
    "#BBBBBB",  # Grey
    "#000000",  # Black
    "#8B4513",  # Brown
]