import os
import re

print("⏳ جاري إضافة نظام النسخ الاحتياطي وتصدير Excel...")

# ==========================================
# 1. تحديث main.py (إضافة مسارات النسخ الاحتياطي)
# ==========================================
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

backup_endpoints = """
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
app.mount("/", StaticFiles(directory="static", html=True), name="static")
"""

# استبدال نهاية الملف
if 'app.mount' in main_code:
    main_code = re.sub(r'# تقديم ملفات الواجهة الأمامية \(PWA\)\s*app\.mount\([^)]+\)', backup_endpoints, main_code)
else:
    main_code += backup_endpoints

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
print("✅ تم تحديث main.py بمسارات النسخ الاحتياطي.")


# ==========================================
# 2. تحديث index.html (إضافة الأزرار في الإعدادات)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

backup_ui = """
                <!-- النسخ الاحتياطي -->
                <h3 class="text-sm font-bold text-gray-500 px-2 mt-6">النسخ الاحتياطي والبيانات</h3>
                <div class="bg-card rounded-3xl premium-shadow overflow-hidden mb-4">
                    <a href="/api/backup/database" download class="p-4 flex items-center justify-between border-b border-gray-100 hover:bg-gray-50 transition text-gray-700">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4zm0 5c0 2.21 3.582 4 8 4s8-1.79 8-4"></path></svg>
                            </div>
                            <span class="font-bold text-sm">تحميل قاعدة البيانات (SQLite)</span>
                        </div>
                        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    </a>
                    
                    <a href="/api/backup/sales-csv" download class="p-4 flex items-center justify-between hover:bg-gray-50 transition text-gray-700">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-green-50 rounded-full flex items-center justify-center text-green-600">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                            </div>
                            <span class="font-bold text-sm">تصدير المبيعات (Excel / CSV)</span>
                        </div>
                        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    </a>
                </div>
"""

# إدخال القسم قبل زر تسجيل الخروج
if '/api/backup/database' not in html:
    html = html.replace(
        '<!-- زر تسجيل الخروج -->',
        backup_ui + '\n                <!-- زر تسجيل الخروج -->'
    )

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم إضافة أزرار النسخ الاحتياطي في الإعدادات.")

# 3. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v10';", "const CACHE_NAME = 'kodnaqi-v11';")
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v11.")

print("\n🎉 اكتمل التحديث! أعد تشغيل السيرفر.")
