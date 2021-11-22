import uuid

from db import db
from flask import jsonify
from sqlalchemy.dialects.postgresql import UUID
from passlib.hash import pbkdf2_sha256

class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(200), primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password = pbkdf2_sha256.hash(password)
    
    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)
    
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        try: 
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            return {"message": "An error occurred: " + str(e)}, 500
        
        return jsonify(self.id)
