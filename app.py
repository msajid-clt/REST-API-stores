import datetime
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_current_user, verify_jwt_in_request
)
from functools import wraps

from flask_restful import Api

from resources.user import UserRegister
from resources.item import ItemManager, ItemList
from resources.store import StoreManager, StoreList

from models.user import UserModel

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.secret_key = 'VerySecret'
api = Api(app)

# if the authentication endpoint has to be changed to something other than auth
# app.config['JWT_AUTH_URL_RULE'] = '/login'

# config JWT to expire within half an hour
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds=1800)

#jwt = JWTManager(app, authenticate, identity_function) #/auth
jwt = JWTManager(app)

# config JWT auth key name to be 'email' instead of default 'username'
# app.config['JWT_AUTH_USERNAME_KEY'] = 'email'

@app.before_first_request
def create_tables():
    db.create_all()

@jwt.user_identity_loader
def user_identity_callback(user):
    print(user)
    return user

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify("Missing JSON in request"), 500

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username:
        return jsonify("Missing username parameter"), 500
    if not password:
        return jsonify("Missing password parameter"), 500

    user = UserModel.find_by_username(username)
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    else:
        return jsonify("Bad username or password"), 401

# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user = UserModel.find_by_username(identity)
    # if user:
    #     if user.username == "rolf":
    #         user["role"] = "admin"
    #     else:
    #         user[0]["role"] = "normal"
    #     return user[0]
    return user

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/who_am_i", methods=["GET"])
@jwt_required()
def protected():
    # We can now access our sqlalchemy User object via `current_user`.
    current_user = get_current_user()
    return jsonify(
        id=current_user.id, 
        username=current_user.username,
    )
    

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
api.add_resource(UserRegister, '/register')
api.add_resource(StoreManager, '/store/<string:name>')
api.add_resource(StoreList, '/stores')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)