import os

print("⏳ جاري إصلاح السطر التالف في main.py...")

with open("main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# البحث عن مكان دالة الإحصائيات لقص الملف من هناك
new_lines = []
skip = False
for line in lines:
    if '@app.get("/api/stats")' in line:
        skip = True
    
    if not skip:
        new_lines.append(line)

# الآن نضيف دالة الإحصائيات والسطر الأخير بشكل نظيف ومضمون
clean_ending = '''
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
        profit_query = db.execute(\'\'\'
            SELECT SUM((si.unit_price - m.cost) * si.quantity) as total_profit
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN medicines m ON si.medicine_id = m.id
            WHERE s.sale_date LIKE ?
        \'\'\', (f"{today}%",)).fetchone()

        # تنبيهات المخزون (أقل من 10 حبات)
        low_stock = db.execute("SELECT id, name, stock_quantity FROM medicines WHERE stock_quantity <= 10").fetchall()
        
        # تنبيهات الصلاحية (تنتهي خلال 30 يوماً)
        expiring_soon = db.execute(\'\'\'
            SELECT id, name, expiry_date, stock_quantity 
            FROM medicines 
            WHERE expiry_date IS NOT NULL 
            AND expiry_date != '' 
            AND date(expiry_date) <= date('now', '+30 days')
            AND date(expiry_date) >= date('now')
        \'\'\').fetchall()

        # الأدوية المنتهية صلاحيتها
        expired = db.execute(\'\'\'
            SELECT id, name, expiry_date, stock_quantity 
            FROM medicines 
            WHERE expiry_date IS NOT NULL 
            AND expiry_date != '' 
            AND date(expiry_date) < date('now')
        \'\'\').fetchall()
        
        return {
            "today_sales_count": today_sales["count"] if today_sales else 0,
            "today_revenue": today_sales["total"] if today_sales and today_sales["total"] else 0,
            "today_profit": profit_query["total_profit"] if profit_query and profit_query["total_profit"] else 0,
            "low_stock_alerts": [dict(r) for r in low_stock],
            "expiring_soon_alerts": [dict(r) for r in expiring_soon],
            "expired_alerts": [dict(r) for r in expired]
        }

# تقديم ملفات الواجهة الأمامية (PWA)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
'''

new_lines.append(clean_ending)

with open("main.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ تم إصلاح main.py بنجاح! السطر التالف تمت إزالته.")
