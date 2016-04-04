from urllib import parse
import requests
from lxml import html


def get_page_for_name(full_name):
    """
    Gets the URL of the first result for a particular search query on UCD Research
    :param full_name: the search query to be sent
    :return:
    """
    search_url = "http://www.ucd.ie/search/?q="
    additional = "&frontend=researchweb&as_sitesearch=www.ucd.ie%2Fresearch&scopel_a=UCD+Research&scopet_a=sitesearch&scopev_a=www.ucd.ie%2Fresearch&sa=Go"
    encoded_name = parse.quote_plus(full_name)
    full_url = search_url + encoded_name + additional
    page = requests.get(full_url)
    tree = html.fromstring(page.content)
    xpath = "/html/body/div[1]/div[3]/div[3]/article/div/div[4]/dl/dt[1]/a/@href"
    results = tree.xpath(xpath)
    if len(results) > 0:
        return results[0]
    else:
        return None


def get_school_from_page(page_url):
    """
    Extracts the name of the school from a user's profile page
    :param page_url: the URL of the page to extract from
    :return: a string for the school if one is found, None if not
    """
    page = requests.get(page_url)
    tree = html.fromstring(page.content)
    results = tree.xpath("/html/body/div[1]/div[3]/div[3]/article/div[1]/div[2]/p[1]/text()")
    if len(results) > 0:
        return results[0].strip()
    else:
        return None
