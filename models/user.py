from db import db

class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    @classmethod
    def find_by_username(cls, username):
        try:
            user = cls.query.filter_by(username=username).first()
            if user:
                status_message = "User '{}' found.".format(username)
                status_code =  200
            else:
                user = None
                status_message = "User '{}' not found.".format(username)
                status_code = 404
        except Exception as e:
            user = None 
            status_message = "An error occurred. " + str(e)
            status_code = 500
        
        return {'msg' : status_message, "msg_code" : status_code, 'user' : user}
    
    @classmethod
    def find_by_id(cls, _id):
        try:
            user = cls.query.filter_by(id=_id).first()
            if user:
                status_message = "User '{}' found.".format(_id)
                status_code =  200
            else:
                user = None
                status_message = "User '{}' not found.".format(_id)
                status_code = 404
        except Exception as e:
            user = None 
            status_message = "An error occurred. " + str(e)
            status_code = 500
        
        return {'msg' : status_message, "msg_code" : status_code, 'user' : user}

    def save_to_db(self):
        try: 
            db.session.add(self)
            db.session.commit()
            status_message = "User {} created successfully.".format(self.name)
            status_code = 201

        except Exception as e:
            status_message = 'An error occurred!' + str(e)
            status_code =  500
        
        return {'msg' : status_message, "msg_code" : status_code}    