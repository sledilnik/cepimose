from typing import Union
from cepimose.types import DateRangeCommands_Requests
import json
import datetime
from .enums import Region, AgeGroup, Manufacturer, Gender

from .commands import (
    _get_date_range_group_commands,
    _create_manufacturers_used_commands,
    _create_in_range_by_age_by_gender_command,
)

_source = "https://wabi-west-europe-e-primary-api.analysis.windows.net/public/reports/querydata?synchronous=true"

_models = {
    "nijz-vaccinations-ver1": {
        "headers": {
            "X-PowerBI-ResourceKey": "e868280f-1322-4be2-a19a-e9fc2112609f",
        },
        "modelId": 159824,
        "ApplicationContext": {
            "DatasetId": "7b40529e-a50e-4dd3-8fe8-997894b4cdaa",
            "Sources": [{"ReportId": "b201281d-b2e7-4470-9f4e-0b3063794c76"}],
        },
    },
    "nijz-vaccinations-ver2": {
        "headers": {
            "X-PowerBI-ResourceKey": "ad74a553-ebd2-476f-ab42-d79b590dd8c2",
        },
        "modelId": 175575,
        "ApplicationContext": {
            "DatasetId": "51c64860-e9ec-49d8-8a36-743bced78e1a",
            "Sources": [{"ReportId": "dddc4907-41d2-4b6c-b34b-3aac90b7fdee"}],
        },
    },
    "nijz-vaccinations-ver3": {
        "headers": {
            "X-PowerBI-ResourceKey": "ad74a553-ebd2-476f-ab42-d79b590dd8c2",
        },
        "modelId": 175575,
        "ApplicationContext": {
            "DatasetId": "51c64860-e9ec-49d8-8a36-743bced78e1a",
            "Sources": [
                {
                    "ReportId": "dddc4907-41d2-4b6c-b34b-3aac90b7fdee",
                    "VisualId": "022fd838583336ee7f55",
                }
            ],
        },
    },
    "nijz-vaccinations-ver4": {
        "headers": {
            "X-PowerBI-ResourceKey": "ad74a553-ebd2-476f-ab42-d79b590dd8c2",
        },
        "modelId": 175575,
        "ApplicationContext": {
            "DatasetId": "51c64860-e9ec-49d8-8a36-743bced78e1a",
            "Sources": [
                {
                    "ReportId": "dddc4907-41d2-4b6c-b34b-3aac90b7fdee",
                    "VisualId": "6c5cb705405bd5425008",
                }
            ],
        },
    },
    "nijz-lab-ver1": {
        "headers": {"X-PowerBI-ResourceKey": "0770982d-8a85-4a4d-82b9-5d329983e65a"},
        "modelId": 165881,
        "ApplicationContext": {
            "DatasetId": "b61173e7-66f4-4659-808b-ba7bd1e74fb5",
            "Sources": [
                {
                    "ReportId": "130880e0-231a-49f2-b031-0669ae443a50",
                    "VisualId": "5620f6f79b45ee8dcb57",
                }
            ],
        },
    },
}


def _get_model_version(ver):
    x_power_bi_resource_key = _models[ver]["headers"]["X-PowerBI-ResourceKey"]
    model_id = _models[ver]["modelId"]
    application_context = _models[ver]["ApplicationContext"]
    return {
        "X-PowerBI-ResourceKey": x_power_bi_resource_key,
        "modelId": model_id,
        "ApplicationContext": application_context,
    }


_vaccinations_dashboard_model_ver = _get_model_version("nijz-vaccinations-ver4")
_lab_dashboard_model_ver = _get_model_version("nijz-lab-ver1")

_model_versions = {
    "vaccinations": _vaccinations_dashboard_model_ver,
    "lab": _lab_dashboard_model_ver,
}


def _get_dashboard_headers(dashboard: str):
    _model_ver = _model_versions[dashboard]
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "application/json, text/plain, */*",
        "X-PowerBI-ResourceKey": _model_ver["X-PowerBI-ResourceKey"],
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://app.powerbi.com",
        "Connection": "keep-alive",
        "Referer": "https://app.powerbi.com/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }


_vaccinations_dashboard_headers = _get_dashboard_headers("vaccinations")
_lab_dashboard_headers = _get_dashboard_headers("lab")


def _get_default_req(dashboard: str):
    _model_ver = _model_versions[dashboard]
    return {
        "cancelQueries": [],
        "modelId": _model_ver["modelId"],
        "version": "1.0.0",
        "queries": [],
    }


def _get_default_query(dashboard: str):
    _model_ver = _model_versions[dashboard]
    return {
        "ApplicationContext": _model_ver["ApplicationContext"],
        "CacheKey": "",
        "Query": {"Commands": []},
        "QueryId": "",
    }


def _create_req(dashboard: str, commands: list, cache_key=False):
    query = _get_default_query(dashboard)
    for command in commands:
        query["Query"]["Commands"].append(command)
    if cache_key:
        query["CacheKey"] = json.dumps(query["Query"]["Commands"])
    req = _get_default_req(dashboard)
    req["queries"].append(query)
    return req


# AGE RANGE (AGE GROUP)
def _get_default_by_age_group_command():
    return {
        "SemanticQueryDataShapeCommand": {
            "Query": {
                "Version": 2,
                "From": [
                    {"Name": "c1", "Entity": "Calendar", "Type": 0},
                    {"Name": "c", "Entity": "eRCO_​​podatki", "Type": 0},
                    {"Name": "x", "Entity": "xls_SURS_starost", "Type": 0},
                ],
                "Select": [
                    {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "c1"}},
                            "Property": "Date",
                        },
                        "Name": "Calendar.Date",
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "c"}},
                            "Property": "KUM_St_en_odmerek",
                        },
                        "Name": "eRCO_podatki.Weight running total in Date",
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "c"}},
                            "Property": "KUM_St_precepljenost",
                        },
                        "Name": "eRCO_podatki_ed.Tekoča vsota za mero Precepljenost v polju Date",
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "c"}},
                            "Property": "KUM_St_dodaten",
                        },
                        "Name": "eRCO_​​podatki.KUM_St_dodaten",
                    },
                ],
                "Where": [
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
                                "Values": [],
                            }
                        }
                    }
                ],
            },
            "Binding": {
                "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3]}]},
                "DataReduction": {"DataVolume": 4, "Primary": {"BinnedLineSample": {}}},
                "Version": 1,
            },
            "ExecutionMetricsKind": 1,
        }
    }


def _get_by_age_group_first_condition_values(group="'90+'"):
    return [
        {"Literal": {"Value": f"'{group}'"}},
    ]


def _create_by_age_group_command(group="'90+'"):
    values = _get_by_age_group_first_condition_values(group)
    command = _get_default_by_age_group_command()
    command["SemanticQueryDataShapeCommand"]["Query"]["Where"][0]["Condition"]["In"][
        "Values"
    ].append(values)
    return command


def _create_by_age_group_commands():
    obj = {}
    for el in AgeGroup:
        command = _create_by_age_group_command(el.value)
        obj[el] = [command]

    return obj


def _create_by_age_group_requests():
    commands = _create_by_age_group_commands()
    key_value = commands.items()
    obj = {}
    for el in key_value:
        key = el[0]
        _commands = el[1]
        group_requests = []
        req = _create_req("vaccinations", [_commands[0]])
        obj[key] = [req]

    return obj


# BY REGION BY DAY
def _get_default_by_region_by_day_command():
    return {
        "SemanticQueryDataShapeCommand": {
            "Query": {
                "Version": 2,
                "From": [
                    {"Name": "c1", "Entity": "Calendar", "Type": 0},
                    {"Name": "c", "Entity": "eRCO_​​podatki", "Type": 0},
                    {"Name": "s", "Entity": "Sifrant_regija", "Type": 0},
                ],
                "Select": [
                    {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "c1"}},
                            "Property": "Date",
                        },
                        "Name": "Calendar.Date",
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "c"}},
                            "Property": "KUM_St_en_odmerek",
                        },
                        "Name": "eRCO_podatki.Weight running total in Date",
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "c"}},
                            "Property": "KUM_St_precepljenost",
                        },
                        "Name": "eRCO_podatki_ed.Tekoča vsota za mero Precepljenost v polju Date",
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "c"}},
                            "Property": "KUM_St_dodaten",
                        },
                        "Name": "eRCO_​​podatki.KUM_St_dodaten",
                    },
                ],
                "Where": [
                    {
                        "Condition": {
                            "In": {
                                "Expressions": [
                                    {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "s"}
                                            },
                                            "Property": "Regija",
                                        }
                                    }
                                ],
                                "Values": [],
                            }
                        }
                    }
                ],
            },
            "Binding": {
                "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3]}]},
                "DataReduction": {"DataVolume": 4, "Primary": {"BinnedLineSample": {}}},
                "Version": 1,
            },
            "ExecutionMetricsKind": 1,
        }
    }


def _get_default_by_region_by_day_condition_values(region):
    return [{"Literal": {"Value": f"'{region}'"}}]


def _create_by_region_by_day_command(region):
    values = _get_default_by_region_by_day_condition_values(region)
    command = _get_default_by_region_by_day_command()
    command["SemanticQueryDataShapeCommand"]["Query"]["Where"][0]["Condition"]["In"][
        "Values"
    ].append(values)
    return command


def _create_by_region_by_day_commands():
    obj = {}
    for el in Region:
        doses_command = _create_by_region_by_day_command(el.value)
        obj[el] = [doses_command]

    return obj


def _create_by_region_by_day_requests():
    commands = _create_by_region_by_day_commands()
    key_value = commands.items()
    obj = {}
    for el in key_value:
        key = el[0]
        _commands = el[1]
        group_requests = []
        doses_req = _create_req("vaccinations", [_commands[0]])
        obj[key] = [doses_req]

    return obj


# AGE GROUP BY REGION ON DAY
def _get_age_group_by_region_on_day_first_condition_value(group="'90+'"):
    return [{"Literal": {"Value": f"'{group}'"}}]


def _get_default_age_group_by_region_on_day_command():
    return {
        "SemanticQueryDataShapeCommand": {
            "Query": {
                "Version": 2,
                "From": [
                    {"Name": "e", "Entity": "eRCO_​​podatki", "Type": 0},
                    {"Name": "s1", "Entity": "Sifrant_regija", "Type": 0},
                    {"Name": "c", "Entity": "Calendar", "Type": 0},
                ],
                "Select": [
                    {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "s1"}},
                            "Property": "Regija",
                        },
                        "Name": "Sifrant_regija.Regija",
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "e"}},
                            "Property": "Delež_regija_1",
                        },
                        "Name": "eRCO_podatki.Delež_regija",
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "e"}},
                            "Property": "Delež_regija_precepljenost",
                        },
                        "Name": "eRCO_podatki_ed.Delež_regija_precepljenost",
                    },
                    {
                        "Aggregation": {
                            "Expression": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "e"}},
                                    "Property": "Odmerek – kopija",
                                }
                            },
                            "Function": 0,
                        },
                        "Name": "Sum(eRCO_​​podatki.Odmerek – kopija)",
                    },
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
                        "Name": "Sum(eRCO_​​podatki.Precepljenost)",
                    },
                ],
                "Where": [
                    {
                        "Condition": {
                            "Not": {
                                "Expression": {
                                    "In": {
                                        "Expressions": [
                                            {
                                                "Column": {
                                                    "Expression": {
                                                        "SourceRef": {"Source": "e"}
                                                    },
                                                    "Property": "CepivoIme",
                                                }
                                            }
                                        ],
                                        "Values": [[{"Literal": {"Value": "null"}}]],
                                    }
                                }
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
                                                        "SourceRef": {"Source": "s1"}
                                                    },
                                                    "Property": "Regija",
                                                }
                                            }
                                        ],
                                        "Values": [
                                            [{"Literal": {"Value": "null"}}],
                                            [
                                                {
                                                    "Literal": {
                                                        "Value": "'Celotna Slovenija'"
                                                    }
                                                }
                                            ],
                                            [{"Literal": {"Value": "'TUJINA'"}}],
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
                                        "Expression": {"SourceRef": {"Source": "c"}},
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
                "OrderBy": [
                    {
                        "Direction": 2,
                        "Expression": {
                            "Measure": {
                                "Expression": {"SourceRef": {"Source": "e"}},
                                "Property": "Delež_regija_1",
                            }
                        },
                    }
                ],
            },
            "Binding": {
                "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3, 4]}]},
                "DataReduction": {
                    "DataVolume": 4,
                    "Primary": {"Window": {"Count": 1000}},
                },
                "SuppressedJoinPredicates": [3, 4],
                "Version": 1,
                "Highlights": [
                    {
                        "Version": 2,
                        "From": [
                            {"Name": "x", "Entity": "xls_SURS_starost", "Type": 0},
                            {"Name": "e", "Entity": "eRCO_​​podatki", "Type": 0},
                        ],
                        "Where": [
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
                                        "Values": [],
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
                        ],
                    }
                ],
            },
            "ExecutionMetricsKind": 1,
        }
    }


def _create_age_group_by_region_on_day_command(group="'90+'"):
    values = _get_age_group_by_region_on_day_first_condition_value(group)
    command = _get_default_age_group_by_region_on_day_command()
    command["SemanticQueryDataShapeCommand"]["Binding"]["Highlights"][0]["Where"][0][
        "Condition"
    ]["In"]["Values"].append(values)
    return command


def _create_age_group_by_region_on_day_commands():
    obj = {}
    for el in AgeGroup:
        command = _create_age_group_by_region_on_day_command(el.value)
        obj[el] = [command]

    return obj


def _create_age_group_by_region_on_day_requests():
    commands = _create_age_group_by_region_on_day_commands()
    key_value = commands.items()
    obj = {}
    for el in key_value:
        key = el[0]
        _commands = el[1]
        req = _create_req("vaccinations", [_commands[0]])
        obj[key] = [req]

    return obj


# BY MANU SUPPLIED AND USED
def _get_vaccination_by_manufacturer_supplied_used_second_condition_value(group):
    return [{"Literal": {"Value": f"'{group}'"}}]


def _get_default_vaccination_by_manufacturer_supplied_used_command():
    return {
        "SemanticQueryDataShapeCommand": {
            "Query": {
                "Version": 2,
                "From": [
                    {"Name": "c1", "Entity": "Calendar", "Type": 0},
                    {"Name": "c", "Entity": "eRCO_​​podatki", "Type": 0},
                    {"Name": "n", "Entity": "xls_NIJZ_Odmerki", "Type": 0},
                    {"Name": "s", "Entity": "Sifrant_Cepivo", "Type": 0},
                ],
                "Select": [
                    {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "c1"}},
                            "Property": "Date",
                        },
                        "Name": "Calendar.Date",
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "c"}},
                            "Property": "Kumulativno skupaj cepljenih",
                        },
                        "Name": "eRCO_podatki.Kumulativno skupaj cepljenih",
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "n"}},
                            "Property": "Tekoča vsota za mero odmerki*​ v polju Date",
                        },
                        "Name": "NIJZ_Odmerki.Tekoča vsota za mero odmerki* v polju Date",
                    },
                ],
                "Where": [
                    {
                        "Condition": {
                            "Comparison": {
                                "ComparisonKind": 2,
                                "Left": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "c1"}},
                                        "Property": "Date",
                                    }
                                },
                                "Right": {
                                    "DateSpan": {
                                        "Expression": {
                                            "Literal": {
                                                "Value": "datetime'2020-12-26T00:00:00'"
                                            }
                                        },
                                        "TimeUnit": 5,
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
                                                "SourceRef": {"Source": "s"}
                                            },
                                            "Property": "Cepivo_Ime",
                                        }
                                    }
                                ],
                                "Values": [],
                            }
                        }
                    },
                ],
            },
            "Binding": {
                "Primary": {"Groupings": [{"Projections": [0, 1, 2]}]},
                "DataReduction": {"DataVolume": 4, "Primary": {"BinnedLineSample": {}}},
                "Version": 1,
            },
            "ExecutionMetricsKind": 1,
        }
    }


def _create_vaccination_by_manufacturer_supplied_used_command(group):
    values = _get_vaccination_by_manufacturer_supplied_used_second_condition_value(
        group
    )
    command = _get_default_vaccination_by_manufacturer_supplied_used_command()
    command["SemanticQueryDataShapeCommand"]["Query"]["Where"][1]["Condition"]["In"][
        "Values"
    ].append(values)
    return command


def _create_vaccination_by_manufacturer_supplied_used_commands():
    obj = {}
    for el in Manufacturer:
        command = _create_vaccination_by_manufacturer_supplied_used_command(el.value)
        obj[el] = [command]

    return obj


def _create_vaccination_by_manufacturer_supplied_used_requests():
    commands = _create_vaccination_by_manufacturer_supplied_used_commands()
    key_value = commands.items()
    obj = {}
    for el in key_value:
        key = el[0]
        _commands = el[1]
        req = _create_req("vaccinations", [_commands[0]])
        obj[key] = [req]

    return obj


# BY GENDER WITH DATE RANGE


def _get_vaccinations_gender_condition(gender):
    return [{"Literal": {"Value": f"'{gender}'"}}]


def _get_vaccinations_gender_date_condition(date: datetime.datetime):
    return {"Literal": {"Value": f"datetime'{date.isoformat()}'"}}


def _get_default_vaccinations_gender_first_between_dates_command():
    return {
        "SemanticQueryDataShapeCommand": {
            "Query": {
                "Version": 2,
                "From": [
                    {"Name": "e", "Entity": "eRCO_​​podatki", "Type": 0},
                    {"Name": "c", "Entity": "Calendar", "Type": 0},
                ],
                "Select": [
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "e"}},
                            "Property": "Weight for 1",
                        },
                        "Name": "eRCO_podatki.Weight for 1",
                    }
                ],
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
                                "Values": [],
                            }
                        }
                    },
                    {
                        "Condition": {
                            "Comparison": {
                                "ComparisonKind": 3,
                                "Left": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "c"}},
                                        "Property": "Date",
                                    }
                                },
                                "Right": {},
                            }
                        }
                    },
                    {
                        "Condition": {
                            "Comparison": {
                                "ComparisonKind": 1,
                                "Left": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "c"}},
                                        "Property": "Date",
                                    }
                                },
                                "Right": {
                                    "DateSpan": {
                                        "Expression": {},
                                        "TimeUnit": 5,
                                    }
                                },
                            }
                        }
                    },
                ],
                "OrderBy": [
                    {
                        "Direction": 2,
                        "Expression": {
                            "Measure": {
                                "Expression": {"SourceRef": {"Source": "e"}},
                                "Property": "Weight for 1",
                            }
                        },
                    }
                ],
            },
            "Binding": {
                "Primary": {"Groupings": [{"Projections": [0]}]},
                "DataReduction": {"DataVolume": 3, "Primary": {"Window": {}}},
                "Version": 1,
            },
            "ExecutionMetricsKind": 1,
        }
    }


def _get_default_vaccinations_gender_second_between_dates_command():
    return {
        "SemanticQueryDataShapeCommand": {
            "Query": {
                "Version": 2,
                "From": [
                    {"Name": "e", "Entity": "eRCO_​​podatki", "Type": 0},
                    {"Name": "c", "Entity": "Calendar", "Type": 0},
                ],
                "Select": [
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
                ],
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
                                "Values": [],
                            }
                        }
                    },
                    {
                        "Condition": {
                            "Comparison": {
                                "ComparisonKind": 3,
                                "Left": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "c"}},
                                        "Property": "Date",
                                    }
                                },
                                "Right": {},
                            }
                        }
                    },
                    {
                        "Condition": {
                            "Comparison": {
                                "ComparisonKind": 1,
                                "Left": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "c"}},
                                        "Property": "Date",
                                    }
                                },
                                "Right": {
                                    "DateSpan": {
                                        "Expression": {},
                                        "TimeUnit": 5,
                                    }
                                },
                            }
                        }
                    },
                ],
                "OrderBy": [
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
                ],
            },
            "Binding": {
                "Primary": {"Groupings": [{"Projections": [0]}]},
                "DataReduction": {"DataVolume": 3, "Primary": {"Window": {}}},
                "Version": 1,
            },
            "ExecutionMetricsKind": 1,
        }
    }


def _create_vaccinations_gender_first_and_second_between_dates_command(
    gender,
    start_date: datetime.datetime = datetime.datetime(2020, 12, 26),
    end_date: datetime.datetime = datetime.datetime(2020, 12, 28),
):
    gender_value = _get_vaccinations_gender_condition(gender)
    date_start_value = _get_vaccinations_gender_date_condition(start_date)
    date_end_value = _get_vaccinations_gender_date_condition(end_date)
    command_first = _get_default_vaccinations_gender_first_between_dates_command()
    command_first["SemanticQueryDataShapeCommand"]["Query"]["Where"][0]["Condition"][
        "In"
    ]["Values"].append(gender_value)
    command_first["SemanticQueryDataShapeCommand"]["Query"]["Where"][1]["Condition"][
        "Comparison"
    ]["Right"] = {**date_end_value}

    command_first["SemanticQueryDataShapeCommand"]["Query"]["Where"][2]["Condition"][
        "Comparison"
    ]["Right"]["DateSpan"]["Expression"] = {**date_start_value}

    command_second = _get_default_vaccinations_gender_second_between_dates_command()
    command_second["SemanticQueryDataShapeCommand"]["Query"]["Where"][0]["Condition"][
        "In"
    ]["Values"].append(gender_value)
    command_second["SemanticQueryDataShapeCommand"]["Query"]["Where"][1]["Condition"][
        "Comparison"
    ]["Right"] = {**date_end_value}
    command_second["SemanticQueryDataShapeCommand"]["Query"]["Where"][2]["Condition"][
        "Comparison"
    ]["Right"]["DateSpan"]["Expression"] = {**date_start_value}
    return [command_first, command_second]


def _create_vaccinations_gender_commands(
    start_date: datetime.datetime = datetime.datetime(2020, 12, 26),
    end_date: datetime.datetime = datetime.datetime(2020, 12, 28),
):
    obj = {}
    for el in Gender:
        (
            command_first,
            command_second,
        ) = _create_vaccinations_gender_first_and_second_between_dates_command(
            el.value, start_date, end_date
        )
        obj[el] = [command_first, command_second]
    return obj


def _create_vaccination_gender_requests():
    first_date = datetime.datetime(2020, 12, 27)
    day_delta = datetime.timedelta(days=1)
    last_date = datetime.datetime.today() + day_delta

    request_by_date = []
    for i in range((last_date - first_date).days):
        date = first_date + i * day_delta
        start_date = first_date + (i - 1) * day_delta
        end_date = first_date + (i + 1) * day_delta
        commands = _create_vaccinations_gender_commands(
            start_date=start_date, end_date=end_date
        )
        female_first_command, female_second_command = commands[Gender.FEMALE]
        male_first_command, male_second_command = commands[Gender.MALE]

        female_first_req = _create_req("vaccinations", [female_first_command])
        female_second_req = _create_req("vaccinations", [female_second_command])
        male_first_req = _create_req("vaccinations", [male_first_command])
        male_second_req = _create_req("vaccinations", [male_second_command])

        obj = {
            "date": date,
            Gender.FEMALE: [female_first_req, female_second_req],
            Gender.MALE: [male_first_req, male_second_req],
        }
        request_by_date.append(obj)
    return request_by_date


def _create_vaccinations_by_manufacturer_requests():
    commands = _create_manufacturers_used_commands()
    obj = {}
    for key, value in commands.items():
        obj[key] = _create_req("vaccinations", [value])
    return obj


# COMMANDS
_vaccinations_timestamp_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "e", "Entity": "eRCO_​​podatki", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "e"}},
                                "Property": "DatumOsveževanja",
                            }
                        },
                        "Function": 3,
                    },
                    "Name": "Min(eRCO_podatki.DatumOsvezevanja)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 1,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
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
                }
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_vaccinations_by_day_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "c1", "Entity": "Calendar", "Type": 0},
                {"Name": "c", "Entity": "eRCO_​​podatki", "Type": 0},
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "c1"}},
                        "Property": "Date",
                    },
                    "Name": "Calendar.Date",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "c"}},
                        "Property": "KUM_St_en_odmerek",
                    },
                    "Name": "eRCO_podatki.Weight running total in Date",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "c"}},
                        "Property": "KUM_St_precepljenost",
                    },
                    "Name": "eRCO_podatki_ed.Tekoča vsota za mero Precepljenost v polju Date",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "c"}},
                        "Property": "KUM_St_dodaten",
                    },
                    "Name": "eRCO_​​podatki.KUM_St_dodaten",
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3]}]},
            "DataReduction": {"DataVolume": 4, "Primary": {"BinnedLineSample": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_vaccinations_by_age_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "s", "Entity": "xls_SURS_starost", "Type": 0},
                {"Name": "e", "Entity": "eRCO_​​podatki", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "s"}},
                        "Property": "Starostni ​razred",
                    },
                    "Name": "SURS_starost.Starostni razred",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "e"}},
                        "Property": "Delež_starost_precepljenost",
                    },
                    "Name": "eRCO_podatki_ed.Delež_starost_precepljenost",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "e"}},
                        "Property": "Delež_starost_1",
                    },
                    "Name": "eRCO_podatki_ed.Delež_starost",
                },
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "e"}},
                                "Property": "Odmerek – kopija",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(eRCO_​​podatki.Odmerek – kopija)",
                },
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
                    "Name": "Sum(eRCO_​​podatki.Precepljenost)",
                },
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "In": {
                                    "Expressions": [
                                        {
                                            "Column": {
                                                "Expression": {
                                                    "SourceRef": {"Source": "e"}
                                                },
                                                "Property": "CepivoIme",
                                            }
                                        }
                                    ],
                                    "Values": [[{"Literal": {"Value": "null"}}]],
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
                                    "Expression": {"SourceRef": {"Source": "c"}},
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
            "OrderBy": [
                {
                    "Direction": 1,
                    "Expression": {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "s"}},
                            "Property": "Starostni ​razred",
                        }
                    },
                }
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3, 4]}]},
            "DataReduction": {"DataVolume": 4, "Primary": {"Window": {"Count": 1000}}},
            "SuppressedJoinPredicates": [3, 4],
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_vaccinations_supplied_and_used_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "c1", "Entity": "Calendar", "Type": 0},
                {"Name": "c", "Entity": "eRCO_​​podatki", "Type": 0},
                {"Name": "n", "Entity": "xls_NIJZ_Odmerki", "Type": 0},
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "c1"}},
                        "Property": "Date",
                    },
                    "Name": "Calendar.Date",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "c"}},
                        "Property": "Kumulativno skupaj cepljenih",
                    },
                    "Name": "eRCO_podatki.Kumulativno skupaj cepljenih",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "n"}},
                        "Property": "Tekoča vsota za mero odmerki*​ v polju Date",
                    },
                    "Name": "NIJZ_Odmerki.Tekoča vsota za mero odmerki* v polju Date",
                },
            ],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 2,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c1"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-12-26T00:00:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                }
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0, 1, 2]}]},
            "DataReduction": {"DataVolume": 4, "Primary": {"BinnedLineSample": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_vaccination_by_region_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "e", "Entity": "eRCO_​​podatki", "Type": 0},
                {"Name": "s1", "Entity": "Sifrant_regija", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "s1"}},
                        "Property": "Regija",
                    },
                    "Name": "Sifrant_regija.Regija",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "e"}},
                        "Property": "Delež_regija_1",
                    },
                    "Name": "eRCO_podatki.Delež_regija",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "e"}},
                        "Property": "Delež_regija_precepljenost",
                    },
                    "Name": "eRCO_podatki_ed.Delež_regija_precepljenost",
                },
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "e"}},
                                "Property": "Odmerek – kopija",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(eRCO_​​podatki.Odmerek – kopija)",
                },
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
                    "Name": "Sum(eRCO_​​podatki.Precepljenost)",
                },
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "In": {
                                    "Expressions": [
                                        {
                                            "Column": {
                                                "Expression": {
                                                    "SourceRef": {"Source": "e"}
                                                },
                                                "Property": "CepivoIme",
                                            }
                                        }
                                    ],
                                    "Values": [[{"Literal": {"Value": "null"}}]],
                                }
                            }
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
                                                    "SourceRef": {"Source": "s1"}
                                                },
                                                "Property": "Regija",
                                            }
                                        }
                                    ],
                                    "Values": [
                                        [{"Literal": {"Value": "null"}}],
                                        [{"Literal": {"Value": "'Celotna Slovenija'"}}],
                                        [{"Literal": {"Value": "'TUJINA'"}}],
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
                                    "Expression": {"SourceRef": {"Source": "c"}},
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
            "OrderBy": [
                {
                    "Direction": 2,
                    "Expression": {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "e"}},
                            "Property": "Delež_regija_1",
                        }
                    },
                }
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3, 4]}]},
            "DataReduction": {"DataVolume": 4, "Primary": {"Window": {"Count": 1000}}},
            "SuppressedJoinPredicates": [3, 4],
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_vaccination_supplied_by_manufacturer_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "c", "Entity": "Calendar", "Type": 0},
                {"Name": "n", "Entity": "xls_NIJZ_Odmerki", "Type": 0},
                {"Name": "s", "Entity": "Sifrant_Cepivo", "Type": 0},
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "c"}},
                        "Property": "Date",
                    },
                    "Name": "Calendar.Date",
                },
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "n"}},
                                "Property": "odmerki*",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(NIJZ_Odmerki.odmerki*)",
                },
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "s"}},
                        "Property": "Cepivo_Ime",
                    },
                    "Name": "Sifrant_Cepivo.Cepivo_Ime",
                },
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Date",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "null"}},
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
                                "Aggregation": {
                                    "Expression": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "n"}
                                            },
                                            "Property": "odmerki*",
                                        }
                                    },
                                    "Function": 0,
                                }
                            },
                            "Right": {"Literal": {"Value": "-100000000000L"}},
                        }
                    },
                    "Target": [
                        {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "c"}},
                                "Property": "Date",
                            }
                        },
                        {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "s"}},
                                "Property": "Cepivo_Ime",
                            }
                        },
                    ],
                },
            ],
            "OrderBy": [
                {
                    "Direction": 1,
                    "Expression": {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "c"}},
                            "Property": "Date",
                        }
                    },
                }
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0, 1, 2], "Subtotal": 1}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Window": {"Count": 500}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_vaccination_supplied_by_manufacturer_cum_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "c1", "Entity": "Calendar", "Type": 0},
                {"Name": "n", "Entity": "xls_NIJZ_Odmerki", "Type": 0},
                {"Name": "s", "Entity": "Sifrant_Cepivo", "Type": 0},
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "c1"}},
                        "Property": "Date",
                    },
                    "Name": "Calendar.Date",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "n"}},
                        "Property": "Tekoča vsota za mero odmerki*​ v polju Date",
                    },
                    "Name": "NIJZ_Odmerki.Tekoča vsota za mero odmerki* v polju Date",
                },
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "s"}},
                        "Property": "Cepivo_Ime",
                    },
                    "Name": "Sifrant_Cepivo.Cepivo_Ime",
                },
            ],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 2,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c1"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-12-20T00:00:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
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
                                                    "SourceRef": {"Source": "n"}
                                                },
                                                "Property": "Vrsta cepiva",
                                            }
                                        }
                                    ],
                                    "Values": [
                                        [{"Literal": {"Value": "'Skupaj'"}}],
                                        [{"Literal": {"Value": "null"}}],
                                    ],
                                }
                            }
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0, 1]}]},
            "Secondary": {"Groupings": [{"Projections": [2]}]},
            "DataReduction": {
                "DataVolume": 4,
                "Intersection": {"BinnedLineSample": {}},
            },
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_vaccinations_by_municipalities_share_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "s", "Entity": "Sifrant_Obcina", "Type": 0},
                {"Name": "e", "Entity": "eRCO_podatki_občine", "Type": 0},
                {"Name": "x", "Entity": "xls_SURS_obcine", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "s"}},
                        "Property": "Obcina",
                    },
                    "Name": "Sifrant_Obcina.Obcina",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "e"}},
                        "Property": "Odst_CelotnaSLO_C",
                    },
                    "Name": "eRCO_podatki_občine.Odst_CelotnaSLO_C",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "e"}},
                        "Property": "Odst_CelotnaSLO_P",
                    },
                    "Name": "eRCO_podatki_občine.Odst_CelotnaSLO_P",
                },
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "x"}},
                                "Property": "PopulacijaObcina",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(xls_SURS_obcine.PopulacijaObcina)",
                },
            ],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 1,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
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
                }
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Window": {"Count": 500}}},
            "Version": 1,
        },
    }
}

# all manufacturers in one response
_vaccinations_by_manufacturer_used_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "c1", "Entity": "Calendar", "Type": 0},
                {"Name": "s", "Entity": "Sifrant_Cepivo", "Type": 0},
                {"Name": "c", "Entity": "eRCO_​​podatki", "Type": 0},
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "c1"}},
                        "Property": "Date",
                    },
                    "Name": "Calendar.Date",
                },
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "s"}},
                        "Property": "Cepivo_Ime",
                    },
                    "Name": "Sifrant_Cepivo.Cepivo_Ime",
                },
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "c"}},
                                "Property": "Weight",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(eRCO_podatki_ed.Weight)",
                },
            ],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 2,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c1"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-12-26T00:00:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
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
                                                    "SourceRef": {"Source": "s"}
                                                },
                                                "Property": "Cepivo_Ime",
                                            }
                                        }
                                    ],
                                    "Values": [[{"Literal": {"Value": "null"}}]],
                                }
                            }
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0, 2]}]},
            "Secondary": {"Groupings": [{"Projections": [1]}]},
            "DataReduction": {
                "DataVolume": 4,
                "Primary": {"Sample": {}},
                "Secondary": {"Top": {}},
            },
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

# REQ
_vaccinations_timestamp_req = _create_req(
    "vaccinations", [_vaccinations_timestamp_command]
)

_vaccinations_by_day_req = _create_req("vaccinations", [_vaccinations_by_day_command])

_vaccinations_by_age_req = _create_req("vaccinations", [_vaccinations_by_age_command])

_vaccines_supplied_and_used_req = _create_req(
    "vaccinations", [_vaccinations_supplied_and_used_command]
)

_vaccinations_by_region_req = _create_req(
    "vaccinations", [_vaccination_by_region_command], True
)

_vaccines_supplied_by_manufacturer_req = _create_req(
    "vaccinations", [_vaccination_supplied_by_manufacturer_command]
)

_vaccines_supplied_by_manufacturer_cum_req = _create_req(
    "vaccinations", [_vaccination_supplied_by_manufacturer_cum_command]
)

_vaccination_by_age_group_requests = _create_by_age_group_requests()

_vaccinations_by_region_by_day_requests = _create_by_region_by_day_requests()

_vaccinations_municipalities_share_req = _create_req(
    "vaccinations", [_vaccinations_by_municipalities_share_command], True
)

_vaccinations_age_group_by_region_on_day_requests = (
    _create_age_group_by_region_on_day_requests()
)

_vaccination_by_manufacturer_supplied_used_requests = (
    _create_vaccination_by_manufacturer_supplied_used_requests()
)


_vaccinations_gender_by_date_requests = _create_vaccination_gender_requests()

_vaccinations_by_manufacturer_used_request = (
    _create_vaccinations_by_manufacturer_requests()
)


# DATE RANGE AGE GROUP and REGION
def _create_vaccinations_data_range_request(
    end_date: datetime.datetime,
    start_date: datetime.datetime,
    property: Union[Region, AgeGroup, None],
):
    commands = _get_date_range_group_commands(start_date, end_date, group=property)

    group_req = _create_req("vaccinations", [commands.group])
    male1_req = _create_req("vaccinations", [commands.male1])
    male2_req = _create_req("vaccinations", [commands.male2])
    female1_req = _create_req("vaccinations", [commands.female1])
    female2_req = _create_req("vaccinations", [commands.female2])
    manufacturers_req = _create_req("vaccinations", [commands.manufacturers])

    requests = DateRangeCommands_Requests(
        group_req, male1_req, male2_req, female1_req, female2_req, manufacturers_req
    )
    return requests


# DATE RANGE -> AGE GROUP -> GENDER
def _create_in_range_age_group_gender_requests(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
):
    create_age_group_gender_command = _create_in_range_by_age_by_gender_command(
        start_date, end_date
    )
    age_group_obj = {}
    for age_group in AgeGroup:
        create_gender_command = create_age_group_gender_command(age_group)
        male_command = create_gender_command(Gender.MALE)
        female_command = create_gender_command(Gender.FEMALE)

        male_first = _create_req("vaccinations", [male_command["first"]])
        male_second = _create_req("vaccinations", [male_command["second"]])
        female_first = _create_req("vaccinations", [female_command["first"]])
        female_second = _create_req("vaccinations", [female_command["second"]])

        age_group_obj[age_group] = {
            "male_first": male_first,
            "male_second": male_second,
            "female_first": female_first,
            "female_second": female_second,
        }

    return age_group_obj


# DASHBOARD LAB
_lab_start_ts_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [{"Name": "c", "Entity": "Calendar", "Type": 0}],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "c"}},
                                "Property": "Date",
                            }
                        },
                        "Function": 3,
                    },
                    "Name": "Min(Calendar.Date)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 1,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                }
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_start_ts_req = _create_req("lab", [_lab_start_ts_command])


_lab_end_ts_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [{"Name": "c", "Entity": "Calendar", "Type": 0}],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "c"}},
                                "Property": "Date",
                            }
                        },
                        "Function": 3,
                    },
                    "Name": "Min(Calendar.Date)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 0,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Razlika_dan",
                                }
                            },
                            "Right": {"Literal": {"Value": "1L"}},
                        }
                    }
                },
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 1,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_end_ts_req = _create_req("lab", [_lab_end_ts_command])
_lab_end_ts_req_with_cache = _create_req("lab", [_lab_end_ts_command], cache_key=True)

_lab_PCR_tests_performed_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "d", "Entity": "Date_agg", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "d"}},
                                "Property": "vsi_pacienti_pcr_cnb",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(Date_agg.vsi_pacienti_pcr_cnb)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 0,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Razlika_dan",
                                }
                            },
                            "Right": {"Literal": {"Value": "1L"}},
                        }
                    }
                },
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 1,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_PCR_tests_performed_req = _create_req("lab", [_lab_PCR_tests_performed_command])
_lab_PCR_tests_performed_req_with_cache = _create_req(
    "lab", [_lab_PCR_tests_performed_command], cache_key=True
)

_lab_PCR_total_tests_performed_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "d", "Entity": "Date_agg", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "d"}},
                                "Property": "vsi_pacienti_pcr_cnb",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(Date_agg.vsi_pacienti_pcr_cnb)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Razlika_dan",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "0L"}},
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
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_PCR_total_tests_performed_req = _create_req(
    "lab", [_lab_PCR_total_tests_performed_command]
)

_lab_active_cases_estimated_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "a", "Entity": "All", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "a"}},
                        "Property": "Aktivni_primeri",
                    },
                    "Name": "All.Aktivni_primeri",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Razlika_dan",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "0L"}},
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
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_active_cases_estimated_req = _create_req(
    "lab", [_lab_active_cases_estimated_command]
)

_lab_confirmed_total_male_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "a", "Entity": "All", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "a"}},
                                "Property": "weight",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(All.weight)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Razlika_dan",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "0L"}},
                                }
                            }
                        }
                    }
                },
                {
                    "Condition": {
                        "In": {
                            "Expressions": [
                                {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "a"}},
                                        "Property": "spol",
                                    }
                                }
                            ],
                            "Values": [[{"Literal": {"Value": "'M'"}}]],
                        }
                    }
                },
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 1,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_confirmed_total_male_req = _create_req("lab", [_lab_confirmed_total_male_command])

_lab_total_vaccinated_first_dose_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "e", "Entity": "eRCO", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "e"}},
                                "Property": "Z 1 odmerkom",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(eRCO.Z 1 odmerkom)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Razlika_dan",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "0L"}},
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
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_total_vaccinated_first_dose_req = _create_req(
    "lab", [_lab_total_vaccinated_first_dose_command]
)

_lab_active_cases_100k_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "a", "Entity": "All", "Type": 0},
                {"Name": "r", "Entity": "Regija", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "a"}},
                        "Property": "Aktivni_100k",
                    },
                    "Name": "All.Aktivni_100k",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "In": {
                                    "Expressions": [
                                        {
                                            "Column": {
                                                "Expression": {
                                                    "SourceRef": {"Source": "r"}
                                                },
                                                "Property": "Regija",
                                            }
                                        }
                                    ],
                                    "Values": [
                                        [{"Literal": {"Value": "null"}}],
                                        [{"Literal": {"Value": "'Celotna Slovenija'"}}],
                                        [{"Literal": {"Value": "'TUJINA'"}}],
                                    ],
                                }
                            }
                        }
                    }
                },
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Razlika_dan",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "0L"}},
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
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}


_lab_active_cases_100k_req = _create_req("lab", [_lab_active_cases_100k_command])

_lab_cases_total_confirmed_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "a", "Entity": "All", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "a"}},
                                "Property": "weight",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(All.weight)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Razlika_dan",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "0L"}},
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
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_cases_total_confirmed_req = _create_req(
    "lab", [_lab_cases_total_confirmed_command]
)

_lab_HAT_total_tests_performed_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "d", "Entity": "Date_agg", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "d"}},
                                "Property": "vsi_pacienti_hagt",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(Date_agg.vsi_pacienti_hagt)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Razlika_dan",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "0L"}},
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
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_HAT_total_tests_performed_req = _create_req(
    "lab", [_lab_HAT_total_tests_performed_command]
)

_lab_cases_confirmed_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "a", "Entity": "All", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "a"}},
                                "Property": "weight",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(All.weight)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 0,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Razlika_dan",
                                }
                            },
                            "Right": {"Literal": {"Value": "1L"}},
                        }
                    }
                },
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 1,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_cases_confirmed_req = _create_req("lab", [_lab_cases_confirmed_command])
_lab_cases_confirmed_req_with_cache = _create_req(
    "lab", [_lab_cases_confirmed_command], cache_key=True
)

_lab_confirmed_total_female_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "a", "Entity": "All", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "a"}},
                                "Property": "weight",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(All.weight)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Razlika_dan",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "0L"}},
                                }
                            }
                        }
                    }
                },
                {
                    "Condition": {
                        "In": {
                            "Expressions": [
                                {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "a"}},
                                        "Property": "spol",
                                    }
                                }
                            ],
                            "Values": [[{"Literal": {"Value": "'F'"}}]],
                        }
                    }
                },
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 1,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_confirmed_total_female_req = _create_req(
    "lab", [_lab_confirmed_total_female_command]
)

_lab_total_vaccinated_fully_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "e", "Entity": "eRCO", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "e"}},
                                "Property": "Z vsemi odmerki",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(eRCO.Z vsemi odmerki)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Razlika_dan",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "0L"}},
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
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_total_vaccinated_fully_req = _create_req(
    "lab", [_lab_total_vaccinated_fully_command]
)

_lab_cases_avg_7Days_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "a", "Entity": "All", "Type": 0},
                {"Name": "r", "Entity": "Regija", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "a"}},
                        "Property": "Povprečje_7dni",
                    },
                    "Name": "All.Povprečje_7dni",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "In": {
                                    "Expressions": [
                                        {
                                            "Column": {
                                                "Expression": {
                                                    "SourceRef": {"Source": "r"}
                                                },
                                                "Property": "Regija",
                                            }
                                        }
                                    ],
                                    "Values": [
                                        [{"Literal": {"Value": "null"}}],
                                        [{"Literal": {"Value": "'Celotna Slovenija'"}}],
                                    ],
                                }
                            }
                        }
                    }
                },
                {
                    "Condition": {
                        "Not": {
                            "Expression": {
                                "Comparison": {
                                    "ComparisonKind": 0,
                                    "Left": {
                                        "Column": {
                                            "Expression": {
                                                "SourceRef": {"Source": "c"}
                                            },
                                            "Property": "Razlika_dan",
                                        }
                                    },
                                    "Right": {"Literal": {"Value": "0L"}},
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
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_cases_avg_7Days_req = _create_req("lab", [_lab_cases_avg_7Days_command])

_lab_HAT_tests_performed_command = {
    "SemanticQueryDataShapeCommand": {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "d", "Entity": "Date_agg", "Type": 0},
                {"Name": "c", "Entity": "Calendar", "Type": 0},
            ],
            "Select": [
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "d"}},
                                "Property": "vsi_pacienti_hagt",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(Date_agg.vsi_pacienti_hagt)",
                }
            ],
            "Where": [
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 0,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Razlika_dan",
                                }
                            },
                            "Right": {"Literal": {"Value": "1L"}},
                        }
                    }
                },
                {
                    "Condition": {
                        "Comparison": {
                            "ComparisonKind": 1,
                            "Left": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Source": "c"}},
                                    "Property": "Date",
                                }
                            },
                            "Right": {
                                "DateSpan": {
                                    "Expression": {
                                        "Literal": {
                                            "Value": "datetime'2020-03-03T01:01:00'"
                                        }
                                    },
                                    "TimeUnit": 5,
                                }
                            },
                        }
                    }
                },
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Top": {}}},
            "Version": 1,
        },
        "ExecutionMetricsKind": 1,
    }
}

_lab_HAT_tests_performed_req = _create_req("lab", [_lab_HAT_tests_performed_command])
_lab_HAT_tests_performed_req_with_cache = _create_req(
    "lab", [_lab_HAT_tests_performed_command], cache_key=True
)
