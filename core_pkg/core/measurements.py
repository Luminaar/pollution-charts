import json
import operator
import os
import statistics
from itertools import groupby
from typing import Generator, List, Optional, Set

from core import service
from core.chemicals import Chemical


class Measurement:
    def __init__(
        self,
        iri: str,
        region: str,
        district: str,
        emission_type: str,
        year: int,
        value: float,
        instrument: str,
        chemical: Optional[str] = None,
        waste_designation: Optional[str] = None,
    ):
        self.iri = iri
        self.region = region
        self.district = district.strip()
        self.emission_type = emission_type
        self.year = year
        self.value = float(value)
        self.instrument = instrument
        self.chemical = chemical
        self.waste_designation = waste_designation


def get_measurements(chemical: str) -> Generator:
    """Return a list of measurements for given chemical."""

    query = (
        """
    prefix sch:<http://schema.org/>
    prefix owl:<http://www.w3.org/2002/07/owl#>
    prefix skos:<http://www.w3.org/2004/02/skos/core#>
    prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix cenia:<http://linked.opendata.cz/ontology/domain/cenia.cz/>

    select distinct ?iri, ?emission_type, ?district, ?year, ?value, ?waste_designation, ?instrument where
    {

    ?iri          sch:object <http://linked.opendata.cz/ontology/domain/cenia.cz/chemicals/%s>;
                  sch:additionalType ?emission_type;
                  sch:startTime ?year;
                  rdf:value ?value;
                  sch:instrument ?instrument;
                  sch:location ?location.

    ?place        owl:sameAs ?location.
    ?place        sch:address ?addr.
    ?addr         sch:addressRegion ?district.
    OPTIONAL      {?iri cenia:urceniOdpadu ?waste_designation}.

    } order by ?region ?year
    """
        % chemical
    )

    results = service.retrieve(query)

    with open(os.path.join(os.path.dirname(__file__), "data/kraje-okresy.json")) as k:
        districts = json.load(k)

    for result in results:
        kwargs = {k: i["value"] for k, i in result.items()}
        if not kwargs["district"]:
            continue
        region = districts[kwargs["district"].strip()]
        measurement = Measurement(chemical=chemical, region=region, **kwargs)
        yield measurement


def get_regions(ms: List[Measurement]) -> Set:
    """Return a set of all regions from passed mesaurments."""

    return set(m.region for m in ms)


def group_by_region(m):
    """Group measurements by region and return a list of groups."""

    m = sorted(m, key=operator.attrgetter("region"))

    return [list(group) for key, group in groupby(m, operator.attrgetter("region"))]


def group_by_year(m):
    """Group measurements by year and return a list of groups."""

    return [list(group) for key, group in groupby(m, operator.attrgetter("year"))]


# Aggregation functions
def total(group):
    """Return total of all measurement values from a group. Unit is tons per
    year."""

    return sum(round(m.value / 1000, 3) for m in group)


def mean(group):
    """Return mean of all measurement values from a group. Unit is tons per
    year."""

    group = list(group)
    count = len(group)

    return round((total(group) / count) / 1000, 3)


def median(group):
    """Return median of all measurement values from a group. Unit is tons per
    year."""

    values = sorted([m.value for m in group])

    return round((statistics.median(values)) / 1000, 3)


AGGREGATORS = {
    "len": {"fun": len, "unit": "Hlášení", "label": "Počet hlášení"},
    "total": {"fun": total, "unit": "t", "label": "Celkové emise"},
    "mean": {"fun": mean, "unit": "t", "label": "Průměrné emise"},
    "median": {"fun": median, "unit": "t", "label": "Medián emisí"},
}


if __name__ == "__main__":

    chem = Chemical("oxid-uhelnatý-co-", "", "", {}, {})

    ms = get_measurements(chem)

    group_by_region(ms)
