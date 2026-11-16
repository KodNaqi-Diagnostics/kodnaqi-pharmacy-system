
let localMedicines = [];
let localSales = [];
let localSettings = { pharmacy_name: "KodNaqi Pharmacy", currency: "SDG" };

const API_URL = "/api";
function formatCurrency(num) { return Number(num).toLocaleString('en-US'); }
let cart = [];
let html5QrCode = null;

// 1. التهيئة والدخول
window.addEventListener('load', () => {
    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        if (splash) {
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.display = 'none';
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
    switchTab('dashboard'); // افتح الرئيسية أولاً
}



async function loadDashboard() {
    try {
        const res = await fetch(`${API_URL}/stats`);
        const data = await res.json();
        
        document.getElementById('stat-revenue').innerText = `${formatCurrency(data.today_revenue)} SDG`;
        document.getElementById('stat-count').innerText = `${data.today_sales_count} فاتورة`;
        document.getElementById('stat-profit').innerText = `${formatCurrency(data.today_profit)} SDG`;
        
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


// 2. التنقل

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


// 3. النوافذ
function showAlert(title, message, type = 'success') {
    return new Promise((resolve) => {
        const modal = document.getElementById('app-modal');
        const content = document.getElementById('modal-content');
        const iconDiv = document.getElementById('modal-icon');
        const input = document.getElementById('modal-input');
        const cancelBtn = document.getElementById('modal-cancel');
        const confirmBtn = document.getElementById('modal-confirm');
        if(!modal) return resolve(true);
        input.classList.add('hidden'); cancelBtn.classList.add('hidden'); confirmBtn.innerText = 'حسناً';
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
        function close() { content.classList.add('scale-95'); setTimeout(() => { modal.classList.add('hidden'); modal.classList.remove('flex'); }, 200); }
    });
}

// 4. الإعدادات

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

// 5. المخزون


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

function filterMedicines() {
    const query = document.getElementById('pos-search').value.toLowerCase();
    const items = document.querySelectorAll('#medicines-list > div');
    items.forEach(item => {
        const text = item.innerText.toLowerCase();
        item.style.display = text.includes(query) ? 'flex' : 'none';
    });
}


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


// 6. الكاشير
function addToCart(id, name, price) {
    const existing = cart.find(item => item.medicine_id === id);
    if (existing) existing.quantity += 1;
    else cart.push({ medicine_id: id, name: name, unit_price: price, quantity: 1 });
    renderCart();
}

function removeFromCart(index) { cart.splice(index, 1); renderCart(); }

function updateQuantity(index, change) {
    cart[index].quantity += change;
    if (cart[index].quantity <= 0) cart.splice(index, 1);
    renderCart();
}

function renderCart() {
    const cartDiv = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');
    if (!cartDiv || !totalEl) return;
    if (cart.length === 0) {
        cartDiv.innerHTML = '<p class="text-gray-400 text-sm text-center py-4">الفاتورة فارغة.</p>';
        totalEl.innerText = `0 SDG`; return;
    }
    let total = 0;
    cartDiv.innerHTML = cart.map((item, index) => {
        total += item.unit_price * item.quantity;
        return `
            <div class="flex justify-between items-center p-3 bg-bg rounded-xl mb-2">
                <div class="flex-1">
                    <p class="font-bold text-sm text-primary">${item.name}</p>
                    <p class="text-xs text-gray-500">${item.unit_price} SDG</p>
                </div>
                <div class="flex items-center gap-3">
                    <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-100">
                        <button onclick="updateQuantity(${index}, 1)" class="px-3 py-1 text-primary font-bold hover:bg-gray-50 rounded-r-lg">+</button>
                        <span class="px-2 font-bold text-sm">${item.quantity}</span>
                        <button onclick="updateQuantity(${index}, -1)" class="px-3 py-1 text-red-500 font-bold hover:bg-gray-50 rounded-l-lg">-</button>
                    </div>
                    <span class="font-bold text-primary w-20 text-left">${formatCurrency(item.unit_price * item.quantity)} SDG</span>
                    <button onclick="removeFromCart(${index})" class="text-red-500 bg-red-50 p-2 rounded-lg hover:bg-red-100 transition">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </div>
            </div>`;
    }).join('');
    totalEl.innerText = `${formatCurrency(total)} SDG`;
}



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


// 7. السجلات والطباعة

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


function preparePrintInvoice(invNum, items, total, paid, change, originalDate = null) {
    const nameEl = document.getElementById('print-pharmacy-name');
    if(nameEl) nameEl.innerText = document.getElementById('pharmacy-name').innerText;
    let printDate = originalDate ? new Date(originalDate) : new Date();
    document.getElementById('print-date').innerText = `التاريخ: ${printDate.toLocaleDateString('en-GB')} ${printDate.toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit'})}`;
    document.getElementById('print-inv-num').innerText = invNum;
    document.getElementById('print-items').innerHTML = items.map(item => `<tr class="border-b border-gray-300 border-dashed"><td class="py-2">${item.name}</td><td class="py-2 text-center">${item.quantity}</td><td class="py-2 text-left">${formatCurrency(item.unit_price)}</td><td class="py-2 text-left">${formatCurrency(item.unit_price * item.quantity)}</td></tr>`).join('');
    document.getElementById('print-total').innerText = `${formatCurrency(total)} SDG`;
    document.getElementById('print-paid').innerText = `${formatCurrency(paid)} SDG`;
    document.getElementById('print-change').innerText = `${formatCurrency(change)} SDG`;
    if (typeof JsBarcode !== 'undefined') JsBarcode("#print-barcode", invNum, { format: "CODE128", lineColor: "#000", width: 2, height: 40, displayValue: false });
    document.getElementById('print-inv-text').innerText = invNum;
}


function reprintInvoice(sale) {
    let total = sale.total_amount || sale.items.reduce((sum, i) => sum + (i.unit_price * i.quantity), 0);
    let items = sale.items;
    preparePrintInvoice(sale.invoice_number, items, total, sale.paid_amount, (sale.paid_amount - total), sale.sale_date);
    setTimeout(() => window.print(), 500);
}


// 8. الكاميرا
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
        if (res.ok) { const med = await res.json(); addToCart(med.id, med.name, med.price); showAlert("تمت الإضافة", `تم إضافة <b>${med.name}</b> للفاتورة.`, "success"); }
        else showAlert("غير موجود", `لا يوجد دواء بالباركود: ${barcode}`, "error");
    } catch (err) { console.error(err); }
}

// 9. Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').then(reg => console.log('SW Registered')));
}


// ==================== محرك المزامنة التلقائية ====================

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


// تشغيل المزامنة عند عودة الإنترنت
window.addEventListener('online', () => {
    showAlert("عاد الاتصال", "جاري مزامنة الفواتير المعلقة...", "success");
    processOutbox();
});

// محاولة المزامنة كل 30 ثانية في الخلفية
setInterval(processOutbox, 30000);
