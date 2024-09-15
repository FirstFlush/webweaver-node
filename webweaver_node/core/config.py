import logging
import os
from dotenv import load_dotenv
from pathlib import Path
from termcolor import colored

from webweaver_node.core.mapping import RouteMap


# Proxy Settings
# =================================================
USE_PROXY = False

PROXY_URL = 'dc.smartproxy.com'
PROXY_ROTATING_PORT = 10000
PROXY_STATIC_PORT_RANGE = (10001, 10100)

# Debug Status
# =================================================
DEBUG = True


# Directory Paths
# =================================================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(ROOT_DIR, "log")
SCRAPING_MODULES_DIR = os.path.join(ROOT_DIR, "scraping_modules")

# Env Vars & Constants
# =================================================
load_dotenv('.env')
ENVIRONMENT = os.getenv('ENV_STATUS')
if ENVIRONMENT == "prod":
    load_dotenv(".env.prod")
else:
    load_dotenv(".env.dev")
HTTP_TIMEOUT = 5
SPIDER_MAX_ERRORS = 5
ACCEPTABLE_SPIDER_DURATION = 10.0 #seconds
SPIDER_DATA_BATCH_SIZE = 1
SCRAPING_MODULES = Path("webweaver.scraping_modules")
SENTINEL = "__SENTINEL_VALUE__"  # value passed into async Queue to stop PipelineListener from listening.
RETURN_EXCEPTIONS = os.getenv("RETURN_EXCEPTIONS")  # for asyncio.gather() calls in SpiderLauncher

# DB Config:
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
POSTGRES_DB = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Requests:
REQUEST_WAIT_MAX = 3600  # 1 hour
REQUEST_WAIT_BASE = 30  # 30 seconds

# Semaphores (not yet implemented):
SEMAPHORE_COUNT = 5
PLAYWRIGHT_COUNT = 5

# Logging
# ====================================================
class ColoredFormatter(logging.Formatter):

    COLORS = {
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red',
        'DEBUG': 'blue',
        'INFO': 'green'
    }

    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, 'white')
        colored_levelname = colored(record.levelname, color)
        return log_message.replace(record.levelname, colored_levelname)


scraping_logger = logging.getLogger('scraping')
sending_logger = logging.getLogger('sending')
auth_logger = logging.getLogger('auth')

if DEBUG == True:
    auth_logger.setLevel(logging.DEBUG)
    scraping_logger.setLevel(logging.DEBUG)
    sending_logger.setLevel(logging.DEBUG)
else:
    auth_logger.setLevel(logging.INFO)
    scraping_logger.setLevel(logging.INFO)
    sending_logger.setLevel(logging.INFO)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_formatter = ColoredFormatter('%(levelname)-10s%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(stream_formatter)

auth_handler = logging.FileHandler(f"{LOG_DIR}/auth.log")
auth_handler.setLevel(logging.INFO)
auth_handler.setFormatter(log_formatter)

auth_logger.addHandler(auth_handler)
auth_logger.addHandler(stream_handler)

scraping_handler = logging.FileHandler(f"{LOG_DIR}/scraping.log")
scraping_handler.setLevel(logging.INFO)
scraping_handler.setFormatter(log_formatter)

scraping_logger.addHandler(scraping_handler)
scraping_logger.addHandler(stream_handler)

sending_handler = logging.FileHandler(f"{LOG_DIR}/sending.log")
sending_handler.setLevel(logging.INFO)
sending_handler.setFormatter(log_formatter)

sending_logger.addHandler(sending_handler)
sending_logger.addHandler(stream_handler)


# Middlewares
# =================================================

REQUEST_MIDDLEWARES = [

]

RESPONSE_MIDDLEWARES = [
    'webweaver.webscraping.middleware.modules.status_code.StatusCodeMiddleware',
]


# Models
# =================================================
core_models = [
    'aerich.models',
    'webweaver.auth.models',
    'webweaver.project.models',
    # 'webweaver.webscraping.models',
    'webweaver.webscraping.campaigns.models',
    # 'webweaver.webscraping.matching.models',
    'webweaver.webscraping.spiders.models',
    # 'webweaver.data.cannabis.models',
]

all_models = core_models

# Routes
# =================================================
ROUTES = RouteMap


# # Static Files
# # =================================================
# STATIC_DIR = "frontend/static"


# # Templates
# # =================================================
# TEMPLATES_DIR = "frontend/templates"
# TEMPLATES = TemplateMap

# templates = Jinja2Templates(directory="frontend/templates")
# templates.env.globals["url"] = ROUTES

