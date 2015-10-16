from rdflib import Graph, Literal, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON

__author__ = 'diarmuid'

def rdflib_get(endpoint):
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
    output_file = open('tester.n3','wb')
    for (subject, predicate, object) in graph:
        print("{0}, {1}, {2}".format(subject,predicate,object))
    graph.serialize(destination=output_file, format='n3', auto_compact=True)
    return graph


def rdflib_put(graph, endpoint):
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    triples = ""
    for (subject, predicate, object) in graph:
        triples += " <{0}> <{1}> ".format(subject,predicate)
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
    print(query)
    sparql.setQuery(query)
    sparql.method = 'POST'
    sparql.query()