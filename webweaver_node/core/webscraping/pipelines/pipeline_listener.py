import asyncio
import logging

from webweaver_node.core.config import SENTINEL
from webweaver_node.core.webscraping.spiders.models import SpiderAsset
from webweaver_node.core.webscraping.pipelines.pipeline_base import Pipeline
from webweaver_node.core.webscraping.registry.scraping_registry import scraping_registry
from webweaver_node.core.webscraping.spiders.spider_data import SpiderData


logger = logging.getLogger("scraping")


class PipelineListener:
    """This class handles listening to the queue for scraped data, 
    and then passing it to the appropriate Pineline subclass.
    """

    def __init__(self, queue:asyncio.Queue):
        self.queue = queue
        self.sentinel = SENTINEL


    def get_spider_asset(self, spider_id:int) -> SpiderAsset:
        """Returns the SpiderAsset from the spider registry"""
        return scraping_registry.registry[spider_id].spider_asset


    def get_pipeline_object(self, sa:SpiderAsset, spider_data:SpiderData=None) -> Pipeline | None:
        """Retrieves the pipeline class for the SpiderAsset"""
        pipeline = None
        PipelineClass = sa.get_pipeline()
        if PipelineClass:
            pipeline = PipelineClass(spider_asset=sa, spider_data=spider_data)
        return pipeline


    async def process_pipeline_data(
            self, 
            spider_data:SpiderData
    ):
        spider_asset = self.get_spider_asset(spider_data.spider_id)
        pipeline = self.get_pipeline_object(sa=spider_asset, spider_data=spider_data)
        if pipeline is not None:
            await pipeline.validate_data()
            try:
                await pipeline.save_data()
            except Exception as e:
                logger.error(f"{e.__class__.__name__} ({spider_asset.spider_name})")
                raise
        return


    async def listen(self):
        """Checking the queue for data and instantiating the 
        appropriate Pipeline subclass for processing.
        """
        while True:
            spider_data:SpiderData = await self.queue.get()
            if spider_data == self.sentinel:
                logger.info("Pipeline sentinel value received")
                break
            await self.process_pipeline_data(spider_data)  

        logger.info("Pipeline terminated")
