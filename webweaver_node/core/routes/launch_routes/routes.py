
import logging
from fastapi import APIRouter, HTTPException

from webweaver_node.core.auth.authentication import AuthRoute
from webweaver_node.core.auth.models import User
from webweaver_node.core.config import USE_PROXY
from webweaver_node.core.schema.pydantic_schemas import (
    SpiderAssetSchema, 
    LaunchSpiderSchema,
)
from webweaver_node.scripts.create_module_files import create_spider_module_files
from webweaver_node.core.webscraping.spiders.models import SpiderAsset
from webweaver_node.core.webscraping.webscrape import WebScrape


logger = logging.getLogger('scraping')
router = APIRouter()


# @router.post("/launch_project")
# # async def launch_spider(launch_data:LaunchSpiderSchema, user:User = Depends((AuthRoute.spider_launch))):
# async def launch_project(launch_data:LaunchSpiderSchema):

#     webscrape = WebScrape(launch_data)
#     await webscrape.scrape()

#     return {"asdffdsa": "fdafdsaf scrapppe"}




@router.post("/launch_spider")
# async def launch_spider(launch_data:LaunchSpiderSchema, user:User = Depends((AuthRoute.spider_launch))):
async def launch_spider(launch_data:LaunchSpiderSchema):

    webscrape = WebScrape(launch_data=launch_data, use_proxy=USE_PROXY)
    await webscrape.scrape()

    return {"asdffdsa": "fdafdsaf scrapppe"}


# @router.post("/test_spider")
# async def test_spider(spider_id: SpiderAssetIdSchema):

#     from playwright.async_api import async_playwright
#     from webscraping.spiders.spider_base import Spider

#     # middleware_manager = MiddlewareManager()
#     proxy_manager = ProxyManager()
#     sa = await SpiderAsset.get_or_none(id=spider_id.id)

#     logger.info(f">>>> Testing {sa.spider_name}Spider")
#     SpiderClass = sa.get_spider()

#     if SpiderClass is not None:
#         p = await async_playwright().start()
#         spider:Spider = SpiderClass(
#             spider_asset=sa,
#             proxy_manager_interface = proxy_manager.proxy_api,
#             p=p,
#             test_env=True
#             )
#         await spider.run()
#         await p.stop()


@router.post("/create_spider")
async def create_spider(data:dict):
    schema = SpiderAssetSchema(**data['spider_asset'])
    spider_type = data['spider_module']['spider_type']
    if await SpiderAsset.exists(spider_name=schema.spider_name):
        raise HTTPException(status_code=400, detail="Failed to create spider")
    spider_data = schema.model_dump()
    del spider_data['id']
    sa = SpiderAsset(**spider_data)
    await sa.save()
    create_spider_module_files(sa, spider_type)

    return {"spider_id": sa.id}



