from functools import wraps
from typing import Callable
from playwright.async_api import Response as ResponsePlaywright
from aiohttp import ClientResponse as ResponseAiohttp

"""
Decorator(s) to process middleware modules when making 
a request or receiving a response.
"""

def response_middleware(func:Callable):
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> ResponsePlaywright|ResponseAiohttp|None:
        # Call the original function and get the response
        response = await func(self, *args, **kwargs)
        if response is None:
            return response
        # Extract the relevant arguments
        request_interface = kwargs.get('request_interface')
        # request_interface = self.spider_context.request_interface if request_interface else None

        # Perform the desired operation with the extracted arguments
        await self.spider_api.call_middleware(
            response=response, 
            request_interface=request_interface
        )

        # Return the response from the original function
        return response

    return wrapper













# def response_middleware(func:Callable):
#     @wraps(func)
#     async def wrapper(self, *args, **kwargs) -> ResponsePlaywright|ResponseAiohttp|None:
#         # Call the original function and get the response
#         response = await func(self, *args, **kwargs)
#         if response is None:
#             return response
#         # Extract the relevant arguments
#         spider_api = self.spider.spider_api
#         request_interface = kwargs.get('request_interface')
#         # request_interface = self.spider_context.request_interface if request_interface else None

#         # Perform the desired operation with the extracted arguments
#         await self.spider.middleware_api.handle_response(
#             response=response, 
#             spider_api=spider_api,
#             request_interface=request_interface
#         )

#         # Return the response from the original function
#         return response

#     return wrapper