from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.store import StoreModel

class StoreManager(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help="The price of the item is required!"
    )

    @jwt_required()
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.toJSON()
            
        return {"message" : "Store '{}' not found.".format(name)}, 404
    
    def post(self, name):
        #data = self.parser.parse_args()
        if not StoreModel.find_by_name(name):
            store = StoreModel(name)
            try:
                store.save_to_db()
            except Exception as e:
                return {"message" : "An exception occurred : " + str(e)}, 500
        else:
            return {"message" : "Store '{}' already exists.".format(name)}, 400

        return {'store' : store.toJSON()}

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete()
            return {"message" : "Store {} deleted successfully!".format(name)}
        else:
            return {"message" : "Store not found!".format(name)}

class StoreList(Resource):
    def get(self):
        return {"stores" : StoreModel.get_all_stores()}

