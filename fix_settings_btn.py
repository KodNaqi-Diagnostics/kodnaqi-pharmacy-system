import os
import re

print("⏳ جاري إعادة زر الإعدادات إلى شريط التنقل...")

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. إضافة زر الإعدادات قبل إغلاق الـ nav
settings_btn = """
            <button onclick="switchTab('settings')" id="btn-settings" class="flex flex-col items-center p-2 text-gray-400 min-w-[60px] transition-all">
                <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                <span class="text-[10px] font-bold">الإعدادات</span>
            </button>
        </nav>
"""

if 'id="btn-settings"' not in html:
    html = html.replace('</nav>', settings_btn)
else:
    print("⚠️ زر الإعدادات موجود بالفعل.")

# التأكد من أن شريط التنقل يدعم السحب (Scroll) لأن الأزرار كثيرة
html = html.replace(
    'class="fixed bottom-0 w-full bg-white border-t flex justify-around py-2 z-20 rounded-t-3xl pb-4 shadow-[0_-4px_20px_rgba(0,0,0,0.04)] overflow-x-auto"',
    'class="fixed bottom-0 w-full bg-white border-t flex overflow-x-auto py-2 z-20 rounded-t-3xl pb-4 shadow-[0_-4px_20px_rgba(0,0,0,0.04)] [&::-webkit-scrollbar]:hidden [-ms-overflow-style:\'none\'] [scrollbar-width:\'none\']"'
)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم إعادة زر الإعدادات وجعل الشريط قابلاً للسحب.")

# كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v32';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v32.")
