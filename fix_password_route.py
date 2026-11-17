import os
import re

print("⏳ جاري إضافة مسار تغيير كلمة المرور بشكل مضمون...")

with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# إذا كان المسار موجوداً مسبقاً، نقوم بإزالته لتجنب التكرار
main_code = re.sub(r'class PasswordChangeIn\(BaseModel\):.*?(?=from fastapi\.staticfiles)', '', main_code, flags=re.DOTALL)

# الكود الجديد الذي سيتم حقنه
password_endpoint = '''
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

'''

# حقن الكود قبل سطر تحميل ملفات الواجهة (StaticFiles)
if 'from fastapi.staticfiles import StaticFiles' in main_code:
    main_code = main_code.replace(
        'from fastapi.staticfiles import StaticFiles',
        password_endpoint + 'from fastapi.staticfiles import StaticFiles'
    )
    print("✅ تمت إضافة مسار تغيير كلمة المرور بنجاح.")
else:
    print("❌ لم يتم العثور على نهاية الملف الصحيحة.")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)

# كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v33';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v33.")
