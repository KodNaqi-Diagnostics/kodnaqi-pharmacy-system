import os
import re

print("⏳ جاري بناء القائمة الدوارة وإصلاح المزامنة...")

# ==========================================
# 1. تحديث الواجهة (index.html)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. إخفاء شريط التنقل السفلي القديم نهائياً
html = re.sub(r'<nav class="fixed bottom-0.*?</nav>', '', html, flags=re.DOTALL)

# ب. إضافة كود الـ CSS الخاص بالقائمة الدوارة في الـ Head
radial_css = """
    <style>
        /* القائمة الدوارة (Radial Menu) */
        .radial-menu-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 100;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .fab-main {
            width: 64px;
            height: 64px;
            background-color: #0b4d3b;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(11, 77, 59, 0.4);
            cursor: pointer;
            transition: all 0.3s ease;
            z-index: 102;
            border: 2px solid #ffffff;
            color: white;
        }

        .fab-main.active {
            transform: rotate(45deg);
            background-color: #dc2626; /* يتحول للأحمر عند الفتح */
        }

        .radial-items {
            position: absolute;
            bottom: 32px;
            right: 32px;
            width: 0;
            height: 0;
            pointer-events: none;
        }

        .radial-item {
            position: absolute;
            width: 50px;
            height: 50px;
            background-color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            opacity: 0;
            transform: translate(0, 0) scale(0);
            pointer-events: auto;
            color: #0b4d3b;
            border: 2px solid #f2ede4;
        }

        .radial-item.active-tab {
            background-color: #0b4d3b;
            color: white;
            border-color: #0b4d3b;
        }

        .radial-menu-container.open .radial-item {
            opacity: 1;
        }

        /* توزيع الأزرار في نصف دائرة (180 درجة) */
        .radial-menu-container.open .radial-item:nth-child(1) { transform: translate(0px, -110px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(2) { transform: translate(-60px, -95px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(3) { transform: translate(-100px, -55px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(4) { transform: translate(-115px, 0px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(5) { transform: translate(-100px, 55px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(6) { transform: translate(-60px, 95px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(7) { transform: translate(0px, 110px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(8) { transform: translate(55px, 95px) scale(1); }

        /* تنسيق شاشة العرض (Overlay) عند فتح القائمة */
        .radial-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(3px);
            z-index: 99;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        .radial-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }

        /* إخفاء الأزرار عند الدخول ككاشير */
        .role-cashier #fab-dashboard, .role-cashier #fab-inventory, .role-cashier #fab-purchases,
        .role-cashier #fab-suppliers, .role-cashier #fab-users, .role-cashier #fab-settings {
            display: none !important;
        }
    </style>
</head>
"""
html = html.replace('</head>', radial_css)

# ج. إضافة عناصر القائمة الدوارة قبل نهاية الـ body
radial_html = """
    <!-- القائمة الدوارة -->
    <div class="radial-overlay" id="radial-overlay" onclick="toggleRadialMenu()"></div>
    
    <div class="radial-menu-container" id="radial-menu">
        <div class="radial-items">
            <div class="radial-item" id="fab-dashboard" onclick="switchTab('dashboard'); toggleRadialMenu()" title="الرئيسية"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg></div>
            <div class="radial-item" id="fab-pos" onclick="switchTab('pos'); toggleRadialMenu()" title="الكاشير"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg></div>
            <div class="radial-item" id="fab-inventory" onclick="switchTab('inventory'); toggleRadialMenu()" title="المخزون"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg></div>
            <div class="radial-item" id="fab-history" onclick="switchTab('history'); toggleRadialMenu()" title="السجلات"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg></div>
            <div class="radial-item" id="fab-purchases" onclick="switchTab('purchases'); toggleRadialMenu()" title="المشتريات"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg></div>
            <div class="radial-item" id="fab-suppliers" onclick="switchTab('suppliers'); toggleRadialMenu()" title="الموردين"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg></div>
            <div class="radial-item" id="fab-users" onclick="switchTab('users'); toggleRadialMenu()" title="الموظفين"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg></div>
            <div class="radial-item" id="fab-settings" onclick="switchTab('settings'); toggleRadialMenu()" title="الإعدادات"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg></div>
        </div>
        <div class="fab-main" id="fab-main" onclick="toggleRadialMenu()">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </div>
    </div>
    
    <script src="/app.js"></script>
</body>
"""
html = html.replace('    <script src="/app.js"></script>\n</body>', radial_html)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html (القائمة الدوارة).")


# ==========================================
# 2. تحديث الجافاسكريبت (app.js)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# أ. إضافة دالة فتح/إغلاق القائمة الدوارة
radial_js = """
function toggleRadialMenu() {
    const menu = document.getElementById('radial-menu');
    const overlay = document.getElementById('radial-overlay');
    const fabMain = document.getElementById('fab-main');
    
    menu.classList.toggle('open');
    overlay.classList.toggle('active');
    fabMain.classList.toggle('active');
    
    // تغيير أيقونة الزر الرئيسي (X عند الفتح)
    if (menu.classList.contains('open')) {
        fabMain.innerHTML = '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>';
    } else {
        fabMain.innerHTML = '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>';
    }
}
"""
if 'function toggleRadialMenu()' not in js:
    js = radial_js + js

# ب. تحديث دالة switchTab لتغيير أيقونة الزر الرئيسي وتحديد التبويب النشط
new_switch_js = """
function switchTab(tabId) { 
    ['dashboard', 'pos', 'inventory', 'history', 'purchases', 'suppliers', 'users', 'settings'].forEach(id => { 
        const view = document.getElementById(`view-${id}`); 
        const btn = document.getElementById(`fab-${id}`); 
        if(view) view.classList.add('hidden'); 
        if(btn) btn.classList.remove('active-tab');
    }); 
    
    const activeView = document.getElementById(`view-${tabId}`); 
    const activeBtn = document.getElementById(`fab-${tabId}`); 
    
    if(activeView) activeView.classList.remove('hidden'); 
    if(activeBtn) activeBtn.classList.add('active-tab'); 
    
    // تحديث أيقونة الزر الرئيسي لتطابق التبويب الحالي
    const fabMain = document.getElementById('fab-main');
    if (fabMain && activeBtn) {
        fabMain.innerHTML = activeBtn.innerHTML;
        // إضافة كلاس يوضح أن الزر يفتح القائمة (سهم صغير)
        fabMain.innerHTML += '<div class="absolute bottom-1 right-1 w-3 h-3 bg-white rounded-full border border-gray-300"></div>';
    }

    const titles = { dashboard: 'الرئيسية', pos: 'الكاشير', inventory: 'المخزون', history: 'السجلات', purchases: 'المشتريات', suppliers: 'الموردين', users: 'الموظفين', settings: 'الإعدادات' }; 
    const titleEl = document.getElementById('current-tab-title'); 
    if(titleEl) titleEl.innerText = titles[tabId]; 
    
    if (tabId === 'dashboard') loadDashboard(); 
    if (tabId === 'inventory') { loadMedicines(); loadSuppliersForDropdown(); } 
    if (tabId === 'history') loadHistory(); 
    if (tabId === 'purchases') { loadPurchasesData(); }
    if (tabId === 'suppliers') loadSuppliersList(); 
    if (tabId === 'users') loadUsers(); 
    if (tabId === 'settings') fetchSettingsForForm(); 
}
"""
js = re.sub(r'function switchTab\(tabId\) \{.*?\n\}', new_switch_js, js, flags=re.DOTALL)

# ج. تحديث showApp لإخفاء أزرار القائمة إذا كان كاشير
new_show_app = """
function showApp() { 
    const app = document.getElementById('app-content'); if(app) app.classList.remove('hidden'); loadSettings(); 
    const role = localStorage.getItem('kodnaqi_role');
    const adminTabs = ['dashboard', 'inventory', 'purchases', 'suppliers', 'users', 'settings'];
    
    if (role !== 'admin') {
        document.body.classList.add('role-cashier');
        switchTab('pos');
    } else {
        document.body.classList.remove('role-cashier');
        switchTab('dashboard');
    }
}
"""
js = re.sub(r'function showApp\(\) \{.*?\n\}', new_show_app, js, flags=re.DOTALL)

# د. إصلاح مشكلة كلمة "معلق" (تحديث السجلات تلقائياً بعد المزامنة)
new_process_outbox = """
async function processOutbox() { 
    if(!navigator.onLine) return; 
    let outbox = await localforage.getItem('kodnaqi_outbox') || []; 
    if(outbox.length === 0) return; 
    
    let sales = await localforage.getItem('kodnaqi_sales') || []; 
    let outboxChanged = false; 
    
    for (let i = 0; i < outbox.length; i++) { 
        let sale = outbox[i]; 
        let sendData = { discount: sale.discount, paid_amount: sale.paid_amount, items: sale.items.map(item => ({ medicine_id: item.medicine_id, quantity: item.quantity, unit_price: item.unit_price })) }; 
        try { 
            let res = await apiFetch(`${API_URL}/sales`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sendData) }); 
            if (res.ok) { 
                let serverData = await res.json(); 
                let localSaleIndex = sales.findIndex(s => s.id == sale.id); 
                if (localSaleIndex !== -1) sales[localSaleIndex].invoice_number = serverData.invoice_number; 
                outbox.splice(i, 1); 
                i--; 
                outboxChanged = true; 
            } else { break; } 
        } catch(e) { break; } 
    } 
    
    if (outboxChanged) { 
        await localforage.setItem('kodnaqi_sales', sales); 
        await localforage.setItem('kodnaqi_outbox', outbox); 
        
        // التحديث التلقائي للسجلات إذا كنا نقف على شاشتها
        const historyView = document.getElementById('view-history');
        if (historyView && !historyView.classList.contains('hidden')) {
            loadHistory();
        }
    } 
}
"""
js = re.sub(r'async function processOutbox\(\) \{.*?\n\}', new_process_outbox, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js (القائمة وإصلاح المزامنة).")

# 3. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v46';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v46.")

print("\n🎉 اكتملت الترقية! ارفع الكود الآن.")
