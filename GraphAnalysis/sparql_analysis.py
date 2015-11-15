from networkx.algorithms.centrality.degree_alg import degree_centrality
from networkx.algorithms.centrality.closeness import closeness_centrality
from networkx.algorithms.centrality.eigenvector import eigenvector_centrality
from networkx.algorithms.components.connected import connected_component_subgraphs
import csv
import os
import time

from GraphAnalysis.community_analysis import CommunityAnalysis
from GraphAnalysis.sparql_queries import get_co_authors_csi, get_co_authors

__author__ = 'diarmuid'


def run_algorithms(graph):
    analyse.graph = graph
    results = {}
    start = time.time()
    # results["closeness"] = closeness_centrality(graph, distance='inv_weight')
    results["closeness"] = closeness_centrality(graph)
    end = time.time()
    print("Closeness time taken: {0}".format(end - start))
    start = time.time()
    results["eigenvector"] = eigenvector_centrality(graph)
    end = time.time()
    print("Eigen time taken: {0}".format(end - start))
    start = time.time()
    results["degree"] = degree_centrality(graph)
    end = time.time()
    print("Degree time taken: {0}".format(end - start))
    results["louvain"] = analyse.run_louvain()
    results["cliques"] = analyse.generate_author_clique_dict(analyse.run_k_cliques(20))
    start = time.time()
    results["connected_components"] = list(connected_component_subgraphs(ngraph))
    end = time.time()
    print("Closeness time taken: {0}".format(end - start))
    return results


def output_nodes(results, filename):
    i = 0
    ids = {}
    writer = csv.writer(open(os.path.join('output', filename), 'w'))
    writer.writerow(
        ["Id", "Label", "CLOSENESS", "EIGENVECTOR", "CLIQUES", "DEGREE", "COMMUNITY", "COMPONENT", "DEPARTMENT"])
    for key, value in results["closeness"].items():
        this_key = key
        this_value = str(value)
        eigen_value = results["eigenvector"][key]
        degreeval = results["degree"][key]
        clique = ""
        if key in results["cliques"]:
            clique = str(results["cliques"][key])
        louvain_value = ""
        if key in results["louvain"]:
            louvain_value = str(results["louvain"][key])
        component = connected_components_dict[key]
        row = [i, this_key, this_value, eigen_value, clique, degreeval, louvain_value, component]
        # departments = analyse.get_affiliation_names(this_key)
        # for each in departments:
        #     row.append(each)
        writer.writerow(row)
        ids[this_key] = i
        i += 1
    return ids


def output_edges(filename, ids, results):
    edges = csv.writer(open(os.path.join('output', filename), 'w'))
    edges.writerow(['Source', 'Target', 'Type', 'Id', 'Label', 'Weight'])
    id = 0
    for row in results:
        data = [ids[row["author"]["value"]], ids[row["coauthor"]["value"]], "Undirected", id, id, row["count"]["value"]]
        edges.writerow(data)
        id += 1


endpoint = 'http://localhost:3030/ucdrr/query'
analyse = CommunityAnalysis(endpoint)
ngraph = analyse.graph
print("Graph created")
results = run_algorithms(ngraph)
connected_components_dict = {}
i = 0
for graph in results["connected_components"]:
    for node in graph.nodes():
        connected_components_dict[node] = i
    i += 1
ids = output_nodes(results, 'nodes.csv')
# query_results = get_co_authors_csi(endpoint)
query_results = get_co_authors(endpoint)
output_edges('coauthors.csv', ids, query_results)
largest_component = max(results['connected_components'], key=len)
component_results = run_algorithms(largest_component)
output_nodes(component_results, 'largest_component_nodes.csv')
