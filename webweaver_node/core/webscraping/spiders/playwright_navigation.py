from asyncio import sleep as async_sleep
import logging
from playwright.async_api import Page, ElementHandle
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError, 
    Error as PlaywrightError, 
    Response as ResponsePlaywright
)
from webweaver_node.core.webscraping.spiders.spider_api import SpiderAPI
from webweaver_node.core.webscraping.middleware.decorators import response_middleware
from webweaver_node.core.exceptions import ClickLinkError, SpiderHttpError


logger = logging.getLogger("scraping")


class PlaywrightNavigation:

    def __init__(self, spider_api:"SpiderAPI", page:Page):
        self.spider_api = spider_api
        self.page = page


    async def click(self, element:ElementHandle, max_retries:int=5, verbose:bool=True, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                async with self.page.expect_navigation() as navigation_info:
                    await  element.click(**kwargs)
                response = await navigation_info.value
                if verbose:
                    logger.debug(f"{self.__class__.__name__}.click() url: {response.url}")
                    logger.debug(f"{self.__class__.__name__}.click() status: {response.status}")
                return
            except (AttributeError, PlaywrightTimeoutError):
                retries += 1
                if verbose:
                    logger.debug(f"{self.__class__.__name__}.click() failed. Retrying x{retries}...")
                await async_sleep(2)
                continue
        raise ClickLinkError(await element.inner_html())


    async def goto_or_none(self, url, timeout:float=100000, **kwargs) -> ResponsePlaywright|None:
        """Calls self.goto_or_error() and returns None if an error is raised."""
        try:
            return await self.goto_or_error(url, timeout, **kwargs)
        except SpiderHttpError as e:
            self.spider_api.log(e)
            return None


    @response_middleware
    async def goto(self, url:str, timeout:float=100000, **kwargs) -> ResponsePlaywright:
        """Wrapper function for playwright's page.goto() method to
        includes error handling and logging.

        *timeout is in milliseconds.
        """
        try:
            return await self.page.goto(url, timeout=timeout, **kwargs)
        except (PlaywrightError, PlaywrightTimeoutError) as e:
            logger.error(e, exc_info=True)
            raise SpiderHttpError(f"{self.__class__.__name__}.goto() failed. url: `{url}`") from e 
