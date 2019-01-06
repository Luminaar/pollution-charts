import json
import operator
from dataclasses import dataclass
from itertools import groupby
from typing import Generator, List, Optional, Set

import service
from chemicals import Chemical


@dataclass(order=True)
class Measurment:
    iri: str
    region: str
    emission_type: str
    year: int
    value: float
    instrument: str
    chemical: Optional[Chemical]
    waste_designation: Optional[str]

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


def get_measurments(chemical: Chemical) -> Generator:
    """Return a list of measurments for given chemical."""

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
        measurment = Measurment(chemical=chemical, region=region, **kwargs)
        yield measurment


def get_regions(ms: List[Measurment]) -> Set:
    """Return a set of all regions from passed mesaurments."""

    return set(m.region for m in ms)


def group_by_region(m):
    """Group measurments by region and return a list of groups."""

    return [list(group) for key, group in groupby(m, operator.attrgetter("region"))]


def group_by_year(m):
    """Group measurments by year and return a list of groups."""

    return [list(group) for key, group in groupby(m, operator.attrgetter("year"))]


if __name__ == "__main__":

    chem = Chemical("oxid-uhelnatý-co-", "", "", {}, {})

    ms = get_measurments(chem)

    group_by_region(ms)
