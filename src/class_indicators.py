# ======================================== #
# Class that does the reading of the SCI database, and preps the data for various uses
# ======================================== #

# =========================================================== #
# PREAMBULE
# Put in packages that we need
# =========================================================== #

import numpy as np
import pandas as pd
import xarray as xr

from src.globals import paths, settings

# =========================================================== #
# CLASS OBJECT
# =========================================================== #

class Indicators(object):

    # =========================================================== #
    # =========================================================== #

    def __init__(self):
        print("# ======================================= #")
        print("# Initializing indicators class           #")
        print("# ======================================= #")

        self.xr_diag = xr.open_dataset(paths.data / 'xr_diag.nc')

        self.xr_ind = self.xr_diag.copy()
        
        # Remove variable coordinate and value variable
        self.xr_ind = self.xr_ind.drop_vars('variable')
        self.xr_ind = self.xr_ind.drop_vars('value')

    # =========================================================== #
    # =========================================================== #

    def dim_responsiveness(self):
        print("- Calculate responsiveness indicators")
        denominator = self.xr_diag.sel(variable='Emissions|CO2|Energy and Industrial Processes',scenario='Current-Policies').value
        self.xr_ind["Relative Abatement Index"] = 1 - (self.xr_diag.sel(variable = 'Emissions|CO2|Energy and Industrial Processes').value / denominator)
        self.xr_ind["Relative Abatement Index"] = self.xr_ind["Relative Abatement Index"].where(self.xr_ind["Relative Abatement Index"] != 0, np.nan)
        
        denominator = self.xr_diag.sel(variable='Emissions|Kyoto Gases',scenario='Current-Policies').value
        self.xr_ind["Relative Abatement Index (GHG)"] = 1 - (self.xr_diag.sel(variable = 'Emissions|Kyoto Gases').value / denominator)
        self.xr_ind["Relative Abatement Index (GHG)"] = self.xr_ind["Relative Abatement Index (GHG)"].where(self.xr_ind["Relative Abatement Index (GHG)"] != 0, np.nan)
        pes = ["Coal", "Oil", "Gas", "Solar", "Wind", "Nuclear", "Biomass"]
        sumdif = None
        for p in pes:
            fr_2025 = (
                self.xr_diag.sel(variable="Primary Energy|" + p, year=2025).value /
                self.xr_diag.sel(variable="Primary Energy", year=2025).value
            )
            fr_bench = (
                self.xr_diag.sel(variable="Primary Energy|" + p, year=2060).value /
                self.xr_diag.sel(variable="Primary Energy", year=2060).value
            )
            diff = abs(fr_bench - fr_2025)
            diff = diff.fillna(0)
            sumdif = diff if sumdif is None else sumdif + diff
        self.xr_ind['Transformation Index'] = sumdif

        # Inertia indicators
        curpol = self.xr_diag.sel(variable = 'Emissions|CO2|Energy and Industrial Processes', scenario="Current-Policies", year=np.arange(2025, 2101)).value
        series = self.xr_diag.sel(variable = 'Emissions|CO2|Energy and Industrial Processes', year=np.arange(2025, 2101)).value
        years = np.zeros(shape=(len(self.xr_diag.scenario),
                                len(self.xr_diag.model),
                                len(self.xr_diag.region)))
        for m_i, m in enumerate(self.xr_diag.model):
            for s_i, s in enumerate(self.xr_diag.scenario):
                wh_tot = np.where(series[m_i, s_i] < curpol.sel(model=m)*(1-0.66))
                for r_i, r in enumerate(np.array(self.xr_diag.region)):
                    wh = wh_tot[1][wh_tot[0]==r_i]
                    if len(wh)>0:
                        years[s_i, m_i, r_i] = np.arange(2025, 2101)[wh[0]]-2025
                    else:
                        years[s_i, m_i, r_i] = np.nan
        years = years
        self.xr_ind['Timescale early mitigation'] = xr.DataArray(data=years,
                                                coords=dict(scenario=self.xr_diag.scenario,
                                                model=self.xr_diag.model,
                                                region=self.xr_diag.region))

        cum_400lin = self.xr_diag.sel(variable = 'Emissions|CO2|Energy and Industrial Processes', scenario='C400-lin', year=np.arange(2040, 2101)).value.sum(dim='year')
        cum_0to400lin = self.xr_diag.sel(variable = 'Emissions|CO2|Energy and Industrial Processes', scenario='C0to400-lin', year=np.arange(2040, 2101)).value.sum(dim='year')
        dif_2040 = self.xr_diag.sel(variable = 'Emissions|CO2|Energy and Industrial Processes', scenario='C0to400-lin', year=2040).value - self.xr_diag.sel(variable = 'Emissions|CO2', scenario='C400-lin', year=2040).value
        self.xr_ind['Inertia of shock'] = (cum_0to400lin - cum_400lin) / dif_2040

        # CAV
        cum_policy_costs = self.xr_diag.sel(variable="Policy Cost|Chosen", year=np.arange(2030, 2061)).sum(dim='year')
        cum_policy_costs = cum_policy_costs.where(cum_policy_costs != 0, np.nan)
        abatement_bench = self.xr_diag.sel(variable="Emissions|Kyoto Gases", year=2030).value - self.xr_diag.sel(variable="Emissions|Kyoto Gases", year=np.arange(2030, 2061)).value
        cum_abatement_weighted = (abatement_bench*self.xr_diag.sel(variable="Price|Carbon", year=np.arange(2030, 2061))).sum(dim='year').value
        cum_abatement_weighted = cum_abatement_weighted.where(cum_abatement_weighted != 0, np.nan)
        self.xr_ind['Cost Per Abatement Value'] = cum_policy_costs.value / cum_abatement_weighted

    # =========================================================== #
    # =========================================================== #

    def dim_strategy(self):
        print("- Calculate mitigation strategy indicators")
        self.xr_ind["Carbon Intensity"]             = self.xr_diag.sel(variable = 'Emissions|Kyoto Gases').value / self.xr_diag.sel(variable = 'Final Energy').value
        self.xr_ind["Carbon Intensity Reduction"]   = (self.xr_ind.sel(year=2025)['Carbon Intensity'] - self.xr_ind['Carbon Intensity']) / self.xr_ind.sel(year=2025)['Carbon Intensity']
        self.xr_ind["Energy Intensity"]             = self.xr_diag.sel(variable = 'Final Energy').value / self.xr_diag.sel(variable = 'GDP|PPP').value
        self.xr_ind["Energy Intensity Reduction"]   = (self.xr_ind.sel(year=2025)['Energy Intensity'] - self.xr_ind['Energy Intensity']) / self.xr_ind.sel(year=2025)['Energy Intensity']
        self.xr_ind["Cumulative Carbon Capture"]    = self.xr_diag.sel(variable='Carbon Capture', year=np.arange(2025, 2061)).value.sum(dim='year')
        nonco2                                      = self.xr_diag.sel(variable='Emissions|Kyoto Gases').value - self.xr_diag.sel(variable='Emissions|CO2').value
        nonco2_reduction                            = nonco2.sel(year=2025) - nonco2
        ghg                                         = self.xr_diag.sel(variable='Emissions|Kyoto Gases').value
        ghg_reduction                               = ghg.sel(year=2025) - ghg
        fraction_nonco2                             = nonco2_reduction / ghg_reduction
        self.xr_ind["Change in non-CO2 mitigation"] = fraction_nonco2 - fraction_nonco2.sel(scenario = 'Current-Policies')
        self.xr_ind['Change in non-CO2 mitigation'] = self.xr_ind['Change in non-CO2 mitigation'].where(self.xr_ind['Change in non-CO2 mitigation'] != 0, np.nan)
        fossil                                      = self.xr_diag.sel(variable=['Primary Energy|Coal', 'Primary Energy|Oil', 'Primary Energy|Gas']).value.sum(dim='variable')
        ffr                                         = (fossil.sel(year=2025) - fossil) / fossil.sel(year=2025)
        self.xr_ind["Fossil Fuel Reduction"]        = ffr - ffr.sel(scenario = 'Current-Policies')

    # =========================================================== #
    # =========================================================== #

    def dim_supply(self):
        print("- Calculate energy supply indicators")
        self.xr_ind["Fraction Primary Coal"]            = self.xr_diag.sel(variable = 'Primary Energy|Coal').value / self.xr_diag.sel(variable = 'Primary Energy').value
        self.xr_ind["Fraction Primary Oil"]             = self.xr_diag.sel(variable = 'Primary Energy|Oil').value / self.xr_diag.sel(variable = 'Primary Energy').value
        self.xr_ind["Fraction Primary Gas"]             = self.xr_diag.sel(variable = 'Primary Energy|Gas').value / self.xr_diag.sel(variable = 'Primary Energy').value
        self.xr_ind["Fraction Primary Solar"]           = self.xr_diag.sel(variable = 'Primary Energy|Solar').value / self.xr_diag.sel(variable = 'Primary Energy').value
        self.xr_ind["Fraction Primary Wind"]            = self.xr_diag.sel(variable = 'Primary Energy|Wind').value / self.xr_diag.sel(variable = 'Primary Energy').value
        self.xr_ind["Fraction Primary Biomass"]         = self.xr_diag.sel(variable = 'Primary Energy|Biomass').value / self.xr_diag.sel(variable = 'Primary Energy').value
        self.xr_ind["Fraction Primary Nuclear"]         = self.xr_diag.sel(variable = 'Primary Energy|Nuclear').value / self.xr_diag.sel(variable = 'Primary Energy').value

    # =========================================================== #
    # =========================================================== #

    def dim_demand(self):
        print("- Calculate energy demand indicators")
        self.xr_ind["Electrification in Industry"]        = self.xr_diag.sel(variable = 'Final Energy|Industry|Electricity').value / self.xr_diag.sel(variable = 'Final Energy|Industry').value
        self.xr_ind["Electrification in Buildings"]       = self.xr_diag.sel(variable = 'Final Energy|Residential and Commercial|Electricity').value / self.xr_diag.sel(variable = 'Final Energy|Residential and Commercial').value
        self.xr_ind["Electrification in Transport"]       = self.xr_diag.sel(variable = 'Final Energy|Transportation|Electricity').value / self.xr_diag.sel(variable = 'Final Energy|Transportation').value
        self.xr_ind["Electrification in Transport"]       = self.xr_ind["Electrification in Transport"].where(self.xr_ind["Electrification in Transport"] != 0, np.nan)
        #self.xr_ind["Total Electrification"]           = self.xr_diag.sel(variable = 'Final Energy|Electricity').value / self.xr_diag.sel(variable = 'Final Energy').value
        self.xr_ind["Cumulative Energy Demand"]           = self.xr_diag.sel(variable = 'Final Energy', year = np.arange(2025, 2061)).value.sum(dim='year')
        self.xr_ind["Cumulative Energy Demand"]           = self.xr_ind["Cumulative Energy Demand"].where(self.xr_ind["Cumulative Energy Demand"] != 0, np.nan)

    # =========================================================== #
    # =========================================================== #

    def dim_land(self):
        print("- Calculate land indicators")
        self.xr_ind['Cumulative Land Use CO2 Emissions']        = self.xr_diag.sel(variable="Emissions|CO2|AFOLU", year=np.arange(2030, 2061)).value.sum(dim="year")
        landuse_nonco2                                          = self.xr_diag.sel(variable="Emissions|CH4|AFOLU") + self.xr_diag.sel(variable="Emissions|N2O|AFOLU")
        landuse_nonco2_mitigation                               = landuse_nonco2 - landuse_nonco2.sel(scenario="Current-Policies")
        landuse_ghg                                             = self.xr_diag.sel(variable="Emissions|Kyoto Gases|AFOLU")
        landuse_ghg_mitigation                                  = landuse_ghg - landuse_ghg.sel(scenario="Current-Policies")
        self.xr_ind['Land Use non-CO2 Mitigation']              = landuse_nonco2_mitigation.value / landuse_ghg_mitigation.value
        self.xr_ind['Land Use non-CO2 Mitigation']              = self.xr_ind['Land Use non-CO2 Mitigation'].where(self.xr_ind['Land Use non-CO2 Mitigation'] != 0, np.nan)
        self.xr_ind['Land based CDR']                           = self.xr_diag.sel(variable="Carbon Removal|Land Use", year=np.arange(2030, 2061)).value.sum(dim='year')
        self.xr_ind['Land based CDR']                           = self.xr_ind['Land based CDR'].where(self.xr_ind['Land based CDR'] != 0, np.nan)
        self.xr_ind['Human appropriated land']                  = (self.xr_diag.sel(variable="Land Cover|Cropland").value + self.xr_diag.sel(variable="Land Cover|Pasture").value + self.xr_diag.sel(variable="Land Cover|Built-Up Area").value) / self.xr_diag.sel(variable="Land Cover").value
        cropyield                                               = (self.xr_diag.sel(variable="Yield|Cropland|Cereals").value + 
                                                                 self.xr_diag.sel(variable="Yield|Cropland|Energy Crops").value + 
                                                                 self.xr_diag.sel(variable="Yield|Cropland|Oil Crops").value + 
                                                                 self.xr_diag.sel(variable="Yield|Cropland|Other Crops").value + 
                                                                 self.xr_diag.sel(variable="Yield|Cropland|Sugar Crops").value)
        self.xr_ind['Crop Yield Change']                        = (cropyield.sel(year=2060) - cropyield.sel(year=2025)) / cropyield.sel(year=2025)
        self.xr_ind['Agricultural Production Change']           = (self.xr_diag.sel(variable="Agricultural Production", year=2060).value - self.xr_diag.sel(variable="Agricultural Production", year=2025).value) / self.xr_diag.sel(variable="Agricultural Production", year=2025).value
        self.xr_ind['Food Availability Change']                 = (self.xr_diag.sel(variable="Food Availability [per capita]", year=2060).value - self.xr_diag.sel(variable="Food Availability [per capita]", year=2025).value) / self.xr_diag.sel(variable="Food Availability [per capita]", year=2025).value
        self.xr_ind['Food Price']                               = self.xr_diag.sel(variable="Price|Agriculture|Food Products [Index]").value

    # =========================================================== #
    # =========================================================== #

    def save(self):
        print("- Save indicators")
        self.xr_ind.to_netcdf(paths.data / 'xr_ind.nc')
