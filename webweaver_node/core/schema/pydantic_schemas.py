from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class SpiderAssetIdSchema(BaseModel):
    id: int


class ParameterValueSchema(BaseModel):
    value: str


class SpiderParamSchema(BaseModel):
    param_name: str
    param_type: str
    param_description:Optional[str] = None
    param_values: List[ParameterValueSchema]

    @field_validator('param_type', pre=True)
    def transform_enum_to_string(cls, value):
        if isinstance(value, Enum):
            return value.value
        return value


class SpiderParameterSchema(BaseModel):
    param_name: str
    param_type: str
    param_description:Optional[str] = None

    @field_validator('param_type', pre=True)
    def transform_enum_to_string(cls, value):
        if isinstance(value, Enum):
            return value.value
        return value
    

class CreateParamsSchema(BaseModel):
    spider_id: int
    params: List[SpiderParameterSchema]    


class SpiderAssetSchema(BaseModel):
    id: Optional[int] = None
    spider_name: str = Field(..., max_length=255)
    domain: str = Field(..., max_length=255)
    is_active: Optional[bool]
    description: Optional[str] = Field(..., max_length=2048)

    class Config:
        exclude_unset = True


class SpiderAssetDetailSchema(SpiderAssetSchema):
    params: Optional[List[SpiderParameterSchema]]


class SelectParamsSchema(BaseModel):
    spider_name: str
    params: Optional[List[SpiderParameterSchema]]


class ParamKeyValueSchema(BaseModel):
    param_name: str
    param_value: str


class LaunchSpiderSchema(BaseModel):
    id: int
    params: Optional[List[ParamKeyValueSchema]]