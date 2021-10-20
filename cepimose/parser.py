from cepimose.enums import Manufacturer, Region
import datetime

from .types import (
    VaccinationByDayRow,
    VaccinationByAgeRow,
    VaccinationsDateRangeManufacturer,
    VaccineSupplyUsage,
    VaccinationByRegionRow,
    VaccinationByManufacturerRow,
    VaccinationDose,
    VaccinationMunShare,
    VaccinationAgeGroupByRegionOnDayDose,
    VaccinationAgeGroupByRegionOnDay,
)


def parse_date(raw):
    return datetime.datetime.utcfromtimestamp(float(raw) / 1000.0)


def _validate_response_data(data):
    if "DS" not in data["results"][0]["result"]["data"]["dsr"]:
        error = data["results"][0]["result"]["data"]["dsr"]["DataShapes"][0][
            "odata.error"
        ]
        print(error)
        raise Exception("Something went wrong!")


def _parse_vaccinations_timestamp(data):
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    return parse_date(resp[0]["M0"])


def _parse_vaccinations_by_day(data) -> "list[VaccinationByDayRow]":
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    parsed_data: "list[VaccinationByDayRow]" = []

    r_list = [None, 2, 6, 8, 10, 12, 14]

    date = None
    people_vaccinated = None
    people_fully_vaccinated = None
    people_third_dose = None
    for element in resp:

        C = element["C"]
        R = element.get("R", None)
        date = parse_date(C[0])

        if R not in r_list:
            print(date, R, C, sep="\t")
            raise Exception("Unknown R value!")

        if R == None:
            people_vaccinated = C[1]
            people_fully_vaccinated = C[2]
            people_third_dose = C[3]

        if R == 2:
            people_vaccinated = parsed_data[-1].first_dose
            people_fully_vaccinated = C[1]
            people_third_dose = C[2]

        if R == 6:
            people_vaccinated = parsed_data[-1].first_dose
            people_fully_vaccinated = parsed_data[-1].first_dose
            people_third_dose = C[1]

        if R == 8:
            people_vaccinated = C[1]
            people_fully_vaccinated = C[2]
            people_third_dose = parsed_data[-1].third_dose

        if R == 10:
            people_vaccinated = parsed_data[-1].first_dose
            people_fully_vaccinated = C[1]
            people_third_dose = parsed_data[-1].third_dose

        if R == 12:
            people_vaccinated = C[1]
            people_fully_vaccinated = parsed_data[-1].second_dose
            people_third_dose = parsed_data[-1].third_dose

        if R == 14:
            people_vaccinated = parsed_data[-1].first_dose
            people_fully_vaccinated = parsed_data[-1].second_dose
            people_third_dose = parsed_data[-1].third_dose

        parsed_data.append(
            VaccinationByDayRow(
                date=date,
                first_dose=people_vaccinated,
                second_dose=people_fully_vaccinated,
                third_dose=people_third_dose,
            )
        )

    return parsed_data


def _parse_vaccinations_by_age(data) -> "list[VaccinationByAgeRow]":
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    parsed_data = []

    for element in resp:
        C = element["C"]
        age_group = str(C[0])
        share_second = float(C[1]) / 100.0
        share_first = float(C[2]) / 100.0
        count_first = int(C[3])
        count_second = int(C[4])

        parsed_data.append(
            VaccinationByAgeRow(
                age_group=age_group,
                count_first=count_first,
                count_second=count_second,
                share_first=share_first,
                share_second=share_second,
            )
        )

    return parsed_data


def _parse_vaccines_supplied_and_used(data) -> "list[VaccineSupplyUsage]":
    _validate_response_data

    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    parsed_data = []

    for element in resp:
        print(element)
        date = parse_date(element["C"][0])

        if "Ø" in element:
            supplied = int(element["C"][1]) if len(element["C"]) > 1 else 0
            used = 0
        else:
            used = (
                int(element["C"][1]) if len(element["C"]) > 1 else parsed_data[-1].used
            )
            supplied = (
                int(element["C"][2])
                if len(element["C"]) > 2
                else parsed_data[-1].supplied
            )

        row = VaccineSupplyUsage(
            date=date,
            supplied=supplied,
            used=used,
        )
        parsed_data.append(row)

    return parsed_data


def _parse_vaccinations_by_region(data) -> "list[VaccinationByRegionRow]":
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    parsed_data = []

    for element in resp:
        C = element["C"]
        region = str(C[0])
        count_first = int(C[3])
        count_second = int(C[4])
        share_first = float(C[1]) / 100.0
        share_second = float(C[2]) / 100.0

        parsed_data.append(
            VaccinationByRegionRow(
                region=region,
                count_first=count_first,
                count_second=count_second,
                share_first=share_first,
                share_second=share_second,
            )
        )

    return parsed_data


def _parse_vaccines_supplied_by_manufacturer(
    data,
) -> "list[VaccinationByManufacturerRow]":
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][1]["DM1"]
    manufacturers = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["ValueDicts"][
        "D0"
    ]
    parsed_data = []

    if len(manufacturers) > 4:
        print(manufacturers)
        raise Exception("New manufacturer!")

    def get_manufacturer(num):
        manu_keys = ["pfizer", "moderna", "az", "janssen"]
        if num > 3 or num == None:
            print(num)
            raise Exception("Missing manufacturer!")
        return manu_keys[num]

    r_list = [None, 1, 2, 4, 5, 6]

    date = None
    manufacturer = None
    value = None

    for element in resp:
        R = element["R"] if "R" in element else None
        C = element["C"]

        if R not in r_list:
            print(R, C, sep="\t")
            raise Exception("Unknown R value!")

        manu_row = VaccinationByManufacturerRow(
            date=None, pfizer=None, moderna=None, az=None, janssen=None
        )

        if R == None:
            # all data
            date = parse_date(C[0])
            manufacturer = get_manufacturer((C[1]))
            value = int(C[2])
            setattr(manu_row, "date", date)
            setattr(manu_row, manufacturer, value)

        if R == 1:
            # same date as previous
            manufacturer = get_manufacturer((C[0]))
            value = int(C[1])
            setattr(parsed_data[-1], manufacturer, value)

        if R == 2:
            # same manufacturer as previous
            date = parse_date(C[0])
            value = int(C[1])
            setattr(manu_row, "date", date)
            setattr(manu_row, manufacturer, value)

        if R == 4:
            # same value as previous, but different manufacturer
            date = parse_date(C[0])
            manufacturer = get_manufacturer((C[1]))
            setattr(manu_row, "date", date)
            setattr(
                manu_row, manufacturer, value
            )  # reuse value from previous iteration

        if R == 5:
            # same value, same date, but different manufacturer
            manufacturer = get_manufacturer((C[0]))
            setattr(
                parsed_data[-1], manufacturer, value
            )  # reuse value from previous iteration

        if R == 6:
            # same manufacturer and value as previous
            date = parse_date(C[0])
            setattr(manu_row, "date", date)
            setattr(manu_row, manufacturer, value)

        if R != 1 and R != 5:
            parsed_data.append(manu_row)
    return parsed_data


def _parse_vaccines_supplied_by_manufacturer_cum(
    data,
) -> "list[VaccinationByManufacturerRow]":
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    parsed_data = []

    for element in resp:
        elements = list(filter(lambda x: "M0" in x, element["X"]))

        date = parse_date(element["G0"])
        moderna = None
        pfizer = None
        az = None
        janssen = None

        for el in elements:
            if el.get("I", None) == 1:
                janssen = round(float(el["M0"]))
            elif el.get("I", None) == 2:
                moderna = round(float(el["M0"]))
            elif el.get("I", None) == 3:
                pfizer = round(float(el["M0"]))
            else:
                az = round(float(el["M0"]))

        parsed_data.append(
            VaccinationByManufacturerRow(
                date=date, pfizer=pfizer, moderna=moderna, az=az, janssen=janssen
            )
        )

    return parsed_data


def _parse_vaccinations_by_age_group(data) -> "list[VaccinationByDayRow]":
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    parsed_data = []

    date = None
    people_vaccinated = None
    people_fully_vaccinated = None
    for element in resp:
        C = element["C"]
        if len(C) == 3:
            date = parse_date(C[0])
            people_vaccinated = C[1]
            people_fully_vaccinated = C[2]
        elif len(C) == 2:
            date = parse_date(C[0])
            R = element["R"]
            if R == 2:
                people_fully_vaccinated = C[1]
            else:
                people_vaccinated = C[1]
        elif len(C) == 1:
            # R == 6
            date = parse_date(C[0])
        else:
            raise Exception("Unknown item length!")

        parsed_data.append(
            VaccinationByDayRow(
                date=date,
                first_dose=people_vaccinated,
                second_dose=people_fully_vaccinated,
            )
        )

    return parsed_data


def _parse_vaccinations_by_region_by_day(data):
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    parsed_data = []

    people_vaccinated = None
    people_fully_vaccinated = None
    for element in resp:
        C = element["C"]

        if len(C) == 3:
            date = parse_date(C[0])
            people_vaccinated = C[1]
            people_fully_vaccinated = C[2]
        elif len(C) == 2:
            date = parse_date(C[0])
            R = element["R"]
            if R == 2:
                people_fully_vaccinated = C[1]
            else:
                people_vaccinated = C[1]
        elif len(C) == 1:
            date = parse_date(C[0])
        else:
            raise Exception("Unknown item length!")

        parsed_data.append(
            VaccinationByDayRow(
                date=date,
                first_dose=people_vaccinated,
                second_dose=people_fully_vaccinated,
            )
        )

    return parsed_data


def _parse_vaccinations_by_municipalities_share(data) -> "list[VaccinationMunShare]":
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    parsed_data = []

    for el in resp:
        C = el["C"]
        R = el.get("R", None)
        dose1 = None
        dose2 = None
        if len(C) == 4:
            name, share1, share2, population = C
            dose1 = round(population * float(share1))
            dose2 = round(population * float(share2))
        else:
            print(el)
            raise Exception(f"Unknown C length: {len(C)}")

        parsed_data.append(
            VaccinationMunShare(
                name=name,
                dose1=dose1,
                share1=float(share1),
                dose2=dose2,
                share2=float(share2),
                population=population,
            )
        )

    return parsed_data


def _parse_vaccinations_age_group_by_region_on_day(
    data,
) -> "list[VaccinationAgeGroupByRegionOnDay]":
    _validate_response_data(data)

    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]

    def parse_resp_data(region, item):
        if len(item) == 4:
            return VaccinationAgeGroupByRegionOnDayDose(
                region=region,
                total_share=float(item[0]),
                group_share=float(item[1]),
                total_count=item[2],
                group_count=item[3],
            )
        if len(item) == 3:
            return VaccinationAgeGroupByRegionOnDayDose(
                region=region,
                total_share=float(item[0]),
                group_share=float(item[1]),
                total_count=item[2],
            )
        if len(item) == 2:
            return VaccinationAgeGroupByRegionOnDayDose(
                region=region,
                total_share=float(item[0]),
                total_count=item[1],
            )
        raise Exception("Unknown item length!")

    parsed_data = []
    for el in resp:
        C = el["C"]
        region = C[0]
        if len(C) == 9:
            first_dose_data = [C[1], C[2], C[5], C[6]]
            second_dose_data = [C[3], C[4], C[7], C[8]]
            first_dose = parse_resp_data(region, first_dose_data)
            second_dose = parse_resp_data(region, second_dose_data)
            parsed_data.append(
                VaccinationAgeGroupByRegionOnDay(
                    region=region, dose1=first_dose, dose2=second_dose
                )
            )
        else:
            R = el.get("R", None)
            if R == 64:
                # ! not sure
                first_dose_data = [C[1], C[2], C[5], C[6]]
                second_dose_data = [C[3], C[4], C[7]]
                first_dose = parse_resp_data(region, first_dose_data)
                second_dose = parse_resp_data(region, second_dose_data)
                parsed_data.append(
                    VaccinationAgeGroupByRegionOnDay(
                        region=region, dose1=first_dose, dose2=second_dose
                    )
                )

    def is_missing(regions, value):
        try:
            regions.index(value)
            return False
        except ValueError:
            return True

    if len(Region) > len(parsed_data):
        regions = [item.region for item in parsed_data]
        missing_regions = [
            item.value for item in Region if is_missing(regions, item.value)
        ]
        for region in missing_regions:
            dose1 = VaccinationAgeGroupByRegionOnDayDose(region)
            dose2 = VaccinationAgeGroupByRegionOnDayDose(region)
            parsed_data.append(
                VaccinationAgeGroupByRegionOnDay(
                    region=region, dose1=dose1, dose2=dose2
                )
            )

    return parsed_data


def _parse_vaccinations_by_manufacturer_supplied_used(
    data,
) -> "list[VaccineSupplyUsage]":
    _validate_response_data(data)

    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]

    parsed_data = []
    item = None
    for el in resp:
        C = el["C"]
        date = parse_date(C[0])
        if len(C) == 2:
            item = VaccineSupplyUsage(date=date, supplied=round(float(C[1])), used=0)
            parsed_data.append(item)
        elif len(C) == 3:
            item = VaccineSupplyUsage(
                date=date, supplied=round(float(C[2])), used=round(float(C[1]))
            )
            parsed_data.append(item)
        else:
            print(el)
            raise Exception("Unknown [C] length")

    return parsed_data


def _parse_vaccinations_gender_by_date(data):
    _validate_response_data(data)

    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    return resp[0].get("M0", None)


# date range parsers
def _parse_vaccinations_date_range(data):
    _validate_response_data(data)

    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]

    parsed_data = []

    date = None
    people_vaccinated = None
    people_fully_vaccinated = None
    for element in resp:
        C = element["C"]
        if len(C) == 3:
            date = parse_date(C[0])
            people_vaccinated = C[1]
            people_fully_vaccinated = C[2]
        elif len(C) == 2:
            date = parse_date(C[0])
            R = element["R"]
            if R == 2:
                people_fully_vaccinated = C[1]
            else:
                people_vaccinated = C[1]
        elif len(C) == 1:
            # R == 6
            date = parse_date(C[0])
        else:
            raise Exception("Unknown item length!")

        parsed_data.append(
            VaccinationByDayRow(
                date=date,
                first_dose=people_vaccinated,
                second_dose=people_fully_vaccinated,
            )
        )

    return parsed_data


def _create_vaccinations_by_manufacturer_parser(manufacturer: Manufacturer):

    DAY_DELTA = datetime.timedelta(days=1)

    Manufacturer_First_Delivery_Date = {
        Manufacturer.PFIZER: datetime.datetime(2020, 12, 26),
        Manufacturer.MODERNA: datetime.datetime(2021, 1, 12),
        Manufacturer.AZ: datetime.datetime(2021, 2, 6),
        Manufacturer.JANSSEN: datetime.datetime(2021, 4, 14),
    }

    def _parse_vaccinations_by_manufacturer_used(data) -> "list[VaccinationDose]":
        # Here is possible to get data for, first, second, third and total.
        # We need total at the moment.
        _validate_response_data(data)
        resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]

        parsed_data: "list[VaccinationDose]" = []
        for element in resp:
            C = element.get("C")
            R = element.get(
                "R", None
            )  # maybe for later if we decide to parse for each dose
            Ø = element.get(
                "Ø", None
            )  # maybe for later if we decide to parse for each dose

            date = parse_date(C[0])
            total_used = C[-1]

            if R == 30:
                total_used = parsed_data[-1].dose

            # I have no idea what Ø is. I can speculate that is related to doses: first, second or third
            if R == 28 and Ø == None:
                total_used = parsed_data[-1].dose

            if R == 28 and Ø == 2:
                total_used = parsed_data[-1].dose

            parsed_data.append(VaccinationDose(date, total_used))

        return parsed_data

    return _parse_vaccinations_by_manufacturer_used


def _parse_vaccinations_date_range_manufacturers_used(data):
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]

    manu_dict = {
        "Astra Zeneca": "az",
        "Janssen": "janssen",
        "Moderna": "moderna",
        "Pfizer-BioNTech": "pfizer",
    }

    parsed_data = []
    for element in resp:
        C = element.get("C", None)
        manufacturer = C[0]
        result = VaccinationsDateRangeManufacturer(manu_dict[manufacturer])
        if len(C) == 3:
            result.dose1 = C[1]
            result.dose2 = C[2]
        if len(C) == 2:
            kind_of_zero = element.get("Ø", None)  # Do not mixup Ø with 0
            if kind_of_zero == 4:
                result.dose1 = C[1]
            elif kind_of_zero == None:
                result.dose2 = C[1]
            else:
                raise Exception(f'Unknown "Ø" value: {kind_of_zero}')

        parsed_data.append(result)
    return parsed_data


def _parse_single_data(data):
    _validate_response_data(data)
    resp = data["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]
    return resp[0]["M0"]
