
const CACHE_NAME = 'kodnaqi-v52'; // تحديث الإصدار
const ASSETS = [
    '/', '/index.html', '/app.js', '/manifest.json', '/logo-pharma.png', '/icon-pharma.png',
    'https://cdn.tailwindcss.com', 'https://unpkg.com/html5-qrcode',
    'https://cdnjs.cloudflare.com/ajax/libs/localforage/1.10.0/localforage.min.js',
    'https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js',
    'https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Poppins:wght@600;700&display=swap'
];

self.addEventListener('install', (e) => {
    self.skipWaiting(); // إجبار التحديث فوراً
    e.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)));
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.map(key => { if (key !== CACHE_NAME) return caches.delete(key); })
        ))
    );
    return self.clients.claim();
});

self.addEventListener('fetch', (e) => {
    if (e.request.url.includes('/api/')) return;
    e.respondWith(
        fetch(e.request).then(res => {
            const resClone = res.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(e.request, resClone));
            return res;
        }).catch(() => caches.match(e.request))
    );
});
