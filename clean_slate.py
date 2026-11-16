import os
import re

print("⏳ جاري إعادة بناء ملف app.js من الصفر...")

# ==========================================
# 1. إعادة كتابة app.js بالكامل (نظيف 100%)
# ==========================================
clean_js = """// KodNaqi Pharmacy - Clean App Logic
const API_URL = "/api";
let cart = [];
let html5QrCode = null;

// ==================== 1. التهيئة والدخول ====================
window.addEventListener('load', () => {
    console.log("🚀 App Loaded");
    
    // إخفاء شاشة البداية
    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        if (splash) {
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.display = 'none';
                
                // التحقق من الدخول
                if (localStorage.getItem('kodnaqi_auth') === 'true') {
                    showApp();
                } else {
                    const login = document.getElementById('login-screen');
                    if(login) { login.classList.remove('hidden'); login.classList.add('flex'); }
                }
            }, 500);
        }
    }, 2000);
});

function handleLogin() {
    const user = document.getElementById('login-user')?.value;
    const pass = document.getElementById('login-pass')?.value;
    if (user && pass) {
        localStorage.setItem('kodnaqi_auth', 'true');
        const login = document.getElementById('login-screen');
        if(login) { login.classList.add('hidden'); login.classList.remove('flex'); }
        showApp();
    }
}

function handleLogout() {
    localStorage.removeItem('kodnaqi_auth');
    window.location.reload();
}

function showApp() {
    const app = document.getElementById('app-content');
    if(app) app.classList.remove('hidden');
    loadSettings();
    loadMedicines();
}

// ==================== 2. التنقل بين الصفحات ====================
function switchTab(tabId) {
    ['pos', 'inventory', 'history', 'settings'].forEach(id => {
        const view = document.getElementById(`view-${id}`);
        const btn = document.getElementById(`btn-${id}`);
        if(view) view.classList.add('hidden');
        if(btn) btn.className = "flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/4 transition-all";
    });

    const activeView = document.getElementById(`view-${tabId}`);
    const activeBtn = document.getElementById(`btn-${tabId}`);
    if(activeView) activeView.classList.remove('hidden');
    if(activeBtn) activeBtn.className = "flex flex-col items-center p-2 text-primary w-1/4 transition-all";

    const titles = { pos: 'الكاشير', inventory: 'المخزون', history: 'السجلات', settings: 'الإعدادات' };
    const titleEl = document.getElementById('current-tab-title');
    if(titleEl) titleEl.innerText = titles[tabId];

    if (tabId === 'inventory') loadMedicines();
    if (tabId === 'history') loadHistory();
    if (tabId === 'settings') fetchSettingsForForm();
}

// ==================== 3. النوافذ المنبثقة ====================
function showAlert(title, message, type = 'success') {
    return new Promise((resolve) => {
        const modal = document.getElementById('app-modal');
        const content = document.getElementById('modal-content');
        const iconDiv = document.getElementById('modal-icon');
        const input = document.getElementById('modal-input');
        const cancelBtn = document.getElementById('modal-cancel');
        const confirmBtn = document.getElementById('modal-confirm');
        
        if(!modal) return resolve(true);

        input.classList.add('hidden'); 
        cancelBtn.classList.add('hidden'); 
        confirmBtn.innerText = 'حسناً';
        
        if (type === 'error') {
            iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4";
            iconDiv.innerHTML = '<span class="text-3xl">❌</span>';
            confirmBtn.className = "flex-1 bg-red-600 hover:bg-red-700 text-white py-3 rounded-xl font-bold transition shadow-lg shadow-red-200";
        } else {
            iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-4";
            iconDiv.innerHTML = '<span class="text-3xl text-primary">✅</span>';
            confirmBtn.className = "flex-1 bg-primary hover:bg-[#073629] text-white py-3 rounded-xl font-bold transition shadow-lg shadow-primary/30";
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
        
        if(!modal) return resolve(null);

        iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 mb-4";
        iconDiv.innerHTML = '<span class="text-3xl">💵</span>';
        confirmBtn.className = "flex-1 bg-primary hover:bg-[#073629] text-white py-3 rounded-xl font-bold transition shadow-lg shadow-primary/30";
        confirmBtn.innerText = 'تأكيد الدفع';
        
        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-message').innerText = message;
        input.classList.remove('hidden'); input.value = defaultValue; input.focus();
        cancelBtn.classList.remove('hidden');
        
        modal.classList.remove('hidden'); modal.classList.add('flex');
        setTimeout(() => content.classList.remove('scale-95'), 10);
        
        confirmBtn.onclick = () => { const val = input.value; close(); resolve(val); };
        cancelBtn.onclick = () => { close(); resolve(null); };
        
        function close() {
            content.classList.add('scale-95');
            setTimeout(() => { modal.classList.add('hidden'); modal.classList.remove('flex'); }, 200);
        }
    });
}

// ==================== 4. الإعدادات والمخزون ====================
async function loadSettings() {
    try {
        const res = await fetch(`${API_URL}/settings`);
        const data = await res.json();
        const nameEl = document.getElementById('pharmacy-name');
        if(nameEl) nameEl.innerText = data.pharmacy_name;
    } catch (err) { console.error("Settings error:", err); }
}

async function fetchSettingsForForm() {
    try {
        const res = await fetch(`${API_URL}/settings`);
        const data = await res.json();
        if(document.getElementById('set-name')) document.getElementById('set-name').value = data.pharmacy_name;
        if(document.getElementById('set-currency')) document.getElementById('set-currency').value = data.currency;
    } catch (err) { console.error(err); }
}

document.getElementById('settings-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const res = await fetch(`${API_URL}/settings`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pharmacy_name: document.getElementById('set-name').value, currency: document.getElementById('set-currency').value }) });
        if (res.ok) { await showAlert("تم بنجاح", "تم تحديث الإعدادات.", "success"); loadSettings(); }
    } catch (err) { showAlert("خطأ", "تعذر التحديث", "error"); }
});

async function loadMedicines() {
    try {
        const res = await fetch(`${API_URL}/medicines`);
        const medicines = await res.json();
        const list = document.getElementById('medicines-list');
        if (!list) return;
        if (medicines.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center">لا توجد أدوية.</p>'; return; }
        
        list.innerHTML = medicines.map(med => `
            <div onclick="addToCart(${med.id}, '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl">
                <div><p class="font-bold text-gray-800 text-sm">${med.name}</p><p class="text-xs text-gray-400">باركود: ${med.barcode || 'غير متوفر'}</p></div>
                <div class="text-left"><p class="font-bold text-primary">${med.price} SDG</p><p class="text-xs text-gray-500">المخزون: ${med.stock_quantity}</p></div>
            </div>
        `).join('');
    } catch (err) { console.error("Medicines error:", err); }
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

// ==================== 5. الكاشير والفاتورة ====================
function addToCart(id, name, price) {
    const existing = cart.find(item => item.medicine_id === id);
    if (existing) existing.quantity += 1;
    else cart.push({ medicine_id: id, name: name, unit_price: price, quantity: 1 });
    renderCart();
}

function removeFromCart(index) { cart.splice(index, 1); renderCart(); }

function renderCart() {
    const cartDiv = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');
    if (!cartDiv || !totalEl) return;
    
    if (cart.length === 0) {
        cartDiv.innerHTML = '<p class="text-gray-400 text-sm text-center py-4">الفاتورة فارغة. اضغط على دواء لإضافته.</p>';
        totalEl.innerText = `0 SDG`; return;
    }
    
    let total = 0;
    cartDiv.innerHTML = cart.map((item, index) => {
        total += item.unit_price * item.quantity;
        return `
            <div class="flex justify-between items-center p-3 bg-bg rounded-xl mb-2">
                <div><p class="font-bold text-sm text-primary">${item.name}</p><p class="text-xs text-gray-500">${item.unit_price} SDG × ${item.quantity}</p></div>
                <div class="flex items-center gap-3">
                    <span class="font-bold text-primary">${item.unit_price * item.quantity} SDG</span>
                    <button onclick="removeFromCart(${index})" class="text-red-500 bg-red-50 p-2 rounded-lg hover:bg-red-100 transition">✖</button>
                </div>
            </div>`;
    }).join('');
    totalEl.innerText = `${total} SDG`;
}

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
            await showAlert("تمت العملية", `رقم الفاتورة: <b>${data.invoice_number}</b><br>الباقي: <b class="text-primary text-lg">${change} SDG</b><br><br><button onclick="window.print()" class="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-bold w-full">🖨️ طباعة الفاتورة</button>`, "success");
            cart = []; renderCart(); loadMedicines(); 
        } else showAlert("فشل الحفظ", data.detail, "error");
    } catch (err) { showAlert("خطأ", "تعذر الاتصال بالسيرفر.", "error"); }
}

// ==================== 6. السجلات والطباعة ====================
async function loadHistory() {
    try {
        const res = await fetch(`${API_URL}/sales`);
        const sales = await res.json();
        const list = document.getElementById('history-list');
        if (!list) return;
        
        if (sales.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center py-4">لا توجد فواتير سابقة.</p>'; return; }

        list.innerHTML = sales.map(sale => {
            const date = new Date(sale.sale_date).toLocaleString('en-GB');
            return `
                <div class="flex justify-between items-center p-4 border-b border-gray-100 hover:bg-gray-50 transition">
                    <div><p class="font-bold text-primary">${sale.invoice_number}</p><p class="text-xs text-gray-400 mt-1">${date}</p></div>
                    <div class="text-left flex items-center gap-4">
                        <div><p class="font-bold text-primary">${sale.total_amount} SDG</p><p class="text-xs text-gray-400">${sale.items.length} أصناف</p></div>
                        <button onclick='reprintInvoice(${JSON.stringify(sale)})' class="bg-blue-50 text-blue-600 p-3 rounded-xl hover:bg-blue-100 transition">🖨️</button>
                    </div>
                </div>`;
        }).join('');
    } catch (err) { console.error("History error:", err); }
}

function preparePrintInvoice(invNum, items, total, paid, change, originalDate = null) {
    const nameEl = document.getElementById('print-pharmacy-name');
    if(nameEl) nameEl.innerText = document.getElementById('pharmacy-name').innerText;
    
    let printDate = originalDate ? new Date(originalDate) : new Date();
    document.getElementById('print-date').innerText = `التاريخ: ${printDate.toLocaleDateString('en-GB')} ${printDate.toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit'})}`;
    document.getElementById('print-inv-num').innerText = invNum;
    
    document.getElementById('print-items').innerHTML = items.map(item => `<tr class="border-b border-gray-300 border-dashed"><td class="py-2">${item.name}</td><td class="py-2 text-center">${item.quantity}</td><td class="py-2 text-left">${item.unit_price}</td><td class="py-2 text-left">${item.unit_price * item.quantity}</td></tr>`).join('');
    
    document.getElementById('print-total').innerText = `${total} SDG`;
    document.getElementById('print-paid').innerText = `${paid} SDG`;
    document.getElementById('print-change').innerText = `${change} SDG`;

    if (typeof JsBarcode !== 'undefined') {
        JsBarcode("#print-barcode", invNum, { format: "CODE128", lineColor: "#000", width: 2, height: 40, displayValue: false });
    }
    document.getElementById('print-inv-text').innerText = invNum;
}

function reprintInvoice(sale) {
    const items = sale.items.map(i => ({ name: i.name, quantity: i.quantity, unit_price: i.unit_price }));
    preparePrintInvoice(sale.invoice_number, items, sale.total_amount, sale.paid_amount, (sale.paid_amount - sale.total_amount), sale.sale_date);
    setTimeout(() => window.print(), 500);
}

// ==================== 7. الكاميرا والباركود ====================
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

// ==================== 8. Service Worker ====================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').then(reg => {
            console.log('SW Registered');
        }).catch(err => console.log('SW Error', err));
    });
}
"""

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(clean_js)
print("✅ تم بناء app.js من الصفر (نظيف تماماً).")

# ==========================================
# 2. تحديث Service Worker (لكسر الكاش نهائياً)
# ==========================================
sw_code = """
const CACHE_NAME = 'kodnaqi-v4'; // تحديث الإصدار
const ASSETS = [
    '/', '/index.html', '/app.js', '/manifest.json', '/logo-pharma.png', '/icon-pharma.png',
    'https://cdn.tailwindcss.com', 'https://unpkg.com/html5-qrcode',
    'https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js',
    'https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Poppins:wght@600;700&display=swap'
];

self.addEventListener('install', (e) => {
    self.skipWaiting(); // إجبار التحديث فوراً
    e.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)));
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.map(key => { if (key !== CACHE_NAME) return caches.delete(key); })
        ))
    );
    return self.clients.claim();
});

self.addEventListener('fetch', (e) => {
    if (e.request.url.includes('/api/')) return;
    e.respondWith(
        fetch(e.request).then(res => {
            const resClone = res.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(e.request, resClone));
            return res;
        }).catch(() => caches.match(e.request))
    );
});
"""
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw_code)
print("✅ تم تحديث Service Worker إلى v4 لإجبار المتصفح على التحديث.")

print("\n🎉 اكتمل التنظيف الشامل! يرجى اتباع الخطوات بدقة.")
