import os
import re

print("⏳ جاري تصحيح القائمة الدوارة وإصلاح كلمة معلق...")

# ==========================================
# 1. تحديث index.html (تصغير الزر وتصحيح CSS)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# استبدال كود الـ CSS الخاص بالقائمة بالكامل ليكون دقيقاً
new_css = """
    <style>
        /* القائمة الدوارة (Radial Menu) */
        .radial-menu-container {
            position: fixed;
            bottom: 25px;
            right: 25px;
            z-index: 1000;
        }
        
        .fab-main {
            width: 56px;
            height: 56px;
            background-color: #0b4d3b;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(11, 77, 59, 0.4);
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 1002;
            border: 2px solid #ffffff;
            color: white;
            position: relative;
        }

        .fab-main.active {
            transform: rotate(45deg);
            background-color: #dc2626;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4);
        }

        .radial-items {
            position: absolute;
            bottom: 28px; /* نصف حجم الزر */
            right: 28px;
            width: 0;
            height: 0;
            pointer-events: none;
        }

        .radial-item {
            position: absolute;
            top: -24px; left: -24px; /* نصف حجم الأيقونة 48px */
            width: 48px;
            height: 48px;
            background-color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            opacity: 0;
            transform: translate(0, 0) scale(0);
            pointer-events: auto;
            color: #0b4d3b;
            border: 2px solid #f2ede4;
        }

        .radial-item.active-tab {
            background-color: #0b4d3b;
            color: white;
            border-color: #0b4d3b;
        }

        .radial-menu-container.open .radial-item {
            opacity: 1;
        }

        /* توزيع الأزرار في نصف دائرة (تجاه الشاشة) */
        .radial-menu-container.open .radial-item:nth-child(1) { transform: translate(0px, -100px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(2) { transform: translate(-45px, -90px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(3) { transform: translate(-80px, -60px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(4) { transform: translate(-100px, 0px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(5) { transform: translate(-80px, 60px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(6) { transform: translate(-45px, 90px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(7) { transform: translate(0px, 100px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(8) { transform: translate(45px, 90px) scale(1); }

        .radial-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(3px);
            z-index: 999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        .radial-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }

        .role-cashier #fab-dashboard, .role-cashier #fab-inventory, .role-cashier #fab-purchases,
        .role-cashier #fab-suppliers, .role-cashier #fab-users, .role-cashier #fab-settings {
            display: none !important;
        }
    </style>
</head>
"""
html = re.sub(r'<style>\s*/\* القائمة الدوارة.*?</style>\s*</head>', new_css, html, flags=re.DOTALL)

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تصحيح أبعاد القائمة الدوارة.")


# ==========================================
# 2. تحديث app.js (إصلاح كلمة معلق)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# تحديث دالة processOutbox لكي تقوم بتحديث السجلات فور المزامنة
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
            let res = await apiFetch(`${API_URL}/sales`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sendData) }); 
            if (res.ok) { 
                let serverData = await res.json(); 
                let localSaleIndex = sales.findIndex(s => s.id == sale.id); 
                if (localSaleIndex !== -1) sales[localSaleIndex].invoice_number = serverData.invoice_number; 
                outbox.splice(i, 1); 
                i--; 
                outboxChanged = true; 
            } else { break; } 
        } catch(e) { break; } 
    } 
    
    if (outboxChanged) { 
        await localforage.setItem('kodnaqi_sales', sales); 
        await localforage.setItem('kodnaqi_outbox', outbox); 
        
        // التحديث التلقائي للسجلات إذا كنا نقف على شاشتها لإخفاء كلمة (معلق) فوراً
        const historyView = document.getElementById('view-history');
        if (historyView && !historyView.classList.contains('hidden')) {
            loadHistory();
        }
        // تحديث لوحة التحكم أيضاً لتحديث الأرقام
        const dashboardView = document.getElementById('view-dashboard');
        if (dashboardView && !dashboardView.classList.contains('hidden')) {
            loadDashboard();
        }
    } 
}
"""
js = re.sub(r'async function processOutbox\(\) \{.*?\n\}', new_process_outbox, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم إصلاح إخفاء كلمة معلق فور المزامنة.")

# 3. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v47';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v47.")

print("\n🎉 اكتمل الإصلاح! ارفع الكود الآن.")
