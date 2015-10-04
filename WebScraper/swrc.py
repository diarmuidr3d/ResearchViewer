from rdflib import Graph, Namespace, RDF, Literal, URIRef, XSD

__author__ = 'diarmuid'

class SWRC:

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

    def __init__(self, uri, file=None, author_uri=None):
        self.graph = Graph(identifier=uri)
        if file is not None:
            try:
                self.graph.load(file, format='n3')
            except FileNotFoundError:
                print("Could not load graph file, it doesn't exist")
        self.graph.namespace_manager.bind("swrc", self.swrc_ns)
        self.out_ns = Namespace(uri)
        self.graph.namespace_manager.bind("", self.out_ns)
        self.uri = uri
        self.author_uri = author_uri

    def resource_in_graph(self, resource):
        resource = URIRef(resource)
        if (resource, None, None) in self.graph:
            return True
        else:
            return False

    def add_paper(self, uri, type, name, authors=None):
        paper_rdf = self.graph.resource(uri)
        if type in self.paper_types:
            paper_type = self.paper_types[type]
        else:
            paper_type = self.swrc_ns.Publication
            print("Type '{0}' for paper {1} not in Journal Types".format(type, uri))
        paper_rdf.set(RDF.type, paper_type)
        title = Literal(name, lang="en")
        paper_rdf.set(self.swrc_ns.title, title)
        if authors is not None:
            authors_rdf = []
            for author in authors:
                authors_rdf.append(self.add_author(author, paper_rdf))
            self.add_co_authors(authors_rdf)
        return paper_rdf

    def add_co_authors(self, array_rdf):
        i = 0
        while i < len(array_rdf):
            j = 0
            while j < len(array_rdf):
                if j is not i and array_rdf[i] is not None and array_rdf[j] is not None:
                    array_rdf[i].add(self.swrc_ns.cooperatesWith, array_rdf[j])
                j += 1
            i += 1

    def add_author(self, author_details, author_of, co_authors=None):
        if author_details["first"] != 'et al.':
            author_rdf = self.graph.resource(author_details["uri"])
            author_rdf.set(RDF.type, self.swrc_ns.AcademicStaff)
            fname_rdf = Literal(author_details["first"], datatype=XSD.string)
            author_rdf.set(self.swrc_ns.firstName, fname_rdf)
            lname_rdf = Literal(author_details["last"], datatype=XSD.string)
            author_rdf.set(self.swrc_ns.lastName, lname_rdf)
            author_rdf.add(self.swrc_ns.publication, author_of)
            author_of.add(self.swrc_ns.contributor, author_rdf)
            if co_authors is not None:
                for co_author in co_authors:
                    author_rdf.add(self.swrc_ns.cooperateWith, co_author)
            return author_rdf
        return None

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
            print("Number of authors LD: {0} ".format(row))
