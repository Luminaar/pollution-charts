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

    chemical = fields.SelectField("Chemikálie", choices=all_chems)
    fun = fields.SelectField("Agregační funkce", choices=functions)


@app.route("/")
def index():
    chem_iri = request.args.get("chemical", "chemical=oxid-uhličitý-co2-")
    fun = request.args.get("fun", "mean")
    unit = AGGREGATORS.get(fun).get("unit", "t")
    label = AGGREGATORS.get(fun).get("label", "Průměrné emise")

    form = ParamForm(fun=fun, chemical=chem_iri)

    chemical = chemicals.get_chemical(chem_iri)

    return render_template(
        "index.html", fun=fun, chemical=chemical, form=form, unit=unit, label=label
    )


@app.route("/api/get/datasets/<iri>")
def datasets(iri):
    years = list(range(2004, 2013))

    try:
        fun = AGGREGATORS.get(request.args.get("fun", "len")).get("fun", len)

        datasets = list(web.get_datasets(iri, years=years, fun=fun))
    except:
        logger.exception("Failed to retrieve datasets.")
        datasets = []

    data = {"labels": years, "datasets": datasets}
    return json.dumps(data, ensure_ascii=False)
