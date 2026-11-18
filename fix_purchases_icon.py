import os
import re

print("⏳ جاري استبدال أيقونة المشتريات بأيقونة شاحنة...")

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# البحث عن زر المشتريات واستبدال الأيقونة القديمة بأيقونة شاحنة توصيل
old_icon = r'<button onclick="switchTab\(\'purchases\'\)" id="btn-purchases".*?</button>'
new_icon = '''<button onclick="switchTab('purchases')" id="btn-purchases" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary min-w-[70px] transition-all">
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"></path>
            </svg>
            <span class="text-[10px] font-bold">المشتريات</span>
        </button>'''

if re.search(old_icon, html, flags=re.DOTALL):
    html = re.sub(old_icon, new_icon, html, flags=re.DOTALL)
    print("✅ تم تغيير الأيقونة إلى شاحنة بنجاح.")
else:
    print("⚠️ لم يتم العثور على أيقونة المشتريات القديمة، قد تكون تغيرت.")

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)

# كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v50';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v50.")
