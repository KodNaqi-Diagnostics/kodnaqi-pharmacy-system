import os
import re

print("⏳ جاري تجهيز النظام للعمل بدون إنترنت (Offline-First) وإصلاح الشعار...")

# ==========================================
# 1. تحديث index.html
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. إصلاح شكل حاوية الشعار (من دائري إلى مربع بحواف دائرية)
html = html.replace(
    '<div class="w-10 h-10 bg-white rounded-full flex items-center justify-center p-1 overflow-hidden shadow-sm">',
    '<div class="w-10 h-10 bg-white rounded-xl flex items-center justify-center p-1 overflow-hidden shadow-sm border border-white/20">'
)

# ب. إضافة مكتبة LocalForage (لتخزين البيانات محلياً في المتصفح)
if 'localforage' not in html:
    html = html.replace(
        '<script src="https://unpkg.com/html5-qrcode"></script>',
        '<script src="https://unpkg.com/html5-qrcode"></script>\n    <script src="https://cdnjs.cloudflare.com/ajax/libs/localforage/1.10.0/localforage.min.js"></script>'
    )

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم إصلاح الشعار وإضافة مكتبة التخزين المحلي.")


# ==========================================
# 2. تحديث app.js (قلب نظام الأوفلاين)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# ---------------------------------------------------------
# أ. تحديث دالة جلب الإعدادات (تعمل أوفلاين)
# ---------------------------------------------------------
load_settings_js = """
async function loadSettings() {
    try {
        const res = await fetch(`${API_URL}/settings`);
        const data = await res.json();
        const nameEl = document.getElementById('pharmacy-name');
        if(nameEl) nameEl.innerText = data.pharmacy_name;
        // حفظ في الذاكرة المحلية للمرة القادمة
        await localforage.setItem('kodnaqi_settings', data);
    } catch (err) { 
        console.log("Offline: Loading settings from local DB");
        const localData = await localforage.getItem('kodnaqi_settings');
        if(localData) {
            const nameEl = document.getElementById('pharmacy-name');
            if(nameEl) nameEl.innerText = localData.pharmacy_name;
        }
    }
}
"""
js = re.sub(r'async function loadSettings\(\) \{.*?\n\}', load_settings_js, js, flags=re.DOTALL)

# ---------------------------------------------------------
# ب. تحديث دالة جلب الأدوية (تعمل أوفلاين)
# ---------------------------------------------------------
load_medicines_js = """
async function loadMedicines() {
    try {
        const res = await fetch(`${API_URL}/medicines`);
        const medicines = await res.json();
        const list = document.getElementById('medicines-list');
        if (!list) return;
        if (medicines.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center py-4">لا توجد أدوية.</p>'; return; }
        
        list.innerHTML = medicines.map(med => `
            <div onclick="addToCart(${med.id}, '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl">
                <div>
                    <p class="font-bold text-gray-800 text-sm">${med.name}</p>
                    <p class="text-xs text-gray-500">${med.scientific_name || ''} ${med.category ? '| ' + med.category : ''}</p>
                </div>
                <div class="text-left">
                    <p class="font-bold text-primary">${med.price} SDG</p>
                    <p class="text-[10px] text-gray-400">المخزون: ${med.stock_quantity}</p>
                </div>
            </div>
        `).join('');
        
        // حفظ في الذاكرة المحلية
        await localforage.setItem('kodnaqi_medicines', medicines);
    } catch (err) { 
        console.log("Offline: Loading medicines from local DB");
        const localMeds = await localforage.getItem('kodnaqi_medicines');
        const list = document.getElementById('medicines-list');
        if(localMeds && list) {
            list.innerHTML = localMeds.map(med => `
                <div onclick="addToCart(${med.id}, '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl">
                    <div>
                        <p class="font-bold text-gray-800 text-sm">${med.name}</p>
                        <p class="text-xs text-gray-500">${med.scientific_name || ''} ${med.category ? '| ' + med.category : ''}</p>
                    </div>
                    <div class="text-left">
                        <p class="font-bold text-primary">${med.price} SDG</p>
                        <p class="text-[10px] text-gray-400">المخزون: ${med.stock_quantity}</p>
                    </div>
                </div>
            `).join('');
        }
    }
}
"""
js = re.sub(r'async function loadMedicines\(\) \{.*?\n\}', load_medicines_js, js, flags=re.DOTALL)

# ---------------------------------------------------------
# ج. تحديث دالة الدفع (حفظ الفاتورة محلياً أولاً ثم إرسالها للسيرفر)
# ---------------------------------------------------------
checkout_js = """
async function checkout() {
    if (cart.length === 0) return showAlert("تنبيه", "الفاتورة فارغة.", "error");
    let total = cart.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
    const paid = await showPrompt("الدفع", `الإجمالي المطلوب: ${total} SDG`, total);
    if (paid === null || paid === "") return; 
    const paidAmount = parseFloat(paid);
    if (isNaN(paidAmount) || paidAmount < total) return showAlert("خطأ", "المبلغ المدفوع غير كافٍ!", "error");

    const saleData = { 
        discount: 0, 
        paid_amount: paidAmount, 
        items: cart.map(i => ({ medicine_id: i.medicine_id, quantity: i.quantity, unit_price: i.unit_price })),
        local_id: Date.now() // معرف محلي فريد لتفادي التكرار
    };

    // 1. إضافة الفاتورة إلى طابور المزامنة المحلي (Outbox) فوراً
    let outbox = await localforage.getItem('kodnaqi_outbox') || [];
    outbox.push(saleData);
    await localforage.setItem('kodnaqi_outbox', outbox);

    // 2. محاولة إرسالها للسيرفر إذا كان هناك إنترنت
    const isSynced = await syncSaleToServer(saleData);

    // 3. تجهيز الفاتورة للطباعة (نستخدم معرف مؤقت إذا كنا أوفلاين)
    const invNum = isSynced ? isSynced.invoice_number : `OFF-${saleData.local_id.toString().slice(-6)}`;
    const change = paidAmount - total;
    
    preparePrintInvoice(invNum, cart, total, paidAmount, change);
    
    let msg = `رقم الفاتورة: <b>${invNum}</b><br>الباقي: <b class="text-primary text-lg">${change} SDG</b>`;
    if(!isSynced) {
        msg += `<br><span class="text-xs text-orange-500 font-bold block mt-2">⚠️ لا يوجد إنترنت: تم حفظ الفاتورة محلياً وستتم المزامنة لاحقاً.</span>`;
    }

    msg += `<br><br><button onclick="window.print()" class="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-bold w-full">🖨️ طباعة الفاتورة</button>`;
    
    await showAlert("تمت العملية", msg, "success");
    
    cart = []; 
    renderCart(); 
    
    // إذا كنا متصلين، نحدث القائمة، وإلا لا نفعل شيء
    if(isSynced) loadMedicines(); 
}

// دالة إرسال الفاتورة للسيرفر
async function syncSaleToServer(saleData) {
    try {
        const res = await fetch(`${API_URL}/sales`, { 
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify(saleData) 
        });
        if (res.ok) {
            const data = await res.json();
            // إذا نجح الإرسال، نقوم بحذفها من طابور الانتظار
            let outbox = await localforage.getItem('kodnaqi_outbox') || [];
            outbox = outbox.filter(s => s.local_id !== saleData.local_id);
            await localforage.setItem('kodnaqi_outbox', outbox);
            return data; // يحتوي على رقم الفاتورة الرسمي
        }
    } catch (err) {
        console.log("Network failed, saved to outbox.");
    }
    return false;
}
"""
js = re.sub(r'async function checkout\(\) \{.*?(?=// 7\. السجلات والطباعة)', checkout_js + "\n\n", js, flags=re.DOTALL)


# ---------------------------------------------------------
# د. إضافة محرك المزامنة التلقائية (Sync Engine)
# ---------------------------------------------------------
sync_engine_js = """
// ==================== محرك المزامنة التلقائية ====================
async function processOutbox() {
    if(!navigator.onLine) return; // إذا لم يوجد إنترنت، لا نفعل شيء
    
    let outbox = await localforage.getItem('kodnaqi_outbox') || [];
    if(outbox.length === 0) return;

    console.log(`🔄 محاولة مزامنة ${outbox.length} فاتورة...`);
    
    for (let i = 0; i < outbox.length; i++) {
        let sale = outbox[i];
        let success = await syncSaleToServer(sale);
        if(success) {
            console.log("✅ تمت مزامنة فاتورة بنجاح");
        } else {
            break; // إذا فشلت واحدة، توقف وحاول لاحقاً
        }
    }
    
    // تحديث الواجهة بعد المزامنة
    loadMedicines();
    if(document.getElementById('view-history').classList.contains('hidden') === false) {
        loadHistory();
    }
}

// تشغيل المزامنة عند عودة الإنترنت
window.addEventListener('online', () => {
    showAlert("عاد الاتصال", "جاري مزامنة الفواتير المعلقة...", "success");
    processOutbox();
});

// محاولة المزامنة كل 30 ثانية في الخلفية
setInterval(processOutbox, 30000);
"""

# حقن محرك المزامنة في نهاية الملف
if "async function processOutbox()" not in js:
    js += "\n" + sync_engine_js

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js (نظام الأوفلاين والمزامنة).")

# ==========================================
# 3. تحديث كاش الـ PWA
# ==========================================
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v5';", "const CACHE_NAME = 'kodnaqi-v6';")
sw = sw.replace("'https://unpkg.com/html5-qrcode',", "'https://unpkg.com/html5-qrcode',\n    'https://cdnjs.cloudflare.com/ajax/libs/localforage/1.10.0/localforage.min.js',")
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v6.")

print("\n🎉 اكتمل التحديث! النظام الآن يعمل بدون إنترنت.")
