from multiprocessing.pool import Pool
import os
import traceback
from lxml import html
import requests
import sys

from swrc import SWRC

__author__ = 'Diarmuid Ryan'


def get_category_links(category_id, query_url):
    """
    Gets the links that are stroed in a particular category on the site, used exclusively now for getting the papers
    :param category_id: the div id for the container
    :param query_url: The website to be queried
    :return: an array of links
    """
    elements = run_query('//div[@id="' + category_id + '"]/ul/li/div/div/a/@href', query_url)
    return elements


def run_query(query, query_url):
    """
    Runs an xpath query on a particular URL. Just used to shorten code elsewhere
    :param query: The XPath query to be used
    :param query_url: The url of the webpage on which the query is to be carried out
    :return: an array of the elements returned by the xpath query
    """
    page = requests.get(query_url)
    tree = html.fromstring(page.content)
    return tree.xpath(query)


def get_next_page(from_page, base_url):
    """
    Gets the "Next Page" link from a particular page and formats it as a Fully Qualified URL
    :param from_page: The lxml tree on which to run the XPath query
    :param base_url: The domain to be appended to the link
    :return: Returns a URL if a next page link is found or None if not
    """
    next_page_links = run_query('//a[text()="Next Page"]/@href', from_page)
    if len(next_page_links) > 0:
        return base_url + "/" + next_page_links[0]
    else:
        return None


def get_page_info(url):
    """
    Gets the details of a paper.
    uri is the URL of the paper
    type is the paper type (eg: Doctoral Thesis)
    title is the title of the paper
    authors is an array of authors made up values returned by split_author_name
    :param url: The URL of the paper
    :return: a list with attributes uri, type, title and authors.
    """
    url = domain + url
    print(url)
    page = requests.get(url)
    tree = html.fromstring(page.content)
    paper_type = tree.xpath('//span[text()="Type of material:"]/../span[text()!="Type of material:"]/text()')[0]
    ptitle = tree.xpath('//div[@id="aspect_artifactbrowser_ItemViewer_div_item-view"]/div/h1/text()')[0]
    authors = tree.xpath('//span[text()="Author:"]/../span/a/text()')
    authors = list(map(split_author_name, authors))
    advisors = tree.xpath('//span[text()="Advisor:"]/../span[2]/text()')
    if len(advisors) > 0:
        advisors = advisors[0]
        authors += split_advisors(advisors)
    contributors = tree.xpath('//span[text()="Contributor:"]/../span/a/text()')
    if len(contributors) > 0:
        contributors = list(map(split_author_name, contributors))
        authors += contributors
    editors = tree.xpath('//span[text()="Editor:"]/../span/a/text()')
    if len(editors) > 0:
        editors = list(map(split_author_name, editors))
        authors += editors
    photographers = tree.xpath('//span[text()="Photographer:"]/../span/a/text()')
    if len(photographers) > 0:
        photographers = list(map(split_author_name, photographers))
        authors += photographers
    paper_title = ptitle.replace('\r\n', " ")
    return {"uri": url, "type": paper_type, "title": paper_title, "authors": authors}


def split_advisors(advisors):
    """
    Splits a string representing a set of authors in a list
    :param advisors: The set of authors in the form Lastname, Firstname; Lastname, Firstname;...
    :return : A list of dictionaries where the dictionaries are those returned by split_author_name
    :rtype : list
    """
    divided_advisors = []
    index = advisors.find(';')
    while index is not -1:
        divided_advisors.append(split_author_name(advisors[:index].strip()))
        advisors = advisors[index + 1:]
        index = advisors.find(';')
    divided_advisors.append(split_author_name(advisors.strip()))
    return divided_advisors


def split_author_name(name):
    """
    Splits a string representing a person up and returns as a dictionary
    :param name: A string of the form Lastname, Firstname
    :return: A dictionary with attributes uri (a unique uri created), last (the person's last name), first (the person's first name)
    """
    if name == 'et al.':
        return None
    else:
        if ',' in name:
            first_name_index = name.index(',')
            last_name_index = first_name_index + 2
        else:
            first_name_index = len(name) - 11
            last_name_index = 0
        return {"uri": uri_to_use + 'author/' + name.replace(',', '').replace(' ', '').replace('.', '').replace("'", ""),
                "last": name[:first_name_index],
                "first": name[last_name_index:]
                }


def get_departments(page_domain, url):
    """
    Gets the Colleges and Schools from the relevant page and adds them and their authors to the graph
    :param page_domain: The website domain
    :param url: The page url (without domain)
    :param process_pool: a multiprocessing pool
    """
    uni = swrc.add_university("http://ucd.ie", "University College Dublin")
    page = requests.get(page_domain + url)
    tree = html.fromstring(page.content)
    colleges = tree.xpath("/html/body/div/div[4]/div/div[1]/div/ul/li")
    print("Colleges got, adding schools")
    index = 1
    for college in colleges:
        name = college.xpath("div/div/a/span/text()")[0]
        link = page_domain + college.xpath("div/div/a/@href")[0]
        school_names = college.xpath("ul/li/div/div/a/span/text()".format(index))
        school_links = college.xpath("ul/li/div/div/a/@href".format(index))
        print("schools for ", name, " are ", school_links)
        college_rdf = swrc.add_college(link, name, uni)
        for school_link, school_name in zip(school_links, school_names):
            print("Adding school {0}".format(school_name))
            dept = swrc.add_school(school_link, school_name, college_rdf)
            # print(school["authors"])
            # for author in school["authors"]:
            #     if author != None: # If the author isn't et al.
            #         swrc.add_affiliation(author_uri=author["uri"], organisation_rdf=dept)
        index += 1

if __name__ == '__main__':
    domain = 'http://researchrepository.ucd.ie'
    departments_link = "/community-list"
    uri_to_use = domain + "/"
    requests.get(uri_to_use + "robots.txt")
    output_filename = 'ucd_research.n3'
    output_filename = os.path.join('output', output_filename)
    # swrc = SWRC(uri_to_use, output_filename, author_uri=uri_to_use + "author/")
    swrc = SWRC(uri_to_use, author_uri=uri_to_use + "author/")
    title = "http://researchrepository.ucd.ie/browse?type=title"
    papers = []
    while title is not None:
        papers = papers + get_category_links("aspect_artifactbrowser_ConfigurableBrowse_div_browse-by-title-results",
                                             title)
        print("Number of papers: {0}".format(len(papers)))
        print(title)
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
        get_departments(domain, departments_link)
    except (KeyboardInterrupt, SystemExit, Exception) as err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_exception: ***")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        print("*** Exception over ***")
        swrc.output(output_filename)
    # swrc.output(output_filename, 'http://localhost:3030/rucd/update')
    swrc.output(output_filename)
    swrc.count_authors()
