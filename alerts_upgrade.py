import os
import re

print("⏳ جاري إضافة نظام التنبيهات الذكية...")

# ==========================================
# 1. تحديث الباك-إند (main.py)
# ==========================================
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# استبدال دالة stats الحالية بدالة تحتوي على استعلامات التنبيه
new_stats_endpoint = '''
@app.get("/api/stats")
def get_stats(admin_user: dict = Depends(check_admin)):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT COUNT(id) as count, SUM(total_amount) as total FROM sales WHERE sale_date::date = CURRENT_DATE")
            today = cur.fetchone()
            cur.execute("SELECT SUM((si.unit_price - m.cost) * si.quantity) as total_profit FROM sale_items si JOIN sales s ON si.sale_id = s.id JOIN medicines m ON si.medicine_id = m.id WHERE s.sale_date::date = CURRENT_DATE")
            profit = cur.fetchone()
            
            # 1. نقص المخزون (أقل من 10)
            cur.execute("SELECT id, name, stock_quantity FROM medicines WHERE stock_quantity <= 10 ORDER BY stock_quantity ASC")
            low_stock = cur.fetchall()
            
            # 2. أوشكت على الانتهاء (خلال 30 يوم)
            cur.execute("SELECT id, name, expiry_date FROM medicines WHERE expiry_date IS NOT NULL AND expiry_date != '' AND expiry_date::date <= CURRENT_DATE + INTERVAL '30 days' AND expiry_date::date >= CURRENT_DATE ORDER BY expiry_date ASC")
            expiring = cur.fetchall()
            
            # 3. منتهية الصلاحية (اليوم وما قبله)
            cur.execute("SELECT id, name, expiry_date FROM medicines WHERE expiry_date IS NOT NULL AND expiry_date != '' AND expiry_date::date < CURRENT_DATE ORDER BY expiry_date ASC")
            expired = cur.fetchall()

            return {
                "today_sales_count": today["count"] or 0, 
                "today_revenue": today["total"] or 0, 
                "today_profit": profit["total_profit"] or 0, 
                "low_stock_alerts": [dict(r) for r in low_stock], 
                "expiring_soon_alerts": [dict(r) for r in expiring], 
                "expired_alerts": [dict(r) for r in expired]
            }
'''

# استبدال الدالة القديمة بالجديدة
main_code = re.sub(r'@app\.get\("/api/stats"\).*?(?=from fastapi\.staticfiles)', new_stats_endpoint + "\n", main_code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
print("✅ تم تحديث main.py بمنطق التنبيهات.")

# ==========================================
# 2. تحديث الواجهة (index.html)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# إضافة أقسام التنبيهات في لوحة التحكم
alerts_ui = """
                <!-- قسم التنبيهات -->
                <div id="alerts-container" class="space-y-4 mt-6">
                    <!-- منتهية الصلاحية -->
                    <div id="expired-container" class="bg-card p-5 rounded-3xl premium-shadow border-r-4 border-red-500 hidden">
                        <h3 class="font-bold text-red-600 mb-3 flex items-center gap-2">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                            أدوية منتهية الصلاحية (سحب فوري)
                        </h3>
                        <div id="expired-list" class="space-y-2 text-sm max-h-40 overflow-y-auto pr-2"></div>
                    </div>

                    <!-- أوشكت على الانتهاء -->
                    <div id="expiring-container" class="bg-card p-5 rounded-3xl premium-shadow border-r-4 border-orange-400 hidden">
                        <h3 class="font-bold text-orange-500 mb-3 flex items-center gap-2">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            تنتهي خلال 30 يوماً
                        </h3>
                        <div id="expiring-list" class="space-y-2 text-sm max-h-40 overflow-y-auto pr-2"></div>
                    </div>

                    <!-- نقص المخزون -->
                    <div id="lowstock-container" class="bg-card p-5 rounded-3xl premium-shadow border-r-4 border-yellow-400 hidden">
                        <h3 class="font-bold text-yellow-600 mb-3 flex items-center gap-2">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
                            أدوية أوشكت على النفاذ
                        </h3>
                        <div id="lowstock-list" class="space-y-2 text-sm max-h-40 overflow-y-auto pr-2"></div>
                    </div>
                </div>
"""
# إدخال التنبيهات بعد الإحصائيات
if 'id="alerts-container"' not in html:
    html = html.replace('</div>\n                <div class="bg-card p-5 rounded-3xl premium-shadow">\n                     <button onclick="printZReport()"', alerts_ui + '</div>\n                <div class="bg-card p-5 rounded-3xl premium-shadow">\n                     <button onclick="printZReport()"')

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html (إضافة واجهة التنبيهات).")

# ==========================================
# 3. تحديث الجافاسكريبت (app.js)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# تحديث دالة loadDashboard لمعالجة وعرض التنبيهات
new_dashboard_js = """
async function loadDashboard() { 
    try { 
        const res = await apiFetch(`${API_URL}/stats`); 
        const data = await res.json(); 
        document.getElementById('stat-revenue').innerText = `${formatCurrency(data.today_revenue)} SDG`; 
        document.getElementById('stat-count').innerText = `${data.today_sales_count} فاتورة`; 
        document.getElementById('stat-profit').innerText = `${formatCurrency(data.today_profit)} SDG`; 

        // 1. منتهية الصلاحية
        const expContainer = document.getElementById('expired-container');
        const expList = document.getElementById('expired-list');
        if (data.expired_alerts.length > 0) {
            expContainer.classList.remove('hidden');
            expList.innerHTML = data.expired_alerts.map(item => `<div class="flex justify-between p-2 bg-red-50 rounded-lg"><span class="font-bold text-gray-800">${item.name}</span><span class="text-red-600 font-bold text-xs">${item.expiry_date}</span></div>`).join('');
        } else { expContainer.classList.add('hidden'); }

        // 2. أوشكت على الانتهاء
        const exsoonContainer = document.getElementById('expiring-container');
        const exsoonList = document.getElementById('expiring-list');
        if (data.expiring_soon_alerts.length > 0) {
            exsoonContainer.classList.remove('hidden');
            exsoonList.innerHTML = data.expiring_soon_alerts.map(item => `<div class="flex justify-between p-2 bg-orange-50 rounded-lg"><span class="font-bold text-gray-800">${item.name}</span><span class="text-orange-600 font-bold text-xs">${item.expiry_date}</span></div>`).join('');
        } else { exsoonContainer.classList.add('hidden'); }

        // 3. نقص المخزون
        const lowContainer = document.getElementById('lowstock-container');
        const lowList = document.getElementById('lowstock-list');
        if (data.low_stock_alerts.length > 0) {
            lowContainer.classList.remove('hidden');
            lowList.innerHTML = data.low_stock_alerts.map(item => `<div class="flex justify-between p-2 bg-yellow-50 rounded-lg"><span class="font-bold text-gray-800">${item.name}</span><span class="text-yellow-700 font-bold text-xs">متبقي: ${item.stock_quantity}</span></div>`).join('');
        } else { lowContainer.classList.add('hidden'); }

    } catch (err) { console.log("Offline Dashboard"); } 
}
"""
# استبدال دالة loadDashboard القديمة
js = re.sub(r'async function loadDashboard\(\) \{.*?\n\}', new_dashboard_js, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js (منطق عرض التنبيهات).")

# 4. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v41';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v41.")

print("\n🎉 اكتملت التنبيهات بنجاح!")
