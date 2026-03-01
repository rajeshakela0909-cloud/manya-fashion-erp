from flask import Flask, request, redirect
import os
import psycopg2
from datetime import datetime

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create Tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    code TEXT PRIMARY KEY,
    name TEXT,
    purchase DOUBLE PRECISION,
    selling DOUBLE PRECISION,
    stock INTEGER
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    bill_no TEXT,
    code TEXT,
    name TEXT,
    qty INTEGER,
    profit DOUBLE PRECISION,
    total DOUBLE PRECISION,
    customer TEXT,
    mobile TEXT,
    date TEXT,
    time TEXT
);
""")

conn.commit()

@app.route("/")
def home():
    return "Manya Fashion ERP Running Successfully 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
