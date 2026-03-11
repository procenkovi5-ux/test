# ===============================
# SMARTMARKET MVP BACKEND
# FastAPI + SQLite
# ===============================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from collections import Counter

DB = "smartmarket.db"

app = FastAPI(title="SmartMarket MVP API")

# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DATABASE ----------------

def db():
    return sqlite3.connect(DB)


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS shops(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        owner TEXT,
        contact TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        image TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


init_db()

# ---------------- MODELS ----------------

class ShopCreate(BaseModel):
    name: str
    owner: str
    contact: str


class OrderCreate(BaseModel):
    product_id: int


# ---------------- SEED DATA ----------------

@app.on_event("startup")
def seed_products():
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]

    if count == 0:
        products = [
            ("Наушники", 12000, "https://picsum.photos/300?1"),
            ("Смарт часы", 25000, "https://picsum.photos/300?2"),
            ("Колонка", 18000, "https://picsum.photos/300?3"),
        ]

        cur.executemany(
            "INSERT INTO products(name,price,image) VALUES(?,?,?)",
            products
        )

    conn.commit()
    conn.close()


# ===============================
# PRODUCTS
# ===============================

@app.get("/api/products")
def get_products():
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT id,name,price,image FROM products")
    rows = cur.fetchall()

    conn.close()

    return [
        {"id": r[0], "name": r[1], "price": r[2], "image": r[3]}
        for r in rows
    ]


# ===============================
# SHOP REGISTRATION
# ===============================

@app.post("/api/shop/register")
def register_shop(shop: ShopCreate):

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO shops(name,owner,contact) VALUES(?,?,?)",
        (shop.name, shop.owner, shop.contact)
    )

    conn.commit()
    conn.close()

    return {"status": "ok"}


# ===============================
# ORDER
# ===============================

@app.post("/api/order")
def create_order(order: OrderCreate):

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO orders(product_id) VALUES(?)",
        (order.product_id,)
    )

    conn.commit()
    conn.close()

    return {"status": "ordered"}


# ===============================
# STATS (ADMIN)
# ===============================

@app.get("/api/stats")
def get_stats():

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM orders")
    sales = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM shops")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products")
    products = cur.fetchone()[0]

    conn.close()

    return {
        "sales": sales,
        "users": users,
        "products": products
    }


# ===============================
# AI RECOMMENDATIONS (MVP AI)
# ===============================

@app.get("/api/recommendations")
def ai_recommendations():

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT product_id FROM orders")
    orders = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT id,name FROM products")
    products = {r[0]: r[1] for r in cur.fetchall()}

    conn.close()

    if not orders:
        return {"text": "Недостаточно данных для анализа."}

    counter = Counter(orders)

    most = counter.most_common(1)[0][0]
    least = min(counter, key=counter.get)

    text = (
        f"📈 Рекомендуется увеличить закуп: {products[most]}\n"
        f"⚠️ Рассмотреть снижение закупа: {products[least]}"
    )

    return {"text": text}