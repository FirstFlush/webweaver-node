from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from webweaver_node.core.routes.launch_routes.routes import router as router_scrape
from webweaver_node.core.routes.auth_routes.routes_auth import router as router_auth
from webweaver_node.core.config import POSTGRES_DB, all_models, scraping_logger, STATIC_DIR


# Initialize FastAPI & Routes
# =================================================
app = FastAPI()
app.include_router(router_scrape, prefix="/scrape", tags=["webscraping"])
app.include_router(router_auth, prefix="/auth", tags=["authentication"])


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static") 
# NOTE: first param on app.mount() corresponds to the href on HTML <link> elements!
# ie: <link rel="stylesheet" href="/webweaver/css/base.css">

app.mount("/media", StaticFiles(directory="media"), name="media")


# Initialize Database
# =================================================
TORTOISE_ORM = {
    'connections': {
        # 'default': config.POSTGRES_DB
        'default': POSTGRES_DB
    },
    'apps': {
        'models': {
            # 'models': config.all_models,
            'models': all_models,
            'default_connection': 'default',
        },
    },
}

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,  # Automatically create database tables for Tortoise models on startup.
    add_exception_handlers=True,
)


scraping_logger.debug("Synced successfully with Tortoise-ORM")