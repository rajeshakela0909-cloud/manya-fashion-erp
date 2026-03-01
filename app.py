from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Railway DATABASE_URL fix (postgres:// → postgresql://)
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

@app.route("/")
def home():
    return "Manya Fashion ERP Running Successfully 🚀"

# Only create tables if DB available
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print("Database not ready yet:", e)
