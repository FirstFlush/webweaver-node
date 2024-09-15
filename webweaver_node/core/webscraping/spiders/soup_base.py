from bs4 import BeautifulSoup, Tag
from bs4 import FeatureNotFound, ParserRejectedMarkup
import logging
import re
from typing import Optional

from webweaver_node.core.exceptions import BadMarkupError


logger = logging.getLogger('scraping')


class SoupRegex:

    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')


class SpiderTag(Tag):

    def flatten_html(self) -> str:
        """Return a flat string of the BeautifulSoup object or HTML Element
        This is required for regex operations.
        """
        return str(self)


    def get_hrefs(self, substring:str=None, regex_pattern:re.Pattern=None) -> list[str]:
        """Retrieve all hrefs on the page and return them as absolute URLs,
        including relative URLs. For base_url pass in

        Two optional parameters allow you to filter the hrefs by substrings or regex.
        """
        anchor_elements = self.find_all('a', href=True)
        hrefs = [anchor_element['href'] for anchor_element in anchor_elements]
        if substring:
            hrefs = [href for href in hrefs if substring in href]
        elif regex_pattern:
            hrefs = [href for href in hrefs if regex_pattern.search(href)]
        
        return hrefs


    def get_href(self, substring:str=None, regex_pattern:re.Pattern=None) -> str:
        return self.get_hrefs(substring, regex_pattern)[0]


    def select_one_text(self, selector:str) -> str | None:
        """Select an element and, if it exists, extract the text."""
        element = self.select_one(selector)
        if element:
            text = element.text
            return text if text != '' else None


    def select_one_attr(self, selector:str, attr:str, strip_text:str=None) -> str | None:
        """Select an element and, if it exists, extract the specified attribute.
        Option to strip text out if necessary.
        """
        element = self.select_one(selector)
        if element:
            if strip_text:
                attr = element[attr].replace(strip_text, '')
            else:
                attr = element[attr]
            return attr if attr != '' else None


    def select_one_and_extract(self, selector:str) -> "SpiderTag | None": 
        """Destructively extract element from tree, if it exists."""
        element = self.select_one(selector)
        if element:
            return element.extract()


    def select_one_and_decompose(self, selector:str) -> None:
        """Find an element matching the CSS selector and, if found, decomposes it."""
        element = self.select_one(selector)
        if element:
            element.decompose()

    def select_and_decompose(self, selectors:str) -> None:
        """Finds all elements matching the CSS selectors and decomposes them."""
        elements = self.select(selectors)
        for element in elements:
            element.decompose()


    def spider_attribute(self, selector:str, attr:str, default=None) -> str|None:
        """Retrieve's an HTML element's attribute, or returns default value if 
        the element does not exist.
        """
        try:
            return self.select_one(selector).get(attr)
        except AttributeError:
            return default


class SpiderSoup(BeautifulSoup):

    regex = SoupRegex

    def __init__(self, spider_name:str, markup:str|bytes, features:str="lxml", *args, **kwargs):
        """Instantiates SpiderParser object, which is just a glorified BeautifulSoup 
        object wrapped up with some logging/error handling, and some regex.
        element_classes is used to subclass bs4 objects that are returned, such as
        Tags or NavigableStrings.
        """
        element_classes = {
            Tag: SpiderTag,
        }
        try:
            super().__init__(
                markup=markup, 
                features=features, 
                element_classes=element_classes, 
                *args,
                **kwargs
            )
        except (FeatureNotFound, ValueError, ParserRejectedMarkup) as e:
            raise BadMarkupError(spider_name, str(e))


    # def select_one(self, *args, **kwargs) -> SpiderTag:
    #     tag:SpiderTag = super().select_one(*args, **kwargs)
    #     return tag


    def flatten_html(self, element:SpiderTag=None) -> str:
        """Return a flat string of the BeautifulSoup object or HTML Element"""
        if element:
            return str(element)
        return str(self)


    def find_emails(self, flattened_html:str, domain:Optional[str]=None) -> list:
        """Returns a list of all emails found in the page. Filters by emails 
        that contain the domain, if a domain is specified.
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, flattened_html)
        if domain is not None:
            emails = [email for email in emails if email.find(domain) != -1]
        return emails


    def get_all_hrefs(self) -> list[str]:
        """Retrieve all hrefs on the page and return them as absolute URLs,
        including relative URLs. For base_url pass in
        """
        return [a['href'] for a in self.find_all('a', href=True)]



    def select_one_text(self, selector:str) -> str | None:
        """Select an element and, if it exists, extract the text."""
        element = self.select_one(selector)
        if element:
            text = element.text
            return text if text != '' else None


    def select_one_attr(self, selector:str, attr:str, strip_text:str=None) -> str | None:
        """Select an element and, if it exists, extract the specified attribute.
        Option to strip text out if necessary.
        """
        element = self.select_one(selector)
        if element:
            if strip_text:
                attr = element[attr].replace(strip_text, '')
            else:
                attr = element[attr]
            return attr if attr != '' else None


    def select_one_and_extract(self, selector:str) -> "SpiderTag | None": 
        """Destructively extract elementfrom tree, if it exists."""
        element = self.select_one(selector)
        if element:
            return element.extract()


    def select_one_and_decompose(self, selector:str) -> None:
        """Find an element matching the CSS selector and, if found, decomposes it."""
        element = self.select_one(selector)
        if element:
            element.decompose()

    def select_and_decompose(self, selectors:str) -> None:
        """Finds all elements matching the CSS selectors and decomposes them."""
        elements = self.select(selectors)
        for element in elements:
            element.decompose()



