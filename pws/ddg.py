#coding=utf-8

from bs4 import BeautifulSoup
from time import sleep as wait
import re
import requests
try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser


##################################################
# Copied code
##################################################
class MLStripper(HTMLParser):
    # Code copied from StackOverflow http://stackoverflow.com/a/925630/3664835
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    # Code copied from StackOverflow http://stackoverflow.com/a/925630/3664835
    s = MLStripper()
    s.feed(html)
    return ' '.join(s.get_data().split())


##################################################
# Helpers
##################################################
# https://duckduckgo.com/html/?q=hello%20world
def generate_url(query):  # , num, start, recent, country_code):
    """(str, str, str) -> str
    A url in the required format is generated.
    """
    query = '%20'.join(query.split())
    url = 'https://duckduckgo.com/html/?q=' + query
    return url


##################################################
# Class
##################################################
class Ddg:

    @staticmethod
    def search(query, num=10, start=0, sleep=True, recent=None, country_code=None):
        if sleep:
            wait(1)
        url = generate_url(query)
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        results = Ddg.scrape_search_result(soup, num, start)

        temp = {'results': results,
                'url': url,
                'expected_num': num,
                'received_num': len(results),
                'start': start,
                'search_engine': 'google',
                'related_queries': '',
                'total_results': '',
                'country_code': country_code,
                }

        return temp

    @staticmethod
    def scrape_search_result(soup, num, start):
        raw_results = soup.find_all('div', attrs={'class': 'results_links results_links_deep web-result'})
        results = []
        
        for result in raw_results:
            subresult = result.find('div', attrs={'class': 'links_main links_deep'})
            link = subresult.find('a').get('href')

            raw_link_text = subresult.find('a')
            link_text = strip_tags(str(raw_link_text))

            raw_link_info = subresult.find('div', attrs={'class': 'snippet'})
            link_info = strip_tags(str(raw_link_info))

            additional_links = dict()
            raw_additional_links = result.find('div', attrs={'class': 'url'})

            if raw_additional_links is not None:
                link_number = 1
                for temp in raw_additional_links:
                    additional_links['additional_link' + str(link_number)] = strip_tags(str(temp))
                    link_number += 1

            temp = {'link': link,
                    'link_text': link_text,
                    'link_info': link_info,
                    'additional_links': additional_links,
                    }

            results.append(temp)

        results = results[start:start+num]
        return results
