import os
import re

print("⏳ جاري إصلاح شاشة البداية وإضافة خط إنجليزي احترافي...")

# ==========================================
# 1. تحديث index.html
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. إضافة خط Poppins للإنجليزية في الـ Head
if 'Poppins' not in html:
    html = html.replace(
        '<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">',
        '<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Poppins:wght@600;700&display=swap" rel="stylesheet">'
    )

# ب. تحديث إعدادات Tailwind لتعريف الخط الإنجليزي
if 'fontFamily: { sans:' in html:
    html = html.replace(
        "fontFamily: { sans: ['Tajawal', 'sans-serif'] },",
        "fontFamily: { sans: ['Tajawal', 'sans-serif'], english: ['Poppins', 'sans-serif'] },"
    )

# ج. تطبيق الخط الإنجليزي على اسم الصيدلية في شاشة البداية
html = html.replace(
    '<h1 class="text-white text-2xl font-bold tracking-wider">KodNaqi Pharmacy</h1>',
    '<h1 class="text-white text-3xl font-bold tracking-widest font-english mt-2">KodNaqi Pharmacy</h1>'
)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html وإضافة الخط الإنجليزي.")

# ==========================================
# 2. إصلاح جذري لملف app.js
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# سنقوم بحذف أي حدث DOMContentLoaded قديم (تالف) وكتابة واحد جديد نظيف
# حذف كل ما يتعلق بـ DOMContentLoaded
js = re.sub(r"document\.addEventListener\('DOMContentLoaded'.*?\}\);", "", js, flags=re.DOTALL)

# كتابة كود التهيئة الجديد والنظيف في نهاية الملف
clean_init = """

// ==================== التهيئة النظيفة (إصلاح التعليق) ====================
window.addEventListener('load', () => {
    console.log("🚀 App Loaded successfully");
    
    // 1. إخفاء شاشة البداية دائماً بعد ثانيتين ونصف (حتى لو حدث خطأ)
    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        if (splash) {
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.display = 'none';
                
                // 2. التحقق من الدخول
                if (localStorage.getItem('kodnaqi_auth') === 'true') {
                    showApp();
                } else {
                    const login = document.getElementById('login-screen');
                    if(login) {
                        login.classList.remove('hidden');
                        login.classList.add('flex');
                    }
                }
            }, 400);
        }
    }, 2000);
});

function handleLogin() {
    const user = document.getElementById('login-user')?.value;
    const pass = document.getElementById('login-pass')?.value;
    
    if (user && pass) {
        localStorage.setItem('kodnaqi_auth', 'true');
        const login = document.getElementById('login-screen');
        if(login) {
            login.classList.add('hidden');
            login.classList.remove('flex');
        }
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
    
    // جلب البيانات بأمان (بدون إيقاف التطبيق إذا فشل الاتصال)
    if (typeof loadSettings === 'function') loadSettings();
    if (typeof loadMedicines === 'function') loadMedicines();
}
"""

js += clean_init

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم إصلاح كود app.js بنجاح (لن يعلق بعد الآن).")

# ==========================================
# 3. تحديث إصدار الكاش في sw.js (لإجبار التحديث)
# ==========================================
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()

# تغيير رقم الإصدار إلى v3
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v3';", sw)

with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث إصدار الكاش إلى v3.")

print("\n🎉 اكتمل الإصلاح! اتبع خطوات التحديث أدناه بدقة.")
