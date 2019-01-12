import json
import logging

from flask import Flask, render_template, request
from wtforms import Form, fields

from core import chemicals, web
from core.measurements import AGGREGATORS

logger = logging.getLogger(__name__)


app = Flask(__name__)


class ParamForm(Form):
    all_chems = [
        (c.iri, c.name) for c in sorted(chemicals.get_all_chemicals().values())
    ]
    functions = [(k, v.get("label")) for k, v in AGGREGATORS.items()]
    types = [("bar", "Podle regionů"), ("line", "Celkem")]

    chemical = fields.SelectField("Chemikálie", choices=all_chems)
    fun = fields.SelectField("Agregační funkce", choices=functions)
    chart_type = fields.SelectField("Zobrazení", choices=types)


@app.route("/regions")
def regions():
    chem_iri = request.args.get("chemical", "oxid-uhličitý-co2-")
    fun = request.args.get("fun", "mean")
    unit = AGGREGATORS.get(fun).get("unit", "t")
    label = AGGREGATORS.get(fun).get("label", "Průměrné emise")
    chart_type = request.args.get("chart_type", "bar")

    form = ParamForm(fun=fun, chemical=chem_iri, chart_type=chart_type)

    chemical = chemicals.get_chemical(chem_iri)

    return render_template(
        "regions.html", fun=fun, chemical=chemical, form=form, unit=unit, label=label
    )


@app.route("/api/by-regions/<iri>")
def datasets(iri):
    years = list(range(2004, 2013))

    try:
        fun = AGGREGATORS.get(request.args.get("fun", "len")).get("fun", len)

        datasets = list(web.region_datasets(iri, years=years, fun=fun))
    except:
        logger.exception("Failed to retrieve datasets.")
        datasets = []

    data = {"labels": years, "datasets": datasets}
    return json.dumps(data, ensure_ascii=False)
