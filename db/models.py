from app import mongo
import cfg
from datetime import datetime
from . import errors
from pymongo import ReturnDocument


class __Document(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args)
        for name, value in kwargs:
            setattr(obj, name, value)

        return obj


class User:
    def __init__(self, data: dict):
        self.__data = data

    @classmethod
    def create_user(cls, email: str, password_hash: bytes):
        data = {"email": email,
                "password": password_hash,
                "created_at": datetime.now(),
                "update_at": datetime.now(),
                "last_login": datetime.now(),
                "size_consumed": 0,
                "name": None,
                # "session_id": [0] * cfg.MAX_SESSIONS,
                "pos": 0,
                "max_size": 300 * 1024 * 1024}
        inserted_id = mongo.db[cfg.USER_COLLECTION].insert_one(data)
        data.update({"_id": inserted_id.inserted_id})
        return cls(data)

    @classmethod
    def find_user(cls, query: dict):
        data = mongo.db[cfg.USER_COLLECTION].find_one(query)
        if data is None:
            raise errors.NoUserError
        return cls(data)

    @staticmethod
    def __update_user(query: dict, update: dict):
        update["$set"].update({"updated_at": datetime.now()})
        mongo.db[cfg.USER_COLLECTION].update_one(query, update)

    @staticmethod
    def __update_and_return(query: dict, update: dict) -> dict:
        update["$set"].update({"updated_at": datetime.now()})
        mongo.db[cfg.USER_COLLECTION].update_one(query, update)
        data = mongo.db[cfg.USER_COLLECTION].find_one_and_update(query, update, return_document=ReturnDocument.AFTER)
        return data

    @staticmethod
    def delete_user(query: dict):
        mongo.db[cfg.USER_COLLECTION].delete_one(query)

    def delete(self):
        User.delete_user({"_id": self.__data["_id"]})
        del self

    def get_email(self) -> str:
        return self.__data["email"]

    def get_name(self) -> str:
        return self.__data["name"]

    def get_size(self) -> int:
        return self.__data["size_consumed"]

    def set_size(self, size: int):
        self.__data["size_consumed"] = size
        User.__update_user({"_id": self.__data["_id"]}, {"$set": {"size_consumed": size}})

    def set_name(self, name: str):
        User.__update_user({"_id": self.__data["_id"]}, {"$set": {"name": name}})
        self.__data["name"] = name

    def set_password(self, password_hash: bytes):
        User.__update_user({"_id": self.__data["_id"]}, {"$set": {"password": password_hash}})
        self.__data["password"] = password_hash

    def get_password(self) -> bytes:
        return self.__data["password"]

    def get_id(self):
        return self.__data["_id"]

    @property
    def max_size(self):
        return self.__data["max_size"]

    @max_size.setter
    def max_size(self, value):
        self.__data["max_size"] = value
        self.__update_user({"_id": self.id}, {"$set": {"max_size": value}})

    # def get_session_id(self) -> list:
    #     return self.__data["session_id"]
    #
    # def __get_pos(self):
    #     return self.__data["pos"]
    #
    # def __set_pos(self, value):
    #     self.__data["pos"] = value

    # def set_session_id(self, value: str):
    #     self.__data["session_id"][self.__pos] = value
    #     self.__pos = (self.__pos + 1) // cfg.MAX_SESSIONS
    #     print(self.session_id)
    #     User.__update_user({"_id": self.id}, {"$set": {"session_id": self.__data["session_id"], "pos": self.__pos}})

    name = property(get_name, set_name)
    email = property(get_email)
    id = property(get_id)
    size = property(get_size, set_size)
    password = property(get_password, set_password)

    # __pos = property(__get_pos, __set_pos)
    # session_id = property(get_session_id, set_session_id)

    def add_file(self, file_name: str, size: int, path: str, file_hash):
        return File.create_file(file_name, size, path, file_hash, self.id)

    def remove_file(self, file_id):
        File.remove_file({"_id": file_id, "email": self.id})


class File:
    def __init__(self, data: dict):
        self.__data = data

    @classmethod
    def create_file(cls, file_name: str, size: int, path: str, file_hash, file_type, user_id):
        data = {"file_name": file_name,
                "user_id": user_id,
                "size": size,
                "created_at": datetime.now(),
                "path": path,
                "is_active": True,
                "hash": file_hash,
                "file_type": file_type,
                "downloads": []}
        inserted = mongo.db[cfg.FILES_COLLECTION].insert_one(data)
        data.update({"_id": inserted.inserted_id})
        return cls(data)

    @classmethod
    def find_file(cls, query: dict):
        data = mongo.db[cfg.FILES_COLLECTION].find_one(query)
        if data is None:
            raise errors.NoFileError
        return cls(data)

    @staticmethod
    def remove_file(query):
        mongo.db[cfg.FILES_COLLECTION].delete_one(query)

    def get_downloads(self):
        return self.__data["downloads"]

    def set_download(self, user_id):
        self.__data["downloads"].append(user_id)
        mongo.db[cfg.FILES_COLLECTION].update_one({"_id": self.id},
                                                  {"$push": {"downloads": {"_id": user_id, "time": datetime.now()}}})

    def get_is_active(self):
        return self.__data["is_active"]

    def set_is_active(self, value: bool):
        self.__data["is_active"] = value
        mongo.db[cfg.FILES_COLLECTION].update_one({"_id": self.id},
                                                  {"$set": {"is_active": value}})

    @staticmethod
    def get_all_file(user_id):
        files = mongo.db[cfg.FILES_COLLECTION].find({"user_id": user_id})
        return [File(data) for data in files]

    def get_id(self):
        return self.__data["_id"]

    @property
    def user_id(self):
        return self.__data["user_id"]

    @property
    def file_name(self):
        return self.__data["file_name"]

    @property
    def size(self):
        return self.__data["size"]

    @property
    def path(self):
        return self.__data["path"]

    @property
    def file_type(self):
        return self.__data["file_type"]

    @property
    def created_at(self):
        return self.__data["created_at"]

    active = property(get_is_active, set_is_active)
    id = property(get_id)
    downloads = property(get_downloads, set_download)


class AuthTokens:

    @staticmethod
    def create_token(email, token):
        mongo.db[cfg.AUTH_COLLECTION].insert_one({"email": email,
                                                  "token": token})

    @staticmethod
    def get_token(email, token):
        return mongo.db[cfg.AUTH_COLLECTION].find_one({"email": email,
                                                       "token": token})

    @staticmethod
    def delete_token(token):
        mongo.db[cfg.AUTH_COLLECTION].delete_one({"token": token})

    @staticmethod
    def check_token(token):
        if mongo.db[cfg.AUTH_COLLECTION].find_one({"token": token}) is None:
            return True
        return False
