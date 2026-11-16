import os

# التأكد من وجود مجلد static
if not os.path.exists("static"):
    os.makedirs("static")
    print("تم إنشاء مجلد static")

# ==========================================
# 1. كتابة ملف index.html بالكامل (محدث)
# ==========================================
html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KodNaqi Pharmacy</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <link rel="manifest" href="/manifest.json">
    <style>
        /* تنسيقات خاصة بالطباعة فقط */
        @media print {
            body > * {
                display: none !important; /* إخفاء كل شيء */
            }
            #print-area {
                display: block !important; /* إظهار الفاتورة فقط */
                position: absolute;
                left: 0;
                top: 0;
                width: 100%;
                max-width: 80mm; /* حجم طابعة حرارية */
                margin: 0;
                padding: 10px;
                color: #000 !important;
                background: #fff !important;
            }
            #app-modal {
                display: none !important; /* إخفاء النافذة المنبثقة */
            }
            @page { margin: 0; }
        }
    </style>
</head>
<body class="bg-gray-100 text-gray-800 font-sans pb-20">
    <header class="bg-emerald-600 text-white p-4 shadow-md sticky top-0 z-10 flex justify-between items-center">
        <h1 id="pharmacy-name" class="text-xl font-bold">جاري التحميل...</h1>
        <span id="current-tab-title" class="text-sm bg-emerald-700 px-3 py-1 rounded-full">الكاشير</span>
    </header>

    <main class="p-4 max-w-4xl mx-auto">
        <!-- قسم الكاشير -->
        <div id="view-pos" class="space-y-6">
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h2 class="text-lg font-semibold mb-4">إضافة دواء للفاتورة</h2>
                <div class="flex gap-2">
                    <input type="text" id="search-input" placeholder="ابحث باسم الدواء أو امسح الباركود..." class="flex-1 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-emerald-500">
                    <button onclick="startScanner()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition flex items-center gap-2">📷 مسح</button>
                </div>
                <div id="reader" class="w-full mt-4 hidden rounded-lg overflow-hidden border-2 border-emerald-500"></div>
                <button onclick="stopScanner()" id="stop-btn" class="hidden mt-2 text-red-600 text-sm font-semibold">إيقاف الكاميرا</button>
            </div>

            <div class="bg-white p-6 rounded-xl shadow-sm border-2 border-emerald-500">
                <h2 class="text-lg font-semibold mb-4 text-emerald-800">🛒 الفاتورة الحالية</h2>
                <div id="cart-items" class="space-y-2 mb-4">
                    <p class="text-gray-400 text-sm text-center">الفاتورة فارغة.</p>
                </div>
                <div class="border-t border-gray-200 pt-4 flex justify-between items-center text-lg font-bold">
                    <span>الإجمالي:</span>
                    <span id="cart-total" class="text-emerald-600">0 SDG</span>
                </div>
                <button onclick="checkout()" class="w-full mt-4 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-lg font-bold text-lg transition">💵 إتمام الدفع</button>
            </div>

            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h2 class="text-lg font-semibold mb-4">الأدوية المتوفرة</h2>
                <div id="medicines-list" class="space-y-2"><p class="text-gray-500">جاري تحميل الأدوية...</p></div>
            </div>
        </div>

        <!-- قسم المخزون -->
        <div id="view-inventory" class="hidden space-y-6">
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h2 class="text-lg font-semibold mb-4 text-blue-800">➕ إضافة دواء جديد للمخزون</h2>
                <form id="add-medicine-form" class="space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                        <input type="text" id="med-name" placeholder="اسم الدواء (إجباري)" required class="border p-3 rounded-lg">
                        <input type="text" id="med-barcode" placeholder="الباركود (اختياري)" class="border p-3 rounded-lg">
                        <input type="number" id="med-price" placeholder="سعر البيع (SDG)" required class="border p-3 rounded-lg">
                        <input type="number" id="med-cost" placeholder="سعر التكلفة (SDG)" class="border p-3 rounded-lg">
                        <input type="number" id="med-stock" placeholder="الكمية" required class="border p-3 rounded-lg">
                        <input type="text" id="med-expiry" placeholder="تاريخ الانتهاء (YYYY-MM-DD)" class="border p-3 rounded-lg">
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-bold">حفظ الدواء</button>
                </form>
            </div>
        </div>

        <!-- قسم الإعدادات -->
        <div id="view-settings" class="hidden space-y-6">
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h2 class="text-lg font-semibold mb-4 text-gray-800">⚙️ إعدادات الصيدلية</h2>
                <form id="settings-form" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">اسم الصيدلية</label>
                        <input type="text" id="set-name" required class="w-full border p-3 rounded-lg">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">العملة</label>
                        <input type="text" id="set-currency" required class="w-full border p-3 rounded-lg">
                    </div>
                    <button type="submit" class="w-full bg-gray-800 hover:bg-gray-900 text-white py-3 rounded-lg font-bold">تحديث الإعدادات</button>
                </form>
            </div>
        </div>
    </main>

    <!-- شريط التنقل السفلي -->
    <nav class="fixed bottom-0 w-full bg-white border-t border-gray-200 flex justify-around p-2 z-20 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
        <button onclick="switchTab('pos')" id="btn-pos" class="flex flex-col items-center p-2 text-emerald-600 w-1/3"><span class="text-2xl">🛒</span><span class="text-xs font-bold mt-1">الكاشير</span></button>
        <button onclick="switchTab('inventory')" id="btn-inventory" class="flex flex-col items-center p-2 text-gray-400 hover:text-emerald-600 w-1/3"><span class="text-2xl">📦</span><span class="text-xs font-bold mt-1">المخزون</span></button>
        <button onclick="switchTab('settings')" id="btn-settings" class="flex flex-col items-center p-2 text-gray-400 hover:text-emerald-600 w-1/3"><span class="text-2xl">⚙️</span><span class="text-xs font-bold mt-1">الإعدادات</span></button>
    </nav>

    <!-- منطقة الفاتورة القابلة للطباعة -->
    <div id="print-area" class="hidden bg-white text-black p-4 w-full max-w-sm mx-auto font-sans text-sm" dir="rtl">
        <div class="text-center border-b-2 border-black border-dashed pb-2 mb-2">
            <h2 id="print-pharmacy-name" class="text-2xl font-bold mb-1">KodNaqi Pharmacy</h2>
            <p class="text-xs">صيدلية معتمدة - نخدمكم بكل ثقة</p>
            <p class="text-xs" id="print-date">التاريخ: 2026-11-16 10:00</p>
            <p class="text-xs font-bold mt-1">رقم الفاتورة: <span id="print-inv-num">INV-123</span></p>
        </div>
        <table class="w-full text-xs text-right mb-2">
            <thead>
                <tr class="border-b border-black">
                    <th class="pb-1">الصنف</th><th class="pb-1 text-center">الكمية</th><th class="pb-1 text-left">السعر</th><th class="pb-1 text-left">الإجمالي</th>
                </tr>
            </thead>
            <tbody id="print-items"></tbody>
        </table>
        <div class="border-t-2 border-black border-dashed pt-2 mb-4 space-y-1 text-sm">
            <div class="flex justify-between font-bold"><span>الإجمالي:</span><span id="print-total">0 SDG</span></div>
            <div class="flex justify-between"><span>المدفوع:</span><span id="print-paid">0 SDG</span></div>
            <div class="flex justify-between"><span>الباقي:</span><span id="print-change">0 SDG</span></div>
        </div>
        <div class="flex justify-between items-end mt-8 text-xs text-center">
            <div><p class="mb-8">توقيع الصيدلي</p><p class="border-t border-black w-24 pt-1 border-dashed">........................</p></div>
            <div class="border-2 border-gray-400 border-dashed rounded-full w-20 h-20 flex items-center justify-center text-gray-400 transform rotate-12">الختم</div>
        </div>
        <div class="text-center text-xs mt-4 border-t border-black border-dashed pt-2">
            <p>شكراً لزيارتكم، نتمنى لكم الشفاء العاجل!</p>
        </div>
    </div>

    <!-- النافذة المنبثقة -->
    <div id="app-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm hidden items-center justify-center z-50 transition-opacity duration-300">
        <div class="bg-white rounded-2xl shadow-2xl p-6 w-11/12 max-w-sm transform scale-95 transition-transform duration-300" id="modal-content">
            <div id="modal-icon" class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-emerald-100 mb-4"><span class="text-3xl">✅</span></div>
            <h3 id="modal-title" class="text-xl font-bold text-center text-gray-800 mb-2">عنوان</h3>
            <p id="modal-message" class="text-center text-gray-600 mb-6 text-sm">رسالة</p>
            <input type="number" id="modal-input" class="hidden w-full text-center text-2xl font-bold border-2 border-emerald-500 rounded-lg p-3 mb-6 focus:outline-none focus:ring-4 focus:ring-emerald-200" dir="ltr">
            <div class="flex gap-3">
                <button id="modal-cancel" class="hidden flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 py-3 rounded-xl font-bold transition">إلغاء</button>
                <button id="modal-confirm" class="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-bold transition shadow-lg shadow-emerald-200">موافق</button>
            </div>
        </div>
    </div>

    <script src="/app.js"></script>
</body>
</html>"""

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("✅ تم تحديث ملف index.html بنجاح.")

# ==========================================
# 2. كتابة ملف app.js بالكامل (محدث)
# ==========================================
js_content = """let html5QrCode = null;
const API_URL = "/api";
let cart = []; 

function showAlert(title, message, type = 'success') {
    return new Promise((resolve) => {
        const modal = document.getElementById('app-modal');
        const content = document.getElementById('modal-content');
        const iconDiv = document.getElementById('modal-icon');
        const input = document.getElementById('modal-input');
        const cancelBtn = document.getElementById('modal-cancel');
        const confirmBtn = document.getElementById('modal-confirm');
        input.classList.add('hidden'); cancelBtn.classList.add('hidden'); confirmBtn.innerText = 'حسناً';
        if (type === 'error') {
            iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4";
            iconDiv.innerHTML = '<span class="text-3xl">❌</span>';
            confirmBtn.className = "flex-1 bg-red-600 hover:bg-red-700 text-white py-3 rounded-xl font-bold transition shadow-lg shadow-red-200";
        } else {
            iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-emerald-100 mb-4";
            iconDiv.innerHTML = '<span class="text-3xl">✅</span>';
            confirmBtn.className = "flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-bold transition shadow-lg shadow-emerald-200";
        }
        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-message').innerHTML = message;
        modal.classList.remove('hidden'); modal.classList.add('flex');
        setTimeout(() => content.classList.remove('scale-95'), 10);
        confirmBtn.onclick = () => {
            content.classList.add('scale-95');
            setTimeout(() => { modal.classList.add('hidden'); modal.classList.remove('flex'); }, 200);
            resolve(true);
        };
    });
}

function showPrompt(title, message, defaultValue) {
    return new Promise((resolve) => {
        const modal = document.getElementById('app-modal');
        const content = document.getElementById('modal-content');
        const iconDiv = document.getElementById('modal-icon');
        const input = document.getElementById('modal-input');
        const cancelBtn = document.getElementById('modal-cancel');
        const confirmBtn = document.getElementById('modal-confirm');
        iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 mb-4";
        iconDiv.innerHTML = '<span class="text-3xl">💵</span>';
        confirmBtn.className = "flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-bold transition shadow-lg shadow-emerald-200";
        confirmBtn.innerText = 'تأكيد الدفع';
        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-message').innerText = message;
        input.classList.remove('hidden'); input.value = defaultValue; input.focus(); input.select();
        cancelBtn.classList.remove('hidden');
        modal.classList.remove('hidden'); modal.classList.add('flex');
        setTimeout(() => content.classList.remove('scale-95'), 10);
        confirmBtn.onclick = () => { const val = input.value; closeModal(); resolve(val); };
        cancelBtn.onclick = () => { closeModal(); resolve(null); };
        function closeModal() {
            content.classList.add('scale-95');
            setTimeout(() => { modal.classList.add('hidden'); modal.classList.remove('flex'); }, 200);
        }
    });
}

async function loadSettings() {
    try {
        const res = await fetch(`${API_URL}/settings`);
        const data = await res.json();
        document.getElementById('pharmacy-name').innerText = data.pharmacy_name;
    } catch (err) { console.error(err); }
}

async function loadMedicines() {
    try {
        const res = await fetch(`${API_URL}/medicines`);
        const medicines = await res.json();
        const list = document.getElementById('medicines-list');
        if (medicines.length === 0) { list.innerHTML = '<p class="text-gray-500">لا توجد أدوية.</p>'; return; }
        list.innerHTML = medicines.map(med => `
            <div onclick="addToCart(${med.id}, '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-emerald-50 transition">
                <div><p class="font-bold text-gray-800">${med.name}</p><p class="text-xs text-gray-500">باركود: ${med.barcode || 'غير متوفر'}</p></div>
                <div class="text-left"><p class="font-bold text-emerald-700">${med.price} SDG</p><p class="text-xs text-gray-500">المخزون: ${med.stock_quantity}</p></div>
            </div>
        `).join('');
    } catch (err) { console.error(err); }
}

function addToCart(id, name, price) {
    const existing = cart.find(item => item.medicine_id === id);
    if (existing) existing.quantity += 1;
    else cart.push({ medicine_id: id, name: name, unit_price: price, quantity: 1 });
    renderCart();
}

function renderCart() {
    const cartDiv = document.getElementById('cart-items');
    if (cart.length === 0) {
        cartDiv.innerHTML = '<p class="text-gray-400 text-sm text-center">الفاتورة فارغة.</p>';
        document.getElementById('cart-total').innerText = `0 SDG`; return;
    }
    let total = 0;
    cartDiv.innerHTML = cart.map((item, index) => {
        total += item.unit_price * item.quantity;
        return `
            <div class="flex justify-between items-center p-2 bg-gray-50 rounded border border-gray-100">
                <div><p class="font-bold text-sm">${item.name}</p><p class="text-xs text-gray-500">${item.unit_price} SDG × ${item.quantity}</p></div>
                <div class="flex items-center gap-2"><span class="font-bold text-emerald-600">${item.unit_price * item.quantity} SDG</span>
                <button onclick="removeFromCart(${index})" class="text-red-500 hover:bg-red-100 p-1 rounded">✖</button></div>
            </div>`;
    }).join('');
    document.getElementById('cart-total').innerText = `${total} SDG`;
}

function removeFromCart(index) { cart.splice(index, 1); renderCart(); }

async function checkout() {
    if (cart.length === 0) return showAlert("تنبيه", "الفاتورة فارغة.", "error");
    let total = cart.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
    const paid = await showPrompt("الدفع", `الإجمالي المطلوب: ${total} SDG`, total);
    if (paid === null || paid === "") return; 
    const paidAmount = parseFloat(paid);
    if (isNaN(paidAmount) || paidAmount < total) return showAlert("خطأ", "المبلغ المدفوع غير كافٍ!", "error");

    const saleData = { discount: 0, paid_amount: paidAmount, items: cart.map(i => ({ medicine_id: i.medicine_id, quantity: i.quantity, unit_price: i.unit_price })) };

    try {
        const res = await fetch(`${API_URL}/sales`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(saleData) });
        const data = await res.json();
        if (res.ok) {
            const change = paidAmount - total;
            preparePrintInvoice(data.invoice_number, cart, total, paidAmount, change);
            await showAlert("تمت العملية بنجاح", `رقم الفاتورة: <b>${data.invoice_number}</b><br><br>الباقي للعميل: <b class="text-emerald-600 text-lg">${change} SDG</b><br><br>
                <button onclick="window.print()" class="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 w-full">🖨️ طباعة الفاتورة</button>`, "success");
            cart = []; renderCart(); loadMedicines(); 
        } else showAlert("فشل الحفظ", data.detail, "error");
    } catch (err) { showAlert("خطأ", "تعذر الاتصال بالسيرفر.", "error"); }
}

function preparePrintInvoice(invNum, items, total, paid, change) {
    document.getElementById('print-pharmacy-name').innerText = document.getElementById('pharmacy-name').innerText;
    const now = new Date();
    document.getElementById('print-date').innerText = `التاريخ: ${now.toLocaleDateString('en-GB')} ${now.toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit'})}`;
    document.getElementById('print-inv-num').innerText = invNum;
    document.getElementById('print-items').innerHTML = items.map(item => `<tr class="border-b border-gray-300 border-dashed"><td class="py-1">${item.name}</td><td class="py-1 text-center">${item.quantity}</td><td class="py-1 text-left">${item.unit_price}</td><td class="py-1 text-left">${item.unit_price * item.quantity}</td></tr>`).join('');
    document.getElementById('print-total').innerText = `${total} SDG`;
    document.getElementById('print-paid').innerText = `${paid} SDG`;
    document.getElementById('print-change').innerText = `${change} SDG`;
}

function startScanner() {
    document.getElementById('reader').classList.remove('hidden');
    document.getElementById('stop-btn').classList.remove('hidden');
    html5QrCode = new Html5Qrcode("reader");
    html5QrCode.start({ facingMode: "environment" }, { fps: 10, qrbox: { width: 250, height: 150 } }, (decodedText) => { stopScanner(); findMedicineByBarcode(decodedText); }, (e) => {}).catch(err => showAlert("خطأ", "تأكد من صلاحية الكاميرا", "error"));
}

function stopScanner() {
    if (html5QrCode) {
        html5QrCode.stop().then(() => {
            document.getElementById('reader').classList.add('hidden');
            document.getElementById('stop-btn').classList.add('hidden');
            html5QrCode = null;
        });
    }
}

async function findMedicineByBarcode(barcode) {
    try {
        const res = await fetch(`${API_URL}/medicines/barcode/${barcode}`);
        if (res.ok) {
            const med = await res.json();
            addToCart(med.id, med.name, med.price);
            showAlert("تمت الإضافة", `تم إضافة <b>${med.name}</b> للفاتورة.`, "success");
        } else showAlert("غير موجود", `لا يوجد دواء بالباركود: ${barcode}`, "error");
    } catch (err) { console.error(err); }
}

function switchTab(tabId) {
    document.getElementById('view-pos').classList.add('hidden');
    document.getElementById('view-inventory').classList.add('hidden');
    document.getElementById('view-settings').classList.add('hidden');
    document.getElementById('btn-pos').className = "flex flex-col items-center p-2 text-gray-400 hover:text-emerald-600 w-1/3";
    document.getElementById('btn-inventory').className = "flex flex-col items-center p-2 text-gray-400 hover:text-emerald-600 w-1/3";
    document.getElementById('btn-settings').className = "flex flex-col items-center p-2 text-gray-400 hover:text-emerald-600 w-1/3";
    document.getElementById(`view-${tabId}`).classList.remove('hidden');
    document.getElementById(`btn-${tabId}`).className = "flex flex-col items-center p-2 text-emerald-600 w-1/3";
    const titles = { pos: 'الكاشير', inventory: 'المخزون', settings: 'الإعدادات' };
    document.getElementById('current-tab-title').innerText = titles[tabId];
    if (tabId === 'settings') fetchSettingsForForm();
    if (tabId === 'inventory') loadMedicines();
}

document.getElementById('add-medicine-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        name: document.getElementById('med-name').value,
        barcode: document.getElementById('med-barcode').value || null,
        price: parseFloat(document.getElementById('med-price').value),
        cost: parseFloat(document.getElementById('med-cost').value) || 0,
        stock_quantity: parseInt(document.getElementById('med-stock').value),
        expiry_date: document.getElementById('med-expiry').value || null,
    };
    try {
        const res = await fetch(`${API_URL}/medicines`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        if (res.ok) {
            await showAlert("تم بنجاح", `تم إضافة الدواء <b>${data.name}</b>.`, "success");
            document.getElementById('add-medicine-form').reset();
            switchTab('pos');
        } else showAlert("خطأ", "تأكد من أن الباركود غير مكرر.", "error");
    } catch (err) { showAlert("خطأ", "تعذر الاتصال بالسيرفر", "error"); }
});

async function fetchSettingsForForm() {
    try {
        const res = await fetch(`${API_URL}/settings`);
        const data = await res.json();
        document.getElementById('set-name').value = data.pharmacy_name;
        document.getElementById('set-currency').value = data.currency;
    } catch (err) { console.error(err); }
}

document.getElementById('settings-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const res = await fetch(`${API_URL}/settings`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pharmacy_name: document.getElementById('set-name').value, currency: document.getElementById('set-currency').value }) });
        if (res.ok) { await showAlert("تم بنجاح", "تم تحديث الإعدادات.", "success"); loadSettings(); }
    } catch (err) { showAlert("خطأ", "تعذر التحديث", "error"); }
});

document.addEventListener('DOMContentLoaded', () => { loadSettings(); loadMedicines(); });
"""

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js_content)
print("✅ تم تحديث ملف app.js بنجاح.")
print("🎉 كل شيء جاهز! قم بعمل Refresh للمتصفح الآن.")
