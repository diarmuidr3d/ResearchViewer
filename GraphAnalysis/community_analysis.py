import time
# from sparql_analysis import load_from_endpoint as load_end
from SPARQLWrapper import SPARQLWrapper, JSON
import community
import networkx as nx
from networkx.algorithms.community.kclique import k_clique_communities
from sparql_queries import get_co_authors

__author__ = 'diarmuid'


class CommunityAnalysis:

    def __init__(self, endpoint=None, nx_graph=None):
        if nx_graph is not None:
            self.graph = nx_graph
        elif endpoint is not None:
            self.graph = self.load_graph(endpoint)
        else:
            self.graph = None
        self.endpoint = endpoint

    def set_graph(self, graph):
        self.graph = graph

    def run_louvain(self):
        start = time.time()
        partitions = community.best_partition(self.graph)
        end = time.time()
        print("Louvain time taken: {0}".format(end-start))
        return partitions

    def run_k_cliques(self, smallest_clique):
        start = time.time()
        cliques = None
        if self.graph is not None:
            cliques = k_clique_communities(self.graph,smallest_clique)
        end = time.time()
        print("K-Cliques ime taken: {0}".format(end-start))
        return cliques

    def generate_author_clique_dict(self, cliques):
        authors = {}
        i = 0
        for clique in cliques:
            for author in clique:
                if author not in authors:
                    authors[author] = []
                authors[author].append(i)
            i += 1
        return authors

    def load_graph(self, endpoint):
        results = get_co_authors(endpoint);
        ngraph = nx.Graph()
        for row in results:
            author = row['author']['value']
            coauthor = row['coauthor']['value']
            # inv_weight = 1/int(row['count']['value'])
            # weight = int(row['count']['value'])
            ngraph.add_edge(author, coauthor)
            # ngraph.add_edge(author, coauthor, weight=weight, inv_weight=inv_weight)
        return ngraph

    # def get_affiliation_names(self, author_uri):
    #     if self.endpoint is None:
    #         return None
    #     sparql = SPARQLWrapper(self.endpoint, returnFormat=JSON)
    #     sparql.setQuery("""
    #     PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#>
    #     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    #     SELECT ?dept_name
    #     WHERE {
    #         <""" + author_uri + """> rucd:affiliation ?department .
    #         ?department rdfs:label ?dept_name
    #     }
    #     """)
    #     results = sparql.queryAndConvert()
    #     departments = []
    #     for row in results["results"]["bindings"]:
    #         departments.append(row["dept_name"]["value"])
    #     return departments
