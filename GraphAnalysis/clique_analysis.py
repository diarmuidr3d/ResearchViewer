import time
# from sparql_analysis import load_from_endpoint as load_end
from networkx.algorithms.community.kclique import k_clique_communities

__author__ = 'diarmuid'


class CliqueUCD:

    def __init__(self, endpoint, nx_graph=None, smallest_clique=20):
        # if nx_graph is None:
        #     self.graph = load_end(endpoint)
        # else:
        #     self.graph = nx_graph
        self.graph = nx_graph
        self.endpoint = endpoint
        self.cliques = self.run_k_cliques(smallest_clique)

    def run_k_cliques(self, smallest_clique):
        start = time.time()
        cliques = k_clique_communities(self.graph,smallest_clique)
        end = time.time()
        print("Time taken: {0}".format(end-start))
        return cliques

    def generate_author_clique_dict(self):
        authors = {}
        i = 0
        for clique in self.cliques:
            for author in clique:
                if author not in authors:
                    authors[author] = []
                authors[author].append(i)
            i += 1
        return authors