
import asyncio
import logging

import random
from typing import TYPE_CHECKING
import ua_generator
import validators

from playwright.async_api._generated import Playwright as AsyncPlaywright
from typing import Optional

from webweaver_node.core.exceptions import BadMarkupError
from webweaver_node.core.config import SENTINEL
from webweaver_node.core.common.enums import SpiderState
from webweaver_node.core.webscraping.spiders.aiohttp_api import AiohttpAPI
from webweaver_node.core.webscraping.fuzzy_matching.fuzzy_handler import FuzzyHandler
from webweaver_node.core.webscraping.spiders.playwright_api import PlaywrightAPI
from webweaver_node.core.webscraping.spiders.spider_api import SpiderAPI
from webweaver_node.core.webscraping.spiders.spider_error import SpiderError
from webweaver_node.core.webscraping.spiders.module_logger import SpiderModuleLog
from webweaver_node.core.webscraping.spiders.spider_regex import SpiderRegex
from webweaver_node.core.webscraping.spiders.soup_base import SpiderSoup
from webweaver_node.core.webscraping.middleware.middleware_manager import MiddlewareAPI
from webweaver_node.core.webscraping.proxy.proxy_session import ProxySession
from webweaver_node.core.webscraping.proxy.proxy_manager import ProxyAPI
from webweaver_node.core.webscraping.registry.scraping_registry import scraping_registry, SpiderState


if TYPE_CHECKING:
    from webweaver_node.core.webscraping.spiders.models import SpiderAsset


logger = logging.getLogger('scraping')


class Spider:
    """Base class for all webscraping spiders"""
    session = None
    url = None

    def __init__(
            self,
            spider_asset:SpiderAsset,
            middleware_api:MiddlewareAPI,
            proxy_api:ProxyAPI,
            p:Optional[AsyncPlaywright]=None,
            test_env:bool = False,
    ):
        self.ua:str = ua_generator.generate(device="desktop").text
        self.headers:dict = self.create_headers()
        self.spider_asset = spider_asset
        self.spider_id = self.spider_asset.id
        self.errors = SpiderError(self)
        self.regex = SpiderRegex(self)
        self.domain = self.spider_asset.domain
        self.url = self._url()
        self.module_logger = SpiderModuleLog(spider_asset.module_dir_path(), spider_asset.spider_name)
        self.middleware_api = middleware_api
        self.proxy_api = proxy_api
        self.spider_api = SpiderAPI(self)
        self.fuzzy_handler = FuzzyHandler
        self.p = p
        self.aio = AiohttpAPI(self) 
        self.playwright = PlaywrightAPI(self)

        if not test_env:
            self.params = self.get_params()


    @property
    def sentinel(self) -> str:
        """Retursn the sentinel value"""
        return SENTINEL


    def _url(self) -> str:
        if self.domain.startswith("https://"):
            return self.domain
        return f"https://{self.domain}"



    def clean_url(self, url:str|None, raise_exc:bool=False) -> str|None:
        """Sometimes <img> src attributes, or <a> href attributes need to be
        cleaned up a bit before making a new web request.
        """
        url = url.strip().replace(' ', '%20')
        if not url:
            self.log(f"TypeError {self.spider_asset.spider_name}: URL '{url}' passed to Spider.clean_url() is None!")
            return
        if url.startswith('//'):
            url = f"https:{url}"
        elif url.startswith('/'):
            url = f"https://{self.spider_asset.domain}{url}"

        if validators.url(url):
            return url
        else:
            msg = f"({self.spider_asset.spider_name}): URL '{url}' passed to Spider.clean_url() is invalid!"
            if raise_exc:
                raise ValueError(msg)
            else:
                self.log(msg)
                return url


    def random_headers(self) -> dict:
        """Currently headers is static except for UA. 
        Will put in functionality here to make the other 
        headers more dynamic.
        """
        headers = {
            "User-Agent": ua_generator.generate(device="desktop").text,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",  # Do Not Track Request Header
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",   
        }
        return headers


    async def get_proxy(self, stateful:bool=False) -> ProxySession | None:
        """Create a new ProxySession object"""
        try:
            return await self.proxy_api.create_proxy_session(stateful)
        except AttributeError as e:
            return None

    def get_params(self) -> dict[str, str]:
        """Retrieves the spider's params from the registry."""
        return scraping_registry.registry[self.spider_id].params


    def soup_check(self, soup:SpiderSoup):
        """Create HTML file from soup"""
        with open('soup_check.html', 'w') as f:
            f.write(soup.prettify())


    def get_soup(self, markup:str|bytes, **kwargs) -> SpiderSoup|None:
        """Instantiates the SpiderSoup object.

        Logs error if SpiderSoup fails
        to instantiate.
        """
        soup = None
        spider_name = self.__class__.__name__
        try:
            soup = SpiderSoup(spider_name=spider_name, markup=markup, features='lxml', **kwargs)
        except BadMarkupError as e:
            self.log(f"{e.__class__.__name__}({e.spider_name}): {e.error_details}")
        return soup


    def get_state(self) -> SpiderState:
        """Gets the current state of the spider in the spider registry."""
        return scraping_registry.get_spider_state(self.spider_id)


    def shuffle(self, list_to_shuffle:list) -> None:
        """Shuffle the order of the list in place. 
        This is useful to randomize clicking through a list of links.
        """
        random.shuffle(list_to_shuffle)
        return


    def check_state(self) -> bool:
        """Checks the spider's state and returns False if it is
        any other state besides 'RUNNING'.
        """
        if self.spider_state() == SpiderState.RUNNING:
            return True
        return False


    def create_headers(self) -> dict:
        """Currently headers is static except for UA. 
        Will put in functionality here to make the other 
        headers more dynamic.
        """
        headers = {
            "User-Agent": self.ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",  # Do Not Track Request Header
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",   
        }
        return headers


    async def jitter(self, low:float=0, high:float=2):
        """A randomized delay. To look more human."""
        await asyncio.sleep(random.uniform(low, high))
        return

