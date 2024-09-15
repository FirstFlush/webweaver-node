
from playwright.async_api import Response as ResponsePlaywright
from aiohttp import ClientResponse as ResponseAiohttp

class GenericResponse:
    """This class acts as an adapter for transforming Playwright's Response object
    and aiohttp's ClientResponse into a standard object that can be operated on
    by the middleware classes.
    """
    def __init__(self, url:str, status_code:int, headers:dict):
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self.retry_after = None


    @classmethod
    def from_playwright(cls, response:ResponsePlaywright) -> "GenericResponse":
        """Factory method for creating GenericResponse from Playwright Response object"""
        return cls(
            url=response.url,
            status_code=response.status,
            headers=response.headers
        )
    
    @classmethod
    def from_aiohttp(cls, response:ResponseAiohttp) -> "GenericResponse":
        "Factor method for creating GenericResponse from aiohttp ClientResponse object"
        return cls(
            url=response.url,
            status_code=response.status,
            headers=response.headers
        )