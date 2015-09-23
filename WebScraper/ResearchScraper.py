from multiprocessing.pool import Pool
import os
from lxml import html
from rdflib import Graph, Namespace, RDF
import requests

__author__ = 'Diarmuid Ryan'


def get_category_links(category_id, query_url, base_url):
    elements = run_query('//div[@id="' + category_id + '"]/ul/li/div/div/a/@href', query_url)
    elements = [base_url + category_link for category_link in elements]
    elements = [elements[0], elements[1]] # Remove this line for full use
    return elements


def run_query(query, query_url):
    page = requests.get(query_url)
    tree = html.fromstring(page.content)
    return tree.xpath(query)


def get_title_link(container_id, query_url, base_url):
    titles_link = run_query('//ul[@id="' + container_id + '"]/li/a[text()="Titles"]/@href', query_url)
    return base_url + titles_link[0]


def get_next_page(from_page, base_url):
    next_page_links = run_query('//a[text()="Next Page"]/@href', from_page)
    if len(next_page_links) > 0:
        return base_url + "/" + next_page_links[0]
    else:
        return None


def get_authors(from_paper, base_url):
    authors = run_query('//span[text()="Author:"]/../span/a/text()', from_paper)
    print(authors)
    return [base_url + "/author/" + author.replace(',', '').replace(' ', '') for author in authors]


domain = 'http://researchrepository.ucd.ie'
uri_to_use = domain + "/"
graph = Graph(identifier=uri_to_use)
swrc_ns = Namespace("http://swrc.ontoware.org/ontology#")
graph.namespace_manager.bind("swrc",swrc_ns)
out_ns = Namespace(uri_to_use)
graph.namespace_manager.bind("rrucd", out_ns)
collections = get_category_links("aspect_artifactbrowser_CommunityBrowser_div_comunity-browser", domain, domain)
print("Collections Obtained: " + str(collections))
for link in collections:
    title = get_title_link("aspect_artifactbrowser_CommunityViewer_list_community-browse", link, domain)
    papers = []
    while title is not None:
        papers = papers + get_category_links("aspect_artifactbrowser_ConfigurableBrowse_div_browse-by-title-results",
                                             title, domain)
        title = get_next_page(title, link)
    for paper in papers:
        paper_rdf = graph.resource(paper)
        paper_rdf.set(RDF.type, swrc_ns.Publication)
        authors = get_authors(paper, domain)
        for author in authors:
            author_rdf = graph.resource(author)
            author_rdf.set(RDF.type, swrc_ns.AcademicStaff)
            author_rdf.add(swrc_ns.publication, paper_rdf)
            paper_rdf.add(swrc_ns.author, author_rdf)
    # #   TODO: change this so they are added based on their type from the web page
    # print("{0}: {1}".format(len(papers), papers))
output_filename = os.path.join('output', 'ucd_research.n3')
output_file = open(output_filename, "wb")
graph.serialize(destination=output_file, format='n3', auto_compact=True)