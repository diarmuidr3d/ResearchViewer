from multiprocessing.pool import Pool
import itertools
import os
from lxml import html
import requests
from swrc import SWRC

__author__ = 'Diarmuid Ryan'


def get_category_links(category_id, query_url):
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


def get_page_info(url):
    domainn = 'http://researchrepository.ucd.ie'
    url = domainn + url
    print(url)
    if not swrc.resource_in_graph(url):
        page = requests.get(url)
        tree = html.fromstring(page.content)
        type = tree.xpath('//span[text()="Type of material:"]/../span[text()!="Type of material:"]/text()')[0]
        title = tree.xpath('//div[@id="aspect_artifactbrowser_ItemViewer_div_item-view"]/div/h1/text()')[0]
        authors = tree.xpath('//span[text()="Author:"]/../span/a/text()')
        authors = map(split_author_name,authors)
        return {"uri":url, "type":type, "title":title, "authors":authors}
    else:
        return None


def split_author_name(name):
    if ',' in name:
        findex = name.index(',')
        lindex = findex+2
    else:
        findex = len(name) -1
        lindex = 0
    return {"uri": uri_to_use + 'author/' + name.replace(',', '').replace(' ', '').replace('.',''),
            "last": name[:findex],
            "first": name[lindex:]
            }


if __name__ == '__main__':
    domain = 'http://researchrepository.ucd.ie'
    uri_to_use = domain + "/"
    output_filename = 'ucd_research.n3'
    output_filename = os.path.join('output', output_filename)
    swrc = SWRC(uri_to_use, output_filename, author_uri=uri_to_use+"author/")
    title = "http://researchrepository.ucd.ie/browse?type=title"
    papers = []
    while title is not None:
        papers = papers + get_category_links("aspect_artifactbrowser_ConfigurableBrowse_div_browse-by-title-results",title)
        print("Number of papers: {0}".format(len(papers)))
        title = get_next_page(title, uri_to_use)
    print("Papers got, getting trees now")
    pool = Pool()
    paper_trees = pool.map(get_page_info, papers)
    print("Trees got, adding data")
    i = 0
    try:
        for paper in paper_trees:
            if paper is not None: # If it doesn't already exist in the graph
                swrc.add_paper(paper["uri"], paper["type"], paper["title"], paper["authors"])
            i += 1
    except (KeyboardInterrupt, SystemExit):
        swrc.output(output_filename)
    swrc.output(output_filename)
    swrc.get_authors()
    # TODO: Add local cache support