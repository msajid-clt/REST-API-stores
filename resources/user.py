import sqlite3
from flask_restful import Resource, reqparse
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
    def register_user(cls, username, password):
        result = UserModel.find_by_username(username)
        user = result['user']
        if user:
            status_message = 'Username {} already exists!. Choose another name.'.format(username)
            status_code = 400            
        else:
            user = UserModel(username, password)
            user.save_to_db()
            status_message = "User {} created successfully.".format(username)
            status_code = 201
                
        return {'msg' : status_message, "msg_code" : status_code}


    def post(self):
        data = UserRegister.parser.parse_args()
        result = UserRegister.register_user(**data)
        return {'message' : result['msg']}, result['msg_code']


        