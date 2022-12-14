"""
This file defines the constants used throughout the different classes. In order to redefine these settings whilst using
the module, extend the respective config class and pass it to the class as the "constants" parameter.
"""
from __future__ import annotations

import pandas as pd
import pint
from ITR.data.osc_units import ureg, Q_, quantity, EmissionsQuantity
from typing import List
from pydantic import BaseModel
from dataclasses import dataclass

class ColumnsConfig:
    # Define a constant for each column used in the dataframe
    COMPANY_ID = "company_id"
    COMPANY_LEI = "company_lei"
    COMPANY_ISIN = "company_isin"
    COMPANY_ISIC = "isic"
    COMPANY_MARKET_CAP = "company_market_cap"
    INVESTMENT_VALUE = "investment_value"
    COMPANY_ENTERPRISE_VALUE = "company_enterprise_value"
    COMPANY_EV_PLUS_CASH = "company_ev_plus_cash"
    COMPANY_TOTAL_ASSETS = "company_total_assets"
    SCOPE = "scope"
    START_YEAR = "start_year"
    VARIABLE = "variable"
    SLOPE = "slope"
    TIME_FRAME = "time_frame"
    TEMPERATURE_SCORE = "temperature_score"
    COMPANY_NAME = "company_name"
    OWNED_EMISSIONS = "owned_emissions"
    COUNTRY = 'country'
    SECTOR = 'sector'
    TEMPLATE_EXPOSURE = 'exposure'
    TEMPLATE_CURRENCY = 'currency'
    TEMPLATE_FX_QUOTE = 'fx_quote'
    TEMPLATE_FX_RATE = 'fx_rate'
    TEMPLATE_REPORT_DATE = 'report_date'
    EMISSIONS_METRIC = 'emissions_metric'
    PRODUCTION_METRIC = 'production_metric'    # The unit of production (i.e., power generated, tons of steel produced, vehicles manufactured, etc.)
    BASE_YEAR_PRODUCTION = 'base_year_production'
    GHG_SCOPE12 = 'ghg_s1s2'
    GHG_SCOPE3 = 'ghg_s3'
    TEMPLATE_SCOPE1 = 'em_s1'
    TEMPLATE_SCOPE2 = 'em_s2'
    TEMPLATE_SCOPE12 = 'em_s1s2'
    TEMPLATE_SCOPE3 = 'em_s3'
    TEMPLATE_SCOPE123 = 'em_s1s2s3'
    HISTORIC_DATA = "historic_data"
    TARGET_DATA = "target_data"
    TEMPLATE_PRODUCTION = 'production'
    COMPANY_REVENUE = 'company_revenue'
    CASH_EQUIVALENTS = 'company_cash_equivalents'
    BASE_YEAR = 'base_year'
    END_YEAR = 'end_year'
    ISIC = 'isic'
    INDUSTRY_LVL1 = "industry_level_1"
    INDUSTRY_LVL2 = "industry_level_2"
    INDUSTRY_LVL3 = "industry_level_3"
    INDUSTRY_LVL4 = "industry_level_4"
    REGION = 'region'
    CUMULATIVE_BUDGET = 'cumulative_budget'
    CUMULATIVE_TRAJECTORY = 'cumulative_trajectory'
    CUMULATIVE_TARGET = 'cumulative_target'
    TARGET_PROBABILITY = 'target_probability'
    BENCHMARK_TEMP = 'benchmark_temperature'
    BENCHMARK_GLOBAL_BUDGET = 'benchmark_global_budget'
    BASE_EI = 'ei_at_base_year'
    PROJECTED_EI = 'projected_intensities'
    PROJECTED_TARGETS = 'projected_targets'
    HISTORIC_PRODUCTIONS = 'historic_productions'
    HISTORIC_EMISSIONS = 'historic_emissions'
    HISTORIC_EI = 'historic_ei'

    TRAJECTORY_SCORE = 'trajectory_score'
    TRAJECTORY_OVERSHOOT = 'trajectory_overshoot_ratio'
    TARGET_SCORE = 'target_score'
    TARGET_OVERSHOOT = 'target_overshoot_ratio'

    # Output columns
    WEIGHTED_TEMPERATURE_SCORE = "weighted_temperature_score"
    CONTRIBUTION_RELATIVE = "contribution_relative"
    CONTRIBUTION = "contribution"


class SectorsConfig:
    POWER_UTILITY = "Electricity Utilities"
    GAS_UTILITY = "Gas Utilities"
    UTILITY = "Utilities"
    STEEL = "Steel"
    ALUMINUM = "Aluminum"
    OIL_AND_GAS = "Oil & Gas"
    AUTOMOBILE = "Autos"
    TRUCKING = "Trucking"
    CEMENT = "Cement"
    BUILDINGS_CONSTRUCTION = "Construction Buildings"
    BUILDINGS_RESIDENTIAL = "Residential Buildings"
    BUILDINGS_COMMERCIAL = "Commercial Buildings"
    TEXTILES = "Textiles"
    CHEMICALS = "Chemicals"
    INFORMATION_TECHNOLOGY = "Information Technology"
    INDUSTRIALS = "Industrials"
    FINANCIALS = "Financials"
    HEALTH_CARE = "Health Care"

    @classmethod
    def get_configured_sectors(cls) -> List[str]:
        """
        Get a list of sectors configured in the tool.
        :return: A list of sectors string values
        """
        return [SectorsConfig.POWER_UTILITY, SectorsConfig.GAS_UTILITY, SectorsConfig.UTILITY,
                SectorsConfig.STEEL, SectorsConfig.ALUMINUM,
                SectorsConfig.OIL_AND_GAS,
                SectorsConfig.AUTOMOBILE, SectorsConfig.TRUCKING,
                SectorsConfig.CEMENT,
                SectorsConfig.BUILDINGS_CONSTRUCTION, SectorsConfig.BUILDINGS_RESIDENTIAL, SectorsConfig.BUILDINGS_COMMERCIAL,
                SectorsConfig.TEXTILES, SectorsConfig.CHEMICALS,
                ]


class VariablesConfig:
    EMISSIONS = "Emissions"
    PRODUCTIONS = "Productions"
    EMISSIONS_INTENSITIES = "Emissions Intensities"


class TargetConfig:
    COMPANY_ID = "company_id"
    COMPANY_LEI = "company_lei"
    COMPANY_ISIN = "company_isin"
    COMPANY_ISIC = "isic"
    NETZERO_DATE = 'netzero_date'
    TARGET_TYPE = 'target_type'
    TARGET_SCOPE = 'target_scope'
    TARGET_START_YEAR = 'target_start_year'
    TARGET_BASE_YEAR = 'target_base_year'
    TARGET_BASE_MAGNITUDE = 'target_base_year_qty'
    TARGET_BASE_UNITS = 'target_base_year_unit'
    TARGET_YEAR = 'target_year'
    TARGET_REDUCTION_VS_BASE = 'target_reduction_ambition'


class TabsConfig:
    FUNDAMENTAL = "fundamental_data"
    PROJECTED_EI = "projected_ei" # really "projected
    PROJECTED_PRODUCTION = "projected_production"
    PROJECTED_TARGET = "projected_target"
    HISTORIC_DATA = "historic_data"
    TEMPLATE_INPUT_DATA = 'ITR input data'
    TEMPLATE_INPUT_DATA_V2 = 'ITR V2 input data'
    TEMPLATE_ESG_DATA_V2 = 'ITR V2 esg data'
    TEMPLATE_TARGET_DATA = 'ITR target input data'


class PortfolioAggregationConfig:
    COLS = ColumnsConfig


@dataclass
class ProjectionControls:
    LOWER_PERCENTILE: float = 0.1
    UPPER_PERCENTILE: float = 0.9

    LOWER_DELTA: float = -0.10
    UPPER_DELTA: float = +0.03

    BASE_YEAR: int = 2019
    TARGET_YEAR: int = 2050
    TREND_CALC_METHOD: Callable[[pd.DataFrame], pd.DataFrame] = staticmethod(pd.DataFrame.median)


class TemperatureScoreControls(BaseModel):
    base_year: int
    target_end_year: int
    tcre: quantity('delta_degC')
    carbon_conversion: EmissionsQuantity
    scenario_target_temperature: quantity('delta_degC')

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def tcre_multiplier(self) -> quantity('delta_degC/(t CO2)'):
        return self.tcre / self.carbon_conversion


class TemperatureScoreConfig(PortfolioAggregationConfig):
    SCORE_RESULT_TYPE = 'score_result_type'
    # FIXME: Sooner or later, mutable default arguments cause problems.
    CONTROLS_CONFIG = TemperatureScoreControls(
        base_year=ProjectionControls.BASE_YEAR,
        target_end_year=ProjectionControls.TARGET_YEAR,
        tcre='2.2 delta_degC',
        carbon_conversion='3664.0 Gt CO2',
        scenario_target_temperature='1.5 delta_degC'
    )
