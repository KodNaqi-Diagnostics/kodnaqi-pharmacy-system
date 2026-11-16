
import os
import psycopg2
from psycopg2.extras import DictCursor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from passlib.context import CryptContext

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL: raise Exception("DATABASE_URL missing!")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI(title="KodNaqi Pharmacy API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def now_iso(): return datetime.now(timezone.utc).isoformat()

def init_db():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT DEFAULT 'admin');")
            cur.execute("CREATE TABLE IF NOT EXISTS suppliers (id SERIAL PRIMARY KEY, name TEXT NOT NULL, phone TEXT);")
            cur.execute("CREATE TABLE IF NOT EXISTS medicines (id SERIAL PRIMARY KEY, barcode TEXT UNIQUE, name TEXT NOT NULL, scientific_name TEXT, category TEXT, price REAL NOT NULL DEFAULT 0, cost REAL NOT NULL DEFAULT 0, stock_quantity INTEGER NOT NULL DEFAULT 0, expiry_date TEXT, supplier_id INTEGER REFERENCES suppliers(id), created_at TEXT, updated_at TEXT);")
            cur.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY CHECK (id=1), pharmacy_name TEXT, currency TEXT, updated_at TEXT);")
            cur.execute("CREATE TABLE IF NOT EXISTS sales (id SERIAL PRIMARY KEY, invoice_number TEXT UNIQUE, total_amount REAL, discount REAL, paid_amount REAL, sale_date TEXT);")
            cur.execute("CREATE TABLE IF NOT EXISTS sale_items (id SERIAL PRIMARY KEY, sale_id INTEGER REFERENCES sales(id) ON DELETE CASCADE, medicine_id INTEGER, quantity INTEGER, unit_price REAL, total_price REAL);")
            cur.execute("SELECT COUNT(*) FROM users")
            if cur.fetchone()[0] == 0: 
                cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", ("admin", pwd_context.hash("admin"), "admin"))
            cur.execute("INSERT INTO settings (id, pharmacy_name, currency, updated_at) VALUES (1, 'KodNaqi Pharmacy', 'SDG', %s) ON CONFLICT (id) DO NOTHING", (now_iso(),))
            conn.commit()
init_db()

class LoginIn(BaseModel):
    username: str
    password: str
class MedicineIn(BaseModel):
    barcode: Optional[str] = None
    name: str
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    price: float = 0
    cost: float = 0
    stock_quantity: int = 0
    expiry_date: Optional[str] = None
    supplier_id: Optional[int] = None
class SupplierIn(BaseModel):
    name: str
    phone: Optional[str] = None
class SettingsIn(BaseModel):
    pharmacy_name: Optional[str] = None
    currency: Optional[str] = None
class SaleItemIn(BaseModel):
    medicine_id: int
    quantity: int
    unit_price: float
class SaleIn(BaseModel):
    discount: float = 0
    paid_amount: float
    items: list[SaleItemIn]

@app.post("/api/login")
def login(data: LoginIn):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (data.username,))
            user = cur.fetchone()
            if user and pwd_context.verify(data.password, user['password_hash']): 
                return {"status": "success", "role": user['role']}
            raise HTTPException(401, "بيانات الدخول غير صحيحة")

@app.get("/api/suppliers")
def get_suppliers():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM suppliers ORDER BY name")
            return [dict(r) for r in cur.fetchall()]

@app.post("/api/suppliers")
def add_supplier(data: SupplierIn):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("INSERT INTO suppliers (name, phone) VALUES (%s, %s) RETURNING *", (data.name, data.phone))
            conn.commit()
            return dict(cur.fetchone())

@app.get("/api/medicines")
def list_medicines():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT m.*, s.name as supplier_name FROM medicines m LEFT JOIN suppliers s ON m.supplier_id = s.id ORDER BY m.name")
            return [dict(r) for r in cur.fetchall()]

@app.post("/api/medicines")
def add_medicine(data: MedicineIn):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("INSERT INTO medicines (barcode, name, scientific_name, category, price, cost, stock_quantity, expiry_date, supplier_id, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *", (data.barcode, data.name, data.scientific_name, data.category, data.price, data.cost, data.stock_quantity, data.expiry_date, data.supplier_id, now_iso(), now_iso()))
            conn.commit()
            return dict(cur.fetchone())

@app.put("/api/medicines/{med_id}")
def update_medicine(med_id: int, data: MedicineIn):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("UPDATE medicines SET barcode=%s, name=%s, scientific_name=%s, category=%s, price=%s, cost=%s, stock_quantity=%s, expiry_date=%s, supplier_id=%s, updated_at=%s WHERE id=%s RETURNING *", (data.barcode, data.name, data.scientific_name, data.category, data.price, data.cost, data.stock_quantity, data.expiry_date, data.supplier_id, now_iso(), med_id))
            conn.commit()
            return dict(cur.fetchone())

@app.delete("/api/medicines/{med_id}")
def delete_medicine(med_id: int):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM medicines WHERE id=%s", (med_id,))
            conn.commit()
            return {"status": "deleted"}

@app.get("/api/medicines/barcode/{barcode}")
def get_by_barcode(barcode: str):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM medicines WHERE barcode = %s", (barcode,))
            row = cur.fetchone()
            if not row: raise HTTPException(404, "Not found")
            return dict(row)

@app.post("/api/sales")
def create_sale(sale: SaleIn):
    now = now_iso()
    total_amount = sum(item.quantity * item.unit_price for item in sale.items) - sale.discount
    invoice_number = f"INV-{int(datetime.now().timestamp())}"
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("INSERT INTO sales (invoice_number, total_amount, discount, paid_amount, sale_date) VALUES (%s, %s, %s, %s, %s) RETURNING id", (invoice_number, total_amount, sale.discount, sale.paid_amount, now))
            sale_id = cur.fetchone()['id']
            for item in sale.items:
                cur.execute("INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, total_price) VALUES (%s, %s, %s, %s, %s)", (sale_id, item.medicine_id, item.quantity, item.unit_price, item.quantity * item.unit_price))
                cur.execute("UPDATE medicines SET stock_quantity = stock_quantity - %s WHERE id = %s", (item.quantity, item.medicine_id))
            conn.commit()
            return {"status": "success", "invoice_number": invoice_number, "sale_id": sale_id}

@app.get("/api/sales")
def get_sales():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM sales ORDER BY id DESC LIMIT 100")
            sales = cur.fetchall()
            result = []
            for sale in sales:
                cur.execute("SELECT si.*, m.name FROM sale_items si JOIN medicines m ON si.medicine_id = m.id WHERE si.sale_id = %s", (sale['id'],))
                sale_dict = dict(sale)
                sale_dict['items'] = [dict(i) for i in cur.fetchall()]
                result.append(sale_dict)
            return result

@app.get("/api/settings")
def get_settings():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM settings WHERE id=1")
            return dict(cur.fetchone())

@app.put("/api/settings")
def update_settings(data: SettingsIn):
    updates, values = [], []
    if data.pharmacy_name: updates.append("pharmacy_name = %s"); values.append(data.pharmacy_name)
    if data.currency: updates.append("currency = %s"); values.append(data.currency)
    if not updates: return {"status": "no changes"}
    updates.append("updated_at = %s"); values.append(now_iso()); values.append(1)
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(f"UPDATE settings SET {', '.join(updates)} WHERE id = %s RETURNING *", tuple(values))
            conn.commit()
            return dict(cur.fetchone())

@app.get("/api/stats")
def get_stats():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT COUNT(id) as count, SUM(total_amount) as total FROM sales WHERE sale_date::date = CURRENT_DATE")
            today = cur.fetchone()
            cur.execute("SELECT SUM((si.unit_price - m.cost) * si.quantity) as total_profit FROM sale_items si JOIN sales s ON si.sale_id = s.id JOIN medicines m ON si.medicine_id = m.id WHERE s.sale_date::date = CURRENT_DATE")
            profit = cur.fetchone()
            cur.execute("SELECT id, name, stock_quantity FROM medicines WHERE stock_quantity <= 10")
            low_stock = cur.fetchall()
            return {"today_sales_count": today["count"] or 0, "today_revenue": today["total"] or 0, "today_profit": profit["total_profit"] or 0, "low_stock_alerts": [dict(r) for r in low_stock], "expiring_soon_alerts": [], "expired_alerts": []}

from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="static", html=True), name="static")
