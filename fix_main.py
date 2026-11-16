import os

if not os.path.exists("main.py"):
    print("❌ لم يتم العثور على main.py")
else:
    with open("main.py", "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open("main.py", "w", encoding="utf-8") as f:
        for line in lines:
            # حذف السطر المكسور الذي يحتوي على القوس الزائد
            if line.strip() == ', name="static")':
                continue
            f.write(line)
    
    print("✅ تم إصلاح ملف main.py بنجاح!")
