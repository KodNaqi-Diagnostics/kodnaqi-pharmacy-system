import os
import re
from datetime import datetime

print("⏳ جاري إضافة نظام تنبيهات انتهاء الصلاحية...")

# ==========================================
# 1. تحديث main.py (الخلفية)
# ==========================================
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# تحديث مسار الإحصائيات ليشمل الأدوية التي تنتهي صلاحيتها خلال 30 يوماً
new_stats_logic = """
        # تنبيهات المخزون (أقل من 10 حبات)
        low_stock = db.execute("SELECT id, name, stock_quantity FROM medicines WHERE stock_quantity <= 10").fetchall()
        
        # تنبيهات الصلاحية (تنتهي خلال 30 يوماً من اليوم)
        # ملاحظة: نستخدم date('now', '+30 days') في SQLite
        expiring_soon = db.execute('''
            SELECT id, name, expiry_date, stock_quantity 
            FROM medicines 
            WHERE expiry_date IS NOT NULL 
            AND expiry_date != '' 
            AND date(expiry_date) <= date('now', '+30 days')
            AND date(expiry_date) >= date('now')
        ''').fetchall()

        # الأدوية المنتهية صلاحيتها بالفعل
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
"""

main_code = re.sub(r'        # تنبيهات المخزون \(أقل من 10 حبات\).*?return \{.*?\}', new_stats_logic, main_code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
print("✅ تم تحديث main.py (إضافة منطق الصلاحية).")


# ==========================================
# 2. تحديث index.html (الواجهة)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. إضافة حقل تاريخ الانتهاء في نموذج إضافة الدواء
if 'id="med-expiry"' not in html:
    html = html.replace(
        '<input type="text" id="med-barcode" placeholder="الباركود (لمسحه بالكاميرا لاحقاً)" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">',
        '''<div class="grid grid-cols-2 gap-3">
            <input type="text" id="med-barcode" placeholder="الباركود" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
            <input type="date" id="med-expiry" title="تاريخ انتهاء الصلاحية" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none text-gray-500">
        </div>'''
    )

# ب. إضافة قسم التنبيهات في لوحة التحكم
if 'id="expiry-alerts-list"' not in html:
    expiry_dashboard_html = """
                <!-- تنبيهات الصلاحية -->
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0 mt-4">
                    <h3 class="font-bold text-orange-500 mb-3 flex items-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        أدوية قاربت على الانتهاء (أقل من 30 يوم)
                    </h3>
                    <div id="expiry-alerts-list" class="space-y-2 text-sm">
                        <p class="text-gray-500 text-xs">لا توجد تنبيهات.</p>
                    </div>
                </div>

                <!-- أدوية منتهية الصلاحية -->
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0 mt-4" id="expired-container" style="display:none;">
                    <h3 class="font-bold text-red-600 mb-3 flex items-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        أدوية منتهية الصلاحية (يجب سحبها فوراً)
                    </h3>
                    <div id="expired-list" class="space-y-2 text-sm"></div>
                </div>
    """
    # إدخال القسم بعد تنبيهات المخزون
    html = html.replace(
        '<div id="low-stock-list" class="space-y-2 text-sm">\n                        <p class="text-gray-500">لا توجد تنبيهات.</p>\n                    </div>\n                </div>',
        '<div id="low-stock-list" class="space-y-2 text-sm">\n                        <p class="text-gray-500">لا توجد تنبيهات.</p>\n                    </div>\n                </div>\n' + expiry_dashboard_html
    )

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html (حقل التاريخ وقسم التنبيهات).")


# ==========================================
# 3. تحديث app.js (المنطق)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# أ. تحديث إرسال النموذج لإرسال تاريخ الانتهاء
js = js.replace(
    "barcode: document.getElementById('med-barcode').value || null,",
    "barcode: document.getElementById('med-barcode').value || null,\n        expiry_date: document.getElementById('med-expiry').value || null,"
)

# ب. تحديث دالة لوحة التحكم لعرض التنبيهات
new_dashboard_js = """
async function loadDashboard() {
    try {
        const res = await fetch(`${API_URL}/stats`);
        const data = await res.json();
        
        document.getElementById('stat-revenue').innerText = `${data.today_revenue} SDG`;
        document.getElementById('stat-count').innerText = `${data.today_sales_count} فاتورة`;
        document.getElementById('stat-profit').innerText = `${data.today_profit} SDG`;
        
        // 1. تنبيهات المخزون
        const lowList = document.getElementById('low-stock-list');
        if(data.low_stock_alerts.length === 0) {
            lowList.innerHTML = '<p class="text-green-600 text-xs font-bold">✅ المخزون بحالة جيدة.</p>';
        } else {
            lowList.innerHTML = data.low_stock_alerts.map(item => `
                <div class="flex justify-between items-center bg-red-50 p-2 rounded-lg">
                    <span class="font-bold text-gray-800 text-xs">${item.name}</span>
                    <span class="text-red-600 font-bold text-xs">متبقي: ${item.stock_quantity}</span>
                </div>
            `).join('');
        }

        // 2. تنبيهات الصلاحية (قريباً)
        const expList = document.getElementById('expiry-alerts-list');
        if(expList) {
            if(data.expiring_soon_alerts.length === 0) {
                expList.innerHTML = '<p class="text-green-600 text-xs font-bold">✅ لا توجد أدوية قاربت على الانتهاء.</p>';
            } else {
                expList.innerHTML = data.expiring_soon_alerts.map(item => `
                    <div class="flex justify-between items-center bg-orange-50 p-2 rounded-lg">
                        <span class="font-bold text-gray-800 text-xs">${item.name}</span>
                        <span class="text-orange-600 font-bold text-[10px]">ينتهي: ${item.expiry_date}</span>
                    </div>
                `).join('');
            }
        }

        // 3. الأدوية المنتهية فعلياً
        const expiredContainer = document.getElementById('expired-container');
        const expiredList = document.getElementById('expired-list');
        if(expiredContainer && expiredList) {
            if(data.expired_alerts.length > 0) {
                expiredContainer.style.display = 'block';
                expiredList.innerHTML = data.expired_alerts.map(item => `
                    <div class="flex justify-between items-center bg-red-100 p-2 rounded-lg border border-red-200">
                        <span class="font-bold text-red-800 text-xs">${item.name}</span>
                        <span class="text-red-600 font-bold text-[10px]">منتهي: ${item.expiry_date}</span>
                    </div>
                `).join('');
            } else {
                expiredContainer.style.display = 'none';
            }
        }

    } catch (err) {
        console.log("Offline mode: Stats not available.");
    }
}
"""
js = re.sub(r'async function loadDashboard\(\) \{.*?\n\}', new_dashboard_js, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js (منطق عرض التنبيهات).")

# 4. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v7';", "const CACHE_NAME = 'kodnaqi-v8';")
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v8.")

print("\n🎉 اكتمل التحديث! أعد تشغيل السيرفر.")
