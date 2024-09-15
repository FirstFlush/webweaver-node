from typing import TYPE_CHECKING
from webweaver_node.core.common.enums import LogLevel
from webweaver_node.core.exceptions import WebScrapingError
from webweaver_node.core.webscraping.middleware.generic_response import GenericResponse

if TYPE_CHECKING:
    from webweaver_node.core.webscraping.spiders.spider_base import SpiderAPI
    from webweaver_node.core.webscraping.spiders.spider_page import RequestContextInterface


class MiddlewareBase:
    """Base class for all middleware modules.

    Middleware modules receive the GenericResponse object and operate on it by
    subclassing the handle_response() method.

    Middleware modules are capable of accessing the Manager via the MiddlewareManagerInterface,
    which in turn allows the middleware module to access the spider's SpiderInterface. This is
    especially important for logging to the spider's module-level log files.
    """
    def __init__(
            self, 
            spider_api:"SpiderAPI",
            request_interface:"RequestContextInterface",
            response:GenericResponse,
    ):
        self.spider_api = spider_api
        self.request_interface = request_interface
        self.response = response


    def log_warning_and_continue(self, msg:str):
        self.spider_api.log(msg, level=LogLevel.WARNING)


    def log_error_and_continue(self, msg:str):
        self.spider_api.log(msg)


    def log(self, e:WebScrapingError=None, level:LogLevel=LogLevel.ERROR):
        self.spider_api.log(e, level)

    async def handle_response(response:GenericResponse):
        raise NotImplementedError("Middleware subclass has no handle_response method!")