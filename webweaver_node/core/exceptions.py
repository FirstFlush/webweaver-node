
# Base Exception Classes
# ========================================================
class WebScrapingError(BaseException):
    """Base class for all webscraping errors."""
    pass

class CampaignError(WebScrapingError):
    """Base class for campaign-related errors"""
    pass

class OutFileError(WebScrapingError):
    """Base class for all outfile-related errors"""
    pass

class PipelineError(WebScrapingError):
    """Base class for all pipeline-related errors"""
    pass

class SpiderError(WebScrapingError):
    """Base class for spider-related errors."""
    pass

class SpiderLaunchError(WebScrapingError):
    """Base class for errors related to the spider launcher."""
    def __init__(self, broken_spiders:int):
        self.message = f"{broken_spiders} broken spiders." 

class SpiderAssetError(WebScrapingError):
    """Base class for errors related to spider asset model instances."""
    pass

class SpiderSoupError(SpiderError):
    """Base class for SpiderSoup errors."""
    pass

class MiddlewareException(WebScrapingError):
    """Base class for middleware related errors."""
    pass

class ProxyException(WebScrapingError):
    """Base class for proxy related errors."""
    pass


# General Scraping Exceptions
# ========================================================
class CountryNotFound(WebScrapingError):
    """Raised when a Country object does not match what we wrote. 
    usually an easily-fixed typo on my part.
    """
    def __init__(self, country_name: str):
        self.country_name = country_name
        class_name = self.__class__.__name__
        super().__init__(
            f"{class_name}: Country with name '{self.country_name}' not found."
        )



# Proxy Exceptions
# ========================================================
class ProxyRequestError(ProxyException):
    """raised ProxyRequest fails."""
    pass



# Middleware Exceptions
# ========================================================
class ResponseUnsupported(MiddlewareException):
    """Raised when MiddlewareManager fails to generate GenericRespones object."""
    pass

class RetryAfterHeaderMalformed(MiddlewareException):
    """Raised when the Retry-After header exists but is malformed."""


# Campaign Exceptions
# ========================================================
class CampaignDirNotFound(CampaignError):
    def __init__(self, dir_path:str):
        error_name = self.__class__.__name__
        super().__init__(f"{error_name}: '{dir_path}'")

class CampaignBuilderError(CampaignError):
    """Raised when the CampaignBuilder class fails to build the campaign."""
    pass

# OutFile Exceptions
# ========================================================
class OutFileDataNotFound(OutFileError):
    """Raised when outfile can not create data dictionary for creating outfile.
    Usually means a DB query returned nothing.
    """
    def __init__(self, scrape_job_id:int):
        self.scrape_job_id = scrape_job_id
        super().__init__(f"{self.__class__.__name__} for ScrapeJob '{self.scrape_job_id}'")


class OutFileHookModuleError(OutFileError):
    """Raised when a campaign's outfile_hook.py is found, but
    there is a problem calling the outfile_hook() function.
    Often because of a typo in outfile_hook()'s name or code.
    """
    pass

class OutFileHookInvalidReturn(OutFileError):
    """Raised when a campaign's outfile_hook() returns an 
    invalid data structure.
    """
    pass


class OutFileFormatNotFound(OutFileError):
    """Raised when chosen outfile format is not found 
    in OutFile's FORMAT_MAPPING dict.
    """
    pass


# SpiderAsset Exceptions
# ========================================================

class SpiderAssetNotFound(SpiderAssetError):
    """Raised when SpiderAsset is not found (duh)"""
    pass

class SpiderModuleNotFound(SpiderAssetError):
    """Raised when Spider module can not be found"""
    pass

class PipelineModuleNotFound(SpiderAssetError):
    """Raised when pipeline module can not be found."""
    pass

class ConfigModuleNotFound(BaseException):
    """Raised when the config.toml file is missing."""
    pass
    # def __init__(self, spider_name:str):
        # super().__init__(f"{self.__class__.__name__} ({spider_name}): config.toml file missing")

class ConfigModelsNotFound(SpiderAssetError):
    """Raised when the config.toml file has no models listed."""
    def __init__(self, spider_name:str):
        super().__init__(f"{self.__class__.__name__} ({spider_name}): config.toml models not found or toml file corrupted")

# class ScrapeModuleTableError(SpiderAssetError):
#     """Raised when there is a problem generating the ScrapeModuleTables from 
#     the list of table names in the registry.
#     """
#     pass




# SpiderLauncher Exceptions
# ========================================================
class BrokenSpidersError(SpiderLaunchError):
    """Raised when 1 or more spiders raises an error and fails to scrape."""
    pass

# class SlowSpidersWarning(SpiderLaunchError):
#     """Raised when the spiders take too long to finish their job.
#     Acceptable time to complete is defined in config.py as 
#     ACCEPTABLE_SPIDER_DURATION
#     """
#     pass

# Spider Exceptions
# ========================================================


class SpiderHttpError(SpiderError):
    """Raised when HTTP request returns a status code of
    4xx or 5xx.
    """
    pass

class SpiderRetryTimeout(SpiderError):
    """Raised when a Spider's RetryContext waiting time exceeds the maximum
    amount of time we are willing to wait, as defined by RetryContext's 
    max_wait_time attribute.
    """
    pass

class SpiderTimeoutError(SpiderError):
    """Raised when HTTP request times out"""
    pass

class SpiderPageError(SpiderError):
    """Base exception class for SpiderPage errors."""
    pass

# SpiderPage Exceptions
# ========================================================
class ClickLinkError(SpiderPageError):
    """Raised when a spider_page.clink_link function fails"""
    pass

# SpiderSoup Exceptions
# ========================================================


class ElementNotFound(SpiderSoupError):
    """Raised when an expected element is None"""
    pass


class BadMarkupError(SpiderSoupError):
    """Raised when SpiderSoup instantiation fails."""
    def __init__(self, spider_name, error_details):
        self.spider_name = spider_name
        self.error_details = error_details
        super().__init__(f"{self.spider_name}: {self.error_details}")


# Pipeline Exceptions
# ========================================================

class SchemaValidationError(PipelineError):
    """Raised when cleaned data fails to conform to our Pydantic model schema."""
    pass


class PipelineCleaningError(PipelineError):
    """Raised when a pipeline value can not be converted to its required data type"""
    def __init__(self, value, target_type):
        self.value = value
        self.target_type = target_type
        super().__init__(f"{self.__class__.__name__}(Failed to convert value '{self.value}' to type '{self.target_type.__name__}')")


class SchemaNotFound(PipelineError):
    """Raised when pipeline module did not subclass self.schema"""
    pass


class MethodNotSubclassed(PipelineError):
    """Raised when pipeline module is found, but process_data() method
    or save_data() method has not been subclassed.
    """