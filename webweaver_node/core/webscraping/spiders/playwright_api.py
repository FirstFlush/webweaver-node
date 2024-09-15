import os
from playwright.async_api._generated import (
    Playwright as AsyncPlaywright, 
    Browser, 
    BrowserContext
)
from webweaver_node.core.config import USE_PROXY
from webweaver_node.core.webscraping.proxy.proxy_session import ProxySession
from webweaver_node.core.webscraping.spiders.spider_page import RequestContext, SpiderContext, SpiderPage


class PlaywrightAPI:
    """This class adds playwright functionality to the spider class."""
    
    def __init__(self, spider_asset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.p:AsyncPlaywright = kwargs.get('p', None)
        self.browser:Browser = None


    async def start(self, browser:str='chromium', headless:bool=True):
        """Launch async webdriver and get a blank page."""
        match browser:
            case 'firefox':
                self.browser = await self.p.firefox.launch(headless=headless)
            case 'webkit':  # requires more libraries
                self.browser = await self.p.webkit.launch(headless=headless)
            case _:
                self.browser = await self.p.chromium.launch(headless=headless)
        return
    
    
    async def _new_browser_context(self, proxy:ProxySession=None) -> BrowserContext:
        """Create a new Playwright BrowserContext, either with proxy config details
        or without proxy entirely.
        """
        if proxy:
            browser_context = await self.browser.new_context(proxy={
                'server': proxy.endpoint,
                'username': os.getenv("PROXY_USER"),
                'password': os.getenv("PROXY_PASS"),
            })
        else:
            browser_context = await self.browser.new_context()
        return browser_context


    async def new_context(self, stateful:bool=False, proxy:bool=True) -> SpiderContext:
        """Factory method for creating new SpiderContext objects:
            -creates RequestContext if request is stateful,
            -creates ProxySession object if request is proxied, 
            -creates the underlying Playwright BrowserContext object,
        then passes it all into SpiderContext along with its self.
        """
        if USE_PROXY and proxy:
            if stateful:
                proxy = await self.get_proxy(stateful=True)
                request_context = RequestContext()
            else:
                proxy = await self.get_proxy()
                request_context = None
        else:
            proxy = None
            request_context = RequestContext()
        browser_context = await self._new_browser_context(proxy=proxy)
        return SpiderContext.create(
            self, 
            context=browser_context, 
            request_context=request_context,
            proxy=proxy, 
        )


    async def new_page(self, spider_context:SpiderContext=None) -> SpiderPage:
        """Factory method which calls SpiderPage's factory method for creating a 
        new SpiderPage. This enables us to create new SpiderPage objects without
        having to import SpiderPage on every new webscraping module we make.
        """
        if spider_context:
            new_page = await spider_context.context.new_page()
        else:
            new_page = await self.browser.new_page()
        return await SpiderPage.create(self, new_page, spider_context)





