"""This module provides functions that are used by web framework to access
chemicals and pollution measurements data."""

import json
from typing import Callable, Generator, List, Union

from core.chemicals import get_chemical
from core.measurements import get_measurements, group_by_region, group_by_year


def color_generator():
    """Return a generator that yields distinctive colors."""

    return (
        c
        for c in [
            "#e6194B",
            "#3cb44b",
            "#ffe119",
            "#4363d8",
            "#f58231",
            "#42d4f4",
            "#f032e6",
            "#fabebe",
            "#469990",
            "#e6beff",
            "#9A6324",
            "#fffac8",
            "#800000",
            "#aaffc3",
            "#000075",
            "#a9a9a9",
        ]
    )


def get_datasets(
    chemical: str,
    regions: Union[None, str, List[str]] = None,
    years: Union[None, int, List[int]] = None,
    fun: Callable = len,
) -> Generator:
    """Return data in JSON that can be consumed by `charts.js` library."""

    if isinstance(years, int):
        years = [years]

    if isinstance(regions, str):
        regions = [regions]

    ms = get_measurements(chemical)

    colors = color_generator()

    for region_group in group_by_region(ms):
        region_name = region_group[0].region

        if not regions or region_name in regions:
            c = next(colors)
            dataset = {"label": region_name, "backgroundColor": c, "borderColor": c}
            data = {}
            for year_group in group_by_year(region_group):
                year = int(year_group[0].year.split("-")[0])

                if not years or year in years:
                    data[year] = fun(year_group)
                else:
                    continue

            dataset["data"] = [data.get(year, 0) for year in years]  # type: ignore
        else:
            continue

        yield dataset


def avg_value(group):
    return sum(m.value for m in group) / len(group)
