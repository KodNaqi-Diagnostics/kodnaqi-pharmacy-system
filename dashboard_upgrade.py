import os
import re

print("⏳ جاري إضافة لوحة التحكم والإحصائيات وإدارة المخزون...")

# ==========================================
# 1. إضافة مسارات الإحصائيات في main.py
# ==========================================
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

stats_endpoint = """
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
        
        # إجمالي الأرباح (سعر البيع - التكلفة) لكل الأصناف المباعة اليوم
        profit_query = db.execute('''
            SELECT SUM((si.unit_price - m.cost) * si.quantity) as total_profit
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN medicines m ON si.medicine_id = m.id
            WHERE s.sale_date LIKE ?
        ''', (f"{today}%",)).fetchone()

        # تنبيهات المخزون (أقل من 10 حبات)
        low_stock = db.execute("SELECT id, name, stock_quantity FROM medicines WHERE stock_quantity <= 10").fetchall()
        
        return {
            "today_sales_count": today_sales["count"] if today_sales else 0,
            "today_revenue": today_sales["total"] if today_sales and today_sales["total"] else 0,
            "today_profit": profit_query["total_profit"] if profit_query and profit_query["total_profit"] else 0,
            "low_stock_alerts": [dict(r) for r in low_stock]
        }

# تقديم ملفات الواجهة الأمامية (PWA)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
"""

# استبدال آخر جزء في الملف لإضافة المسار
if 'app.mount' in main_code:
    main_code = re.sub(r'# تقديم ملفات الواجهة الأمامية \(PWA\)\s*app\.mount\([^)]+\)', stats_endpoint, main_code)
else:
    main_code += stats_endpoint

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
print("✅ تم تحديث main.py بمسار الإحصائيات.")


# ==========================================
# 2. تحديث index.html
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. إضافة قسم "الرئيسية" (Dashboard) وإضافة زر جديد في شريط التنقل
if 'id="view-dashboard"' not in html:
    # 1. إضافة قسم لوحة التحكم قبل قسم الكاشير
    dashboard_html = """
            <!-- قسم لوحة التحكم (الرئيسية) -->
            <div id="view-dashboard" class="hidden space-y-6">
                <h2 class="text-xl font-bold text-primary mb-2 px-2">نظرة عامة</h2>
                
                <!-- بطاقات الإحصائيات -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-card p-4 rounded-3xl premium-shadow border-0 flex flex-col items-center justify-center text-center">
                        <span class="text-gray-500 text-xs font-bold mb-1">مبيعات اليوم</span>
                        <span id="stat-revenue" class="text-2xl font-bold text-primary">0 SDG</span>
                        <span id="stat-count" class="text-[10px] text-gray-400 mt-1">0 فاتورة</span>
                    </div>
                    <div class="bg-card p-4 rounded-3xl premium-shadow border-0 flex flex-col items-center justify-center text-center">
                        <span class="text-gray-500 text-xs font-bold mb-1">أرباح اليوم (تقديري)</span>
                        <span id="stat-profit" class="text-2xl font-bold text-blue-600">0 SDG</span>
                        <span class="text-[10px] text-gray-400 mt-1">سعر البيع - التكلفة</span>
                    </div>
                </div>

                <!-- تنبيهات المخزون -->
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0">
                    <h3 class="font-bold text-red-600 mb-3 flex items-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                        أدوية أوشكت على النفاذ (أقل من 10)
                    </h3>
                    <div id="low-stock-list" class="space-y-2 text-sm">
                        <p class="text-gray-500">لا توجد تنبيهات.</p>
                    </div>
                </div>
            </div>
    """
    html = html.replace('<div id="view-pos" class="space-y-6">', dashboard_html + '\n            <div id="view-pos" class="space-y-6">')

    # 2. إضافة زر لوحة التحكم في شريط التنقل السفلي (وتقليل عرض باقي الأزرار)
    html = html.replace('class="flex flex-col items-center p-2 text-primary w-1/4 transition-all">', 'class="flex flex-col items-center p-2 text-primary w-1/5 transition-all">')
    html = html.replace('class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/4 transition-all">', 'class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/5 transition-all">')
    
    dash_btn = """
            <button onclick="switchTab('dashboard')" id="btn-dashboard" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/5 transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                <span class="text-[10px] font-bold">الرئيسية</span>
            </button>
    """
    html = html.replace('</nav>', dash_btn + '</nav>')

# ب. إضافة قائمة الأدوية في تبويب المخزون
if 'id="inventory-list"' not in html:
    inv_list = """
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0 mb-4 mt-6">
                    <h2 class="text-lg font-bold mb-4 text-primary">الأدوية في المخزون</h2>
                    <input type="text" id="inv-search" onkeyup="filterInventory()" placeholder="ابحث في المخزون..." class="w-full bg-bg border-0 rounded-xl p-3 mb-4 focus:ring-2 focus:ring-primary outline-none text-sm">
                    <div id="inventory-list" class="space-y-2 max-h-96 overflow-y-auto">
                        <p class="text-gray-500 text-center py-4">جاري التحميل...</p>
                    </div>
                </div>
            </div>
    """
    # استبدال إغلاق قسم المخزون
    html = html.replace('</form>\n                </div>\n            </div>', '</form>\n                </div>\n' + inv_list)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html (لوحة التحكم وقائمة المخزون).")


# ==========================================
# 3. تحديث app.js
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# أ. تحديث دالة التنقل switchTab
switch_js = """
function switchTab(tabId) {
    ['dashboard', 'pos', 'inventory', 'history', 'settings'].forEach(id => {
        const view = document.getElementById(`view-${id}`);
        const btn = document.getElementById(`btn-${id}`);
        if(view) view.classList.add('hidden');
        if(btn) btn.className = "flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/5 transition-all";
    });

    const activeView = document.getElementById(`view-${tabId}`);
    const activeBtn = document.getElementById(`btn-${tabId}`);
    if(activeView) activeView.classList.remove('hidden');
    if(activeBtn) activeBtn.className = "flex flex-col items-center p-2 text-primary w-1/5 transition-all";

    const titles = { dashboard: 'الرئيسية', pos: 'الكاشير', inventory: 'المخزون', history: 'السجلات', settings: 'الإعدادات' };
    const titleEl = document.getElementById('current-tab-title');
    if(titleEl) titleEl.innerText = titles[tabId];

    if (tabId === 'dashboard') loadDashboard();
    if (tabId === 'inventory') { loadMedicines(); loadInventoryList(); }
    if (tabId === 'history') loadHistory();
    if (tabId === 'settings') fetchSettingsForForm();
}
"""
js = re.sub(r'function switchTab\(tabId\) \{.*?\n\}', switch_js, js, flags=re.DOTALL)

# ب. دالة جلب الإحصائيات
dashboard_js = """
async function loadDashboard() {
    try {
        const res = await fetch(`${API_URL}/stats`);
        const data = await res.json();
        
        document.getElementById('stat-revenue').innerText = `${data.today_revenue} SDG`;
        document.getElementById('stat-count').innerText = `${data.today_sales_count} فاتورة`;
        document.getElementById('stat-profit').innerText = `${data.today_profit} SDG`;
        
        const list = document.getElementById('low-stock-list');
        if(data.low_stock_alerts.length === 0) {
            list.innerHTML = '<p class="text-green-600 text-xs font-bold">✅ المخزون بحالة جيدة.</p>';
        } else {
            list.innerHTML = data.low_stock_alerts.map(item => `
                <div class="flex justify-between items-center bg-red-50 p-2 rounded-lg">
                    <span class="font-bold text-gray-800 text-xs">${item.name}</span>
                    <span class="text-red-600 font-bold text-xs">متبقي: ${item.stock_quantity}</span>
                </div>
            `).join('');
        }
    } catch (err) {
        console.log("Offline mode: Stats not available.");
    }
}
"""
if "async function loadDashboard()" not in js:
    js = js.replace("// 2. التنقل", dashboard_js + "\n// 2. التنقل")

# ج. دالة عرض قائمة المخزون
inventory_list_js = """
async function loadInventoryList() {
    try {
        const res = await fetch(`${API_URL}/medicines`);
        const medicines = await res.json();
        const list = document.getElementById('inventory-list');
        if (!list) return;
        
        list.innerHTML = medicines.map(med => `
            <div class="flex justify-between items-center p-3 border-b border-gray-100">
                <div>
                    <p class="font-bold text-gray-800 text-sm">${med.name}</p>
                    <p class="text-xs text-gray-500">${med.category || 'غير مصنف'} | ${med.scientific_name || ''}</p>
                </div>
                <div class="text-left">
                    <p class="font-bold text-primary text-sm">${med.price} SDG</p>
                    <p class="text-[10px] ${med.stock_quantity <= 10 ? 'text-red-500 font-bold' : 'text-gray-400'}">المخزون: ${med.stock_quantity}</p>
                </div>
            </div>
        `).join('');
    } catch (err) { console.error(err); }
}

function filterInventory() {
    const query = document.getElementById('inv-search').value.toLowerCase();
    const items = document.querySelectorAll('#inventory-list > div');
    items.forEach(item => {
        const text = item.innerText.toLowerCase();
        item.style.display = text.includes(query) ? 'flex' : 'none';
    });
}
"""
if "async function loadInventoryList()" not in js:
    js = js.replace("function filterMedicines()", inventory_list_js + "\nfunction filterMedicines()")

# د. تغيير الصفحة الافتراضية عند الدخول إلى لوحة التحكم
js = js.replace("showApp() {\n    const app = document.getElementById('app-content');\n    if(app) app.classList.remove('hidden');\n    loadSettings();\n    loadMedicines();\n}", "showApp() {\n    const app = document.getElementById('app-content');\n    if(app) app.classList.remove('hidden');\n    loadSettings();\n    switchTab('dashboard'); // افتح الرئيسية أولاً\n}")

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js (منطق الإحصائيات والمخزون).")

# 4. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v6';", "const CACHE_NAME = 'kodnaqi-v7';")
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v7.")

print("\n🎉 اكتمل التحديث! أعد تشغيل السيرفر.")
