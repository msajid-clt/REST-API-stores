from flask import jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.user import UserModel

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'username',
        type=str,
        required=True,
        help="Username is required!"
    )
    parser.add_argument(
        'password',
        type=str,
        required=True,
        help="Password is required!"
    )

    @classmethod
    @jwt_required()
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

    @jwt_required()
    def post(self):
        data = UserRegister.parser.parse_args()
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
        