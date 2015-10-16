from multiprocessing.pool import Pool
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
    page = requests.get(url)
    tree = html.fromstring(page.content)
    paper_type = tree.xpath('//span[text()="Type of material:"]/../span[text()!="Type of material:"]/text()')[0]
    ptitle = tree.xpath('//div[@id="aspect_artifactbrowser_ItemViewer_div_item-view"]/div/h1/text()')[0]
    authors = tree.xpath('//span[text()="Author:"]/../span/a/text()')
    authors = map(split_author_name, authors)
    paper_title = ptitle.replace('\r\n', " ")
    return {"uri": url, "type": paper_type, "title": paper_title, "authors": authors}


def split_author_name(name):
    if ',' in name:
        first_name_index = name.index(',')
        last_name_index = first_name_index + 2
    else:
        first_name_index = len(name) - 11
        last_name_index = 0
    return {"uri": uri_to_use + 'author/' + name.replace(',', '').replace(' ', '').replace('.', ''),
            "last": name[:first_name_index],
            "first": name[last_name_index:]
            }


def get_departments(page_domain, url, process_pool):
    uni = swrc.add_university("http://ucd.ie", "University College Dublin")
    page = requests.get(page_domain + url)
    tree = html.fromstring(page.content)
    college_names = tree.xpath("/html/body/div/div[4]/div/div[1]/div/ul/li/div/div/a/span/text()")
    college_links = tree.xpath("/html/body/div/div[4]/div/div[1]/div/ul/li/div/div/a/@href")
    index = 1
    print("Colleges got, adding schools")
    while index <= len(college_names):
        college_link = page_domain + college_links[index - 1]
        college = swrc.add_department(college_link, college_names[index - 1], uni)
        school_names = tree.xpath(
            "/html/body/div/div[4]/div/div[1]/div/ul/li[{0}]/ul/li/div/div/a/span/text()".format(index))
        school_links = tree.xpath(
            "/html/body/div/div[4]/div/div[1]/div/ul/li[{0}]/ul/li//div/div/a/@href".format(index))
        schools = process_pool.map(get_department_authors, zip(school_links, school_names))
        for school in schools:
            print("Adding {0}".format(school["name"]))
            dept = swrc.add_department(school["uri"], school["name"], college)
            for author in school["authors"]:
                swrc.add_affiliation(author_uri=author["uri"], organisation_rdf=dept)
        index += 1


def get_department_authors(dep):
    page_domain = "http://researchrepository.ucd.ie"
    (link, name) = dep
    link = page_domain + link
    page = requests.get(link)
    tree = html.fromstring(page.content)
    author_link = link + tree.xpath("/html/body/div/div[4]/div/div[1]/div/div[1]/div/ul/li[2]/a/@href")[0]
    authors = []
    while author_link is not None:
        print("Page requested: ", author_link)
        page = requests.get(author_link)
        tree = html.fromstring(page.content)
        # This XPath is different to that in a browser as the acutal code and the browser display are different
        got_authors = tree.xpath("/html/body/div/div[4]/div/div[1]/div/div[2]/table/tr/td/a/text()")
        this_page = list(map(split_author_name, got_authors))
        authors = authors + this_page
        author_link = tree.xpath("/html/body/div/div[4]/div/div[1]/div/div[1]/ul/li[2]/a/@href")
        if len(author_link) > 0:
            author_link = link + "/" + author_link[0]
        else:
            author_link = None
    return {"uri": link, "name": name, "authors": authors}


if __name__ == '__main__':
    domain = 'http://researchrepository.ucd.ie'
    departments_link = "/community-list"
    uri_to_use = domain + "/"
    requests.get(uri_to_use + "robots.txt")
    output_filename = 'ucd_research.n3'
    output_filename = os.path.join('output', output_filename)
    swrc = SWRC(uri_to_use, output_filename, author_uri=uri_to_use + "author/")
    title = "http://researchrepository.ucd.ie/browse?type=title"
    papers = []
    while title is not None:
        papers = papers + get_category_links("aspect_artifactbrowser_ConfigurableBrowse_div_browse-by-title-results",
                                             title)
        print("Number of papers: {0}".format(len(papers)))
        title = get_next_page(title, uri_to_use)
    print("Papers got, getting trees now")
    pool = Pool()
    paper_trees = pool.map(get_page_info, papers)
    print("Trees got, adding data")
    i = 0
    try:
        for paper in paper_trees:
            if paper is not None:  # If it doesn't already exist in the graph
                swrc.add_paper(paper["uri"], paper["type"], paper["title"], paper["authors"])
            print(i)
            i += 1
        get_departments(domain, departments_link, pool)
    except (KeyboardInterrupt, SystemExit):
        swrc.output(output_filename, 'http://localhost:3030/rrucd/update')
    swrc.output(output_filename, 'http://localhost:3030/rrucd/update')
    swrc.get_authors()
