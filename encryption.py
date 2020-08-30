import hashlib
import random
import string
from cfg import COOKIE_LENGTH


def encrypt_string(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


def generate_string(length):
    ascii_letters = string.ascii_lowercase
    random_string = ''.join(random.choice(ascii_letters) for i in range(length))
    return random_string


def create_cookie_auth(collection, length=COOKIE_LENGTH):
    random_string = generate_string(length)
    if collection.find_one({"token": encrypt_string(random_string)}) is None:
        return random_string
    return create_cookie_auth(collection, length)
