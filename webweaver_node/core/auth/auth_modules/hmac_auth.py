from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, HTTPDigest

from tortoise.exceptions import DoesNotExist, OperationalError

from webweaver_node.auth.exceptions import UserInvalid, UserValidKeyInvalid
from webweaver_node.auth.models import User
from webweaver_node.auth.auth_module_base import AuthModuleBase



class HmacAuthModule(AuthModuleBase):
    pass