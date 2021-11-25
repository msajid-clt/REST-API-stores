import datetime, os
from functools import wraps
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, verify_jwt_in_request, get_current_user
)
from flask_restful import Api

from resources.user import (
    UserRegister, User, UserLogin, 
    UserLogout, UserCheck, TokenRefresh,
)
from resources.item import ItemManager, ItemList
from resources.store import StoreManager, StoreList
from models.user import UserModel
from redis_manager import redis_manager

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKENS_CHECKS'] = ['access', 'refresh']
app.config['JWT_SECRET_KEY'] = 'msdev'

# DATABASE_URI
database_uri = os.environ.get("DATABASE_URL", "sqlite:///data.db")  # or other relevant config var 
if database_uri.startswith("postgres://"):     
    database_uri = database_uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

app.secret_key = 'VerySecret'
api = Api(app)

# config JWT to expire within half an hour
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds=30)

#use jwt
#jwt = JWT(app, authenticate, identity_function) #/auth
#use jwt_extended
jwt = JWTManager(app)

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    user = UserModel.find_by_id(identity)
    if user.username == "admin":
        return {"is_admin" : True}  
    return {"is_admin" : False}  

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token_in_blocklist = redis_manager.jwt_redis_blocklist.get(jti)
    return  token_in_blocklist is not None


@jwt.user_identity_loader
def user_identity_callback(user):
    return user

# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_payload):
    identity = jwt_payload["sub"]
    user = UserModel.find_by_id(identity)
    # if user:
    #     if user.username == "rolf":
    #         user["role"] = "admin"
    #     else:
    #         user[0]["role"] = "normal"
    #     return user[0]
    return user

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description' : 'The token has expired',
        'error' : 'Token expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description' : 'Signature verification failed',
        'error' : 'Token is invalid'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description' : 'Request does not contain an access token',
        'error' : 'Authorization required'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({
        'description' : 'The access token is not fresh',
        'error' : 'Fresh Token required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description' : 'The access token has been revoked',
        'error' : 'Access Token revoked'
    }), 401

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        if user["username"] == "rolf":
            return fn(*args, **kwargs)

        return jsonify(msg='Admins only!'), 403
    return wrapper

@app.route("/admin_only")
@jwt_required
@admin_required
def admin_only():
    return ""

api.add_resource(ItemManager, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreManager, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<string:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(UserCheck, '/who_am_i')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    @app.before_first_request
    def create_tables():
        db.create_all()
    app.run(port=5000, debug=True)