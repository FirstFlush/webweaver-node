
from dataclasses import dataclass
from typing import Any


@dataclass
class SpiderData:
    """Data holding class, serving as the container for 
    scraped data passed from SpiderLauncher to PipelineListener, 
    through the async Queue.
    """
    data: dict[str, Any]
    spider_id: int
