"""This module provides functions that are used by web framework to access
chemicals and pollution measurements data."""

import json
import random
import string
from typing import Callable, Generator, List, Union

from core.chemicals import Chemical, get_chemical
from core.measurements import get_measurements, group_by_region, group_by_year


def color():
    return "#" + "".join(random.choices(string.hexdigits, k=6))


def get_datasets(
    chemical: Chemical,
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

    for region_group in group_by_region(ms):
        region_name = region_group[0].region

        if not regions or region_name in regions:
            c = color()
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


if __name__ == "__main__":
    years = list(range(2004, 2013))

    chemical_iri = "oxid-uhličitý-co2-"
    chemical = get_chemical(chemical_iri)
    if chemical:
        data = {
            "labels": years,
            "datasets": list(get_datasets(chemical, years=years, fun=avg_value)),
        }

        top = (
            """
        <!DOCTYPE html>

        <html>
          <head>
            <title>%s</title>
            <script type="text/javascript" charset="utf-8" src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.3/Chart.min.js"></script>
          </head>

          <body>

            <div>
              <canvas id="myChart"></canvas>
            </div>

            <script>
            var ctx = document.getElementById("myChart").getContext('2d');
            var myChart = new Chart(ctx, {
                type: 'bar',
                data:
        """
            % chemical_iri
        )

        bottom = """
                options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero:true
                            }
                        }]
                    }
                }
            });
            </script>
          </body>
        </html>
        """

        with open("index.html", "w") as f:
            f.write(top)
            json.dump(data, f, ensure_ascii=False)
            f.write(",")
            f.write(bottom)

        from http.server import HTTPServer, SimpleHTTPRequestHandler

        def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
            server_address = ("", 8000)
            httpd = server_class(server_address, handler_class)
            httpd.serve_forever()

        run()
