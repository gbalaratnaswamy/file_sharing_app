import encryption.encryption as e
# import jwt
# tok = jwt.encode({"email": "nono"},"enoen")
# print(tok)
# try:
#     print(e.decode_token_jwt(tok))
# except jwt.exceptions.InvalidSignatureError:
#     print("invalid")


# print(e.decode_token_jwt(b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImdiYWxhcmF0bmFzd2FteUBnbWFpbC5jb20iLCJuYW1lIjpudWxsfQ.0yrpZ82q8J931juP5JMcwgNAx4cZzD-1UbEJfqathD8')
from db.models import File
from bson import ObjectId
a=(File.get_all_file(ObjectId("5f590a0440d5ea6db9c13923")))
print(a)
for item in a:
    print(item.get_is_active())