import datetime
from typing import Union
import requests
import time
from .data import (
    _source,
    _vaccinations_dashboard_headers,
    _lab_dashboard_headers,
    _vaccinations_by_day_req,
    _vaccinations_by_age_req,
    _vaccines_supplied_and_used_req,
    _vaccinations_by_region_req,
    _vaccines_supplied_by_manufacturer_req,
    _vaccines_supplied_by_manufacturer_cum_req,
    _vaccination_by_age_group_requests,
    _vaccinations_by_region_by_day_requests,
    _vaccinations_municipalities_share_req,
    _vaccinations_timestamp_req,
    _vaccinations_age_group_by_region_on_day_requests,
    _vaccination_by_manufacturer_supplied_used_requests,
    _vaccinations_gender_by_date_requests,
    _create_vaccinations_data_range_request,
    _create_in_range_age_group_gender_requests,
    _vaccinations_by_manufacturer_used_request,
    _lab_start_ts_req,
    _lab_end_ts_req,
    _lab_end_ts_req_with_cache,
    _lab_PCR_tests_performed_req,
    _lab_PCR_tests_performed_req_with_cache,
    _lab_PCR_total_tests_performed_req,
    _lab_active_cases_estimated_req,
    _lab_confirmed_total_male_req,
    _lab_total_vaccinated_first_dose_req,
    _lab_active_cases_100k_req,
    _lab_cases_total_confirmed_req,
    _lab_HAT_total_tests_performed_req,
    _lab_cases_confirmed_req,
    _lab_cases_confirmed_req_with_cache,
    _lab_confirmed_total_female_req,
    _lab_total_vaccinated_fully_req,
    _lab_cases_avg_7Days_req,
    _lab_HAT_tests_performed_req,
    _lab_HAT_tests_performed_req_with_cache,
)
from .parser import (
    _parse_vaccinations_by_age,
    _parse_vaccinations_by_day,
    _parse_vaccines_supplied_and_used,
    _parse_vaccinations_by_region,
    _parse_vaccines_supplied_by_manufacturer,
    _parse_vaccines_supplied_by_manufacturer_cum,
    _parse_vaccinations_by_age_group,
    _parse_vaccinations_by_region_by_day,
    _parse_vaccinations_by_municipalities_share,
    _parse_vaccinations_timestamp,
    _parse_vaccinations_age_group_by_region_on_day,
    _parse_vaccinations_by_manufacturer_supplied_used,
    _parse_vaccinations_gender_by_date,
    _parse_vaccinations_date_range,
    _parse_vaccinations_date_range_manufacturers_used,
    _create_vaccinations_by_manufacturer_parser,
    _parse_single_data,
)

from .types import (
    VaccinationByAgeRow,
    VaccinationByDayRow,
    VaccinationDose,
    VaccinationsByGender,
    VaccinationsDateRangeByGroup,
    VaccinationsDoses,
    VaccineSupplyUsage,
    VaccinationByRegionRow,
    VaccinationByManufacturerRow,
    VaccinationAgeGroupByRegionOnDay,
    VaccinationsInDateRangeAgeGroupGender,
    LabDashboard,
)

from .enums import Manufacturer, Region, AgeGroup, Gender

DAY_DELTA = datetime.timedelta(days=1)
FIRST_DATE = datetime.datetime(2020, 12, 26)
TODAY_TIME = datetime.datetime.today()
TODAY = datetime.datetime(TODAY_TIME.year, TODAY_TIME.month, TODAY_TIME.day)


def _get_data(req, parse_response, headers=_vaccinations_dashboard_headers):
    resp = requests.post(_source, headers=headers, json=req)
    resp.raise_for_status()
    return parse_response(resp.json())


def vaccinations_timestamp():
    """Gets data refresh time

    Returns:
        datetime: datetime representing NIJZ data refresh time
    """
    return _get_data(_vaccinations_timestamp_req, _parse_vaccinations_timestamp)


def vaccinations_by_day() -> "list[VaccinationByDayRow]":
    """Gets number of vaccinations by day


    Returns:
        list: a list of VaccinationByDayRow representing number of vaccinated
        persons with first dose and fully vaccinated.
    """
    return _get_data(_vaccinations_by_day_req, _parse_vaccinations_by_day)


def vaccinations_by_age() -> "list[VaccinationByAgeRow]":
    """Gets number of vaccinations and shares per age group for today

    Returns:
        list: a list of VaccinationByAgeRow representing number of vaccinated
        persons with first dose, fully vaccinated and corresponding shares per
        age group for today
    """
    return _get_data(_vaccinations_by_age_req, _parse_vaccinations_by_age)


def vaccines_supplied_and_used() -> "list[VaccineSupplyUsage]":
    """Gets cumulative number of supplied and used vaccines by day

    Returns:
        list: a list of VaccineSupplyUsage representing total supplied and used
        vaccines on particular day
    """
    return _get_data(_vaccines_supplied_and_used_req, _parse_vaccines_supplied_and_used)


def vaccinations_by_region() -> "list[VaccinationByRegionRow]":
    """Gets number of vaccinations and shares per region for today

    Returns:
        list: a list of VaccinationByRegionRow representing number of vaccinated
        persons with first dose, fully vaccinated and corresponding shares per
        region for today
    """
    return _get_data(_vaccinations_by_region_req, _parse_vaccinations_by_region)


def vaccines_supplied_by_manufacturer() -> "list[VaccinationByManufacturerRow]":
    """Gets number of supplied vaccines by manufacturer by day

    Returns:
        list: a list of VaccinationByManufacturerRow representing supplied
        vaccines by manufacturer on particular day
    """
    return _get_data(
        _vaccines_supplied_by_manufacturer_req, _parse_vaccines_supplied_by_manufacturer
    )


def vaccines_supplied_by_manufacturer_cumulative() -> "list[VaccinationByManufacturerRow]":
    """Gets cumulative number of supplied vaccines by manufacturer by day

    Returns:
        list: a list of VaccinationByManufacturerRow representing supplied
        vaccines by manufacturer on particular day
    """
    return _get_data(
        _vaccines_supplied_by_manufacturer_cum_req,
        _parse_vaccines_supplied_by_manufacturer_cum,
    )


# by age group
def vaccinations_by_age_group(
    group: AgeGroup = None,
) -> "dict[AgeGroup,list[VaccinationByDayRow]] or list[VaccinationByDayRow]":
    """Gets cumulative number of vaccinations for age group by day

    Args:
        group (enum[AgeGroup] | None): represents age group, default is None


    Returns:
        dict [group = None]: a dict with keys AgeGroup enum members and values as
        list of VaccinationByDayRow respresenting  number of vaccinated
        persons with first dose and fully vaccinated.

        list [group = AgeGroup enum member]: a list of VaccinationByDayRow
        respresenting  number of vaccinated persons with first dose and fully
        vaccinated for enum member.

    """
    obj = {}
    if group == None:

        key_value = _vaccination_by_age_group_requests.items()
        for key, req_list in key_value:
            req = req_list[0]
            obj[key] = _get_data(req, _parse_vaccinations_by_day)
        return obj

    req = _vaccination_by_age_group_requests[group][0]
    return _get_data(req, _parse_vaccinations_by_day)


# by region by day
def vaccinations_by_region_by_day(
    region: Region = None,
) -> "dict[Region, list[VaccinationByDayRow]]":
    # TODO make same return if arg is not None as vaccinations_by_age_group and vaccinations_age_group_by_region_on_day or vice verse
    """Gets cumulative number of vaccinations for region by day

    Args:
        group (enum[Region] | None): represents region, default is None


    Returns:
        dict [group = None]: a dict with keys Region enum members and values as
        list of VaccinationByDayRow respresenting  number of vaccinated
        persons with first dose and fully vaccinated.
        If arg [group] is set then returns only for that group.
    """
    obj = {}
    if region == None:
        key_value = _vaccinations_by_region_by_day_requests.items()
        for key, req_list in key_value:
            req = req_list[0]
            doses = _get_data(req, _parse_vaccinations_by_day)
            obj[key] = doses
        return obj

    req = _vaccinations_by_region_by_day_requests[region][0]
    doses = _get_data(req, _parse_vaccinations_by_day)
    obj[region] = doses

    return obj


def vaccinations_age_group_by_region_on_day(
    group: AgeGroup = None,
) -> "Union[dict[AgeGroup, list[VaccinationAgeGroupByRegionOnDay]],list[VaccinationAgeGroupByRegionOnDay]]":
    """Gets number of vaccinations for regions in each age group

    Args:
        group (enum[AgeGroup] | None): represents age group, default is None

    Returns:
        dict [group = None]: a dict with keys AgeGroup enum members and values as
        list of VaccinationAgeGroupByRegionOnDay respresenting number of vaccinated persons with first dose and fully vaccinated per region as a list of VaccinationAgeGroupByRegionOnDayDose representing region, cumulative number of vaccinated persons in age group, number of vaccinated person in region for age group with coresponding shares.

        list [group = AgeGroup enum member]: a list of VaccinationAgeGroupByRegionOnDay respresenting number of vaccinated persons with first dose and fully vaccinated per region as a list of VaccinationAgeGroupByRegionOnDayDose representing region, cumulative number of vaccinated persons in age group, number of vaccinated person in region for age group with coresponding shares.
    """
    obj = {}

    if group == None:
        key_value = _vaccinations_age_group_by_region_on_day_requests.items()
        for key, req_list in key_value:
            req = req_list[0]
            doses = _get_data(req, _parse_vaccinations_age_group_by_region_on_day)
            obj[key] = doses
        return obj

    req = _vaccinations_age_group_by_region_on_day_requests[group][0]
    doses = _get_data(req, _parse_vaccinations_age_group_by_region_on_day)
    return doses


# PAGE 2
# municipalities
def vaccinations_by_municipalities_share():
    """Gets number of vaccinations per municipality on today.

    Returns:
        list: a list of VaccinationMunShare representing municipality, vaccinated persons with first dose and fully vaccinated with coresponding shares and municipality's population.

    """
    return _get_data(
        _vaccinations_municipalities_share_req,
        _parse_vaccinations_by_municipalities_share,
    )


# PAGE 3
# manufacturers
def vaccinations_by_manufacturer_supplied_used(
    group: Manufacturer = None,
) -> "dict[Manufacturer, list[VaccineSupplyUsage]] or list[VaccineSupplyUsage]":
    """Gets cumulative number of supplied and used vaccines on delivery date.

    Returns:
        dict [group = None]: a dict with keys Manufacturer enum members and values as
        list of VaccineSupplyUsage representing manufacturer's cumulative number of supplied and used vaccines

        list [group = Manufacturer enum member]: list of VaccineSupplyUsage representing manufacturer's cumulative number of supplied and used vaccines
    """
    obj = {}

    if group == None:
        key_value = _vaccination_by_manufacturer_supplied_used_requests.items()
        for key, req_list in key_value:
            req = req_list[0]
            doses = _get_data(req, _parse_vaccinations_by_manufacturer_supplied_used)
            obj[key] = doses
        return obj

    req = _vaccination_by_manufacturer_supplied_used_requests[group][0]
    doses = _get_data(req, _parse_vaccinations_by_manufacturer_supplied_used)
    return doses


def vaccinations_by_manufacturer_used() -> "list[VaccinationByManufacturerRow]":
    """Gets number of used vaccines per manufacturer per day.

    Warning: There is some discrepancy for first supply and first use of Moderna and Astra Zeneca vaccine! Both vaccines were used before first supply! See: 2021-01-08 for Moderna, 2021-01-28 for Astra Zeneca

    Returns:
        list: a list of VaccinationByManufacturerRow representing each manufacturer's number of used vaccines on day.
    """
    obj = {}
    for manu in Manufacturer:
        print(manu)
        manufacturer_parser = _create_vaccinations_by_manufacturer_parser(manu)
        obj[manu] = _get_data(
            _vaccinations_by_manufacturer_used_request[manu],
            manufacturer_parser,
        )

    start_date = FIRST_DATE + DAY_DELTA
    end_date = TODAY

    result = []
    while start_date <= end_date:
        pfizer = list(filter(lambda x: x.date == start_date, obj[Manufacturer.PFIZER]))
        moderna = list(
            filter(lambda x: x.date == start_date, obj[Manufacturer.MODERNA])
        )
        az = list(filter(lambda x: x.date == start_date, obj[Manufacturer.AZ]))
        janssen = list(
            filter(lambda x: x.date == start_date, obj[Manufacturer.JANSSEN])
        )
        novavax = list(
            filter(lambda x: x.date == start_date, obj[Manufacturer.NOVAVAX])
        )
        try:
            pfizer_used = pfizer[0].dose if len(pfizer) != 0 else None
            moderna_used = moderna[0].dose if len(moderna) != 0 else None
            az_used = az[0].dose if len(az) != 0 else None
            janssen_used = janssen[0].dose if len(janssen) != 0 else None
            novavax_used = novavax[0].dose if len(novavax) != 0 else None
            result.append(
                VaccinationByManufacturerRow(
                    start_date,
                    pfizer_used,
                    moderna_used,
                    az_used,
                    janssen_used,
                    novavax_used,
                )
            )
        except:
            print(start_date, "Something went wrong")
            print(pfizer, moderna, az, janssen, novavax)
        start_date += DAY_DELTA
    return result


# PAGE 1
# gender
def vaccinations_gender_by_date(
    date: datetime.datetime = None,
) -> "Union[VaccinationsByGender, list[VaccinationsByGender]]":
    """Gets number of presons vaccinated with first dose and fully vaccinated persons by gender on day.

    Returns:
        list [date = None]: a list of VaccinationsByGender representing fully vaccinated and vaccinated persons with first dose by gender.

    """
    start = time.perf_counter()

    if date == None:
        result = []
        for day in _vaccinations_gender_by_date_requests:
            date = day["date"]
            female = day[Gender.FEMALE]
            male = day[Gender.MALE]
            female_first = _get_data(female[0], _parse_vaccinations_gender_by_date)
            female_second = _get_data(female[1], _parse_vaccinations_gender_by_date)
            male_first = _get_data(male[0], _parse_vaccinations_gender_by_date)
            male_second = _get_data(male[1], _parse_vaccinations_gender_by_date)
            result.append(
                VaccinationsByGender(
                    date=date,
                    female_first=female_first,
                    female_second=female_second,
                    male_first=male_first,
                    male_second=male_second,
                )
            )
        finish = time.perf_counter()
        print(f"Elapsed time: {finish - start}")
        return result

    filtered_days = list(
        filter(lambda item: item["date"] == date, _vaccinations_gender_by_date_requests)
    )

    if len(filtered_days) == 0:
        return None

    day = filtered_days[0]

    date = day["date"]
    female = day[Gender.FEMALE]
    male = day[Gender.MALE]
    female_first = _get_data(female[0], _parse_vaccinations_gender_by_date)
    female_second = _get_data(female[1], _parse_vaccinations_gender_by_date)
    male_first = _get_data(male[0], _parse_vaccinations_gender_by_date)
    male_second = _get_data(male[1], _parse_vaccinations_gender_by_date)
    finish = time.perf_counter()
    print(f"Elapsed time: {finish - start}")
    return VaccinationsByGender(
        date=date,
        female_first=female_first,
        female_second=female_second,
        male_first=male_first,
        male_second=male_second,
    )


# PAGE 1
def vaccinations_date_range(
    property: Union[Region, AgeGroup, None] = None,
    start_date: datetime.datetime = FIRST_DATE + DAY_DELTA,
    end_date: datetime.datetime = TODAY,
) -> VaccinationsDateRangeByGroup:
    """Gets cumulative number of fully and first does vaccinated persons by day in date range and cumulative number of vaccinated persons by gender and cumulative number of used vaccines by manufacturer on last day in date range either for region, age group or whole country.

    Source: PAGE 1 at https://app.powerbi.com/view?r=eyJrIjoiYWQ3NGE1NTMtZWJkMi00NzZmLWFiNDItZDc5YjU5MGRkOGMyIiwidCI6ImFkMjQ1ZGFlLTQ0YTAtNGQ5NC04OTY3LTVjNjk5MGFmYTQ2MyIsImMiOjl9

    Args:
        property (enum[Region] | enum[AgeGroup] | None): represents how data is filtered, default is None
        start_date (datetime): represent begining of date range
        end_date (datetime): represent begining of date range

    Returns:
        VaccinationsDateRangeByGroup: a VaccinationsDateRangeByGroup representing date range, cumulative vaccinations by day in date range and cumulative vaccinations by gender and by manufacturer on last date in date range.
    """

    if end_date < start_date:
        raise Exception(
            f"Argument [end_date]: {end_date} should be greater or equal than [start_date]: {start_date}"
        )

    if (
        not isinstance(property, Region)
        and not isinstance(property, AgeGroup)
        and property != None
    ):
        raise Exception(
            f"Argument [property] must be instance of Region, AgeGroup or None"
        )

    req = _create_vaccinations_data_range_request(
        end_date=end_date + DAY_DELTA, start_date=start_date, property=property
    )

    group = _get_data(req.group, _parse_vaccinations_date_range)

    result = VaccinationsDateRangeByGroup(start_date, end_date, property, group)

    male1 = _get_data(req.male1, _parse_vaccinations_gender_by_date)
    male2 = _get_data(req.male2, _parse_vaccinations_gender_by_date)
    result.male = VaccinationsDoses(male1, male2)

    female1 = _get_data(req.female1, _parse_vaccinations_gender_by_date)
    female2 = _get_data(req.female2, _parse_vaccinations_gender_by_date)
    result.female = VaccinationsDoses(female1, female2)

    manufacturers = _get_data(
        req.manufacturers, _parse_vaccinations_date_range_manufacturers_used
    )

    for manu in manufacturers:
        result.__setattr__(manu.name, VaccinationsDoses(manu.dose1, manu.dose2))

    return result


def vaccinations_in_range_by_age_group_by_gender(
    start_date=datetime.datetime(2020, 12, 26),
    end_date=datetime.datetime.today().date(),
) -> "dict[AgeGroup]":
    requests = _create_in_range_age_group_gender_requests(start_date, end_date)
    result = {}
    for [age_group, gender_requests] in requests.items():
        group = VaccinationsInDateRangeAgeGroupGender(
            date_start=start_date,
            date_end=end_date,
            age_group=age_group,
            male=VaccinationsDoses(),
            female=VaccinationsDoses(),
        )

        doses = [
            _get_data(_request, _parse_single_data)
            for _request in gender_requests.values()
        ]
        [
            group.male.dose1,
            group.male.dose2,
            group.female.dose1,
            group.female.dose2,
        ] = doses
        result[age_group] = group
    return result


# DASHBOARD LAB


def lab_start_timestamp() -> datetime.datetime:
    """Gets NIJZ first COVID-19 case time

    Returns:
        datetime: datetime representing NIJZ first COVID-19 case
    """
    return _get_data(
        _lab_start_ts_req, _parse_vaccinations_timestamp, _lab_dashboard_headers
    )


def lab_end_timestamp() -> datetime.datetime:
    """Gets NIJZ last data update time

    Returns:
        datetime: datetime representing NIJZ last data update time
    """
    return _get_data(
        _lab_end_ts_req, _parse_vaccinations_timestamp, _lab_dashboard_headers
    )


def lab_end_timestamp_with_cache() -> datetime.datetime:
    """Gets NIJZ last data update time

    Returns:
        datetime: datetime representing NIJZ last data update time
    """
    return _get_data(
        _lab_end_ts_req_with_cache,
        _parse_vaccinations_timestamp,
        _lab_dashboard_headers,
    )


def lab_PCR_tests_performed() -> int:
    """Gets performed PCR tests on today

    today -> date from lab_end_timestamp()

    Returns:
        int: a int number representing performed PCR tests on today
    """
    return _get_data(
        _lab_PCR_tests_performed_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_PCR_tests_performed_with_cache() -> int:
    """Gets performed PCR tests on today

    today -> date from lab_end_timestamp()

    Returns:
        int: a int number representing performed PCR tests on today
    """
    return _get_data(
        _lab_PCR_tests_performed_req_with_cache,
        _parse_single_data,
        _lab_dashboard_headers,
    )


def lab_PCR_total_tests_performed() -> int:
    """Gets performed PCR tests in date range

    start -> date from lab_start_timestamp()
    end -> date from lab_end_timestamp()

    Returns:
        int: a int number representing performed PCR tests in date range
    """
    return _get_data(
        _lab_PCR_total_tests_performed_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_active_cases_estimated() -> int:
    """Gets estimated active cases

    Returns:
        int: a int number representing estimated active cases
    """
    return _get_data(
        _lab_active_cases_estimated_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_confirmed_total_male() -> int:
    """Gets male total confirmed cases in date range

    start -> date from lab_start_timestamp()
    end -> date from lab_end_timestamp()

    Returns:
        int: a int number representing male total confirmed cases in date range
    """
    return _get_data(
        _lab_confirmed_total_male_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_total_vaccinated_first_dose() -> int:
    """Gets vaccinated population with first dose in date range

    start -> date from lab_start_timestamp()
    end -> date from lab_end_timestamp()

    Returns:
        int: a int number representing vaccinated population with first dose in date range
    """
    return _get_data(
        _lab_total_vaccinated_first_dose_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_active_cases_100k() -> float:
    """Gets number of active cases per 100k population

    Returns:
        float: a float number representing active cases per 100k population
    """
    parsed_resp = _get_data(
        _lab_active_cases_100k_req, _parse_single_data, _lab_dashboard_headers
    )
    return float(parsed_resp)


def lab_cases_total_confirmed() -> int:
    """Gets total confirmed cases in date range

    start -> date from lab_start_timestamp()
    end -> date from lab_end_timestamp()

    Returns:
        int: a int number representing total confirmed cases in date range
    """
    return _get_data(
        _lab_cases_total_confirmed_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_HAT_total_tests_performed() -> int:
    """Gets performed HAT tests in date range

    start -> date from lab_start_timestamp()
    end -> date from lab_end_timestamp()

    Returns:
        int: a int number representing performed HAT tests in date range
    """
    return _get_data(
        _lab_HAT_total_tests_performed_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_cases_confirmed() -> int:
    """Gets confirmed cases on today

    today -> date from lab_end_timestamp()

    Returns:
        int: a int number representing confirmed cases on today
    """
    return _get_data(
        _lab_cases_confirmed_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_cases_confirmed_with_cache() -> int:
    """Gets confirmed cases on today

    today -> date from lab_end_timestamp()

    Returns:
        int: a int number representing confirmed cases on today
    """
    return _get_data(
        _lab_cases_confirmed_req_with_cache, _parse_single_data, _lab_dashboard_headers
    )


def lab_confirmed_total_female() -> int:
    """Gets female total confirmed cases in date range

    start -> date from lab_start_timestamp()
    end -> date from lab_end_timestamp()

    Returns:
        int: a int number representing female total confirmed cases in date range
    """
    return _get_data(
        _lab_confirmed_total_female_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_total_vaccinated_fully() -> int:
    """Gets fully vaccinated population in date range

    start -> date from lab_start_timestamp()
    end -> date from lab_end_timestamp()

    Returns:
        int: a int number representing fully vaccinated population in date range
    """
    return _get_data(
        _lab_total_vaccinated_fully_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_cases_avg_7Days() -> float:
    """Gets 7 days average confirmed cases

    Returns:
        float: a float number representing 7 days average confirmed cases
    """
    parsed_resp = _get_data(
        _lab_cases_avg_7Days_req, _parse_single_data, _lab_dashboard_headers
    )
    return float(parsed_resp)


def lab_HAT_tests_performed():
    """Gets performed HAT tests on today

    today -> date from lab_end_timestamp()

    Returns:
        int: a int number representing performed HAT tests on today
    """
    return _get_data(
        _lab_HAT_tests_performed_req, _parse_single_data, _lab_dashboard_headers
    )


def lab_HAT_tests_performed_with_cache():
    """Gets performed HAT tests on today

    today -> date from lab_end_timestamp()

    Returns:
        int: a int number representing performed HAT tests on today
    """
    return _get_data(
        _lab_HAT_tests_performed_req_with_cache,
        _parse_single_data,
        _lab_dashboard_headers,
    )


def get_lab_dashboard() -> LabDashboard:
    """Gets NIJZ dashboard:
        'Prikaz števila opravljenih cepljenj, testiranj in potrjenih okužb s covid-19 v SLoveniji'

    source: https://app.powerbi.com/view?r=eyJrIjoiMDc3MDk4MmQtOGE4NS00YTRkLTgyYjktNWQzMjk5ODNlNjVhIiwidCI6ImFkMjQ1ZGFlLTQ0YTAtNGQ5NC04OTY3LTVjNjk5MGFmYTQ2MyIsImMiOjl9&pageName=ReportSection24198f7e6d06db643832

    Returns:
        LabDashboard: a LabDashboard represent all data from dashboard
    """
    start_date = lab_start_timestamp()
    end_date = lab_end_timestamp()
    pcr = lab_PCR_tests_performed()
    pcr_total = lab_PCR_total_tests_performed()
    hat = lab_HAT_tests_performed()
    hat_total = lab_HAT_total_tests_performed()
    estimated_cases = lab_active_cases_estimated()
    cases_avg_100k = lab_active_cases_100k()
    cases_avg_7days = lab_cases_avg_7Days()
    cases = lab_cases_confirmed()
    cases_total = lab_cases_total_confirmed()
    cases_total_male = lab_confirmed_total_male()
    cases_total_female = lab_confirmed_total_female()
    vaccinated_first_dose = lab_total_vaccinated_first_dose()
    vaccinated_fully = lab_total_vaccinated_fully()

    result = LabDashboard(
        date=end_date,
        pcr=pcr,
        hat=hat,
        confirmed=cases,
        active_estimated=estimated_cases,
        cases_active_100k=cases_avg_100k,
        cases_active_7days=cases_avg_7days,
        date_start=start_date,
        pcr_total=pcr_total,
        hat_total=hat_total,
        confirmed_total=cases_total,
        male_total=cases_total_male,
        female_total=cases_total_female,
        vaccinated_first_dose=vaccinated_first_dose,
        vaccinated_fully=vaccinated_fully,
    )

    return result


def abort_update_labtests():
    end_date = lab_end_timestamp()
    end_date_with_cache = lab_end_timestamp_with_cache()

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    now = datetime.datetime.now()

    should_abort = end_date.date() < yesterday
    should_abort_with_cache = end_date_with_cache.date() < yesterday

    result = {
        "abort": True,
        "now": now,
        "date_no_cache": end_date,
        "date_with_cache": end_date_with_cache,
        "date": yesterday - datetime.timedelta(days=1),
    }

    if should_abort and should_abort_with_cache:
        print("Aborting update labtests")
        print(
            f"Now is {now}. Date no cache: {end_date.date()}. Date with cache: {end_date_with_cache.date()}. Expecting: {yesterday}"
        )
        return result

    result["abort"] = False
    result["date"] = yesterday
    return result


def get_lab_dashboard_with_cache():
    pcr = lab_PCR_tests_performed_with_cache()
    hat = lab_HAT_tests_performed_with_cache()
    cases = lab_cases_confirmed_with_cache()
    end_date = lab_end_timestamp_with_cache()

    result = LabDashboard(date=end_date, pcr=pcr, hat=hat, confirmed=cases)

    return result