from flask import Flask, request, redirect
import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS products (code TEXT PRIMARY KEY, name TEXT, purchase DOUBLE PRECISION,
selling DOUBLE PRECISION, stock INTEGER)")
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
)
""")
conn.commit()

@app.route("/")
def home():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.execute("SELECT SUM(profit) FROM sales WHERE date=?", (datetime.now().strftime("%Y-%m-%d"),))
    today_profit = cursor.fetchone()[0]
    if not today_profit:
        today_profit = 0

    html = "<h2>Manya Fashion Jewellery - Premium</h2>"

    html += """
    <h3>Add Product</h3>
    <form method='post' action='/add'>
    Code:<input name='code'><br>
    Name:<input name='name'><br>
    Purchase:<input name='purchase'><br>
    Selling:<input name='selling'><br>
    Stock:<input name='stock'><br>
    <button>Add</button>
    </form>
    <hr>
    <h3>Sell Product</h3>
    <form method='post' action='/sell'>
    Code:<input name='code'><br>
    Qty:<input name='qty'><br>
    <button>Sell</button>
    </form>
    <hr>
    <h3>Products</h3>
    """

    for p in products:
        html += f"{p[0]} | {p[1]} | ₹{p[2]} → ₹{p[3]} | Stock: {p[4]}<br>"

    html += f"<hr><h3>Today's Profit: ₹{today_profit}</h3>"

    return html

@app.route("/add", methods=["POST"])
def add():
    cursor.execute("INSERT INTO products VALUES (?,?,?,?,?)",
                   (request.form["code"],
                    request.form["name"],
                    float(request.form["purchase"]),
                    float(request.form["selling"]),
                    int(request.form["stock"])))
    conn.commit()
    return redirect("/")

@app.route("/sell", methods=["POST"])
def sell():
    code = request.form["code"]
    qty = int(request.form["qty"])

    cursor.execute("SELECT * FROM products WHERE code=?", (code,))
    product = cursor.fetchone()

    if product and product[4] >= qty:
        profit = (product[3] - product[2]) * qty
        new_stock = product[4] - qty

        cursor.execute("UPDATE products SET stock=? WHERE code=?", (new_stock, code))

        cursor.execute("INSERT INTO sales (code,name,qty,profit,date,time) VALUES (?,?,?,?,?,?)",
                       (code, product[1], qty, profit,
                        datetime.now().strftime("%Y-%m-%d"),
                        datetime.now().strftime("%H:%M:%S")))

        conn.commit()

    return redirect("/")


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


