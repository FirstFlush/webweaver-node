import os
import random
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from webweaver_node.core.webscraping.proxy.proxy_manager import SessionProxyManagerInterface


class ProxySession:
    """This class governs the communication with the proxy service endpoint.
    If we have 100 IPs to scrape with then up to 100 ProxySessions will be made. 
    This approach allows some proxy sessions to be stateless and some to be stateful.
    Stateful ProxySession objects have a RequestContext object to manage state between
    requests.

    ProxySessions can also share state via the methods in their self.manager_interface
    class, which is an interface for getting/setting state in the ProxyManager object
    that created them all.
    """
    def __init__(
            self, 
            endpoint:str,
            manager_interface:"SessionProxyManagerInterface", 
            # request_context:Optional[RequestContext],
            ):
        self.endpoint = endpoint
        self.manager_interface = manager_interface
        # self.request_context = request_context


    @property
    def full_endpoint(self) -> str:
        """Includes the username/pass in the proxy endpoint"""
        return f"http://{os.getenv('PROXY_USER')}:{os.getenv('PROXY_PASS')}@{self.endpoint}"


    async def release(self):
        """Releases the proxy endpoint so that other proxysession objects
        may use it.
        """
        await self.manager_interface.release_endpoint(self.endpoint)
        return

    
