import os

print("⏳ جاري إصلاح أيقونة زر المزامنة...")

with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# البحث عن الزر واستبداله بالكامل بأيقونة واضحة ومناسبة
old_btn = """
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

new_btn = """
                <!-- زر المزامنة اليدوية -->
                <div class="bg-card rounded-3xl premium-shadow overflow-hidden mb-4">
                    <button onclick="forceSync()" class="w-full p-4 flex items-center justify-between text-primary hover:bg-blue-50 transition">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                                <!-- أيقونة مزامنة واضحة -->
                                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                                </svg>
                            </div>
                            <span class="font-bold text-sm">مزامنة البيانات المعلقة الآن</span>
                        </div>
                        <!-- سهم صغير في اليسار لتوضيح أنه زر -->
                        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
                    </button>
                </div>
"""

if old_btn.strip() in html:
    html = html.replace(old_btn.strip(), new_btn.strip())
    print("✅ تم استبدال الأيقونة القديمة بنجاح.")
else:
    # إذا لم يجد النص المطابق تماماً (بسبب المسافات)، يبحث بطريقة أخرى
    import re
    pattern = r'<div class="bg-card rounded-3xl premium-shadow overflow-hidden mb-4">\s*<button onclick="forceSync\(\)".*?</button>\s*</div>'
    html = re.sub(pattern, new_btn.strip(), html, flags=re.DOTALL)
    print("✅ تم البحث والاستبدال بالطريقة الاحتياطية.")

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("🎉 اكتمل إصلاح الأيقونة!")
