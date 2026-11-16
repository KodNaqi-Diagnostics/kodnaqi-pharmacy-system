import os
import re

print("⏳ جاري ربط الشعارات الجديدة (logo-pharma & icon-pharma)...")

# 1. تحديث index.html
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# استبدال أي إشارة للشعار القديم بالشعار الكامل
html = html.replace('src="/logo.png"', 'src="/logo-pharma.png"')

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تحديث index.html لاستخدام logo-pharma.png")

# 2. تحديث manifest.json (أيقونة الهاتف)
manifest = """
{
  "name": "KodNaqi Pharmacy",
  "short_name": "KodNaqi",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0b4d3b",
  "theme_color": "#0b4d3b",
  "icons": [
    {
      "src": "/icon-pharma.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-pharma.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
"""
with open("static/manifest.json", "w", encoding="utf-8") as f:
    f.write(manifest)
print("✅ تم تحديث manifest.json لاستخدام icon-pharma.png")

# 3. تحديث sw.js (الذاكرة المؤقتة)
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()

# تحديث قائمة الملفات المحفوظة أوفلاين
if '/logo-pharma.png' not in sw:
    sw = sw.replace("'/manifest.json',", "'/manifest.json',\n    '/logo-pharma.png',\n    '/icon-pharma.png',")
    # حذف الأسماء القديمة إن وجدت
    sw = sw.replace("'/logo.png',", "")
    sw = sw.replace("'/icon.png',", "")
    
    with open("static/sw.js", "w", encoding="utf-8") as f:
        f.write(sw)
print("✅ تم تحديث sw.js لتخزين الصور الجديدة أوفلاين.")

print("\n🎉 اكتمل الربط! أعد تشغيل السيرفر واعمل Refresh.")
