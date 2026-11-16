print("⏳ جاري إصلاح توقيت إعادة طباعة الفواتير...")

with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. تحديث دالة تجهيز الطباعة لتقبل تاريخاً اختيارياً
old_prep = """function preparePrintInvoice(invNum, items, total, paid, change) {
    document.getElementById('print-pharmacy-name').innerText = document.getElementById('pharmacy-name').innerText;
    const now = new Date();
    document.getElementById('print-date').innerText = `التاريخ: ${now.toLocaleDateString('en-GB')} ${now.toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit'})}`;"""

new_prep = """function preparePrintInvoice(invNum, items, total, paid, change, originalDate = null) {
    document.getElementById('print-pharmacy-name').innerText = document.getElementById('pharmacy-name').innerText;
    
    // إذا كان هناك تاريخ أصلي (من السجلات) استخدمه، وإلا استخدم الوقت الحالي
    let printDate;
    if (originalDate) {
        printDate = new Date(originalDate);
    } else {
        printDate = new Date();
    }
    
    document.getElementById('print-date').innerText = `التاريخ: ${printDate.toLocaleDateString('en-GB')} ${printDate.toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit'})}`;"""

js = js.replace(old_prep, new_prep)

# 2. تحديث دالة إعادة الطباعة لتمرير تاريخ الفاتورة الأصلي
js = js.replace(
    "preparePrintInvoice(sale.invoice_number, items, total, paid, change);",
    "preparePrintInvoice(sale.invoice_number, items, total, paid, change, sale.sale_date);"
)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)

print("✅ تم إصلاح التوقيت بنجاح!")
