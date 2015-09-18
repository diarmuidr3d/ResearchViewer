from lxml import html
import requests

__author__ = 'Diarmuid Ryan'


def get_category_links(category_id, query_url, base_url):
    elements = run_query('//div[@id="' + category_id + '"]/ul/li/div/div/a/@href', query_url)
    elements = [base_url + category_link for category_link in elements]
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

domain = 'http://researchrepository.ucd.ie'
collections = get_category_links("aspect_artifactbrowser_CommunityBrowser_div_comunity-browser", domain, domain)
for link in collections:
    title = get_title_link("aspect_artifactbrowser_CommunityViewer_list_community-browse", link, domain)
    papers = []
    while title is not None:
        papers = papers + get_category_links("aspect_artifactbrowser_ConfigurableBrowse_div_browse-by-title-results",
                                             title, domain)
        title = get_next_page(title, link)
    print("{0}: {1}".format(len(papers), papers))