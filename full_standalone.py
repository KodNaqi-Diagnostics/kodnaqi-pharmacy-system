import os
import re

print("⏳ جاري تحويل النظام ليعمل بشكل مستقل تماماً (بدون Termux)...")

# 1. قراءة ملف app.js الحالي
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# 2. إضافة منطق التخزين المحلي في بداية الملف
init_db_js = """
let localMedicines = [];
let localSales = [];
let localSettings = { pharmacy_name: "KodNaqi Pharmacy", currency: "SDG" };
"""
if 'localMedicines = []' not in js:
    js = js.replace('const API_URL = "/api";', init_db_js + '\nconst API_URL = "/api";')

# 3. تحديث دالة جلب الأدوية (تعتمد على الهاتف أولاً)
new_load_meds = """
async function loadMedicines() {
    const list = document.getElementById('medicines-list');
    if (!list) return;

    // 1. جلب من ذاكرة الهاتف أولاً (فوري)
    let meds = await localforage.getItem('kodnaqi_medicines') || [];
    renderMedsList(meds, list);

    // 2. محاولة جلب الأحدث من السيرفر في الخلفية
    try {
        const res = await fetch(`${API_URL}/medicines`);
        if(res.ok) {
            const serverMeds = await res.json();
            // تحديث الذاكرة المحلية
            await localforage.setItem('kodnaqi_medicines', serverMeds);
            // تحديث الشاشة
            renderMedsList(serverMeds, list);
        }
    } catch (err) {
        console.log("Offline mode: Using local medicines.");
    }
}

function renderMedsList(medicines, list) {
    if (medicines.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center py-4">لا توجد أدوية.</p>'; return; }
    list.innerHTML = medicines.map(med => `
        <div onclick="addToCart('${med.id}', '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl">
            <div>
                <p class="font-bold text-gray-800 text-sm">${med.name}</p>
                <p class="text-xs text-gray-500">${med.scientific_name || ''} ${med.category ? '| ' + med.category : ''}</p>
            </div>
            <div class="text-left">
                <p class="font-bold text-primary">${formatCurrency(med.price)} SDG</p>
                <p class="text-[10px] text-gray-400">المخزون: ${med.stock_quantity}</p>
            </div>
        </div>
    `).join('');
}
"""
js = re.sub(r'async function loadMedicines\(\) \{.*?\n\}', new_load_meds, js, flags=re.DOTALL)

# 4. تحديث دالة إضافة دواء جديد (تحفظ في الهاتف أولاً)
new_add_med = """
document.getElementById('add-medicine-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // إنشاء معرف محلي فريد (إذا كنا أوفلاين)
    const localId = 'loc_' + Date.now();
    
    const data = {
        id: localId,
        name: document.getElementById('med-name').value,
        scientific_name: document.getElementById('med-scientific').value || null,
        category: document.getElementById('med-category').value || null,
        price: parseFloat(document.getElementById('med-price').value),
        stock_quantity: parseInt(document.getElementById('med-stock').value),
        barcode: document.getElementById('med-barcode').value || null,
        expiry_date: document.getElementById('med-expiry').value || null,
        cost: 0
    };

    // 1. الحفظ في ذاكرة الهاتف فوراً (لضمان عدم ضياع البيانات)
    let meds = await localforage.getItem('kodnaqi_medicines') || [];
    meds.push(data);
    await localforage.setItem('kodnaqi_medicines', meds);
    
    // 2. إضافة لطابور المزامنة
    let medOutbox = await localforage.getItem('kodnaqi_med_outbox') || [];
    medOutbox.push(data);
    await localforage.setItem('kodnaqi_med_outbox', medOutbox);

    // 3. تحديث الواجهة
    await showAlert("تم الحفظ محلياً", `تم إضافة الدواء <b>${data.name}</b> إلى ذاكرة الهاتف.`, "success");
    document.getElementById('add-medicine-form').reset();
    switchTab('pos');
    
    // 4. محاولة الإرسال للسيرفر في الخلفية
    syncMedicinesToServer();
});

async function syncMedicinesToServer() {
    try {
        let medOutbox = await localforage.getItem('kodnaqi_med_outbox') || [];
        if(medOutbox.length === 0) return;

        for (let i = 0; i < medOutbox.length; i++) {
            let med = medOutbox[i];
            // إرسال للسيرفر (بدون الـ ID المحلي)
            let sendData = {...med};
            delete sendData.id; 

            const res = await fetch(`${API_URL}/medicines`, { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify(sendData) 
            });
            
            if (res.ok) {
                // إذا نجح، نحذفه من طابور الانتظار
                medOutbox.splice(i, 1);
                i--;
            } else {
                break; // توقف إذا فشل الاتصال
            }
        }
        await localforage.setItem('kodnaqi_med_outbox', medOutbox);
        // جلب أحدث نسخة من السيرفر
        const res = await fetch(`${API_URL}/medicines`);
        if(res.ok) {
            const serverMeds = await res.json();
            await localforage.setItem('kodnaqi_medicines', serverMeds);
        }
    } catch(err) {
        console.log("Sync paused: Server unreachable.");
    }
}
"""
js = re.sub(r"document\.getElementById\('add-medicine-form'\)\?\.addEventListener\('submit', async \(e\) => \{.*?\n\}\);", new_add_med, js, flags=re.DOTALL)

# 5. تحديث دالة الدفع (تخصم من المخزون المحلي فوراً)
new_checkout = """
async function checkout() {
    if (cart.length === 0) return showAlert("تنبيه", "الفاتورة فارغة.", "error");
    let total = cart.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
    const paid = await showPrompt("الدفع", `الإجمالي المطلوب: ${formatCurrency(total)} SDG`, total);
    if (paid === null || paid === "") return; 
    const paidAmount = parseFloat(paid);
    if (isNaN(paidAmount) || paidAmount < total) return showAlert("خطأ", "المبلغ المدفوع غير كافٍ!", "error");

    const localId = Date.now();
    const saleData = { 
        id: localId,
        discount: 0, 
        paid_amount: paidAmount, 
        items: cart.map(i => ({ medicine_id: i.medicine_id, name: i.name, quantity: i.quantity, unit_price: i.unit_price })),
        invoice_number: `OFF-${localId.toString().slice(-6)}`,
        sale_date: new Date().toISOString()
    };

    // 1. خصم الكميات من ذاكرة الهاتف (المخزون المحلي)
    let meds = await localforage.getItem('kodnaqi_medicines') || [];
    cart.forEach(cartItem => {
        let med = meds.find(m => m.id == cartItem.medicine_id);
        if(med) med.stock_quantity -= cartItem.quantity;
    });
    await localforage.setItem('kodnaqi_medicines', meds);

    // 2. إضافة الفاتورة للسجلات المحلية
    let sales = await localforage.getItem('kodnaqi_sales') || [];
    sales.unshift(saleData); // إضافتها في البداية
    await localforage.setItem('kodnaqi_sales', sales);

    // 3. إضافتها لطابور المزامنة
    let outbox = await localforage.getItem('kodnaqi_outbox') || [];
    outbox.push(saleData);
    await localforage.setItem('kodnaqi_outbox', outbox);

    // 4. تجهيز وطباعة الفاتورة
    const change = paidAmount - total;
    preparePrintInvoice(saleData.invoice_number, cart, total, paidAmount, change);
    
    let msg = `رقم الفاتورة: <b>${saleData.invoice_number}</b><br>الباقي: <b class="text-primary text-lg">${formatCurrency(change)} SDG</b>`;
    msg += `<br><br><button onclick="window.print()" class="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-bold w-full">🖨️ طباعة الفاتورة</button>`;
    
    await showAlert("تمت العملية", msg, "success");
    
    cart = []; 
    renderCart(); 
    loadMedicines(); // لتحديث الكميات
    
    // محاولة المزامنة في الخلفية
    processOutbox();
}
"""
js = re.sub(r'async function checkout\(\) \{.*?(?=// دالة إرسال الفاتورة للسيرفر)', new_checkout + "\n\n", js, flags=re.DOTALL)

# 6. تحديث محرك المزامنة ليرسل الفواتير والأدوية
new_process_outbox = """
async function processOutbox() {
    if(!navigator.onLine) return; 
    
    // 1. مزامنة الفواتير
    let outbox = await localforage.getItem('kodnaqi_outbox') || [];
    for (let i = 0; i < outbox.length; i++) {
        let sale = outbox[i];
        let sendData = { discount: sale.discount, paid_amount: sale.paid_amount, items: sale.items.map(item => ({ medicine_id: item.medicine_id, quantity: item.quantity, unit_price: item.unit_price })) };
        
        try {
            let res = await fetch(`${API_URL}/sales`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sendData) });
            if (res.ok) {
                outbox.splice(i, 1);
                i--;
            } else { break; }
        } catch(e) { break; }
    }
    await localforage.setItem('kodnaqi_outbox', outbox);

    // 2. مزامنة الأدوية الجديدة
    syncMedicinesToServer();
}
"""
js = re.sub(r'async function processOutbox\(\) \{.*?\n\}', new_process_outbox, js, flags=re.DOTALL)

# 7. تحديث السجلات لتقرأ من الهاتف
new_load_history = """
async function loadHistory() {
    const list = document.getElementById('history-list');
    if (!list) return;
    
    // 1. جلب من الهاتف
    let sales = await localforage.getItem('kodnaqi_sales') || [];
    renderHistoryList(sales, list);

    // 2. جلب من السيرفر
    try {
        const res = await fetch(`${API_URL}/sales`);
        if(res.ok) {
            const serverSales = await res.json();
            // دمج البيانات (تجنب التكرار بناءً على رقم الفاتورة)
            let mergedSales = [...sales];
            serverSales.forEach(ss => {
                if(!mergedSales.find(s => s.invoice_number === ss.invoice_number)) mergedSales.push(ss);
            });
            mergedSales.sort((a,b) => new Date(b.sale_date) - new Date(a.sale_date));
            await localforage.setItem('kodnaqi_sales', mergedSales);
            renderHistoryList(mergedSales, list);
        }
    } catch(e) {}
}

function renderHistoryList(sales, list) {
    if (sales.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center py-4">لا توجد فواتير سابقة.</p>'; return; }
    list.innerHTML = sales.map(sale => {
        const date = new Date(sale.sale_date).toLocaleString('en-GB');
        const isSynced = !sale.invoice_number.startsWith('OFF-');
        return `
            <div class="flex justify-between items-center p-4 border-b border-gray-100 hover:bg-gray-50 transition">
                <div>
                    <p class="font-bold text-primary">${sale.invoice_number} ${!isSynced ? '<span class="text-[9px] text-orange-500 bg-orange-50 px-1 rounded">معلق</span>' : ''}</p>
                    <p class="text-xs text-gray-400 mt-1">${date}</p>
                </div>
                <div class="text-left flex items-center gap-4">
                    <div><p class="font-bold text-primary">${formatCurrency(sale.total_amount || sale.items.reduce((s,i)=>s+(i.unit_price*i.quantity),0))} SDG</p><p class="text-xs text-gray-400">${sale.items.length} أصناف</p></div>
                    <button onclick='reprintInvoice(${JSON.stringify(sale)})' class="bg-blue-50 text-blue-600 p-3 rounded-xl hover:bg-blue-100 transition">🖨️</button>
                </div>
            </div>`;
    }).join('');
}
"""
js = re.sub(r'async function loadHistory\(\) \{.*?\n\}', new_load_history, js, flags=re.DOTALL)

# 8. تحديث الطباعة لتقبل الفواتير المحلية
new_print = """
function reprintInvoice(sale) {
    let total = sale.total_amount || sale.items.reduce((sum, i) => sum + (i.unit_price * i.quantity), 0);
    let items = sale.items;
    preparePrintInvoice(sale.invoice_number, items, total, sale.paid_amount, (sale.paid_amount - total), sale.sale_date);
    setTimeout(() => window.print(), 500);
}
"""
js = re.sub(r'function reprintInvoice\(sale\) \{.*?\n\}', new_print, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحويل app.js ليعمل بشكل مستقل (Local-First).")

# 9. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v12';", "const CACHE_NAME = 'kodnaqi-v13';")
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v13.")

print("\n🎉 اكتمل التحديث! الآن التطبيق مستقل تماماً.")
