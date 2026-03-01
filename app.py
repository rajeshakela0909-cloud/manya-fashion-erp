from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------- MODELS ----------------

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    mobile = db.Column(db.String(20))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50))
    name = db.Column(db.String(100))
    cost = db.Column(db.Float)
    sell = db.Column(db.Float)
    stock = db.Column(db.Integer)


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    quantity = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')
    customer = db.relationship('Customer')


# ---------------- ROUTES ----------------

@app.route("/")
def dashboard():
    products = Product.query.all()
    customers = Customer.query.all()
    sales = Sale.query.order_by(Sale.date.desc()).all()
    return render_template("index.html", products=products, customers=customers, sales=sales)


@app.route("/add_product", methods=["POST"])
def add_product():
    product = Product(
        code=request.form["code"],
        name=request.form["name"],
        cost=float(request.form["cost"]),
        sell=float(request.form["sell"]),
        stock=int(request.form["stock"])
    )
    db.session.add(product)
    db.session.commit()
    return redirect("/")


@app.route("/add_customer", methods=["POST"])
def add_customer():
    customer = Customer(
        name=request.form["name"],
        mobile=request.form["mobile"]
    )
    db.session.add(customer)
    db.session.commit()
    return redirect("/")


@app.route("/add_sale", methods=["POST"])
def add_sale():
    product = Product.query.get(int(request.form["product_id"]))
    customer = Customer.query.get(int(request.form["customer_id"]))
    qty = int(request.form["quantity"])

    if product and product.stock >= qty:
        product.stock -= qty
        sale = Sale(product=product, customer=customer, quantity=qty)
        db.session.add(sale)
        db.session.commit()

    return redirect("/")


# ---------------- START ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
