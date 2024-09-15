from typing import Any, TYPE_CHECKING

from webweaver_node.core.exceptions import WebScrapingError
from webweaver_node.core.common.enums import LogLevel
from webweaver_node.core.webscraping.spiders.spider_page import RequestContextInterface

if TYPE_CHECKING:
    from webweaver_node.core.webscraping.spiders.spider_base import Spider


class SpiderAPI:
    """Currently this class exists as a way for other objects to access 
    the spider's module-level logging functionality.
    More functionalty will be developed
    """
    def __init__(self, spider:"Spider"):
        self.spider = spider

    def log(self, e:WebScrapingError=None, level:LogLevel=LogLevel.ERROR):
        return self.spider.module_logger.log(e, level)

    async def call_middleware(self, response:Any, request_interface:RequestContextInterface=None):
        await self.spider.middleware_api.handle_response(
            response=response, 
            spider_api=self,
            request_interface=request_interface
        )

