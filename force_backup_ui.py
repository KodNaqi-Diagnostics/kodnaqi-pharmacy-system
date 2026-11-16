import os

print("⏳ جاري إجبار إضافة أزرار النسخ الاحتياطي...")

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

backup_ui = """
                <!-- النسخ الاحتياطي -->
                <h3 class="text-sm font-bold text-gray-500 px-2 mt-6">النسخ الاحتياطي والبيانات</h3>
                <div class="bg-card rounded-3xl premium-shadow overflow-hidden mb-4">
                    <a href="/api/backup/database" download class="p-4 flex items-center justify-between border-b border-gray-100 hover:bg-gray-50 transition text-gray-700">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4zm0 5c0 2.21 3.582 4 8 4s8-1.79 8-4"></path></svg>
                            </div>
                            <span class="font-bold text-sm">تحميل قاعدة البيانات (SQLite)</span>
                        </div>
                        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    </a>
                    
                    <a href="/api/backup/sales-csv" download class="p-4 flex items-center justify-between hover:bg-gray-50 transition text-gray-700">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-green-50 rounded-full flex items-center justify-center text-green-600">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                            </div>
                            <span class="font-bold text-sm">تصدير المبيعات (Excel / CSV)</span>
                        </div>
                        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    </a>
                </div>
"""

# سنجد زر تسجيل الخروج (الذي يحتوي على كلاس mt-4) ونضع الأزرار قبله مباشرة
target_div = '<div class="bg-card rounded-3xl premium-shadow overflow-hidden mt-4">'

if target_div in html:
    if '/api/backup/database' not in html:
        html = html.replace(target_div, backup_ui + '\n                ' + target_div)
        print("✅ تمت إضافة الأزرار بنجاح.")
    else:
        print("⚠️ الأزرار موجودة بالفعل في الكود.")
else:
    print("❌ لم يتم العثور على مكان زر الخروج. يرجى إخباري.")

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)

# كسر الكاش لتحميل التحديث
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v11';", "const CACHE_NAME = 'kodnaqi-v12';")
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v10';", "const CACHE_NAME = 'kodnaqi-v12';") # احتياط
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v12.")
