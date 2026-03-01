from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Product Table
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    sell_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Sales Table
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(50))
    customer_name = db.Column(db.String(100))
    quantity_sold = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    profit = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/")
def home():
    return "Manya Fashion ERP Running Successfully 🚀"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
