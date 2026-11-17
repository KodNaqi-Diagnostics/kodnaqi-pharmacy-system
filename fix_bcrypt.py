import os

print("⏳ جاري إصلاح تعارض مكتبة bcrypt...")

# تحديث ملف requirements.txt لتثبيت إصدار متوافق
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("fastapi\nuvicorn[standard]\npsycopg2-binary\npasslib[bcrypt]\nbcrypt==4.0.1\n")

print("✅ تم تحديث requirements.txt لتثبيت bcrypt==4.0.1")
