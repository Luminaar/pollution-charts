import json
import logging
import sys

from flask import Flask, render_template, request

from core import chemicals, web
from core.measurements import AGGREGATORS

print(sys.argv[0])

logger = logging.getLogger(__name__)


app = Flask(__name__)


@app.route("/")
def index():
    chem_iri = request.args.get("chemical", "naftalen")
    fun = request.args.get("fun", "len")

    chemical = chemicals.get_chemical(chem_iri)

    return render_template("index.html", fun=fun, chemical=chemical)


@app.route("/api/get/datasets/<iri>")
def datasets(iri):
    years = list(range(2004, 2013))

    try:
        fun = AGGREGATORS.get(request.args.get("fun", "len"), len)

        datasets = list(web.get_datasets(iri, years=years, fun=fun))
    except:
        logger.exception("Failed to retrieve datasets.")
        datasets = []

    data = {"labels": years, "datasets": datasets}
    return json.dumps(data, ensure_ascii=False)
