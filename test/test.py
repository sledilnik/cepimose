from cepimose.enums import AgeGroup, Manufacturer, Region
import unittest
import cepimose
import datetime
from nose.plugins.attrib import attr


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

    @attr('sledilnik')
    def test_vaccinations_by_day(self):
        # Test feature one.
        data = cepimose.vaccinations_by_day()
        self.assertGreater(len(data), 100)

        def assertRow(row, expected_date, expected_first, expected_second):
            self.assertEqual(row.date, expected_date)
            self.assertAlmostEqual(row.first_dose, expected_first, delta=400)
            self.assertAlmostEqual(row.second_dose, expected_second, delta=400)

        #! NIJZ is changing data tests could fail in the future
        assertRow(data[9], datetime.datetime(2021, 1, 5), 15711, 0)
        assertRow(data[22], datetime.datetime(2021, 1, 18), 49100, 315)
        assertRow(data[41], datetime.datetime(2021, 2, 6), 56066, 44924)
        assertRow(data[42], datetime.datetime(2021, 2, 7), 56066, 44924)

        # values should be growing
        firstPrevious = 0
        secondPrevious = 0
        for row in data:
            print(row, firstPrevious, secondPrevious)
            self.assertGreaterEqual(row.first_dose, firstPrevious)
            self.assertGreaterEqual(row.second_dose, secondPrevious)
            firstPrevious = row.first_dose
            secondPrevious = row.second_dose

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 27))

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

    @attr('sledilnik')
    def test_supplied_by_manufacturer(self):
        data = cepimose.vaccines_supplied_by_manufacturer()
        self.assertTrue(len(data) > 10)

        def assertRow(row, expected_date, expected):
            self.assertEqual(row.date, expected_date)
            self.assertEqual(row.pfizer, expected[0])
            self.assertEqual(row.moderna, expected[1])
            self.assertEqual(row.az, expected[2])
            self.assertEqual(row.janssen, expected[3])

        assertRow(
            data[1], datetime.datetime(2020, 12, 30), [8190, None, None, None]
        )  # R = 2
        assertRow(
            data[3], datetime.datetime(2021, 1, 11), [19890, None, None, None]
        )  # R = 6
        assertRow(
            data[16], datetime.datetime(2021, 2, 25), [None, 8400, 16800, None]
        )  # combined: two response data items with same date; second has R = 1
        assertRow(data[32], datetime.datetime(2021, 4, 14), [None, None, None, 7200])

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

    @attr('sledilnik')
    def test_vaccinations_by_region_by_day(self):
        data = cepimose.vaccinations_by_region_by_day()
        expected_keys = [key for key in cepimose.enums.Region]

        self.assertEquals(expected_keys, list(data.keys()), "Object keys")

        for element in data.items():
            print(element[0])
            self.assertTrue(len(element[1]) != 0)
            self.assertDatesIncreaseSince(element[1], datetime.datetime(2020, 12, 27))

            # values should be growing
            firstPrevious = 0
            secondPrevious = 0
            for row in data[element[0]]:
                print(row, firstPrevious, secondPrevious)
                self.assertGreaterEqual(row.first_dose, firstPrevious)
                self.assertGreaterEqual(row.second_dose, secondPrevious)
                firstPrevious = row.first_dose
                secondPrevious = row.second_dose

        pomurska_region = data[cepimose.data.Region.POMURSKA]

        def assertRow(row, expected_date, expected_first, expected_second):
            self.assertEqual(row.date, expected_date)
            self.assertAlmostEqual(row.first_dose, expected_first, delta=30)
            self.assertAlmostEqual(row.second_dose, expected_second, delta=30)

        assertRow(pomurska_region[9], datetime.datetime(2021, 1, 5), 988, 0)
        assertRow(pomurska_region[22], datetime.datetime(2021, 1, 18), 2847, 5)

    def test_vaccinations_by_region_by_day_with_arg(self):
        data = cepimose.vaccinations_by_region_by_day(cepimose.data.Region.POMURSKA)
        expected_keys = [cepimose.data.Region.POMURSKA]
        self.assertEquals(expected_keys, list(data.keys()), "Object keys")

        pomurska_region = data[cepimose.data.Region.POMURSKA]

        def assertRow(row, expected_date, expected_first, expected_second):
            self.assertEqual(row.date, expected_date)
            self.assertAlmostEqual(row.first_dose, expected_first, delta=30)
            self.assertAlmostEqual(row.second_dose, expected_second, delta=30)

        assertRow(pomurska_region[9], datetime.datetime(2021, 1, 5), 988, 0)
        assertRow(pomurska_region[22], datetime.datetime(2021, 1, 18), 2847, 5)

    @attr('sledilnik')
    def test_vaccinations_by_municipalities_share(self):
        data = cepimose.vaccinations_by_municipalities_share()

        mun_number = 212

        self.assertTrue(len(data), mun_number)

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

    def test_vaccination_timestamp(self):
        ts = cepimose.vaccinations_timestamp()
        print("Last update:", ts)
        day_delta = datetime.timedelta(days=3)
        today = datetime.datetime.now()
        diff = today - ts
        self.assertGreaterEqual(day_delta, diff)
        # self.assertGreaterEqual(today, ts) // TODO: adjust timezone for github actions

    def test_vaccinations_gender_by_date(self):
        test_date1 = datetime.datetime(2021, 1, 10)
        test_date2 = datetime.datetime(2021, 2, 10)
        test_date3 = datetime.datetime(2021, 3, 10)
        test_date4 = datetime.datetime(2021, 4, 10)
        test_date5 = datetime.datetime(2021, 5, 10)

        data1 = cepimose.vaccinations_gender_by_date(test_date1)
        data2 = cepimose.vaccinations_gender_by_date(test_date2)
        data3 = cepimose.vaccinations_gender_by_date(test_date3)
        data4 = cepimose.vaccinations_gender_by_date(test_date4)
        data5 = cepimose.vaccinations_gender_by_date(test_date5)

        def assertRow(row, expected_date, expected_data):
            print(row)
            self.assertEqual(row.date, expected_date)
            self.assertAlmostEqual(row.female_first, expected_data[0], delta=300)
            self.assertAlmostEqual(row.female_second, expected_data[1], delta=300)
            self.assertAlmostEqual(row.male_first, expected_data[2], delta=300)
            self.assertAlmostEqual(row.male_second, expected_data[3], delta=300)

        assertRow(data1, test_date1, [None, None, 1, 0])
        assertRow(data2, test_date2, [1536, 495, 916, 215])
        assertRow(data3, test_date3, [2851, 3024, 1870, 1902])
        assertRow(data4, test_date4, [4652, 76, 4400, 53])
        assertRow(data5, test_date5, [1009, 690, 1321, 681])

    def test_vaccinations_gender_by_date_for_today(self):
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

    def test_vaccinations_by_upplied_used(self):
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
                "used": 13259,
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
            self.assertAlmostEqual(row.supplied, expected_first, delta=300)
            self.assertAlmostEqual(row.used, expected_second, delta=300)

        for key, group_data in data.items():
            print(key, len(group_data))
            self.assertTrue(len(group_data) > 0)
            self.assertDatesIncreaseSince(group_data, datetime.datetime(2020, 12, 26))
            test_item = Test_data[key]
            assertRow(
                group_data[test_item["row"]],
                test_item["date"],
                test_item["supplied"],
                test_item["used"],
            )
            # ? more assertions

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

        # assertRow(
        #     data[len(data) - 1], datetime.datetime(2021, 4, 2), [285480, 46800, 144000]
        # )  # this test will fail in the future

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

    @attr('sledilnik')
    def test_vaccinations_by_age_group(self):
        data = cepimose.vaccinations_by_age_group()
        expected_keys = [key for key in cepimose.enums.AgeGroup]

        self.assertEquals(expected_keys, list(data.keys()), "Dict keys")

        for key, group_data in data.items():
            print(key, len(group_data))
            self.assertTrue(len(group_data) != 0)
            self.assertDatesIncreaseSince(group_data, datetime.datetime(2020, 12, 27))
            # ? more assertions

    def test_vaccinations_by_age_group_with_arg(self):
        data = cepimose.vaccinations_by_age_group(cepimose.enums.AgeGroup.GROUP_90)

        self.assertTrue(len(data) > 10)

        def assertRow(row, expected_date, expected_dose):
            self.assertEqual(row.date, expected_date)
            self.assertAlmostEqual(row.first_dose, expected_dose[0], delta=30)
            self.assertAlmostEqual(row.second_dose, expected_dose[1], delta=30)

        assertRow(data[21], datetime.datetime(2021, 1, 17), [3580, 1])
        assertRow(data[70], datetime.datetime(2021, 3, 7), [7866, 4821])

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

    def test_vaccinations_age_group_by_region_on_day(self):
        data = cepimose.vaccinations_age_group_by_region_on_day()
        expected_keys = [key for key in cepimose.enums.AgeGroup]

        self.assertEquals(expected_keys, list(data.keys()), "Dict keys")

        for key, group_data in data.items():
            print(key, len(group_data))
            self.assertTrue(len(group_data) == len(list(cepimose.Region)))
            # ? more assertions

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

    # vaccinations_date_range
    def test_vaccinations_date_range_region(self):
        property = Region.POMURSKA

        start_date = datetime.datetime(2021, 3, 1)
        # assert args end_date and start_date are equal
        data = cepimose.vaccinations_date_range(
            end_date=start_date, start_date=start_date, property=property
        )
        self.assertEqual(len(data), 1)

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
        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

    def test_vaccinations_date_range_age_group(self):
        property = AgeGroup.GROUP_90

        start_date = datetime.datetime(2021, 3, 1)
        # assert args end_date and start_date are equal
        data = cepimose.vaccinations_date_range(
            end_date=start_date, start_date=start_date, property=property
        )
        self.assertEqual(len(data), 1)

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
        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

    @attr('sledilnik')
    def test_vaccinations_by_manufacturer_used(self):
        data = cepimose.vaccinations_by_manufacturer_used()

        self.assertDatesIncreaseSince(data, datetime.datetime(2020, 12, 26))

        def assertRow(row, expected_date, expected):
            self.assertEqual(row.date, expected_date)
            self.assertAlmostEqual(row.pfizer, expected[0], delta=50)
            self.assertAlmostEqual(row.moderna, expected[1], delta=50)
            self.assertAlmostEqual(row.az, expected[2], delta=50)
            self.assertAlmostEqual(row.janssen, expected[3], delta=50)

        assertRow(data[20], datetime.datetime(2021, 1, 16), [324, None, None, None])
        assertRow(data[23], datetime.datetime(2021, 1, 19), [2103, 66, None, None])
        assertRow(data[38], datetime.datetime(2021, 2, 3), [4805, None, 1, None])
        assertRow(data[42], datetime.datetime(2021, 2, 7), [None, None, None, None])
        assertRow(data[50], datetime.datetime(2021, 2, 15), [28, 40, 18, None])
        assertRow(data[79], datetime.datetime(2021, 3, 16), [606, 445, None, None])
        assertRow(data[98], datetime.datetime(2021, 4, 4), [None, 1594, None, None])
        assertRow(data[99], datetime.datetime(2021, 4, 5), [1, None, None, None])
        assertRow(data[120], datetime.datetime(2021, 4, 26), [None, None, 385, None])
        assertRow(data[134], datetime.datetime(2021, 5, 10), [46, 141, 2080, 717])

        for row in data:
            print(row)
            self.assertTrue(
                row.date >= datetime.datetime(2021, 1, 8, 0, 0) or row.moderna == None,
                f"Too early for Moderna usage: {row}",
            )
            self.assertTrue(
                row.date >= datetime.datetime(2021, 2, 2, 0, 0) or row.az == None,
                f"Too early for Astra Zeneca usage: {row}",
            )
            self.assertTrue(
                row.date >= datetime.datetime(2021, 4, 14, 0, 0) or row.janssen == None,
                f"Too early for Janssen usage: {row}",
            )
