import uuid
from db import db

class ItemModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float(precision=2))

    store_id = db.Column(db.String, db.ForeignKey('stores.id'))
    store = db.relationship("StoreModel")

    def __init__(self, name, price, store_id):
        self.id = str(uuid.uuid4())
        self.name = name
        self.price = price
        self.store_id = store_id

    def toJSON(self):
        return {"id" : self.id, "name" : self.name, "price" : self.price, "store_id": self.store_id }
    
    def toJSON_without_auth(self):
        return {"name" : self.name,  "store_id": self.store_id }
    
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
    
    @classmethod
    def get_all_items(cls, user_id):
        if user_id:
            return {
                "items" : [item.toJSON() for item in cls.query.all()]
            }
        return {
            "items" : [item.toJSON_without_auth() for item in cls.query.all()],
            "message" : "More data available on log in."
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
