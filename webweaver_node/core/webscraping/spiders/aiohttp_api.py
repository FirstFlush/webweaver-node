import aiohttp
import asyncio
import logging
import os
import time
from typing import TYPE_CHECKING

from webweaver_node.core.common.enums import LogLevel

logger = logging.getLogger('scrapings')


if TYPE_CHECKING:
    from webweaver_node.core.webscraping.spiders.spider_base import Spider
    from webweaver_node.core.webscraping.spiders.soup_base import SpiderTag

class AiohttpAPI:
    """Asynchronous functionality for the base Spider class with aiohttp package"""

    def __init__(self, spider:"Spider"):
        self.spider = spider
        self.session = aiohttp.ClientSession()


    async def test_scrape(self, url:str, outfile_name:str=None):
        """Scrape the page and save the resulting HTML to a file.
        This method is to help troubleshoot problems when we aren't
        receiving the HTML from the server that we expect.
        
        *NOTE This method makes an HTTP Request
        """
        logger.info(f'Sending request to {url}')
        res = await self.get(url)
        logger.info(f'Response status: {res.status}')
        if res.status == 200:
            soup = self.spider.get_soup(await res.text())
            if not outfile_name:
                outfile_name = "aio_test_scrape.html"
            else:
                if outfile_name[-5:] != ".html":
                    outfile_name = f"{outfile_name}.html"
            with open(outfile_name, 'w') as f:
                f.write(soup.prettify())
            logger.info(f'Saved response to {os.getcwd()}/{outfile_name}')
        else:
            logger.info('Did not save file due to non 200 status code')


    async def scrape_image(self, image_element:"SpiderTag", use_proxy:bool=True, src_attribute:str='src', raise_exc:bool=True) -> bytes | None:
        """Scrape the binary data tha represents the product image
        
        *NOTE This method makes an HTTP request.
        """
        image_src_url = self.spider.clean_url(image_element.get(src_attribute), raise_exc)
        if image_src_url:
            response = await self.get(image_src_url, use_proxy=use_proxy)
            if response.status == 200:
                return await response.read()


    async def scrape_image_url(self, url:str, use_proxy:bool=True, raise_exc:bool=True) -> bytes | None:
        """Scrape the binary data tha represents the product image
        
        *NOTE This method makes an HTTP request.
        """
        url = self.spider.clean_url(url, raise_exc)
        response = await self.get(url, use_proxy=use_proxy)
        if response.status == 200:
            image_chunks = []
            async for chunk in response.content.iter_chunked(1024):  # Adjust chunk size as needed
                image_chunks.append(chunk)
            image = b''.join(image_chunks)
            return image
            # return await response.read()


    async def get_or_error(self, url:str, use_proxy:bool=True, **kwargs) -> aiohttp.ClientResponse:
        res = await self.get(url, use_proxy=use_proxy, **kwargs)
        if res.status != 200:
            raise self.spider.errors.SpiderHttpError(f"{url}, use_proxy={use_proxy}")
        return res


    async def get(self, url:str, use_proxy:bool=True, **kwargs) -> aiohttp.ClientResponse:
        """Sends an HTTP request using aiohttp's session.get() method.
        The difference is this function will automatically use the proxy and
        will also automatically randomize the headers (well, the UA of the headers).
        """
        if use_proxy:
            proxy_retry_base_time = 2
            max_wait_time = 60
            # max_wait_time = 3
            retry_count = 0
            while True:
                try:
                    proxy = await self.spider.get_proxy(stateful=False)
                    res = await self.session.get(
                        url=url,
                        proxy = proxy.full_endpoint,
                        headers = self.spider.random_headers(),
                        **kwargs
                    )
                except aiohttp.ClientConnectionError as error:
                    msg = f"{error.__class__.__name__}: '{self.spider.spider_asset.spider_name}' URL: '{url}'  RETRYING..."
                    self.spider.log(
                        e = error,
                        level = LogLevel.WARNING,
                        msg = msg
                    )
                    retry_count += 1
                    exponential_backoff = proxy_retry_base_time * (2 ** retry_count)
                    if exponential_backoff > max_wait_time:
                        self.spider.log(e=error)
                        raise error
                    else:
                        logger.info(msg)
                        logger.info(f"Retrying in {exponential_backoff} seconds...")
                        await asyncio.sleep(exponential_backoff) 
                    continue

                except (aiohttp.ClientHttpProxyError, aiohttp.ClientPayloadError, ConnectionResetError) as error:
                    self.spider.log(
                        e = error,
                        level = LogLevel.WARNING,
                        msg = f"{error.__class__.__name__} '{self.spider.spider_asset.spider_name}' URL: '{url} Retrying..."
                    )
                    retry_count += 1
                    exponential_backoff = proxy_retry_base_time * (2 ** retry_count)
                    if exponential_backoff > max_wait_time:
                        self.spider.log(e=error)
                        raise error
                    else:
                        time.sleep(exponential_backoff) #synchronous otherwise other connections will keep trying.
                    continue

                else: 
                    break

        else:
            res = await self.session.get(url=url, **kwargs)
        return res


    async def close_session(self):
        await self.session.close()
