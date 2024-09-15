import logging

from fastapi import Request, Depends

from webweaver_node.core.auth.auth_modules.api_key_auth import ApiKeyAuthModule
from webweaver_node.core.auth.authorization import Authorization
from webweaver_node.core.auth.auth_modules.hmac_auth import HmacAuthModule
from webweaver_node.core.auth.models import User


logger = logging.getLogger('auth')


class Authenticators:

    @classmethod
    async def key_auth(cls, request:Request) -> User:
        akm = ApiKeyAuthModule(request)
        user = await akm.authenticate()
        return user

    @classmethod
    async def hmac_auth(cls, request:Request) -> User:
        hm = HmacAuthModule(request)
        user = await hm.authenticate()
        return user



class AuthRoute:
    """Static methods in this class are what actually get called in the "Depends()"
    param of each route. These static methods are the point of entry for our auth module,
    via the routes the user is attempting to access.
    """
    @staticmethod
    async def spider_launch(user: User = Depends(Authenticators.key_auth)) -> User:
        """spider launch endpoint"""
        perm = Authorization()
        await perm.has_permissions(user, perm.STAFF, perm.SPIDER_LAUNCH)
        return user
    

    @staticmethod
    async def create_campaign(user: User = Depends(Authenticators.key_auth)) -> User:
        """Create a new scraping campaign"""
        perm = Authorization()
        await perm.has_permissions(user, perm.STAFF, perm.CREATE_CAMPAIGN)
        return user


    @staticmethod
    async def staff_only(user: User = Depends(Authenticators.key_auth)) -> User:
        """Staff members only"""   
        perm = Authorization()
        await perm.has_permissions(user, perm.STAFF)
        return user


    @staticmethod
    async def admin_only(user: User = Depends(Authenticators.key_auth)) -> User:
        """Admin level only"""   
        perm = Authorization()
        await perm.has_permissions(user, perm.ADMIN)
        
        return user


