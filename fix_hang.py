import os
import re

print("⏳ جاري إصلاح التعليق وتحديث الكاش...")

# 1. تحديث شاشة البداية في index.html لتظهر الشعار الجديد
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# استبدال الأيقونة القديمة (المبنى) بالشعار الخاص بك
splash_regex = r'<div id="splash-screen".*?</div>\s*<h1 class="text-white text-2xl font-bold tracking-wider">KodNaqi Pharmacy</h1>'
new_splash = """<div id="splash-screen" class="fixed inset-0 bg-primary z-[100] flex flex-col items-center justify-center transition-opacity duration-500">
        <img src="/logo-pharma.png" alt="KodNaqi Logo" class="w-48 h-48 object-contain mb-4 drop-shadow-2xl">
        <h1 class="text-white text-2xl font-bold tracking-wider">KodNaqi Pharmacy</h1>"""

html = re.sub(splash_regex, new_splash, html, flags=re.DOTALL)
with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم وضع الشعار في شاشة البداية.")


# 2. تحديث ملف sw.js لإجبار المتصفح على تحميل الملفات الجديدة (حل مشكلة 304)
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()

# تغيير اسم الكاش إلى الإصدار الثاني
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v2';", sw)

with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث إصدار الكاش لإجبار المتصفح على التحديث.")


# 3. إصلاح أي أخطاء في app.js قد تسبب التعليق
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# إزالة أي أكواد مكررة أو تالفة من عمليات الاستبدال السابقة
# والتأكد من أن حدث DOMContentLoaded يعمل بشكل سليم
auth_logic = """
// ==================== منطق شاشة البداية والدخول ====================
document.addEventListener('DOMContentLoaded', () => {
    // إخفاء شاشة البداية بعد ثانيتين
    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        if(splash) {
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.display = 'none';
                // التحقق من تسجيل الدخول
                if (localStorage.getItem('kodnaqi_auth') === 'true') {
                    showApp();
                } else {
                    const loginScreen = document.getElementById('login-screen');
                    if(loginScreen) {
                        loginScreen.classList.remove('hidden');
                        loginScreen.classList.add('flex');
                    }
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
        const loginScreen = document.getElementById('login-screen');
        if(loginScreen) {
            loginScreen.classList.add('hidden');
            loginScreen.classList.remove('flex');
        }
        showApp();
    }
}

function handleLogout() {
    localStorage.removeItem('kodnaqi_auth');
    window.location.reload();
}

function showApp() {
    const appContent = document.getElementById('app-content');
    if(appContent) appContent.classList.remove('hidden');
    loadSettings();
    loadMedicines();
}
"""

# استبدال أي حدث DOMContentLoaded قديم بالنسخة النظيفة
js = re.sub(r"// ==================== منطق شاشة البداية والدخول ====================.*?(?=// ====================)", auth_logic + "\n", js, flags=re.DOTALL)
# إذا لم يجد العلامة، يبحث عن الحدث العادي
js = re.sub(r"document\.addEventListener\('DOMContentLoaded',.*?\);", auth_logic, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم إصلاح كود app.js.")

print("\n🎉 اكتمل الإصلاح! اتبع خطوات التحديث بدقة.")
