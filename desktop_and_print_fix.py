import os
import re

print("⏳ جاري تحسين واجهة الكمبيوتر وإصلاح زر الطباعة...")

# ==========================================
# 1. تحديث الواجهة (index.html)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. تحسين شكل التطبيق على الكمبيوتر (تقييد العرض وتوسيطه)
html = html.replace(
    '<div id="app-content" class="hidden">',
    '<div id="app-content" class="hidden max-w-4xl mx-auto min-h-screen shadow-2xl bg-bg">'
)

# ب. تحسين شريط العنوان (Header)
new_header = """
        <header class="bg-primary text-white p-4 shadow-md sticky top-0 z-10 rounded-b-3xl mb-4">
            <div class="flex justify-between items-center w-full max-w-4xl mx-auto">
                <div class="flex items-center gap-2">
                    <span id="current-tab-title" class="text-xs bg-white/20 px-3 py-1.5 rounded-full font-medium">الرئيسية</span>
                    <span id="user-role-badge" class="text-[10px] bg-yellow-500 text-primary px-2 py-1 rounded-full font-bold hidden">مدير</span>
                </div>
                <div class="flex items-center gap-3">
                    <h1 id="pharmacy-name" class="text-xl font-bold">KodNaqi Pharmacy</h1>
                    <div class="w-10 h-10 bg-white rounded-xl flex items-center justify-center p-1 shadow-sm border border-white/20"><img src="/icon-pharma.png" class="w-full h-full object-contain"></div>
                </div>
            </div>
        </header>
"""
html = re.sub(r'<header.*?</header>', new_header, html, flags=re.DOTALL)

# ج. تحسين شريط التنقل السفلي (توزيع متساوٍ وتوسيط للكمبيوتر)
new_nav = """
    <nav class="fixed bottom-0 w-full max-w-4xl left-1/2 -translate-x-1/2 bg-white border-t border-gray-100 flex justify-between overflow-x-auto py-2 z-20 rounded-t-3xl pb-4 shadow-[0_-4px_20px_rgba(0,0,0,0.04)] [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
        <button onclick="switchTab('dashboard')" id="btn-dashboard" class="flex-1 flex flex-col items-center p-2 text-gray-400 hover:text-primary transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
            <span class="text-[10px] font-bold">الرئيسية</span>
        </button>
        <button onclick="switchTab('pos')" id="btn-pos" class="flex-1 flex flex-col items-center p-2 text-gray-400 hover:text-primary transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
            <span class="text-[10px] font-bold">الكاشير</span>
        </button>
        <button onclick="switchTab('inventory')" id="btn-inventory" class="flex-1 flex flex-col items-center p-2 text-gray-400 hover:text-primary transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
            <span class="text-[10px] font-bold">المخزون</span>
        </button>
        <button onclick="switchTab('history')" id="btn-history" class="flex-1 flex flex-col items-center p-2 text-gray-400 hover:text-primary transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            <span class="text-[10px] font-bold">السجلات</span>
        </button>
        <button onclick="switchTab('purchases')" id="btn-purchases" class="flex-1 flex flex-col items-center p-2 text-gray-400 hover:text-primary transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"></path></svg>
            <span class="text-[10px] font-bold">المشتريات</span>
        </button>
        <button onclick="switchTab('suppliers')" id="btn-suppliers" class="flex-1 flex flex-col items-center p-2 text-gray-400 hover:text-primary transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
            <span class="text-[10px] font-bold">الموردين</span>
        </button>
        <button onclick="switchTab('users')" id="btn-users" class="flex-1 flex flex-col items-center p-2 text-gray-400 hover:text-primary transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
            <span class="text-[10px] font-bold">الموظفين</span>
        </button>
        <button onclick="switchTab('settings')" id="btn-settings" class="flex-1 flex flex-col items-center p-2 text-gray-400 hover:text-primary transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            <span class="text-[10px] font-bold">الإعدادات</span>
        </button>
    </nav>
"""
html = re.sub(r'<nav.*?</nav>', new_nav, html, flags=re.DOTALL)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحسين واجهة الكمبيوتر وشريط التنقل.")


# ==========================================
# 2. تحديث الجافاسكريبت (app.js)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# أ. تحديث showApp لإظهار رتبة المستخدم بجانب اسم الرئيسية
new_show_app = """
function showApp() { 
    const app = document.getElementById('app-content'); if(app) app.classList.remove('hidden'); loadSettings(); 
    const role = localStorage.getItem('kodnaqi_role');
    const roleBadge = document.getElementById('user-role-badge');
    
    if (roleBadge) {
        roleBadge.classList.remove('hidden');
        roleBadge.innerText = role === 'admin' ? 'مدير' : 'كاشير';
        if (role === 'admin') roleBadge.className = "text-[10px] bg-green-500 text-white px-2 py-1 rounded-full font-bold";
        else roleBadge.className = "text-[10px] bg-blue-500 text-white px-2 py-1 rounded-full font-bold";
    }

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

# ب. إعادة زر الطباعة في السجلات
new_render_history = """
function renderHistoryList(sales, list) { 
    if (sales.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center py-4">لا توجد فواتير سابقة.</p>'; return; } 
    list.innerHTML = sales.map(sale => { 
        const date = new Date(sale.sale_date).toLocaleString('en-GB'); 
        const isSynced = !sale.invoice_number.startsWith('OFF-'); 
        return `<div class="flex justify-between items-center p-4 border-b border-gray-100 hover:bg-gray-50 transition">
            <div>
                <p class="font-bold text-primary">${sale.invoice_number} ${!isSynced ? '<span class="text-[9px] text-orange-500 bg-orange-50 px-1 rounded">معلق</span>' : ''}</p>
                <p class="text-xs text-gray-400 mt-1">${date}</p>
            </div>
            <div class="flex items-center gap-4">
                <div class="text-left">
                    <p class="font-bold text-primary">${formatCurrency(sale.total_amount || sale.items.reduce((s,i)=>s+(i.unit_price*i.quantity),0))} SDG</p>
                    <p class="text-xs text-gray-400">${sale.items.length} أصناف</p>
                </div>
                <!-- زر الطباعة -->
                <button onclick='reprintInvoice(${JSON.stringify(sale)})' class="bg-blue-50 text-blue-600 p-3 rounded-xl hover:bg-blue-100 transition shadow-sm" title="إعادة طباعة">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
                </button>
            </div>
        </div>`; 
    }).join(''); 
}
"""
js = re.sub(r'function renderHistoryList\(sales, list\) \{.*?\n\}', new_render_history, js, flags=re.DOTALL)

# ج. تحسين نافذة الدفع لإظهار محتويات الفاتورة قبل الدفع
new_checkout = """
async function checkout() { 
    if (cart.length === 0) return showAlert("تنبيه", "الفاتورة فارغة.", "error"); 
    let total = cart.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0); 
    
    // تجهيز قائمة الأدوية لعرضها في النافذة
    let itemsHtml = cart.map(item => `<div class="flex justify-between text-xs text-gray-600 mb-1"><span>${item.name} (x${item.quantity})</span><span>${formatCurrency(item.unit_price * item.quantity)} SDG</span></div>`).join('');
    let promptMsg = `<div class="max-h-32 overflow-y-auto mb-4 text-right pr-2">${itemsHtml}</div><hr class="mb-4"><div class="flex justify-between font-bold text-lg mb-4"><span>الإجمالي:</span><span class="text-primary">${formatCurrency(total)} SDG</span></div><div class="text-sm font-bold text-gray-700 mb-2">أدخل المبلغ المدفوع:</div>`;

    const paid = await showPrompt("تأكيد الفاتورة", promptMsg, total); 
    if (paid === null || paid === "") return; 
    const paidAmount = parseFloat(paid); 
    if (isNaN(paidAmount) || paidAmount < total) return showAlert("خطأ", "المبلغ غير كافٍ!", "error"); 
    
    const localId = Date.now(); 
    const saleData = { id: localId, discount: 0, paid_amount: paidAmount, items: cart.map(i => ({ medicine_id: i.medicine_id, quantity: i.quantity, unit_price: i.unit_price })), invoice_number: `OFF-${localId.toString().slice(-6)}`, sale_date: new Date().toISOString() }; 
    
    let sales = await localforage.getItem('kodnaqi_sales') || []; 
    sales.unshift(saleData); 
    await localforage.setItem('kodnaqi_sales', sales); 
    
    let outbox = await localforage.getItem('kodnaqi_outbox') || []; 
    outbox.push(saleData); 
    await localforage.setItem('kodnaqi_outbox', outbox); 
    
    const change = paidAmount - total; 
    preparePrintInvoice(saleData.invoice_number, cart, total, paidAmount, change); 
    
    let msg = `رقم الفاتورة: <b>${saleData.invoice_number}</b><br>الباقي للعميل: <b class="text-primary text-lg">${formatCurrency(change)} SDG</b>`; 
    msg += `<br><br><button onclick="window.print()" class="mt-2 bg-blue-600 text-white px-6 py-3 rounded-xl font-bold w-full shadow-lg">🖨️ طباعة الفاتورة</button>`; 
    
    await showAlert("تمت العملية بنجاح", msg, "success"); 
    cart = []; 
    renderCart(); 
    loadMedicines(); 
    processOutbox(); 
}
"""
js = re.sub(r'async function checkout\(\) \{.*?(?=// Sync & History)', new_checkout + "\n", js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js (زر الطباعة ونافذة الدفع).")

# 3. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v51';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v51.")

print("\n🎉 اكتمل التحديث! ارفع الكود الآن.")
