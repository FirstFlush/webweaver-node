import importlib
import logging
import toml
from pathlib import Path
from typing import Awaitable, List, TYPE_CHECKING

from tortoise.models import Model
from tortoise import fields

from webweaver_node.core.common.fields import DomainField
from webweaver_node.core.config import SCRAPING_MODULES, SCRAPING_MODULES_DIR
from webweaver_node.core.exceptions import (
    SpiderModuleNotFound, 
    PipelineModuleNotFound,
    ConfigModuleNotFound,
    ConfigModelsNotFound,
)
if TYPE_CHECKING:
    from webweaver_node.core.webscraping.spiders.spider_base import Spider
    from webweaver_node.core.webscraping.pipelines.pipeline_base import Pipeline


logger = logging.getLogger('scraping')


class SpiderAsset(Model):

    spider_name         = fields.CharField(max_length=255)
    domain              = DomainField(max_length=255)
    description         = fields.TextField(max_length=2048)
    is_active           = fields.BooleanField(default=True)
    # is_search_string    = fields.BooleanField(default=False)
    date_modified       = fields.DatetimeField(auto_now=True)
    date_created        = fields.DatetimeField(auto_now_add=True)


    @property
    def module_config(self) -> dict:
        """Returns the spider's config.toml file data as a dict."""
        config_path = self.module_dir_path() / Path("config.toml")
        try:
            return toml.load(config_path)
        except (FileNotFoundError, toml.TomlDecodeError, TypeError) as e:
            logger.error(ConfigModuleNotFound(e))
            raise ConfigModuleNotFound(e)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._module_config = None


    def __str__(self):
        return self.spider_name

    
    def module_path(self) -> str:
        """Retrieve the full MODULE path to the spider's scraping module"""
        return f"{SCRAPING_MODULES}.{self.spider_name.lower()}"
    

    def module_dir_path(self) -> Path:
        """Retrieve the full DIRECTORY path of the spider's scraping module"""
        return SCRAPING_MODULES_DIR / Path(self.spider_name.lower())


    def table_names(self) -> list:
        """Retrieve the table names in the module's .toml config file."""
        try:
            tables = self.module_config['models']['table_names']
        except KeyError:
            pass
        else:    
            if isinstance(tables, list):            
                if len(tables) < 1:
                    logger.warning(f"{self.spider_name}: No models found in config.toml")
                return tables

        raise ConfigModelsNotFound(self.spider_name)
        

    def get_spider(self) -> "Spider" | None:
        """Retrieve the Spider subclass, based on naming convention."""
        SpiderClass = None
        module_name = f"{SCRAPING_MODULES}.{self.spider_name.lower()}.spider"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            logger.error(repr(SpiderModuleNotFound(self.spider_name)))
        else:
            try:
                SpiderClass = getattr(module, f"{self.spider_name}Spider")
            except AttributeError:
                pass

        return SpiderClass


    def get_pipeline(self) -> "Pipeline" | None:
        """Retrieve the Pipeline subclass, based on the same 
        naming convention as self.get_spider()
        """
        PipelineClass = None
        module_name = f"{SCRAPING_MODULES}.{self.spider_name.lower()}.pipeline"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            logger.error(repr(PipelineModuleNotFound(self.spider_name)))
        else:
            try:
                PipelineClass = getattr(module, f"{self.spider_name}Pipeline")
            except AttributeError:
                pass

        return PipelineClass


    async def activate(self):
        """Activates the spider so it can be loaded into the SpiderLauncher"""
        self.is_active = True
        await self.save()
        return


    async def deactivate(self):
        """Deactivates the spider so it will not be loaded into the SpiderLauncher"""
        self.is_active = False
        await self.save()
        return


    async def failures(self) -> Awaitable[List["SpiderFailure"]]:
        return await self.spider_failures.all()
        

    async def error_count(self) -> int:
        """Get number of errors this spider has generated."""
        return await SpiderFailure.filter(spider_id=self).count()


    def file_path(self, modules_path:str) -> str:
        """Returns the full file path, assuming the naming convention is:
        Class   SpiderName
        File    spidername.py
        """
        path = f"{modules_path}/{self.spider_name.lower()}.py"
        return path


    @classmethod
    async def get_active(cls) -> Awaitable[List["SpiderAsset"]]:
        """Returns all active Spider assets"""
        spiders = await cls.filter(is_active=True)
        return spiders
    

    @classmethod
    async def get_spiders_from_list_of_names(
        cls, 
        spider_names:list[str]
    ) -> Awaitable[List["SpiderAsset"]]:
        """Returns the active SpiderAsset objects from a list of spider names."""
        return await cls.filter(spider_name__in=spider_names, is_active=True)


    @classmethod
    async def compare_names_from_list(
        cls, 
        spider_names:list[str], 
        fetched_spiders:list["SpiderAsset"] = None
    ) -> bool:
        """Compares fetched spider names with a given list of spider names. 
        If no fetched spiders are provided, the spiders will be fetched from 
        the DB based on the names provided in the list.

        Ultimately this function is checking if all spiders on the list are indeed
        present and active in our DB. This is used when creating a new campaign.
        """
        if fetched_spiders is None:
            fetched_spiders = await cls.get_spiders_from_names(spider_names)
        fetched_spider_names = [spider.spider_name for spider in fetched_spiders]
        return bool(set(fetched_spider_names) == set(spider_names))


class SpiderFailure(Model):

    spider_id = fields.ForeignKeyField('models.SpiderAsset', related_name='spider_failures', on_delete=fields.CASCADE)
    error_type = fields.CharField(max_length=255)
    traceback = fields.TextField(null=True)
    date_logged = fields.DatetimeField(auto_now_add=True)
