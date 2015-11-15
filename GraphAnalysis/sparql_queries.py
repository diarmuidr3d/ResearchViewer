from SPARQLWrapper import SPARQLWrapper, JSON

__author__ = 'diarmuid'


def get_co_authors_csi(endpoint):
    sparql = SPARQLWrapper(endpoint, returnFormat=JSON)
    sparql.setQuery("""PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT (CONCAT(CONCAT(?lnameA, ", "), ?fnameA) as ?author) (CONCAT(CONCAT(?lnameB, ", "), ?fnameB) as ?coauthor) (COUNT (?paper) AS ?count)
    WHERE {
        ?authorA rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/849> .
        ?authorB rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/849> .
        ?authorA rucd:cooperatesWith ?authorB .
        ?authorA rucd:publication ?paper .
        ?authorB rucd:publication ?paper .
        ?authorA rucd:firstName ?fnameA .
        ?authorA rucd:lastName ?lnameA .
        ?authorB rucd:firstName ?fnameB .
        ?authorB rucd:lastName ?lnameB .
    }
    GROUP BY ?author ?coauthor ?lnameA ?fnameA ?lnameB ?fnameB
    """)
    return sparql.queryAndConvert()['results']['bindings']



def get_co_authors(endpoint):
    sparql = SPARQLWrapper(endpoint, returnFormat=JSON)
    sparql.setQuery("""PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT (CONCAT(CONCAT(?lnameA, ", "), ?fnameA) as ?author) (CONCAT(CONCAT(?lnameB, ", "), ?fnameB) as ?coauthor) (COUNT (?paper) AS ?count)
    WHERE {
        ?authorA rucd:cooperatesWith ?authorB .
        ?authorA rucd:publication ?paper .
        ?authorB rucd:publication ?paper .
        ?authorA rucd:firstName ?fnameA .
        ?authorA rucd:lastName ?lnameA .
        ?authorB rucd:firstName ?fnameB .
        ?authorB rucd:lastName ?lnameB .
    }
    GROUP BY ?author ?coauthor ?lnameA ?fnameA ?lnameB ?fnameB
    """)
    return sparql.queryAndConvert()['results']['bindings']