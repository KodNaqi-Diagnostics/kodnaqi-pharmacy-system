import os
import re

print("⏳ جاري إعادة زر الطباعة إلى قائمة السجلات...")

with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# دالة عرض السجلات الجديدة مع زر الطباعة
new_render_history = """
function renderHistoryList(sales, list) { 
    if (sales.length === 0) { list.innerHTML = '<p class="text-gray-500 text-center py-4">لا توجد فواتير سابقة.</p>'; return; } 
    list.innerHTML = sales.map(sale => { 
        const date = new Date(sale.sale_date).toLocaleString('en-GB'); 
        const isSynced = !sale.invoice_number.startsWith('OFF-'); 
        return `
            <div class="flex justify-between items-center p-4 border-b border-gray-100 hover:bg-gray-50 transition">
                <div>
                    <p class="font-bold text-primary">${sale.invoice_number} ${!isSynced ? '<span class="text-[9px] text-orange-500 bg-orange-50 px-1 rounded">معلق</span>' : ''}</p>
                    <p class="text-xs text-gray-400 mt-1">${date}</p>
                </div>
                <div class="flex items-center gap-4">
                    <div class="text-left">
                        <p class="font-bold text-primary">${formatCurrency(sale.total_amount || sale.items.reduce((s,i)=>s+(i.unit_price*i.quantity),0))} SDG</p>
                        <p class="text-xs text-gray-400">${sale.items.length} أصناف</p>
                    </div>
                    <!-- زر الطباعة -->
                    <button onclick='reprintInvoice(${JSON.stringify(sale)})' class="bg-blue-50 text-blue-600 p-3 rounded-xl hover:bg-blue-100 transition shadow-sm flex items-center justify-center" title="إعادة طباعة">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
                    </button>
                </div>
            </div>`; 
    }).join(''); 
}
"""

# استبدال الدالة القديمة بالجديدة
js = re.sub(r'function renderHistoryList\(sales, list\) \{.*?\n\}', new_render_history, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم إعادة زر الطباعة بنجاح.")

# كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v53';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v53.")

print("\n🎉 اكتمل التعديل! ارفع الكود الآن.")
