from __future__ import annotations

import numpy as np
import pandas as pd
from uncertainties import ufloat
from uncertainties.core import Variable as utype
from uncertainties import unumpy as unp

from operator import add
from enum import Enum
from typing import Optional, Dict, List, Literal, Union
from typing import TYPE_CHECKING, Callable
from pydantic import BaseModel, parse_obj_as, validator, root_validator
from dataclasses import dataclass

import pint
from ITR.data.osc_units import ureg, Q_, M_
from pint.errors import DimensionalityError


@dataclass
class ProjectionControls:
    LOWER_PERCENTILE: float = 0.1
    UPPER_PERCENTILE: float = 0.9

    LOWER_DELTA: float = -0.10
    UPPER_DELTA: float = +0.03

    # FIXME: Should agree with TemperatureScoreConfig.CONTROLS_CONFIG
    BASE_YEAR: int = 2019
    TARGET_YEAR: int = 2050
    TREND_CALC_METHOD: Callable[[pd.DataFrame], pd.DataFrame] = staticmethod(pd.DataFrame.median)


class PintModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

# List of all the production units we know
_production_units = [ "Wh", "t Steel", "pkm", "tkm", "boe", "t Aluminum", "t Cement", "USD", "m**2" ]
_ei_units = [f"t CO2/({pu})" if ' ' in pu else f"t CO2/{pu}" for pu in _production_units]

# Borrowed from https://github.com/hgrecco/pint/issues/1166
registry = ureg

schema_extra = dict(definitions=[
    dict(
        Quantity=dict(type="string"),
        # We don't need EmissionsQuantity separately because Quantity does all we nmeed
        ProductionQuantity=dict(type="List[str]"),
        EI_Quantity=dict(type="List[str]"),
    )
])


def quantity(dimensionality: str) -> type:
    """A method for making a pydantic compliant Pint quantity field type."""

    try:
        registry.get_dimensionality(dimensionality)
    except KeyError:
        raise ValueError(f"{dimensionality} is not a valid dimensionality in pint!")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        quantity = Q_(value)
        if quantity.is_compatible_with(cls.dimensionality):
            return quantity
        assert quantity.check(cls.dimensionality), f"Dimensionality must be {cls.dimensionality} {breakpoint()}"
        return quantity

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            {"$ref": "#/definitions/Quantity"}
        )
    
    return type(
        "Quantity",
        (pint.Quantity,),
        dict(
            __get_validators__=__get_validators__,
            __modify_schema__=__modify_schema__,
            dimensionality=dimensionality,
            validate=validate,
        ),
    )


class MyModel(BaseModel):

    distance: quantity("[length]")
    speed: quantity("[length]/[time]")

    class Config:
        validate_assignment = True
        schema_extra = schema_extra
        json_encoders = {
            pint.Quantity: str,
        }
# end of borrowing


def emissions_quantity(dimensionality: str) -> type:
    """A method for making a pydantic compliant Pint quantity field type."""

    try:
        registry.get_dimensionality(dimensionality)
    except KeyError:
        raise ValueError(f"{dimensionality} is not a valid dimensionality in pint!")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, dict):
            quantity = Q_(value['units'])
        else:
            quantity = Q_(value)
        if quantity.is_compatible_with(cls.dimensionality):
            return quantity
        assert quantity.check(cls.dimensionality), f"Dimensionality must be {cls.dimensionality} {breakpoint()}"
        return quantity

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            {"$ref": "#/definitions/EmissionsQuantity"}
        )
    
    return type(
        "Quantity",
        (pint.Quantity,),
        dict(
            __get_validators__=__get_validators__,
            __modify_schema__=__modify_schema__,
            dimensionality=dimensionality,
            validate=validate,
        ),
    )

class ProductionQuantity(BaseModel):

    dims_list: List[str]

    @validator('dims_list')
    def units_must_be_registered(cls, v):
        for d in v:
            try:
                registry.get_dimensionality(d)
            except KeyError:
                raise ValueError(f"{d} is not a valid dimensionality in pint!")
        return v

    class Config:
        validate_assignment = True
        schema_extra = schema_extra
        json_encoders = {
            pint.Quantity: str,
        }

def production_quantity(dims_list: List[str]) -> type:
    """A method for making a pydantic compliant Pint production quantity."""

    try:
        for dimensionality in dims_list:
            registry.get_dimensionality(dimensionality)
    except KeyError:
        raise ValueError(f"{dimensionality} is not a valid dimensionality in pint!")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, dict):
            quantity = Q_(value['units'])
        else:
            quantity = Q_(value)
        for dimensionality in ProductionQuantity(dims_list=dims_list).dims_list:
            if quantity.check(dimensionality):
                return quantity
        raise DimensionalityError(value.units, f"in [{ProductionQuantity(dims_list).dims_list}]")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            {"$ref": "#/definitions/ProductionQuantity"}
        )
    
    return type(
        "ProductionQuantity",
        (ProductionQuantity,),
        dict(
            __get_validators__=__get_validators__,
            __modify_schema__=__modify_schema__,
            dims_list=f"List[str] = {dims_list}",
            validate=validate,
        ),
    )


class EI_Quantity(BaseModel):

    dims_list: List[str]

    @validator('dims_list')
    def units_must_be_registered(cls, v):
        for d in v:
            try:
                registry.get_dimensionality(d)
            except KeyError:
                raise ValueError(f"{d} is not a valid dimensionality in pint!")
        return v

    class Config:
        validate_assignment = True
        schema_extra = schema_extra
        json_encoders = {
            pint.Quantity: str,
        }

def ei_quantity(dims_list: List[str]) -> type:
    """A method for making a pydantic compliant Pint Emissions Intensity (EI) quantity."""

    try:
        for dimensionality in dims_list:
            registry.get_dimensionality(dimensionality)
    except KeyError:
        raise ValueError(f"{dimensionality} is not a valid dimensionality in pint!")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, dict):
            quantity = Q_(value['units'])
        else:
            quantity = Q_(value)
        for dimensionality in EI_Quantity(dims_list=dims_list).dims_list:
            if quantity.check(dimensionality):
                return quantity
        raise DimensionalityError(value.units, f"in [{EI_Quantity(dims_list).dims_list}]")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            {"$ref": "#/definitions/EI_Quantity"}
        )
    
    return type(
        "EI_Quantity",
        (EI_Quantity,),
        dict(
            __get_validators__=__get_validators__,
            __modify_schema__=__modify_schema__,
            dims_list=f"List[str] = {dims_list}",
            validate=validate,
        ),
    )

# FIXME: delete this when we are done converting to new Pint
class ProductionMetric(BaseModel):
    units: str
    @validator('units')
    def unit_must_be_production(cls, v):
        qty = ureg(v)
        for pu in _production_units:
            if qty.is_compatible_with(pu):
                return v
        raise ValueError(f"cannot convert {v} to units of production")

    def __str__(self):
        return self.units


# Right now we have only one kind of Emissions: Co2
class EmissionsMetric(BaseModel):
    units: str
    @validator('units')
    def units_must_be_tCO2(cls, v):
        qty = ureg(v)
        if qty.is_compatible_with("t CO2"):
            return v
        raise ValueError(f"cannot convert {v} to t CO2")


class IntensityMetric(BaseModel):
    units: str 
    @validator('units')
    def units_must_be_EI(cls, v):
        qty = ureg(v)
        for ei_u in _ei_units:
            if qty.is_compatible_with(ei_u):
                return v
        raise ValueError(f"cannot convert {v} to known t CO2/production unit")


class OSC_Metric(BaseModel):
    units: str 
    @validator('units')
    def units_must_be_OSC(cls, v):
        if v == 'dimensionless':
            return v
        try:
            if ProductionMetric.unit_must_be_production(v):
                return v
        except ValueError:
            try:
                if EmissionsMetric.units_must_be_tCO2(v):
                    return v
            except ValueError:
                try:
                    if IntensityMetric.units_must_be_EI(v):
                        return v
                except ValueError:
                    raise ValueError(f"cannot understand {v} as OSC_Metric")


class SortableEnum(Enum):
    def __str__(self):
        return self.name

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            order = list(self.__class__)
            return order.index(self) >= order.index(other)
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            order = list(self.__class__)
            return order.index(self) > order.index(other)
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            order = list(self.__class__)
            return order.index(self) <= order.index(other)
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            order = list(self.__class__)
            return order.index(self) < order.index(other)
        return NotImplemented


class EScope(SortableEnum):
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S1S2 = "S1+S2"
    S1S2S3 = "S1+S2+S3"

    @classmethod
    def get_scopes(cls) -> List[str]:
        """
        Get a list of all scopes.
        :return: A list of EScope string values
        """
        return ['S1', 'S2', 'S3', 'S1S2', 'S1S2S3']

    @classmethod
    def get_result_scopes(cls) -> List['EScope']:
        """
        Get a list of scopes that should be calculated if the user leaves it open.

        :return: A list of EScope objects
        """
        return [cls.S1S2, cls.S3, cls.S1S2S3]


class ETimeFrames(SortableEnum):
    """
    TODO: add support for multiple timeframes. Long currently corresponds to 2050.
    """
    SHORT = "short"
    MID = "mid"
    LONG = "long"


class ECarbonBudgetScenario(Enum):
    P25 = "25 percentile"
    P75 = "75 percentile"
    MEAN = "Average"


class EScoreResultType(Enum):
    DEFAULT = "Default"
    TRAJECTORY_ONLY = "Trajectory only"
    COMPLETE = "Complete"


class AggregationContribution(PintModel):
    company_name: str
    company_id: str
    temperature_score: quantity('delta_degC')
    contribution_relative: Optional[quantity('percent')]
    contribution: Optional[quantity('delta_degC')]

    def __getitem__(self, item):
        return getattr(self, item)


class Aggregation(PintModel):
    score: quantity('delta_degC')
    # proportion is a number from 0..1
    proportion: float
    contributions: List[AggregationContribution]

    def __getitem__(self, item):
        return getattr(self, item)


class ScoreAggregation(BaseModel):
    all: Aggregation
    influence_percentage: float
    grouped: Dict[str, Aggregation]

    def __getitem__(self, item):
        return getattr(self, item)


class ScoreAggregationScopes(BaseModel):
    S1S2: Optional[ScoreAggregation]
    S3: Optional[ScoreAggregation]
    S1S2S3: Optional[ScoreAggregation]

    def __getitem__(self, item):
        return getattr(self, item)


class ScoreAggregations(BaseModel):
    short: Optional[ScoreAggregationScopes]
    mid: Optional[ScoreAggregationScopes]
    long: Optional[ScoreAggregationScopes]

    def __getitem__(self, item):
        return getattr(self, item)


class PortfolioCompany(BaseModel):
    company_name: str
    company_id: str
    company_isin: Optional[str]
    investment_value: float
    user_fields: Optional[dict]

def pint_ify(x, units='dimensionless'):
    global stop_pint_ify

    try:
        if 'units' in units:
            breakoint()
            units = units['units']
    except TypeError:
        pass
    if x is None:
        return Q_(np.nan, units)
    if type(x) == str:
        if x.startswith('nan '):
            return Q_(np.nan, units)
        return ureg(x)
    if unp.isnan(x):
        return Q_(np.nan, units)
    if isinstance(x, pint.Quantity):
        # Emissions intensities can arrive as dimensionless if emissions_metric and production_metric are both None
        if unp.isnan(x.m) and x.u == 'dimensionless':
            return Q_(np.nan, units)
        return x
    return Q_(x, units)


def UProjections_to_IProjections(classtype, ul, metric):
    if ul is np.nan or (isinstance(ul, utype) and unp.isnan(ul)):
        breakpoint()
        return ul
    if ul is None:
        return ul
    for x in ul:
        if isinstance(x, classtype):
            return ul
    units = metric['units']
    try:
        if 'units' in units:
            breakpoint()
            units = units['units']
    except TypeError:
        pass
    pl = [dict(x) for x in ul]
    for x in pl:
        if x['value'] is None or unp.isnan(x['value']):
            x['value'] = Q_(np.nan, units)
        else:
            x['value'] = pint_ify(x['value'], units)
    return pl


# U is Unquantified
class UProjection(BaseModel):
    year: int
    value: Optional[float]


# When IProjection is NULL, we don't actually know its type, so we instantiate that later
class IProjection(PintModel):
    year: int
    value: Optional[pint.Quantity]


class IBenchmark(BaseModel):
    sector: str
    region: str
    benchmark_metric: OSC_Metric
    projections: List[IProjection]

    def __init__(self, benchmark_metric, projections, *args, **kwargs):
        # FIXME: Probably want to define `target_end_year` to be 2051, not 2050...
        super().__init__(benchmark_metric=benchmark_metric,
                         projections=UProjections_to_IProjections(IProjection, projections, benchmark_metric),
                         *args, **kwargs)
        # Sadly we need to build the full projection range before cutting it down to size...
        # ...until Tiemann learns the bi-valence of dict and Model parameters
        self.projections = [p for p in self.projections
                            if p.year in range(ProjectionControls.BASE_YEAR,
                                               ProjectionControls.TARGET_YEAR+1)]


    def __getitem__(self, item):
        return getattr(self, item)


class IBenchmarks(BaseModel):
    benchmarks: List[IBenchmark]

    def __getitem__(self, item):
        return getattr(self, item)


class IProductionBenchmarkScopes(BaseModel):
    S1S2: Optional[IBenchmarks]
    S3: Optional[IBenchmarks]
    S1S2S3: Optional[IBenchmarks]


class IEIBenchmarkScopes(PintModel):
    S1S2: Optional[IBenchmarks]
    S3: Optional[IBenchmarks]
    S1S2S3: Optional[IBenchmarks]
    benchmark_temperature: quantity('delta_degC')
    benchmark_global_budget: quantity('Gt CO2')
    is_AFOLU_included: bool

    def __init__(self, benchmark_temperature, benchmark_global_budget, *args, **kwargs):
        super().__init__(benchmark_temperature=pint_ify(benchmark_temperature, 'delta_degC'),
                         benchmark_global_budget=pint_ify(benchmark_global_budget, 'Gt CO2'),
                         *args, **kwargs)

    def __getitem__(self, item):
        return getattr(self, item)


class ICompanyEIProjection(PintModel):
    year: int
    value: Optional[ei_quantity(_ei_units)]

    def add(self, o):
        assert self.year==o.year, f"{breakpoint()}"
        return IEIRealization(year=self.year, value = self.value + o.value)


class ICompanyEIProjections(BaseModel):
    ei_metric: IntensityMetric
    projections: List[ICompanyEIProjection]

    def __init__(self, ei_metric, projections, *args, **kwargs):
        super().__init__(ei_metric=ei_metric,
                         projections=UProjections_to_IProjections(ICompanyEIProjection, projections,
                                                                  ei_metric.dict() if isinstance(ei_metric, BaseModel) else ei_metric),
                         *args, **kwargs)

    def __getitem__(self, item):
        return getattr(self, item)


class ICompanyEIProjectionsScopes(BaseModel):
    S1: Optional[ICompanyEIProjections]
    S2: Optional[ICompanyEIProjections]
    S1S2: Optional[ICompanyEIProjections]
    S3: Optional[ICompanyEIProjections]
    S1S2S3: Optional[ICompanyEIProjections]

    def __getitem__(self, item):
        return getattr(self, item)


class IProductionRealization(BaseModel):
    year: int
    value: Optional[production_quantity(_production_units)]


class IEmissionRealization(PintModel):
    year: int
    value: Optional[emissions_quantity('t CO2')]

    def add(self, o):
        assert self.year==o.year
        return IEmissionRealization(year=self.year, value = self.value + o.value)


class IHistoricEmissionsScopes(PintModel):
    S1: List[IEmissionRealization]
    S2: List[IEmissionRealization]
    S1S2: List[IEmissionRealization]
    S3: List[IEmissionRealization]
    S1S2S3: List[IEmissionRealization]


class IEIRealization(PintModel):
    year: int
    value: Optional[ei_quantity(_ei_units)]

    def add(self, o):
        assert self.year==o.year
        return IEIRealization(year=self.year, value = self.value + o.value)


class IHistoricEIScopes(PintModel):
    S1: List[IEIRealization]
    S2: List[IEIRealization]
    S1S2: List[IEIRealization]
    S3: List[IEIRealization]
    S1S2S3: List[IEIRealization]


class IHistoricData(PintModel):
    productions: Optional[List[IProductionRealization]]
    emissions: Optional[IHistoricEmissionsScopes]
    emissions_intensities: Optional[IHistoricEIScopes]


class ITargetData(PintModel):
    netzero_year: Optional[int]
    target_type: Union[Literal['intensity'], Literal['absolute'], Literal['Intensity'], Literal['Absolute']]
    target_scope: EScope
    target_start_year: Optional[int]
    target_base_year: int
    target_end_year: int

    target_base_year_qty: float
    target_base_year_unit: str
    target_reduction_pct: float

    @root_validator
    def must_be_greater_than_2022(cls, v):
        if v['target_end_year'] < 2023:
            raise ValueError(f"Scope {v['target_scope']}: Target end year ({v['target_end_year']}) must be greater than 2022")
        return v


class ICompanyData(PintModel):
    company_name: str
    company_id: str

    region: str  # TODO: make SortableEnums
    sector: str  # TODO: make SortableEnums
    target_probability: float = 0.5

    target_data: Optional[List[ITargetData]]
    historic_data: Optional[IHistoricData]

    country: Optional[str]

    emissions_metric: Optional[emissions_quantity('t CO2')]    # Typically use t CO2 for MWh/GJ and Mt CO2 for TWh/PJ
    production_metric: Optional[production_quantity(_production_units)]  # Optional because it can be inferred from sector and region
    
    # These three instance variables match against financial data below, but are incomplete as historic_data and target_data
    base_year_production: Optional[production_quantity(_production_units)]
    ghg_s1s2: Optional[emissions_quantity('t CO2')]
    ghg_s3: Optional[emissions_quantity('t CO2')]

    industry_level_1: Optional[str]
    industry_level_2: Optional[str]
    industry_level_3: Optional[str]
    industry_level_4: Optional[str]

    company_revenue: Optional[float]
    company_market_cap: Optional[float]
    company_enterprise_value: Optional[float]
    company_ev_plus_cash: Optional[float]
    company_total_assets: Optional[float]
    company_cash_equivalents: Optional[float]

    # Initialized later when we have benchmark information.  It is OK to initialize as None and fix later.
    # They will show up as {'S1S2': { 'projections': [ ... ] }}
    projected_targets: Optional[ICompanyEIProjectionsScopes]
    projected_intensities: Optional[ICompanyEIProjectionsScopes]

    # TODO: Do we want to do some sector inferencing here?
    
    def _fixup_year_value_list(self, ListType, u_list, metric, inferred_metric):
        # u_list is unprocessed; i_list is processed; r_list is returned list
        i_list = [ul.dict() if isinstance(ul, BaseModel)
                  # In Python 3.9, dictionary union of x, y is x | y
                  # In Python 3.8, it's {**x, **y}
                  else {**{'year':ul['year']}, **{'value':Q_(ul['value'])
                                                  # Make NaNs dimensionless for now...we will fixup below
                                                  if ul['value'] is not None else Q_(np.nan, 'dimensionless')}}
                  for ul in u_list]
        if not i_list:
            return []
        if metric is None:
            try:
                metric = next(str(x['value'].u) for x in i_list if str(x['value'].u) != 'dimensionless')
            except StopIteration as e:
                # TODO: If everything in the list is empty, why not NULL it out and return []?
                metric = inferred_metric
        elif isinstance(metric, dict):
            metric = metric['units']
        else:
            metric = metric.u
        for il in i_list:
            if str(il['value'].u) == 'dimensionless':
                il['value'] = Q_(il['value'].m, metric)
        r_list = UProjections_to_IProjections(ListType, i_list, {'units':metric})
        return r_list
    
    def _sector_to_production_units(self, sector, region="Global"):
        sector_unit_dict = {
            'Electricity Utilities': { 'North America':'MWh', 'Global': 'GJ' },
            'Gas Utilities': { 'Global': 'PJ' },
            'Utilities': { 'Global': 'PJ' },
            'Steel': { 'Global': 't Steel' },
            'Aluminum': { 'Global': 't Aluminum' },
            'Oil & Gas': { 'Global': 'mmboe' },
            'Autos': { 'Global': 'pkm' },
            'Trucking': { 'Global': 'tkm' },
            'Cement': { 'Global': 't Cement' },
            'Construction Buildings': { 'Global': 'billion USD' },
            'Residential Buildings': { 'Global': 'billion m**2' }, # Should it be 'built m**2' ?
            'Commercial Buildings': { 'Global': 'billion m**2' }, # Should it be 'built m**2' ?
            'Textiles': { 'Global': 'billion USD' },
            'Chemicals': { 'Global': 'billion USD' },
        }
        units = None
        if sector_unit_dict.get(sector):
            region_unit_dict = sector_unit_dict[sector]
            if region_unit_dict.get(region):
                units = region_unit_dict[region]
            else:
                units = region_unit_dict['Global']
        else:
            raise ValueError(f"No source of production metrics for {self.company_name}")
        return units        

    def _fixup_ei_projections(self, projections, production_metric, emissions_metric, sector, region):
        if projections is None or isinstance(projections, ICompanyEIProjectionsScopes):
            return projections
        ei_metric = None
        if emissions_metric is None and production_metric is None:
            inferred_emissions_metric = 't CO2'
            inferred_production_metric = self._sector_to_production_units(sector, region)
        else:
            if isinstance(emissions_metric, dict):
                inferred_emissions_metric = emissions_metric['units']
            else:
                inferred_emissions_metric = emissions_metric
            if isinstance(production_metric, dict):
                inferred_production_metric = production_metric['units']
            else:
                inferred_production_metric = production_metric
        inferred_ei_metric = f"{inferred_emissions_metric}/({inferred_production_metric})"
        for scope in projections:
            if projections[scope] is None:
                continue
            projections[scope]['projections'] = self._fixup_year_value_list(ICompanyEIProjectionsScopes, projections[scope]['projections'], None, inferred_ei_metric)
            ei_metric = f"{projections[scope]['projections'][0]['value'].u:~P}"
            projections[scope]['ei_metric'] = {'units':ei_metric}
        model_projections = ICompanyEIProjectionsScopes(**projections)
        return model_projections

    def _fixup_historic_data(self, historic_data, production_metric, emissions_metric, sector, region):
        if historic_data is None:
            return None
        if production_metric is None:
            inferred_production_metric = self._sector_to_production_units(sector, region)
        elif isinstance(production_metric, dict):
            inferred_production_metric = production_metric['units']
        else:
            inferred_production_metric = production_metric
        if not historic_data.get('productions'):
            productions = None
        else:
            productions = self._fixup_year_value_list(IProductionRealization, historic_data['productions'], production_metric, inferred_production_metric)
        if emissions_metric is None:
            if production_metric in ['TWh', 'PJ', 'mmboe']:
                inferred_emissions_metric = 'Mt CO2'
            else:
                inferred_emissions_metric = 't CO2'
        elif isinstance(emissions_metric, dict):
            inferred_emissions_metric = emissions_metric['units']
        else:
            inferred_emissions_metric = emissions_metric
        if not historic_data.get('emissions'):
            emissions = None
        else:
            emissions = {}
            for scope in historic_data['emissions']:
                emissions[scope] = self._fixup_year_value_list(IEmissionRealization, historic_data['emissions'][scope], emissions_metric, inferred_emissions_metric)
        if not historic_data.get('emissions_intensities'):
            emissions_intensities = None
        else: 
            emissions_intensities = {}
            inferred_ei_metric = f"{inferred_emissions_metric}/({inferred_production_metric})"
            for scope in historic_data['emissions_intensities']:
                emissions_intensities[scope] = self._fixup_year_value_list(IEIRealization, historic_data['emissions_intensities'][scope], None, inferred_ei_metric)

        # Tempting to rewrite history here to push S3 into S1S2, but we have to wait until projections are finished
        model_historic_data = IHistoricData(productions=productions, emissions=emissions, emissions_intensities=emissions_intensities)
        return model_historic_data

    def _get_base_realization_from_historic(self, realized_values: List[PintModel], units, base_year=None):
        valid_realizations = [rv for rv in realized_values if not unp.isnan(rv.value)]
        if not valid_realizations:
            retval = realized_values[0].copy()
            retval.year = None
            return retval
        valid_realizations.sort(key=lambda x:x.year, reverse=True)
        if base_year and valid_realizations[0].year != base_year:
            retval = realized_values[0].copy()
            retval.year = base_year
            retval.value = Q_(np.nan, units)
            return retval
        return valid_realizations[0]

    def __init__(self, historic_data=None, projected_targets=None, projected_intensities=None, emissions_metric=None,
                 production_metric=None, base_year_production=None, ghg_s1s2=None, ghg_s3=None, *args, **kwargs):
        super().__init__(historic_data=self._fixup_historic_data(historic_data, production_metric, emissions_metric, kwargs.get('sector'), kwargs.get('region')),
                         # Not necessarily initialized here; may be fixed up if initially None after benchmark info is set
                         projected_targets=self._fixup_ei_projections(projected_targets, production_metric, emissions_metric, kwargs.get('sector'), kwargs.get('region')),
                         projected_intensities=self._fixup_ei_projections(projected_intensities, production_metric, emissions_metric, kwargs.get('sector'), kwargs.get('region')),
                         emissions_metric=emissions_metric,
                         production_metric=production_metric,
                         *args, **kwargs)
        # In-bound parameters are dicts, which are converted to models by __super__ and stored as instance variables
        if production_metric is None:
            units = self._sector_to_production_units(self.sector, self.region)
            self.production_metric = parse_obj_as(ProductionMetric, {'units': units})
            if emissions_metric is None:
                self.emissions_metric = parse_obj_as(EmissionsMetric, {'units': 't CO2'})
        elif emissions_metric is None:
            if self.production_metric.units in ['TWh', 'PJ', 'MFe_ton', 'megaFe_ton', 'mmboe']:
                self.emissions_metric = parse_obj_as(EmissionsMetric, {'units': 'Mt CO2'})
            else:
                self.emissions_metric = parse_obj_as(EmissionsMetric, {'units': 't CO2'})
            # TODO: Should raise a warning here
        base_year = None
        if base_year_production is not None:
            self.base_year_production = pint_ify(base_year_production, self.production_metric.units)
        elif self.historic_data and self.historic_data.productions:
            # TODO: This is a hack to get things going.
            base_realization = self._get_base_realization_from_historic(self.historic_data.productions, self.production_metric.units, base_year)
            base_year = base_realization.year
            self.base_year_production = base_realization.value
        else:
            # raise ValueError(f"missing historic data for base_year_production for {self.company_name}")
            self.base_year_production = Q_(np.nan, self.production_metric.units)
        if ghg_s1s2 is not None:
            self.ghg_s1s2=pint_ify(ghg_s1s2, self.emissions_metric.units)
        elif self.historic_data and self.historic_data.emissions:
            if self.historic_data.emissions.S1S2:
                base_realization = self._get_base_realization_from_historic(self.historic_data.emissions.S1S2, self.emissions_metric.units, base_year)
                base_year = base_year or base_realization.year
                self.ghg_s1s2 = base_realization.value
            elif self.historic_data.emissions.S1 and self.historic_data.emissions.S2:
                base_realization_s1 = self._get_base_realization_from_historic(self.historic_data.emissions.S1, self.emissions_metric.units, base_year)
                base_realization_s2 = self._get_base_realization_from_historic(self.historic_data.emissions.S2, self.emissions_metric.units, base_year)
                base_year = base_year or base_realization_s1.year
                self.ghg_s1s2 = base_realization_s1.value + base_realization_s2.value
        if self.ghg_s1s2 is None and self.historic_data and self.historic_data.emissions_intensities:
            intensity_units = (Q_(1.0, self.emissions_metric.units) / Q_(1.0, self.production_metric.units)).units
            if self.historic_data.emissions_intensities.S1S2:
                base_realization = self._get_base_realization_from_historic(self.historic_data.emissions_intensities.S1S2, intensity_units, base_year)
                base_year = base_year or base_realization.year
                self.ghg_s1s2 = base_realization.value * self.base_year_production
            elif self.historic_data.emissions_intensities.S1 and self.historic_data.emissions_intensities.S2:
                base_realization_s1 = self._get_base_realization_from_historic(self.historic_data.emissions_intensities.S1, intensity_units, base_year)
                base_realization_s2 = self._get_base_realization_from_historic(self.historic_data.emissions_intensities.S2, intensity_units, base_year)
                base_year = base_year or base_realization_s1.year
                self.ghg_s1s2 = (base_realization_s1.value + base_realization_s2.value) * self.base_year_production
            else:
                raise ValueError(f"missing S1S2 historic intensity data for {self.company_name}")
        if self.ghg_s1s2 is None:
            raise ValueError(f"missing historic emissions or intensity data to calculate ghg_s1s2 for {self.company_name}")
        if ghg_s3 is not None:
            self.ghg_s3 = pint_ify(ghg_s3, self.emissions_metric.units)
        elif self.historic_data and self.historic_data.emissions and self.historic_data.emissions.S3:
            base_realization_s3 = self._get_base_realization_from_historic(self.historic_data.emissions.S3, self.emissions_metric.units, base_year)
            self.ghg_s3 = base_realization_s3.value
        if self.ghg_s3 is None and self.historic_data and self.historic_data.emissions_intensities:
            if self.historic_data.emissions_intensities.S3:
                intensity_units = (Q_(1.0, self.emissions_metric.units) / Q_(1.0, self.production_metric.units)).units
                base_realization_s3 = self._get_base_realization_from_historic(self.historic_data.emissions_intensities.S3, intensity_units, base_year)
                self.ghg_s3 = base_realization_s3.value * self.base_year_production


class ICompanyAggregates(ICompanyData):
    cumulative_budget: emissions_quantity('t CO2')
    cumulative_trajectory: emissions_quantity('t CO2')
    cumulative_target: emissions_quantity('t CO2')
    benchmark_temperature: quantity('delta_degC')
    benchmark_global_budget: emissions_quantity('t CO2')

    # projected_targets: Optional[ICompanyEIProjectionsScopes]
    # projected_intensities: Optional[ICompanyEIProjectionsScopes]

    def __init__(self, cumulative_budget, cumulative_trajectory, cumulative_target,
                 benchmark_temperature, benchmark_global_budget,
                 *args, **kwargs):
        super().__init__(cumulative_budget=pint_ify(cumulative_budget, 't CO2'),
                         cumulative_trajectory=pint_ify(cumulative_trajectory, 't CO2'),
                         cumulative_target=pint_ify(cumulative_target, 't CO2'),
                         benchmark_temperature=pint_ify(benchmark_temperature, 'delta_degC'),
                         benchmark_global_budget=pint_ify(benchmark_global_budget, 'Gt CO2'),
                         *args, **kwargs)


class TemperatureScoreControls(PintModel):
    base_year: int
    target_end_year: int
    projection_start_year: int
    projection_end_year: int
    tcre: quantity('delta_degC')
    carbon_conversion: emissions_quantity('t CO2')
    scenario_target_temperature: quantity('delta_degC')

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def tcre_multiplier(self) -> quantity('delta_degC/(t CO2)'):
        return self.tcre / self.carbon_conversion

# FIXME: Can somebody help sort out the circularities we have?
IEIRealization.update_forward_refs()
TemperatureScoreControls.update_forward_refs()