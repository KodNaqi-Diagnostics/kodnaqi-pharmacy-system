import re

print("⏳ جاري إصلاح مشكلة الطباعة في السجلات...")

with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# استبدال دالة إعادة الطباعة القديمة بدالة جديدة تفتح الطباعة مباشرة
new_reprint = """function reprintInvoice(sale) {
    const items = sale.items.map(i => ({
        name: i.name,
        quantity: i.quantity,
        unit_price: i.unit_price
    }));
    
    const total = sale.total_amount;
    const paid = sale.paid_amount;
    const change = paid - total;
    
    // 1. تجهيز الفاتورة والباركود
    preparePrintInvoice(sale.invoice_number, items, total, paid, change);
    
    // 2. إعطاء المتصفح نصف ثانية لرسم الباركود ثم فتح نافذة الطباعة فوراً
    setTimeout(() => {
        window.print();
    }, 500);
}"""

js = re.sub(r'function reprintInvoice\(sale\) \{.*?\n\}', new_reprint, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)

print("✅ تم إصلاح زر الطباعة بنجاح!")
