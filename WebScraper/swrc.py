from rdflib import Graph, Namespace, RDF, Literal, URIRef

__author__ = 'diarmuid'

class SWRC:

    dbo_ns = Namespace("http://dbpedia.org/ontology/")
    swrc_ns = Namespace("http://swrc.ontoware.org/ontology#")
    paper_types = {
        "Journal Article": swrc_ns.Article,
        "Book Chapter": swrc_ns.InBook,
        "Technical Report": swrc_ns.TechnicalReport,
        "Doctoral Thesis": swrc_ns.PhDThesis,
        "Conference Publication": swrc_ns.InProceedings,
        "Working Paper": swrc_ns.TechnicalReport,
        "Book": swrc_ns.Book,
        "Contribution to Newspaper/Magazine": swrc_ns.Magazine
    }
    authors=[]

    def __init__(self, uri, file=None):
        self.graph = Graph(identifier=uri)
        if file is not None:
            self.graph.load(file, format='n3')
        self.graph.namespace_manager.bind("swrc", self.swrc_ns)
        self.out_ns = Namespace(uri)
        self.graph.namespace_manager.bind("rrucd", self.out_ns)

    def resource_in_graph(self, resource):
        resource = URIRef(resource)
        if (resource, None, None) in self.graph:
            return True
        else:
            return False

    def add_paper(self, uri, type, name):
        paper_rdf = self.graph.resource(uri)
        if type in self.paper_types:
            paper_type = self.paper_types[type]
        else:
            paper_type = self.swrc_ns.Publication
            print("Type '{0}' for paper {1} not in Journal Types".format(type, uri))
        paper_rdf.set(RDF.type, paper_type)
        title = Literal(name, lang="en")
        paper_rdf.set(self.swrc_ns.title, title)
        return paper_rdf

    def add_author(self, uri, name, author_of):
        if name != 'et al.':
            author_rdf = self.graph.resource(uri)
            if name not in self.authors:
                author_rdf.set(RDF.type, self.swrc_ns.AcademicStaff)
                # name_rdf = Literal(name, lang="en", datatype=XSD.string)
                name_rdf = Literal(name, lang="en")
                author_rdf.set(self.dbo_ns.birthName, name_rdf)
                self.authors.append(name)
            author_rdf.add(self.swrc_ns.publication, author_of)
            author_of.add(self.swrc_ns.contributor, author_rdf)

    def output(self, filename):
        output_file = open(filename, "wb")
        self.graph.serialize(destination=output_file, format='n3', auto_compact=True)

    def get_authors(self):
        result = self.graph.query(
            """
            PREFIX swrc: <http://swrc.ontoware.org/ontology#>
            SELECT (COUNT(DISTINCT ?a) AS ?count)
            WHERE { ?a rdf:type swrc:AcademicStaff }
            """
        )
        for row in result:
            print("Number of authors LD: {0}, #Array: ".format(row, len(self.authors)))
        authors = sorted(self.authors, key=str.lower)
        print(authors)
