import os
import re

print("⏳ جاري إضافة النسخ الاحتياطي وشاشات التحميل...")

# ==========================================
# 1. تحديث الباك-إند (main.py)
# ==========================================
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

backup_endpoints = '''
import csv
from io import StringIO
from fastapi.responses import Response

@app.get("/api/backup/sales")
def export_sales_csv(admin_user: dict = Depends(check_admin)):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT invoice_number, sale_date, total_amount, discount, paid_amount FROM sales ORDER BY id DESC")
            sales = cur.fetchall()
    
    output = StringIO()
    output.write('\ufeff') # لدعم اللغة العربية في الإكسيل
    writer = csv.writer(output)
    writer.writerow(["Invoice Number", "Date", "Total Amount", "Discount", "Paid Amount"])
    for s in sales:
        writer.writerow([s["invoice_number"], s["sale_date"], s["total_amount"], s["discount"], s["paid_amount"]])
    
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=kodnaqi_sales.csv"})

@app.get("/api/backup/medicines")
def export_medicines_csv(admin_user: dict = Depends(check_admin)):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT name, barcode, category, price, cost, stock_quantity, expiry_date FROM medicines ORDER BY name")
            meds = cur.fetchall()
            
    output = StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    writer.writerow(["Name", "Barcode", "Category", "Price", "Cost", "Stock", "Expiry Date"])
    for m in meds:
        writer.writerow([m["name"], m["barcode"], m["category"], m["price"], m["cost"], m["stock_quantity"], m["expiry_date"]])
        
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=kodnaqi_inventory.csv"})

'''

# حقن مسارات النسخ الاحتياطي قبل مسار الستاتيك
if 'from fastapi.staticfiles import StaticFiles' in main_code:
    main_code = main_code.replace('from fastapi.staticfiles import StaticFiles', backup_endpoints + 'from fastapi.staticfiles import StaticFiles')

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
print("✅ تم تحديث main.py (مسارات النسخ الاحتياطي).")

# ==========================================
# 2. تحديث الواجهة (index.html)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. إضافة قسم النسخ الاحتياطي في الإعدادات
backup_ui = """
                <!-- النسخ الاحتياطي -->
                <div class="bg-card rounded-3xl premium-shadow overflow-hidden mt-4">
                    <div class="p-4 border-b border-gray-100">
                        <h3 class="font-bold text-primary flex items-center gap-2">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4zm0 5c0 2.21 3.582 4 8 4s8-1.79 8-4"></path></svg>
                            النسخ الاحتياطي والبيانات
                        </h3>
                    </div>
                    <div class="divide-y divide-gray-100">
                        <button onclick="downloadBackup('sales')" class="w-full p-4 flex items-center justify-between text-gray-700 hover:bg-gray-50 transition">
                            <span class="font-bold text-sm">تصدير المبيعات (Excel)</span>
                            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                        </button>
                        <button onclick="downloadBackup('medicines')" class="w-full p-4 flex items-center justify-between text-gray-700 hover:bg-gray-50 transition">
                            <span class="font-bold text-sm">تصدير المخزون (Excel)</span>
                            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                        </button>
                    </div>
                </div>
"""
# إدخال قسم النسخ الاحتياطي قبل زر تسجيل الخروج
if '/api/backup/sales' not in html:
    html = html.replace(
        '<div class="bg-card rounded-3xl premium-shadow overflow-hidden"><button onclick="handleLogout()"',
        backup_ui + '\n                <div class="bg-card rounded-3xl premium-shadow overflow-hidden mt-4"><button onclick="handleLogout()"'
    )

# ب. إضافة شاشة التحميل (Loading Overlay)
loading_overlay = """
    <!-- شاشة التحميل -->
    <div id="loading-overlay" class="fixed inset-0 bg-black/40 backdrop-blur-sm hidden items-center justify-center z-[200]">
        <div class="bg-white p-6 rounded-3xl shadow-2xl flex flex-col items-center">
            <div class="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
            <p class="mt-4 font-bold text-primary text-sm">جاري المعالجة...</p>
        </div>
    </div>
"""
if 'id="loading-overlay"' not in html:
    html = html.replace('<div id="app-modal"', loading_overlay + '\n    <div id="app-modal"')

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html (قسم النسخ الاحتياطي وشاشة التحميل).")

# ==========================================
# 3. تحديث الجافاسكريبت (app.js)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# أ. تحديث دالة apiFetch لإظهار شاشة التحميل تلقائياً
new_apifetch = """
async function apiFetch(url, options = {}) {
    const loader = document.getElementById('loading-overlay');
    if (loader) { loader.classList.remove('hidden'); loader.classList.add('flex'); }
    
    try {
        options.headers = { ...getAuthHeaders(), ...options.headers };
        const res = await fetch(url, options);
        if (res.status === 401 || res.status === 403) {
            if(res.status === 401) { localStorage.removeItem('kodnaqi_token'); localStorage.removeItem('kodnaqi_role'); window.location.reload(); }
            else { const data = await res.json(); showAlert("ممنوع", data.detail || "ليس لديك صلاحية", "error"); throw new Error("Forbidden"); }
        }
        return res;
    } finally {
        if (loader) { loader.classList.add('hidden'); loader.classList.remove('flex'); }
    }
}
"""
js = re.sub(r'async function apiFetch\(url, options = \{\}\) \{.*?\n\}', new_apifetch, js, flags=re.DOTALL)

# ب. إضافة دالة تحميل النسخة الاحتياطية
backup_js = """
async function downloadBackup(type) {
    try {
        const loader = document.getElementById('loading-overlay');
        if (loader) { loader.classList.remove('hidden'); loader.classList.add('flex'); }
        
        const res = await fetch(`${API_URL}/backup/${type}`, { headers: getAuthHeaders() });
        if (!res.ok) throw new Error("Failed");
        
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `kodnaqi_${type}_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
        if (loader) { loader.classList.add('hidden'); loader.classList.remove('flex'); }
    } catch (err) {
        if (loader) { loader.classList.add('hidden'); loader.classList.remove('flex'); }
        showAlert("خطأ", "تعذر تحميل الملف", "error");
    }
}
"""
if 'async function downloadBackup' not in js:
    js += "\n" + backup_js

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js (النسخ الاحتياطي وشاشة التحميل).")

# 4. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v45';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v45.")

print("\n🎉 اكتملت اللمسات النهائية! ارفع الكود الآن.")
