from fastapi import HTTPException
from webweaver_node.core.webscraping.spiders.models import SpiderAsset


async def get_spider_by_id_or_none(spider_id:int = None) -> SpiderAsset | None:
    spider = await SpiderAsset.get_or_none(id=spider_id)
    if not spider:
        raise HTTPException(status_code=404, detail="Can not retrieve spider.")

    return spider


