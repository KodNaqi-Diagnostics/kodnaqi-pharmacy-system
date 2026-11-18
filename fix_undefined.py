import os
import re

print("⏳ جاري إصلاح مسارات الإعدادات وتقفيل الوردية...")

with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# الكود المفقود الذي سنقوم بحقنه
missing_endpoints = '''
# --- Z-Report ---
@app.get("/api/z-report")
def get_z_report(user: dict = Depends(get_current_user)):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT COUNT(id) as count, SUM(total_amount) as total FROM sales WHERE sale_date::date = CURRENT_DATE")
            today_sales = cur.fetchone()
            cur.execute("SELECT SUM((si.unit_price - m.cost) * si.quantity) as total_profit FROM sale_items si JOIN sales s ON si.sale_id = s.id JOIN medicines m ON si.medicine_id = m.id WHERE s.sale_date::date = CURRENT_DATE")
            profit = cur.fetchone()
            return {
                "date": str(datetime.now().date()),
                "total_sales": today_sales["total"] or 0,
                "total_invoices": today_sales["count"] or 0,
                "total_profit": profit["total_profit"] or 0
            }

# --- Settings ---
@app.get("/api/settings")
def get_settings(user: dict = Depends(get_current_user)):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM settings WHERE id=1")
            return dict(cur.fetchone())

@app.put("/api/settings")
def update_settings(data: SettingsIn, admin_user: dict = Depends(check_admin)):
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

'''

# حقن الكود المفقود قبل سطر تحميل ملفات الواجهة (StaticFiles)
if 'from fastapi.staticfiles import StaticFiles' in main_code:
    if 'def get_z_report' not in main_code:
        main_code = main_code.replace('from fastapi.staticfiles import StaticFiles', missing_endpoints + 'from fastapi.staticfiles import StaticFiles')
        print("✅ تمت إضافة مسارات الإعدادات وتقفيل الوردية بنجاح.")
    else:
        print("⚠️ المسارات موجودة مسبقاً.")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)

# كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v42';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v42.")
