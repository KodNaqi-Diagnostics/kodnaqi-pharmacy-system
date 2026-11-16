import os
import re

print("⏳ جاري ترتيب القائمة وتنسيق الأرقام بالفواصل...")

# ==========================================
# 1. ترتيب شريط التنقل في index.html
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# استخراج زر الرئيسية من مكانه الحالي
dash_btn_pattern = r'<button onclick="switchTab\(\'dashboard\'\)".*?</button>'
dash_btn_match = re.search(dash_btn_pattern, html, flags=re.DOTALL)

if dash_btn_match:
    dash_btn_html = dash_btn_match.group(0)
    # حذفه من مكانه الحالي
    html = html.replace(dash_btn_html, "")
    # إضافته في بداية الـ nav
    html = html.replace('<nav class="fixed bottom-0 w-full', dash_btn_html + '\n        <nav class="fixed bottom-0 w-full')

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم نقل زر (الرئيسية) إلى أقصى اليمين في شريط التنقل.")


# ==========================================
# 2. تنسيق الأرقام بالفواصل في app.js
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# دالة مساعدة لتنسيق الأرقام
if 'function formatCurrency' not in js:
    js = js.replace("const API_URL = \"/api\";", "const API_URL = \"/api\";\nfunction formatCurrency(num) { return Number(num).toLocaleString('en-US'); }")

# أ. لوحة التحكم
js = js.replace(
    "document.getElementById('stat-revenue').innerText = `${data.today_revenue} SDG`;",
    "document.getElementById('stat-revenue').innerText = `${formatCurrency(data.today_revenue)} SDG`;"
)
js = js.replace(
    "document.getElementById('stat-profit').innerText = `${data.today_profit} SDG`;",
    "document.getElementById('stat-profit').innerText = `${formatCurrency(data.today_profit)} SDG`;"
)

# ب. الكاشير (الفاتورة)
js = js.replace(
    "<span class=\"font-bold text-primary w-16 text-left\">${item.unit_price * item.quantity} SDG</span>",
    "<span class=\"font-bold text-primary w-20 text-left\">${formatCurrency(item.unit_price * item.quantity)} SDG</span>"
)
js = js.replace(
    "totalEl.innerText = `${total} SDG`;",
    "totalEl.innerText = `${formatCurrency(total)} SDG`;"
)
js = js.replace(
    "const paid = await showPrompt(\"الدفع\", `الإجمالي المطلوب: ${total} SDG`, total);",
    "const paid = await showPrompt(\"الدفع\", `الإجمالي المطلوب: ${formatCurrency(total)} SDG`, total);"
)
js = js.replace(
    "`الباقي: <b class=\"text-primary text-lg\">${change} SDG</b>`",
    "`الباقي: <b class=\"text-primary text-lg\">${formatCurrency(change)} SDG</b>`"
)

# ج. الطباعة
js = js.replace(
    "document.getElementById('print-total').innerText = `${total} SDG`;",
    "document.getElementById('print-total').innerText = `${formatCurrency(total)} SDG`;"
)
js = js.replace(
    "document.getElementById('print-paid').innerText = `${paid} SDG`;",
    "document.getElementById('print-paid').innerText = `${formatCurrency(paid)} SDG`;"
)
js = js.replace(
    "document.getElementById('print-change').innerText = `${change} SDG`;",
    "document.getElementById('print-change').innerText = `${formatCurrency(change)} SDG`;"
)
js = js.replace(
    "<td class=\"py-2 text-left\">${item.unit_price}</td><td class=\"py-2 text-left\">${item.unit_price * item.quantity}</td>",
    "<td class=\"py-2 text-left\">${formatCurrency(item.unit_price)}</td><td class=\"py-2 text-left\">${formatCurrency(item.unit_price * item.quantity)}</td>"
)

# د. السجلات
js = js.replace(
    "<p class=\"font-bold text-primary\">${sale.total_amount} SDG</p>",
    "<p class=\"font-bold text-primary\">${formatCurrency(sale.total_amount)} SDG</p>"
)

# هـ. قائمة الأدوية (الكاشير والمخزون)
js = js.replace(
    "<p class=\"font-bold text-primary\">${med.price} SDG</p>",
    "<p class=\"font-bold text-primary\">${formatCurrency(med.price)} SDG</p>"
)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تطبيق الفواصل العشرية (,) على جميع الأرقام في النظام.")


# ==========================================
# 3. كسر الكاش لتحميل التحديثات
# ==========================================
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = sw.replace("const CACHE_NAME = 'kodnaqi-v8';", "const CACHE_NAME = 'kodnaqi-v9';")
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v9.")

print("\n🎉 اكتملت اللمسات النهائية! أعد تشغيل السيرفر.")
