from rdflib import Graph, Literal, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON

__author__ = 'diarmuid'

# class RDFLib_SPARQL:
def get():
    sparql = SPARQLWrapper('http://localhost:3030/rrucd/query')
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
    graph.serialize(destination=output_file, format='n3', auto_compact=True)

# def put():
#     TODO

get()