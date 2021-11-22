from werkzeug.security import safe_str_cmp
from models.user import UserModel

def authenticate(username, password):
    result = UserModel.find_by_username(username)
    user = result['user']
    if user and safe_str_cmp(user.password, password):
        return user

def identity(payload):
    user_id = payload['identity']
    result = UserModel.find_by_id(user_id)
    user = result['user']
    return user