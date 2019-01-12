"""This module provides functions that are used by web framework to access
chemicals and pollution measurements data."""

from typing import Callable, Generator, List, Union

from core.measurements import (get_measurements, group_by_emission,
                               group_by_region, group_by_year)


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
            "#800000",
            "#aaffc3",
            "#000075",
            "#a9a9a9",
            "#800000",
        ]
    )


def region_datasets(
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
                year = year_group[0].year

                if not years or year in years:
                    data[year] = fun(year_group)
                else:
                    continue

            dataset["data"] = [data.get(year, 0) for year in years]  # type: ignore
        else:
            continue

        yield dataset


def chemical_datasets(chemical: str, years: List[int]):
    """Return data in JSON that can be used by `charts.js` library."""

    ms = filter(lambda m: m.year in years, get_measurements(chemical))

    by_em_type = {}
    for emission_group in group_by_emission(ms):
        emission_group = list(filter(lambda m: m.year in years, emission_group))
        emission_type = emission_group[0].emission_type

        by_em_type[emission_type] = {
            "count": len(emission_group),
            "total": sum(m.value for m in emission_group),
        }

    colors = color_generator()

    labels = []
    data = []
    bgColors = []
    for k, v in by_em_type.items():
        labels.append(k)
        data.append(v["count"])
        bgColors.append(next(colors))

    return {"datasets": [{"data": data, "backgroundColor": bgColors}], "labels": labels}


def avg_value(group):
    return sum(m.value for m in group) / len(group)


if __name__ == "__main__":
    chemical = "oktylfenoly-a-oktylfenol-ethoxyláty"
    years = list(range(2004, 2013))
    chemical_datasets(chemical, years)
