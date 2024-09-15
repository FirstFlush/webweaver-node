import os
from webweaver_node.core.config import SCRAPING_MODULES_DIR
from webweaver_node.core.webscraping.spiders.models import SpiderAsset


def create_spider_module_files(sa:SpiderAsset, spider_type:str):
    """Creates module directory of spider's name with the following files:
        -__init__.py
        -config.toml
        -models.py
        -pipeline.py
        -schema.py
        -spider.py
    """
    module_dir = f'{SCRAPING_MODULES_DIR}/{sa.spider_name.lower()}'
    os.makedirs(module_dir, exist_ok=False)

    with open(f'{module_dir}/__init__.py', 'w') as f:
        pass

    with open(f'{module_dir}/spider.py', 'w') as f:
        f.write(f"from webweaver_node.webscraping.spiders.models import SpiderAsset\n")
        f.write(f"from webweaver_node.webscraping.spiders.spider_base import {spider_type}\n\n\n")
        f.write(f"class {sa.spider_name}Selectors:\n")
        f.write("    ...\n\n\n")
        f.write(f"class {sa.spider_name}Spider({spider_type}):\n\n")
        f.write(f"    selectors = {sa.spider_name}Selectors\n\n")
        f.write("    def __init__(self, spider_asset:SpiderAsset, **kwargs):\n")
        f.write("        super().__init__(spider_asset, **kwargs)\n")
        f.write("        self.url = spider_asset.domain\n\n")
        f.write("    async def run(self):\n")
        f.write(f"        await self.start('chromium', headless=True)\n")
        f.write("        spider_context = await self.new_context()\n")
        f.write("        spider_page = await spider_context.new_spider_page()\n")
        f.write("        res = await spider_page.goto_or_none(self.url)\n")
        f.write("        if res is None:\n")
        f.write("            return\n")

    with open(f'{module_dir}/validation.py', 'w') as f:
        f.write("from pydantic import BaseModel, validator\n\n")
        f.write("from webweaver_node.webscraping.pipelines.pipeline_cleaner import PipelineCleaner\n\n\n")
        f.write(f"class {sa.spider_name}Schema(BaseModel):\n")
        f.write("    # add your validation schema here\n")
        f.write("    ...\n")

    #pipeline imports from schema, so this must come AFTER schema.py is created
    with open(f'{module_dir}/pipeline.py', 'w') as f:
        f.write('from tortoise.transactions import in_transaction\n\n')
        f.write("from webweaver_node.webscraping.pipelines.pipeline_base import Pipeline\n")
        f.write(f"from webweaver_node.scraping_modules.{sa.spider_name.lower()}.validation import {sa.spider_name}Schema\n\n\n")
        f.write(f"class {sa.spider_name}Pipeline(Pipeline):\n\n")
        f.write(f"    schema = {sa.spider_name}Schema\n\n")
        f.write("    async def save_data(self):\n")
        f.write("    # Add your pipeline logic here\n")
        f.write("        pass\n")

    # with open(f'{module_dir}/models.py', 'w') as f:
    #     f.write("from tortoise import fields\n\n")
    #     f.write("from webweaver_node.webscraping.models import ScrapeModel\n\n\n")
    #     f.write("# Create your database models here")

    with open(f'{module_dir}/config.toml', 'w') as f:
        f.write('[spider]\n')
        f.write(f'id = {sa.id}\n')
        f.write(f'spider_name = "{sa.spider_name}"\n')
        f.write(f'domain = "{sa.domain}"\n')
        f.write(f'description = "{sa.description}"\n\n')
        f.write('[models]\n')
        f.write('table_names = []\n\n')
        f.write('[params]\n')
