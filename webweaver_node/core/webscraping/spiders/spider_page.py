import logging
import random
from typing import TYPE_CHECKING

from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import (
    Page, 
    BrowserContext,
    ElementHandle, 
    Response as ResponsePlaywright
)
from webweaver_node.core.exceptions import SpiderHttpError
from webweaver_node.core.webscraping.spiders.playwright_navigation import PlaywrightNavigation
from webweaver_node.core.webscraping.spiders.dom import (
    PageConfig,
    Cursor,
    Scroll
)
from webweaver_node.core.webscraping.middleware.decorators import response_middleware


if TYPE_CHECKING:
    from webweaver_node.core.webscraping.proxy.proxy_session import ProxySession
    from webweaver_node.core.webscraping.spiders.spider_base import Spider


logger = logging.getLogger('scraping')


class RequestContextInterface:

    def __init__(self, request_context:"RequestContext"):
        self.request_context = request_context

    def increase_retry_count(self):
        self.request_context.retry_count += 1
        return

    @property
    def retry_count(self) -> int:
        return self.request_context.retry_count


class RequestContext:
    """The shared-state between multiple requests within the
    same SpiderContext. 
    This is also the object Middleware will operate on.
    """
    def __init__(self):
        self.retry_count = 0
        # self.begin = datetime.utcnow()
        self.url = None



class SpiderContext():
    """Wrapper class to extend the functionality of Playwright's BrowserContext object.
    When using a proxy in Playwright, the proxy is passed into the BrowserContext object
    upon instantiation. The SpiderContext object will keep the ProxySession object for
    as long as the session is needed.
    """
    def __init__(
            self, 
            spider: "Spider",
            context:BrowserContext,
            request_context:RequestContext|None=None,
            proxy:"ProxySession"|None=None,
        ):
        self.spider = spider
        self.context = context
        self.proxy = proxy
        self.request_context = request_context
        if self.request_context:
            self.request_interface = RequestContextInterface(request_context)
        else:
            self.request_interface = None

    @property
    def is_stateful(self) -> bool:
        return self.request_context is not None

    async def new_spider_page(self) -> "SpiderPage":
        """Create a new SpiderPage object, controlled by this SpiderContext."""
        page = await self.context.new_page()
        return await SpiderPage.create(
            spider = self.spider, 
            page = page, 
            spider_context = self
        )


    @staticmethod
    def create(
            spider:"Spider", 
            context:BrowserContext, 
            request_context:RequestContext=None,
            proxy:"ProxySession"=None, 
        ) -> "SpiderContext":
        """Factory method for creating new SpiderContext objects."""
        spider_context = SpiderContext(
            spider=spider, 
            context=context, 
            request_context=request_context,
            proxy=proxy
        )
        return spider_context


class SpiderPage():
    """Wrapper class to extend the functionality of Playwright's Page object."""
    def __init__(self, spider:"Spider", page:Page, spider_context:SpiderContext):
        self.spider = spider
        self.page = page
        self.spider_context = spider_context
        self.config = PageConfig(self.page)
        self.cursor = Cursor(self.page)
        self.scroll = Scroll(self.page)
        self.navigation = PlaywrightNavigation(self.spider.spider_api, self.page)


    @staticmethod
    async def create(spider:"Spider", page:Page, spider_context:SpiderContext) ->"SpiderPage":
        """Factory method for creating new SpiderPage objects 
        while avoiding having to make the init function async
        """
        spider_page = SpiderPage(spider, page, spider_context)
        await spider_page.config.set_page_config()
        return spider_page


    async def check_element(self, element:ElementHandle, timeout:float=100000, **kwargs) -> ElementHandle|None:
        """Check if an element exists. If it does, return the element. 
        Otherwise, return None.
        """
        try:
            return await self.page.wait_for_selector(selector=element, timeout=timeout, **kwargs)
        except PlaywrightTimeoutError:
            return None

