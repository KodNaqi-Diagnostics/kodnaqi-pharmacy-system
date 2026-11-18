import os
import re

print("⏳ جاري استعادة شريط التنقل السفلي التقليدي...")

# ==========================================
# 1. تحديث index.html
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. حذف كود الـ CSS الخاص بالقائمة الدوارة
html = re.sub(r'<style>\s*/\* القائمة الدوارة.*?</style>\s*</head>', '</head>', html, flags=re.DOTALL)

# ب. حذف عناصر القائمة الدوارة (Overlay + Container)
html = re.sub(r'<!-- القائمة الدوارة -->.*?</div>\s*</div>\s*<script src="/app.js">', '<script src="/app.js">', html, flags=re.DOTALL)

# ج. إضافة شريط التنقل السفلي الجديد (قابل للسحب أفقياً)
bottom_nav = """
    <!-- شريط التنقل السفلي الجديد (قابل للسحب) -->
    <nav class="fixed bottom-0 w-full bg-white border-t border-gray-100 flex overflow-x-auto py-2 z-50 rounded-t-3xl pb-4 shadow-[0_-4px_20px_rgba(0,0,0,0.04)] [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
        <button onclick="switchTab('dashboard')" id="btn-dashboard" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
            <span class="text-[10px] font-bold">الرئيسية</span>
        </button>
        <button onclick="switchTab('pos')" id="btn-pos" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
            <span class="text-[10px] font-bold">الكاشير</span>
        </button>
        <button onclick="switchTab('inventory')" id="btn-inventory" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
            <span class="text-[10px] font-bold">المخزون</span>
        </button>
        <button onclick="switchTab('history')" id="btn-history" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            <span class="text-[10px] font-bold">السجلات</span>
        </button>
        <button onclick="switchTab('purchases')" id="btn-purchases" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4"></path></svg>
            <span class="text-[10px] font-bold">المشتريات</span>
        </button>
        <button onclick="switchTab('suppliers')" id="btn-suppliers" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
            <span class="text-[10px] font-bold">الموردين</span>
        </button>
        <button onclick="switchTab('users')" id="btn-users" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
            <span class="text-[10px] font-bold">الموظفين</span>
        </button>
        <button onclick="switchTab('settings')" id="btn-settings" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            <span class="text-[10px] font-bold">الإعدادات</span>
        </button>
    </nav>
    
    <script src="/app.js"></script>
"""
html = html.replace('<script src="/app.js"></script>', bottom_nav)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تمت استعادة شريط التنقل السفلي (القابل للسحب).")


# ==========================================
# 2. تحديث app.js (إزالة أكواد القائمة الدوارة)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# أ. إزالة دالة toggleRadialMenu ومستمع التمرير
js = re.sub(r'function toggleRadialMenu\(\) \{.*?(?=function switchTab)', '', js, flags=re.DOTALL)
js = re.sub(r'window\.addEventListener\(\'scroll\', \(\) => \{.*?\n\}\);', '', js, flags=re.DOTALL)

# ب. إعادة دالة switchTab الأصلية التي تتعامل مع أزرار الـ nav السفلي
new_switch_js = """
function switchTab(tabId) { 
    ['dashboard', 'pos', 'inventory', 'history', 'purchases', 'suppliers', 'users', 'settings'].forEach(id => { 
        const view = document.getElementById(`view-${id}`); 
        const btn = document.getElementById(`btn-${id}`); 
        if(view) view.classList.add('hidden'); 
        if(btn) btn.className = "flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all"; 
    }); 
    
    const activeView = document.getElementById(`view-${tabId}`); 
    const activeBtn = document.getElementById(`btn-${tabId}`); 
    
    if(activeView) activeView.classList.remove('hidden'); 
    if(activeBtn) activeBtn.className = "flex flex-col items-center p-2 text-primary min-w-[70px] transition-all"; 
    
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

# ج. تحديث showApp لإخفاء الأزرار في الشريط السفلي بناءً على الصلاحية
new_show_app = """
function showApp() { 
    const app = document.getElementById('app-content'); if(app) app.classList.remove('hidden'); loadSettings(); 
    const role = localStorage.getItem('kodnaqi_role');
    const adminTabs = ['dashboard', 'inventory', 'purchases', 'suppliers', 'users', 'settings'];
    
    if (role !== 'admin') {
        adminTabs.forEach(id => { const el = document.getElementById(`btn-${id}`); if(el) el.style.display = 'none'; });
        switchTab('pos');
    } else {
        adminTabs.forEach(id => { const el = document.getElementById(`btn-${id}`); if(el) el.style.display = 'flex'; });
        switchTab('dashboard');
    }
}
"""
js = re.sub(r'function showApp\(\) \{.*?\n\}', new_show_app, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js وإزالة أكواد القائمة الدوارة.")

# 3. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v49';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v49.")

print("\n🎉 اكتملت العودة للشريط السفلي! ارفع الكود الآن.")
