import os
import re

print("⏳ جاري تطبيق التحديث الشامل (Premium UI + Splash + Login + Icons)...")

# ==========================================
# 1. تحديث index.html
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. تحديث الـ Head (الخطوط والألوان)
new_head = """
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KodNaqi Pharmacy</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Tajawal', 'sans-serif'] },
                    colors: {
                        primary: '#0b4d3b', // الأخضر الداكن
                        bg: '#f2ede4',      // الرمادي/البيج الدافئ (مطابق لصرف)
                        card: '#ffffff',
                        textMain: '#1a202c'
                    }
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
        /* تنسيقات الطباعة */
        @media print {
            body > * { display: none !important; }
            #print-area { display: block !important; margin: 0 auto !important; padding: 10px; width: 100%; max-width: 80mm; color: #000 !important; background: #fff !important; }
            #app-modal { display: none !important; }
            @page { margin: 5mm; }
        }
    </style>
</head>"""
html = re.sub(r'<head>.*?</head>', new_head, html, flags=re.DOTALL)

# ب. إضافة شاشة البداية وشاشة الدخول (قبل الـ body)
splash_login = """
<body class="text-textMain pb-24">
    <!-- 1. شاشة البداية (Splash Screen) -->
    <div id="splash-screen" class="fixed inset-0 bg-primary z-[100] flex flex-col items-center justify-center transition-opacity duration-500">
        <!-- ضع رابط شعار الصيدلية هنا لاحقاً -->
        <div class="w-24 h-24 bg-white rounded-full flex items-center justify-center mb-4 shadow-lg">
            <svg class="w-12 h-12 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
        </div>
        <h1 class="text-white text-2xl font-bold tracking-wider">KodNaqi Pharmacy</h1>
        <p class="text-white/70 text-sm mt-2">نظام إدارة الصيدلية</p>
    </div>

    <!-- 2. شاشة تسجيل الدخول (Login Screen) -->
    <div id="login-screen" class="fixed inset-0 bg-bg z-50 hidden flex-col justify-center p-6">
        <div class="text-center mb-10">
            <div class="w-20 h-20 bg-primary rounded-2xl mx-auto flex items-center justify-center mb-4 shadow-lg shadow-primary/30">
                <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
            </div>
            <h2 class="text-2xl font-bold text-primary">مرحباً بك مجدداً</h2>
            <p class="text-gray-500 text-sm mt-1">سجل الدخول لإدارة صيدليتك</p>
        </div>
        
        <div class="bg-card p-6 rounded-3xl premium-shadow">
            <div class="mb-4">
                <label class="block text-sm font-bold text-gray-700 mb-2">اسم المستخدم</label>
                <input type="text" id="login-user" value="admin" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none" placeholder="أدخل اسم المستخدم">
            </div>
            <div class="mb-6">
                <label class="block text-sm font-bold text-gray-700 mb-2">كلمة المرور</label>
                <input type="password" id="login-pass" value="123456" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none" placeholder="••••••••">
            </div>
            <button onclick="handleLogin()" class="w-full bg-primary hover:bg-[#073629] text-white py-3.5 rounded-xl font-bold text-lg transition-all shadow-lg shadow-primary/30">
                تسجيل الدخول
            </button>
        </div>
    </div>

    <!-- 3. التطبيق الأساسي -->
    <div id="app-content" class="hidden">
"""
html = html.replace('<body class="text-gray-800 pb-24">', splash_login)

# ج. تحديث الشريط العلوي (Header)
html = re.sub(
    r'<header.*?</header>', 
    """<header class="bg-primary text-white p-4 shadow-md sticky top-0 z-10 flex justify-between items-center rounded-b-3xl mb-4">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
            </div>
            <h1 id="pharmacy-name" class="text-xl font-bold">جاري التحميل...</h1>
        </div>
        <span id="current-tab-title" class="text-xs bg-white/20 px-3 py-1.5 rounded-full font-medium">الكاشير</span>
    </header>""", 
    html, flags=re.DOTALL
)

# د. تحديث شاشة الإعدادات لتكون مثل تطبيق صرف (List Style)
settings_html = """
        <!-- قسم الإعدادات -->
        <div id="view-settings" class="hidden space-y-6">
            <h2 class="text-xl font-bold text-primary mb-2 px-2">الإعدادات</h2>
            
            <!-- مجموعة الحساب -->
            <div class="bg-card rounded-3xl premium-shadow overflow-hidden">
                <div class="p-4 border-b border-gray-100 flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-bg rounded-full flex items-center justify-center text-primary">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        </div>
                        <div>
                            <p class="font-bold text-sm">مدير النظام</p>
                            <p class="text-xs text-gray-500">admin@kodnaqi.com</p>
                        </div>
                    </div>
                    <span class="text-xs bg-primary/10 text-primary px-2 py-1 rounded-md font-bold">Admin</span>
                </div>
            </div>

            <!-- مجموعة التطبيق -->
            <h3 class="text-sm font-bold text-gray-500 px-2 mt-4">التطبيق</h3>
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

            <!-- زر تسجيل الخروج -->
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
"""
html = re.sub(r'<!-- قسم الإعدادات -->.*?<div id="view-settings".*?</div>\s*</main>', settings_html + '\n    </main>', html, flags=re.DOTALL)

# هـ. تحديث شريط التنقل السفلي (أيقونات SVG احترافية)
new_nav = """
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
"""
html = re.sub(r'<nav.*?</nav>', new_nav, html, flags=re.DOTALL)

# إغلاق الـ div الخاص بالتطبيق الأساسي
html = html.replace('    <script src="/app.js"></script>\n</body>', '    </div> <!-- End App Content -->\n    <script src="/app.js"></script>\n</body>')

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث التصميم (ألوان، أيقونات SVG، شاشة بداية، تسجيل دخول، إعدادات).")

# ==========================================
# 2. تحديث app.js (التحكم في شاشة الدخول والبداية)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

auth_logic = """
// ==================== منطق شاشة البداية والدخول ====================
document.addEventListener('DOMContentLoaded', () => {
    // 1. إخفاء شاشة البداية بعد ثانيتين
    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        if(splash) {
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.display = 'none';
                
                // 2. التحقق من تسجيل الدخول
                if (localStorage.getItem('kodnaqi_auth') === 'true') {
                    showApp();
                } else {
                    document.getElementById('login-screen').classList.remove('hidden');
                    document.getElementById('login-screen').classList.add('flex');
                }
            }, 500);
        }
    }, 2000);
});

function handleLogin() {
    const user = document.getElementById('login-user').value;
    const pass = document.getElementById('login-pass').value;
    
    if (user && pass) {
        localStorage.setItem('kodnaqi_auth', 'true');
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('login-screen').classList.remove('flex');
        showApp();
    }
}

function handleLogout() {
    localStorage.removeItem('kodnaqi_auth');
    window.location.reload();
}

function showApp() {
    document.getElementById('app-content').classList.remove('hidden');
    // تحميل البيانات
    loadSettings();
    loadMedicines();
}
"""

# استبدال حدث DOMContentLoaded القديم بالجديد
js = re.sub(r"document\.addEventListener\('DOMContentLoaded',.*?\);", auth_logic, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js بمنطق الدخول.")
print("\n🎉 اكتمل التحديث الشامل! أعد تشغيل السيرفر واعمل Refresh.")
