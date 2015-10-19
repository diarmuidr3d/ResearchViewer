from rdflib import Graph, Namespace, RDF, Literal, URIRef, XSD, RDFS
from graph_load import rdflib_put

__author__ = 'diarmuid'

class SWRC:

    ucd_ns = Namespace("http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#")
    paper_types = {
        "Journal Article": ucd_ns.Article,
        "Book Chapter": ucd_ns.InBook,
        "Technical Report": ucd_ns.TechnicalReport,
        "Doctoral Thesis": ucd_ns.PhDThesis,
        "Conference Publication": ucd_ns.InProceedings,
        "Working Paper": ucd_ns.TechnicalReport,
        "Book": ucd_ns.Book,
        "Contribution to Newspaper/Magazine": ucd_ns.Magazine,
        "Review": ucd_ns.Misc,
        "Government Publication": ucd_ns.Publication,
        "Other": ucd_ns.Misc,
        "Master Thesis": ucd_ns.MasterThesis
    }

    def __init__(self, uri, file=None, author_uri=None):
        self.graph = Graph(identifier=uri)
        # I would like to use the below version but it uses an older version of URLGrabber
        # self.graph = rdflib.ConjunctiveGraph('SPARQLUpdateStore')
        # self.graph.open("http://localhost:3030/rrucd/sparql",
        #        "http://localhost:3030/rrucd/update")
        if file is not None:
            try:
                self.graph.load(file, format='n3')
            except FileNotFoundError:
                print("Could not load graph file, it doesn't exist")
        self.graph.namespace_manager.bind("rucd", self.ucd_ns)
        self.out_ns = Namespace(uri)
        self.graph.namespace_manager.bind("data", self.out_ns)
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
            paper_type = self.ucd_ns.Misc
            print("Type '{0}' for paper {1} not in Journal Types".format(type, uri))
        paper_rdf.set(RDF.type, paper_type)
        title = Literal(name, lang="en")
        paper_rdf.set(self.ucd_ns.title, title)
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
                    array_rdf[i].add(self.ucd_ns.cooperatesWith, array_rdf[j])
                j += 1
            i += 1

    def add_author(self, author_details, author_of, co_authors=None):
        if author_details["first"] != 'et al.':
            author_rdf = self.graph.resource(author_details["uri"])
            author_rdf.set(RDF.type, self.ucd_ns.AcademicStaff)
            fname_rdf = Literal(author_details["first"], datatype=XSD.string)
            author_rdf.set(self.ucd_ns.firstName, fname_rdf)
            lname_rdf = Literal(author_details["last"], datatype=XSD.string)
            author_rdf.set(self.ucd_ns.lastName, lname_rdf)
            author_rdf.add(self.ucd_ns.publication, author_of)
            author_of.add(self.ucd_ns.contributor, author_rdf)
            if co_authors is not None:
                for co_author in co_authors:
                    author_rdf.add(self.ucd_ns.cooperateWith, co_author)
            return author_rdf
        return None

    def add_affiliation(self, author_rdf=None, author_uri=None, organisation_rdf=None, organisation_uri=None):
        def add_org(author):
            if organisation_rdf is not None:
                author.add(self.ucd_ns.affiliation, organisation_rdf)
            elif organisation_uri is not None:
                org = self.graph.resource(organisation_uri)
                author.add(self.ucd_ns.affiliation, org)
        if author_rdf is not None:
            add_org(author_rdf)
        elif author_uri is not None:
            auth = self.graph.resource(author_uri)
            add_org(auth)

    def add_university(self, uri, name):
        university = self.graph.resource(uri)
        university.set(RDF.type, self.ucd_ns.University)
        name = Literal(name, datatype=XSD.string)
        university.set(RDFS.label, name)
        return university

    def add_college(self, uri, name, university_rdf=None):
        college = self.graph.resource(uri)
        college.set(RDF.type, self.ucd_ns.College)
        name = Literal(name, datatype=XSD.string)
        college.set(RDFS.label, name)
        if university_rdf is not None:
            university_rdf.add(self.ucd_ns.hasParts, college)
        return college

    def add_school(self, uri, name, college_rdf=None):
        school = self.graph.resource(uri)
        school.set(RDF.type, self.ucd_ns.School)
        name = Literal(name, datatype=XSD.string)
        school.set(RDFS.label, name)
        if college_rdf is not None:
            college_rdf.add(self.ucd_ns.hasParts, school)
        return school

    def add_institute(self, uri, name, department_rdf=None):
        institute = self.graph.resource(uri)
        institute.set(RDF.type, self.ucd_ns.Institute)
        name = Literal(name, datatype=XSD.string)
        institute.set(RDFS.label, name)
        if department_rdf is not None:
            department_rdf.add(self.ucd_ns.hasParts, institute)
        return institute

    def output(self, filename=None, endpoint=None):
        if filename != None:
            output_file = open(filename, "wb")
            self.graph.serialize(destination=output_file, format='n3', auto_compact=True)
        if endpoint != None:
            rdflib_put(self.graph, endpoint)

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
