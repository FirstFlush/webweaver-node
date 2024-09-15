import logging
from pathlib import Path
from webweaver_node.core.common.enums import LogLevel
from webweaver_node.core.exceptions import WebScrapingError


class SpiderModuleLog:
    """Module-level logging for a specific spider's webscraping errors"""
    def __init__(self, module_path:Path, spider_name:str):
        self.logger = logging.getLogger(spider_name.lower())
        self.logger_traceback = logging.getLogger(f"{spider_name.lower()}_traceback")
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        module_handler = logging.FileHandler(module_path / Path(f"{spider_name.lower()}.log"))
        module_handler.setLevel(logging.DEBUG)
        module_handler.setFormatter(log_formatter)
        traceback_handler = logging.FileHandler(module_path / Path(f"{spider_name.lower()}_traceback.log"))
        traceback_handler.setLevel(logging.DEBUG)
        traceback_handler.setFormatter(log_formatter)
        self.logger.addHandler(module_handler)
        self.logger_traceback.addHandler(traceback_handler)
    

    def log(self, e:WebScrapingError=None, level:LogLevel=LogLevel.ERROR, msg:str=None):
        """Logging method if individual spiders need to log an error."""
        if not msg:
            msg = f"{repr(e)}"
        match level:
            case LogLevel.EXCEPTION:
                self.logger.exception(msg)
            case LogLevel.CRITICAL:
                self.logger.critical(msg)
                self.logger_traceback.exception(msg)
            case LogLevel.ERROR:
                self.logger.error(msg)
                self.logger_traceback.exception(msg)
            case LogLevel.WARNING:
                self.logger.warning(msg)
            case LogLevel.INFO:
                self.logger.info(msg)
            case LogLevel.DEBUG:
                self.logger.debug(msg)
            case _:
                self.logger.critical(f"Unexpected log level: {level}. Original error: {msg}")
                self.logger_traceback.exception(f"{msg}")
        return
