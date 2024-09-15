from datetime import datetime
import dateutil
import dateutil.parser
from decimal import Decimal, ROUND_HALF_UP
import logging
import re
from urllib.parse import urlparse, urlunparse
import validators


logger = logging.getLogger('scraping')


class PipelineCleaner:
    """Transforms the scraped data to the appropriate data type/format"""


    @staticmethod
    def to_datetime(value:str):
        if isinstance(value, datetime):
            return value        
        try:
            return dateutil.parser.parse(value)
        except Exception as e:
            logger.error(e, exc_info=True)
            raise


    @classmethod
    def to_iso(cls, value:str) -> str:
        """Converts string to iso date format"""
        return cls.to_datetime(value).isoformat()


    @classmethod
    def to_bool(cls, value:str) -> bool:
        """Convert string to bool. Need function for this because
        the string 'False' will evaluate to True.
        """
        if isinstance(value, bool):
            return value
        true_values = {"true", "1", "yes"}
        try:
            if value.lower() in true_values:
                return True
            else:
                return False
        except AttributeError as e:
            raise e(f"Can not convert {value} to bool")


    @classmethod
    def strip_nondigits(cls, value:str) -> int:
        """This will strip out all non-digit characters"""
        return int(''.join([char for char in value if char.isdigit()]))


    @classmethod
    def clean_str(cls, value:str) -> str:
        """Remove weird/funky chars from the string"""
        return value.replace('–','-').replace('—','-').replace("\u200b", "").replace("\u00AD", "").strip()


    @classmethod
    def to_float(cls, value:str) -> float:
        if not value:
            raise AttributeError(f"value `{value}`is of type {type(value)}")
        value = value.replace('$','').replace(',','')
        match = re.search(r'(\d+(\.\d+)?)', value)
        return float(match.group(0))


    @classmethod
    def to_decimal(cls, value:str) -> Decimal|None:
        return Decimal(cls.to_float(value))


    @classmethod
    def to_decimal_rounded(cls, value:str) -> Decimal|None:
        """Automatically rounds the decimal value to 2 places"""
        decimal_value = Decimal(cls.to_float(value))
        if decimal_value or int(decimal_value) == 0:
            return decimal_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


    @classmethod
    def to_decimal_rounded_or_zero(cls, value:str) -> Decimal:
        try:
            decimal_value = cls.to_decimal_rounded(value)
        except AttributeError:
            decimal_value = 0
        return decimal_value if isinstance(decimal_value,  Decimal) else 0


    @classmethod
    def to_float_or_none(cls, value:str) -> float|None:
        try:
            return cls.to_float(value)
        except AttributeError:
            return None


    @classmethod
    def to_int_rounded(cls, value:str) -> int:
        return round(cls.to_float(value))


    @classmethod
    def to_int_or_none(cls, value:str) -> int|None:
        try:
            return int(cls.to_float(value))
        except AttributeError:
            return None


    @classmethod
    def to_int(cls, value:str) -> int:
        return int(cls.to_float(value))


    @classmethod
    def url_domain(cls, url:str) -> str|None:
        """This: https://foo.com/bar/?bleh=1
        becomes: https://foo.com/
        """
        if url is None:
            return ''
        parsed_url = urlparse(url)
        cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
        return cleaned_url


    @classmethod
    def url_domain_dirs(cls, url:str) -> str:
        """This: https://foo.com/bar/?bleh=1
        becomes: https://foo.com/bar/
        """
        validated_url = cls.url_validate(url)
        parsed_url = urlparse(validated_url)
        cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
        return cleaned_url


    @classmethod
    def url_validate(cls, url:str) -> str:
        try:
            validators.url(url)
        except validators.ValidationError:
            raise ValueError(f"Invalid URL: {url}") # raising a basic error type so Pydantic will catch it.
        return url