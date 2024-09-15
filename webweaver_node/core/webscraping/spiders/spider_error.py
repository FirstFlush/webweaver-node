from aiohttp import ClientPayloadError
import logging
from typing import TYPE_CHECKING
from webweaver_node.core.exceptions import SpiderHttpError, ElementNotFound, SpiderSoupError, WebScrapingError

if TYPE_CHECKING:
    from webweaver_node.core.webscraping.spiders.spider_base import Spider

logger = logging.getLogger('scraping')


class SpiderError:
    SpiderHttpError = SpiderHttpError
    ElementNotFound = ElementNotFound
    SpiderSoupError = SpiderSoupError
    WebScrapingError = WebScrapingError
    ClientPayloadError = ClientPayloadError

    def __init__(self, spider:"Spider"):
        self.spider = spider


    def raise_http_error(self, msg:str=None, url:str=None, ignore_error:bool=False):
        """Logs and raises an HTTP error. Will only log the error if ignore_error is True."""
        if not msg:
            msg = f"SpiderHttpError: '{self.spider.spider_asset.spider_name}', URL: '{url}'"
        logger.error(msg)
        if not ignore_error:
            raise self.SpiderHttpError(msg)

