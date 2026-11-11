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

import ixmp4

from src.globals import paths, settings

# =========================================================== #
# CLASS OBJECT
# =========================================================== #

class ReadData(object):

    # =========================================================== #
    # =========================================================== #

    def __init__(self):
        print("# ======================================= #")
        print("# Initializing data reading               #")
        print("# ======================================= #")

    # =========================================================== #
    # =========================================================== #

    def download_data(self):
        if settings.DOWNLOAD_AGAIN:
            print("- Download data from IIASA database")
            platform = ixmp4.Platform("iam-diagnostics-internal")
            df_download = platform.iamc.tabulate(variable=settings.VARIABLES,
                                                 region='World')
            ds = (df_download.set_index(["model","scenario","region","variable","year",])["value"].to_xarray().to_dataset(name="value"))
            ds = ds.interpolate_na(dim="year", method="linear")
            self.xr_diag_raw = ds.ffill("year").bfill("year")
            self.xr_diag_raw = self.xr_diag_raw.assign_coords(year=self.xr_diag_raw.year.values.astype("int"))
            
            self.xr_diag_raw.to_netcdf(paths.data / 'xr_diag_raw.nc')
        else:
            print('- Skip downloading files, already preloaded')
            self.xr_diag_raw = xr.open_dataset(paths.data / 'xr_diag_raw.nc')

    # =========================================================== #
    # =========================================================== #

    def data_cleaning(self):
        print("- Clean data")
        self.xr_diag = self.xr_diag_raw.copy()

        # NEMESIS No-Policy scenario
        self.xr_diag.loc[dict(model="NEMESIS-World 1.1", scenario='Current-Policies')] = self.xr_diag.sel(scenario='No-Policy').value.loc[dict(model="NEMESIS-World 1.1")]

        # NEMESIS Kyoto Gases
        self.xr_diag.loc[dict(model="NEMESIS-World 1.1", variable='Emissions|Kyoto Gases')] = self.xr_diag.sel(model="NEMESIS-World 1.1", variable='Emissions|Kyoto Gases').value / 1e6

        # CO2 emissions MERGE-ETL
        self.xr_diag.loc[dict(model="MERGE-ETL 6.0", variable='Emissions|CO2|Energy and Industrial Processes')] = self.xr_diag.sel(model="MERGE-ETL 6.0", variable='Emissions|CO2').value

        # Policy costs
        self.xr_diag.loc[dict(model="NEMESIS-World 1.1", variable='Policy Cost|Consumption Loss')] = self.xr_diag.sel(model="NEMESIS-World 1.1", variable='Policy Cost|Consumption Loss').value/1e6
        frida_models = ['FRIDA 3.1','FRIDA 3.1 [02.5 Percentile]', 'FRIDA 3.1 [97.5 Percentile]','FRIDA 3.1 [Best Estimate]']
        self.xr_diag.loc[dict(model=frida_models, variable='Policy Cost|Consumption Loss')] = self.xr_diag.sel(model=frida_models, variable='Policy Cost|Consumption Loss').value

        # Select policy cost variable depending on reporting
        self.xr_diag = self.xr_diag.reindex(variable=list(self.xr_diag.variable.values) + ['Policy Cost|Chosen'])
        for mod in self.xr_diag.model.values:
            area_cost = self.xr_diag.sel(model=mod, variable='Policy Cost|Area under MAC Curve').value
            cons_loss = self.xr_diag.sel(model=mod, variable='Policy Cost|Consumption Loss').value
            gdp_loss = self.xr_diag.sel(model=mod, variable='Policy Cost|GDP Loss w/o Transfers').value
            if not area_cost.isnull().all():
                chosen = area_cost
            elif not cons_loss.isnull().all():
                chosen = cons_loss
            elif not gdp_loss.isnull().all():
                chosen = gdp_loss
            else:
                chosen = self.xr_diag.sel(model=mod, variable='Policy Cost|Additional Total Energy System Cost').value # Also if this gives nans
            self.xr_diag.loc[dict(model=mod, variable='Policy Cost|Chosen')] = chosen
        self.xr_diag.loc[dict(variable='Policy Cost|Chosen')]  = self.xr_diag.loc[dict(variable='Policy Cost|Chosen')].where(self.xr_diag.loc[dict(variable='Policy Cost|Chosen')] != 0, np.nan)

    # =========================================================== #
    # =========================================================== #

    def save(self):
        print("- Save")
        self.xr_diag.to_netcdf(paths.data / 'xr_diag.nc')