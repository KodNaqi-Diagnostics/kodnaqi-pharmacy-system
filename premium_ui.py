import os
import re

print("⏳ جاري تطبيق الهوية البصرية الجديدة (Premium UI)...")

# ==========================================
# 1. تحديث index.html
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# تحديث الـ Head لإضافة الخطوط (Tajawal) وإعدادات Tailwind المخصصة
new_head = """
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KodNaqi Pharmacy</title>
    <!-- خط تجوال الاحترافي -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Tajawal', 'sans-serif'] },
                    colors: {
                        primary: '#0b4d3b', // الأخضر الداكن من الصورة
                        bg: '#f9f6f0',      // لون الخلفية البيج
                        card: '#ffffff'
                    }
                }
            }
        }
    </script>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
    <link rel="manifest" href="/manifest.json">
    <style>
        body { font-family: 'Tajawal', sans-serif; background-color: #f9f6f0; }
        .premium-shadow { box-shadow: 0 4px 20px rgba(0,0,0,0.04); }
        @media print {
            body > * { display: none !important; }
            #print-area { display: block !important; margin: 0 auto !important; padding: 10px; width: 100%; max-width: 80mm; color: #000 !important; background: #fff !important; }
            #app-modal { display: none !important; }
            @page { margin: 5mm; }
        }
    </style>
</head>"""

# استبدال الـ head القديم بالجديد
html = re.sub(r'<head>.*?</head>', new_head, html, flags=re.DOTALL)

# تحديث الشريط العلوي (Header)
html = re.sub(
    r'<header.*?</header>', 
    """<header class="bg-primary text-white p-4 shadow-md sticky top-0 z-10 flex justify-between items-center rounded-b-2xl">
        <h1 id="pharmacy-name" class="text-xl font-bold">جاري التحميل...</h1>
        <span id="current-tab-title" class="text-xs bg-white/20 px-3 py-1 rounded-full font-medium">الكاشير</span>
    </header>""", 
    html, flags=re.DOTALL
)

# تحديث ألوان الخلفيات والبطاقات (تغيير bg-white إلى bg-card، وإضافة premium-shadow)
html = html.replace('bg-gray-100 text-gray-800 font-sans pb-20', 'text-gray-800 pb-24')
html = html.replace('bg-white p-6 rounded-xl shadow-sm border border-gray-200', 'bg-card p-5 rounded-3xl premium-shadow border-0')
html = html.replace('bg-white p-6 rounded-xl shadow-sm border-2 border-emerald-500', 'bg-card p-5 rounded-3xl premium-shadow border-2 border-primary')
html = html.replace('text-emerald-800', 'text-primary')
html = html.replace('text-emerald-600', 'text-primary')
html = html.replace('bg-emerald-600 hover:bg-emerald-700', 'bg-primary hover:bg-[#073629]')
html = html.replace('focus:ring-emerald-500', 'focus:ring-primary')

# تحديث شريط التنقل السفلي
new_nav = """
    <nav class="fixed bottom-0 w-full bg-white border-t border-gray-100 flex justify-around py-2 px-1 z-20 shadow-[0_-4px_20px_rgba(0,0,0,0.05)] rounded-t-2xl">
        <button onclick="switchTab('pos')" id="btn-pos" class="flex flex-col items-center p-2 text-primary w-1/4 transition-all"><span class="text-2xl mb-1">🛒</span><span class="text-[10px] font-bold">الكاشير</span></button>
        <button onclick="switchTab('inventory')" id="btn-inventory" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/4 transition-all"><span class="text-2xl mb-1">📦</span><span class="text-[10px] font-bold">المخزون</span></button>
        <button onclick="switchTab('history')" id="btn-history" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/4 transition-all"><span class="text-2xl mb-1">📋</span><span class="text-[10px] font-bold">السجلات</span></button>
        <button onclick="switchTab('settings')" id="btn-settings" class="flex flex-col items-center p-2 text-gray-400 hover:text-primary w-1/4 transition-all"><span class="text-2xl mb-1">⚙️</span><span class="text-[10px] font-bold">الإعدادات</span></button>
    </nav>"""

html = re.sub(r'<nav.*?</nav>', new_nav, html, flags=re.DOTALL)

# تحديث أزرار شريط التنقل في الجافاسكريبت (لتناسب التصميم الجديد)
html = html.replace('w-1/4', 'w-1/4') # تأكيد على العرض

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ تم تطبيق التصميم الجديد على index.html")

# ==========================================
# 2. إنشاء ملفات PWA (manifest.json + sw.js)
# ==========================================
manifest = """
{
  "name": "KodNaqi Pharmacy",
  "short_name": "KodNaqi",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#f9f6f0",
  "theme_color": "#0b4d3b",
  "icons": [
    {
      "src": "https://cdn-icons-png.flaticon.com/512/2966/2966327.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
"""
with open("static/manifest.json", "w", encoding="utf-8") as f:
    f.write(manifest)
print("✅ تم إنشاء manifest.json")

sw = """
const CACHE_NAME = 'kodnaqi-v1';
const ASSETS = [
    '/',
    '/index.html',
    '/app.js',
    '/manifest.json',
    'https://cdn.tailwindcss.com',
    'https://unpkg.com/html5-qrcode',
    'https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js',
    'https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap'
];

// تثبيت الـ Service Worker وتخزين الملفات
self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
    self.skipWaiting();
});

// تفعيل وحذف الكاش القديم
self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) return caches.delete(key);
                })
            );
        })
    );
    return self.clients.claim();
});

// استراتيجية الجلب (Network First, Fallback to Cache)
self.addEventListener('fetch', (e) => {
    // لا نقوم بتخزين طلبات الـ API في الكاش (سنعالجها لاحقاً بـ IndexedDB)
    if (e.request.url.includes('/api/')) return;
    
    e.respondWith(
        fetch(e.request)
            .then((res) => {
                const resClone = res.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(e.request, resClone);
                });
                return res;
            })
            .catch(() => caches.match(e.request))
    );
});
"""
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم إنشاء sw.js")

# ==========================================
# 3. ربط الـ Service Worker في app.js
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

if 'serviceWorker' not in js:
    sw_registration = """
// تسجيل Service Worker لتفعيل الـ PWA والعمل أوفلاين
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('✅ Service Worker registered'))
            .catch(err => console.log('❌ Service Worker error', err));
    });
}
"""
    js += sw_registration

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم تحديث app.js لتسجيل Service Worker")

print("\n🎉 اكتمل التحول! يرجى إعادة تشغيل السيرفر وتحديث المتصفح.")
