from SPARQLWrapper import JSON, SPARQLWrapper


def retrieve(query):
    service = SPARQLWrapper("https://linked.opendata.cz/sparql", "utf-8", "GET")
    service.setReturnFormat(JSON)
    service.setQuery(query)
    return service.query().convert()["results"]["bindings"]
