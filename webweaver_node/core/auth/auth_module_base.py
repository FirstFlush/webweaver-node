from abc import ABC, abstractmethod
import logging
from fastapi import Request, Depends, HTTPException
from webweaver_node.core.auth.exceptions import AuthModuleNotFound
# from auth.models import User


logger = logging.getLogger('auth')


class AuthModuleBase(ABC):

    def __init__(self, request:Request):
        self.request = request


    @abstractmethod
    async def authenticate(self):
        """Overwrite this method for custom authentication logic 
        for each AuthModule.
        """
        logger.error(repr(AuthModuleNotFound(self.__class__.__name__)))
        raise HTTPException(status_code=401, detail="Access denied")
        

    def deny(self, message:str="Access denied"):
        raise HTTPException(status_code=401, detail=message)