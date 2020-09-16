import cfg
from db.models import AuthTokens
from .encryption import generate_random_string


def generate_auth_token():
    random_string = generate_random_string(cfg.AUTH_TOKEN_LENGTH)
    if AuthTokens.check_token(random_string):
        return random_string
    return generate_auth_token()
