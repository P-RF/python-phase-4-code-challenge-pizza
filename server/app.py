#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):

    def get(self):
        response_dict_list = [r.to_dict(only=('id', 'address', 'name')) for r in Restaurant.query.all()]
        return response_dict_list


class RestaurantByID(Resource):

    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        response_dict = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name,
            "restaurant_pizzas": []
        }

        for rp in restaurant.restaurant_pizzas:
            restaurant_pizzas_dict = {
                "id": rp.id,
                "pizza": {
                    "id": rp.pizza.id,
                    "ingredients": rp.pizza.ingredients,
                    "name": rp.pizza.name,
                },
                "pizza_id": rp.pizza.id,
                "price": rp.price,
                "restaurant_id": rp.restaurant.id,
            }
            response_dict["restaurant_pizzas"].append(restaurant_pizzas_dict)
        return response_dict, 200

    def delete(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()

        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()

        return '', 204

class Pizzas(Resource):

    def get(self):
        pizzas = [p.to_dict(only=('id', 'ingredients', 'name')) for p in Pizza.query.all()]
        return pizzas, 200


class RestaurantPizzaRes(Resource):

    def post(self):
        request_data = request.get_json()

        pizza_id = request_data.get("pizza_id")
        restaurant_id = request_data.get("restaurant_id")
        price = request_data.get("price")

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        # validation
        if not pizza or not restaurant or price is None or not (1 <= price <= 30):
            return {"errors": ["validation errors"]}, 400

        new_rp = RestaurantPizza(
            price=price,
            pizza_id=pizza.id,
            restaurant_id=restaurant.id
        )
        db.session.add(new_rp)
        db.session.commit()

        response_dict = {
            "id": new_rp.id,
            "pizza": {
                "id": pizza.id,
                "ingredients": pizza.ingredients,
                "name": pizza.name,
            },
            "pizza_id": pizza.id,
            "price": new_rp.price,
            "restaurant": {
                "address": restaurant.address,
                "id": restaurant.id,
                "name": restaurant.name,
            },
            "restaurant_id": restaurant.id
        }
        return response_dict, 201

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzaRes, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
