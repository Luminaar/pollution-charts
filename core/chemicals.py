import csv
from dataclasses import dataclass
from itertools import groupby
from typing import Dict, Optional

import os
import service


@dataclass(order=True)
class Chemical:

    iri: str
    name: str
    formula: str
    s_labels: dict
    r_labels: dict


def retrieve_chemical_data():
    query = """prefix sch:<http://schema.org/>
    prefix owl:<http://www.w3.org/2002/07/owl#>
    prefix skos:<http://www.w3.org/2004/02/skos/core#>
    prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix cenia:<http://linked.opendata.cz/ontology/domain/cenia.cz/>
    prefix irz: <http://linked.opendata.cz/ontology/domain/irz/>
    prefix core: <http://www.w3.org/2004/02/skos/core#>

    select ?mobject, ?name, ?formula, ?slabel, ?rlabel where
    {

    ?mobject     a  skos:Concept;
                 skos:inScheme  <http://linked.opendata.cz/ontology/domain/cenia.cz/chemicals/ConceptScheme>;
                 owl:sameAs ?chemical.
    OPTIONAL {?mobject core:prefLabel ?name.}
    OPTIONAL {?chemical  irz:vzorec ?formula.}
    OPTIONAL {?chemical irz:vetaR ?rlabel.}
    OPTIONAL {?chemical irz:vetaS ?slabel.}

    } order by ?mobject
    """

    results = service.retrieve(query)
    return [{k: v["value"] for k, v in result.items()} for result in results]


def read_csv(path):
    """Return contents of a CSV file as a dict."""

    full_path = os.path.join(os.path.dirname(__file__), path)

    with open(full_path) as f:
        reader = csv.DictReader(f)
        return [line for line in reader]


def transform_chemicals(data, s_labels, r_labels):
    for gr in groupby(data, lambda row: row["mobject"]):
        iri = gr[0]
        iri = iri.strip("/").split("/")[-1]
        group = list(gr[1])

        s_lbls: dict = {}
        r_lbls: dict = {}
        for item in group:
            formula = item.get("formula", None)
            name = item["name"]

            try:
                s_label = s_labels[item["slabel"]]
                s_lbls[s_label[0]] = s_label[1]
            except KeyError:
                pass

            try:
                r_label = r_labels[item["rlabel"]]
                r_lbls[r_label[0]] = r_label[1]
            except KeyError:
                pass

        yield Chemical(iri, name, formula, s_lbls, r_lbls)


def get_all_chemicals() -> Dict[str, Chemical]:
    """Load and return a dictionary of all chemicals."""

    r_labels = {
        r["iri"]: (r["notation"], r["label"]) for r in read_csv("data/r-vety.csv")
    }
    s_labels = {
        r["iri"]: (r["notation"], r["label"]) for r in read_csv("data/s-vety.csv")
    }

    data = retrieve_chemical_data()
    return {chem.iri: chem for chem in transform_chemicals(data, s_labels, r_labels)}
