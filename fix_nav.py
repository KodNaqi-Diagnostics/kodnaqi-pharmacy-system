import os
import re

print("⏳ جاري تصحيح مكان زر (الرئيسية)...")

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. استخراج كود زر الرئيسية
dash_btn_pattern = r'<button onclick="switchTab\(\'dashboard\'\)".*?</button>'
dash_btn_match = re.search(dash_btn_pattern, html, flags=re.DOTALL)

if dash_btn_match:
    dash_btn_html = dash_btn_match.group(0)
    
    # إزالته من مكانه الحالي (الطائر في الهواء)
    html = html.replace(dash_btn_html, "")
    
    # التأكد من أن الزر يحمل كلاسات الأزرار الأخرى (w-1/5)
    dash_btn_html = dash_btn_html.replace('w-1/5', 'w-1/5') 
    
    # إضافته داخل الـ nav مباشرة (كأول زر من اليمين)
    html = html.replace(
        '<nav class="fixed bottom-0 w-full bg-white border-t border-gray-100 flex justify-around py-2 px-1 z-20 shadow-[0_-4px_20px_rgba(0,0,0,0.04)] rounded-t-3xl pb-4">',
        '<nav class="fixed bottom-0 w-full bg-white border-t border-gray-100 flex justify-around py-2 px-1 z-20 shadow-[0_-4px_20px_rgba(0,0,0,0.04)] rounded-t-3xl pb-4">\n            ' + dash_btn_html
    )

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم وضع الزر في مكانه الصحيح داخل شريط التنقل.")

# كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v9';", "const CACHE_NAME = 'kodnaqi-v10';")
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v10.")
