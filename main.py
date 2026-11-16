"""
KodNaqi Pharmacy - Backend API (Phase 1)
Local-First PWA Backend - SQLite + FastAPI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from contextlib import contextmanager
from datetime import datetime, timezone
import sqlite3
import os
from fastapi.staticfiles import StaticFiles

DB_PATH = os.path.join(os.path.dirname(__file__), "pharmacy.db")

app = FastAPI(title="KodNaqi Pharmacy API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Database Helpers ====================
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            pharmacy_name TEXT NOT NULL DEFAULT 'KodNaqi Pharmacy',
            logo_url TEXT,
            currency TEXT NOT NULL DEFAULT 'SDG',
            address TEXT,
            phone TEXT,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            name TEXT NOT NULL,
            scientific_name TEXT,
            category TEXT,
            price REAL NOT NULL DEFAULT 0,
            cost REAL NOT NULL DEFAULT 0,
            stock_quantity INTEGER NOT NULL DEFAULT 0,
            expiry_date TEXT,
            batch_number TEXT,
            supplier_id INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_medicines_barcode ON medicines(barcode);
        CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines(name);

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE,
            customer_id INTEGER,
            total_amount REAL NOT NULL,
            discount REAL DEFAULT 0,
            paid_amount REAL NOT NULL,
            sale_date TEXT NOT NULL,
            user_id INTEGER,
            sync_status TEXT DEFAULT 'pending'
        );

        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY(medicine_id) REFERENCES medicines(id)
        );

        CREATE TABLE IF NOT EXISTS sync_outbox (
            id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            operation TEXT NOT NULL,
            payload TEXT,
            created_at TEXT NOT NULL,
            synced_at TEXT
        );
        """)

        cur = db.execute("SELECT COUNT(*) FROM settings WHERE id = 1")
        if cur.fetchone()[0] == 0:
            db.execute(
                "INSERT INTO settings (id, pharmacy_name, currency, updated_at) VALUES (1, ?, ?, ?)",
                ("KodNaqi Pharmacy", "SDG", now_iso()),
            )


# ==================== Pydantic Models ====================

class MedicineIn(BaseModel):
    barcode: Optional[str] = None
    name: str # الاسم التجاري
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    price: float = 0
    cost: float = 0
    stock_quantity: int = 0
    expiry_date: Optional[str] = None
    batch_number: Optional[str] = None
    supplier_id: Optional[int] = None


class SettingsIn(BaseModel):
    pharmacy_name: Optional[str] = None
    logo_url: Optional[str] = None
    currency: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


# ==================== Startup ====================
init_db()


# ==================== Routes ====================
#@app.get("/")
#def root():
    #return {"status": "ok", "app": "KodNaqi Pharmacy", "version": "0.1.0"}


@app.get("/api/health")
def health():
    return {"status": "healthy", "time": now_iso()}


# ---- Settings ----
@app.get("/api/settings")
def get_settings():
    with get_db() as db:
        row = db.execute("SELECT * FROM settings WHERE id = 1").fetchone()
        return dict(row)


@app.put("/api/settings")
def update_settings(data: SettingsIn):
    updates, values = [], []
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            updates.append(f"{field} = ?")
            values.append(value)
    if not updates:
        raise HTTPException(400, "No fields to update")
    updates.append("updated_at = ?")
    values.append(now_iso())
    values.append(1)
    with get_db() as db:
        db.execute(f"UPDATE settings SET {', '.join(updates)} WHERE id = ?", values)
        row = db.execute("SELECT * FROM settings WHERE id = 1").fetchone()
        return dict(row)


# ---- Medicines ----
@app.get("/api/medicines")
def list_medicines(q: Optional[str] = None, limit: int = 100, offset: int = 0):
    with get_db() as db:

        if q:
            rows = db.execute(
                "SELECT * FROM medicines WHERE name LIKE ? OR scientific_name LIKE ? OR barcode LIKE ? "
                "ORDER BY name LIMIT ? OFFSET ?",
                (f"%{q}%", f"%{q}%", f"%{q}%", limit, offset),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM medicines ORDER BY name LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()

        return [dict(r) for r in rows]


@app.get("/api/medicines/barcode/{barcode}")
def get_by_barcode(barcode: str):
    with get_db() as db:
        row = db.execute("SELECT * FROM medicines WHERE barcode = ?", (barcode,)).fetchone()
        if not row:
            raise HTTPException(404, "Medicine not found")
        return dict(row)


@app.get("/api/medicines/{med_id}")
def get_medicine(med_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM medicines WHERE id = ?", (med_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Medicine not found")
        return dict(row)


@app.post("/api/medicines")
def create_medicine(data: MedicineIn):
    now = now_iso()
    with get_db() as db:
        try:
            cur = db.execute(
                """INSERT INTO medicines (barcode, name, scientific_name, category, price, cost,
                   stock_quantity, expiry_date, batch_number, supplier_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (data.barcode, data.name, data.scientific_name, data.category, data.price,
                 data.cost, data.stock_quantity, data.expiry_date, data.batch_number,
                 data.supplier_id, now, now),
            )
            row = db.execute("SELECT * FROM medicines WHERE id = ?", (cur.lastrowid,)).fetchone()
            return dict(row)
        except sqlite3.IntegrityError as e:
            raise HTTPException(400, f"Integrity error: {e}")


@app.put("/api/medicines/{med_id}")
def update_medicine(med_id: int, data: MedicineIn):
    updates, values = [], []
    for field, value in data.model_dump(exclude_unset=True).items():
        updates.append(f"{field} = ?")
        values.append(value)
    if not updates:
        raise HTTPException(400, "No fields to update")
    updates.append("updated_at = ?")
    values.append(now_iso())
    values.append(med_id)
    with get_db() as db:
        db.execute(f"UPDATE medicines SET {', '.join(updates)} WHERE id = ?", values)
        row = db.execute("SELECT * FROM medicines WHERE id = ?", (med_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Medicine not found")
        return dict(row)


@app.delete("/api/medicines/{med_id}")
def delete_medicine(med_id: int):
    with get_db() as db:
        cur = db.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Medicine not found")
        return {"deleted": True}

# ==================== Sales (POS) ====================
class SaleItemIn(BaseModel):
    medicine_id: int
    quantity: int
    unit_price: float

class SaleIn(BaseModel):
    customer_id: Optional[int] = None
    discount: float = 0
    paid_amount: float
    items: list[SaleItemIn]

@app.post("/api/sales")
def create_sale(sale: SaleIn):
    now = now_iso()
    total_amount = sum(item.quantity * item.unit_price for item in sale.items) - sale.discount
    invoice_number = f"INV-{int(datetime.now().timestamp())}"
    
    with get_db() as db:
        try:
            # 1. إنشاء الفاتورة
            cur = db.execute(
                """INSERT INTO sales (invoice_number, customer_id, total_amount, discount, paid_amount, sale_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (invoice_number, sale.customer_id, total_amount, sale.discount, sale.paid_amount, now)
            )
            sale_id = cur.lastrowid

            # 2. إضافة عناصر الفاتورة وتحديث المخزون
            for item in sale.items:
                # إضافة العنصر
                db.execute(
                    """INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, total_price)
                       VALUES (?, ?, ?, ?, ?)""",
                    (sale_id, item.medicine_id, item.quantity, item.unit_price, item.quantity * item.unit_price)
                )
                # خصم الكمية من المخزون
                db.execute(
                    "UPDATE medicines SET stock_quantity = stock_quantity - ? WHERE id = ?",
                    (item.quantity, item.medicine_id)
                )
            
            return {"status": "success", "invoice_number": invoice_number, "sale_id": sale_id}
        except Exception as e:
            raise HTTPException(400, f"حدث خطأ أثناء الحفظ: {str(e)}")


# ==================== Sales History ====================
@app.get("/api/sales")
def get_sales_history():
    with get_db() as db:
        sales = db.execute("SELECT * FROM sales ORDER BY id DESC LIMIT 100").fetchall()
        result = []
        for sale in sales:
            items = db.execute('''
                SELECT si.*, m.name 
                FROM sale_items si 
                JOIN medicines m ON si.medicine_id = m.id 
                WHERE si.sale_id = ?
            ''', (sale['id'],)).fetchall()
            sale_dict = dict(sale)
            sale_dict['items'] = [dict(i) for i in items]
            result.append(sale_dict)
        return result


# ==================== Dashboard Statistics ====================

# ==================== Dashboard Statistics ====================
@app.get("/api/stats")
def get_stats():
    today = datetime.now(timezone.utc).date().isoformat()
    with get_db() as db:
        # مبيعات اليوم
        today_sales = db.execute(
            "SELECT COUNT(id) as count, SUM(total_amount) as total FROM sales WHERE sale_date LIKE ?", 
            (f"{today}%",)
        ).fetchone()
        
        # إجمالي الأرباح اليوم
        profit_query = db.execute('''
            SELECT SUM((si.unit_price - m.cost) * si.quantity) as total_profit
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN medicines m ON si.medicine_id = m.id
            WHERE s.sale_date LIKE ?
        ''', (f"{today}%",)).fetchone()

        # تنبيهات المخزون (أقل من 10 حبات)
        low_stock = db.execute("SELECT id, name, stock_quantity FROM medicines WHERE stock_quantity <= 10").fetchall()
        
        # تنبيهات الصلاحية (تنتهي خلال 30 يوماً)
        expiring_soon = db.execute('''
            SELECT id, name, expiry_date, stock_quantity 
            FROM medicines 
            WHERE expiry_date IS NOT NULL 
            AND expiry_date != '' 
            AND date(expiry_date) <= date('now', '+30 days')
            AND date(expiry_date) >= date('now')
        ''').fetchall()

        # الأدوية المنتهية صلاحيتها
        expired = db.execute('''
            SELECT id, name, expiry_date, stock_quantity 
            FROM medicines 
            WHERE expiry_date IS NOT NULL 
            AND expiry_date != '' 
            AND date(expiry_date) < date('now')
        ''').fetchall()
        
        return {
            "today_sales_count": today_sales["count"] if today_sales else 0,
            "today_revenue": today_sales["total"] if today_sales and today_sales["total"] else 0,
            "today_profit": profit_query["total_profit"] if profit_query and profit_query["total_profit"] else 0,
            "low_stock_alerts": [dict(r) for r in low_stock],
            "expiring_soon_alerts": [dict(r) for r in expiring_soon],
            "expired_alerts": [dict(r) for r in expired]
        }


# ==================== Backup & Export ====================
from fastapi.responses import FileResponse
import csv
from io import StringIO

@app.get("/api/backup/database")
def backup_database():
    db_path = os.path.join(os.path.dirname(__file__), "pharmacy.db")
    if os.path.exists(db_path):
        return FileResponse(db_path, media_type="application/x-sqlite3", filename="kodnaqi_backup.db")
    raise HTTPException(404, "Database file not found")

@app.get("/api/backup/sales-csv")
def export_sales_csv():
    with get_db() as db:
        sales = db.execute("SELECT invoice_number, sale_date, total_amount, paid_amount FROM sales ORDER BY id DESC").fetchall()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Invoice Number", "Date", "Total Amount", "Paid Amount"])
    for sale in sales:
        writer.writerow([sale["invoice_number"], sale["sale_date"], sale["total_amount"], sale["paid_amount"]])
    
    csv_content = output.getvalue()
    output.close()
    
    from fastapi.responses import Response
    return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=kodnaqi_sales.csv"})

# تقديم ملفات الواجهة الأمامية (PWA)

# تقديم ملفات الواجهة الأمامية (PWA)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
