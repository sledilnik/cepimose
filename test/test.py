from typing import List
from unittest.case import skip
from cepimose.enums import AgeGroup, Manufacturer, Region
import unittest
import cepimose
import datetime
from nose.plugins.attrib import attr

from cepimose.types import VaccinationByDayRow


class CepimoseTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def assertDatesIncreaseSince(self, data, startDate):
        previousDate = startDate - datetime.timedelta(days=1)
        for row in data:
            self.assertGreater(row.date, previousDate, row)
            previousDate = row.date

    def createAssertVaccinationByDayRow(self, delta, fixed_delta=True):
        def assertVaccinationByDayRow(
            row: VaccinationByDayRow, expected_date, expected_data
        ):
            if expected_date:
                self.assertEqual(row.date, expected_date)

            row_data = [row.first_dose, row.second_dose, row.third_dose]
            self.assertEqual(len(row_data), len(expected_data), "Missing argument!")

            for index, compare in enumerate(row_data):
                _delta = delta if fixed_delta == True else delta * expected_data[index]
                self.assertAlmostEqual(compare, expected_data[index], delta=_delta)

        return assertVaccinationByDayRow

    @attr("sledilnik")
    def test_vaccinations_by_day(self):
        # Test feature one.
        data = cepimose.vaccinations_by_day()
        self.assertGreater(len(data), 150)

        assertRow = self.createAssertVaccinationByDayRow(0.1, False)

        #! NIJZ is changing data tests could fail in the future
        assertRow(data[9], datetime.datetime(2021, 1, 5), [15711, 1, 0])
        assertRow(data[22], datetime.datetime(2021, 1, 18), [49100, 324, 0])
        assertRow(data[41], datetime.datetime(2021, 2, 6), [56066, 46072, 0])
        assertRow(data[42], datetime.datetime(2021, 2, 7), [56066, 46072, 0])
        assertRow(data[274], datetime.datetime(2021, 9, 27), [1157192, 1024689, 18295])

        # values should be growing
        firstPrevious = 0
        secondPrevious = 0
        thirdPrevious = 0
        row: VaccinationByDayRow
        for row in data:
            print(row, firstPrevious, secondPrevious)
            self.assertGreaterEqual(row.first_dose, firstPrevious)
            self.assertGreaterEqual(row.second_dose, secondPrevious)
            self.assertGreaterEqual(row.third_dose, thirdPrevious)
            firstPrevious = row.first_dose
            secondPrevious = row.second_dose
            thirdPrevious = row.third_dose

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 27))

    @skip
    def test_vaccinations_by_age(self):
        # Test feature one.
        data = {row.age_group: row for row in cepimose.vaccinations_by_age()}

        expected_age_groups = [
            "0-17",
            "18-24",
            "25-29",
            "30-34",
            "35-39",
            "40-44",
            "45-49",
            "50-54",
            "55-59",
            "60-64",
            "65-69",
            "70-74",
            "75-79",
            "80-84",
            "85-89",
            "90+",
        ]

        self.assertTrue(len(data), len(expected_age_groups))

        for grp in expected_age_groups:
            self.assertGreater(data[grp].count_first, 0)
            self.assertGreater(data[grp].share_first, 0)
            self.assertGreater(data[grp].count_second, 0)
            self.assertGreater(data[grp].share_second, 0)
            self.assertGreaterEqual(data[grp].count_first, data[grp].count_second)

    @attr("sledilnik")
    def test_vaccines_supplied_by_manufacturer(self):
        data = cepimose.vaccines_supplied_by_manufacturer()
        self.assertTrue(len(data) > 50)

        def assertRow(row, expected_date, expected):
            self.assertEqual(row.date, expected_date)
            self.assertEqual(row.pfizer, expected[0])
            self.assertEqual(row.moderna, expected[1])
            self.assertEqual(row.az, expected[2])
            self.assertEqual(row.janssen, expected[3])
            self.assertEqual(row.novavax, expected[4])

        assertRow(
            data[0], datetime.datetime(2020, 12, 26), [11700, None, None, None, None]
        )  # first ever supply

        assertRow(
            data[1], datetime.datetime(2020, 12, 30), [8190, None, None, None, None]
        )  # R = 2
        assertRow(
            data[3], datetime.datetime(2021, 1, 11), [19890, None, None, None, None]
        )  # R = 6
        assertRow(
            data[16], datetime.datetime(2021, 2, 25), [None, 8400, 16800, None, None]
        )  # combined: two response data items with same date; second has R = 1
        assertRow(
            data[32], datetime.datetime(2021, 4, 14), [None, None, None, 7200, None]
        )
        assertRow(
            data[65], datetime.datetime(2021, 7, 12), [72540, None, -250000, None, None]
        )  # Negative
        assertRow(
            data[73], datetime.datetime(2021, 7, 30), [None, 12000, None, 12000, None]
        )  # R = 5, combined: two response data items with same, date, same value, different manufacturer
        assertRow(
            data[123], datetime.datetime(2022, 3, 1), [None, None, None, None, 36000]
        )  # Novavax

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

    @attr("sledilnik")
    def test_vaccinations_by_region_by_day(self):
        data = cepimose.vaccinations_by_region_by_day()
        expected_keys = [key for key in cepimose.enums.Region]

        self.assertEquals(expected_keys, list(data.keys()), "Object keys")

        region: List[VaccinationByDayRow]
        for key, region in data.items():
            print(key)
            self.assertTrue(len(region) != 0)
            self.assertDatesIncreaseSince(region, datetime.datetime(2020, 12, 27))

            # values should be growing
            previous = [0, 0, 0]
            row: VaccinationByDayRow
            for row in region:
                print(row, previous)
                row_data = [row.first_dose, row.second_dose, row.third_dose]
                for index, dose in enumerate(row_data):
                    self.assertGreaterEqual(dose, previous[index])
                previous = [row.first_dose, row.second_dose, row.third_dose]

    def test_vaccinations_by_region_by_day_with_arg(self):
        data = cepimose.vaccinations_by_region_by_day(cepimose.data.Region.POMURSKA)
        expected_keys = [cepimose.data.Region.POMURSKA]
        self.assertEquals(expected_keys, list(data.keys()), "Object keys")

        region = data[cepimose.data.Region.POMURSKA]

        assertRow = self.createAssertVaccinationByDayRow(0.1, False)

        assertRow(region[9], datetime.datetime(2021, 1, 5), [1180, 1, 0])
        assertRow(region[22], datetime.datetime(2021, 1, 18), [3043, 6, 0])
        assertRow(region[274], datetime.datetime(2021, 9, 27), [63078, 55760, 588])

    @attr("sledilnik")
    def test_vaccinations_by_municipalities_share(self):
        data = cepimose.vaccinations_by_municipalities_share()

        mun_number = 212

        self.assertEqual(len(data), mun_number, "Unexpected number of municipalities")

        for m in data:
            print(m)
            self.assertGreater(m.dose1, 0)
            self.assertGreater(m.dose2, 0)
            self.assertGreaterEqual(m.dose1, m.dose2)
            self.assertGreaterEqual(m.population, m.dose1)
            self.assertGreaterEqual(m.population, m.dose2)

            self.assertGreater(m.share1, 0)
            self.assertGreater(m.share2, 0)
            self.assertGreaterEqual(m.share1, m.share2)
            self.assertGreaterEqual(1, m.share1)
            self.assertGreaterEqual(1, m.share2)

            self.assertAlmostEqual(
                m.dose1, m.population * float(m.share1), delta=0.00001
            )
            self.assertAlmostEqual(
                m.dose2, m.population * float(m.share2), delta=0.00001
            )

    @skip
    def test_vaccination_timestamp(self):
        ts = cepimose.vaccinations_timestamp()
        print("Last update:", ts)
        day_delta = datetime.timedelta(days=3)
        today = datetime.datetime.now()
        diff = today - ts
        self.assertGreaterEqual(day_delta, diff)
        # self.assertGreaterEqual(today, ts) // TODO: adjust timezone for github actions

    @skip
    def test_vaccinations_by_manufacturer_supplied_used(self):
        data = cepimose.vaccinations_by_manufacturer_supplied_used()
        expected_keys = [key for key in cepimose.enums.Manufacturer]

        self.assertEquals(expected_keys, list(data.keys()), "Dict keys")

        Test_data = {
            Manufacturer.JANSSEN: {
                "row": 1,
                "date": datetime.datetime(2021, 4, 30),
                "supplied": 13200,
                "used": 73,
            },
            Manufacturer.MODERNA: {
                "row": 2,
                "date": datetime.datetime(2021, 2, 5),
                "supplied": 8400,
                "used": 996,
            },
            Manufacturer.PFIZER: {
                "row": 2,
                "date": datetime.datetime(2021, 1, 4),
                "supplied": 39780,
                "used": 13563,
            },
            Manufacturer.AZ: {
                "row": 2,
                "date": datetime.datetime(2021, 2, 18),
                "supplied": 36000,
                "used": 4462,
            },
        }

        def assertRow(row, expected_date, expected_first, expected_second):
            self.assertEqual(row.date, expected_date)
            self.assertAlmostEqual(row.supplied, expected_first, delta=350)
            self.assertAlmostEqual(row.used, expected_second, delta=350)

        for key, group_data in data.items():
            print(key, len(group_data))
            self.assertTrue(len(group_data) > 0)
            self.assertDatesIncreaseSince(group_data, datetime.datetime(2020, 12, 26))
            test_item = Test_data[key]
            print(group_data[test_item["row"]])
            assertRow(
                group_data[test_item["row"]],
                test_item["date"],
                test_item["supplied"],
                test_item["used"],
            )
            # ? more assertions

    @attr("sledilnik")
    def test_vaccinations_by_manufacturer_used(self):
        data = cepimose.vaccinations_by_manufacturer_used()

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

        def assertRow(row, expected_date, expected):
            print(row, expected)
            (
                expected_pfizer,
                expected_moderna,
                expected_az,
                expected_janssen,
                expected_novavax,
            ) = expected
            self.assertEqual(row.date, expected_date)
            self.assertAlmostEqual(row.pfizer, expected_pfizer, delta=150)
            self.assertAlmostEqual(row.moderna, expected_moderna, delta=50)
            self.assertAlmostEqual(row.az, expected_az, delta=50)
            self.assertAlmostEqual(row.janssen, expected_janssen, delta=50)
            self.assertAlmostEqual(row.novavax, expected_novavax, delta=50)

        assertRow(
            data[20], datetime.datetime(2021, 1, 16), [323, None, None, None, None]
        )
        assertRow(
            data[23], datetime.datetime(2021, 1, 19), [2119, 66, None, None, None]
        )
        assertRow(data[33], datetime.datetime(2021, 1, 29), [4601, 1, None, None, None])
        assertRow(
            data[38], datetime.datetime(2021, 2, 3), [4854, None, None, None, None]
        )
        assertRow(
            data[42], datetime.datetime(2021, 2, 7), [None, None, None, None, None]
        )
        assertRow(data[50], datetime.datetime(2021, 2, 15), [28, 40, 18, None, None])
        assertRow(
            data[79], datetime.datetime(2021, 3, 16), [609, 452, None, None, None]
        )
        assertRow(
            data[98], datetime.datetime(2021, 4, 4), [None, 1594, None, None, None]
        )
        assertRow(data[99], datetime.datetime(2021, 4, 5), [1, None, None, None, None])
        assertRow(data[120], datetime.datetime(2021, 4, 26), [1, None, 381, None, None])
        assertRow(data[134], datetime.datetime(2021, 5, 10), [46, 141, 2080, 717, None])
        assertRow(
            data[290], datetime.datetime(2021, 10, 13), [5192, 438, 4, None, None]
        )
        assertRow(data[431], datetime.datetime(2022, 3, 3), [743, 15, None, None, 1])

        for row in data:
            print(row)
            self.assertTrue(
                row.date >= datetime.datetime(2021, 1, 8, 0, 0) or row.moderna == None,
                f"Too early for Moderna usage: {row}",
            )
            self.assertTrue(
                row.date >= datetime.datetime(2021, 1, 28, 0, 0) or row.az == None,
                f"Too early for Astra Zeneca usage: {row}",
            )
            self.assertTrue(
                row.date >= datetime.datetime(2021, 4, 14, 0, 0) or row.janssen == None,
                f"Too early for Janssen usage: {row}",
            )

            self.assertTrue(
                row.date >= datetime.datetime(2022, 3, 1, 0, 0) or row.novavax == None,
                f"Too early for Novavax usage: {row}",
            )

            # check for absurdly high numbers (eg leaked timestamps)
            if row.pfizer is not None:
                self.assertLess(row.pfizer, 100000, row)
            if row.moderna is not None:
                self.assertLess(row.moderna, 100000, row)
            if row.az is not None:
                self.assertLess(row.az, 100000, row)
            if row.janssen is not None:
                self.assertLess(row.janssen, 100000, row)

    @skip
    def test_vaccine_supply_and_usage(self):
        data = cepimose.vaccines_supplied_and_used()
        self.assertGreater(len(data), 100)

        def assertRow(row, expected_date, expected_supp, expected_used):
            self.assertEqual(row.date, expected_date)
            self.assertAlmostEqual(row.supplied, expected_supp, delta=400)
            self.assertAlmostEqual(row.used, expected_used, delta=400)

        #! NIJZ is changing data tests could fail in the future
        assertRow(data[9], datetime.datetime(2021, 1, 4), 39780, 13248)
        assertRow(data[22], datetime.datetime(2021, 1, 17), 60870, 49189)

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

    @skip
    def test_vaccinations_by_region(self):
        # Test feature one.
        data = {row.region: row for row in cepimose.vaccinations_by_region()}

        expected_regions = [
            "Koroška",
            "Zasavska",
            "Goriška",
            "Posavska",
            "Gorenjska",
            "Podravska",
            "Pomurska",
            "Osrednjeslovenska",
            "Jugovzhodna Slovenija",
            "Primorsko-notranjska",
            "Savinjska",
            "Obalno-kraška",
        ]

        print(data.keys())

        self.assertTrue(len(data), len(expected_regions))

        for grp in expected_regions:
            self.assertGreater(data[grp].count_first, 0)
            self.assertGreater(data[grp].share_first, 0)
            self.assertGreater(data[grp].count_second, 0)
            self.assertGreater(data[grp].share_second, 0)

    @skip
    def test_supplied_by_manufacturer_cumulative(self):
        data = cepimose.vaccines_supplied_by_manufacturer_cumulative()
        self.assertTrue(len(data) > 10)

        def assertRow(row, expected_date, expected):
            self.assertEqual(row.date, expected_date)
            self.assertEqual(row.pfizer, expected[0])
            self.assertEqual(row.moderna, expected[1])
            self.assertEqual(row.az, expected[2])
            self.assertEqual(row.janssen, expected[3])

        assertRow(data[3], datetime.datetime(2021, 1, 11), [59670, None, None, None])
        assertRow(data[7], datetime.datetime(2021, 1, 31), [None, 3600, None, None])
        assertRow(data[10], datetime.datetime(2021, 2, 6), [None, None, 9600, None])
        assertRow(data[16], datetime.datetime(2021, 2, 25), [None, 16800, 52800, None])
        assertRow(data[32], datetime.datetime(2021, 4, 14), [None, None, None, 7200])

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

    @attr("sledilnik")
    def test_vaccinations_by_age_group(self):
        data = cepimose.vaccinations_by_age_group()
        expected_keys = [key for key in cepimose.enums.AgeGroup]

        self.assertEquals(expected_keys, list(data.keys()), "Dict keys")

        group: List[VaccinationByDayRow]
        for group in data.values():
            self.assertTrue(len(group) != 0)
            self.assertDatesIncreaseSince(group, datetime.datetime(2020, 12, 27))

            row: VaccinationByDayRow
            for row in group:
                self.assertGreaterEqual(row.first_dose, 0)
                self.assertGreaterEqual(row.second_dose, 0)
                self.assertGreaterEqual(row.third_dose, 0)

    def test_vaccinations_by_age_group_with_arg(self):
        data: List[VaccinationByDayRow] = cepimose.vaccinations_by_age_group(
            cepimose.enums.AgeGroup.GROUP_90
        )

        self.assertTrue(len(data) > 10)

        assertRow = self.createAssertVaccinationByDayRow(500, True)

        assertRow(data[21], datetime.datetime(2021, 1, 17), [5088, 1, 0])
        assertRow(data[70], datetime.datetime(2021, 3, 7), [11835, 6742, 0])
        assertRow(data[274], datetime.datetime(2021, 9, 27), [17589, 16227, 1356])

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

    @skip
    def test_vaccinations_age_group_by_region_on_day(self):
        data = cepimose.vaccinations_age_group_by_region_on_day()
        expected_keys = [key for key in cepimose.enums.AgeGroup]

        self.assertEquals(expected_keys, list(data.keys()), "Dict keys")

        for key, group_data in data.items():
            print(key, len(group_data))
            self.assertTrue(len(group_data) == len(list(cepimose.Region)))

            for group_day in group_data:
                print(group_day)
                self.assertEqual(group_day.region, group_day.dose1.region)
                self.assertEqual(group_day.region, group_day.dose2.region)
                self.assertEqual(group_day.dose1.region, group_day.dose2.region)
                self.assertGreaterEqual(group_day.dose1.total_count, 0)
                self.assertGreaterEqual(group_day.dose1.group_count, 0)
                self.assertGreaterEqual(group_day.dose1.total_share, 0)
                self.assertGreaterEqual(group_day.dose1.group_share, 0)
                self.assertGreaterEqual(group_day.dose2.total_count, 0)
                self.assertGreaterEqual(group_day.dose2.group_count, 0)
                self.assertGreaterEqual(group_day.dose2.total_share, 0)
                self.assertGreaterEqual(group_day.dose2.group_share, 0)

    @skip
    def test_vaccinations_age_group_by_region_on_day_with_arg(self):
        chosen_group = cepimose.AgeGroup.GROUP_0_17
        data = cepimose.vaccinations_age_group_by_region_on_day(chosen_group)

        self.assertTrue(len(data) == len(list(cepimose.Region)))

        region_names = [name.value for name in list(cepimose.Region)]

        for item in data:
            print(item)
            self.assertTrue(item.region in region_names)

            self.assertTrue(item.region, item.dose1.region)
            self.assertGreaterEqual(item.dose1.total_count, 0)
            self.assertGreaterEqual(item.dose1.group_count, 0)
            self.assertGreaterEqual(item.dose1.total_count, item.dose1.group_count)
            self.assertGreaterEqual(item.dose1.total_share, 0)
            self.assertGreaterEqual(item.dose1.group_share, 0)
            self.assertGreaterEqual(item.dose1.total_share, item.dose1.group_share)

            self.assertTrue(item.region, item.dose2.region)
            self.assertGreaterEqual(item.dose2.total_count, 0)
            self.assertGreaterEqual(item.dose2.group_count, 0)
            self.assertGreaterEqual(item.dose2.total_count, item.dose2.group_count)
            self.assertGreaterEqual(item.dose2.total_share, 0)
            self.assertGreaterEqual(item.dose2.group_share, 0)
            self.assertGreaterEqual(item.dose2.total_share, item.dose2.group_share)

    @skip
    def test_vaccinations_date_range(self):
        start_date = datetime.datetime(2021, 5, 6)
        # assert args end_date and start_date are equal
        data = cepimose.vaccinations_date_range(
            end_date=start_date, start_date=start_date
        )
        print(data)
        self.assertEqual(start_date, data.date_from)
        self.assertEqual(data.date_from, data.date_to)
        self.assertEqual(data.property, None)
        self.assertEqual(len(data.by_day), 1)
        self.assertAlmostEqual(data.male.dose1, 7906, delta=50)
        self.assertAlmostEqual(data.male.dose2, 5857, delta=50)
        self.assertAlmostEqual(data.female.dose1, 7684, delta=50)
        self.assertAlmostEqual(data.female.dose2, 6375, delta=50)
        self.assertEqual(data.by_day[0].first_dose, data.male.dose1 + data.female.dose1)
        self.assertEqual(
            data.by_day[0].second_dose, data.male.dose2 + data.female.dose2
        )
        self.assertAlmostEqual(data.pfizer.dose1, 13945, delta=50)
        self.assertAlmostEqual(data.pfizer.dose2, 11436, delta=50)
        self.assertAlmostEqual(data.az.dose1, 1332, delta=50)
        self.assertAlmostEqual(data.az.dose2, 473, delta=50)
        self.assertAlmostEqual(data.moderna.dose1, 253, delta=50)
        self.assertAlmostEqual(data.moderna.dose2, 164, delta=50)
        self.assertAlmostEqual(data.janssen.dose1, 60, delta=50)
        self.assertAlmostEqual(data.janssen.dose2, 0, delta=50)

        # assert arg start_date is greater than end_date
        end_date = datetime.datetime(2021, 2, 28)
        with self.assertRaises(Exception):
            cepimose.vaccinations_date_range(end_date=end_date, start_date=start_date)

        start_date = datetime.datetime(2020, 12, 26)
        today = datetime.datetime.today()
        end_date = datetime.datetime(today.year, today.month, today.day)
        data = cepimose.vaccinations_date_range(
            end_date=end_date, start_date=start_date
        )
        self.assertDatesIncreaseSince(data.by_day, datetime.datetime(2020, 12, 26))

        self.assertEqual(start_date, data.date_from)
        self.assertEqual(end_date, data.date_to)

    @skip
    def test_vaccinations_date_range_region(self):
        property = Region.POMURSKA

        start_date = datetime.datetime(2021, 4, 20)
        # assert args end_date and start_date are equal
        data = cepimose.vaccinations_date_range(
            end_date=start_date, start_date=start_date, property=property
        )
        print(data)
        self.assertEqual(start_date, data.date_from)
        self.assertEqual(data.date_from, data.date_to)
        self.assertEqual(data.property, property)
        self.assertEqual(len(data.by_day), 1)
        self.assertAlmostEqual(data.male.dose1, 18, delta=5)
        self.assertAlmostEqual(data.male.dose2, 147, delta=10)
        self.assertAlmostEqual(data.female.dose1, 10, delta=5)
        self.assertAlmostEqual(data.female.dose2, 165, delta=10)
        self.assertEqual(data.by_day[0].first_dose, data.male.dose1 + data.female.dose1)
        self.assertEqual(
            data.by_day[0].second_dose, data.male.dose2 + data.female.dose2
        )
        self.assertAlmostEqual(data.pfizer.dose1, 8, delta=10)
        self.assertAlmostEqual(data.pfizer.dose2, 312, delta=10)
        self.assertAlmostEqual(data.az.dose1, 20, delta=10)
        self.assertAlmostEqual(data.az.dose2, 0, delta=10)
        self.assertAlmostEqual(data.moderna.dose1, 0, delta=10)
        self.assertAlmostEqual(data.moderna.dose2, 0, delta=10)
        self.assertAlmostEqual(data.janssen.dose1, 0, delta=10)
        self.assertAlmostEqual(data.janssen.dose2, 0, delta=10)

        # assert arg start_date is greater than end_date
        end_date = datetime.datetime(2021, 2, 28)
        with self.assertRaises(Exception):
            cepimose.vaccinations_date_range(
                end_date=end_date, start_date=start_date, property=property
            )

        start_date = datetime.datetime(2020, 12, 26)
        today = datetime.datetime.today()
        end_date = datetime.datetime(today.year, today.month, today.day)
        data = cepimose.vaccinations_date_range(
            end_date=end_date, start_date=start_date, property=property
        )
        self.assertDatesIncreaseSince(data.by_day, datetime.datetime(2020, 12, 26))

        self.assertEqual(start_date, data.date_from)
        self.assertEqual(end_date, data.date_to)

    @skip
    def test_vaccinations_date_range_age_group(self):
        property = AgeGroup.GROUP_70_74

        start_date = datetime.datetime(2021, 4, 20)
        # assert args end_date and start_date are equal
        data = cepimose.vaccinations_date_range(
            end_date=start_date, start_date=start_date, property=property
        )
        self.assertEqual(len(data.by_day), 1)

        print(data)
        self.assertEqual(start_date, data.date_from)
        self.assertEqual(data.date_from, data.date_to)
        self.assertEqual(data.property, property)
        self.assertEqual(len(data.by_day), 1)
        self.assertAlmostEqual(data.male.dose1, 46, delta=5)
        self.assertAlmostEqual(data.male.dose2, 533, delta=10)
        self.assertAlmostEqual(data.female.dose1, 42, delta=5)
        self.assertAlmostEqual(data.female.dose2, 579, delta=10)
        self.assertEqual(data.by_day[0].first_dose, data.male.dose1 + data.female.dose1)
        self.assertEqual(
            data.by_day[0].second_dose, data.male.dose2 + data.female.dose2
        )
        self.assertAlmostEqual(data.pfizer.dose1, 41, delta=10)
        self.assertAlmostEqual(data.pfizer.dose2, 1111, delta=10)
        self.assertAlmostEqual(data.az.dose1, 5, delta=10)
        self.assertAlmostEqual(data.az.dose2, 1, delta=10)
        self.assertAlmostEqual(data.moderna.dose1, 42, delta=10)
        self.assertAlmostEqual(data.moderna.dose2, 0, delta=10)
        self.assertAlmostEqual(data.janssen.dose1, 0, delta=10)
        self.assertAlmostEqual(data.janssen.dose2, 0, delta=10)

        # assert arg start_date is greater than arg end_date
        end_date = datetime.datetime(2021, 2, 28)
        with self.assertRaises(Exception):
            cepimose.vaccinations_date_range(
                end_date=end_date, start_date=start_date, property=property
            )

        start_date = datetime.datetime(2020, 12, 26)
        today = datetime.datetime.today()
        end_date = datetime.datetime(today.year, today.month, today.day)
        data = cepimose.vaccinations_date_range(
            end_date=end_date, start_date=start_date, property=property
        )
        self.assertDatesIncreaseSince(data.by_day, datetime.datetime(2020, 12, 26))

        self.assertEqual(start_date, data.date_from)
        self.assertEqual(end_date, data.date_to)

    @skip
    def test_vaccinations_gender_by_date(self):
        # it takes to long to fetch data for whole period from 2020-12-27 until today

        test_date1 = datetime.datetime(2021, 1, 10)
        test_date2 = datetime.datetime(2021, 2, 10)
        test_date3 = datetime.datetime(2021, 3, 10)
        test_date4 = datetime.datetime(2021, 4, 10)
        test_date5 = datetime.datetime(2021, 5, 10)

        test_date6 = datetime.datetime(2021, 2, 7)
        test_date7 = datetime.datetime(2021, 4, 4)
        test_date8 = datetime.datetime(2021, 4, 5)

        data1 = cepimose.vaccinations_gender_by_date(test_date1)
        data2 = cepimose.vaccinations_gender_by_date(test_date2)
        data3 = cepimose.vaccinations_gender_by_date(test_date3)
        data4 = cepimose.vaccinations_gender_by_date(test_date4)
        data5 = cepimose.vaccinations_gender_by_date(test_date5)

        data6 = cepimose.vaccinations_gender_by_date(test_date6)
        data7 = cepimose.vaccinations_gender_by_date(test_date7)
        data8 = cepimose.vaccinations_gender_by_date(test_date8)

        def assertRow(row, expected_date, expected_data):
            print(row, expected_date, expected_data)
            self.assertEqual(row.date, expected_date)
            self.assertAlmostEqual(row.female_first, expected_data[0], delta=300)
            self.assertAlmostEqual(row.female_second, expected_data[1], delta=300)
            self.assertAlmostEqual(row.male_first, expected_data[2], delta=300)
            self.assertAlmostEqual(row.male_second, expected_data[3], delta=300)

        assertRow(data1, test_date1, [None, None, 1, 0])
        assertRow(data2, test_date2, [1536, 495, 916, 215])
        assertRow(data3, test_date3, [2851, 2722, 1870, 1597])
        assertRow(data4, test_date4, [4652, 76, 4400, 53])
        assertRow(data5, test_date5, [1009, 690, 1321, 681])

        assertRow(data6, test_date6, [None, None, None, None])
        assertRow(data7, test_date7, [835, 1, 749, 1])
        assertRow(data8, test_date8, [None, None, 1, 0])

    @skip
    def test_vaccinations_gender_by_date_for_today(self):
        # not sure if this test is useful
        test_date_today = datetime.datetime.today()
        test_today_year = test_date_today.year
        test_today_month = test_date_today.month
        test_today_day = test_date_today.day
        test_today_without_time = datetime.datetime(
            test_today_year, test_today_month, test_today_day
        )
        data_today = cepimose.vaccinations_gender_by_date(test_today_without_time)
        print(f"Today: {test_date_today}")
        self.assertIsNot(data_today, None)

    def test_vaccinations_in_range_by_age_group_by_gender(self):

        start_date = datetime.datetime(2020, 12, 27)
        end_date = datetime.datetime(2021, 9, 14)

        data = cepimose.vaccinations_in_range_by_age_group_by_gender(
            start_date, end_date
        )

        group90 = data[AgeGroup.GROUP_90]
        self.assertEqual(group90.age_group, AgeGroup.GROUP_90)
        self.assertAlmostEqual(group90.female.dose1, 9062, delta=200)
        self.assertAlmostEqual(group90.female.dose2, 7438, delta=200)
        self.assertAlmostEqual(group90.male.dose1, 2969, delta=200)
        self.assertAlmostEqual(group90.male.dose2, 2382, delta=200)
