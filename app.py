from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    sell_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    @app.route("/delete/<int:id>")
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return redirect("/")

@app.route("/")
def home():
    products = Product.query.all()
    return render_template("index.html", products=products)

@app.route("/add", methods=["POST"])
def add_product():
    product = Product(
        code=request.form["code"],
        name=request.form["name"],
        cost_price=float(request.form["cost_price"]),
        sell_price=float(request.form["sell_price"]),
        quantity=int(request.form["quantity"])
    )
    db.session.add(product)
    db.session.commit()
    return redirect("/")

with app.app_context():
    db.create_all()

