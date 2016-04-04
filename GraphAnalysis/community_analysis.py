import time
import community
import networkx as nx
from networkx.algorithms.community.kclique import k_clique_communities
from networkx.algorithms.distance_measures import diameter
from networkx.algorithms.distance_measures import eccentricity

from GraphAnalysis.sparql_queries import get_co_authors_csi, get_co_authors, get_department_collaboration

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

    def get_diameter(self, graph):
        """
        Calculates the diameter of graph
        :param graph: A networkx graph
        :return: the value of the graph diameter
        """
        return diameter(graph)

    def get_edge_nodes(self, graph):
        """
        Returns the nodes of the graph tagged with their eccentricity
        :param graph: A networkx graph
        :return: A dictionary of nodes to eccentricity value
        """
        return eccentricity(graph)

    def run_louvain(self):
        """
        Returns communities of the network using the louvain algorithm
        :return: A dictionary with nodes as the keys and the community id as the value
        """
        start = time.time()
        partitions = community.best_partition(self.graph)
        end = time.time()
        print("Louvain time taken: {0}".format(end-start))
        return partitions

    def run_k_cliques(self, smallest_clique):
        """
        Runs K-Cliques on the graph
        :param smallest_clique: the smallest clique that qill be generated
        :return: A dictionary of clique ids to nodes
        """
        start = time.time()
        cliques = None
        if self.graph is not None:
            cliques = k_clique_communities(self.graph,smallest_clique)
        end = time.time()
        print("K-Cliques ime taken: {0}".format(end-start))
        return cliques

    def generate_author_clique_dict(self, cliques):
        """
        Creates an author-clique dictionary from a clique-author dictionary
        :param cliques: The clique-author dictionary
        :return: an author-clique dictionary
        """
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
        """
        Loads the networkx graph from a sparql endpoint
        :param endpoint: The URL of the SPARQL Endpoint
        :return: a networkx graph
        """
        results = get_co_authors_csi(endpoint)
        # results = get_co_authors(endpoint)
        # results = get_department_collaboration(endpoint)
        ngraph = nx.Graph()
        for row in results:
            author = row['author']['value']
            coauthor = row['coauthor']['value']
            inv_weight = 1/int(row['count']['value'])
            weight = int(row['count']['value'])
            if not ngraph.has_edge(author, coauthor) and not ngraph.has_edge(coauthor, author):
                ngraph.add_edge(author, coauthor, weight=weight, inv_weight=inv_weight)
        return ngraph
