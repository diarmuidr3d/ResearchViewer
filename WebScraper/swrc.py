import os
from rdflib import Graph, Namespace, RDF, Literal, XSD

__author__ = 'diarmuid'

class SWRC:

    dbo_ns = Namespace("http://dbpedia.org/ontology/")
    swrc_ns = Namespace("http://swrc.ontoware.org/ontology#")
    paper_types = {
        "Journal Article": swrc_ns.Article,
        "Book Chapter": swrc_ns.InBook,
        "Technical Report": swrc_ns.TechnicalReport,
        "Doctoral Thesis": swrc_ns.PhDThesis
    }

    def __init__(self, uri):
        self.graph = Graph(identifier=uri)
        self.graph.namespace_manager.bind("swrc", self.swrc_ns)
        self.out_ns = Namespace(uri)
        self.graph.namespace_manager.bind("rrucd", self.out_ns)

    def add_paper(self, uri, type):
        paper_rdf = self.graph.resource(uri)
        if type in self.paper_types:
            paper_type = self.paper_types[type]
        else:
            paper_type = self.swrc_ns.Publication
            print("Type '{0}' for paper {1} not in Journal Types".format(type, uri))
        paper_rdf.set(RDF.type, paper_type)
        return paper_rdf

    def add_author(self, uri, name, author_of):
        author_rdf = self.graph.resource(uri)
        author_rdf.set(RDF.type, self.swrc_ns.AcademicStaff)
        author_rdf.add(self.swrc_ns.publication, author_of)
        # name_rdf = Literal(name, lang="en", datatype=XSD.string)
        name_rdf = Literal(name, lang="en")
        author_rdf.set(self.dbo_ns.birthName, name_rdf)
        author_of.add(self.swrc_ns.author, author_rdf)

    def output(self, filename):
        output_filename = os.path.join('output', filename)
        output_file = open(output_filename, "wb")
        self.graph.serialize(destination=output_file, format='n3', auto_compact=True)