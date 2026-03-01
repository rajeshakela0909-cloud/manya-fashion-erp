from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# ---------------- DATABASE ---------------- #

database_url = os.environ.get("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- MODELS ---------------- #

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    sell_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20))
    address = db.Column(db.String(200))

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float)
    profit = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')
    customer = db.relationship('Customer')

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    products = Product.query.all()
    customers = Customer.query.all()
    sales = Sale.query.order_by(Sale.date.desc()).all()

    total_profit = sum(s.profit for s in sales) if sales else 0

    return render_template(
        "index.html",
        products=products,
        customers=customers,
        sales=sales,
        total_profit=total_profit
    )

# ---------------- PRODUCT ---------------- #

@app.route("/add_product", methods=["POST"])
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

@app.route("/delete_product/<int:id>")
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect("/")

# ---------------- CUSTOMER ---------------- #

@app.route("/add_customer", methods=["POST"])
def add_customer():
    customer = Customer(
        name=request.form["name"],
        mobile=request.form["mobile"],
        address=request.form["address"]
    )
    db.session.add(customer)
    db.session.commit()
    return redirect("/")

# ---------------- SALE ---------------- #

@app.route("/add_sale", methods=["POST"])
def add_sale():
    product = Product.query.get(int(request.form["product_id"]))
    customer = Customer.query.get(int(request.form["customer_id"]))
    qty = int(request.form["quantity"])

    if product and customer and product.quantity >= qty:
        total = product.sell_price * qty
        profit = (product.sell_price - product.cost_price) * qty

        product.quantity -= qty

        sale = Sale(
            product=product,
            customer=customer,
            quantity=qty,
            total_amount=total,
            profit=profit
        )

        db.session.add(sale)
        db.session.commit()

        return redirect(f"/invoice/{sale.id}")

    return redirect("/")

# ---------------- INVOICE ---------------- #

@app.route("/invoice/<int:id>")
def invoice(id):
    sale = Sale.query.get(id)

    if not sale:
        return redirect("/")

    return render_template("invoice.html", sale=sale)

# ---------------- INIT ---------------- #

with app.app_context():
    db.create_all()

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
