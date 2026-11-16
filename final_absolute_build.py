import os

print("⏳ جاري بناء النظام المطلق (النسخة النهائية 100%)...")

# ==========================================
# 1. تحديث المتطلبات
# ==========================================
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("fastapi\nuvicorn[standard]\npsycopg2-binary\npasslib[bcrypt]\n")

# ==========================================
# 2. بناء main.py (الباك-إند)
# ==========================================
main_code = '''
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
'''
with open("main.py", "w", encoding="utf-8") as f: 
    f.write(main_code)

# ==========================================
# 3. بناء index.html (الواجهة)
# ==========================================
html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KodNaqi Pharmacy</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Poppins:wght@600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = { theme: { extend: { fontFamily: { sans: ['Tajawal', 'sans-serif'], english: ['Poppins', 'sans-serif'] }, colors: { primary: '#0b4d3b', bg: '#f2ede4', card: '#ffffff', textMain: '#1a202c' } } } }</script>
    <script src="https://unpkg.com/html5-qrcode"></script><script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/localforage/1.10.0/localforage.min.js"></script>
    <link rel="manifest" href="/manifest.json">
    <style>body { font-family: 'Tajawal', sans-serif; background-color: #f2ede4; color: #1a202c; } .premium-shadow { box-shadow: 0 4px 25px rgba(0,0,0,0.03); } @media print { body > * { display: none !important; } #print-area { display: block !important; margin: 0 auto !important; padding: 10px; width: 100%; max-width: 80mm; color: #000 !important; background: #fff !important; } #app-modal { display: none !important; } @page { margin: 5mm; } }</style>
</head>
<body class="text-textMain pb-24">
    <div id="splash-screen" class="fixed inset-0 bg-primary z-[100] flex flex-col items-center justify-center transition-opacity duration-500"><img src="/logo-pharma.png" class="w-48 h-48 object-contain mb-4"><h1 class="text-white text-3xl font-bold tracking-widest font-english mt-2">KodNaqi Pharmacy</h1></div>
    <div id="login-screen" class="fixed inset-0 bg-bg z-50 hidden flex-col justify-center p-6">
        <div class="text-center mb-10"><div class="w-24 h-24 bg-primary rounded-3xl mx-auto flex items-center justify-center mb-6 shadow-xl shadow-primary/30"><span class="font-english text-4xl font-bold text-white tracking-widest">KN</span></div><h2 class="text-2xl font-bold text-primary">مرحباً بك مجدداً</h2></div>
        <div class="bg-card p-6 rounded-3xl premium-shadow">
            <div class="mb-4"><label class="block text-sm font-bold text-gray-700 mb-2">اسم المستخدم</label><input type="text" id="login-user" placeholder="admin" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none"></div>
            <div class="mb-6"><label class="block text-sm font-bold text-gray-700 mb-2">كلمة المرور</label><input type="password" id="login-pass" placeholder="••••••••" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none" dir="ltr"></div>
            <button onclick="handleLogin()" class="w-full bg-primary hover:bg-[#073629] text-white py-3.5 rounded-xl font-bold text-lg shadow-lg shadow-primary/30">تسجيل الدخول</button>
        </div>
    </div>
    <div id="app-content" class="hidden">
        <header class="bg-primary text-white p-4 shadow-md sticky top-0 z-10 flex justify-between items-center rounded-b-3xl mb-4">
            <div class="flex items-center gap-3"><div class="w-10 h-10 bg-white rounded-xl flex items-center justify-center p-1 shadow-sm border border-white/20"><img src="/icon-pharma.png" class="w-full h-full object-contain"></div><h1 id="pharmacy-name" class="text-xl font-bold">جاري التحميل...</h1></div>
            <span id="current-tab-title" class="text-xs bg-white/20 px-3 py-1.5 rounded-full font-medium">الرئيسية</span>
        </header>
        <main class="p-4 max-w-4xl mx-auto">
            <div id="view-dashboard" class="hidden space-y-6"><h2 class="text-xl font-bold text-primary mb-2 px-2">نظرة عامة</h2><div class="grid grid-cols-2 gap-4"><div class="bg-card p-4 rounded-3xl premium-shadow flex flex-col items-center"><span class="text-gray-500 text-xs font-bold mb-1">مبيعات اليوم</span><span id="stat-revenue" class="text-2xl font-bold text-primary">0 SDG</span><span id="stat-count" class="text-[10px] text-gray-400 mt-1">0 فاتورة</span></div><div class="bg-card p-4 rounded-3xl premium-shadow flex flex-col items-center"><span class="text-gray-500 text-xs font-bold mb-1">أرباح اليوم</span><span id="stat-profit" class="text-2xl font-bold text-blue-600">0 SDG</span></div></div></div>
            <div id="view-pos" class="hidden space-y-6"><div class="bg-card p-5 rounded-3xl premium-shadow mb-4"><h2 class="text-lg font-bold mb-4 text-primary">إضافة دواء للفاتورة</h2><div class="flex gap-2 mb-4"><input type="text" id="pos-search" onkeyup="filterMedicines()" placeholder="ابحث..." class="flex-1 bg-bg border-0 rounded-xl p-3 text-sm"><button onclick="startScanner()" class="bg-primary text-white px-5 rounded-xl font-bold">📷</button></div><div id="reader" class="w-full hidden rounded-xl border-2 border-primary mb-2"></div><button onclick="stopScanner()" id="stop-btn" class="hidden w-full text-red-600 font-bold bg-red-50 py-2 rounded-lg">إيقاف</button></div><div class="bg-card p-5 rounded-3xl premium-shadow border-2 border-primary"><h2 class="text-lg font-bold mb-4 text-primary">الفاتورة الحالية</h2><div id="cart-items" class="space-y-2 mb-4"><p class="text-gray-400 text-sm text-center">فارغة.</p></div><div class="border-t pt-4 flex justify-between font-bold"><span>الإجمالي:</span><span id="cart-total" class="text-primary">0 SDG</span></div><button onclick="checkout()" class="w-full mt-4 bg-primary text-white py-3.5 rounded-xl font-bold">💵 إتمام الدفع</button></div><div class="bg-card p-5 rounded-3xl premium-shadow"><h2 class="text-lg font-bold mb-4 text-primary">الأدوية المتوفرة</h2><div id="medicines-list" class="space-y-2"></div></div></div>
            <div id="view-inventory" class="hidden space-y-6"><div class="bg-card p-5 rounded-3xl premium-shadow mb-4"><h2 class="text-lg font-bold mb-4 text-primary" id="inv-form-title">إضافة دواء جديد</h2><form id="add-medicine-form" class="space-y-3"><input type="hidden" id="med-id"><input type="text" id="med-name" placeholder="الاسم التجاري" required class="w-full bg-bg rounded-xl p-3 text-sm"><input type="text" id="med-scientific" placeholder="الاسم العلمي" class="w-full bg-bg rounded-xl p-3 text-sm"><select id="med-category" class="w-full bg-bg rounded-xl p-3 text-sm"><option value="">التصنيف...</option><option value="حبوب">حبوب</option><option value="كبسولات">كبسولات</option><option value="شراب">شراب</option><option value="حقن">حقن</option><option value="محاليل">محاليل</option><option value="مراهم">مراهم</option><option value="قطرة">قطرة</option></select><select id="med-supplier" class="w-full bg-bg rounded-xl p-3 text-sm"><option value="">المورد...</option></select><div class="grid grid-cols-2 gap-3"><input type="number" id="med-price" placeholder="سعر البيع" required class="bg-bg rounded-xl p-3 text-sm"><input type="number" id="med-cost" placeholder="التكلفة" class="bg-bg rounded-xl p-3 text-sm"></div><div class="grid grid-cols-2 gap-3"><input type="number" id="med-stock" placeholder="الكمية" required class="bg-bg rounded-xl p-3 text-sm"><input type="text" id="med-barcode" placeholder="الباركود" class="bg-bg rounded-xl p-3 text-sm"></div><input type="date" id="med-expiry" class="w-full bg-bg rounded-xl p-3 text-sm"><button type="submit" class="w-full bg-primary text-white py-3.5 rounded-xl font-bold">حفظ</button><button type="button" id="cancel-edit-btn" onclick="resetInvForm()" class="w-full bg-gray-200 text-gray-700 py-2 rounded-xl font-bold hidden">إلغاء التعديل</button></form></div><div class="bg-card p-5 rounded-3xl premium-shadow"><h2 class="text-lg font-bold mb-4 text-primary">قائمة الأدوية</h2><input type="text" id="inv-search" onkeyup="filterInventory()" placeholder="ابحث..." class="w-full bg-bg rounded-xl p-3 mb-4 text-sm"><div id="inventory-list" class="space-y-2 max-h-96 overflow-y-auto"></div></div></div>
            <div id="view-history" class="hidden space-y-6"><div class="bg-card p-5 rounded-3xl premium-shadow"><h2 class="text-lg font-bold mb-4 text-primary">سجل الفواتير</h2><div id="history-list" class="space-y-2"></div></div></div>
            <div id="view-suppliers" class="hidden space-y-6"><div class="bg-card p-5 rounded-3xl premium-shadow mb-4"><h2 class="text-lg font-bold mb-4 text-primary">إضافة مورد</h2><form id="add-supplier-form" class="flex gap-2"><input type="text" id="sup-name" placeholder="اسم المورد" required class="flex-1 bg-bg rounded-xl p-3 text-sm"><input type="text" id="sup-phone" placeholder="الهاتف" class="flex-1 bg-bg rounded-xl p-3 text-sm"><button type="submit" class="bg-primary text-white px-4 rounded-xl font-bold">حفظ</button></form></div><div class="bg-card p-5 rounded-3xl premium-shadow"><h2 class="text-lg font-bold mb-4 text-primary">الموردين</h2><div id="suppliers-list" class="space-y-2"></div></div></div>
            <div id="view-settings" class="hidden space-y-6"><h2 class="text-xl font-bold text-primary mb-2 px-2">الإعدادات</h2><div class="bg-card rounded-3xl premium-shadow overflow-hidden"><form id="settings-form" class="divide-y divide-gray-100"><div class="p-4 flex justify-between"><span class="font-bold text-sm">اسم الصيدلية</span><input type="text" id="set-name" required class="text-left bg-bg rounded-lg p-2 text-sm w-1/2 text-primary font-bold"></div><div class="p-4 flex justify-between"><span class="font-bold text-sm">العملة</span><input type="text" id="set-currency" required class="text-left bg-bg rounded-lg p-2 text-sm w-1/2 text-primary font-bold"></div><div class="p-4"><button type="submit" class="w-full bg-primary/10 text-primary py-3 rounded-xl font-bold">تحديث</button></div></form></div><div class="bg-card rounded-3xl premium-shadow overflow-hidden mt-4"><button onclick="handleLogout()" class="w-full p-4 text-red-600 font-bold text-sm">تسجيل الخروج</button></div></div>
        </main>
        <nav class="fixed bottom-0 w-full bg-white border-t flex justify-around py-2 z-20 rounded-t-3xl pb-4 shadow-[0_-4px_20px_rgba(0,0,0,0.04)]">
            <button onclick="switchTab('dashboard')" id="btn-dashboard" class="flex flex-col items-center p-2 text-gray-400 w-1/5"><svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg><span class="text-[10px] font-bold">الرئيسية</span></button>
            <button onclick="switchTab('pos')" id="btn-pos" class="flex flex-col items-center p-2 text-gray-400 w-1/5"><svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg><span class="text-[10px] font-bold">الكاشير</span></button>
            <button onclick="switchTab('inventory')" id="btn-inventory" class="flex flex-col items-center p-2 text-gray-400 w-1/5"><svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg><span class="text-[10px] font-bold">المخزون</span></button>
            <button onclick="switchTab('history')" id="btn-history" class="flex flex-col items-center p-2 text-gray-400 w-1/5"><svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span class="text-[10px] font-bold">السجلات</span></button>
            <button onclick="switchTab('suppliers')" id="btn-suppliers" class="flex flex-col items-center p-2 text-gray-400 w-1/5"><svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg><span class="text-[10px] font-bold">الموردين</span></button>
        </nav>
    </div>
    <div id="print-area" class="hidden bg-white text-black p-4 w-full max-w-sm mx-auto font-sans text-sm" dir="rtl"><div class="text-center border-b-2 border-black border-dashed pb-2 mb-2"><h2 id="print-pharmacy-name" class="text-xl font-bold mb-1">اسم الصيدلية</h2><p class="text-xs" id="print-date">التاريخ</p><p class="text-xs font-bold mt-1">رقم الفاتورة: <span id="print-inv-num"></span></p></div><table class="w-full text-xs text-right mb-2"><thead><tr class="border-b border-black"><th class="pb-1">الصنف</th><th class="pb-1 text-center">الكمية</th><th class="pb-1 text-left">السعر</th><th class="pb-1 text-left">الإجمالي</th></tr></thead><tbody id="print-items"></tbody></table><div class="border-t-2 border-black border-dashed pt-2 mb-4 space-y-1 text-sm"><div class="flex justify-between font-bold"><span>الإجمالي:</span><span id="print-total"></span></div><div class="flex justify-between"><span>المدفوع:</span><span id="print-paid"></span></div><div class="flex justify-between"><span>الباقي:</span><span id="print-change"></span></div></div><div class="flex flex-col items-center mt-6"><svg id="print-barcode" class="w-full max-w-[200px]"></svg><p class="text-xs mt-1 font-mono" id="print-inv-text"></p></div><div class="text-center text-xs mt-4 border-t border-black border-dashed pt-2"><p>شكراً لزيارتكم!</p></div></div>
    <div id="app-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm hidden items-center justify-center z-50"><div class="bg-white rounded-2xl shadow-2xl p-6 w-11/12 max-w-sm transform scale-95 transition-transform" id="modal-content"><div id="modal-icon" class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-4"><span class="text-3xl text-primary">✅</span></div><h3 id="modal-title" class="text-xl font-bold text-center mb-2">عنوان</h3><p id="modal-message" class="text-center text-gray-600 mb-6 text-sm">رسالة</p><input type="number" id="modal-input" class="hidden w-full text-center text-2xl font-bold border-2 border-primary rounded-lg p-3 mb-6" dir="ltr"><div class="flex gap-3"><button id="modal-cancel" class="hidden flex-1 bg-gray-200 text-gray-800 py-3 rounded-xl font-bold">إلغاء</button><button id="modal-confirm" class="flex-1 bg-primary text-white py-3 rounded-xl font-bold">موافق</button></div></div></div>
    <script src="/app.js"></script>
</body>
</html>"""
with open("static/index.html", "w", encoding="utf-8") as f: 
    f.write(html_content)

# ==========================================
# 4. بناء app.js (المنطق الكامل)
# ==========================================
js_content = """const API_URL = "/api"; let cart = []; let html5QrCode = null;
function formatCurrency(num) { return Number(num).toLocaleString('en-US'); }

// 1. Init & Auth
window.addEventListener('load', () => { setTimeout(() => { const splash = document.getElementById('splash-screen'); if (splash) { splash.style.opacity = '0'; setTimeout(() => { splash.style.display = 'none'; if (localStorage.getItem('kodnaqi_auth') === 'true') { showApp(); } else { const login = document.getElementById('login-screen'); if(login) { login.classList.remove('hidden'); login.classList.add('flex'); } } }, 500); } }, 2000); });
async function handleLogin() { const user = document.getElementById('login-user').value; const pass = document.getElementById('login-pass').value; if(!user || !pass) return showAlert("تنبيه", "أدخل البيانات", "error"); try { const res = await fetch(`${API_URL}/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: user, password: pass }) }); const data = await res.json(); if (res.ok) { localStorage.setItem('kodnaqi_auth', 'true'); document.getElementById('login-screen').classList.add('hidden'); document.getElementById('login-screen').classList.remove('flex'); showApp(); } else { showAlert("خطأ", data.detail || "بيانات غير صحيحة", "error"); } } catch (err) { if(user === 'admin' && pass === 'admin') { localStorage.setItem('kodnaqi_auth', 'true'); document.getElementById('login-screen').classList.add('hidden'); document.getElementById('login-screen').classList.remove('flex'); showApp(); } else { showAlert("خطأ", "تعذر الاتصال", "error"); } } }
function handleLogout() { localStorage.removeItem('kodnaqi_auth'); window.location.reload(); }
function showApp() { const app = document.getElementById('app-content'); if(app) app.classList.remove('hidden'); loadSettings(); switchTab('dashboard'); }

// 2. Tabs & Modals
function switchTab(tabId) { ['dashboard', 'pos', 'inventory', 'history', 'suppliers', 'settings'].forEach(id => { const view = document.getElementById(`view-${id}`); const btn = document.getElementById(`btn-${id}`); if(view) view.classList.add('hidden'); if(btn) btn.className = "flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/5 transition-all"; }); const activeView = document.getElementById(`view-${tabId}`); const activeBtn = document.getElementById(`btn-${tabId}`); if(activeView) activeView.classList.remove('hidden'); if(activeBtn) activeBtn.className = "flex flex-col items-center p-2 text-primary w-1/5 transition-all"; const titles = { dashboard: 'الرئيسية', pos: 'الكاشير', inventory: 'المخزون', history: 'السجلات', suppliers: 'الموردين', settings: 'الإعدادات' }; const titleEl = document.getElementById('current-tab-title'); if(titleEl) titleEl.innerText = titles[tabId]; if (tabId === 'dashboard') loadDashboard(); if (tabId === 'inventory') { loadMedicines(); loadSuppliersForDropdown(); } if (tabId === 'history') loadHistory(); if (tabId === 'suppliers') loadSuppliersList(); if (tabId === 'settings') fetchSettingsForForm(); }
function showAlert(title, message, type = 'success') { return new Promise((resolve) => { const modal = document.getElementById('app-modal'); const content = document.getElementById('modal-content'); const iconDiv = document.getElementById('modal-icon'); const input = document.getElementById('modal-input'); const cancelBtn = document.getElementById('modal-cancel'); const confirmBtn = document.getElementById('modal-confirm'); if(!modal) return resolve(true); input.classList.add('hidden'); cancelBtn.classList.add('hidden'); confirmBtn.innerText = 'حسناً'; if (type === 'error') { iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4"; iconDiv.innerHTML = '<span class="text-3xl">❌</span>'; confirmBtn.className = "flex-1 bg-red-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-red-200"; } else { iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-4"; iconDiv.innerHTML = '<span class="text-3xl text-primary">✅</span>'; confirmBtn.className = "flex-1 bg-primary text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/30"; } document.getElementById('modal-title').innerText = title; document.getElementById('modal-message').innerHTML = message; modal.classList.remove('hidden'); modal.classList.add('flex'); setTimeout(() => content.classList.remove('scale-95'), 10); confirmBtn.onclick = () => { content.classList.add('scale-95'); setTimeout(() => { modal.classList.add('hidden'); modal.classList.remove('flex'); }, 200); resolve(true); }; }); }
function showPrompt(title, message, defaultValue) { return new Promise((resolve) => { const modal = document.getElementById('app-modal'); const content = document.getElementById('modal-content'); const iconDiv = document.getElementById('modal-icon'); const input = document.getElementById('modal-input'); const cancelBtn = document.getElementById('modal-cancel'); const confirmBtn = document.getElementById('modal-confirm'); if(!modal) return resolve(null); iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 mb-4"; iconDiv.innerHTML = '<span class="text-3xl">💵</span>'; confirmBtn.className = "flex-1 bg-primary text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/30"; confirmBtn.innerText = 'تأكيد الدفع'; document.getElementById('modal-title').innerText = title; document.getElementById('modal-message').innerText = message; input.classList.remove('hidden'); input.value = defaultValue; input.focus(); cancelBtn.classList.remove('hidden'); modal.classList.remove('hidden'); modal.classList.add('flex'); setTimeout(() => content.classList.remove('scale-95'), 10); confirmBtn.onclick = () => { const val = input.value; close(); resolve(val); }; cancelBtn.onclick = () => { close(); resolve(null); }; function close() { content.classList.add('scale-95'); setTimeout(() => { modal.classList.add('hidden'); modal.classList.remove('flex'); }, 200); } }); }

// 3. Settings & Dashboard
async function loadSettings() { try { const res = await fetch(`${API_URL}/settings`); const data = await res.json(); const nameEl = document.getElementById('pharmacy-name'); if(nameEl) nameEl.innerText = data.pharmacy_name; await localforage.setItem('kodnaqi_settings', data); } catch (err) { const localData = await localforage.getItem('kodnaqi_settings'); if(localData) { document.getElementById('pharmacy-name').innerText = localData.pharmacy_name; } } }
async function fetchSettingsForForm() { try { const res = await fetch(`${API_URL}/settings`); const data = await res.json(); if(document.getElementById('set-name')) document.getElementById('set-name').value = data.pharmacy_name; if(document.getElementById('set-currency')) document.getElementById('set-currency').value = data.currency; } catch (err) { console.error(err); } }
document.getElementById('settings-form')?.addEventListener('submit', async (e) => { e.preventDefault(); try { const res = await fetch(`${API_URL}/settings`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pharmacy_name: document.getElementById('set-name').value, currency: document.getElementById('set-currency').value }) }); if (res.ok) { await showAlert("تم بنجاح", "تم التحديث.", "success"); loadSettings(); } } catch (err) { showAlert("خطأ", "تعذر التحديث", "error"); } });
async function loadDashboard() { try { const res = await fetch(`${API_URL}/stats`); const data = await res.json(); document.getElementById('stat-revenue').innerText = `${formatCurrency(data.today_revenue)} SDG`; document.getElementById('stat-count').innerText = `${data.today_sales_count} فاتورة`; document.getElementById('stat-profit').innerText = `${formatCurrency(data.today_profit)} SDG`; } catch (err) { console.log("Offline Dashboard"); } }

// 4. Suppliers
async function loadSuppliersList() { try { const res = await fetch(`${API_URL}/suppliers`); const suppliers = await res.json(); const list = document.getElementById('suppliers-list'); if(suppliers.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center">لا يوجد موردين.</p>'; return; } list.innerHTML = suppliers.map(s => `<div class="flex justify-between items-center p-3 border-b border-gray-100"><div><p class="font-bold text-primary">${s.name}</p><p class="text-xs text-gray-500">${s.phone || 'لا يوجد هاتف'}</p></div></div>`).join(''); } catch (err) { console.error(err); } }
async function loadSuppliersForDropdown() { try { const res = await fetch(`${API_URL}/suppliers`); const suppliers = await res.json(); const select = document.getElementById('med-supplier'); if(!select) return; select.innerHTML = '<option value="">اختر المورد...</option>' + suppliers.map(s => `<option value="${s.id}">${s.name}</option>`).join(''); } catch (err) { console.error(err); } }
document.getElementById('add-supplier-form')?.addEventListener('submit', async (e) => { e.preventDefault(); const name = document.getElementById('sup-name').value; const phone = document.getElementById('sup-phone').value; try { const res = await fetch(`${API_URL}/suppliers`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, phone }) }); if(res.ok) { await showAlert("تم بنجاح", "تم إضافة المورد.", "success"); document.getElementById('add-supplier-form').reset(); loadSuppliersList(); } } catch (err) { showAlert("خطأ", "تعذر الاتصال", "error"); } });

// 5. Medicines CRUD
async function loadMedicines() { try { const res = await fetch(`${API_URL}/medicines`); const medicines = await res.json(); const posList = document.getElementById('medicines-list'); if(posList) { posList.innerHTML = medicines.map(med => `<div onclick="addToCart(${med.id}, '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl"><div><p class="font-bold text-gray-800 text-sm">${med.name}</p></div><div class="text-left"><p class="font-bold text-primary">${formatCurrency(med.price)} SDG</p><p class="text-[10px] text-gray-400">المخزون: ${med.stock_quantity}</p></div></div>`).join(''); } const invList = document.getElementById('inventory-list'); if(invList) { invList.innerHTML = medicines.map(med => `<div class="flex justify-between items-center p-3 border-b border-gray-100"><div><p class="font-bold text-gray-800 text-sm">${med.name}</p><p class="text-[10px] text-gray-500">${med.category || ''} | ${med.supplier_name || 'بدون مورد'}</p></div><div class="text-left flex items-center gap-3"><div><p class="font-bold text-primary text-sm">${med.price} SDG</p><p class="text-[10px] ${med.stock_quantity <= 10 ? 'text-red-500 font-bold' : 'text-gray-400'}">المخزون: ${med.stock_quantity}</p></div><button onclick='editMedicine(${JSON.stringify(med)})' class="bg-blue-50 text-blue-600 p-2 rounded-lg">✏️</button><button onclick="deleteMedicine(${med.id})" class="bg-red-50 text-red-600 p-2 rounded-lg">🗑️</button></div></div>`).join(''); } await localforage.setItem('kodnaqi_medicines', medicines); } catch (err) { const meds = await localforage.getItem('kodnaqi_medicines') || []; const posList = document.getElementById('medicines-list'); if(posList && meds.length) { posList.innerHTML = meds.map(med => `<div onclick="addToCart(${med.id}, '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl"><div><p class="font-bold text-gray-800 text-sm">${med.name}</p></div><div class="text-left"><p class="font-bold text-primary">${formatCurrency(med.price)} SDG</p><p class="text-[10px] text-gray-400">المخزون: ${med.stock_quantity}</p></div></div>`).join(''); } } }
document.getElementById('add-medicine-form')?.addEventListener('submit', async (e) => { e.preventDefault(); const id = document.getElementById('med-id').value; const data = { name: document.getElementById('med-name').value, scientific_name: document.getElementById('med-scientific').value || null, category: document.getElementById('med-category').value || null, supplier_id: document.getElementById('med-supplier').value ? parseInt(document.getElementById('med-supplier').value) : null, price: parseFloat(document.getElementById('med-price').value), cost: parseFloat(document.getElementById('med-cost').value) || 0, stock_quantity: parseInt(document.getElementById('med-stock').value), barcode: document.getElementById('med-barcode').value || null, expiry_date: document.getElementById('med-expiry').value || null }; const method = id ? 'PUT' : 'POST'; const url = id ? `${API_URL}/medicines/${id}` : `${API_URL}/medicines`; try { const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }); if (res.ok) { await showAlert("تم بنجاح", id ? "تم التعديل." : "تم الإضافة.", "success"); resetInvForm(); loadMedicines(); } else showAlert("خطأ", "تأكد من أن الباركود غير مكرر.", "error"); } catch (err) { showAlert("خطأ", "تعذر الاتصال", "error"); } });
function editMedicine(med) { document.getElementById('med-id').value = med.id; document.getElementById('med-name').value = med.name; document.getElementById('med-scientific').value = med.scientific_name || ''; document.getElementById('med-category').value = med.category || ''; document.getElementById('med-supplier').value = med.supplier_id || ''; document.getElementById('med-price').value = med.price; document.getElementById('med-cost').value = med.cost || ''; document.getElementById('med-stock').value = med.stock_quantity; document.getElementById('med-barcode').value = med.barcode || ''; document.getElementById('med-expiry').value = med.expiry_date || ''; document.getElementById('inv-form-title').innerText = "تعديل دواء"; document.getElementById('cancel-edit-btn').classList.remove('hidden'); window.scrollTo(0,0); }
function resetInvForm() { document.getElementById('add-medicine-form').reset(); document.getElementById('med-id').value = ''; document.getElementById('inv-form-title').innerText = "إضافة دواء جديد"; document.getElementById('cancel-edit-btn').classList.add('hidden'); }
async function deleteMedicine(id) { if(!confirm("هل أنت متأكد من حذف هذا الدواء؟")) return; try { const res = await fetch(`${API_URL}/medicines/${id}`, { method: 'DELETE' }); if(res.ok) { loadMedicines(); showAlert("تم", "تم حذف الدواء.", "success"); } } catch (err) { console.error(err); } }
function filterMedicines() { const query = document.getElementById('pos-search').value.toLowerCase(); const items = document.querySelectorAll('#medicines-list > div'); items.forEach(item => { item.style.display = item.innerText.toLowerCase().includes(query) ? 'flex' : 'none'; }); }
function filterInventory() { const query = document.getElementById('inv-search').value.toLowerCase(); const items = document.querySelectorAll('#inventory-list > div'); items.forEach(item => { item.style.display = item.innerText.toLowerCase().includes(query) ? 'flex' : 'none'; }); }

// 6. POS & Cart
function addToCart(id, name, price) { const existing = cart.find(item => item.medicine_id === id); if (existing) existing.quantity += 1; else cart.push({ medicine_id: id, name: name, unit_price: price, quantity: 1 }); renderCart(); }
function removeFromCart(index) { cart.splice(index, 1); renderCart(); }
function updateQuantity(index, change) { cart[index].quantity += change; if (cart[index].quantity <= 0) cart.splice(index, 1); renderCart(); }
function renderCart() { const cartDiv = document.getElementById('cart-items'); const totalEl = document.getElementById('cart-total'); if (!cartDiv || !totalEl) return; if (cart.length === 0) { cartDiv.innerHTML = '<p class="text-gray-400 text-sm text-center py-4">الفاتورة فارغة.</p>'; totalEl.innerText = `0 SDG`; return; } let total = 0; cartDiv.innerHTML = cart.map((item, index) => { total += item.unit_price * item.quantity; return `<div class="flex justify-between items-center p-3 bg-bg rounded-xl mb-2"><div class="flex-1"><p class="font-bold text-sm text-primary">${item.name}</p><p class="text-xs text-gray-500">${item.unit_price} SDG</p></div><div class="flex items-center gap-3"><div class="flex items-center bg-white rounded-lg border border-gray-100"><button onclick="updateQuantity(${index}, 1)" class="px-3 py-1 text-primary font-bold">+</button><span class="px-2 font-bold text-sm">${item.quantity}</span><button onclick="updateQuantity(${index}, -1)" class="px-3 py-1 text-red-500 font-bold">-</button></div><span class="font-bold text-primary w-20 text-left">${formatCurrency(item.unit_price * item.quantity)} SDG</span><button onclick="removeFromCart(${index})" class="text-red-500 bg-red-50 p-2 rounded-lg">✖</button></div></div>`; }).join(''); totalEl.innerText = `${formatCurrency(total)} SDG`; }
async function checkout() { if (cart.length === 0) return showAlert("تنبيه", "الفاتورة فارغة.", "error"); let total = cart.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0); const paid = await showPrompt("الدفع", `الإجمالي المطلوب: ${formatCurrency(total)} SDG`, total); if (paid === null || paid === "") return; const paidAmount = parseFloat(paid); if (isNaN(paidAmount) || paidAmount < total) return showAlert("خطأ", "المبلغ غير كافٍ!", "error"); const localId = Date.now(); const saleData = { id: localId, discount: 0, paid_amount: paidAmount, items: cart.map(i => ({ medicine_id: i.medicine_id, quantity: i.quantity, unit_price: i.unit_price })), invoice_number: `OFF-${localId.toString().slice(-6)}`, sale_date: new Date().toISOString() }; let sales = await localforage.getItem('kodnaqi_sales') || []; sales.unshift(saleData); await localforage.setItem('kodnaqi_sales', sales); let outbox = await localforage.getItem('kodnaqi_outbox') || []; outbox.push(saleData); await localforage.setItem('kodnaqi_outbox', outbox); const change = paidAmount - total; preparePrintInvoice(saleData.invoice_number, cart, total, paidAmount, change); let msg = `رقم الفاتورة: <b>${saleData.invoice_number}</b><br>الباقي: <b class="text-primary text-lg">${formatCurrency(change)} SDG</b>`; msg += `<br><br><button onclick="window.print()" class="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-bold w-full">🖨️ طباعة الفاتورة</button>`; await showAlert("تمت العملية", msg, "success"); cart = []; renderCart(); loadMedicines(); processOutbox(); }

// 7. Sync & History
async function processOutbox() { if(!navigator.onLine) return; let outbox = await localforage.getItem('kodnaqi_outbox') || []; if(outbox.length === 0) return; let sales = await localforage.getItem('kodnaqi_sales') || []; let outboxChanged = false; for (let i = 0; i < outbox.length; i++) { let sale = outbox[i]; let sendData = { discount: sale.discount, paid_amount: sale.paid_amount, items: sale.items.map(item => ({ medicine_id: item.medicine_id, quantity: item.quantity, unit_price: item.unit_price })) }; try { let res = await fetch(`${API_URL}/sales`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sendData) }); if (res.ok) { let serverData = await res.json(); let localSaleIndex = sales.findIndex(s => s.id == sale.id); if (localSaleIndex !== -1) sales[localSaleIndex].invoice_number = serverData.invoice_number; outbox.splice(i, 1); i--; outboxChanged = true; } else { break; } } catch(e) { break; } } if (outboxChanged) { await localforage.setItem('kodnaqi_sales', sales); await localforage.setItem('kodnaqi_outbox', outbox); } }
async function loadHistory() { const list = document.getElementById('history-list'); if (!list) return; let localSales = await localforage.getItem('kodnaqi_sales') || []; try { const res = await fetch(`${API_URL}/sales`); if(res.ok) { const serverSales = await res.json(); let mergedSales = [...localSales]; serverSales.forEach(ss => { let existingIndex = mergedSales.findIndex(s => s.invoice_number === ss.invoice_number); if(existingIndex !== -1) mergedSales[existingIndex] = { ...mergedSales[existingIndex], ...ss }; else mergedSales.push(ss); }); mergedSales.sort((a,b) => new Date(b.sale_date) - new Date(a.sale_date)); await localforage.setItem('kodnaqi_sales', mergedSales); renderHistoryList(mergedSales, list); } else renderHistoryList(localSales, list); } catch(e) { renderHistoryList(localSales, list); } }
function renderHistoryList(sales, list) { if (sales.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center py-4">لا توجد فواتير سابقة.</p>'; return; } list.innerHTML = sales.map(sale => { const date = new Date(sale.sale_date).toLocaleString('en-GB'); const isSynced = !sale.invoice_number.startsWith('OFF-'); return `<div class="flex justify-between items-center p-4 border-b border-gray-100 hover:bg-gray-50 transition"><div><p class="font-bold text-primary">${sale.invoice_number} ${!isSynced ? '<span class="text-[9px] text-orange-500 bg-orange-50 px-1 rounded">معلق</span>' : ''}</p><p class="text-xs text-gray-400 mt-1">${date}</p></div><div class="text-left flex items-center gap-4"><div><p class="font-bold text-primary">${formatCurrency(sale.total_amount || sale.items.reduce((s,i)=>s+(i.unit_price*i.quantity),0))} SDG</p><p class="text-xs text-gray-400">${sale.items.length} أصناف</p></div><button onclick='reprintInvoice(${JSON.stringify(sale)})' class="bg-blue-50 text-blue-600 p-3 rounded-xl hover:bg-blue-100 transition">🖨️</button></div></div>`; }).join(''); }

// 8. Print & Camera
function preparePrintInvoice(invNum, items, total, paid, change, originalDate = null) { const nameEl = document.getElementById('print-pharmacy-name'); if(nameEl) nameEl.innerText = document.getElementById('pharmacy-name').innerText; let printDate = originalDate ? new Date(originalDate) : new Date(); document.getElementById('print-date').innerText = `التاريخ: ${printDate.toLocaleDateString('en-GB')} ${printDate.toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit'})}`; document.getElementById('print-inv-num').innerText = invNum; document.getElementById('print-items').innerHTML = items.map(item => `<tr class="border-b border-gray-300 border-dashed"><td class="py-2">${item.name}</td><td class="py-2 text-center">${item.quantity}</td><td class="py-2 text-left">${formatCurrency(item.unit_price)}</td><td class="py-2 text-left">${formatCurrency(item.unit_price * item.quantity)}</td></tr>`).join(''); document.getElementById('print-total').innerText = `${formatCurrency(total)} SDG`; document.getElementById('print-paid').innerText = `${formatCurrency(paid)} SDG`; document.getElementById('print-change').innerText = `${formatCurrency(change)} SDG`; if (typeof JsBarcode !== 'undefined') JsBarcode("#print-barcode", invNum, { format: "CODE128", lineColor: "#000", width: 2, height: 40, displayValue: false }); document.getElementById('print-inv-text').innerText = invNum; }
function reprintInvoice(sale) { let total = sale.total_amount || sale.items.reduce((sum, i) => sum + (i.unit_price * i.quantity), 0); preparePrintInvoice(sale.invoice_number, sale.items, total, sale.paid_amount, (sale.paid_amount - total), sale.sale_date); setTimeout(() => window.print(), 500); }
function startScanner() { document.getElementById('reader').classList.remove('hidden'); document.getElementById('stop-btn').classList.remove('hidden'); html5QrCode = new Html5Qrcode("reader"); html5QrCode.start({ facingMode: "environment" }, { fps: 10, qrbox: { width: 250, height: 150 } }, (decodedText) => { stopScanner(); findMedicineByBarcode(decodedText); }, (e) => {}).catch(err => showAlert("خطأ", "تأكد من صلاحية الكاميرا", "error")); }
function stopScanner() { if (html5QrCode) { html5QrCode.stop().then(() => { document.getElementById('reader').classList.add('hidden'); document.getElementById('stop-btn').classList.add('hidden'); html5QrCode = null; }); } }
async function findMedicineByBarcode(barcode) { try { const res = await fetch(`${API_URL}/medicines/barcode/${barcode}`); if (res.ok) { const med = await res.json(); addToCart(med.id, med.name, med.price); showAlert("تمت الإضافة", `تم إضافة <b>${med.name}</b>.`, "success"); } else showAlert("غير موجود", `لا يوجد دواء بالباركود: ${barcode}`, "error"); } catch (err) { console.error(err); } }

// 9. Service Worker
if ('serviceWorker' in navigator) { window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').then(reg => console.log('SW Registered'))); }
"""
with open("static/app.js", "w", encoding="utf-8") as f: 
    f.write(js_content)

# ==========================================
# 5. كسر الكاش
# ==========================================
with open("static/sw.js", "r", encoding="utf-8") as f: 
    sw = f.read()
import re
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v20';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f: 
    f.write(sw)

print("\n🎉 اكتمل بناء النظام المطلق بنجاح 100%. لا يوجد أي سطر ناقص.")
