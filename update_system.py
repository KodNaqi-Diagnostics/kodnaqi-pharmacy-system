import os
import re

print("⏳ جاري تحديث ملف main.py لإضافة ميزة السجلات...")
# 1. تحديث main.py لإضافة مسار جلب الفواتير السابقة
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

sales_endpoint = """
# ==================== Sales History ====================
@app.get("/api/sales")
def get_sales_history():
    with get_db() as db:
        sales = db.execute("SELECT * FROM sales ORDER BY id DESC LIMIT 100").fetchall()
        result = []
        for sale in sales:
            items = db.execute('''
                SELECT si.*, m.name 
                FROM sale_items si 
                JOIN medicines m ON si.medicine_id = m.id 
                WHERE si.sale_id = ?
            ''', (sale['id'],)).fetchall()
            sale_dict = dict(sale)
            sale_dict['items'] = [dict(i) for i in items]
            result.append(sale_dict)
        return result

# تقديم ملفات الواجهة الأمامية (PWA)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
"""

# استبدال السطر الأخير (app.mount) بالكود الجديد
if 'app.mount' in main_code:
    main_code = re.sub(r'# تقديم ملفات الواجهة الأمامية \(PWA\)\s*app\.mount\([^)]+\)', sales_endpoint, main_code)
else:
    main_code += sales_endpoint

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
print("✅ تم تحديث main.py")


print("⏳ جاري تحديث index.html (الباركود، السجلات، وتوسيط الطباعة)...")
# 2. تحديث index.html
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. إضافة مكتبة JsBarcode وتوسيط الطباعة في الـ head
head_addition = """
    <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
    <style>
        @media print {
            body > * { display: none !important; }
            #print-area {
                display: block !important;
                margin: 0 auto !important; /* التوسيط */
                padding: 10px;
                width: 100%;
                max-width: 80mm;
                color: #000 !important;
                background: #fff !important;
            }
            #app-modal { display: none !important; }
            @page { margin: 5mm; } /* هوامش بسيطة للتوسيط */
        }
    </style>
</head>"""
html = html.replace("</head>", head_addition)

# ب. إضافة زر السجلات في شريط التنقل السفلي
nav_addition = """
        <button onclick="switchTab('history')" id="btn-history" class="flex flex-col items-center p-2 text-gray-400 hover:text-emerald-600 w-1/4"><span class="text-2xl">📋</span><span class="text-xs font-bold mt-1">السجلات</span></button>
    </nav>"""
html = html.replace("</nav>", nav_addition)
# تعديل عرض الأزرار لتكون 4 أزرار
html = html.replace('w-1/3"><span class="text-2xl">🛒', 'w-1/4"><span class="text-2xl">🛒')
html = html.replace('w-1/3"><span class="text-2xl">📦', 'w-1/4"><span class="text-2xl">📦')
html = html.replace('w-1/3"><span class="text-2xl">⚙️', 'w-1/4"><span class="text-2xl">⚙️')

# ج. إضافة قسم السجلات (History View) قبل نهاية main
history_view = """
        <!-- قسم السجلات -->
        <div id="view-history" class="hidden space-y-6">
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h2 class="text-lg font-semibold mb-4 text-emerald-800">📋 سجل الفواتير السابقة</h2>
                <div id="history-list" class="space-y-2">
                    <p class="text-gray-500 text-center">جاري التحميل...</p>
                </div>
            </div>
        </div>
    </main>"""
html = html.replace("</main>", history_view)

# د. استبدال الختم والتوقيع بباركود في الفاتورة
old_footer = re.search(r'<div class="flex justify-between items-end mt-8 text-xs text-center">.*?</div>\s*</div>', html, re.DOTALL)
new_footer = """
        <div class="flex flex-col items-center mt-6">
            <svg id="print-barcode" class="w-full max-w-[200px]"></svg>
            <p class="text-xs mt-1 font-mono" id="print-inv-text">INV-123</p>
        </div>
    </div>"""
if old_footer:
    html = html.replace(old_footer.group(0), new_footer)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html")


print("⏳ جاري تحديث app.js (الباركود والسجلات)...")
# 3. تحديث app.js
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# أ. تحديث دالة preparePrintInvoice لتوليد الباركود
js = js.replace(
    'document.getElementById(\'print-change\').innerText = `${change} SDG`;',
    '''document.getElementById('print-change').innerText = `${change} SDG`;
    // توليد الباركود
    JsBarcode("#print-barcode", invNum, { format: "CODE128", lineColor: "#000", width: 2, height: 40, displayValue: false });
    document.getElementById('print-inv-text').innerText = invNum;'''
)

# ب. تحديث دالة switchTab لدعم قسم السجلات
js = js.replace(
    "document.getElementById('view-settings').classList.add('hidden');",
    "document.getElementById('view-settings').classList.add('hidden');\n    document.getElementById('view-history').classList.add('hidden');"
)
js = js.replace(
    "document.getElementById('btn-settings').className = \"flex flex-col items-center p-2 text-gray-400 hover:text-emerald-600 w-1/3\";",
    "document.getElementById('btn-settings').className = \"flex flex-col items-center p-2 text-gray-400 hover:text-emerald-600 w-1/4\";\n    document.getElementById('btn-history').className = \"flex flex-col items-center p-2 text-gray-400 hover:text-emerald-600 w-1/4\";"
)
js = js.replace(
    "document.getElementById(`btn-${tabId}`).className = \"flex flex-col items-center p-2 text-emerald-600 w-1/3\";",
    "document.getElementById(`btn-${tabId}`).className = \"flex flex-col items-center p-2 text-emerald-600 w-1/4\";"
)
js = js.replace(
    "const titles = { pos: 'الكاشير', inventory: 'المخزون', settings: 'الإعدادات' };",
    "const titles = { pos: 'الكاشير', inventory: 'المخزون', settings: 'الإعدادات', history: 'السجلات' };"
)
js = js.replace(
    "if (tabId === 'inventory') loadMedicines();",
    "if (tabId === 'inventory') loadMedicines();\n    if (tabId === 'history') loadHistory();"
)

# ج. إضافة دوال السجلات وإعادة الطباعة
history_functions = """
// ==================== سجل الفواتير ====================
async function loadHistory() {
    try {
        const res = await fetch(`${API_URL}/sales`);
        const sales = await res.json();
        const list = document.getElementById('history-list');
        
        if (sales.length === 0) {
            list.innerHTML = '<p class="text-gray-500 text-center">لا توجد فواتير سابقة.</p>';
            return;
        }

        list.innerHTML = sales.map(sale => {
            const date = new Date(sale.sale_date).toLocaleString('en-GB');
            return `
                <div class="flex justify-between items-center p-3 border-b border-gray-100 hover:bg-gray-50">
                    <div>
                        <p class="font-bold text-gray-800">${sale.invoice_number}</p>
                        <p class="text-xs text-gray-500">${date}</p>
                    </div>
                    <div class="text-left flex items-center gap-4">
                        <div>
                            <p class="font-bold text-emerald-600">${sale.total_amount} SDG</p>
                            <p class="text-xs text-gray-500">${sale.items.length} أصناف</p>
                        </div>
                        <button onclick='reprintInvoice(${JSON.stringify(sale)})' class="bg-blue-100 text-blue-700 p-2 rounded hover:bg-blue-200 transition">
                            🖨️ طباعة
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) { console.error(err); }
}

function reprintInvoice(sale) {
    const items = sale.items.map(i => ({
        name: i.name,
        quantity: i.quantity,
        unit_price: i.unit_price
    }));
    
    const total = sale.total_amount;
    const paid = sale.paid_amount;
    const change = paid - total;
    
    preparePrintInvoice(sale.invoice_number, items, total, paid, change);
    showAlert("جاهز للطباعة", "تم تجهيز الفاتورة، اضغط على زر الطباعة بالأسفل.", "success")
    .then(() => {
        // إضافة زر طباعة سريع في الرسالة
        document.getElementById('modal-message').innerHTML += `<br><br><button onclick="window.print()" class="mt-2 bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 w-full">🖨️ طباعة الآن</button>`;
    });
}

document.addEventListener('DOMContentLoaded', () => { loadSettings(); loadMedicines(); });
"""
js = js.replace("document.addEventListener('DOMContentLoaded', () => { loadSettings(); loadMedicines(); });", history_functions)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js")

print("🎉 اكتمل التحديث بنجاح! يرجى إعادة تشغيل السيرفر.")
