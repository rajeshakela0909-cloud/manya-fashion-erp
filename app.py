from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# DATABASE CONFIG (Railway ke liye)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50))
    name = db.Column(db.String(100))
    cost_price = db.Column(db.Float)
    sell_price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer)
    total = db.Column(db.Float)
    profit = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    products = Product.query.all()
    sales = Sale.query.order_by(Sale.date.desc()).all()
    return render_template("dashboard.html", products=products, sales=sales)

@app.route("/add_product", methods=["POST"])
def add_product():
    product = Product(
        code=request.form["code"],
        name=request.form["name"],
        cost_price=float(request.form["cost_price"]),
        sell_price=float(request.form["sell_price"]),
        quantity=int(request.form["quantity"]),
    )
    db.session.add(product)
    db.session.commit()
    return redirect("/")

@app.route("/sell", methods=["POST"])
def sell():
    product_id = int(request.form["product_id"])
    qty = int(request.form["quantity"])

    product = Product.query.get(product_id)

    if not product:
        return redirect("/")

    if product.quantity < qty:
        return redirect("/")

    total = product.sell_price * qty
    profit = (product.sell_price - product.cost_price) * qty

    product.quantity -= qty

    sale = Sale(
        product_id=product.id,
        quantity=qty,
        total=total,
        profit=profit,
    )

    db.session.add(sale)
    db.session.commit()

    return redirect(url_for("invoice", sale_id=sale.id))

@app.route("/invoice/<int:sale_id>")
def invoice(sale_id):
    sale = Sale.query.get(sale_id)
    if not sale:
        return redirect("/")
    return render_template("invoice.html", sale=sale)

@app.route("/delete/<int:id>")
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect("/")

# ---------------- CREATE TABLES ----------------

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
