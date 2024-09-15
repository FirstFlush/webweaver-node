import asyncio
import logging

from webweaver_node.core.webscraping.middleware.middleware_manager import MiddlewareManager
from webweaver_node.core.webscraping.pipelines.pipeline_listener import PipelineListener
from webweaver_node.core.webscraping.proxy.proxy_manager import ProxyManager
from webweaver_node.core.schema.pydantic_schemas import LaunchSpiderSchema
from webweaver_node.core.webscraping.registry.builders import RegistryBuilder
from webweaver_node.core.webscraping.registry.scraping_registry import scraping_registry
from webweaver_node.core.webscraping.spiders.spider_launcher import SpiderLauncher


logger = logging.getLogger('scraping')


class WebScrape:
    """Class for any scraping-related views/routes. Mainly created to keep
    route files clean and standardize the logic between launching spiders
    and launching campaigns.
    """
    def __init__(self, launch_data:LaunchSpiderSchema, use_proxy:bool):
        self.launch_data = launch_data
        self.use_proxy = use_proxy
        self.middleware_manager = self._middleware_manager()
        self.proxy_manager = self._proxy_manager(self.use_proxy)
        self.async_queue = self._async_queue()

    def _proxy_manager(self, is_proxy:bool) -> ProxyManager | None:
        if is_proxy:
            proxy_manager = ProxyManager()
            logger.debug("initialized ProxyManager")
            return proxy_manager

    def _middleware_manager(self) -> MiddlewareManager:
        middleware_manager = MiddlewareManager()
        logger.debug("initialized MiddlewareManager")
        return middleware_manager

    async def _build_scraping_registry(self):
        builder = RegistryBuilder(self.launch_data)
        await builder.initialize_solo_scrape()
        await scraping_registry.build(solospider_builder=builder)
        logger.debug('Scraping registry built')

    def _async_queue(self):
        queue = asyncio.Queue()
        logger.debug('initialized async queue')
        return queue

    async def scrape(self):

        await self._build_scraping_registry()

        sl = SpiderLauncher(
            self.async_queue, 
            spiders=scraping_registry.spiders,
            middleware_api=self.middleware_manager.middleware_api,
            proxy_api=self.proxy_manager.proxy_api
        )
        logger.debug('Initialized SpiderLauncher')
        pl = PipelineListener(self.async_queue)
        logger.debug('Initialized PipelineListener')

        await asyncio.gather(sl.launch(), pl.listen())

        await scraping_registry.finish()



