# wsgi.py
# pylint: disable=missing-docstring

from config import Config
from flask import Flask, abort, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow  # NEW LINE (Order is important here!)

BASE_URL = '/api/v1'
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
from models import Product
from schemas import many_product_schema, one_product_schema
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

admin = Admin(app, template_mode='bootstrap3')
admin.add_view(ModelView(Product, db.session))

@app.route('/')
def home():
    products = db.session.query(Product).all()

    return render_template('home.html', products=products)

@app.route('/<int:product_id>')
def product_html(product_id):
    product = db.session.query(Product).get(product_id)
    return render_template('product.html', product=product)

@app.route(f'{BASE_URL}/products', methods=['GET'])
def get_many_product():
    products = db.session.query(Product).all() # SQLAlchemy request => 'SELECT * FROM products'
    return many_product_schema.jsonify(products), 200

@app.route(f'{BASE_URL}/products', methods=['POST'])
def create_one_product():
    content = request.json
    name = content.get('name', None)
    description = content.get('description', '')
    if name is None:
        return {}, 404
    new_product = Product(name=name, description=description)
    db.session.add(new_product)
    db.session.commit()
    return one_product_schema.jsonify(new_product), 201

@app.route(f'{BASE_URL}/products/<int:id>', methods=['GET'])
def get_one_product(id):
    product = db.session.query(Product).get(id)
    return one_product_schema.jsonify(product), 200

@app.route(f'{BASE_URL}/products/<int:id>', methods=['DELETE'])
def delete_one_product(id):
    db.session.query(Product).filter_by(id=id).delete()
    db.session.commit()
    return {}, 204

@app.route(f'{BASE_URL}/products/<int:id>', methods=['PATCH'])
def update_one_product(id):
    product = db.session.query(Product).get(id)
    if product is None:
        return {}, 404
    content = request.json
    name = content.get('name', None)
    description = content.get('description', None)
    if name is not None and name != '':
        product.name = name
    if description is not None and description != '':
        product.description = description
    db.session.add(product)
    db.session.commit()
    return one_product_schema.jsonify(product), 201
