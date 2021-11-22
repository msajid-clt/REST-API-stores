from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel
import json

class ItemManager(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help="The price of the item is required!"
    )
    parser.add_argument(
        'store_id',
        type=int,
        required=True,
        help="The store_id of the item is required!"
    )

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.toJSON()
    
        return {"message" : "Item '{}' not found.".format(name)}, 404
    
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message" : "Item '{}' already exists!".format(name)}, 400
        else:
            data = self.parser.parse_args()
            #item = ItemModel(name, data['price'], data['store_id'])
            item = ItemModel(name, **data)
            try:
                item.save_to_db()
            except Exception as e:
                return {"message" : "An exception occurred: " + str(e)}, 500
    
        return {"message" : "Item '{}' added successfully!".format(name)}, 201

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            try:
                item.delete()
            except Exception as e:
                return {"message" : "An exception occurred: " + str(e)}, 500
    
        return {"message" : "Item '{}' deleted successfully!".format(name)}, 200

    def put(self, name):
        item = ItemModel.find_by_name(name)
        data = self.parser.parse_args()
        if item is None:
            #item = ItemModel(name, data['price'], data['store_id'])
            item = ItemModel(name, **data)
        else:        
            item.price = data['price']
            item.store_id = data['store_id']
        try:
            item.save_to_db()
        except Exception as e:
            return {"message" : "An exception occurred: " + str(e)}, 500

        return item.toJSON(), 200
    

class ItemList(Resource):
    def get(self):
        return ItemModel.get_all_items(), 200
