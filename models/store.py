import uuid
from db import db
from models.item import ItemModel

class StoreModel(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(80))
    
    items = db.relationship('ItemModel', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name

    def toJSON(self):
        return {"id" : self.id, "name" : self.name, "items" : [item.toJSON() for item in self.items.all()]}
    
    @classmethod
    def find_by_name(cls, name):
        try:
            return cls.query.filter_by(name=name).first()
        except Exception as e:
            return "Exception occurred: " + str(e)

    @classmethod
    def find_by_id(cls, _id):
        try: 
            return cls.query.filter_by(id=_id).first()
        except Exception as e:
            return "Exception occurred : " + str(e)
    
    @classmethod
    def get_all_stores(cls):
        try :
            return [store.toJSON() for store in cls.query.all()]
        except Exception as e:
            return "An error occurred : " + str(e)

    def get_all_items_in_a_store(name):
        try :
            store = StoreModel.find_by_name(name)
            return ItemModel.get_all_items(store.id)
        except Exception as e:
            return "An error occurred : " + str(e)

    def save_to_db(self):
        try: 
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            return 'An error occurred!' + str(e)

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            return "An error occurred : " + str(e)

    def add_item_to_store(storename, itemname, price):
        try:
            store = StoreModel.find_by_name(storename)
            item = ItemModel(itemname, price, store.id)
            store.items.append(item)
            store.save_to_db()
        except Exception as e:
            return "An error occurred : " + str(e)
        return store