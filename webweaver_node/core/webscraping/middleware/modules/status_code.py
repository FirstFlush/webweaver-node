import asyncio
from datetime import datetime, timezone
import email.utils
import math

from webweaver_node.core.config import REQUEST_WAIT_BASE, REQUEST_WAIT_MAX
from webweaver_node.core.exceptions import RetryAfterHeaderMalformed, SpiderRetryTimeout
from webweaver_node.core.webscraping.middleware.middleware_base import MiddlewareBase
# from webscraping.proxy.proxy_base import RequestContext 


#TODO:  retry_time = self.context.calculate_wait_time()
        # -this line no good. need fix


"""
    200 Series (Success):
        200 OK: The request has succeeded. The meaning of the success depends on the HTTP method used.
    300 Series (Redirection):
        301 Moved Permanently: The requested resource has been assigned a new permanent URI.
        302 Found: The requested resource resides temporarily under a different URI.
        304 Not Modified: Indicates that the resource has not been modified since the last request (useful with caching).
    400 Series (Client Errors):
        400 Bad Request: The server cannot or will not process the request due to something perceived as a client error.
        401 Unauthorized: Authentication is required and has failed or has not been provided.
        403 Forbidden: The request was valid, but the server is refusing to respond to it. This can sometimes indicate scraping detection.
        404 Not Found: The requested resource could not be found.
        429 Too Many Requests: This is a clear indicator of throttling. It means the user has sent too many requests in a given amount of time ("rate limiting").
    500 Series (Server Errors):
        500 Internal Server Error: A generic error message when the server encounters an unexpected condition.
        503 Service Unavailable: The server is currently unable to handle the request due to a temporary overloading or maintenance. This can also be a result of rate limiting or throttling, especially if accompanied by a Retry-After header.
"""


class StatusCodeMiddleware(MiddlewareBase):
    """Manages spider behavior for different HTTP status codes.
    Can influence the Spider/SpiderPage's actions by setting the
    following attributes:
        retry_after
    """

    async def handle_response(self):
        """The response is handled based on its status code"""
        wait_time = None
        print('status_code: ', self.response.status_code)
        match self.response.status_code:
            case 200:
                return
            case 400| 401 | 403 | 404:
                msg = f"Status code: {self.response.status_code} from '{self.response.url}'"
                self.log_error_and_continue(msg)
            case 429 | 503:
                msg = f"Status code: {self.response.status_code} from '{self.response.url}'"
                self.log_error_and_continue(msg)
                wait_time = self.wait_time()
            case _:
                msg = f"Unhandled status code: {self.response.status_code} from '{self.response.url}'"
                self.log_warning_and_continue(msg)

        if wait_time:
            if wait_time > REQUEST_WAIT_MAX:
                self.spider_api.log(SpiderRetryTimeout(f"Wait time of {wait_time} seconds is too long"))
                raise SpiderRetryTimeout(f"Wait time of {wait_time} seconds is too long")
            await asyncio.sleep(wait_time)
            self.request_interface.increase_retry_count()


    def calculate_wait_time(self) -> int:
        """Retrieve the wait time with the exponential backoff algorithm,
        based on self.retry_count value.
        """
        wait_time = self.exponential_backoff()
        return wait_time


    def exponential_backoff(self) -> int:
        """Calculates the time (in seconds) this spider/proxy should wait 
        before retrying using an exponential backoff algorithm.
        """
        return REQUEST_WAIT_BASE * (2 ** self.request_interface.retry_count)


    def wait_time(self) -> int:
        """Determines the length of time to wait before retrying"""
        wait_time = 0
        retry_header = self._get_retry_after_header()
        if retry_header:
            try:
                wait_time = self._read_retry_after_header(retry_header)
            except (ValueError, AttributeError) as e:
                self.spider_api.log(RetryAfterHeaderMalformed(f"Retry-After header: {retry_header}"))
        if wait_time == 0:
            wait_time = self.calculate_wait_time()
        return wait_time


    def _read_retry_after_header(self, retry_header:str) -> int:
        """Retry-After headers will typically either be: 
        1.  an int value indicating the number of seconds to wait before making a new request
        2.  a HTTP-date indicating when to make the new request

        Either way, we want to return an int so our spider knows how long to wait (in seconds)
        before sending more requests.
        """
        try:
            if retry_header.isdigit():
                return int(retry_header)
        except AttributeError as e:
            raise AttributeError(f"Invalid Retry-After header format: {retry_header}") from e
        else:
            try:
                retry_time = email.utils.parsedate_to_datetime(retry_header)
                if retry_time.tzinfo is None or retry_time.tzinfo.utcoffset(retry_time) is None:
                    retry_time = retry_time.replace(tzinfo=timezone.utc)
                current_time = datetime.now(tz=timezone.utc)
                delay = math.ceil((retry_time - current_time).total_seconds())
                return max(delay, 0)
            except (TypeError, ValueError, OverflowError) as e:
                raise ValueError(f"Invalid Retry-After header format: {retry_header}") from e


    def _get_retry_after_header(self) -> str|None:
        """Check if there is a `Retry-After` header and return the result."""
        retry_header = self.response.headers.get('Retry-After')
        if retry_header is None:
            retry_header = self.response.headers.get('retry-after')
        try:
            return retry_header.strip()
        except AttributeError:
            return None
