// ============================================================
// KodNaqi Pharmacy - Complete Fixed app.js
// ============================================================

// --- Config ---
const API_URL = window.location.origin + "/api";

// --- Global State ---
let cart = [];
let purchaseCart = [];
let html5QrCode = null;
let currentUser = {
    username: localStorage.getItem('kodnaqi_user') || null,
    role: localStorage.getItem('kodnaqi_role') || 'cashier'
};

function isAdmin() {
    return currentUser.role === 'admin';
}

// --- Web Audio API for Vault Sound ---
const AudioContextClass = window.AudioContext || window.webkitAudioContext;
const audioCtx = new AudioContextClass();

function playVaultSound(type) {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    const now = audioCtx.currentTime;

    if (type === 'tick') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(1600, now);
        osc.frequency.exponentialRampToValueAtTime(220, now + 0.02);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.02);
        osc.connect(gain); gain.connect(audioCtx.destination);
        osc.start(now); osc.stop(now + 0.02);
    } else if (type === 'lock') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(520, now);
        osc.frequency.exponentialRampToValueAtTime(75, now + 0.08);
        gain.gain.setValueAtTime(0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
        osc.connect(gain); gain.connect(audioCtx.destination);
        osc.start(now); osc.stop(now + 0.08);
    }
}

// --- Helpers ---
function formatCurrency(num) {
    if (num === null || num === undefined || isNaN(num)) return "0";
    return Number(num).toLocaleString('en-US');
}

async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('kodnaqi_token');
    const headers = { ...(options.headers || {}) };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // لا نضيف Content-Type إذا كان body من نوع FormData
    if (!(options.body instanceof FormData) && !headers['Content-Type'] && options.body) {
        headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(url, { ...options, headers });

    if (res.status === 401) {
        localStorage.removeItem('kodnaqi_token');
        showLoginScreen();
        throw new Error("Unauthorized");
    }
    return res;
}

// ============================================================
// AUTH
// ============================================================
function showLoginScreen() {
    const splash = document.getElementById('splash-screen');
    if (splash) {
        splash.style.opacity = '0';
        setTimeout(() => splash.classList.add('hidden'), 400);
    }
    document.getElementById('app-content')?.classList.add('hidden');
    const login = document.getElementById('login-screen');
    if (login) {
        login.classList.remove('hidden');
        login.classList.add('flex');
    }
}

function showApp() {
    const splash = document.getElementById('splash-screen');
    if (splash) {
        splash.style.opacity = '0';
        setTimeout(() => splash.classList.add('hidden'), 400);
    }
    document.getElementById('login-screen')?.classList.add('hidden');
    document.getElementById('login-screen')?.classList.remove('flex');
    document.getElementById('app-content')?.classList.remove('hidden');
    applyRoleUI();
    switchTab('dashboard');
    loadSettings();
}

function applyRoleUI() {
    // إخفاء عناصر المدير عن الكاشير
    const adminOnlyButtons = ['btn-users'];
    adminOnlyButtons.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        if (isAdmin()) {
            el.classList.remove('hidden');
            el.style.display = '';
        } else {
            el.classList.add('hidden');
            el.style.display = 'none';
        }
    });

    // إخفاء أزرار النسخ الاحتياطي عن الكاشير إن وجدت
    document.querySelectorAll('[onclick*="downloadBackup"]').forEach(btn => {
        if (!isAdmin()) {
            btn.style.display = 'none';
        } else {
            btn.style.display = '';
        }
    });
}

function toggleAuthMode() {
    const loginBox = document.getElementById('login-form-box');
    const regBox = document.getElementById('register-form-box');
    const btn = document.getElementById('toggle-auth-btn');
    const title = document.getElementById('auth-title');
    const subtitle = document.getElementById('auth-subtitle');

    if (!loginBox || !regBox) return;

    if (loginBox.classList.contains('hidden')) {
        // العودة لوضع تسجيل الدخول
        loginBox.classList.remove('hidden');
        regBox.classList.add('hidden');
        if (btn) btn.innerText = "ليس لديك حساب؟ إنشاء حساب جديد";
        if (title) title.innerText = "مرحباً بك مجدداً";
        if (subtitle) subtitle.innerText = "سجل الدخول لإدارة صيدليتك";
    } else {
        // وضع التسجيل
        loginBox.classList.add('hidden');
        regBox.classList.remove('hidden');
        if (btn) btn.innerText = "لديك حساب بالفعل؟ تسجيل الدخول";
        if (title) title.innerText = "إنشاء حساب جديد";
        if (subtitle) subtitle.innerText = "أنشئ حساباً لبدء استخدام النظام";
    }
}

async function handleLogin() {
    const username = document.getElementById('login-user')?.value.trim();
    const password = document.getElementById('login-pass')?.value;

    if (!username || !password) {
        return showAlert("تنبيه", "أدخل اسم المستخدم وكلمة المرور", "error");
    }

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json().catch(() => ({}));
        if (res.ok) {
            localStorage.setItem('kodnaqi_token', data.access_token || data.token);
            localStorage.setItem('kodnaqi_role', data.role || 'cashier');
            localStorage.setItem('kodnaqi_user', username);
            currentUser = { username, role: data.role || 'cashier' };
            playVaultSound('lock');
            showApp();
        } else {
            showAlert("خطأ", data.detail || "اسم المستخدم أو كلمة المرور غير صحيحة", "error");
        }
    } catch (err) {
        console.error(err);
        showAlert("خطأ", "تعذر الاتصال بالخادم", "error");
    }
}

async function handleRegister() {
    const username = document.getElementById('reg-user')?.value.trim();
    const password = document.getElementById('reg-pass')?.value;
    const confirm = document.getElementById('reg-pass-confirm')?.value;

    if (!username || !password) return showAlert("تنبيه", "أكمل البيانات", "error");
    if (password !== confirm) return showAlert("خطأ", "كلمتا المرور غير متطابقتين", "error");

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json().catch(() => ({}));
        if (res.ok) {
            await showAlert("تم", "تم إنشاء الحساب بنجاح، يمكنك تسجيل الدخول الآن");
            toggleAuthMode();
        } else {
            showAlert("خطأ", data.detail || "حدث خطأ أثناء التسجيل", "error");
        }
    } catch (err) {
        showAlert("خطأ", "تعذر الاتصال بالخادم", "error");
    }
}

function handleLogout() {
    localStorage.removeItem('kodnaqi_token');
    localStorage.removeItem('kodnaqi_role');
    localStorage.removeItem('kodnaqi_user');
    currentUser = { username: null, role: 'cashier' };
    cart = [];
    purchaseCart = [];
    showLoginScreen();
}

// ============================================================
// UI Helpers (Modal)
// ============================================================
function showAlert(title, message, type = 'success') {
    return new Promise((resolve) => {
        const modal = document.getElementById('app-modal');
        const content = document.getElementById('modal-content');
        const iconDiv = document.getElementById('modal-icon');
        const input = document.getElementById('modal-input');
        const cancelBtn = document.getElementById('modal-cancel');
        const confirmBtn = document.getElementById('modal-confirm');

        if (!modal) {
            alert(title + "\n" + message.replace(/<[^>]+>/g, ''));
            return resolve(true);
        }

        input?.classList.add('hidden');
        cancelBtn?.classList.add('hidden');
        if (confirmBtn) confirmBtn.innerText = 'حسناً';

        if (type === 'error') {
            if (iconDiv) {
                iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4";
                iconDiv.innerHTML = '<span class="text-3xl">❌</span>';
            }
            if (confirmBtn) confirmBtn.className = "flex-1 bg-red-600 text-white py-3 rounded-xl font-bold shadow-lg shadow-red-200";
        } else {
            if (iconDiv) {
                iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-4";
                iconDiv.innerHTML = '<span class="text-3xl text-primary">✅</span>';
            }
            if (confirmBtn) confirmBtn.className = "flex-1 bg-primary text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/30";
        }

        const titleEl = document.getElementById('modal-title');
        const msgEl = document.getElementById('modal-message');
        if (titleEl) titleEl.innerText = title;
        if (msgEl) msgEl.innerHTML = message;

        modal.classList.remove('hidden');
        modal.classList.add('flex');
        setTimeout(() => content?.classList.remove('scale-95'), 10);

        if (confirmBtn) {
            confirmBtn.onclick = () => {
                content?.classList.add('scale-95');
                setTimeout(() => {
                    modal.classList.add('hidden');
                    modal.classList.remove('flex');
                }, 200);
                resolve(true);
            };
        }
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

        if (!modal || !input) {
            const val = prompt(message, defaultValue);
            return resolve(val);
        }

        if (iconDiv) {
            iconDiv.className = "mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 mb-4";
            iconDiv.innerHTML = '<span class="text-3xl">💵</span>';
        }
        if (confirmBtn) {
            confirmBtn.className = "flex-1 bg-primary text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/30";
            confirmBtn.innerText = 'تأكيد الدفع';
        }

        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-message').innerText = message;
        input.classList.remove('hidden');
        input.value = defaultValue ?? '';
        input.focus();
        cancelBtn?.classList.remove('hidden');

        modal.classList.remove('hidden');
        modal.classList.add('flex');
        setTimeout(() => content?.classList.remove('scale-95'), 10);

        function close() {
            content?.classList.add('scale-95');
            setTimeout(() => {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            }, 200);
        }

        if (confirmBtn) {
            confirmBtn.onclick = () => {
                const val = input.value;
                close();
                resolve(val);
            };
        }
        if (cancelBtn) {
            cancelBtn.onclick = () => {
                close();
                resolve(null);
            };
        }
    });
}

// ============================================================
// Tabs
// ============================================================
function switchTab(tabId) {
    ['dashboard', 'pos', 'inventory', 'history', 'purchases', 'suppliers', 'users', 'settings'].forEach(id => {
        const view = document.getElementById(`view-${id}`);
        const btn = document.getElementById(`btn-${id}`);
        if (view) view.classList.add('hidden');
        if (btn) btn.className = "flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all";
    });

    const activeView = document.getElementById(`view-${tabId}`);
    const activeBtn = document.getElementById(`btn-${tabId}`);

    if (activeView) activeView.classList.remove('hidden');
    if (activeBtn) activeBtn.className = "flex flex-col items-center p-2 text-primary min-w-[70px] transition-all";

    const titles = {
        dashboard: 'الرئيسية',
        pos: 'الكاشير',
        inventory: 'المخزون',
        history: 'السجلات',
        purchases: 'المشتريات',
        suppliers: 'الموردين',
        users: 'الموظفين',
        settings: 'الإعدادات'
    };
    const titleEl = document.getElementById('current-tab-title');
    if (titleEl) titleEl.innerText = titles[tabId] || '';

    if (tabId === 'dashboard') loadDashboard();
    if (tabId === 'inventory') { loadMedicines(); loadSuppliersForDropdown(); }
    if (tabId === 'history') loadHistory();
    if (tabId === 'purchases') loadPurchasesData();
    if (tabId === 'suppliers') loadSuppliersList();
    if (tabId === 'users') loadUsers();
    if (tabId === 'settings') fetchSettingsForForm();
    if (tabId === 'pos') loadMedicines();
}

// ============================================================
// Settings & Dashboard
// ============================================================
async function loadSettings() {
    try {
        const res = await apiFetch(`${API_URL}/settings`);
        const data = await res.json();
        const nameEl = document.getElementById('pharmacy-name');
        if (nameEl) nameEl.innerText = data.pharmacy_name || 'KodNaqi Pharmacy';
        await localforage.setItem('kodnaqi_settings', data);
    } catch (err) {
        const localData = await localforage.getItem('kodnaqi_settings');
        if (localData) {
            const nameEl = document.getElementById('pharmacy-name');
            if (nameEl) nameEl.innerText = localData.pharmacy_name || 'KodNaqi Pharmacy';
        }
    }
}

async function fetchSettingsForForm() {
    try {
        const res = await apiFetch(`${API_URL}/settings`);
        const data = await res.json();
        if (document.getElementById('set-name')) document.getElementById('set-name').value = data.pharmacy_name || '';
        if (document.getElementById('set-currency')) document.getElementById('set-currency').value = data.currency || 'SDG';
    } catch (err) {
        console.error(err);
    }
}

document.getElementById('settings-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const res = await apiFetch(`${API_URL}/settings`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pharmacy_name: document.getElementById('set-name').value,
                currency: document.getElementById('set-currency').value
            })
        });
        if (res.ok) {
            await showAlert("تم بنجاح", "تم التحديث.", "success");
            loadSettings();
        }
    } catch (err) {
        showAlert("خطأ", "تعذر التحديث", "error");
    }
});

document.getElementById('change-password-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const oldPass = document.getElementById('old-password')?.value;
    const newPass = document.getElementById('new-password')?.value;
    try {
        const res = await apiFetch(`${API_URL}/users/me/password`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ old_password: oldPass, new_password: newPass })
        });
        const data = await res.json().catch(() => ({}));
        if (res.ok) {
            await showAlert("تم بنجاح", "تم تغيير كلمة المرور.", "success");
            document.getElementById('change-password-form')?.reset();
        } else {
            showAlert("خطأ", data.detail || "حدث خطأ", "error");
        }
    } catch (err) {
        showAlert("خطأ", "تعذر الاتصال", "error");
    }
});

async function loadDashboard() {
    const revEl = document.getElementById('stat-revenue');
    const countEl = document.getElementById('stat-count');
    const profitEl = document.getElementById('stat-profit');

    // محاولة جلب الإحصائيات (للمدير)
    try {
        const res = await apiFetch(`${API_URL}/stats`);
        if (res.ok) {
            const data = await res.json();
            if (revEl) revEl.innerText = `${formatCurrency(data.today_revenue || 0)} SDG`;
            if (countEl) countEl.innerText = `${data.today_sales_count || 0} فاتورة`;
            if (profitEl) profitEl.innerText = `${formatCurrency(data.today_profit || 0)} SDG`;

            renderAlerts(data);
            return;
        }
    } catch (err) {}

    // للكاشير أو عند فشل stats: حساب مبسط من المبيعات
    try {
        const res = await apiFetch(`${API_URL}/sales`);
        const sales = res.ok ? await res.json() : [];
        const today = new Date().toISOString().slice(0, 10);
        const todaySales = (sales || []).filter(s => (s.sale_date || '').startsWith(today));
        const revenue = todaySales.reduce((sum, s) => sum + (s.total_amount || s.paid_amount || 0), 0);

        if (revEl) revEl.innerText = `${formatCurrency(revenue)} SDG`;
        if (countEl) countEl.innerText = `${todaySales.length} فاتورة`;
        if (profitEl) profitEl.innerText = isAdmin() ? `${formatCurrency(0)} SDG` : '—';

        // إخفاء تنبيهات المدير عن الكاشير إن لم تتوفر
        ['expired-container', 'expiring-container', 'lowstock-container'].forEach(id => {
            document.getElementById(id)?.classList.add('hidden');
        });
    } catch (err) {
        if (revEl) revEl.innerText = '0 SDG';
        if (countEl) countEl.innerText = '0 فاتورة';
        if (profitEl) profitEl.innerText = '0 SDG';
    }
}

function renderAlerts(data) {
    // منتهية الصلاحية
    const expContainer = document.getElementById('expired-container');
    const expList = document.getElementById('expired-list');
    if (expContainer && expList) {
        if (data.expired_alerts && data.expired_alerts.length > 0) {
            expContainer.classList.remove('hidden');
            expList.innerHTML = data.expired_alerts.map(item =>
                `<div class="flex justify-between text-sm py-1"><span>${item.name}</span><span class="text-red-600 font-bold">${item.expiry_date}</span></div>`
            ).join('');
        } else {
            expContainer.classList.add('hidden');
        }
    }

    // أوشكت على الانتهاء
    const exsoonContainer = document.getElementById('expiring-container');
    const exsoonList = document.getElementById('expiring-list');
    if (exsoonContainer && exsoonList) {
        if (data.expiring_soon_alerts && data.expiring_soon_alerts.length > 0) {
            exsoonContainer.classList.remove('hidden');
            exsoonList.innerHTML = data.expiring_soon_alerts.map(item =>
                `<div class="flex justify-between text-sm py-1"><span>${item.name}</span><span class="text-orange-600 font-bold">${item.expiry_date}</span></div>`
            ).join('');
        } else {
            exsoonContainer.classList.add('hidden');
        }
    }

    // نقص المخزون
    const lowContainer = document.getElementById('lowstock-container');
    const lowList = document.getElementById('lowstock-list');
    if (lowContainer && lowList) {
        if (data.low_stock_alerts && data.low_stock_alerts.length > 0) {
            lowContainer.classList.remove('hidden');
            lowList.innerHTML = data.low_stock_alerts.map(item =>
                `<div class="flex justify-between text-sm py-1"><span>${item.name}</span><span class="text-yellow-700 font-bold">متبقي: ${item.stock_quantity}</span></div>`
            ).join('');
        } else {
            lowContainer.classList.add('hidden');
        }
    }
}

// ============================================================
// Users
// ============================================================
async function loadUsers() {
    const list = document.getElementById('users-list');
    if (!list) return;

    if (!isAdmin()) {
        list.innerHTML = '<p class="text-gray-400 text-center py-6">هذه الصفحة متاحة للمدير فقط</p>';
        return;
    }

    try {
        const res = await apiFetch(`${API_URL}/users`);
        if (!res.ok) {
            list.innerHTML = '<p class="text-gray-400 text-center py-6">تعذر تحميل الموظفين</p>';
            return;
        }
        const users = await res.json();

        if (!users || users.length === 0) {
            list.innerHTML = '<p class="text-gray-400 text-center py-6">لا يوجد موظفون بعد</p>';
            return;
        }

        list.innerHTML = users.map(u => `
            <div class="flex justify-between items-center p-3 border-b border-gray-100">
                <div>
                    <p class="font-bold text-primary">${u.username}</p>
                    <p class="text-xs text-gray-500">${u.role === 'admin' ? 'مدير' : 'كاشير'}</p>
                </div>
                ${u.username !== 'admin' ? `<button onclick="deleteUser(${u.id})" class="bg-red-50 text-red-600 p-2 rounded-lg">🗑️</button>` : ''}
            </div>
        `).join('');
    } catch (err) {
        list.innerHTML = '<p class="text-gray-400 text-center py-6">تعذر تحميل الموظفين</p>';
    }
}

document.getElementById('add-user-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('new-username')?.value;
    const password = document.getElementById('new-password')?.value;
    const role = document.getElementById('new-role')?.value || 'cashier';

    try {
        const res = await apiFetch(`${API_URL}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role })
        });
        if (res.ok) {
            await showAlert("تم", "تم إضافة الموظف.", "success");
            document.getElementById('add-user-form')?.reset();
            loadUsers();
        } else {
            const data = await res.json().catch(() => ({}));
            showAlert("خطأ", data.detail || "تعذر الإضافة", "error");
        }
    } catch (err) {
        showAlert("خطأ", "تعذر الاتصال", "error");
    }
});

async function deleteUser(id) {
    if (!confirm("حذف هذا الموظف؟")) return;
    try {
        const res = await apiFetch(`${API_URL}/users/${id}`, { method: 'DELETE' });
        if (res.ok) {
            loadUsers();
            showAlert("تم", "تم الحذف.", "success");
        }
    } catch (err) {
        console.error(err);
    }
}

// ============================================================
// Suppliers
// ============================================================
async function loadSuppliersList() {
    try {
        const res = await apiFetch(`${API_URL}/suppliers`);
        const suppliers = await res.json();
        const list = document.getElementById('suppliers-list');
        if (!list) return;

        if (!suppliers || suppliers.length === 0) {
            list.innerHTML = '<p class="text-gray-500 text-center py-4">لا يوجد موردين.</p>';
            return;
        }
        list.innerHTML = suppliers.map(s => `
            <div class="flex justify-between items-center p-3 border-b border-gray-100">
                <div>
                    <p class="font-bold text-primary">${s.name}</p>
                    <p class="text-xs text-gray-500">${s.phone || 'لا يوجد هاتف'}</p>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

async function loadSuppliersForDropdown() {
    try {
        const res = await apiFetch(`${API_URL}/suppliers`);
        const suppliers = await res.json();
        const select = document.getElementById('med-supplier');
        const purSelect = document.getElementById('pur-supplier');
        if (!select && !purSelect) return;

        const html = '<option value="">اختر المورد...</option>' +
            (suppliers || []).map(s => `<option value="${s.id}">${s.name}</option>`).join('');

        if (select) select.innerHTML = html;
        if (purSelect) purSelect.innerHTML = html;
    } catch (err) {
        console.error(err);
    }
}

document.getElementById('add-supplier-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('sup-name')?.value;
    const phone = document.getElementById('sup-phone')?.value;
    try {
        const res = await apiFetch(`${API_URL}/suppliers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone })
        });
        if (res.ok) {
            await showAlert("تم بنجاح", "تم إضافة المورد.", "success");
            document.getElementById('add-supplier-form')?.reset();
            loadSuppliersList();
            loadSuppliersForDropdown();
        }
    } catch (err) {
        showAlert("خطأ", "تعذر الاتصال", "error");
    }
});

// ============================================================
// Medicines / Inventory
// ============================================================
async function loadMedicines() {
    try {
        const res = await apiFetch(`${API_URL}/medicines`);
        const medicines = await res.json();

        // قائمة الكاشير
        const posList = document.getElementById('medicines-list');
        if (posList) {
            if (!medicines || medicines.length === 0) {
                posList.innerHTML = '<p class="text-gray-400 text-center py-6 text-sm">لا توجد أدوية بعد. أضف أدوية من شاشة المخزون.</p>';
            } else {
                posList.innerHTML = medicines.map(med => `
                    <div onclick="addToCart(${med.id}, '${(med.name || '').replace(/'/g, "\\'")}', ${med.price || 0})"
                         class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl">
                        <div>
                            <p class="font-bold text-gray-800 text-sm">${med.name}</p>
                        </div>
                        <div class="text-left">
                            <p class="font-bold text-primary">${formatCurrency(med.price)} SDG</p>
                            <p class="text-[10px] text-gray-400">المخزون: ${med.stock_quantity ?? 0}</p>
                        </div>
                    </div>
                `).join('');
            }
        }

        // قائمة المخزون
        const invList = document.getElementById('inventory-list');
        if (invList) {
            if (!medicines || medicines.length === 0) {
                invList.innerHTML = '<p class="text-gray-400 text-center py-6 text-sm">لا توجد أدوية. أضف أول دواء من النموذج أعلاه.</p>';
            } else {
                invList.innerHTML = medicines.map(med => `
                    <div class="flex justify-between items-center p-3 border-b border-gray-100">
                        <div class="flex-1">
                            <p class="font-bold text-primary text-sm">${med.name}</p>
                            <p class="text-xs text-gray-500">${med.category || ''} | ${med.supplier_name || 'بدون مورد'}</p>
                        </div>
                        <div class="text-left mr-3">
                            <p class="font-bold text-sm">${formatCurrency(med.price)} SDG</p>
                            <p class="text-xs text-gray-400">المخزون: ${med.stock_quantity ?? 0}</p>
                        </div>
                        <div class="flex gap-2">
                            <button onclick='editMedicine(${JSON.stringify(med).replace(/'/g, "&#39;")})' class="bg-blue-50 text-blue-600 p-2 rounded-lg text-sm">✏️</button>
                            <button onclick="deleteMedicine(${med.id})" class="bg-red-50 text-red-600 p-2 rounded-lg text-sm">🗑️</button>
                        </div>
                    </div>
                `).join('');
            }
        }

        await localforage.setItem('kodnaqi_medicines', medicines || []);
    } catch (err) {
        // Offline fallback
        const meds = await localforage.getItem('kodnaqi_medicines') || [];
        const posList = document.getElementById('medicines-list');
        if (posList && meds.length) {
            posList.innerHTML = meds.map(med => `
                <div onclick="addToCart(${med.id}, '${(med.name || '').replace(/'/g, "\\'")}', ${med.price || 0})"
                     class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl">
                    <div><p class="font-bold text-gray-800 text-sm">${med.name}</p></div>
                    <div class="text-left">
                        <p class="font-bold text-primary">${formatCurrency(med.price)} SDG</p>
                        <p class="text-[10px] text-gray-400">المخزون: ${med.stock_quantity ?? 0}</p>
                    </div>
                </div>
            `).join('');
        }
    }
}

document.getElementById('add-medicine-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('med-id')?.value;
    const data = {
        name: document.getElementById('med-name')?.value,
        scientific_name: document.getElementById('med-scientific')?.value || null,
        category: document.getElementById('med-category')?.value || null,
        supplier_id: document.getElementById('med-supplier')?.value ? parseInt(document.getElementById('med-supplier').value) : null,
        price: parseFloat(document.getElementById('med-price')?.value) || 0,
        cost: parseFloat(document.getElementById('med-cost')?.value) || 0,
        stock_quantity: parseInt(document.getElementById('med-stock')?.value) || 0,
        barcode: document.getElementById('med-barcode')?.value || null,
        expiry_date: document.getElementById('med-expiry')?.value || null
    };

    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/medicines/${id}` : `${API_URL}/medicines`;

    try {
        const res = await apiFetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            await showAlert("تم بنجاح", id ? "تم التعديل." : "تم الإضافة.", "success");
            resetInvForm();
            loadMedicines();
        } else {
            showAlert("خطأ", "تأكد من أن الباركود غير مكرر.", "error");
        }
    } catch (err) {
        showAlert("خطأ", "تعذر الاتصال", "error");
    }
});

function editMedicine(med) {
    if (typeof med === 'string') {
        try { med = JSON.parse(med); } catch (e) { return; }
    }
    document.getElementById('med-id').value = med.id || '';
    document.getElementById('med-name').value = med.name || '';
    document.getElementById('med-scientific').value = med.scientific_name || '';
    document.getElementById('med-category').value = med.category || '';
    document.getElementById('med-supplier').value = med.supplier_id || '';
    document.getElementById('med-price').value = med.price || '';
    document.getElementById('med-cost').value = med.cost || '';
    document.getElementById('med-stock').value = med.stock_quantity || '';
    document.getElementById('med-barcode').value = med.barcode || '';
    document.getElementById('med-expiry').value = med.expiry_date || '';
    const title = document.getElementById('inv-form-title');
    if (title) title.innerText = "تعديل دواء";
    document.getElementById('cancel-edit-btn')?.classList.remove('hidden');
    window.scrollTo(0, 0);
}

function resetInvForm() {
    document.getElementById('add-medicine-form')?.reset();
    if (document.getElementById('med-id')) document.getElementById('med-id').value = '';
    const title = document.getElementById('inv-form-title');
    if (title) title.innerText = "إضافة دواء جديد";
    document.getElementById('cancel-edit-btn')?.classList.add('hidden');
}

async function deleteMedicine(id) {
    if (!confirm("هل أنت متأكد من حذف هذا الدواء؟")) return;
    try {
        const res = await apiFetch(`${API_URL}/medicines/${id}`, { method: 'DELETE' });
        if (res.ok) {
            loadMedicines();
            showAlert("تم", "تم حذف الدواء.", "success");
        }
    } catch (err) {
        console.error(err);
    }
}

function filterMedicines() {
    const query = (document.getElementById('pos-search')?.value || '').toLowerCase();
    const items = document.querySelectorAll('#medicines-list > div');
    items.forEach(item => {
        item.style.display = item.innerText.toLowerCase().includes(query) ? 'flex' : 'none';
    });
}

function filterInventory() {
    const query = (document.getElementById('inv-search')?.value || '').toLowerCase();
    const items = document.querySelectorAll('#inventory-list > div');
    items.forEach(item => {
        item.style.display = item.innerText.toLowerCase().includes(query) ? 'flex' : 'none';
    });
}

// ============================================================
// POS / Cart
// ============================================================
function addToCart(id, name, price) {
    const existing = cart.find(item => item.medicine_id === id);
    if (existing) existing.quantity += 1;
    else cart.push({ medicine_id: id, name: name, unit_price: price, quantity: 1 });
    playVaultSound('tick');
    renderCart();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    renderCart();
}

function updateQuantity(index, change) {
    if (!cart[index]) return;
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
        totalEl.innerText = `0 SDG`;
        return;
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
                    <div class="flex items-center bg-white rounded-lg border border-gray-100">
                        <button onclick="updateQuantity(${index}, 1)" class="px-3 py-1 text-primary font-bold">+</button>
                        <span class="px-2 font-bold text-sm">${item.quantity}</span>
                        <button onclick="updateQuantity(${index}, -1)" class="px-3 py-1 text-red-500 font-bold">-</button>
                    </div>
                    <span class="font-bold text-primary w-20 text-left">${formatCurrency(item.unit_price * item.quantity)} SDG</span>
                    <button onclick="removeFromCart(${index})" class="text-red-500 bg-red-50 p-2 rounded-lg">✖</button>
                </div>
            </div>
        `;
    }).join('');
    totalEl.innerText = `${formatCurrency(total)} SDG`;
}

async function checkout() {
    if (cart.length === 0) return showAlert("تنبيه", "الفاتورة فارغة.", "error");

    let total = cart.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
    const paid = await showPrompt("الدفع", `الإجمالي المطلوب: ${formatCurrency(total)} SDG`, total);
    if (paid === null || paid === "") return;

    const paidAmount = parseFloat(paid);
    if (isNaN(paidAmount) || paidAmount < total) {
        return showAlert("خطأ", "المبلغ غير كافٍ!", "error");
    }

    const localId = Date.now();
    const saleData = {
        id: localId,
        discount: 0,
        paid_amount: paidAmount,
        items: cart.map(i => ({
            medicine_id: i.medicine_id,
            quantity: i.quantity,
            unit_price: i.unit_price
        })),
        invoice_number: `OFF-${localId.toString().slice(-6)}`,
        sale_date: new Date().toISOString()
    };

    // حفظ محلي أولاً (Offline-first)
    let sales = await localforage.getItem('kodnaqi_sales') || [];
    sales.unshift(saleData);
    await localforage.setItem('kodnaqi_sales', sales);

    let outbox = await localforage.getItem('kodnaqi_outbox') || [];
    outbox.push(saleData);
    await localforage.setItem('kodnaqi_outbox', outbox);

    const change = paidAmount - total;
    preparePrintInvoice(saleData.invoice_number, cart, total, paidAmount, change);

    let msg = `رقم الفاتورة: <b>${saleData.invoice_number}</b><br>الباقي: <b class="text-primary text-lg">${formatCurrency(change)} SDG</b>`;
    msg += `<br><br><button onclick="window.print()" class="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-bold w-full">🖨️ طباعة الفاتورة</button>`;

    await showAlert("تمت العملية", msg, "success");
    cart = [];
    renderCart();
    loadMedicines();
    processOutbox();
}

function preparePrintInvoice(invoiceNumber, items, total, paid, change) {
    const pharmacyName = document.getElementById('pharmacy-name')?.innerText || 'KodNaqi Pharmacy';
    const nameEl = document.getElementById('print-pharmacy-name');
    const dateEl = document.getElementById('print-date');
    const invEl = document.getElementById('print-inv-num');
    const itemsEl = document.getElementById('print-items');
    const totalEl = document.getElementById('print-total');
    const paidEl = document.getElementById('print-paid');
    const changeEl = document.getElementById('print-change');
    const invText = document.getElementById('print-inv-text');

    if (nameEl) nameEl.innerText = pharmacyName;
    if (dateEl) dateEl.innerText = new Date().toLocaleString('ar-EG');
    if (invEl) invEl.innerText = invoiceNumber;
    if (invText) invText.innerText = invoiceNumber;

    if (itemsEl) {
        itemsEl.innerHTML = items.map(item => `
            <tr>
                <td class="py-1">${item.name}</td>
                <td class="py-1 text-center">${item.quantity}</td>
                <td class="py-1 text-left">${formatCurrency(item.unit_price)}</td>
                <td class="py-1 text-left">${formatCurrency(item.unit_price * item.quantity)}</td>
            </tr>
        `).join('');
    }

    if (totalEl) totalEl.innerText = formatCurrency(total) + ' SDG';
    if (paidEl) paidEl.innerText = formatCurrency(paid) + ' SDG';
    if (changeEl) changeEl.innerText = formatCurrency(change) + ' SDG';

    // باركود (إن وجد JsBarcode)
    try {
        if (window.JsBarcode && document.getElementById('print-barcode')) {
            JsBarcode("#print-barcode", invoiceNumber, {
                format: "CODE128",
                width: 1.5,
                height: 40,
                displayValue: false
            });
        }
    } catch (e) {}
}

// ============================================================
// Purchases
// ============================================================
async function loadPurchasesData() {
    await loadSuppliersForDropdown();
    try {
        const res = await apiFetch(`${API_URL}/medicines`);
        const meds = await res.json();
        const select = document.getElementById('pur-medicine');
        if (select) {
            select.innerHTML = '<option value="">اختر الدواء...</option>' +
                (meds || []).map(m => `<option value="${m.id}" data-cost="${m.cost || 0}">${m.name}</option>`).join('');
        }
    } catch (e) {}
    renderPurchaseCart();
}

function addToPurchaseCart() {
    const medId = document.getElementById('pur-medicine')?.value;
    const qty = parseInt(document.getElementById('pur-qty')?.value);
    const cost = parseFloat(document.getElementById('pur-cost')?.value);

    if (!medId || !qty || isNaN(cost)) {
        return showAlert("تنبيه", "اختر الدواء وأدخل الكمية والتكلفة", "error");
    }

    const select = document.getElementById('pur-medicine');
    const medName = select?.options[select.selectedIndex]?.text || '';

    const existing = purchaseCart.find(i => i.medicine_id == medId);
    if (existing) {
        existing.quantity += qty;
        existing.unit_cost = cost;
    } else {
        purchaseCart.push({
            medicine_id: parseInt(medId),
            name: medName,
            quantity: qty,
            unit_cost: cost
        });
    }

    if (document.getElementById('pur-qty')) document.getElementById('pur-qty').value = '';
    if (document.getElementById('pur-cost')) document.getElementById('pur-cost').value = '';
    renderPurchaseCart();
}

function renderPurchaseCart() {
    const div = document.getElementById('purchase-cart');
    if (!div) return;

    if (purchaseCart.length === 0) {
        div.innerHTML = '<p class="text-gray-400 text-sm text-center">لم تتم إضافة أصناف.</p>';
        return;
    }

    div.innerHTML = purchaseCart.map((item, i) => `
        <div class="flex justify-between items-center p-3 bg-bg rounded-xl mb-2">
            <div>
                <p class="font-bold text-sm text-primary">${item.name}</p>
                <p class="text-xs text-gray-500">الكمية: ${item.quantity} | التكلفة: ${item.unit_cost}</p>
            </div>
            <button onclick="purchaseCart.splice(${i},1); renderPurchaseCart()" class="text-red-500 bg-red-50 p-2 rounded-lg">✖</button>
        </div>
    `).join('');
}

async function savePurchase() {
    const supplierId = document.getElementById('pur-supplier')?.value;
    if (!supplierId) return showAlert("تنبيه", "اختر المورد", "error");
    if (purchaseCart.length === 0) return showAlert("تنبيه", "أضف أصنافاً للفاتورة", "error");

    try {
        const res = await apiFetch(`${API_URL}/purchases`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                supplier_id: parseInt(supplierId),
                items: purchaseCart.map(i => ({
                    medicine_id: i.medicine_id,
                    quantity: i.quantity,
                    unit_cost: i.unit_cost
                }))
            })
        });

        if (res.ok) {
            await showAlert("تم", "تم حفظ فاتورة الشراء وتحديث المخزون", "success");
            purchaseCart = [];
            renderPurchaseCart();
            loadMedicines();
            loadPurchasesData();
        } else {
            const data = await res.json().catch(() => ({}));
            showAlert("خطأ", data.detail || "تعذر الحفظ", "error");
        }
    } catch (err) {
        showAlert("خطأ", "تعذر الاتصال", "error");
    }
}

// ============================================================
// History & Sync
// ============================================================
async function loadHistory() {
    const list = document.getElementById('history-list');
    if (!list) return;

    try {
        const res = await apiFetch(`${API_URL}/sales`);
        const sales = await res.json();

        if (!sales || sales.length === 0) {
            list.innerHTML = '<p class="text-gray-400 text-center py-6">لا توجد فواتير بعد</p>';
            return;
        }

        list.innerHTML = sales.map(s => `
            <div class="flex justify-between items-center p-3 border-b border-gray-100">
                <div>
                    <p class="font-bold text-primary text-sm">${s.invoice_number || ('#' + s.id)}</p>
                    <p class="text-xs text-gray-500">${new Date(s.sale_date || s.created_at).toLocaleString('ar-EG')}</p>
                </div>
                <div class="text-left">
                    <p class="font-bold text-primary">${formatCurrency(s.total || s.paid_amount || 0)} SDG</p>
                </div>
            </div>
        `).join('');
    } catch (err) {
        // Offline
        const localSales = await localforage.getItem('kodnaqi_sales') || [];
        if (localSales.length === 0) {
            list.innerHTML = '<p class="text-gray-400 text-center py-6">لا توجد فواتير (أوفلاين)</p>';
            return;
        }
        list.innerHTML = localSales.map(s => `
            <div class="flex justify-between items-center p-3 border-b border-gray-100">
                <div>
                    <p class="font-bold text-primary text-sm">${s.invoice_number} <span class="text-orange-500 text-xs">(معلق)</span></p>
                    <p class="text-xs text-gray-500">${new Date(s.sale_date).toLocaleString('ar-EG')}</p>
                </div>
                <div class="text-left">
                    <p class="font-bold text-primary">${formatCurrency(s.paid_amount)} SDG</p>
                </div>
            </div>
        `).join('');
    }
}

async function processOutbox() {
    if (!navigator.onLine) return;

    let outbox = await localforage.getItem('kodnaqi_outbox') || [];
    if (outbox.length === 0) return;

    let sales = await localforage.getItem('kodnaqi_sales') || [];
    let outboxChanged = false;

    for (let i = 0; i < outbox.length; i++) {
        let sale = outbox[i];
        let sendData = {
            discount: sale.discount || 0,
            paid_amount: sale.paid_amount,
            items: sale.items.map(item => ({
                medicine_id: item.medicine_id,
                quantity: item.quantity,
                unit_price: item.unit_price
            }))
        };

        try {
            let res = await apiFetch(`${API_URL}/sales`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(sendData)
            });

            if (res.ok) {
                let serverData = await res.json();
                let localSaleIndex = sales.findIndex(s => s.id == sale.id);
                if (localSaleIndex !== -1 && serverData.invoice_number) {
                    sales[localSaleIndex].invoice_number = serverData.invoice_number;
                }
                outbox.splice(i, 1);
                i--;
                outboxChanged = true;
            } else {
                break;
            }
        } catch (e) {
            break;
        }
    }

    if (outboxChanged) {
        await localforage.setItem('kodnaqi_sales', sales);
        await localforage.setItem('kodnaqi_outbox', outbox);

        const historyView = document.getElementById('view-history');
        if (historyView && !historyView.classList.contains('hidden')) {
            loadHistory();
        }
        const dashboardView = document.getElementById('view-dashboard');
        if (dashboardView && !dashboardView.classList.contains('hidden')) {
            loadDashboard();
        }
    }
}

// ============================================================
// Z-Report & Backup
// ============================================================
async function printZReport() {
    try {
        const res = await apiFetch(`${API_URL}/z-report`);
        const data = await res.json();

        const dateEl = document.getElementById('z-report-date');
        const countEl = document.getElementById('z-report-count');
        const salesEl = document.getElementById('z-report-sales');
        const profitEl = document.getElementById('z-report-profit');

        if (dateEl) dateEl.innerText = new Date().toLocaleString('ar-EG');
        if (countEl) countEl.innerText = data.sales_count || data.today_sales_count || 0;
        if (salesEl) salesEl.innerText = formatCurrency(data.total_sales || data.today_revenue || 0) + ' SDG';
        if (profitEl) profitEl.innerText = formatCurrency(data.total_profit || data.today_profit || 0) + ' SDG';

        // إظهار منطقة الطباعة مؤقتاً
        const zArea = document.getElementById('z-report-area');
        if (zArea) zArea.classList.remove('hidden');
        window.print();
        setTimeout(() => zArea?.classList.add('hidden'), 500);
    } catch (e) {
        // fallback باستخدام stats
        try {
            const res = await apiFetch(`${API_URL}/stats`);
            const data = await res.json();
            document.getElementById('z-report-date').innerText = new Date().toLocaleString('ar-EG');
            document.getElementById('z-report-count').innerText = data.today_sales_count || 0;
            document.getElementById('z-report-sales').innerText = formatCurrency(data.today_revenue || 0) + ' SDG';
            document.getElementById('z-report-profit').innerText = formatCurrency(data.today_profit || 0) + ' SDG';
            document.getElementById('z-report-area')?.classList.remove('hidden');
            window.print();
            setTimeout(() => document.getElementById('z-report-area')?.classList.add('hidden'), 500);
        } catch (err) {
            showAlert("خطأ", "تعذر تحميل التقرير", "error");
        }
    }
}

async function downloadBackup(type) {
    if (!isAdmin()) {
        return showAlert("تنبيه", "التصدير متاح للمدير فقط", "error");
    }
    try {
        const endpoint = type === 'sales' ? '/backup/sales' : '/backup/medicines';
        const res = await apiFetch(`${API_URL}${endpoint}`);
        if (!res.ok) throw new Error('fail');

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}_${new Date().toISOString().slice(0, 10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (err) {
        showAlert("خطأ", "تعذر التصدير", "error");
    }
}

// ============================================================
// Barcode Scanner
// ============================================================
function startScanner() {
    if (html5QrCode) return;
    const reader = document.getElementById('reader');
    if (!reader) return;

    html5QrCode = new Html5Qrcode("reader");
    html5QrCode.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        async (decodedText) => {
            stopScanner();
            try {
                // ابحث عن الدواء بالباركود
                const res = await apiFetch(`${API_URL}/medicines/barcode/${encodeURIComponent(decodedText)}`);
                if (res.ok) {
                    const med = await res.json();
                    addToCart(med.id, med.name, med.price);
                    showAlert("تم", `تمت إضافة: ${med.name}`, "success");
                } else {
                    showAlert("تنبيه", "لم يتم العثور على دواء بهذا الباركود", "error");
                }
            } catch (e) {
                showAlert("تنبيه", "لم يتم العثور على دواء بهذا الباركود", "error");
            }
        },
        () => {}
    ).catch(err => {
        console.error(err);
        showAlert("خطأ", "تعذر تشغيل الكاميرا", "error");
        html5QrCode = null;
    });

    document.getElementById('stop-btn')?.classList.remove('hidden');
}

function stopScanner() {
    if (html5QrCode) {
        html5QrCode.stop().then(() => {
            html5QrCode.clear();
            html5QrCode = null;
        }).catch(() => {
            html5QrCode = null;
        });
    }
    document.getElementById('stop-btn')?.classList.add('hidden');
}

// ============================================================
// INIT
// ============================================================
async function initApp() {
    currentUser = {
        username: localStorage.getItem('kodnaqi_user') || null,
        role: localStorage.getItem('kodnaqi_role') || 'cashier'
    };

    const token = localStorage.getItem('kodnaqi_token');
    if (token) {
        try {
            const res = await apiFetch(`${API_URL}/settings`);
            if (res.ok) {
                showApp();
                processOutbox();
                return;
            }
        } catch (e) {
            localStorage.removeItem('kodnaqi_token');
            localStorage.removeItem('kodnaqi_role');
            localStorage.removeItem('kodnaqi_user');
        }
    }
    showLoginScreen();
}

// تشغيل عند تحميل الصفحة
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

// مزامنة عند عودة الاتصال
window.addEventListener('online', () => {
    processOutbox();
});
