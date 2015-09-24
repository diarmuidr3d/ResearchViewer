from lxml import html
import requests
from swrc import SWRC

__author__ = 'Diarmuid Ryan'


def get_category_links(category_id, query_url, base_url):
    elements = run_query('//div[@id="' + category_id + '"]/ul/li/div/div/a/@href', query_url)
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


def add_paper_details(from_paper, base_url):
    page = requests.get(from_paper)
    tree = html.fromstring(page.content)
    type = tree.xpath('//span[text()="Type of material:"]/../span[text()!="Type of material:"]/text()')
    title = tree.xpath('//div[@id="aspect_artifactbrowser_ItemViewer_div_item-view"]/div/h1/text()')
    paper_rdf = swrc.add_paper(from_paper, type[0], title[0])
    authors = tree.xpath('//span[text()="Author:"]/../span/a/text()')
    for author in authors:
        author_uri = base_url + "/author/" + author.replace(',', '').replace(' ', '')
        swrc.add_author(author_uri, author, paper_rdf)


if __name__ == '__main__':
    domain = 'http://researchrepository.ucd.ie'
    uri_to_use = domain + "/"
    swrc = SWRC(uri_to_use)
    # collections = get_category_links("aspect_artifactbrowser_CommunityBrowser_div_comunity-browser", domain, domain)
    # print("Collections Obtained: " + str(collections))
    # for link in collections:
    #     link = domain + link
    title = "http://researchrepository.ucd.ie/browse?type=title"
    # title = get_title_link("aspect_artifactbrowser_CommunityViewer_list_community-browse", link, domain)
    papers = []
    while title is not None:
        papers = papers + get_category_links("aspect_artifactbrowser_ConfigurableBrowse_div_browse-by-title-results",
                                             title, domain)
        print("Number of papers: {0}".format(len(papers)))
        title = get_next_page(title, uri_to_use)
    print("Papers got")
    i=0
    for paper in papers:
        paper = domain + paper
        print("{0}".format(i))
        add_paper_details(paper, domain)
        i += 1
        if i == 20:
            break
    swrc.output('ucd_research.n3')