from SPARQLWrapper import SPARQLWrapper, JSON
import networkx as nx
<<<<<<< HEAD
from networkx.algorithms.centrality.degree_alg import degree_centrality
=======
>>>>>>> 62d1686af5373530e917e274d5e4a3fcae6271fb
from networkx.algorithms.centrality.closeness import closeness_centrality
from networkx.algorithms.centrality.eigenvector import eigenvector_centrality
import csv
import os
import time
<<<<<<< HEAD
from community_analysis import CommunityAnalysis
=======
from clique_analysis import CliqueUCD
>>>>>>> 62d1686af5373530e917e274d5e4a3fcae6271fb

__author__ = 'diarmuid'


def load_from_endpoint(endpoint):
    ngraph = nx.Graph()
    sparql = SPARQLWrapper(endpoint, returnFormat=JSON)
    sparql.setQuery("""
    PREFIX rucd: <http://diarmuidr3d.github.io/swrc_ont/swrc_UCD.owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?authorA ?authorB (COUNT (?paper) AS ?count)
    WHERE {
        ?authorA rucd:cooperatesWith ?authorB .
        ?authorA rucd:publication ?paper .
        ?authorB rucd:publication ?paper .
    }
    GROUP BY ?authorA ?authorB
    """)
    results = sparql.queryAndConvert()
    for row in results['results']['bindings']:
        author = row['authorA']['value']
        coauthor = row['authorB']['value']
<<<<<<< HEAD
        # inv_weight = 1/int(row['count']['value'])
        # weight = int(row['count']['value'])
        ngraph.add_edge(author, coauthor)
        # ngraph.add_edge(author, coauthor, weight=weight, inv_weight=inv_weight)
=======
        inv_weight = 1/int(row['count']['value'])
        weight = int(row['count']['value'])
        ngraph.add_edge(author, coauthor, weight=weight, inv_weight=inv_weight)
>>>>>>> 62d1686af5373530e917e274d5e4a3fcae6271fb
    return ngraph


ngraph = load_from_endpoint('http://localhost:3030/ucdrr/query')
print("Graph created")
start = time.time()
<<<<<<< HEAD
# closeness = closeness_centrality(ngraph, distance='inv_weight')
closeness = closeness_centrality(ngraph)
end = time.time()
print("Closeness time taken: {0}".format(end-start))
start = time.time()
eigenvector = eigenvector_centrality(ngraph)
end = time.time()
print("Eigen time taken: {0}".format(end-start))
start = time.time()
degree = degree_centrality(ngraph)
end = time.time()
print("Degree time taken: {0}".format(end-start))
analyse = CommunityAnalysis('http://localhost:3030/ucdrr/query', nx_graph=ngraph)
louvain = analyse.run_louvain()
cliques = analyse.generate_author_clique_dict(analyse.run_k_cliques(20))
writer = csv.writer(open(os.path.join('output','closeness.csv'), 'w'))
writer.writerow(["URI", "CLOSENESS", "EIGENVECTOR", "CLIQUES", "DEGREE", "COMMUNITY", "DEPARTMENT"])
for key, value in closeness.items():
    this_key = key
    this_value = str(value)
    eigen_value = eigenvector[key]
    degreeval = degree[key]
    clique = ""
    if key in cliques:
        clique = str(cliques[key])
    louvain_value = ""
    if key in louvain:
        louvain_value = str(louvain[key])
    row = [this_key, this_value, eigen_value, clique, degreeval, louvain_value]
    departments = analyse.get_affiliation_names(this_key)
    for each in departments:
        row.append(each)
    writer.writerow(row)
=======
closeness = closeness_centrality(ngraph, distance='inv_weight')
end = time.time()
print("Time taken: {0}".format(end-start))
start = time.time()
eigenvector = eigenvector_centrality(ngraph)
end = time.time()
print("Time taken: {0}".format(end-start))
cliques = CliqueUCD('http://localhost:3030/ucdrr/query', nx_graph=ngraph)
author_cliques = cliques.generate_author_clique_dict()
writer = csv.writer(open(os.path.join('output','closeness.csv'), 'w'))
writer.writerow(["URI", "CLOSENESS", "EIGENVECTOR", "CLIQUES"])
for key, value in closeness.items():
    this_key = key
    this_value = str(value)
    eigenval = eigenvector[key]
    clique = ""
    if key in author_cliques:
        clique = str(author_cliques[key])
    writer.writerow([this_key, this_value, eigenval, clique])
>>>>>>> 62d1686af5373530e917e274d5e4a3fcae6271fb
