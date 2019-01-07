import json
import operator
from dataclasses import dataclass
from itertools import groupby
from typing import Generator, List, Optional, Set

import service
from chemicals import Chemical


class Measurement:

    def __init__(
        self,
        iri: str,
        region: str,
        district: str,
        emission_type: str,  # TODO: Enum
        year: int,
        value: float,
        instrument: str,  # TODO: Enum
        chemical: Optional[Chemical] = None,
        waste_designation: Optional[str] = None,  # TODO: Enum
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

    def __repr__(self):
        return f"Chemical: {self.name}"




def get_measurements(chemical: Chemical) -> Generator:
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

    } order by ?district ?year
    """
        % chemical.iri
    )

    results = service.retrieve(query)

    with open("core/data/kraje-okresy.json") as k:
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

    return [list(group) for key, group in groupby(m, operator.attrgetter("region"))]


def group_by_year(m):
    """Group measurements by year and return a list of groups."""

    return [list(group) for key, group in groupby(m, operator.attrgetter("year"))]


if __name__ == "__main__":

    chem = Chemical("oxid-uhelnatý-co-", "", "", {}, {})

    ms = get_measurements(chem)

    group_by_region(ms)
