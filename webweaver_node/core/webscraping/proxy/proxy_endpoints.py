import os
from webweaver_node.core.config import PROXY_ROTATING_PORT, PROXY_URL, PROXY_STATIC_PORT_RANGE

class ProxyEndpoints:

    def __init__(self):
        self.PROXY_USER = os.environ.get('PROXY_USER')
        self.PROXY_PASS = os.environ.get('PROXY_PASS')
        self.rotating = f"{PROXY_URL}:{PROXY_ROTATING_PORT}"
        self.sticky = [f"{PROXY_URL}:{i}" for i in range(PROXY_ROTATING_PORT[0], PROXY_ROTATING_PORT[1]+1)]
        self.in_use = set()