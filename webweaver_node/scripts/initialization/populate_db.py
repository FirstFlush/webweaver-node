
from tortoise import Tortoise, run_async
from webscraping.models import Country, ReviewSource
from common.enums import CountryEnum, ReviewSourceEnum
from config import POSTGRES_DB, all_models


class DatabasePopulator:
    """This class helps with initial set-up of the app on a new server. Populates the DB
    with all the base information it needs.
    """

    async def db_init(self):
        await Tortoise.init(db_url=POSTGRES_DB, modules={"models": all_models})
        await Tortoise.generate_schemas()



    # async def populate_review_source(self):
    #     """Populates the Country table with all the country codes"""
    #     # await Tortoise.init(db_url=POSTGRES_DB, modules={"models": all_models})
    #     # await Tortoise.generate_schemas()
    #     await Tortoise.init(db_url=POSTGRES_DB, modules={"models": all_models})
    #     await Tortoise.generate_schemas()
    #     for review_source in ReviewSourceEnum:
    #         await ReviewSource.create(source=review_source.value)

    async def populate_countries(self):
        """Populates the Country table with all the country codes"""
        # await Tortoise.init(db_url=POSTGRES_DB, modules={"models": all_models})
        # await Tortoise.generate_schemas()

        for country in CountryEnum:
            await Country.create(iso_code=country.value)


if __name__ == '__main__':
    dp = DatabasePopulator()
    
    run_async(dp.populate_review_source())
    # run_async(populate_countries())