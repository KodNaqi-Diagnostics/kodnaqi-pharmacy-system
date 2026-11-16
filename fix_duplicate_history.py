import os
import re

print("⏳ جاري إصلاح مشكلة تكرار الفواتير عند المزامنة...")

with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. تحديث دالة processOutbox لتحديث الفاتورة المحلية بدلاً من تركها
new_process_outbox = """
async function processOutbox() {
    if(!navigator.onLine) return; 
    
    let outbox = await localforage.getItem('kodnaqi_outbox') || [];
    if(outbox.length === 0) return;

    let sales = await localforage.getItem('kodnaqi_sales') || [];
    let outboxChanged = false;

    for (let i = 0; i < outbox.length; i++) {
        let sale = outbox[i];
        let sendData = { discount: sale.discount, paid_amount: sale.paid_amount, items: sale.items.map(item => ({ medicine_id: item.medicine_id, quantity: item.quantity, unit_price: item.unit_price })) };
        
        try {
            let res = await fetch(`${API_URL}/sales`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sendData) });
            if (res.ok) {
                let serverData = await res.json();
                
                // تحديث الفاتورة المحلية بالرقم الجديد القادم من السيرفر
                let localSaleIndex = sales.findIndex(s => s.id == sale.id);
                if (localSaleIndex !== -1) {
                    sales[localSaleIndex].invoice_number = serverData.invoice_number;
                }
                
                outbox.splice(i, 1);
                i--;
                outboxChanged = true;
            } else { break; }
        } catch(e) { break; }
    }
    
    if (outboxChanged) {
        await localforage.setItem('kodnaqi_sales', sales);
        await localforage.setItem('kodnaqi_outbox', outbox);
    }
}
"""
js = re.sub(r'async function processOutbox\(\) \{.*?\n\}', new_process_outbox, js, flags=re.DOTALL)

# 2. تحديث دالة loadHistory لتمنع تكرار الفواتير عند الدمج
new_load_history = """
async function loadHistory() {
    const list = document.getElementById('history-list');
    if (!list) return;
    
    // 1. جلب الفواتير المحلية
    let localSales = await localforage.getItem('kodnaqi_sales') || [];
    
    // 2. جلب الفواتير من السيرفر
    try {
        const res = await fetch(`${API_URL}/sales`);
        if(res.ok) {
            const serverSales = await res.json();
            
            // دمج الفواتير: نتجنب التكرار عن طريق مطابقة رقم الفاتورة
            let mergedSales = [...localSales];
            serverSales.forEach(ss => {
                // إذا كانت الفاتورة موجودة محلياً (رقم INV)، نحدث بياناتها
                let existingIndex = mergedSales.findIndex(s => s.invoice_number === ss.invoice_number);
                if(existingIndex !== -1) {
                    mergedSales[existingIndex] = { ...mergedSales[existingIndex], ...ss };
                } else {
                    // إذا لم تكن موجودة، نضيفها
                    mergedSales.push(ss);
                }
            });

            // ترتيب الفواتير من الأحدث للأقدم
            mergedSales.sort((a,b) => new Date(b.sale_date) - new Date(a.sale_date));
            
            // حفظ النسخة المدمجة في الهاتف
            await localforage.setItem('kodnaqi_sales', mergedSales);
            renderHistoryList(mergedSales, list);
        } else {
            renderHistoryList(localSales, list);
        }
    } catch(e) { 
        renderHistoryList(localSales, list);
    }
}
"""
js = re.sub(r'async function loadHistory\(\) \{.*?\n\}', new_load_history, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم إصلاح كود المزامنة وعرض السجلات.")
