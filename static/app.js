
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
const API_URL = "/api"; let cart = []; let html5QrCode = null; let purchaseCart = [];
function formatCurrency(num) { return Number(num).toLocaleString('en-US'); }
function getAuthHeaders() { const token = localStorage.getItem('kodnaqi_token'); return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }; }


async function apiFetch(url, options = {}) {
    const loader = document.getElementById('loading-overlay');
    if (loader) { loader.classList.remove('hidden'); loader.classList.add('flex'); }
    
    try {
        options.headers = { ...getAuthHeaders(), ...options.headers };
        const res = await fetch(url, options);
        if (res.status === 401 || res.status === 403) {
            if(res.status === 401) { localStorage.removeItem('kodnaqi_token'); localStorage.removeItem('kodnaqi_role'); window.location.reload(); }
            else { const data = await res.json(); showAlert("ممنوع", data.detail || "ليس لديك صلاحية", "error"); throw new Error("Forbidden"); }
        }
        return res;
    } finally {
        if (loader) { loader.classList.add('hidden'); loader.classList.remove('flex'); }
    }
}


let isLoginMode = true;
function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    const loginBox = document.getElementById('login-form-box'); const regBox = document.getElementById('register-form-box');
    const title = document.getElementById('auth-title'); const subtitle = document.getElementById('auth-subtitle'); const toggleBtn = document.getElementById('toggle-auth-btn');
    if (isLoginMode) { loginBox.classList.remove('hidden'); regBox.classList.add('hidden'); title.innerText = "مرحباً بك مجدداً"; subtitle.innerText = "سجل الدخول لإدارة صيدليتك"; toggleBtn.innerText = "ليس لديك حساب؟ إنشاء حساب جديد"; } 
    else { loginBox.classList.add('hidden'); regBox.classList.remove('hidden'); title.innerText = "حساب جديد"; subtitle.innerText = "أنشئ حسابك لإدارة صيدليتك"; toggleBtn.innerText = "لديك حساب بالفعل؟ تسجيل الدخول"; }
}

async function handleRegister() {
    const user = document.getElementById('reg-user').value; const pass = document.getElementById('reg-pass').value; const confirmPass = document.getElementById('reg-pass-confirm').value;
    if(!user || !pass) return showAlert("تنبيه", "أدخل البيانات", "error"); if(pass !== confirmPass) return showAlert("خطأ", "كلمتا المرور غير متطابقتين", "error");
    try {
        const res = await fetch(`${API_URL}/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: user, password: pass }) });
        const data = await res.json();
        if (res.ok) { await showAlert("تم بنجاح", "تم إنشاء الحساب، يمكنك الآن تسجيل الدخول.", "success"); toggleAuthMode(); document.getElementById('login-user').value = user; } 
        else { showAlert("خطأ", data.detail || "حدث خطأ", "error"); }
    } catch (err) { showAlert("خطأ", "تعذر الاتصال", "error"); }
}

window.addEventListener('load', () => { setTimeout(() => { const splash = document.getElementById('splash-screen'); if (splash) { splash.style.opacity = '0'; setTimeout(() => { splash.style.display = 'none'; if (localStorage.getItem('kodnaqi_token')) { showApp(); } else { const login = document.getElementById('login-screen'); if(login) { login.classList.remove('hidden'); login.classList.add('flex'); } } }, 500); } }, 2000); });

async function handleLogin() { 
    const user = document.getElementById('login-user').value; const pass = document.getElementById('login-pass').value; if(!user || !pass) return showAlert("تنبيه", "أدخل البيانات", "error"); 
    try { 
        const res = await fetch(`${API_URL}/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: user, password: pass }) }); 
        const data = await res.json(); 
        if (res.ok) { localStorage.setItem('kodnaqi_token', data.access_token); localStorage.setItem('kodnaqi_role', data.role); document.getElementById('login-screen').classList.add('hidden'); document.getElementById('login-screen').classList.remove('flex'); showApp(); } 
        else { showAlert("خطأ", data.detail || "بيانات غير صحيحة", "error"); } 
    } catch (err) { showAlert("خطأ", "تعذر الاتصال", "error"); } 
}

function handleLogout() { localStorage.removeItem('kodnaqi_token'); localStorage.removeItem('kodnaqi_role'); window.location.reload(); }


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


function showAlert(title, message, type = 'success') { return new Promise((resolve) => { const modal = document.getElementById('app-modal'); const content = document.getElementById('modal-content'); const iconDiv = document.getElementById('modal-icon'); const input = document.getElementById('modal-input'); const cancelBtn = document.getElementById('modal-cancel'); const confirmBtn = document.getElementById('modal-confirm'); if(!modal) return resolve(true); input.classList.add('hidden'); cancelBtn.classList.add('hidden'); confirmBtn.innerText = 'حسناً'; if (type === 'error') { iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4"; iconDiv.innerHTML = '<span class="text-3xl">❌</span>'; confirmBtn.className = "flex-1 bg-red-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-red-200"; } else { iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-4"; iconDiv.innerHTML = '<span class="text-3xl text-primary">✅</span>'; confirmBtn.className = "flex-1 bg-primary text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/30"; } document.getElementById('modal-title').innerText = title; document.getElementById('modal-message').innerHTML = message; modal.classList.remove('hidden'); modal.classList.add('flex'); setTimeout(() => content.classList.remove('scale-95'), 10); confirmBtn.onclick = () => { content.classList.add('scale-95'); setTimeout(() => { modal.classList.add('hidden'); modal.classList.remove('flex'); }, 200); resolve(true); }; }); }
function showPrompt(title, message, defaultValue) { return new Promise((resolve) => { const modal = document.getElementById('app-modal'); const content = document.getElementById('modal-content'); const iconDiv = document.getElementById('modal-icon'); const input = document.getElementById('modal-input'); const cancelBtn = document.getElementById('modal-cancel'); const confirmBtn = document.getElementById('modal-confirm'); if(!modal) return resolve(null); iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 mb-4"; iconDiv.innerHTML = '<span class="text-3xl">💵</span>'; confirmBtn.className = "flex-1 bg-primary text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/30"; confirmBtn.innerText = 'تأكيد الدفع'; document.getElementById('modal-title').innerText = title; document.getElementById('modal-message').innerText = message; input.classList.remove('hidden'); input.value = defaultValue; input.focus(); cancelBtn.classList.remove('hidden'); modal.classList.remove('hidden'); modal.classList.add('flex'); setTimeout(() => content.classList.remove('scale-95'), 10); confirmBtn.onclick = () => { const val = input.value; close(); resolve(val); }; cancelBtn.onclick = () => { close(); resolve(null); }; function close() { content.classList.add('scale-95'); setTimeout(() => { modal.classList.add('hidden'); modal.classList.remove('flex'); }, 200); } }); }

// Users
async function loadUsers() { try { const res = await apiFetch(`${API_URL}/users`); const users = await res.json(); const list = document.getElementById('users-list'); list.innerHTML = users.map(u => `<div class="flex justify-between items-center p-3 border-b border-gray-100"><div><p class="font-bold text-primary">${u.username}</p><p class="text-xs text-gray-500">${u.role === 'admin' ? 'مدير' : 'كاشير'}</p></div>${u.username !== 'admin' ? `<button onclick="deleteUser(${u.id})" class="bg-red-50 text-red-600 p-2 rounded-lg">🗑️</button>` : ''}</div>`).join(''); } catch (err) { console.error(err); } }
document.getElementById('add-user-form')?.addEventListener('submit', async (e) => { e.preventDefault(); const username = document.getElementById('new-username').value; const password = document.getElementById('new-password').value; const role = document.getElementById('new-role').value; try { const res = await apiFetch(`${API_URL}/users`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password, role }) }); if(res.ok) { await showAlert("تم", "تم إضافة الموظف.", "success"); document.getElementById('add-user-form').reset(); loadUsers(); } } catch (err) {} });
async function deleteUser(id) { if(!confirm("حذف هذا الموظف؟")) return; try { const res = await apiFetch(`${API_URL}/users/${id}`, { method: 'DELETE' }); if(res.ok) { loadUsers(); showAlert("تم", "تم الحذف.", "success"); } } catch (err) {} }

// Settings & Dashboard & Z-Report
async function loadSettings() { try { const res = await apiFetch(`${API_URL}/settings`); const data = await res.json(); const nameEl = document.getElementById('pharmacy-name'); if(nameEl) nameEl.innerText = data.pharmacy_name; await localforage.setItem('kodnaqi_settings', data); } catch (err) { const localData = await localforage.getItem('kodnaqi_settings'); if(localData) { document.getElementById('pharmacy-name').innerText = localData.pharmacy_name; } } }
async function fetchSettingsForForm() { try { const res = await apiFetch(`${API_URL}/settings`); const data = await res.json(); if(document.getElementById('set-name')) document.getElementById('set-name').value = data.pharmacy_name; if(document.getElementById('set-currency')) document.getElementById('set-currency').value = data.currency; } catch (err) { console.error(err); } }
document.getElementById('settings-form')?.addEventListener('submit', async (e) => { e.preventDefault(); try { const res = await apiFetch(`${API_URL}/settings`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pharmacy_name: document.getElementById('set-name').value, currency: document.getElementById('set-currency').value }) }); if (res.ok) { await showAlert("تم بنجاح", "تم التحديث.", "success"); loadSettings(); } } catch (err) { showAlert("خطأ", "تعذر التحديث", "error"); } });
document.getElementById('change-password-form')?.addEventListener('submit', async (e) => { e.preventDefault(); const oldPass = document.getElementById('old-password').value; const newPass = document.getElementById('new-password').value; try { const res = await apiFetch(`${API_URL}/users/me/password`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ old_password: oldPass, new_password: newPass }) }); const data = await res.json(); if (res.ok) { await showAlert("تم بنجاح", "تم تغيير كلمة المرور.", "success"); document.getElementById('change-password-form').reset(); } else { showAlert("خطأ", data.detail || "حدث خطأ", "error"); } } catch (err) { showAlert("خطأ", "تعذر الاتصال", "error"); } });

async function loadDashboard() { 
    try { 
        const res = await apiFetch(`${API_URL}/stats`); 
        const data = await res.json(); 
        document.getElementById('stat-revenue').innerText = `${formatCurrency(data.today_revenue)} SDG`; 
        document.getElementById('stat-count').innerText = `${data.today_sales_count} فاتورة`; 
        document.getElementById('stat-profit').innerText = `${formatCurrency(data.today_profit)} SDG`; 

        // 1. منتهية الصلاحية
        const expContainer = document.getElementById('expired-container');
        const expList = document.getElementById('expired-list');
        if (data.expired_alerts.length > 0) {
            expContainer.classList.remove('hidden');
            expList.innerHTML = data.expired_alerts.map(item => `<div class="flex justify-between p-2 bg-red-50 rounded-lg"><span class="font-bold text-gray-800">${item.name}</span><span class="text-red-600 font-bold text-xs">${item.expiry_date}</span></div>`).join('');
        } else { expContainer.classList.add('hidden'); }

        // 2. أوشكت على الانتهاء
        const exsoonContainer = document.getElementById('expiring-container');
        const exsoonList = document.getElementById('expiring-list');
        if (data.expiring_soon_alerts.length > 0) {
            exsoonContainer.classList.remove('hidden');
            exsoonList.innerHTML = data.expiring_soon_alerts.map(item => `<div class="flex justify-between p-2 bg-orange-50 rounded-lg"><span class="font-bold text-gray-800">${item.name}</span><span class="text-orange-600 font-bold text-xs">${item.expiry_date}</span></div>`).join('');
        } else { exsoonContainer.classList.add('hidden'); }

        // 3. نقص المخزون
        const lowContainer = document.getElementById('lowstock-container');
        const lowList = document.getElementById('lowstock-list');
        if (data.low_stock_alerts.length > 0) {
            lowContainer.classList.remove('hidden');
            lowList.innerHTML = data.low_stock_alerts.map(item => `<div class="flex justify-between p-2 bg-yellow-50 rounded-lg"><span class="font-bold text-gray-800">${item.name}</span><span class="text-yellow-700 font-bold text-xs">متبقي: ${item.stock_quantity}</span></div>`).join('');
        } else { lowContainer.classList.add('hidden'); }

    } catch (err) { console.log("Offline Dashboard"); } 
}


// Suppliers & Medicines
async function loadSuppliersList() { try { const res = await apiFetch(`${API_URL}/suppliers`); const suppliers = await res.json(); const list = document.getElementById('suppliers-list'); if(suppliers.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center">لا يوجد موردين.</p>'; return; } list.innerHTML = suppliers.map(s => `<div class="flex justify-between items-center p-3 border-b border-gray-100"><div><p class="font-bold text-primary">${s.name}</p><p class="text-xs text-gray-500">${s.phone || 'لا يوجد هاتف'}</p></div></div>`).join(''); } catch (err) { console.error(err); } }
async function loadSuppliersForDropdown() { try { const res = await apiFetch(`${API_URL}/suppliers`); const suppliers = await res.json(); const select = document.getElementById('med-supplier'); const purSelect = document.getElementById('pur-supplier'); if(!select || !purSelect) return; const html = '<option value="">اختر المورد...</option>' + suppliers.map(s => `<option value="${s.id}">${s.name}</option>`).join(''); select.innerHTML = html; purSelect.innerHTML = html; } catch (err) { console.error(err); } }
document.getElementById('add-supplier-form')?.addEventListener('submit', async (e) => { e.preventDefault(); const name = document.getElementById('sup-name').value; const phone = document.getElementById('sup-phone').value; try { const res = await apiFetch(`${API_URL}/suppliers`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, phone }) }); if(res.ok) { await showAlert("تم بنجاح", "تم إضافة المورد.", "success"); document.getElementById('add-supplier-form').reset(); loadSuppliersList(); loadSuppliersForDropdown(); } } catch (err) { showAlert("خطأ", "تعذر الاتصال", "error"); } });

async function loadMedicines() { try { const res = await apiFetch(`${API_URL}/medicines`); const medicines = await res.json(); const posList = document.getElementById('medicines-list'); if(posList) { posList.innerHTML = medicines.map(med => `<div onclick="addToCart(${med.id}, '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl"><div><p class="font-bold text-gray-800 text-sm">${med.name}</p></div><div class="text-left"><p class="font-bold text-primary">${formatCurrency(med.price)} SDG</p><p class="text-[10px] text-gray-400">المخزون: ${med.stock_quantity}</p></div></div>`).join(''); } const invList = document.getElementById('inventory-list'); if(invList) { invList.innerHTML = medicines.map(med => `<div class="flex justify-between items-center p-3 border-b border-gray-100"><div><p class="font-bold text-gray-800 text-sm">${med.name}</p><p class="text-[10px] text-gray-500">${med.category || ''} | ${med.supplier_name || 'بدون مورد'}</p></div><div class="text-left flex items-center gap-3"><div><p class="font-bold text-primary text-sm">${med.price} SDG</p><p class="text-[10px] ${med.stock_quantity <= 10 ? 'text-red-500 font-bold' : 'text-gray-400'}">المخزون: ${med.stock_quantity}</p></div><button onclick='editMedicine(${JSON.stringify(med)})' class="bg-blue-50 text-blue-600 p-2 rounded-lg">✏️</button><button onclick="deleteMedicine(${med.id})" class="bg-red-50 text-red-600 p-2 rounded-lg">🗑️</button></div></div>`).join(''); } await localforage.setItem('kodnaqi_medicines', medicines); } catch (err) { const meds = await localforage.getItem('kodnaqi_medicines') || []; const posList = document.getElementById('medicines-list'); if(posList && meds.length) { posList.innerHTML = meds.map(med => `<div onclick="addToCart(${med.id}, '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl"><div><p class="font-bold text-gray-800 text-sm">${med.name}</p></div><div class="text-left"><p class="font-bold text-primary">${formatCurrency(med.price)} SDG</p><p class="text-[10px] text-gray-400">المخزون: ${med.stock_quantity}</p></div></div>`).join(''); } } }
document.getElementById('add-medicine-form')?.addEventListener('submit', async (e) => { e.preventDefault(); const id = document.getElementById('med-id').value; const data = { name: document.getElementById('med-name').value, scientific_name: document.getElementById('med-scientific').value || null, category: document.getElementById('med-category').value || null, supplier_id: document.getElementById('med-supplier').value ? parseInt(document.getElementById('med-supplier').value) : null, price: parseFloat(document.getElementById('med-price').value), cost: parseFloat(document.getElementById('med-cost').value) || 0, stock_quantity: parseInt(document.getElementById('med-stock').value), barcode: document.getElementById('med-barcode').value || null, expiry_date: document.getElementById('med-expiry').value || null }; const method = id ? 'PUT' : 'POST'; const url = id ? `${API_URL}/medicines/${id}` : `${API_URL}/medicines`; try { const res = await apiFetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }); if (res.ok) { await showAlert("تم بنجاح", id ? "تم التعديل." : "تم الإضافة.", "success"); resetInvForm(); loadMedicines(); } else showAlert("خطأ", "تأكد من أن الباركود غير مكرر.", "error"); } catch (err) { showAlert("خطأ", "تعذر الاتصال", "error"); } });
function editMedicine(med) { document.getElementById('med-id').value = med.id; document.getElementById('med-name').value = med.name; document.getElementById('med-scientific').value = med.scientific_name || ''; document.getElementById('med-category').value = med.category || ''; document.getElementById('med-supplier').value = med.supplier_id || ''; document.getElementById('med-price').value = med.price; document.getElementById('med-cost').value = med.cost || ''; document.getElementById('med-stock').value = med.stock_quantity; document.getElementById('med-barcode').value = med.barcode || ''; document.getElementById('med-expiry').value = med.expiry_date || ''; document.getElementById('inv-form-title').innerText = "تعديل دواء"; document.getElementById('cancel-edit-btn').classList.remove('hidden'); window.scrollTo(0,0); }
function resetInvForm() { document.getElementById('add-medicine-form').reset(); document.getElementById('med-id').value = ''; document.getElementById('inv-form-title').innerText = "إضافة دواء جديد"; document.getElementById('cancel-edit-btn').classList.add('hidden'); }
async function deleteMedicine(id) { if(!confirm("هل أنت متأكد من حذف هذا الدواء؟")) return; try { const res = await apiFetch(`${API_URL}/medicines/${id}`, { method: 'DELETE' }); if(res.ok) { loadMedicines(); showAlert("تم", "تم حذف الدواء.", "success"); } } catch (err) { console.error(err); } }
function filterMedicines() { const query = document.getElementById('pos-search').value.toLowerCase(); const items = document.querySelectorAll('#medicines-list > div'); items.forEach(item => { item.style.display = item.innerText.toLowerCase().includes(query) ? 'flex' : 'none'; }); }
function filterInventory() { const query = document.getElementById('inv-search').value.toLowerCase(); const items = document.querySelectorAll('#inventory-list > div'); items.forEach(item => { item.style.display = item.innerText.toLowerCase().includes(query) ? 'flex' : 'none'; }); }

// Purchases
async function loadPurchasesData() {
    await loadSuppliersForDropdown();
    const res = await apiFetch(`${API_URL}/medicines`);
    const meds = await res.json();
    const select = document.getElementById('pur-medicine');
    select.innerHTML = '<option value="">اختر الدواء...</option>' + meds.map(m => `<option value="${m.id}" data-cost="${m.cost}">${m.name}</option>`).join('');
    renderPurchaseCart();
}
function addToPurchaseCart() {
    const medId = document.getElementById('pur-medicine').value;
    const qty = parseInt(document.getElementById('pur-qty').value);
    const cost = parseFloat(document.getElementById('pur-cost').value);
    if(!medId || !qty || !cost) return showAlert("تنبيه", "اختر الدواء وأدخل الكمية والتكلفة", "error");
    
    const select = document.getElementById('pur-medicine');
    const medName = select.options[select.selectedIndex].text;
    
    const existing = purchaseCart.find(i => i.medicine_id == medId);
    if(existing) { existing.quantity += qty; existing.unit_cost = cost; }
    else { purchaseCart.push({ medicine_id: parseInt(medId), name: medName, quantity: qty, unit_cost: cost }); }
    
    document.getElementById('pur-qty').value = ''; document.getElementById('pur-cost').value = '';
    renderPurchaseCart();
}
function renderPurchaseCart() {
    const div = document.getElementById('purchase-cart');
    if(purchaseCart.length === 0) { div.innerHTML = '<p class="text-gray-400 text-sm text-center">لم تتم إضافة أصناف.</p>'; return; }
    div.innerHTML = purchaseCart.map((item, i) => `<div class="flex justify-between items-center p-3 bg-bg rounded-xl mb-2"><div><p class="font-bold text-sm text-primary">${item.name}</p><p class="text-xs text-gray-500">الكمية: ${item.quantity} | التكلفة: ${item.unit_cost}</p></div><button onclick="purchaseCart.splice(${i},1); renderPurchaseCart()" class="text-red-500 bg-red-50 p-2 rounded-lg">✖</button></div>`).join('');
}
async function savePurchase() {
    const supplierId = document.getElementById('pur-supplier').value;
    if(!supplierId) return showAlert("تنبيه", "اختر المورد أولاً", "error");
    if(purchaseCart.length === 0) return showAlert("تنبيه", "أضف أصنافاً للفاتورة", "error");
    
    try {
        const res = await apiFetch(`${API_URL}/purchases`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ supplier_id: parseInt(supplierId), items: purchaseCart }) });
        if(res.ok) {
            await showAlert("تم بنجاح", "تم حفظ فاتورة الشراء وتحديث المخزون.", "success");
            purchaseCart = []; renderPurchaseCart(); loadMedicines(); loadPurchasesData();
        } else showAlert("خطأ", "تعذر الحفظ", "error");
    } catch (err) { showAlert("خطأ", "تعذر الاتصال", "error"); }
}

// POS & Cart
function addToCart(id, name, price) { const existing = cart.find(item => item.medicine_id === id); if (existing) existing.quantity += 1; else cart.push({ medicine_id: id, name: name, unit_price: price, quantity: 1 }); renderCart(); }
function removeFromCart(index) { cart.splice(index, 1); renderCart(); }
function updateQuantity(index, change) { cart[index].quantity += change; if (cart[index].quantity <= 0) cart.splice(index, 1); renderCart(); }
function renderCart() { const cartDiv = document.getElementById('cart-items'); const totalEl = document.getElementById('cart-total'); if (!cartDiv || !totalEl) return; if (cart.length === 0) { cartDiv.innerHTML = '<p class="text-gray-400 text-sm text-center py-4">الفاتورة فارغة.</p>'; totalEl.innerText = `0 SDG`; return; } let total = 0; cartDiv.innerHTML = cart.map((item, index) => { total += item.unit_price * item.quantity; return `<div class="flex justify-between items-center p-3 bg-bg rounded-xl mb-2"><div class="flex-1"><p class="font-bold text-sm text-primary">${item.name}</p><p class="text-xs text-gray-500">${item.unit_price} SDG</p></div><div class="flex items-center gap-3"><div class="flex items-center bg-white rounded-lg border border-gray-100"><button onclick="updateQuantity(${index}, 1)" class="px-3 py-1 text-primary font-bold">+</button><span class="px-2 font-bold text-sm">${item.quantity}</span><button onclick="updateQuantity(${index}, -1)" class="px-3 py-1 text-red-500 font-bold">-</button></div><span class="font-bold text-primary w-20 text-left">${formatCurrency(item.unit_price * item.quantity)} SDG</span><button onclick="removeFromCart(${index})" class="text-red-500 bg-red-50 p-2 rounded-lg">✖</button></div></div>`; }).join(''); totalEl.innerText = `${formatCurrency(total)} SDG`; }
async function checkout() { if (cart.length === 0) return showAlert("تنبيه", "الفاتورة فارغة.", "error"); let total = cart.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0); const paid = await showPrompt("الدفع", `الإجمالي المطلوب: ${formatCurrency(total)} SDG`, total); if (paid === null || paid === "") return; const paidAmount = parseFloat(paid); if (isNaN(paidAmount) || paidAmount < total) return showAlert("خطأ", "المبلغ غير كافٍ!", "error"); const localId = Date.now(); const saleData = { id: localId, discount: 0, paid_amount: paidAmount, items: cart.map(i => ({ medicine_id: i.medicine_id, quantity: i.quantity, unit_price: i.unit_price })), invoice_number: `OFF-${localId.toString().slice(-6)}`, sale_date: new Date().toISOString() }; let sales = await localforage.getItem('kodnaqi_sales') || []; sales.unshift(saleData); await localforage.setItem('kodnaqi_sales', sales); let outbox = await localforage.getItem('kodnaqi_outbox') || []; outbox.push(saleData); await localforage.setItem('kodnaqi_outbox', outbox); const change = paidAmount - total; preparePrintInvoice(saleData.invoice_number, cart, total, paidAmount, change); let msg = `رقم الفاتورة: <b>${saleData.invoice_number}</b><br>الباقي: <b class="text-primary text-lg">${formatCurrency(change)} SDG</b>`; msg += `<br><br><button onclick="window.print()" class="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-bold w-full">🖨️ طباعة الفاتورة</button>`; await showAlert("تمت العملية", msg, "success"); cart = []; renderCart(); loadMedicines(); processOutbox(); }

// Sync & History

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

