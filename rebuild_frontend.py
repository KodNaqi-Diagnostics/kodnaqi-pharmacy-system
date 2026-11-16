import os

print("⏳ جاري إعادة بناء الواجهة بالكامل (نسخة نظيفة ومضمونة 100%)...")

# ==========================================
# 1. كتابة index.html من الصفر
# ==========================================
html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KodNaqi Pharmacy</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
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

    <!-- 2. شاشة الدخول -->
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
                <input type="text" id="login-user" value="admin" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none">
            </div>
            <div class="mb-6">
                <label class="block text-sm font-bold text-gray-700 mb-2">كلمة المرور</label>
                <input type="password" id="login-pass" value="123456" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none" dir="ltr">
            </div>
            <button onclick="handleLogin()" class="w-full bg-primary hover:bg-[#073629] text-white py-3.5 rounded-xl font-bold text-lg transition-all shadow-lg shadow-primary/30">تسجيل الدخول</button>
        </div>
    </div>

    <!-- 3. التطبيق الأساسي -->
    <div id="app-content" class="hidden">
        <header class="bg-primary text-white p-4 shadow-md sticky top-0 z-10 flex justify-between items-center rounded-b-3xl mb-4">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center p-1 overflow-hidden shadow-sm">
                    <img src="/icon-pharma.png" alt="Logo" class="w-full h-full object-contain">
                </div>
                <h1 id="pharmacy-name" class="text-xl font-bold">جاري التحميل...</h1>
            </div>
            <span id="current-tab-title" class="text-xs bg-white/20 px-3 py-1.5 rounded-full font-medium">الكاشير</span>
        </header>

        <main class="p-4 max-w-4xl mx-auto">
            <!-- قسم الكاشير -->
            <div id="view-pos" class="space-y-6">
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0 mb-4">
                    <h2 class="text-lg font-bold mb-4 text-primary">إضافة دواء للفاتورة</h2>
                    <div class="flex gap-2 mb-4">
                        <div class="relative flex-1">
                            <input type="text" id="pos-search" onkeyup="filterMedicines()" placeholder="ابحث بالاسم التجاري أو العلمي..." class="w-full bg-bg border-0 rounded-xl p-3 pl-10 focus:ring-2 focus:ring-primary outline-none text-sm">
                            <svg class="w-5 h-5 text-gray-400 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                        </div>
                        <button onclick="startScanner()" class="bg-primary hover:bg-[#073629] text-white px-5 rounded-xl font-bold transition flex items-center justify-center">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                        </button>
                    </div>
                    <div id="reader" class="w-full hidden rounded-xl overflow-hidden border-2 border-primary mb-2"></div>
                    <button onclick="stopScanner()" id="stop-btn" class="hidden w-full text-red-600 text-sm font-bold bg-red-50 py-2 rounded-lg">إيقاف الكاميرا</button>
                </div>

                <div class="bg-card p-5 rounded-3xl premium-shadow border-2 border-primary">
                    <h2 class="text-lg font-bold mb-4 text-primary flex items-center gap-2">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                        الفاتورة الحالية
                    </h2>
                    <div id="cart-items" class="space-y-2 mb-4"><p class="text-gray-400 text-sm text-center py-4">الفاتورة فارغة.</p></div>
                    <div class="border-t border-gray-200 pt-4 flex justify-between items-center text-lg font-bold">
                        <span>الإجمالي:</span>
                        <span id="cart-total" class="text-primary">0 SDG</span>
                    </div>
                    <button onclick="checkout()" class="w-full mt-4 bg-primary hover:bg-[#073629] text-white py-3.5 rounded-xl font-bold text-lg transition shadow-lg shadow-primary/30">💵 إتمام الدفع</button>
                </div>

                <div class="bg-card p-5 rounded-3xl premium-shadow border-0">
                    <h2 class="text-lg font-bold mb-4 text-primary">الأدوية المتوفرة</h2>
                    <div id="medicines-list" class="space-y-2"><p class="text-gray-500 text-center py-4">جاري تحميل الأدوية...</p></div>
                </div>
            </div>

            <!-- قسم المخزون -->
            <div id="view-inventory" class="hidden space-y-6">
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0 mb-4">
                    <h2 class="text-lg font-bold mb-4 text-primary flex items-center gap-2">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                        إضافة دواء جديد
                    </h2>
                    <form id="add-medicine-form" class="space-y-4">
                        <div class="grid grid-cols-1 gap-3">
                            <input type="text" id="med-name" placeholder="الاسم التجاري (إجباري)" required class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                            <input type="text" id="med-scientific" placeholder="الاسم العلمي (اختياري)" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                            <select id="med-category" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none text-gray-700">
                                <option value="" disabled selected>اختر تصنيف الدواء...</option>
                                <option value="حبوب أو أقراص">حبوب أو أقراص (Tablets)</option>
                                <option value="كبسولات">كبسولات (Capsules)</option>
                                <option value="شراب">شراب (Syrup)</option>
                                <option value="حقن">حقن (Injections)</option>
                                <option value="محاليل وريدية">محاليل وريدية (IV Fluids)</option>
                                <option value="مراهم / كريمات">مراهم / كريمات (Ointments)</option>
                                <option value="قطرة">قطرة (Drops)</option>
                                <option value="مستلزمات طبية">مستلزمات طبية (قطن، شاش، كانيولا...)</option>
                                <option value="أخرى">أخرى (Other)</option>
                            </select>
                            <div class="grid grid-cols-2 gap-3">
                                <input type="number" id="med-price" placeholder="سعر البيع (SDG)" required class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                                <input type="number" id="med-stock" placeholder="الكمية المتوفرة" required class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                            </div>
                            <input type="text" id="med-barcode" placeholder="الباركود (لمسحه بالكاميرا لاحقاً)" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                        </div>
                        <button type="submit" class="w-full bg-primary hover:bg-[#073629] text-white py-3.5 rounded-xl font-bold shadow-lg shadow-primary/30 transition">حفظ في المخزون</button>
                    </form>
                </div>
            </div>

            <!-- قسم السجلات -->
            <div id="view-history" class="hidden space-y-6">
                <div class="bg-card p-5 rounded-3xl premium-shadow border-0">
                    <h2 class="text-lg font-bold mb-4 text-primary flex items-center gap-2">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                        سجل الفواتير
                    </h2>
                    <div id="history-list" class="space-y-2"><p class="text-gray-500 text-center py-4">جاري التحميل...</p></div>
                </div>
            </div>

            <!-- قسم الإعدادات -->
            <div id="view-settings" class="hidden space-y-6">
                <h2 class="text-xl font-bold text-primary mb-2 px-2">الإعدادات</h2>
                <div class="bg-card rounded-3xl premium-shadow overflow-hidden">
                    <form id="settings-form" class="divide-y divide-gray-100">
                        <div class="p-4 flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 bg-bg rounded-full flex items-center justify-center text-primary">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                                </div>
                                <span class="font-bold text-sm text-gray-700">اسم الصيدلية</span>
                            </div>
                            <input type="text" id="set-name" required class="text-left bg-bg border-0 rounded-lg p-2 text-sm focus:ring-1 focus:ring-primary outline-none w-1/2 text-primary font-bold">
                        </div>
                        <div class="p-4 flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 bg-bg rounded-full flex items-center justify-center text-primary">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                </div>
                                <span class="font-bold text-sm text-gray-700">العملة</span>
                            </div>
                            <input type="text" id="set-currency" required class="text-left bg-bg border-0 rounded-lg p-2 text-sm focus:ring-1 focus:ring-primary outline-none w-1/2 text-primary font-bold">
                        </div>
                        <div class="p-4">
                            <button type="submit" class="w-full bg-primary/10 hover:bg-primary/20 text-primary py-3 rounded-xl font-bold transition-all">تحديث الإعدادات</button>
                        </div>
                    </form>
                </div>
                <div class="bg-card rounded-3xl premium-shadow overflow-hidden mt-4">
                    <button onclick="handleLogout()" class="w-full p-4 flex items-center justify-between text-red-600 hover:bg-red-50 transition">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                                <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                            </div>
                            <span class="font-bold text-sm">تسجيل الخروج</span>
                        </div>
                    </button>
                </div>
            </div>
        </main>

        <!-- شريط التنقل السفلي -->
        <nav class="fixed bottom-0 w-full bg-white border-t border-gray-100 flex justify-around py-2 px-1 z-20 shadow-[0_-4px_20px_rgba(0,0,0,0.04)] rounded-t-3xl pb-4">
            <button onclick="switchTab('pos')" id="btn-pos" class="flex flex-col items-center p-2 text-primary w-1/4 transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                <span class="text-[10px] font-bold">الكاشير</span>
            </button>
            <button onclick="switchTab('inventory')" id="btn-inventory" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/4 transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
                <span class="text-[10px] font-bold">المخزون</span>
            </button>
            <button onclick="switchTab('history')" id="btn-history" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/4 transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                <span class="text-[10px] font-bold">السجلات</span>
            </button>
            <button onclick="switchTab('settings')" id="btn-settings" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/4 transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                <span class="text-[10px] font-bold">الإعدادات</span>
            </button>
        </nav>
    </div>

    <!-- منطقة الطباعة -->
    <div id="print-area" class="hidden bg-white text-black p-4 w-full max-w-sm mx-auto font-sans text-sm" dir="rtl">
        <div class="text-center border-b-2 border-black border-dashed pb-2 mb-2">
            <img src="/logo-pharma.png" alt="Logo" class="w-24 h-24 object-contain mx-auto mb-2 grayscale">
            <h2 id="print-pharmacy-name" class="text-xl font-bold mb-1">اسم الصيدلية</h2>
            <p class="text-xs" id="print-date">التاريخ</p>
            <p class="text-xs font-bold mt-1">رقم الفاتورة: <span id="print-inv-num"></span></p>
        </div>
        <table class="w-full text-xs text-right mb-2">
            <thead><tr class="border-b border-black"><th class="pb-1">الصنف</th><th class="pb-1 text-center">الكمية</th><th class="pb-1 text-left">السعر</th><th class="pb-1 text-left">الإجمالي</th></tr></thead>
            <tbody id="print-items"></tbody>
        </table>
        <div class="border-t-2 border-black border-dashed pt-2 mb-4 space-y-1 text-sm">
            <div class="flex justify-between font-bold"><span>الإجمالي:</span><span id="print-total">0 SDG</span></div>
            <div class="flex justify-between"><span>المدفوع:</span><span id="print-paid">0 SDG</span></div>
            <div class="flex justify-between"><span>الباقي:</span><span id="print-change">0 SDG</span></div>
        </div>
        <div class="flex flex-col items-center mt-6">
            <svg id="print-barcode" class="w-full max-w-[200px]"></svg>
            <p class="text-xs mt-1 font-mono" id="print-inv-text"></p>
        </div>
        <div class="text-center text-xs mt-4 border-t border-black border-dashed pt-2"><p>شكراً لزيارتكم!</p></div>
    </div>

    <!-- النوافذ المنبثقة -->
    <div id="app-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm hidden items-center justify-center z-50 transition-opacity duration-300">
        <div class="bg-white rounded-2xl shadow-2xl p-6 w-11/12 max-w-sm transform scale-95 transition-transform duration-300" id="modal-content">
            <div id="modal-icon" class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-emerald-100 mb-4"><span class="text-3xl">✅</span></div>
            <h3 id="modal-title" class="text-xl font-bold text-center text-gray-800 mb-2">عنوان</h3>
            <p id="modal-message" class="text-center text-gray-600 mb-6 text-sm">رسالة</p>
            <input type="number" id="modal-input" class="hidden w-full text-center text-2xl font-bold border-2 border-primary rounded-lg p-3 mb-6 focus:outline-none focus:ring-4 focus:ring-primary/20" dir="ltr">
            <div class="flex gap-3">
                <button id="modal-cancel" class="hidden flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 py-3 rounded-xl font-bold transition">إلغاء</button>
                <button id="modal-confirm" class="flex-1 bg-primary hover:bg-[#073629] text-white py-3 rounded-xl font-bold transition shadow-lg shadow-primary/30">موافق</button>
            </div>
        </div>
    </div>

    <script src="/app.js"></script>
</body>
</html>"""

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("✅ تم بناء index.html (النسخة النهائية).")


# ==========================================
# 2. كتابة app.js من الصفر
# ==========================================
js_content = """const API_URL = "/api";
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
    loadMedicines();
}

// 2. التنقل
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
    } catch (err) { console.error(err); }
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
    } catch (err) { console.error(err); }
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
    const data = {
        name: document.getElementById('med-name').value,
        scientific_name: document.getElementById('med-scientific').value || null,
        category: document.getElementById('med-category').value || null,
        price: parseFloat(document.getElementById('med-price').value),
        stock_quantity: parseInt(document.getElementById('med-stock').value),
        barcode: document.getElementById('med-barcode').value || null,
        cost: 0
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
                    <span class="font-bold text-primary w-16 text-left">${item.unit_price * item.quantity} SDG</span>
                    <button onclick="removeFromCart(${index})" class="text-red-500 bg-red-50 p-2 rounded-lg hover:bg-red-100 transition">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
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

// 7. السجلات والطباعة
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
    } catch (err) { console.error(err); }
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
    if (typeof JsBarcode !== 'undefined') JsBarcode("#print-barcode", invNum, { format: "CODE128", lineColor: "#000", width: 2, height: 40, displayValue: false });
    document.getElementById('print-inv-text').innerText = invNum;
}

function reprintInvoice(sale) {
    const items = sale.items.map(i => ({ name: i.name, quantity: i.quantity, unit_price: i.unit_price }));
    preparePrintInvoice(sale.invoice_number, items, sale.total_amount, sale.paid_amount, (sale.paid_amount - sale.total_amount), sale.sale_date);
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
"""

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js_content)
print("✅ تم بناء app.js (النسخة النهائية).")

# 3. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v4';", "const CACHE_NAME = 'kodnaqi-v5';")
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v5.")

print("\n🎉 اكتملت إعادة البناء! اتبع خطوات المسح.")
