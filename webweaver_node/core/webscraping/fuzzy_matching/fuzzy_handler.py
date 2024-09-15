from enum import Enum
import re
from rapidfuzz import process, fuzz
from tortoise.models import Model


class FuzzyRegexPatterns:
    preprocess = re.compile(r'[^A-Za-z0-9]+')


class FuzzyHandler:
    """This class handles all fuzzy string matching efforts."""

    REGEX_PATTERNS = FuzzyRegexPatterns

    def __init__(
        self, 
        data_set:list[str], 
        model_map:dict[str, Model]=None,
        preprocess:bool=True
    ):
        if preprocess:
            self.data_set = [self.preprocess(s, self.REGEX_PATTERNS.preprocess) for s in data_set]
        else:
            self.data_set = data_set
        self.model_map = model_map


    @classmethod
    def create_from_list(cls, word_list:list) -> "FuzzyHandler":
        """Factory method to generate a FuzzyHandler from a list of words."""
        if len(word_list) == 0:
            raise IndexError("Length of word_list is 0. Can not generate fuzzy handler with dataset of 0.")

        preprocessed_list = [cls.preprocess(word) for word in word_list]

        return cls(
            data_set = preprocessed_list,
            preprocess = False,
        )


    @classmethod
    def create_from_enum(cls, enum:Enum, exclude_values:set[str] | list[str]) -> "FuzzyHandler":
        """This calls cls.get_handler_from_list but first will process the Enum values
        into a word list. You can pass in certain values you want excluded from the
        word list.
        """
        if isinstance(exclude_values, list):
            exclude_values = set(exclude_values)
        preprocessed_list = [cls.preprocess(attr.value) for attr in enum if attr.value not in exclude_values]
        return cls.get_handler_from_list(
            word_list = preprocessed_list,
        )


    @classmethod
    async def create_from_model(cls, model:Model, field_name:str='name') -> "FuzzyHandler":
        """Factory method to generate a new instance of FuzzyHandler.
        
        Pass in a model class and a field name (column name, technically) and it will generate
        a list of preprocessed strings of that column, ready for fuzzy matching.
        These preprocessed strings will then be mapped to their corresponding model objects.
        The FuzzyHandler will be created with this list of strings and model mapping.
        """
        model_map = {}
        preprocessed_strings = []

        instances = await model.all()
        if not instances:
            raise IndexError(f"No {model.__class__.__name__} instances found to generate fuzzy word list from")

        if not hasattr(instances[0], field_name):
            raise AttributeError(f"{model} has no field name '{field_name}'")

        for instance in instances:
            preprocessed_string = cls.preprocess(s=getattr(instance, field_name))
            model_map[preprocessed_string] = instance
            preprocessed_strings.append(preprocessed_string)

        return cls(
            data_set = preprocessed_strings,
            model_map = model_map,
            preprocess = False,
        )



    @classmethod
    def preprocess(cls, s:str, pattern:re.Pattern=None) -> str:
        """Prepare the string for comparison by applying a preprocessing regex
        which removes all special characeters and spaces. Then the string is
        converted to lowercase.
        """
        if not pattern:
            pattern = cls.REGEX_PATTERNS.preprocess
        return pattern.sub('', s).lower().strip()


    def exact_match(self, s:str, preprocess:bool=True) -> bool:
        """Check if the string is an exact fuzzy match."""
        return bool(self.best_match(s=s, preprocess=preprocess)[1] == 100.0) 


    def best_match(self, s:str, preprocess:bool=True) -> tuple:
        if preprocess:
            s = self.preprocess(s, pattern=self.REGEX_PATTERNS.preprocess)

        return process.extractOne(s, self.data_set, scorer=fuzz.WRatio)