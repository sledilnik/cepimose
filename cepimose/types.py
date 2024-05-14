from cepimose.enums import AgeGroup, Gender, Region
from dataclasses import dataclass, field
import datetime
from typing import List, Optional, Union


@dataclass
class VaccinationByDayRow:
    """Represents on row of vaccinations by day table"""

    date: datetime.datetime
    first_dose: int
    second_dose: int = 0
    third_dose: int = 0


# ? TODO merge VaccinationByAgeRow and VaccinationByRegionRow into one dataclass
@dataclass
class VaccinationByAgeRow:
    age_group: str
    count_first: int
    count_second: int
    share_first: float
    share_second: float


# ? TODO rename VaccineSupplyUsage to VaccinesSuppliedUsed
@dataclass
class VaccineSupplyUsage:
    date: datetime.datetime
    supplied: int
    used: int


@dataclass
class VaccinationByRegionRow:
    region: str
    count_first: int
    count_second: int
    share_first: float
    share_second: float


@dataclass
class VaccinationByManufacturerRow:
    date: datetime.datetime
    pfizer: Optional[int]
    moderna: Optional[int]
    az: Optional[int]
    janssen: Optional[int]
    novavax: Optional[int]


@dataclass
class VaccinationDose:
    date: datetime.datetime
    dose: int


@dataclass
class VaccinationMunShare:
    name: str
    dose1: int
    share1: float
    dose2: int
    share2: float
    population: int


@dataclass
class VaccinationAgeGroupByRegionOnDayDose:
    region: str
    total_count: int = 0
    group_count: int = 0
    total_share: float = 0.0
    group_share: float = 0.0


@dataclass
class VaccinationAgeGroupByRegionOnDay:
    region: str
    dose1: VaccinationAgeGroupByRegionOnDayDose
    dose2: VaccinationAgeGroupByRegionOnDayDose


@dataclass
class VaccinationsByGender:
    date: datetime.datetime
    female_first: int = 0
    female_second: int = 0
    male_first: int = 0
    male_second: int = 0


@dataclass
class DateRangeCommands_Requests:
    group: dict
    male1: dict
    male2: dict
    female1: dict
    female2: dict
    manufacturers: dict


@dataclass
class VaccinationsDateRangeManufacturer:
    name: str
    dose1: Optional[int] = 0
    dose2: Optional[int] = 0


@dataclass
class VaccinationsDoses:
    dose1: Optional[int] = 0
    dose2: Optional[int] = 0


@dataclass
class VaccinationsInDateRangeAgeGroupGender:
    date_start: datetime.datetime
    date_end: datetime.datetime
    age_group: AgeGroup
    male: VaccinationsDoses
    female: VaccinationsDoses


@dataclass
class VaccinationsDateRangeByGroup:
    date_from: datetime.datetime
    date_to: datetime.datetime
    property: Union[Region, AgeGroup]
    by_day: List[VaccinationByDayRow] = field(default_factory=list)
    male: Optional[VaccinationsDoses] = field(default_factory=VaccinationsDoses)
    female: Optional[VaccinationsDoses] = field(default_factory=VaccinationsDoses)
    pfizer: Optional[VaccinationsDoses] = field(default_factory=VaccinationsDoses)
    az: Optional[VaccinationsDoses] = field(default_factory=VaccinationsDoses)
    moderna: Optional[VaccinationsDoses] = field(default_factory=VaccinationsDoses)
    janssen: Optional[VaccinationsDoses] = field(default_factory=VaccinationsDoses)
    novavax: Optional[VaccinationsDoses] = field(default_factory=VaccinationsDoses)


@dataclass
class CommandQueryFrom:
    name: str
    entity: str
    type: int


@dataclass
class LabDashboard:
    """Represents data from NIJZ dashboard:
        'Prikaz števila opravljenih cepljenj, testiranj in potrjenih okužb s covid-19 v SLoveniji'

    source: https://app.powerbi.com/view?r=eyJrIjoiMDc3MDk4MmQtOGE4NS00YTRkLTgyYjktNWQzMjk5ODNlNjVhIiwidCI6ImFkMjQ1ZGFlLTQ0YTAtNGQ5NC04OTY3LTVjNjk5MGFmYTQ2MyIsImMiOjl9&pageName=ReportSection24198f7e6d06db643832
    """

    date: datetime.datetime = None
    pcr: int = None
    hat: int = None
    confirmed: int = None
    active_estimated: int = None
    cases_active_100k: float = None
    cases_active_7days: float = None
    date_start: datetime.datetime = None
    pcr_total: int = None
    hat_total: int = None
    confirmed_total: int = None
    male_total: int = None
    female_total: int = None
    vaccinated_first_dose: int = None
    vaccinated_fully: int = None
