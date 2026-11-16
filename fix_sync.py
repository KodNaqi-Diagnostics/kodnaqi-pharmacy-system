import os
import re

print("⏳ جاري إصلاح مشكلة المزامنة (ID Mismatch)...")

with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# تحديث دالة مزامنة الأدوية لتحديث الـ ID المحلي بالـ ID القادم من السيرفر
new_sync_meds = """
async function syncMedicinesToServer() {
    try {
        let medOutbox = await localforage.getItem('kodnaqi_med_outbox') || [];
        if(medOutbox.length === 0) return;

        let localMeds = await localforage.getItem('kodnaqi_medicines') || [];
        let outboxChanged = false;

        for (let i = 0; i < medOutbox.length; i++) {
            let med = medOutbox[i];
            let sendData = {...med};
            delete sendData.id; // إرسال البيانات بدون المعرف المحلي

            const res = await fetch(`${API_URL}/medicines`, { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify(sendData) 
            });
            
            if (res.ok) {
                const serverMed = await res.json(); // السيرفر يعيد الدواء مع الـ ID الحقيقي
                
                // تحديث ذاكرة الهاتف بالـ ID الحقيقي
                let localIndex = localMeds.findIndex(m => m.id === med.id);
                if (localIndex !== -1) {
                    localMeds[localIndex].id = serverMed.id;
                }
                
                medOutbox.splice(i, 1);
                i--;
                outboxChanged = true;
            } else {
                break; 
            }
        }
        
        if (outboxChanged) {
            await localforage.setItem('kodnaqi_medicines', localMeds);
            await localforage.setItem('kodnaqi_med_outbox', medOutbox);
            console.log("✅ Medicines synced and IDs updated.");
        }
    } catch(err) {
        console.log("Sync paused: Server unreachable.");
    }
}
"""
js = re.sub(r'async function syncMedicinesToServer\(\) \{.*?\n\}', new_sync_meds, js, flags=re.DOTALL)

# إضافة زر مزامنة يدوي في الإعدادات (لمسح الفواتير المعلقة)
sync_btn_ui = """
                <!-- زر المزامنة اليدوية -->
                <div class="bg-card rounded-3xl premium-shadow overflow-hidden mb-4">
                    <button onclick="forceSync()" class="w-full p-4 flex items-center justify-between text-primary hover:bg-blue-50 transition">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                                <svg class="w-5 h-5 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                            </div>
                            <span class="font-bold text-sm">مزامنة البيانات المعلقة الآن</span>
                        </div>
                    </button>
                </div>
"""
if 'forceSync()' not in js:
    js += """
async function forceSync() {
    await showAlert("جاري المزامنة", "يتم إرسال البيانات المعلقة للسحابة...", "success");
    await syncMedicinesToServer();
    await processOutbox();
    await loadMedicines();
    await loadHistory();
    await showAlert("تمت المزامنة", "تمت مزامنة جميع البيانات المعلقة بنجاح!", "success");
}
"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    if 'forceSync()' not in html:
        html = html.replace('<h3 class="text-sm font-bold text-gray-500 px-2 mt-6">النسخ الاحتياطي والبيانات</h3>', sync_btn_ui + '\n<h3 class="text-sm font-bold text-gray-500 px-2 mt-6">النسخ الاحتياطي والبيانات</h3>')
        with open("static/index.html", "w", encoding="utf-8") as f:
            f.write(html)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم إصلاح المزامنة وإضافة زر المزامنة اليدوية.")
