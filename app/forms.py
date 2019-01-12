from wtforms import Form
from wtforms.fields import SelectField

from core import chemicals
from core.measurements import AGGREGATORS


class ParamForm(Form):
    all_chems = [
        (c.iri, c.name) for c in sorted(chemicals.get_all_chemicals().values())
    ]
    functions = [(k, v.get("label")) for k, v in AGGREGATORS.items()]
    types = [("bar", "Podle regionů"), ("line", "Celkem")]

    chemical = SelectField("Látka", choices=all_chems)
    fun = SelectField("Agregační funkce", choices=functions)
    chart_type = SelectField("Zobrazení", choices=types)


class ChemicalParamForm(Form):
    all_chems = [
        (c.iri, c.name) for c in sorted(chemicals.get_all_chemicals().values())
    ]
    chemical = SelectField("Látka", choices=all_chems)

    years = list(zip(range(2004, 2013), range(2004, 2013)))

    year_from = SelectField("Od roku", choices=years)
    year_to = SelectField("Do roku", choices=years)
