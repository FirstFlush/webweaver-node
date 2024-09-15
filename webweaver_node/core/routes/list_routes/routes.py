
from fastapi import APIRouter,Depends, HTTPException
from typing import Optional

from webweaver_node.core.auth.authentication import AuthRoute
from webweaver_node.core.auth.models import User
from webweaver_node.core.common.utils import instance_to_dict
from webweaver_node.core.webscraping.spiders.models import SpiderAsset
from webweaver_node.core.schema.pydantic_schemas import (
    SpiderAssetDetailSchema,
    SpiderAssetSchema,
)

router = APIRouter()




@router.get("/listSpiders")
async def list_spiders(spider_id: Optional[int]=None):

    if spider_id:
        sa = await SpiderAsset.get_or_none(id=spider_id).values("id", "spider_name", "domain", "description", "is_active")
        if not sa:
            raise HTTPException(status_code=404, detail="Spider not found")
        # params = await SpiderParameter.filter(spider_id=spider_id).values("param_name", "param_type", "param_description")       
        params = {}
        if params:
            sa['params'] = params
        else:
            sa['params'] = None
        validated_data = SpiderAssetDetailSchema(**sa)
        return validated_data
    else:
        spiders = await SpiderAsset.all()
        return [SpiderAssetSchema(
            id=spider.id,
            spider_name=spider.spider_name, 
            is_active=spider.is_active, 
            domain=spider.domain, 
            description=spider.description
        ) for spider in spiders]
