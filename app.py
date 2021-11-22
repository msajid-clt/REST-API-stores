import datetime
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity as identity_function
from resources.user import UserRegister
from resources.item import ItemManager, ItemList
from resources.store import StoreManager, StoreList

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.secret_key = 'VerySecret'
api = Api(app)

# if the authentication endpoint has to be changed to something other than auth
# app.config['JWT_AUTH_URL_RULE'] = '/login'

# config JWT to expire within half an hour
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds=1800)

# config JWT auth key name to be 'email' instead of default 'username'
# app.config['JWT_AUTH_USERNAME_KEY'] = 'email'

@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWT(app, authenticate, identity_function) #/auth

@jwt.auth_response_handler
def customized_response_handler(access_token, identity):
    return jsonify({
        'access_token':
        access_token.decode('utf-8'),
        'user_id': identity.id
    })

@jwt.jwt_error_handler
def customized_error_handler(error):
    return jsonify({
        'message': error.description,
        'code': error.status_code
    }), error.status_code

api.add_resource(ItemManager, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(StoreManager, '/store/<string:name>')
api.add_resource(StoreList, '/stores')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)