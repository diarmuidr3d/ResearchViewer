from rdflib import Graph, Namespace, RDF, Literal, URIRef, XSD, RDFS
from WebScraper.graph_load import rdflib_put

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
        """
        Checks if a particular resource is contained in the Graph already
        :param resource: the URI of the resource to be checked
        :return: True if the object is contained in it, False otherwise
        """
        resource = URIRef(resource)
        if (resource, None, None) in self.graph:
            return True
        else:
            return False

    def get_authors(self):
        author_array = []
        for author in self.graph.subjects(RDF.type, self.ucd_ns.AcademicStaff):
            fname = self.graph.value(subject=author, predicate=self.ucd_ns.firstName).value
            lname = self.graph.value(subject=author, predicate=self.ucd_ns.lastName).value
            author_array.append({"uri":author, "firstName": fname, "lastName": lname})
        return author_array

    def add_paper(self, uri, type, name, authors=None):
        """
        Adds a paper to the graph
        :param uri: The uri to be given to the paper
        :param type: The type of the paper from @paper_type
        :param name: The name of the paper
        :param authors: The authors of the paper
        :return: The RDF resource for the paper in the graph
        """
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
                if author is not None:
                    authors_rdf.append(self.add_author(author, paper_rdf))
            self.add_co_authors(authors_rdf)
        return paper_rdf

    def add_co_authors(self, array_rdf):
        """
        Takes a list of author Resources and creates cooperatesWith links between all of them
        :param array_rdf: The list of author Resources
        """
        i = 0
        while i < len(array_rdf):
            j = 0
            while j < len(array_rdf):
                if j is not i and array_rdf[i] is not None and array_rdf[j] is not None:
                    array_rdf[i].add(self.ucd_ns.cooperatesWith, array_rdf[j])
                j += 1
            i += 1

    def add_author(self, author_details, author_of, co_authors=None):
        """
        Adds an author to the graph
        :param author_details: a dictionary of the author details containing values for uri, first and last names
        :param author_of: A paper of which the author contributed to
        :param co_authors: The other authors that this author worked with
        :return: The author's Resource
        """
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
        """
        Adds an affiliation for an author to an organisation (eg: Institute)
        One of author_rdf or author_uri must be provided
        One of organisation_rdf or organisation_uri must be provided
        :param author_rdf: A Resource for the author
        :param author_uri: the Author's URI
        :param organisation_rdf: A Resource for the organisation
        :param organisation_uri: the Organisation's URI
        """

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
        """
        Adds a University to the graph
        :param uri: The unique URI for the university
        :param name: the name of the university
        :return: The Resource for the University
        """
        university = self.graph.resource(uri)
        university.set(RDF.type, self.ucd_ns.University)
        name = Literal(name, datatype=XSD.string)
        university.set(RDFS.label, name)
        return university

    def add_college(self, uri, name, university_rdf=None):
        """
        Adds a college
        :param uri: The URI for the college
        :param name: The name of the college
        :param university_rdf: The University Resource of which the college is part
        :return: The Resource for the college
        """
        college = self.graph.resource(uri)
        college.set(RDF.type, self.ucd_ns.College)
        name = Literal(name, datatype=XSD.string)
        college.set(RDFS.label, name)
        if university_rdf is not None:
            university_rdf.add(self.ucd_ns.hasParts, college)
        return college

    def add_school(self, uri, name, college_rdf=None):
        """
        Adds a school to the graph
        :param uri: The URI for the school
        :param name: The name of the school
        :param college_rdf: A College Resource of which the school is part
        :return: A resource for the school
        """
        school = self.graph.resource(uri)
        school.set(RDF.type, self.ucd_ns.School)
        name = Literal(name, datatype=XSD.string)
        school.set(RDFS.label, name)
        if college_rdf is not None:
            college_rdf.add(self.ucd_ns.hasParts, school)
        return school

    def add_institute(self, uri, name, department_rdf=None):
        """
        Adds a institute to the graph
        :param uri: The URI for the institute
        :param name: The name of the institute
        :param college_rdf: An organisation Resource of which the institute is part
        :return: A resource for the institute
        """
        institute = self.graph.resource(uri)
        institute.set(RDF.type, self.ucd_ns.Institute)
        name = Literal(name, datatype=XSD.string)
        institute.set(RDFS.label, name)
        if department_rdf is not None:
            department_rdf.add(self.ucd_ns.hasParts, institute)
        return institute

    def output(self, filename=None, endpoint=None):
        """
        Outputs the graph into a file / sparql endpoint
        :param filename: the file in which to store the graph
        :param endpoint: the endpoint in which to store the graph
        """
        if filename != None:
            output_file = open(filename, "wb")
            self.graph.serialize(destination=output_file, format='n3', auto_compact=True)
        if endpoint != None:
            rdflib_put(self.graph, endpoint)

    def count_authors(self):
        """
        Prints the number of authors in the graph

        """
        result = self.graph.query(
            """
            PREFIX swrc: <http://swrc.ontoware.org/ontology#>
            SELECT (COUNT(DISTINCT ?a) AS ?count)
            WHERE { ?a rdf:type swrc:AcademicStaff }
            """
        )
        for row in result:
            print("Number of authors LD: {0} ".format(row))
