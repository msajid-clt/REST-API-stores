from datetime import timedelta
from flask import jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    get_jwt_identity, get_jwt, create_refresh_token, jwt_required, 
    create_access_token, get_current_user
)
from models.user import UserModel
from redis_manager import redis_manager

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
        'username',
        type=str,
        required=True,
        help="Username is required!"
)
_user_parser.add_argument(
        'password',
        type=str,
        required=True,
        help="Password is required!"
)

class UserRegister(Resource):
    @classmethod
    def register_user(cls, username, password):
        if username is None or password is None:
            return {"message" : "Either username or password is empty."}, 500
        user = UserModel.find_by_username(username)
        if user:
            return {"message": "Username {} already exists!. Choose another name.".format(username)}, 400
        else:
            user = UserModel(username, password)
            id = user.save_to_db()
        return id

    def post(self):
        data = _user_parser.parse_args()
        return UserRegister.register_user(**data)
        

class User(Resource):
    @classmethod
    @jwt_required()
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message' : 'User not found'}, 404
        else:
            return user.toJSON()
    
    @classmethod
    @jwt_required()
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message' : 'User not found'}, 404
        else:
            user.delete()
            return {'message' : "User '{}' deleted successfully".format(user.username)}, 200

class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parser
        data = _user_parser.parse_args()
        username = data['username']
        password = data['password']
        
        if not username:
            return jsonify("Missing username parameter"), 500
        if not password:
            return jsonify("Missing password parameter"), 500

        # find user in database
        user = UserModel.find_by_username(username)
        
        # check password
        if user and user.check_password(password):
            # create access token
            access_token = create_access_token(identity=user.id, fresh=True)
            # create refresh token
            refresh_token = create_refresh_token(identity=user.id)
            # return tokens        
            return {
                    "access_token" : access_token,
                    "refresh_token" : refresh_token,
            }, 200
        else:
            return {"message" : "Authentication failed. Bad credentials!"}, 401

class UserCheck(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        # We can now access our sqlalchemy User object via `current_user`.
        current_user = get_current_user()
        return jsonify(
            id=current_user.id, 
            username=current_user.username,
        )

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        redis_manager.jwt_redis_blocklist.set(jti, "")
        return {'message' : 'Successfully logged out.'}, 200

class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user, fresh=False)
        return {
                "access_token" : new_access_token,
            }, 200

