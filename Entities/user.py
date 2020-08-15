from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)
from passlib.apps import custom_app_context as pwd_context
from enum import Enum


# All permissions that available for a user: 1 - regular user, 2 - moderator user, 3 - ROOT
# moderator users can be intervene in the conversations, give alerts and change configurations
# ROOT user can control the permissions of the other users, grant users the moderator permission
class Permission(Enum):
    USER = 1
    MODERATOR = 2
    ROOT = 3


class User:

    def __init__(self, *args, **kwargs):
        self._id = kwargs.get('user_id', "")
        self.user_name = kwargs.get('user_name', "")
        self.password_hash = kwargs.get('password', "")
        self.first_name = kwargs.get('first_name', "")
        self.last_name = kwargs.get('last_name', "")
        self.permission = kwargs.get('permission', Permission.USER.value)

    def get_user_id(self):
        return self._id

    def get_user_name(self):
        return self.user_name

    def get_password(self):
        return self.password_hash

    def set_password(self, password):
        self.password_hash = password

    def get_first_name(self):
        return self.first_name

    def set_first_name(self, first_name):
        self.first_name = first_name

    def get_last_name(self):
        return self.last_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def get_permission(self):
        return self.permission

    def set_permission(self, permission):
        self.permission = permission

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, secret_key, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.user_name})

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "password_hash": self.password_hash,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "permission": self.permission
        }
