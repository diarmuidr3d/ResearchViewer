from networkx import get_edge_attributes
from networkx.algorithms.centrality.degree_alg import degree_centrality
from networkx.algorithms.centrality.closeness import closeness_centrality
from networkx.algorithms.centrality.eigenvector import eigenvector_centrality
from networkx.algorithms.components.connected import connected_component_subgraphs
from networkx.algorithms.shortest_paths import average_shortest_path_length
import csv
import os
import time

from GraphAnalysis.community_analysis import CommunityAnalysis
from GraphAnalysis.sparql_queries import get_co_authors_csi, get_co_authors, get_author_department

__author__ = 'diarmuid'

class stats:
    closeness = "closeness"
    eigenvector = "eigenvector"
    degree = "degree"
    louvain = "louvain"
    cliques = "cliques"
    components = "connected_components"

def run_algorithms(graph):
    """
    Runs all network analysis algorithms on the graph
    :param graph: the networkx graph
    :return: a dictionary indexed by algorithm which each contains a dictionary of nodes to value
    """
    analyse.graph = graph
    results = {}
    start = time.time()
    # results["closeness"] = closeness_centrality(graph, distance='inv_weight')
    results[stats.closeness] = closeness_centrality(graph)
    end = time.time()
    print("Closeness time taken: {0}".format(end - start))
    start = time.time()
    results[stats.eigenvector] = eigenvector_centrality(graph)
    end = time.time()
    print("Eigen time taken: {0}".format(end - start))
    start = time.time()
    results[stats.degree] = degree_centrality(graph)
    end = time.time()
    print("Degree time taken: {0}".format(end - start))
    results[stats.louvain] = analyse.run_louvain()
    results[stats.cliques] = analyse.generate_author_clique_dict(analyse.run_k_cliques(20))
    start = time.time()
    results[stats.components] = list(connected_component_subgraphs(ngraph))
    end = time.time()
    print("Closeness time taken: {0}".format(end - start))
    return results


def output_nodes(results, filename):
    """
    Prints the nodes of the network plus their stats to the output file as csv rows
    :param results: a dictionary obtained from run_algorithms or similar
    :param filename: the file to print to
    :return: the integer id values assigned to each node
    """
    i = 0
    ids = {}
    writer = csv.writer(open(os.path.join('output', filename), 'w'))
    writer.writerow(
        ["Id", "Label", "CLOSENESS", "EIGENVECTOR", "CLIQUES", "DEGREE", "COMMUNITY", "COMPONENT", "DEPARTMENT"])
    author_departments = get_author_department(endpoint)
    for key, value in results[stats.closeness].items():
        this_key = key
        this_value = str(value)
        eigen_value = results[stats.eigenvector][key]
        degreeval = results[stats.degree][key]
        clique = ""
        if key in results[stats.cliques]:
            clique = str(results[stats.cliques][key])
        louvain_value = ""
        if key in results[stats.louvain]:
            louvain_value = str(results[stats.louvain][key])
        component = connected_components_dict[key]
        if this_key in author_departments:
            department = author_departments[this_key]
        else:
            department = "None"
        row = [i, this_key, this_value, "{0:.10f}".format(eigen_value), clique, degreeval, louvain_value, component, department]
        writer.writerow(row)
        ids[this_key] = i
        i += 1
    return ids


def output_edges(filename, ids, graph):
    """
    Prints the edges of the graph to the output file as csv
    :param filename: the file tou output to
    :param ids: the ids assigned to each node
    :param graph: the networkx graph
    """
    edges = csv.writer(open(os.path.join('output', filename), 'w'))
    edges.writerow(['Source', 'Target', 'Type', 'Id', 'Label', 'Weight'])
    id = 0
    weights = get_edge_attributes(graph, 'weight')
    for (source, target) in graph.edges():
        data = [ids[source], ids[target], "Undirected", id, id, weights[(source, target)]]
        edges.writerow(data)
        id += 1


# Loads a networkx graph from the sparql endpoint, runs the algorithms on it and outputs the results to csv files
endpoint = 'http://localhost:3030/rucd2/query'
analyse = CommunityAnalysis(endpoint)
ngraph = analyse.graph
print("Graph created")
results = run_algorithms(ngraph)
connected_components_dict = {}
i = 0
for graph in results[stats.components]:
    for node in graph.nodes():
        connected_components_dict[node] = i
    i += 1
ids = output_nodes(results, 'nodes.csv')
output_edges('coauthors.csv', ids, ngraph)
largest_component = max(results[stats.components], key=len)
component_results = run_algorithms(largest_component)
output_nodes(component_results, 'largest_component_nodes.csv')
