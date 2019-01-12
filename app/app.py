import json
import logging

from flask import Flask, render_template, request
from wtforms import Form
from wtforms.fields import SelectField

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

    chemical = SelectField("Látka", choices=all_chems)
    fun = SelectField("Agregační funkce", choices=functions)
    chart_type = SelectField("Zobrazení", choices=types)


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


class ChemicalParamForm(Form):
    all_chems = [
        (c.iri, c.name) for c in sorted(chemicals.get_all_chemicals().values())
    ]
    chemical = SelectField("Látka", choices=all_chems)

    years = list(zip(range(2004, 2013), range(2004, 2013)))

    year_from = SelectField("Od roku", choices=years)
    year_to = SelectField("Do roku", choices=years)


@app.route("/chemicals")
def chemical():
    chem_iri = request.args.get("chemical", "oxid-uhličitý-co2-")
    year_from = request.args.get("year_from", 2004)
    year_to = request.args.get("year_to", 2012)
    form = ChemicalParamForm(chemical=chem_iri, year_from=year_from, year_to=year_to)

    chemical = chemicals.get_chemical(chem_iri)
    chemical.retrieve_info()
    chemical.info = chemical.info.replace("\n", "<br>")

    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    chemical.formula = chemical.formula.translate(SUB)

    s_labels = [k for k in sorted(list(chemical.s_labels.keys()))]
    r_labels = [k for k in sorted(list(chemical.r_labels.keys()))]

    return render_template(
        "chemicals.html",
        form=form,
        chemical=chemical,
        s_labels=s_labels,
        r_labels=r_labels,
    )


@app.route("/api/by-regions/<iri>")
def region_data(iri):
    years = list(range(2004, 2013))

    try:
        fun = AGGREGATORS.get(request.args.get("fun", "len")).get("fun", len)

        datasets = list(web.region_datasets(iri, years=years, fun=fun))
    except:
        logger.exception("Failed to retrieve datasets.")
        datasets = []

    data = {"labels": years, "datasets": datasets}
    return json.dumps(data, ensure_ascii=False)


@app.route("/api/chemical/<iri>")
def chemical_data(iri):
    year_from = request.args.get("year_from", 2004)
    year_to = request.args.get("year_to", 2012)
    years = list(range(int(year_from), int(year_to) + 1))
    print(years)

    return json.dumps(web.chemical_datasets(iri, years))
