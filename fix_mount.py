import os

print("⏳ جاري إصلاح السطر التالف (app.mount) نهائياً...")

with open("main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
# 1. حذف أي سطر يحتوي على app.mount أو name="static" لأنه تالف
for line in lines:
    if 'app.mount' in line or ', name="static")' in line:
        continue # تخطي هذا السطر
    new_lines.append(line)

# 2. التأكد من وجود استدعاء StaticFiles في الأعلى
main_content = "".join(new_lines)
if "from fastapi.staticfiles import StaticFiles" not in main_content:
    main_content = main_content.replace("from fastapi import FastAPI", "from fastapi import FastAPI\nfrom fastapi.staticfiles import StaticFiles")

# 3. إضافة السطر الصحيح في نهاية الملف
final_code = main_content.strip() + '\n\n# تقديم ملفات الواجهة الأمامية (PWA)\napp.mount("/", StaticFiles(directory="static", html=True), name="static")\n'

with open("main.py", "w", encoding="utf-8") as f:
    f.write(final_code)

print("✅ تم إصلاح main.py بنجاح! السطر التالف تمت إزالته وكتابة السطر الصحيح.")
