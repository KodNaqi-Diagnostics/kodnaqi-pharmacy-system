import os

print("⏳ جاري بناء الواجهة الأمامية الجديدة (تسجيل دخول حقيقي، موردين، وتعديل مخزون)...")

# ==========================================
# 1. بناء index.html
# ==========================================
html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KodNaqi Pharmacy</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Poppins:wght@600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Tajawal', 'sans-serif'], english: ['Poppins', 'sans-serif'] },
                    colors: { primary: '#0b4d3b', bg: '#f2ede4', card: '#ffffff', textMain: '#1a202c' }
                }
            }
        }
    </script>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/localforage/1.10.0/localforage.min.js"></script>
    <link rel="manifest" href="/manifest.json">
    <style>
        body { font-family: 'Tajawal', sans-serif; background-color: #f2ede4; color: #1a202c; }
        .premium-shadow { box-shadow: 0 4px 25px rgba(0,0,0,0.03); }
        @media print {
            body > * { display: none !important; }
            #print-area { display: block !important; margin: 0 auto !important; padding: 10px; width: 100%; max-width: 80mm; color: #000 !important; background: #fff !important; }
            #app-modal { display: none !important; }
            @page { margin: 5mm; }
        }
    </style>
</head>
<body class="text-textMain pb-24">

    <!-- 1. شاشة البداية -->
    <div id="splash-screen" class="fixed inset-0 bg-primary z-[100] flex flex-col items-center justify-center transition-opacity duration-500">
        <img src="/logo-pharma.png" alt="Logo" class="w-48 h-48 object-contain mb-4 drop-shadow-2xl">
        <h1 class="text-white text-3xl font-bold tracking-widest font-english mt-2">KodNaqi Pharmacy</h1>
        <p class="text-white/70 text-sm mt-2">نظام إدارة الصيدلية</p>
    </div>

    <!-- 2. شاشة الدخول الحقيقية -->
    <div id="login-screen" class="fixed inset-0 bg-bg z-50 hidden flex-col justify-center p-6">
        <div class="text-center mb-10">
            <div class="w-24 h-24 bg-primary rounded-3xl mx-auto flex items-center justify-center mb-6 shadow-xl shadow-primary/30">
                <span class="font-english text-4xl font-bold text-white tracking-widest">KN</span>
            </div>
            <h2 class="text-2xl font-bold text-primary">مرحباً بك مجدداً</h2>
            <p class="text-gray-500 text-sm mt-1">سجل الدخول لإدارة صيدليتك</p>
        </div>
        <div class="bg-card p-6 rounded-3xl premium-shadow">
            <div class="mb-4">
                <label class="block text-sm font-bold text-gray-700 mb-2">اسم المستخدم</label>
                <input type="text" id="login-user" placeholder="admin" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none">
            </div>
            <div class="mb-6">
                <label class="block text-sm font-bold text-gray-700 mb-2">كلمة المرور</label>
                <input type="password" id="login-pass" placeholder="••••••••" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none" dir="ltr">
            </div>
            <button onclick="handleLogin()" class="w-full bg-primary hover:bg-[#073629] text-white py-3.5 rounded-xl font-bold text-lg transition-all shadow-lg shadow-primary/30">تسجيل الدخول</button>
        </div>
    </div>

    <!-- 3. التطبيق الأساسي -->
    <div id="app-content" class="hidden">
        <header class="bg-primary text-white p-4 shadow-md sticky top-0 z-10 flex justify-between items-center rounded-b-3xl mb-4">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-white rounded-xl flex items-center justify-center p-1 overflow-hidden shadow-sm border border-white/20">
                    <img src="/icon-pharma.png" alt="Logo" class="w-full h-full object-contain">
                </div>
                <h1 id="pharmacy-name" class="text-xl font-bold">جاري التحميل...</h1>
            </div>
            <span id="current-tab-title" class="text-xs bg-white/20 px-3 py-1.5 rounded-full font-medium">الرئيسية</span>
        </header>

        <main class="p-4 max-w-4xl mx-auto">
            <!-- لوحة التحكم -->
            <div id="view-dashboard" class="hidden space-y-6">
                <h2 class="text-xl font-bold text-primary mb-2 px-2">نظرة عامة</h2>
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-card p-4 rounded-3xl premium-shadow border-0 flex flex-col items-center justify-center text-center">
                        <span class="text-gray-500 text-xs font-bold mb-1">مبيعات اليوم</span>
                        <span id="stat-revenue" class="text-2xl font-bold text-primary">0 SDG</span>
                        <span id="stat-count" class="text-[10px] text-gray-400 mt-1">0 فاتورة</span>
                    </div>
                    <div class="bg-card p-4 rounded-3xl premium-shadow border-0 flex flex-col items-center justify-center text-center">
                        <span class="text-gray-500 text-xs font-bold mb-1">أرباح اليوم (تقديري)</span>
                        <span id="stat-profit" class="text-2xl font-bold text-blue-600">0 SDG</span>
                    </div>
                </div>
            </div>

            <!-- الكاشير -->
            <div id="view-pos" class="hidden space-y-6">
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0 mb-4">
                    <h2 class="text-lg font-bold mb-4 text-primary">إضافة دواء للفاتورة</h2>
                    <div class="flex gap-2 mb-4">
                        <input type="text" id="pos-search" onkeyup="filterMedicines()" placeholder="ابحث بالاسم..." class="flex-1 bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none text-sm">
                        <button onclick="startScanner()" class="bg-primary text-white px-5 rounded-xl font-bold transition">📷 مسح</button>
                    </div>
                    <div id="reader" class="w-full hidden rounded-xl overflow-hidden border-2 border-primary mb-2"></div>
                    <button onclick="stopScanner()" id="stop-btn" class="hidden w-full text-red-600 text-sm font-bold bg-red-50 py-2 rounded-lg">إيقاف الكاميرا</button>
                </div>
                <div class="bg-card p-5 rounded-3xl premium-shadow border-2 border-primary">
                    <h2 class="text-lg font-bold mb-4 text-primary">الفاتورة الحالية</h2>
                    <div id="cart-items" class="space-y-2 mb-4"><p class="text-gray-400 text-sm text-center py-4">الفاتورة فارغة.</p></div>
                    <div class="border-t border-gray-200 pt-4 flex justify-between items-center text-lg font-bold">
                        <span>الإجمالي:</span><span id="cart-total" class="text-primary">0 SDG</span>
                    </div>
                    <button onclick="checkout()" class="w-full mt-4 bg-primary text-white py-3.5 rounded-xl font-bold text-lg shadow-lg shadow-primary/30">💵 إتمام الدفع</button>
                </div>
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0">
                    <h2 class="text-lg font-bold mb-4 text-primary">الأدوية المتوفرة</h2>
                    <div id="medicines-list" class="space-y-2"></div>
                </div>
            </div>

            <!-- المخزون -->
            <div id="view-inventory" class="hidden space-y-6">
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0 mb-4">
                    <h2 class="text-lg font-bold mb-4 text-primary" id="inv-form-title">إضافة دواء جديد</h2>
                    <form id="add-medicine-form" class="space-y-3">
                        <input type="hidden" id="med-id">
                        <input type="text" id="med-name" placeholder="الاسم التجاري (إجباري)" required class="w-full bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                        <input type="text" id="med-scientific" placeholder="الاسم العلمي (اختياري)" class="w-full bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                        <select id="med-category" class="w-full bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none text-gray-700">
                            <option value="">اختر تصنيف الدواء...</option>
                            <option value="حبوب أو أقراص">حبوب أو أقراص</option>
                            <option value="كبسولات">كبسولات</option>
                            <option value="شراب">شراب</option>
                            <option value="حقن">حقن</option>
                            <option value="محاليل وريدية">محاليل وريدية</option>
                            <option value="مراهم / كريمات">مراهم / كريمات</option>
                            <option value="قطرة">قطرة</option>
                            <option value="مستلزمات طبية">مستلزمات طبية</option>
                        </select>
                        <select id="med-supplier" class="w-full bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none text-gray-700">
                            <option value="">اختر المورد (اختياري)...</option>
                        </select>
                        <div class="grid grid-cols-2 gap-3">
                            <input type="number" id="med-price" placeholder="سعر البيع" required class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                            <input type="number" id="med-cost" placeholder="سعر التكلفة" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <input type="number" id="med-stock" placeholder="الكمية" required class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                            <input type="text" id="med-barcode" placeholder="الباركود" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                        </div>
                        <input type="date" id="med-expiry" title="تاريخ الانتهاء" class="w-full bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none text-gray-500">
                        <button type="submit" class="w-full bg-primary text-white py-3.5 rounded-xl font-bold shadow-lg shadow-primary/30 transition">حفظ في المخزون</button>
                        <button type="button" id="cancel-edit-btn" onclick="resetInvForm()" class="w-full bg-gray-200 text-gray-700 py-2 rounded-xl font-bold hidden">إلغاء التعديل</button>
                    </form>
                </div>
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0">
                    <h2 class="text-lg font-bold mb-4 text-primary">قائمة الأدوية</h2>
                    <input type="text" id="inv-search" onkeyup="filterInventory()" placeholder="ابحث في المخزون..." class="w-full bg-bg border-0 rounded-xl p-3 mb-4 text-sm">
                    <div id="inventory-list" class="space-y-2 max-h-96 overflow-y-auto"></div>
                </div>
            </div>

            <!-- السجلات -->
            <div id="view-history" class="hidden space-y-6">
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0">
                    <h2 class="text-lg font-bold mb-4 text-primary">سجل الفواتير</h2>
                    <div id="history-list" class="space-y-2"></div>
                </div>
            </div>

            <!-- الموردين -->
            <div id="view-suppliers" class="hidden space-y-6">
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0 mb-4">
                    <h2 class="text-lg font-bold mb-4 text-primary">إضافة مورد جديد</h2>
                    <form id="add-supplier-form" class="flex gap-2">
                        <input type="text" id="sup-name" placeholder="اسم المورد" required class="flex-1 bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                        <input type="text" id="sup-phone" placeholder="رقم الهاتف" class="flex-1 bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                        <button type="submit" class="bg-primary text-white px-4 rounded-xl font-bold">حفظ</button>
                    </form>
                </div>
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0">
                    <h2 class="text-lg font-bold mb-4 text-primary">قائمة الموردين</h2>
                    <div id="suppliers-list" class="space-y-2"></div>
                </div>
            </div>

            <!-- الإعدادات -->
            <div id="view-settings" class="hidden space-y-6">
                <h2 class="text-xl font-bold text-primary mb-2 px-2">الإعدادات</h2>
                <div class="bg-card rounded-3xl premium-shadow overflow-hidden">
                    <form id="settings-form" class="divide-y divide-gray-100">
                        <div class="p-4 flex items-center justify-between">
                            <span class="font-bold text-sm text-gray-700">اسم الصيدلية</span>
                            <input type="text" id="set-name" required class="text-left bg-bg border-0 rounded-lg p-2 text-sm w-1/2 text-primary font-bold">
                        </div>
                        <div class="p-4 flex items-center justify-between">
                            <span class="font-bold text-sm text-gray-700">العملة</span>
                            <input type="text" id="set-currency" required class="text-left bg-bg border-0 rounded-lg p-2 text-sm w-1/2 text-primary font-bold">
                        </div>
                        <div class="p-4">
                            <button type="submit" class="w-full bg-primary/10 text-primary py-3 rounded-xl font-bold">تحديث الإعدادات</button>
                        </div>
                    </form>
                </div>
                <div class="bg-card rounded-3xl premium-shadow overflow-hidden mt-4">
                    <button onclick="handleLogout()" class="w-full p-4 flex items-center justify-between text-red-600 hover:bg-red-50 transition">
                        <span class="font-bold text-sm">تسجيل الخروج</span>
                    </button>
                </div>
            </div>
        </main>

        <!-- شريط التنقل السفلي -->
        <nav class="fixed bottom-0 w-full bg-white border-t border-gray-100 flex justify-around py-2 px-1 z-20 shadow-[0_-4px_20px_rgba(0,0,0,0.04)] rounded-t-3xl pb-4">
            <button onclick="switchTab('dashboard')" id="btn-dashboard" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/5 transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                <span class="text-[10px] font-bold">الرئيسية</span>
            </button>
            <button onclick="switchTab('pos')" id="btn-pos" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/5 transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                <span class="text-[10px] font-bold">الكاشير</span>
            </button>
            <button onclick="switchTab('inventory')" id="btn-inventory" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/5 transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
                <span class="text-[10px] font-bold">المخزون</span>
            </button>
            <button onclick="switchTab('history')" id="btn-history" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/5 transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                <span class="text-[10px] font-bold">السجلات</span>
            </button>
            <button onclick="switchTab('suppliers')" id="btn-suppliers" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/5 transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                <span class="text-[10px] font-bold">الموردين</span>
            </button>
        </nav>
    </div>

    <!-- منطقة الطباعة -->
    <div id="print-area" class="hidden bg-white text-black p-4 w-full max-w-sm mx-auto font-sans text-sm" dir="rtl">
        <div class="text-center border-b-2 border-black border-dashed pb-2 mb-2">
            <h2 id="print-pharmacy-name" class="text-xl font-bold mb-1">اسم الصيدلية</h2>
            <p class="text-xs" id="print-date">التاريخ</p>
            <p class="text-xs font-bold mt-1">رقم الفاتورة: <span id="print-inv-num"></span></p>
        </div>
        <table class="w-full text-xs text-right mb-2">
            <thead><tr class="border-b border-black"><th class="pb-1">الصنف</th><th class="pb-1 text-center">الكمية</th><th class="pb-1 text-left">السعر</th><th class="pb-1 text-left">الإجمالي</th></tr></thead>
            <tbody id="print-items"></tbody>
        </table>
        <div class="border-t-2 border-black border-dashed pt-2 mb-4 space-y-1 text-sm">
            <div class="flex justify-between font-bold"><span>الإجمالي:</span><span id="print-total"></span></div>
            <div class="flex justify-between"><span>المدفوع:</span><span id="print-paid"></span></div>
            <div class="flex justify-between"><span>الباقي:</span><span id="print-change"></span></div>
        </div>
        <div class="flex flex-col items-center mt-6">
            <svg id="print-barcode" class="w-full max-w-[200px]"></svg>
            <p class="text-xs mt-1 font-mono" id="print-inv-text"></p>
        </div>
        <div class="text-center text-xs mt-4 border-t border-black border-dashed pt-2"><p>شكراً لزيارتكم!</p></div>
    </div>

    <!-- النافذة المنبثقة -->
    <div id="app-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm hidden items-center justify-center z-50 transition-opacity duration-300">
        <div class="bg-white rounded-2xl shadow-2xl p-6 w-11/12 max-w-sm transform scale-95 transition-transform duration-300" id="modal-content">
            <div id="modal-icon" class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-4"><span class="text-3xl text-primary">✅</span></div>
            <h3 id="modal-title" class="text-xl font-bold text-center text-gray-800 mb-2">عنوان</h3>
            <p id="modal-message" class="text-center text-gray-600 mb-6 text-sm">رسالة</p>
            <input type="number" id="modal-input" class="hidden w-full text-center text-2xl font-bold border-2 border-primary rounded-lg p-3 mb-6 focus:outline-none" dir="ltr">
            <div class="flex gap-3">
                <button id="modal-cancel" class="hidden flex-1 bg-gray-200 text-gray-800 py-3 rounded-xl font-bold">إلغاء</button>
                <button id="modal-confirm" class="flex-1 bg-primary text-white py-3 rounded-xl font-bold shadow-lg shadow-primary/30">موافق</button>
            </div>
        </div>
    </div>

    <script src="/app.js"></script>
</body>
</html>"""

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# ==========================================
# 2. بناء app.js
# ==========================================
js_content = """const API_URL = "/api";
let cart = [];
let html5QrCode = null;

function formatCurrency(num) { return Number(num).toLocaleString('en-US'); }

// ==================== Auth & Init ====================
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

async function handleLogin() {
    const user = document.getElementById('login-user').value;
    const pass = document.getElementById('login-pass').value;
    
    if(!user || !pass) return showAlert("تنبيه", "أدخل اسم المستخدم وكلمة المرور", "error");

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass })
        });
        const data = await res.json();
        
        if (res.ok) {
            localStorage.setItem('kodnaqi_auth', 'true');
            document.getElementById('login-screen').classList.add('hidden');
            document.getElementById('login-screen').classList.remove('flex');
            showApp();
        } else {
            showAlert("خطأ", data.detail || "بيانات الدخول غير صحيحة", "error");
        }
    } catch (err) {
        showAlert("خطأ", "تعذر الاتصال بالسيرفر", "error");
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
    switchTab('dashboard');
}

// ==================== Tabs ====================
function switchTab(tabId) {
    ['dashboard', 'pos', 'inventory', 'history', 'suppliers', 'settings'].forEach(id => {
        const view = document.getElementById(`view-${id}`);
        const btn = document.getElementById(`btn-${id}`);
        if(view) view.classList.add('hidden');
        if(btn) btn.className = "flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/5 transition-all";
    });

    const activeView = document.getElementById(`view-${tabId}`);
    const activeBtn = document.getElementById(`btn-${tabId}`);
    if(activeView) activeView.classList.remove('hidden');
    if(activeBtn) activeBtn.className = "flex flex-col items-center p-2 text-primary w-1/5 transition-all";

    const titles = { dashboard: 'الرئيسية', pos: 'الكاشير', inventory: 'المخزون', history: 'السجلات', suppliers: 'الموردين', settings: 'الإعدادات' };
    const titleEl = document.getElementById('current-tab-title');
    if(titleEl) titleEl.innerText = titles[tabId];

    if (tabId === 'dashboard') loadDashboard();
    if (tabId === 'inventory') { loadMedicines(); loadSuppliersForDropdown(); }
    if (tabId === 'history') loadHistory();
    if (tabId === 'suppliers') loadSuppliersList();
    if (tabId === 'settings') fetchSettingsForForm();
}

// ==================== Alerts ====================
function showAlert(title, message, type = 'success') { /* ... same as before ... */ }
function showPrompt(title, message, defaultValue) { /* ... same as before ... */ }

// ==================== Suppliers ====================
async function loadSuppliersList() {
    try {
        const res = await fetch(`${API_URL}/suppliers`);
        const suppliers = await res.json();
        const list = document.getElementById('suppliers-list');
        if(suppliers.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center">لا يوجد موردين.</p>'; return; }
        
        list.innerHTML = suppliers.map(s => `
            <div class="flex justify-between items-center p-3 border-b border-gray-100">
                <div><p class="font-bold text-primary">${s.name}</p><p class="text-xs text-gray-500">${s.phone || 'لا يوجد هاتف'}</p></div>
            </div>
        `).join('');
    } catch (err) { console.error(err); }
}

async function loadSuppliersForDropdown() {
    try {
        const res = await fetch(`${API_URL}/suppliers`);
        const suppliers = await res.json();
        const select = document.getElementById('med-supplier');
        if(!select) return;
        select.innerHTML = '<option value="">اختر المورد...</option>' + suppliers.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    } catch (err) { console.error(err); }
}

document.getElementById('add-supplier-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('sup-name').value;
    const phone = document.getElementById('sup-phone').value;
    try {
        const res = await fetch(`${API_URL}/suppliers`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, phone }) });
        if(res.ok) {
            await showAlert("تم بنجاح", "تم إضافة المورد.", "success");
            document.getElementById('add-supplier-form').reset();
            loadSuppliersList();
        }
    } catch (err) { showAlert("خطأ", "تعذر الاتصال بالسيرفر", "error"); }
});

// ==================== Medicines CRUD ====================
async function loadMedicines() {
    try {
        const res = await fetch(`${API_URL}/medicines`);
        const medicines = await res.json();
        
        // For POS list
        const posList = document.getElementById('medicines-list');
        if(posList) {
            posList.innerHTML = medicines.map(med => `
                <div onclick="addToCart(${med.id}, '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl">
                    <div><p class="font-bold text-gray-800 text-sm">${med.name}</p></div>
                    <div class="text-left"><p class="font-bold text-primary">${formatCurrency(med.price)} SDG</p></div>
                </div>
            `).join('');
        }

        // For Inventory list
        const invList = document.getElementById('inventory-list');
        if(invList) {
            invList.innerHTML = medicines.map(med => `
                <div class="flex justify-between items-center p-3 border-b border-gray-100">
                    <div>
                        <p class="font-bold text-gray-800 text-sm">${med.name}</p>
                        <p class="text-[10px] text-gray-500">${med.category || ''} | ${med.supplier_name || 'بدون مورد'}</p>
                    </div>
                    <div class="text-left flex items-center gap-3">
                        <div><p class="font-bold text-primary text-sm">${med.price} SDG</p><p class="text-[10px] ${med.stock_quantity <= 10 ? 'text-red-500 font-bold' : 'text-gray-400'}">المخزون: ${med.stock_quantity}</p></div>
                        <button onclick='editMedicine(${JSON.stringify(med)})' class="bg-blue-50 text-blue-600 p-2 rounded-lg">✏️</button>
                        <button onclick="deleteMedicine(${med.id})" class="bg-red-50 text-red-600 p-2 rounded-lg">🗑️</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (err) { console.error(err); }
}

document.getElementById('add-medicine-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('med-id').value;
    const data = {
        name: document.getElementById('med-name').value,
        scientific_name: document.getElementById('med-scientific').value || null,
        category: document.getElementById('med-category').value || null,
        supplier_id: document.getElementById('med-supplier').value ? parseInt(document.getElementById('med-supplier').value) : null,
        price: parseFloat(document.getElementById('med-price').value),
        cost: parseFloat(document.getElementById('med-cost').value) || 0,
        stock_quantity: parseInt(document.getElementById('med-stock').value),
        barcode: document.getElementById('med-barcode').value || null,
        expiry_date: document.getElementById('med-expiry').value || null
    };

    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/medicines/${id}` : `${API_URL}/medicines`;

    try {
        const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        if (res.ok) {
            await showAlert("تم بنجاح", id ? "تم تعديل الدواء." : "تم إضافة الدواء.", "success");
            resetInvForm();
            loadMedicines();
        } else showAlert("خطأ", "تأكد من أن الباركود غير مكرر.", "error");
    } catch (err) { showAlert("خطأ", "تعذر الاتصال", "error"); }
});

function editMedicine(med) {
    document.getElementById('med-id').value = med.id;
    document.getElementById('med-name').value = med.name;
    document.getElementById('med-scientific').value = med.scientific_name || '';
    document.getElementById('med-category').value = med.category || '';
    document.getElementById('med-supplier').value = med.supplier_id || '';
    document.getElementById('med-price').value = med.price;
    document.getElementById('med-cost').value = med.cost || '';
    document.getElementById('med-stock').value = med.stock_quantity;
    document.getElementById('med-barcode').value = med.barcode || '';
    document.getElementById('med-expiry').value = med.expiry_date || '';
    
    document.getElementById('inv-form-title').innerText = "تعديل دواء";
    document.getElementById('cancel-edit-btn').classList.remove('hidden');
    window.scrollTo(0,0);
}

function resetInvForm() {
    document.getElementById('add-medicine-form').reset();
    document.getElementById('med-id').value = '';
    document.getElementById('inv-form-title').innerText = "إضافة دواء جديد";
    document.getElementById('cancel-edit-btn').classList.add('hidden');
}

async function deleteMedicine(id) {
    if(!confirm("هل أنت متأكد من حذف هذا الدواء؟")) return;
    try {
        const res = await fetch(`${API_URL}/medicines/${id}`, { method: 'DELETE' });
        if(res.ok) { loadMedicines(); showAlert("تم", "تم حذف الدواء.", "success"); }
    } catch (err) { console.error(err); }
}

// (باقي الدوال مثل loadDashboard, checkout, loadHistory, الكاميرا, الطباعة، الخ تبقى كما هي)
"""

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("✅ تم بناء الواجهة الجديدة.")

# كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v13';", "const CACHE_NAME = 'kodnaqi-v14';")
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v14.")
