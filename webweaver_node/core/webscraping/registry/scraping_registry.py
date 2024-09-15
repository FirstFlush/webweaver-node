from __future__ import annotations
from dataclasses import dataclass
from asyncio import Lock
import logging

from webweaver_node.core.common.enums import SpiderState
from webweaver_node.core.webscraping.registry.builders import RegistryBuilder
from webweaver_node.core.webscraping.spiders.models import SpiderAsset


logger = logging.getLogger('scraping')
lock = Lock()


@dataclass
class SpiderRegistryItem:
    spider_asset: SpiderAsset
    params: dict[str, str]
    state: SpiderState


class ScrapingRegistry:
    """This class serves as a shared state between diferent parts of the app.
    For example if a pipeline module encounters an error and wants to tell a spider module
    to stop scraping, it can inform the spider by updating the spider's state in the ScrapingRegistry. 
    The Spider can check this state periodically as it scrapes.

    Example self.registry:
    {
        1: SpiderRegistryItem(spider_asset=ABCSpider, params={"search":"bakeries, NY"}, SpiderState.RUNNING)
        8: SpiderRegistryItem(spider_asset=XYZSpider, params={"dir_path":"/search/newyork"}, SpiderState.COMPLETE)
    }
    -The keys (ints) are the SpiderAsset IDs. The values are the SpiderAssets and their states.
    -Spider's check_state() method checks the state and Pipeline's update_state() updates it.
    """
    registry: dict[int, SpiderRegistryItem] = {}
    spiders: list[SpiderAsset] = None

    async def build(self,
            builder: RegistryBuilder = None,
    ):
        self.add_spiders(builder.spider_details)  
        self.spiders = self.create_spider_list(builder.spider_details)


    def create_spider_list(self, spider_details: list) -> list[SpiderAsset]:
        return [spider['spider'] for spider in spider_details]


    def add_spider(
            self,
            spider_id: int,
            spider_asset: SpiderAsset,
            params: dict[str, str],
            state: SpiderState = SpiderState.RUNNING
    ):
        self.registry[spider_id] = SpiderRegistryItem(
            spider_asset, params, state)


    def add_spiders(self, spider_details: list):
        """Adds the spiders and their respective parameters to the registry"""
        for spider_detail in spider_details:
            spider = spider_detail['spider']
            params = spider_detail['params']
            self.add_spider(
                spider_id=spider.id,
                spider_asset=spider,
                params=params
            )


    def _get_sri(self, spider_id: int) -> SpiderRegistryItem:
        """Grab a SpiderRegistryItem based on the SpiderAsset's id."""
        return self.registry[spider_id]

    def get_spider_asset(self, spider_id:int) -> SpiderAsset:
        """Grab a SpiderAsset object from the registry."""
        return self.registry[spider_id].spider_asset


    async def spider_error(self, spider_id:int):
        """When a spider causes pipeline errors, the pipeline listener can
        set the spider's state the ERROR to stop webscraping from proceeding.
        """
        async with lock:
            self._get_sri(spider_id).state = SpiderState.ERROR

    async def set_spider_state(self, spider_id: int, state: SpiderState):
        async with lock:
            self._get_sri(spider_id).state = state

    def get_spider_name(self, spider_id: int) -> str:
        return self._get_sri(spider_id).spider_asset.spider_name

    def get_spider_state(self, spider_id: int) -> SpiderState:
        return self._get_sri(spider_id).state


    async def finish(self):
        """Scrape job finished successfully!
        clear the registry.
        """
        async with lock:
            # await self.increase_scrape_count(scrape_finished=True)
            self.clear()
            logger.info("Scraping successful")
            logger.info("Scraping registry cleared")


    def clear(self):
        """Sets all the registry's values to defaults, thus clearing the registry."""
        self.registry = {}
        self.spiders = None
        return


scraping_registry = ScrapingRegistry()
