from enum import Enum
import importlib
from tortoise import Model
from tortoise.transactions import in_transaction


def import_class_from_string(class_path:str) -> object:
    """Dynamically import a class from a string path."""
    module_name, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def instance_to_dict(instance:Model) -> dict:
    """Convert model instance to dict."""
    return {f: getattr(instance, f) for f in instance._meta.fields_map.keys()}


def _extract_enum_value(data: dict) -> dict:
    """Convert enum objects to their actual values."""
    for key, value in data.items():
        if isinstance(value, Enum):
            data[key] = value.value
    return data


async def populate_table_from_enum(enum:Enum, table:Model, column):
    """Populates the table with the values in the enum.
    *To be used when first initializing the project
    """
    async with in_transaction():
        for _ in enum:
            await table.get_or_create(**{column:enum.value})


def sanitize_name(name:str) -> str:
    """Turns 'Wine & Spirits into WINE_AND_SPIRITS"""
    sanitized = name.replace("&", "and")
    sanitized = ''.join(e for e in sanitized if e.isalnum() or e.isspace())
    sanitized = sanitized.replace(" ", "_").upper()
    return sanitized

# Common viewport sizes for desktop computers
VIEWPORTS = [
    (1440, 900),
    (2560, 1600), 
    (2880, 1800), 
    (3072, 1920),
    (1920, 1080), 
    (2256, 1504),
    (1366, 768),
    (1920, 1080),
    (2560, 1440), 
    (3440, 1440),
    (3840, 2160),
    (1280, 800),
    (1280, 1024),
    (1680, 1050),
    (1920, 1200),
]