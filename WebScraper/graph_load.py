from rdflib import Graph, Literal, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON

__author__ = 'diarmuid'


def rdflib_get(endpoint):
    """
    Gets an RDFlib graph from a SPARQL Endpoint
    :param endpoint: the URL of the endpoint
    :return: an RDFLib graph containing all data from the endpoint
    """
    print("Getting graph from ", endpoint)
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    sparql.setQuery('''
        SELECT ?s ?p ?o
        WHERE { ?s ?p ?o }
    ''')
    results = sparql.query().convert()
    graph = Graph(identifier='http://researchrepository.ucd.ie/')
    for spo in results['results']['bindings']:
        s = graph.resource(spo['s']['value'])
        p = URIRef(spo['p']['value'])
        oval = spo['o']
        if oval['type'] == 'literal':
            if 'xml:lang' in oval:
                o = Literal(oval['value'], lang=oval['xml:lang'])
            else:
                o = Literal(oval['value'])
        else:
            o = graph.resource(oval['value'])
        s.add(p, o)
    print("Got graph from endpoint")
    return graph


def rdflib_put(graph, endpoint):
    """
    Updates a SPARQL Endpoint with all data from an RDFlib graph
    :param graph: The RDFLib graph to get the data from
    :param endpoint: The URL of the SPARQL Update Enpoint to which the data will be sent
    """
    print("Putting ", graph, " to ", endpoint)
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    triples = ""
    for (subject, predicate, object) in graph:
        triples += " <{0}> <{1}> ".format(subject, predicate)
        if type(object) is Literal:
            triples += '"{0}"'.format(object)
            if object.language is not None:
                triples += '@{0}'.format(object.language)
            elif object.datatype is not None:
                triples += '^^<{0}>'.format(object.datatype)
        else:
            triples += "<{0}>".format(object)
        triples += " . "
    query = 'DELETE { ' + triples + ' } INSERT { ' + triples + ' } WHERE {} '
    print("Setting update")
    sparql.setQuery(query)
    sparql.method = 'POST'
    sparql.query()
    print("Updated")
