import os
import re

print("⏳ جاري تكبير أزرار القائمة السفلية للشاشات الكبيرة...")

# ==========================================
# 1. تحديث الواجهة (index.html)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. تكبير الأيقونات (SVG) والنصوص (Span) داخل شريط التنقل السفلي فقط
# نستخدم تعبير نمطي (Regex) لاستهداف الأيقونات داخل الـ nav فقط
def scale_nav_elements(match):
    element = match.group(0)
    # تكبير الأيقونة
    element = element.replace('class="w-6 h-6 mb-1"', 'class="w-6 h-6 md:w-8 md:h-8 mb-1 md:mb-1.5"')
    # تكبير النص
    element = element.replace('class="text-[10px] font-bold"', 'class="text-[10px] md:text-sm font-bold"')
    return element

# استخراج شريط التنقل وتطبيق التعديل عليه فقط
nav_match = re.search(r'<nav.*?</nav>', html, flags=re.DOTALL)
if nav_match:
    old_nav = nav_match.group(0)
    new_nav = re.sub(r'<svg.*?</svg>|<span.*?</span>', scale_nav_elements, old_nav, flags=re.DOTALL)
    html = html.replace(old_nav, new_nav)
    print("✅ تم تكبير الأيقونات والنصوص في index.html.")

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)


# ==========================================
# 2. تحديث الجافاسكريبت (app.js)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# تحديث دالة switchTab لإضافة الكلاسات الجديدة (الحشوة والمسافات) عند التفعيل وغير التفعيل
new_switch_js = """
function switchTab(tabId) { 
    ['dashboard', 'pos', 'inventory', 'history', 'purchases', 'suppliers', 'users', 'settings'].forEach(id => { 
        const view = document.getElementById(`view-${id}`); 
        const btn = document.getElementById(`btn-${id}`); 
        if(view) view.classList.add('hidden'); 
        if(btn) btn.className = "flex-1 flex flex-col items-center justify-center p-2 md:p-3 text-gray-400 hover:text-primary transition-all group"; 
    }); 
    
    const activeView = document.getElementById(`view-${tabId}`); 
    const activeBtn = document.getElementById(`btn-${tabId}`); 
    
    if(activeView) activeView.classList.remove('hidden'); 
    if(activeBtn) activeBtn.className = "flex-1 flex flex-col items-center justify-center p-2 md:p-3 text-primary transition-all group"; 
    
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

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث كلاسات الأزرار في app.js.")

# 3. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v52';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v52.")

print("\n🎉 اكتمل التعديل! ارفع الكود الآن.")
