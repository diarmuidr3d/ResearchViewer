from SPARQLWrapper import SPARQLWrapper, JSON

__author__ = 'diarmuid'


def get_co_authors_csi(endpoint):
    """
    Runs a sparql query on the endpoint to retreive all authors affiliated with computer science in UCD
    :param endpoint: the sparql endpoint on which to run the query
    :return: the bindings from running the sparql query
    """
    sparql = SPARQLWrapper(endpoint, returnFormat=JSON)
    sparql.setQuery("""PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT (CONCAT(CONCAT(?lnameA, ", "), ?fnameA) as ?author) (CONCAT(CONCAT(?lnameB, ", "), ?fnameB) as ?coauthor) (COUNT (?paper) AS ?count)
    WHERE {
        {?authorA rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/849> }
        UNION
        { ?authorA rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/855> }
        UNION
        { ?authorA rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/2207> }
        UNION
        { ?authorA rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/2494> }
        UNION
        { ?authorA rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/5476> } .
        {?authorB rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/849> }
        UNION
        { ?authorB rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/855> }
        UNION
        { ?authorB rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/2207> }
        UNION
        { ?authorB rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/2494> }
        UNION
        { ?authorB rucd:affiliation <http://researchrepository.ucd.ie/handle/10197/5476> } .
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
    """
    Runs a sparql query on the endpoint to retreive all co-authors
    :param endpoint: the sparql endpoint on which to run the query
    :return: the bindings from running the sparql query
    """
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


def get_author_department(endpoint):
    """
    Gets the affiliations of each author
    :param endpoint: the sparql endpoint on which to run the query
    :return: the bindings from running the sparql query
    """
    sparql = SPARQLWrapper(endpoint, returnFormat=JSON)
    sparql.setQuery("""PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT (CONCAT(CONCAT(?lname, ", "), ?fname) as ?name) ?department
    WHERE {
        ?author rucd:affiliation ?affil .
        ?affil rdfs:label ?department .
        ?author rucd:firstName ?fname .
        ?author rucd:lastName ?lname .
    }
    """)
    return {row["name"]["value"]: row["department"]["value"] for row in sparql.queryAndConvert()['results']['bindings']}


def get_department_collaboration(endpoint):
    """
    Runs a sparql query on the endpoint to retreive all department collaboration
    :param endpoint: the sparql endpoint on which to run the query
    :return: the bindings from running the sparql query
    """
    sparql = SPARQLWrapper(endpoint, returnFormat=JSON)
    sparql.setQuery("""PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?author ?coauthor (COUNT (?paper) AS ?count)
    WHERE {
        ?authorA rucd:cooperatesWith ?authorB .
        ?authorA rucd:publication ?paper .
        ?authorB rucd:publication ?paper .
        ?authorA rucd:affiliation ?deptA .
        ?authorB rucd:affiliation ?deptB .
        FILTER(?deptA != ?deptB) .
        ?deptA rdfs:label ?author .
        ?deptB rdfs:label ?coauthor .
    }
    GROUP BY ?author ?coauthor ?fnameB
    """)
    return sparql.queryAndConvert()['results']['bindings']