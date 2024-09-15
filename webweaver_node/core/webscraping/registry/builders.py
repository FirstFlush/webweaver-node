import logging

# from common.utils import instance_to_dict

from webweaver_node.core.exceptions import SpiderAssetNotFound
from webweaver_node.core.schema.pydantic_schemas import LaunchSpiderSchema
from webweaver_node.core.webscraping.spiders.models import SpiderAsset


logger = logging.getLogger('scraping')



class RegistryBuilder:

    def __init__(self, launch_data:LaunchSpiderSchema):
        self.spider_details = []
        self.spider_id = launch_data.id
        self.spider_asset:SpiderAsset = None
        self.params = {}
        params_list = [param.model_dump() for param in launch_data.params]
        for param in params_list:
            self.params[param['param_name']] = param['param_value']

    async def initialize_solo_scrape(self):
        self.spider_asset = await self._get_spider_asset()
        self.build_spider_details()

    def build_spider_details(self):
        d = {
            'spider': self.spider_asset,
            'params': self.params
        }
        self.spider_details.append(d)

    async def _get_spider_asset(self) -> SpiderAsset:
        """Returns the SpiderAsset for scraping."""
        spider_asset = await SpiderAsset.get_or_none(id=self.spider_id)
        if spider_asset is None:
            msg = f"SpiderAssetNotFound: SingleSpiderScrapeBuilder could not find spider asset with id `{self.spider_id}`"
            logger.error(msg, exc_info=True)
            raise SpiderAssetNotFound(msg)
        return spider_asset

