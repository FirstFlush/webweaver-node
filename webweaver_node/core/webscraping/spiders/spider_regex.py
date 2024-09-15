import re
from typing import TYPE_CHECKING
from urllib.parse import urljoin

if TYPE_CHECKING:
    from webweaver_node.core.webscraping.spiders.spider_base import Spider


class SpiderRegex:

    def __init__(self, spider:"Spider"):
        self.spider = spider

    # def find_emails(self, flattened_html:str, domain:Optional[str]=None) -> list:
    #     """Returns a list of all emails found in the page. Filters by emails 
    #     that contain the domain, if a domain is specified.
    #     """
    #     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    #     emails = re.findall(email_pattern, flattened_html)
    #     if domain is not None:
    #         emails = [email for email in emails if email.find(domain) != -1]
    #     return emails


    # def href_links(self, base_url:str) -> list[str]:
    #     """Retrieve all hrefs on the page and return them as absolute URLs,
    #     including relative URLs. For base_url pass in
    #     """
    #     a_tags = self.find_all('a', href=True)
    #     return [urljoin(base_url, a['href']) for a in a_tags]

