import os
import re

print("⏳ جاري ترقية النظام (تصنيفات، بحث، كميات، وأيقونة الدخول)...")

# ==========================================
# 1. تحديث main.py (تحديث نموذج البيانات)
# ==========================================
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# تحديث MedicineIn ليشمل الحقول الجديدة بوضوح
new_model = """
class MedicineIn(BaseModel):
    barcode: Optional[str] = None
    name: str # الاسم التجاري
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    price: float = 0
    cost: float = 0
    stock_quantity: int = 0
    expiry_date: Optional[str] = None
    batch_number: Optional[str] = None
    supplier_id: Optional[int] = None
"""
main_code = re.sub(r'class MedicineIn\(BaseModel\):.*?(?=class SettingsIn)', new_model + "\n\n", main_code, flags=re.DOTALL)

# تحديث دالة البحث لتشمل الاسم العلمي والتصنيف
search_logic = """
        if q:
            rows = db.execute(
                "SELECT * FROM medicines WHERE name LIKE ? OR scientific_name LIKE ? OR barcode LIKE ? "
                "ORDER BY name LIMIT ? OFFSET ?",
                (f"%{q}%", f"%{q}%", f"%{q}%", limit, offset),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM medicines ORDER BY name LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()
"""
main_code = re.sub(r'        if q:\n            rows = db\.execute\(.*?\n        else:\n            rows = db\.execute\(.*?\n            \)\.fetchall\(\)', search_logic, main_code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
print("✅ تم تحديث main.py (قاعدة البيانات والبحث).")


# ==========================================
# 2. تحديث index.html (الواجهة)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# أ. تغيير أيقونة الدخول إلى KN
login_icon_regex = r'<div class="w-20 h-20 bg-primary rounded-2xl mx-auto flex items-center justify-center mb-4 shadow-lg shadow-primary/30">\s*<svg.*?</svg>\s*</div>'
new_login_icon = """<div class="w-24 h-24 bg-primary rounded-3xl mx-auto flex items-center justify-center mb-6 shadow-xl shadow-primary/30">
                <span class="font-english text-4xl font-bold text-white tracking-widest">KN</span>
            </div>"""
html = re.sub(login_icon_regex, new_login_icon, html, flags=re.DOTALL)

# ب. تحديث شريط البحث في الكاشير
pos_search_html = """
            <div class="bg-card p-5 rounded-3xl premium-shadow border-0 mb-4">
                <h2 class="text-lg font-bold mb-4 text-primary">إضافة دواء للفاتورة</h2>
                <div class="flex gap-2 mb-4">
                    <div class="relative flex-1">
                        <input type="text" id="pos-search" onkeyup="filterMedicines()" placeholder="ابحث بالاسم التجاري أو العلمي..." class="w-full bg-bg border-0 rounded-xl p-3 pl-10 focus:ring-2 focus:ring-primary outline-none text-sm">
                        <svg class="w-5 h-5 text-gray-400 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    </div>
                    <button onclick="startScanner()" class="bg-primary hover:bg-[#073629] text-white px-5 rounded-xl font-bold transition flex items-center justify-center">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                    </button>
                </div>
                <div id="reader" class="w-full hidden rounded-xl overflow-hidden border-2 border-primary mb-2"></div>
                <button onclick="stopScanner()" id="stop-btn" class="hidden w-full text-red-600 text-sm font-bold bg-red-50 py-2 rounded-lg">إيقاف الكاميرا</button>
            </div>
"""
html = re.sub(r'<div class="bg-card p-5 rounded-3xl premium-shadow border-0">\s*<h2 class="text-lg font-semibold mb-4">إضافة دواء للفاتورة</h2>.*?</div>\s*</div>', pos_search_html, html, flags=re.DOTALL)

# ج. تحديث نموذج إضافة دواء في المخزون
inventory_form_html = """
            <div class="bg-card p-5 rounded-3xl premium-shadow border-0 mb-4">
                <h2 class="text-lg font-bold mb-4 text-primary flex items-center gap-2">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                    إضافة دواء جديد
                </h2>
                <form id="add-medicine-form" class="space-y-4">
                    <div class="grid grid-cols-1 gap-3">
                        <input type="text" id="med-name" placeholder="الاسم التجاري (إجباري)" required class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                        <input type="text" id="med-scientific" placeholder="الاسم العلمي (اختياري)" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                        
                        <select id="med-category" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none text-gray-700">
                            <option value="" disabled selected>اختر تصنيف الدواء...</option>
                            <option value="حبوب أو أقراص">حبوب أو أقراص (Tablets)</option>
                            <option value="كبسولات">كبسولات (Capsules)</option>
                            <option value="شراب">شراب (Syrup)</option>
                            <option value="حقن">حقن (Injections)</option>
                            <option value="محاليل وريدية">محاليل وريدية (IV Fluids)</option>
                            <option value="مراهم / كريمات">مراهم / كريمات (Ointments)</option>
                            <option value="قطرة">قطرة (Drops)</option>
                            <option value="مستلزمات طبية">مستلزمات طبية (قطن، شاش، كانيولا...)</option>
                            <option value="أخرى">أخرى (Other)</option>
                        </select>

                        <div class="grid grid-cols-2 gap-3">
                            <input type="number" id="med-price" placeholder="سعر البيع (SDG)" required class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                            <input type="number" id="med-stock" placeholder="الكمية المتوفرة" required class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                        </div>
                        <input type="text" id="med-barcode" placeholder="الباركود (لمسحه بالكاميرا لاحقاً)" class="bg-bg border-0 rounded-xl p-3 text-sm focus:ring-2 focus:ring-primary outline-none">
                    </div>
                    <button type="submit" class="w-full bg-primary hover:bg-[#073629] text-white py-3.5 rounded-xl font-bold shadow-lg shadow-primary/30 transition">حفظ في المخزون</button>
                </form>
            </div>
"""
html = re.sub(r'<div class="bg-card p-5 rounded-3xl premium-shadow border-0">\s*<h2.*?إضافة دواء جديد للمخزون</h2>.*?</div>\s*</div>', inventory_form_html, html, flags=re.DOTALL)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html (أيقونة KN، البحث، نموذج المخزون).")


# ==========================================
# 3. تحديث app.js (المنطق والبرمجة)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# أ. دالة البحث الفوري (Client-Side Filtering)
filter_js = """
function filterMedicines() {
    const query = document.getElementById('pos-search').value.toLowerCase();
    const items = document.querySelectorAll('#medicines-list > div');
    items.forEach(item => {
        const text = item.innerText.toLowerCase();
        item.style.display = text.includes(query) ? 'flex' : 'none';
    });
}
"""
if "function filterMedicines()" not in js:
    js = js.replace("function addToCart", filter_js + "\nfunction addToCart")

# ب. تحديث عرض الأدوية ليظهر الاسم العلمي والتصنيف
render_js = """
        list.innerHTML = medicines.map(med => `
            <div onclick="addToCart(${med.id}, '${med.name}', ${med.price})" class="cursor-pointer flex justify-between items-center p-3 border-b border-gray-100 hover:bg-primary/5 transition rounded-xl">
                <div>
                    <p class="font-bold text-gray-800 text-sm">${med.name}</p>
                    <p class="text-xs text-gray-500">${med.scientific_name || ''} ${med.category ? '| ' + med.category : ''}</p>
                </div>
                <div class="text-left">
                    <p class="font-bold text-primary">${med.price} SDG</p>
                    <p class="text-[10px] text-gray-400">المخزون: ${med.stock_quantity}</p>
                </div>
            </div>
        `).join('');
"""
js = re.sub(r'list\.innerHTML = medicines\.map\(med => `.*?`\)\.join\(\'\'\);', render_js, js, flags=re.DOTALL)

# ج. تحديث زر الإضافة للمخزون ليرسل الحقول الجديدة
form_submit_js = """
    const data = {
        name: document.getElementById('med-name').value,
        scientific_name: document.getElementById('med-scientific').value || null,
        category: document.getElementById('med-category').value || null,
        price: parseFloat(document.getElementById('med-price').value),
        stock_quantity: parseInt(document.getElementById('med-stock').value),
        barcode: document.getElementById('med-barcode').value || null,
        cost: 0
    };
"""
js = re.sub(r'const data = \{\s*name: document\.getElementById\(\'med-name\'\)\.value,.*?expiry_date: document\.getElementById\(\'med-expiry\'\)\.value \|\| null,\s*\};', form_submit_js, js, flags=re.DOTALL)

# د. تحديث الفاتورة لإضافة أزرار (+ و -) للكميات
cart_js = """
function renderCart() {
    const cartDiv = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total');
    if (!cartDiv || !totalEl) return;
    
    if (cart.length === 0) {
        cartDiv.innerHTML = '<p class="text-gray-400 text-sm text-center py-4">الفاتورة فارغة. اضغط على دواء لإضافته.</p>';
        totalEl.innerText = `0 SDG`; return;
    }
    
    let total = 0;
    cartDiv.innerHTML = cart.map((item, index) => {
        total += item.unit_price * item.quantity;
        return `
            <div class="flex justify-between items-center p-3 bg-bg rounded-xl mb-2">
                <div class="flex-1">
                    <p class="font-bold text-sm text-primary">${item.name}</p>
                    <p class="text-xs text-gray-500">${item.unit_price} SDG</p>
                </div>
                <div class="flex items-center gap-3">
                    <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-100">
                        <button onclick="updateQuantity(${index}, 1)" class="px-3 py-1 text-primary font-bold hover:bg-gray-50 rounded-r-lg">+</button>
                        <span class="px-2 font-bold text-sm">${item.quantity}</span>
                        <button onclick="updateQuantity(${index}, -1)" class="px-3 py-1 text-red-500 font-bold hover:bg-gray-50 rounded-l-lg">-</button>
                    </div>
                    <span class="font-bold text-primary w-16 text-left">${item.unit_price * item.quantity} SDG</span>
                    <button onclick="removeFromCart(${index})" class="text-red-500 bg-red-50 p-2 rounded-lg hover:bg-red-100 transition">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </div>
            </div>`;
    }).join('');
    totalEl.innerText = `${total} SDG`;
}

function updateQuantity(index, change) {
    cart[index].quantity += change;
    if (cart[index].quantity <= 0) {
        cart.splice(index, 1);
    }
    renderCart();
}
"""
js = re.sub(r'function renderCart\(\) \{.*?(?=async function checkout)', cart_js + "\n\n", js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js (البحث، الكميات، والتصنيفات).")

print("\n🎉 اكتملت الترقية! أعد تشغيل السيرفر واعمل مسح للكاش.")
