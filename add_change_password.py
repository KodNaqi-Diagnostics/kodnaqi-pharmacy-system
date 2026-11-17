import os
import re

print("⏳ جاري إضافة ميزة تغيير كلمة المرور...")

# ==========================================
# 1. تحديث الباك-إند (main.py)
# ==========================================
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# إضافة نموذج تغيير كلمة المرور ومساره
pwd_endpoint = """
class PasswordChangeIn(BaseModel):
    old_password: str
    new_password: str

@app.put("/api/users/me/password")
def change_password(data: PasswordChangeIn, user: dict = Depends(get_current_user)):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # التحقق من كلمة المرور القديمة
            if not pwd_context.verify(data.old_password, user['password_hash']):
                raise HTTPException(400, "كلمة المرور الحالية غير صحيحة")
            
            # تحديث كلمة المرور
            new_hash = pwd_context.hash(data.new_password)
            cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user['id']))
            conn.commit()
            return {"status": "success", "message": "تم تغيير كلمة المرور بنجاح"}

# --- Users ---
"""
main_code = main_code.replace("# --- Users ---", pwd_endpoint)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
print("✅ تم تحديث main.py (إضافة مسار تغيير كلمة المرور).")

# ==========================================
# 2. تحديث الواجهة (index.html)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# إضافة نموذج تغيير كلمة المرور في تبويب الإعدادات
pwd_ui = """
                <div class="bg-card rounded-3xl premium-shadow overflow-hidden mt-4 mb-4">
                    <div class="p-4 border-b border-gray-100">
                        <h3 class="font-bold text-primary flex items-center gap-2">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path></svg>
                            تغيير كلمة المرور
                        </h3>
                    </div>
                    <form id="change-password-form" class="p-4 space-y-3">
                        <input type="password" id="old-password" placeholder="كلمة المرور الحالية" required class="w-full bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none" dir="ltr">
                        <input type="password" id="new-password" placeholder="كلمة المرور الجديدة" required class="w-full bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none" dir="ltr">
                        <button type="submit" class="w-full bg-blue-50 text-blue-600 py-3 rounded-xl font-bold">تحديث كلمة المرور</button>
                    </form>
                </div>
"""
# إدخال النموذج قبل زر تسجيل الخروج
if 'change-password-form' not in html:
    html = html.replace(
        '<div class="bg-card rounded-3xl premium-shadow overflow-hidden mt-4"><button onclick="handleLogout()"',
        pwd_ui + '\n                <div class="bg-card rounded-3xl premium-shadow overflow-hidden mt-4"><button onclick="handleLogout()"'
    )

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html (إضافة نموذج تغيير كلمة المرور).")

# ==========================================
# 3. تحديث الجافاسكريبت (app.js)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

pwd_js = """
document.getElementById('change-password-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const oldPass = document.getElementById('old-password').value;
    const newPass = document.getElementById('new-password').value;
    
    try {
        const res = await apiFetch(`${API_URL}/users/me/password`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ old_password: oldPass, new_password: newPass })
        });
        const data = await res.json();
        
        if (res.ok) {
            await showAlert("تم بنجاح", "تم تغيير كلمة المرور بنجاح. يرجى استخدام الكلمة الجديدة في المرة القادمة.", "success");
            document.getElementById('change-password-form').reset();
        } else {
            showAlert("خطأ", data.detail || "حدث خطأ أثناء التغيير", "error");
        }
    } catch (err) {
        showAlert("خطأ", "تعذر الاتصال بالسيرفر", "error");
    }
});
"""
# إضافة الحدث في نهاية الملف
if 'change-password-form' not in js:
    js += "\n" + pwd_js

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js (منطق تغيير كلمة المرور).")

# 4. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v31';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v31.")

print("\n🎉 اكتمل التحديث! ارفع الكود الآن.")
