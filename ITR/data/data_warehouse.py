from abc import ABC
from typing import List
import pandas as pd
from pydantic import ValidationError
import numpy as np

import pint
import pint_pandas

ureg = pint.get_application_registry()
Q_ = ureg.Quantity

from ITR.interfaces import ICompanyAggregates
from ITR.data.data_providers import CompanyDataProvider, ProductionBenchmarkDataProvider, IntensityBenchmarkDataProvider
from ITR.configs import ColumnsConfig, TemperatureScoreConfig
from typing import Type
import logging


class DataWarehouse(ABC):
    """
    General data provider super class.
    """

    def __init__(self, company_data: CompanyDataProvider,
                 benchmark_projected_production: ProductionBenchmarkDataProvider,
                 benchmarks_projected_emission_intensity: IntensityBenchmarkDataProvider,
                 column_config: Type[ColumnsConfig] = ColumnsConfig,
                 tempscore_config: Type[TemperatureScoreConfig] = TemperatureScoreConfig):
        """
        Create a new data warehouse instance.

        :param company_data: CompanyDataProvider
        :param benchmark_projected_production: ProductionBenchmarkDataProvider
        :param benchmarks_projected_emission_intensity: IntensityBenchmarkDataProvider
        """
        self.company_data = company_data
        self.benchmark_projected_production = benchmark_projected_production
        self.benchmarks_projected_emission_intensity = benchmarks_projected_emission_intensity
        self.temp_config = tempscore_config
        self.column_config = column_config

    def get_preprocessed_company_data(self, company_ids: List[str]) -> List[ICompanyAggregates]:
        """
        Get all relevant data for a list of company ids. This method should return a list of ICompanyAggregates
        instances.

        :param company_ids: A list of company IDs (ISINs)
        :return: A list containing the company data and additional precalculated fields
        """
        print(f"company_ids = {company_ids}\n\n")
        company_data = self.company_data.get_company_data(company_ids)
        print(f"company_data = {company_data}\n\n")
        df_company_data = pd.DataFrame.from_records([c.dict() for c in company_data])

        print(f"df_company_data = {df_company_data}\n\n")
        assert pd.Series(company_ids).isin(df_company_data.loc[:, self.column_config.COMPANY_ID]).all(), \
            "some of the company ids are not included in the fundamental data"

        company_info_at_base_year = self.company_data.get_company_intensity_and_production_at_base_year(company_ids)
        projected_production = self.benchmark_projected_production.get_company_projected_production(
            company_info_at_base_year)

        df_company_data.loc[:, self.column_config.CUMULATIVE_TRAJECTORY] = self._get_cumulative_emission(
            projected_emission_intensity=self.company_data.get_company_projected_intensities(company_ids),
            projected_production=projected_production).to_numpy()

        df_company_data.loc[:, self.column_config.CUMULATIVE_TARGET] = self._get_cumulative_emission(
            projected_emission_intensity=self.company_data.get_company_projected_targets(company_ids),
            projected_production=projected_production).to_numpy()

        df_company_data.loc[:, self.column_config.CUMULATIVE_BUDGET] = self._get_cumulative_emission(
            projected_emission_intensity=self.benchmarks_projected_emission_intensity.get_SDA_intensity_benchmarks(
                company_info_at_base_year),
            projected_production=projected_production).to_numpy()

        print(f"self.benchmarks_projected_emission_intensity.benchmark_global_budget = {self.benchmarks_projected_emission_intensity.benchmark_global_budget}\n\n")
        df_company_data.loc[:,
        self.column_config.BENCHMARK_GLOBAL_BUDGET] = self.benchmarks_projected_emission_intensity.benchmark_global_budget
        df_company_data.loc[:,
        self.column_config.BENCHMARK_TEMP] = self.benchmarks_projected_emission_intensity.benchmark_temperature

        companies = df_company_data.to_dict(orient="records")

        aggregate_company_data: List[ICompanyAggregates] = [ICompanyAggregates.parse_obj(company) for company in
                                                            companies]

        return aggregate_company_data

    def _convert_df_to_model(self, df_company_data: pd.DataFrame) -> List[ICompanyAggregates]:

        """
        transforms Dataframe Company data and preprocessed values into list of IDataProviderTarget instances

        :param df_company_data: pandas Dataframe with targets
        :return: A list containing the targets
        """
        logger = logging.getLogger(__name__)
        df_company_data = df_company_data.where(pd.notnull(df_company_data), None).replace(
            {np.nan: None})  # set NaN to None since NaN is float instance
        companies_data_dict = df_company_data.to_dict(orient="records")
        model_companies: List[ICompanyAggregates] = []
        for company_data in companies_data_dict:
            try:
                model_companies.append(ICompanyAggregates.parse_obj(company_data))
            except ValidationError as e:
                print(__name__, e)
                logger.warning(
                    "DW: (one of) the input(s) of company %s is invalid and will be skipped" % company_data[
                        self.column_config.COMPANY_NAME])
                pass
        return model_companies

    def _get_cumulative_emission(self, projected_emission_intensity: pd.DataFrame, projected_production: pd.DataFrame
                                 ) -> pd.Series:
        """
        get the weighted sum of the projected emission times the projected production
        :param projected_emission_intensity: series of projected emissions
        :param projected_production: series of projected production series
        :return: weighted sum of production and emission
        """

        return projected_emission_intensity.reset_index(drop=True).multiply(projected_production.reset_index(
            drop=True)).sum(axis=1)
