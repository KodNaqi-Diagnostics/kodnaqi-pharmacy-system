import os
import re

print("⏳ جاري إضافة نظام إنشاء الحساب وإصلاح تصميم الموردين...")

# ==========================================
# 1. تحديث الباك-إند (main.py) لإضافة مسار التسجيل
# ==========================================
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# إضافة نموذج التسجيل ومساره
register_endpoint = """
class RegisterIn(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

@app.post("/api/register")
def register(data: RegisterIn):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # التحقق من عدم وجود المستخدم
            cur.execute("SELECT * FROM users WHERE username = %s", (data.username,))
            if cur.fetchone():
                raise HTTPException(400, "اسم المستخدم موجود بالفعل")
            
            hashed_pw = pwd_context.hash(data.password)
            cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) RETURNING id", (data.username, hashed_pw, 'admin'))
            conn.commit()
            return {"status": "success", "message": "تم إنشاء الحساب بنجاح"}

# --- Auth (Login) ---
"""

# إدراج مسار التسجيل قبل مسار الدخول
main_code = main_code.replace("# --- Auth ---", register_endpoint)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
print("✅ تم تحديث main.py (إضافة مسار /api/register).")


# ==========================================
# 2. تحديث الواجهة (index.html) لإصلاح الموردين وشاشة الدخول
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. إصلاح زر الحفظ في الموردين
html = html.replace(
    '<form id="add-supplier-form" class="flex gap-2">',
    '<form id="add-supplier-form" class="flex flex-col md:flex-row gap-3">'
)
html = html.replace(
    '<input type="text" id="sup-name" placeholder="اسم المورد" required class="flex-1 bg-bg rounded-xl p-3 text-sm"><input type="text" id="sup-phone" placeholder="الهاتف" class="flex-1 bg-bg rounded-xl p-3 text-sm"><button type="submit" class="bg-primary text-white px-4 rounded-xl font-bold">حفظ</button>',
    '<input type="text" id="sup-name" placeholder="اسم المورد" required class="flex-1 bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none"><input type="text" id="sup-phone" placeholder="الهاتف" class="flex-1 bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none"><button type="submit" class="bg-primary text-white px-6 py-3 rounded-xl font-bold shadow-lg shadow-primary/30">حفظ</button>'
)

# ب. إعادة تصميم شاشة الدخول لتشمل إنشاء حساب
old_login = re.search(r'<div id="login-screen".*?</div>\s*</div>\s*</div>', html, flags=re.DOTALL)
new_login = """
    <div id="login-screen" class="fixed inset-0 bg-bg z-50 hidden flex-col justify-center p-6 overflow-y-auto">
        <div class="text-center mb-6 mt-10">
            <div class="w-20 h-20 bg-primary rounded-3xl mx-auto flex items-center justify-center mb-4 shadow-xl shadow-primary/30">
                <span class="font-english text-3xl font-bold text-white tracking-widest">KN</span>
            </div>
            <h2 id="auth-title" class="text-2xl font-bold text-primary">مرحباً بك مجدداً</h2>
            <p id="auth-subtitle" class="text-gray-500 text-sm mt-1">سجل الدخول لإدارة صيدليتك</p>
        </div>
        
        <div class="bg-card p-6 rounded-3xl premium-shadow mb-10">
            <!-- نموذج تسجيل الدخول -->
            <div id="login-form-box">
                <div class="mb-4">
                    <label class="block text-sm font-bold text-gray-700 mb-2">اسم المستخدم</label>
                    <input type="text" id="login-user" placeholder="admin" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none">
                </div>
                <div class="mb-6">
                    <label class="block text-sm font-bold text-gray-700 mb-2">كلمة المرور</label>
                    <input type="password" id="login-pass" placeholder="••••••••" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none" dir="ltr">
                </div>
                <button onclick="handleLogin()" class="w-full bg-primary hover:bg-[#073629] text-white py-3.5 rounded-xl font-bold text-lg shadow-lg shadow-primary/30">تسجيل الدخول</button>
            </div>

            <!-- نموذج إنشاء حساب (مخفي افتراضياً) -->
            <div id="register-form-box" class="hidden">
                <div class="mb-3">
                    <label class="block text-sm font-bold text-gray-700 mb-2">اسم المستخدم</label>
                    <input type="text" id="reg-user" placeholder="اسم جديد" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none">
                </div>
                <div class="mb-3">
                    <label class="block text-sm font-bold text-gray-700 mb-2">البريد الإلكتروني (اختياري)</label>
                    <input type="email" id="reg-email" placeholder="email@example.com" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none" dir="ltr">
                </div>
                <div class="mb-3">
                    <label class="block text-sm font-bold text-gray-700 mb-2">كلمة المرور</label>
                    <input type="password" id="reg-pass" placeholder="••••••••" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none" dir="ltr">
                </div>
                <div class="mb-6">
                    <label class="block text-sm font-bold text-gray-700 mb-2">تأكيد كلمة المرور</label>
                    <input type="password" id="reg-pass-confirm" placeholder="••••••••" class="w-full bg-bg border-0 rounded-xl p-3 focus:ring-2 focus:ring-primary outline-none" dir="ltr">
                </div>
                <button onclick="handleRegister()" class="w-full bg-primary hover:bg-[#073629] text-white py-3.5 rounded-xl font-bold text-lg shadow-lg shadow-primary/30">إنشاء الحساب</button>
            </div>

            <div class="mt-4 text-center">
                <button onclick="toggleAuthMode()" id="toggle-auth-btn" class="text-sm text-primary font-bold hover:underline">ليس لديك حساب؟ إنشاء حساب جديد</button>
            </div>
        </div>
    </div>
"""
if old_login:
    html = html.replace(old_login.group(0), new_login)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html (تصميم الموردين وشاشة الدخول).")


# ==========================================
# 3. تحديث الجافاسكريبت (app.js) لدعم التسجيل
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

auth_js = """
let isLoginMode = true;

function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    const loginBox = document.getElementById('login-form-box');
    const regBox = document.getElementById('register-form-box');
    const title = document.getElementById('auth-title');
    const subtitle = document.getElementById('auth-subtitle');
    const toggleBtn = document.getElementById('toggle-auth-btn');

    if (isLoginMode) {
        loginBox.classList.remove('hidden');
        regBox.classList.add('hidden');
        title.innerText = "مرحباً بك مجدداً";
        subtitle.innerText = "سجل الدخول لإدارة صيدليتك";
        toggleBtn.innerText = "ليس لديك حساب؟ إنشاء حساب جديد";
    } else {
        loginBox.classList.add('hidden');
        regBox.classList.remove('hidden');
        title.innerText = "حساب جديد";
        subtitle.innerText = "أنشئ حسابك لإدارة صيدليتك";
        toggleBtn.innerText = "لديك حساب بالفعل؟ تسجيل الدخول";
    }
}

async function handleRegister() {
    const user = document.getElementById('reg-user').value;
    const email = document.getElementById('reg-email').value;
    const pass = document.getElementById('reg-pass').value;
    const confirmPass = document.getElementById('reg-pass-confirm').value;

    if(!user || !pass) return showAlert("تنبيه", "أدخل اسم المستخدم وكلمة المرور", "error");
    if(pass !== confirmPass) return showAlert("خطأ", "كلمتا المرور غير متطابقتين", "error");

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, email: email, password: pass })
        });
        const data = await res.json();
        
        if (res.ok) {
            await showAlert("تم بنجاح", "تم إنشاء الحساب، يمكنك الآن تسجيل الدخول.", "success");
            toggleAuthMode(); // العودة لنموذج الدخول
            document.getElementById('login-user').value = user; // تعبئة اسم المستخدم
        } else {
            showAlert("خطأ", data.detail || "حدث خطأ أثناء إنشاء الحساب", "error");
        }
    } catch (err) {
        showAlert("خطأ", "تعذر الاتصال بالسيرفر", "error");
    }
}
"""

if "function toggleAuthMode()" not in js:
    js = js.replace("async function handleLogin() {", auth_js + "\nasync function handleLogin() {")

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js (منطق التسجيل).")

# 4. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v21';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v21.")

print("\n🎉 اكتمل الإصلاح! أعد تشغيل السيرفر.")
