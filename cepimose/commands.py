import datetime
from typing import Union

from cepimose.enums import AgeGroup, Gender, Region, Manufacturer
from cepimose.types import CommandQueryFrom, DateRangeCommands_Requests


_ExecutionMetrics = {"ExecutionMetricsKind": 1}


def _get_Binding(projections: list, data_volume: int, primary: dict, version: int):
    return {
        "Primary": {"Groupings": [{"Projections": projections}]},
        "DataReduction": {"DataVolume": data_volume, "Primary": primary},
        "Version": version,
    }


def _get_Version(version: int = 2) -> "int":
    return version


def _get_Where(
    functions: list, arguments: list, special_args: list, skip_function: list
) -> "list":
    result = []
    for index, func in enumerate(functions):
        if not index in skip_function:
            result.append(func(*arguments[index], *special_args[index]))
    return result


# DATE RANGE GROUP QUERY FROM
def _get_From(*args: CommandQueryFrom) -> "list[dict]":
    result = []
    for arg in args:
        result.append({"Name": arg.name, "Entity": arg.entity, "Type": arg.type})
    return result


# DATE RANGE GROUP QUERY WHERE
def _get_Column(
    source: str,
    Property="Date",
):
    return {"Expression": {"SourceRef": {"Source": source}}, "Property": Property}


def _get_DateSpan(value=datetime.datetime(2020, 12, 26), time_unit=5):
    return {
        "Expression": {"Literal": {"Value": f"datetime'{value.isoformat()}'"}},
        "TimeUnit": time_unit,
    }


def _get_Comparison_With_DateSpan(comparison_kind, source, Property, value, time_unit):
    return {
        "ComparisonKind": comparison_kind,
        "Left": {"Column": _get_Column(source, Property)},
        "Right": {"DateSpan": _get_DateSpan(value, time_unit)},
    }


def _get_Comparison_With_Literal(
    comparison_kind: int,
    source,
    Property="Date",
    value=datetime.datetime(2020, 12, 26),
):
    Value = (
        f"datetime'{value.isoformat()}'"
        if isinstance(value, datetime.datetime)
        else value
    )

    return {
        "ComparisonKind": comparison_kind,
        "Left": {"Column": _get_Column(source, Property)},
        "Right": {"Literal": {"Value": Value}},
    }


def _get_Condition_Comparison_With_DateSpan(
    source: str,
    comparison_kind=1,
    Property="Date",
    value=datetime.datetime(2020, 12, 26),
    time_unit=5,
):
    return {
        "Condition": {
            "Comparison": _get_Comparison_With_DateSpan(
                comparison_kind, source, Property, value, time_unit
            )
        }
    }


def _get_Condition_Left_And_Right_Comparison(
    source: str, start_date: datetime.datetime, end_date: datetime.datetime
):
    left = {
        "Left": {
            "Comparison": _get_Comparison_With_Literal(2, source, "Date", start_date)
        }
    }
    right = {
        "Right": {
            "Comparison": _get_Comparison_With_Literal(3, source, "Date", end_date)
        },
    }
    return {"Condition": {"And": {**left, **right}}}


def _get_Condition_In_Expression(Property: str, source: str, value: str):
    return {
        "Condition": {
            "In": {
                "Expressions": [{"Column": _get_Column(source, Property)}],
                "Values": [[{"Literal": {"Value": f"'{value}'"}}]],
            }
        }
    }


# DATE RANGE GROUP QUERY SELECT
def _get_Group_Select(*options: list):
    def create_Select_item(item):
        return {item[0]: _get_Column(item[1], item[2]), "Name": f"{item[3]}.{item[2]}"}

    return list(map(create_Select_item, options))


_Date_Range_Group_Used_By_Day_Query_Options = {
    "common": {
        "Query": {
            "Version": _get_Version,
            "From": _get_From,
            "Where": [
                _get_Condition_Left_And_Right_Comparison,
                _get_Condition_In_Expression,
                _get_Condition_Comparison_With_DateSpan,
            ],
            "Select": _get_Group_Select,
        },
        "Binding": _get_Binding,
    },
    "args": {
        "Version": [],
        "From": [],
        "Where": [],
        "Select": [
            ["Column", "c1", "Date", "Calendar"],
            ["Measure", "c", "Weight running total in Date", "eRCO_podatki"],
            [
                "Measure",
                "c",
                "Tekoča vsota za mero Precepljenost v polju Date",
                "eRCO_podatki_ed",
            ],
        ],
        "OrderBy": [],
        "Binding": [[0, 1, 2], 4, {"BinnedLineSample": {}}, 1],
    },
    None: {
        "Where": [["c1"], [], ["c1"]],
        "From": [
            CommandQueryFrom("c", "eRCO_​​podatki", 0),
            CommandQueryFrom("c1", "Calendar", 0),
        ],
        "skip_common_where_index": [1],
    },
    Region: {
        "Where": [["c1"], ["Regija", "s"], ["c1"]],
        "From": [
            CommandQueryFrom("c", "eRCO_​​podatki", 0),
            CommandQueryFrom("c1", "Calendar", 0),
            CommandQueryFrom("s", "Sifrant_regija", 0),
        ],
    },
    AgeGroup: {
        "Where": [["c1"], ["Starostni ​razred", "x"], ["c1"]],
        "From": [
            CommandQueryFrom("c", "eRCO_​​podatki", 0),
            CommandQueryFrom("c1", "Calendar", 0),
            CommandQueryFrom("x", "xls_SURS_starost", 0),
        ],
    },
}


# GENDER
def _get_gender_Query_Select_Dose(dose):
    select = {
        "dose1": [
            {
                "Measure": _get_Column("e", "Weight for 1"),
                "Name": "eRCO_podatki.Weight for 1",
            }
        ],
        "dose2": [
            {
                "Aggregation": {
                    "Expression": {"Column": _get_Column("e", "Precepljenost")},
                    "Function": 0,
                },
                "Name": "Sum(eRCO_podatki_ed.Precepljenost)",
            }
        ],
    }
    return select[dose]


def _get_OrderBy(options: list = [0], select: "list[dict]" = []):
    if len(select) == 0:
        raise Exception("Empty arg [select]!")

    index = options[0]
    expression = {**select[index]}
    del expression["Name"]
    return [{"Direction": 2, "Expression": expression}]


_Date_Range_Group_Gender_Query_Options = {
    "common": {
        "Query": {
            "Version": _get_Version,
            "From": _get_From,
            "Where": [
                _get_Condition_In_Expression,
                _get_Condition_Left_And_Right_Comparison,
                _get_Condition_In_Expression,
                _get_Condition_Comparison_With_DateSpan,  # arg = "c"
            ],
            "Select": _get_gender_Query_Select_Dose,
            "OrderBy": _get_OrderBy,
        },
        "Binding": _get_Binding,
    },
    "args": {
        "Version": [],
        "From": [],
        "Where": [],
        "Select": [],
        "OrderBy": [[0]],
        "Binding": [[0], 3, {"Window": {}}, 1],
    },
    "specific": ["dose1", "dose2"],
    None: {
        "Where": [[], ["c"], [], ["c"]],
        "From": [
            CommandQueryFrom("e", "eRCO_​​podatki", 0),
            CommandQueryFrom("c", "Calendar", 0),
        ],
        "skip_common_where_index": [2],
    },
    Region: {
        "Where": [[], ["c"], ["Regija", "s"], ["c"]],
        "From": [
            CommandQueryFrom("c", "Calendar", 0),
            CommandQueryFrom("e", "eRCO_​​podatki", 0),
            CommandQueryFrom("s", "Sifrant_regija", 0),
        ],
    },
    AgeGroup: {
        "Where": [[], ["c"], ["Starostni ​razred", "x"], ["c"]],
        "From": [
            CommandQueryFrom("c", "Calendar", 0),
            CommandQueryFrom("e", "eRCO_​​podatki", 0),
            CommandQueryFrom("x", "xls_SURS_starost", 0),
        ],
    },
}


def _get_Condition_Not_Expression():
    return {
        "Condition": {
            "Not": {
                "Expression": {
                    "In": {
                        "Expressions": [{"Column": _get_Column("s", "Cepivo_Ime")}],
                        "Values": [[{"Literal": {"Value": "null"}}]],
                    }
                }
            }
        }
    }


_Date_Range_Group_Manufacturers_Query_Options = {
    "common": {
        "Query": {
            "Version": _get_Version,
            "From": _get_From,
            "Where": [
                _get_Condition_Not_Expression,
                _get_Condition_Left_And_Right_Comparison,
                _get_Condition_In_Expression,
                _get_Condition_Comparison_With_DateSpan,
            ],
            "Select": _get_Group_Select,
            "OrderBy": _get_OrderBy,
        },
        "Binding": _get_Binding,
    },
    "args": {
        "Version": [],
        "From": [],
        "Where": [],
        "Select": [
            ["Measure", "e", "Weight for 1", "eRCO_podatki"],
            ["Measure", "e", "Weight for 2", "eRCO_podatki"],
            ["Column", "s", "Cepivo_Ime", "Sifrant_Cepivo"],
        ],
        "OrderBy": [[1]],
        "Binding": [[0, 1, 2], 3, {"Window": {}}, 1],
    },
    None: {
        "Where": [[], ["c"], [], ["c"]],
        "From": [
            CommandQueryFrom("e", "eRCO_​​podatki", 0),
            CommandQueryFrom("s", "Sifrant_Cepivo", 0),
            CommandQueryFrom("c", "Calendar", 0),
        ],
        "skip_common_where_index": [2],
    },
    Region: {
        "Where": [[], ["c"], ["Regija", "s1"], ["c"]],
        "From": [
            CommandQueryFrom("e", "eRCO_​​podatki", 0),
            CommandQueryFrom("s", "Sifrant_Cepivo", 0),
            CommandQueryFrom("c", "Calendar", 0),
            CommandQueryFrom("s1", "Sifrant_regija", 0),
        ],
    },
    AgeGroup: {
        "Where": [[], ["c"], ["Starostni ​razred", "x1"], ["c"]],
        "From": [
            CommandQueryFrom("e", "eRCO_​​podatki", 0),
            CommandQueryFrom("s", "Sifrant_Cepivo", 0),
            CommandQueryFrom("c", "Calendar", 0),
            CommandQueryFrom("x1", "xls_SURS_starost", 0),
        ],
    },
}

_Date_Range_Group_Query_Options = {
    "by_day": _Date_Range_Group_Used_By_Day_Query_Options,
    "gender": _Date_Range_Group_Gender_Query_Options,
    "manufacturers": _Date_Range_Group_Manufacturers_Query_Options,
}


def _get_date_range_group_Query(
    common_options: dict,
    group_options: dict,
    version_args: list = [],
    where_args: list = [],
    select_args: list = [],
    order_by_args: list = [],
):

    from_args = group_options["From"]

    Query = common_options["Query"]

    skip_where_function_index = group_options.get("skip_common_where_index", [])

    select = Query["Select"](*select_args)

    where = _get_Where(
        Query["Where"], group_options["Where"], where_args, skip_where_function_index
    )

    order_by = Query.get("OrderBy", None)

    order_by = {"OrderBy": order_by(*order_by_args, select)} if order_by != None else {}
    command = {}
    command["Query"] = {
        "Version": Query["Version"](*version_args),
        "From": Query["From"](*from_args),
        "Select": select,
        "Where": where,
        **order_by,
    }

    return command


def _get_command(
    group: Union[Region, AgeGroup],
    command_type: str,
    where_args: list = [],
    specific_args: dict = {"Select": [], "OrderBy": []},
):
    command_options = _Date_Range_Group_Query_Options[command_type]
    common_options = command_options["common"]
    args_options = command_options["args"]

    version_args = args_options["Version"]
    select_args = [*specific_args["Select"], *args_options["Select"]]
    order_by_args = args_options["OrderBy"]
    binding_args = args_options["Binding"]

    command = {}
    command["SemanticQueryDataShapeCommand"] = {
        "Binding": common_options["Binding"](*binding_args),
        **_ExecutionMetrics,
    }
    group_type = type(group)
    group_options = command_options[group_type if group_type != type(None) else None]

    query = _get_date_range_group_Query(
        common_options,
        group_options,
        version_args,
        where_args,
        select_args,
        order_by_args,
    )

    command["SemanticQueryDataShapeCommand"] = {
        **query,
        **command["SemanticQueryDataShapeCommand"],
    }
    return command


def _get_gender_commands(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    group: Union[Region, AgeGroup, None],
):
    specific_options = _Date_Range_Group_Gender_Query_Options["specific"]

    commands = {}
    for gender in Gender:
        where_args = [
            ["OsebaSpol", "e", gender.value],
            [start_date, end_date],
            [group.value] if group != None else [],
            [],
        ]
        commands[gender] = [
            _get_command(
                group,
                "gender",
                where_args=where_args,
                specific_args={"Select": [dose]},
            )
            for dose in specific_options
        ]

    return commands


def _get_date_range_group_commands(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    group: Union[Region, AgeGroup, None],
) -> DateRangeCommands_Requests:

    where_by_day_args = [
        [start_date, end_date],
        [group.value] if group != None else [],
        [],
    ]
    where_manufacturers_args = [
        [],
        [start_date, end_date],
        [group.value] if group != None else [],
        [],
    ]

    by_day = _get_command(group, "by_day", where_by_day_args)

    gender = _get_gender_commands(start_date, end_date, group)
    male = gender[Gender.MALE]
    female = gender[Gender.FEMALE]

    manufacturers = _get_command(group, "manufacturers", where_manufacturers_args)

    commands = DateRangeCommands_Requests(by_day, *male, *female, manufacturers)

    return commands


def _get_default_manufacturer_used_command(manu: Manufacturer):
    return {
        "SemanticQueryDataShapeCommand": {
            "Query": {
                "Version": _get_Version(),
                "From": _get_From(
                    CommandQueryFrom("c1", "Calendar", 0),
                    CommandQueryFrom("s", "Sifrant_Cepivo", 0),
                    CommandQueryFrom("c", "eRCO_​​podatki", 0),
                ),
                "Select": [
                    {
                        "Column": _get_Column("c1", "Date"),
                        "Name": "Calendar.Date",
                    },
                    {
                        "Measure": _get_Column("c", "Weight for 1"),
                        "Name": "eRCO_​​podatki.Weight for 1",
                    },
                    {
                        "Measure": _get_Column("c", "Weight for 2"),
                        "Name": "eRCO_​​podatki.Weight for 2",
                    },
                    {
                        "Measure": _get_Column("c", "Weight for 2"),
                        "Name": "eRCO_​​podatki.Weight for 2",
                    },
                    {
                        "Aggregation": {
                            "Expression": {"Column": _get_Column("c", "weight")},
                            "Function": 0,
                        },
                        "Name": "Sum(eRCO_podatki_ed.Weight)",
                    },
                ],
                "Where": [
                    _get_Condition_Comparison_With_DateSpan("c1", 2),
                    _get_Condition_In_Expression("Cepivo_Ime", "s", manu.value),
                ],
            },
            "Binding": {
                "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3, 4]}]},
                "DataReduction": {"DataVolume": 4, "Primary": {"Sample": {}}},
                "Version": 1,
            },
            **_ExecutionMetrics,
        }
    }


def _create_manufacturers_used_commands():
    obj = {}
    for manu in Manufacturer:
        obj[manu] = _get_default_manufacturer_used_command(manu)

    return obj


def _create_in_range_by_age_by_gender_command(
    date_start: datetime.datetime, date_end: datetime.datetime
):
    def _create_by_age_by_gender_command(age_group: AgeGroup):
        def _create_by_gender_command(gender: Gender):

            _from = [
                {"Name": "e", "Entity": "eRCO_​​podatki", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
                {"Name": "x", "Entity": "xls_SURS_starost", "Type": 0},
            ]

            first_select = [
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "e"}},
                        "Property": "Weight for 1",
                    },
                    "Name": "eRCO_podatki.Weight for 1",
                }
            ]

            second_select = [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "e"}},
                                "Property": "Precepljenost",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(eRCO_podatki_ed.Precepljenost)",
                }
            ]

            first_order_by = [
                {
                    "Direction": 2,
                    "Expression": {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "e"}},
                            "Property": "Weight for 1",
                        }
                    },
                }
            ]

            second_order_by = [
                {
                    "Direction": 2,
                    "Expression": {
                        "Aggregation": {
                            "Expression": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "e"}},
                                    "Property": "Precepljenost",
                                }
                            },
                            "Function": 0,
                        }
                    },
                }
            ]

            binding = {
                "Primary": {"Groupings": [{"Projections": [0]}]},
                "DataReduction": {
                    "DataVolume": 3,
                    "Primary": {"Window": {}},
                },
                "Version": 1,
            }

            def _first_dose_command():
                return {
                    "SemanticQueryDataShapeCommand": {
                        "Query": {
                            "Version": 2,
                            "From": _from,
                            "Select": first_select,
                            "Where": [
                                {
                                    "Condition": {
                                        "In": {
                                            "Expressions": [
                                                {
                                                    "Column": {
                                                        "Expression": {
                                                            "SourceRef": {"Source": "e"}
                                                        },
                                                        "Property": "OsebaSpol",
                                                    }
                                                }
                                            ],
                                            "Values": [
                                                [
                                                    {
                                                        "Literal": {
                                                            "Value": f"'{gender.value}'"
                                                        }
                                                    }
                                                ]
                                            ],
                                        }
                                    }
                                },
                                {
                                    "Condition": {
                                        "And": {
                                            "Left": {
                                                "Comparison": {
                                                    "ComparisonKind": 2,
                                                    "Left": {
                                                        "Column": {
                                                            "Expression": {
                                                                "SourceRef": {
                                                                    "Source": "c"
                                                                }
                                                            },
                                                            "Property": "Date",
                                                        }
                                                    },
                                                    "Right": {
                                                        "Literal": {
                                                            "Value": f"datetime'{date_start.isoformat()}'"
                                                        }
                                                    },
                                                }
                                            },
                                            "Right": {
                                                "Comparison": {
                                                    "ComparisonKind": 3,
                                                    "Left": {
                                                        "Column": {
                                                            "Expression": {
                                                                "SourceRef": {
                                                                    "Source": "c"
                                                                }
                                                            },
                                                            "Property": "Date",
                                                        }
                                                    },
                                                    "Right": {
                                                        "Literal": {
                                                            "Value": f"datetime'{date_end.isoformat()}'"
                                                        }
                                                    },
                                                }
                                            },
                                        }
                                    }
                                },
                                {
                                    "Condition": {
                                        "In": {
                                            "Expressions": [
                                                {
                                                    "Column": {
                                                        "Expression": {
                                                            "SourceRef": {"Source": "x"}
                                                        },
                                                        "Property": "Starostni ​razred",
                                                    }
                                                }
                                            ],
                                            "Values": [
                                                [
                                                    {
                                                        "Literal": {
                                                            "Value": f"'{age_group.value}'"
                                                        }
                                                    }
                                                ]
                                            ],
                                        }
                                    }
                                },
                                {
                                    "Condition": {
                                        "Not": {
                                            "Expression": {
                                                "In": {
                                                    "Expressions": [
                                                        {
                                                            "Column": {
                                                                "Expression": {
                                                                    "SourceRef": {
                                                                        "Source": "e"
                                                                    }
                                                                },
                                                                "Property": "CepivoIme",
                                                            }
                                                        }
                                                    ],
                                                    "Values": [
                                                        [{"Literal": {"Value": "null"}}]
                                                    ],
                                                }
                                            }
                                        }
                                    }
                                },
                                {
                                    "Condition": {
                                        "Comparison": {
                                            "ComparisonKind": 1,
                                            "Left": {
                                                "Column": {
                                                    "Expression": {
                                                        "SourceRef": {"Source": "c"}
                                                    },
                                                    "Property": "Date",
                                                }
                                            },
                                            "Right": {
                                                "DateSpan": {
                                                    "Expression": {
                                                        "Literal": {
                                                            "Value": "datetime'2020-12-26T01:00:00'"
                                                        }
                                                    },
                                                    "TimeUnit": 5,
                                                }
                                            },
                                        }
                                    }
                                },
                            ],
                            "OrderBy": first_order_by,
                        },
                        "Binding": binding,
                        "ExecutionMetricsKind": 1,
                    }
                }

            def _second_dose_command():
                return {
                    "SemanticQueryDataShapeCommand": {
                        "Query": {
                            "Version": 2,
                            "From": _from,
                            "Select": second_select,
                            "Where": [
                                {
                                    "Condition": {
                                        "In": {
                                            "Expressions": [
                                                {
                                                    "Column": {
                                                        "Expression": {
                                                            "SourceRef": {"Source": "e"}
                                                        },
                                                        "Property": "OsebaSpol",
                                                    }
                                                }
                                            ],
                                            "Values": [
                                                [
                                                    {
                                                        "Literal": {
                                                            "Value": f"'{gender.value}'"
                                                        }
                                                    }
                                                ]
                                            ],
                                        }
                                    }
                                },
                                {
                                    "Condition": {
                                        "And": {
                                            "Left": {
                                                "Comparison": {
                                                    "ComparisonKind": 2,
                                                    "Left": {
                                                        "Column": {
                                                            "Expression": {
                                                                "SourceRef": {
                                                                    "Source": "c"
                                                                }
                                                            },
                                                            "Property": "Date",
                                                        }
                                                    },
                                                    "Right": {
                                                        "Literal": {
                                                            "Value": f"datetime'{date_start.isoformat()}'"
                                                        }
                                                    },
                                                }
                                            },
                                            "Right": {
                                                "Comparison": {
                                                    "ComparisonKind": 3,
                                                    "Left": {
                                                        "Column": {
                                                            "Expression": {
                                                                "SourceRef": {
                                                                    "Source": "c"
                                                                }
                                                            },
                                                            "Property": "Date",
                                                        }
                                                    },
                                                    "Right": {
                                                        "Literal": {
                                                            "Value": f"datetime'{date_end.isoformat()}'"
                                                        }
                                                    },
                                                }
                                            },
                                        }
                                    }
                                },
                                {
                                    "Condition": {
                                        "In": {
                                            "Expressions": [
                                                {
                                                    "Column": {
                                                        "Expression": {
                                                            "SourceRef": {"Source": "x"}
                                                        },
                                                        "Property": "Starostni ​razred",
                                                    }
                                                }
                                            ],
                                            "Values": [
                                                [
                                                    {
                                                        "Literal": {
                                                            "Value": f"'{age_group.value}'"
                                                        }
                                                    }
                                                ]
                                            ],
                                        }
                                    }
                                },
                                {
                                    "Condition": {
                                        "Not": {
                                            "Expression": {
                                                "In": {
                                                    "Expressions": [
                                                        {
                                                            "Column": {
                                                                "Expression": {
                                                                    "SourceRef": {
                                                                        "Source": "e"
                                                                    }
                                                                },
                                                                "Property": "CepivoIme",
                                                            }
                                                        }
                                                    ],
                                                    "Values": [
                                                        [{"Literal": {"Value": "null"}}]
                                                    ],
                                                }
                                            }
                                        }
                                    }
                                },
                                {
                                    "Condition": {
                                        "Comparison": {
                                            "ComparisonKind": 1,
                                            "Left": {
                                                "Column": {
                                                    "Expression": {
                                                        "SourceRef": {"Source": "c"}
                                                    },
                                                    "Property": "Date",
                                                }
                                            },
                                            "Right": {
                                                "DateSpan": {
                                                    "Expression": {
                                                        "Literal": {
                                                            "Value": "datetime'2020-12-26T01:00:00'"
                                                        }
                                                    },
                                                    "TimeUnit": 5,
                                                }
                                            },
                                        }
                                    }
                                },
                            ],
                            "OrderBy": second_order_by,
                        },
                        "Binding": binding,
                        "ExecutionMetricsKind": 1,
                    }
                }

            return {"first": _first_dose_command(), "second": _second_dose_command()}

        return _create_by_gender_command

    return _create_by_age_by_gender_command
