#!/usr/bin/env python3

from models import db, Customer, Coffee, Order
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
api = Api(app)
db.init_app(app)

class Coffees(Resource):
    def get(self):
        all_coffee = [c.to_dict(rules=('-orders',)) for c in Coffee.query.all()]
        return make_response(all_coffee,200)
api.add_resource(Coffees,'/coffees')
class CustomerById(Resource):
    def get(self,id):
        customer = Customer.query.get(id)
        if not customer:
            return make_response({"error": "Customer not found"},404)
        return make_response(customer.to_dict(),200)
api.add_resource(CustomerById,'/customers/<id>')
class CoffeesById(Resource):
    def delete(self,id):
        coffee = Coffee.query.get(id)
        if not coffee:
            return make_response({"error": "Coffee not found"},404)
        db.session.delete(coffee)
        db.session.commit()
        return make_response("Can't See Me",204)
api.add_resource(CoffeesById,'/coffees/<id>')
class Orders(Resource):
    def get(self):
        all_orders = [o.to_dict(rules=('-coffee_id','-price','-customer_id')) for o in Order.query.all()]
        return make_response(all_orders,200)
    def post(self):
        params = request.json
        try:
            order = Order(price=params['price'],customization=params['customization'],customer_id=params['customer_id'],coffee_id=['coffee_id'])
        except:
            return make_response({"errors": ["validation errors"]},400)
        db.session.add(order)
        db.session.commit()
        return make_response(order.to_dict(),200)
api.add_resource(Orders,'/orders')
@app.route('/')
def index():
    return '<h1>Coffee Shop Practice Challenge</h1>'

if __name__ == '__main__':
    app.run(port=5555, debug=True)
