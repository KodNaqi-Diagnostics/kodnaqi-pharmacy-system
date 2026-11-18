import os
import re

print("⏳ جاري إصلاح القائمة الدوارة (صوت + تمرير + توزيع)...")

# ==========================================
# 1. تحديث index.html (إصلاح المسافات)
# ==========================================
with open("static/index.html", "r", encoding="utf-8") as f:
    html = f.read()

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
            bottom: 28px;
            right: 28px;
            width: 0;
            height: 0;
            pointer-events: none;
        }

        .radial-item {
            position: absolute;
            top: -24px; left: -24px;
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

        /* توزيع الأزرار في قوس دقيق (نصف قطر 90 بكسل) */
        .radial-menu-container.open .radial-item:nth-child(1) { transform: translate(0px, -90px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(2) { transform: translate(-40px, -80px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(3) { transform: translate(-70px, -55px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(4) { transform: translate(-88px, -20px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(5) { transform: translate(-88px, 20px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(6) { transform: translate(-70px, 55px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(7) { transform: translate(-40px, 80px) scale(1); }
        .radial-menu-container.open .radial-item:nth-child(8) { transform: translate(0px, 90px) scale(1); }

        .radial-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.3);
            backdrop-filter: blur(2px);
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
print("✅ تم إصلاح توزيع الأزرار في index.html.")


# ==========================================
# 2. تحديث app.js (الصوت + التمرير)
# ==========================================
with open("static/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# إضافة نظام الصوت (Web Audio API)
audio_js = """
// --- Web Audio API for Vault Sound ---
const AudioContextClass = window.AudioContext || window.webkitAudioContext;
const audioCtx = new AudioContextClass();

function playVaultSound(type) {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    const now = audioCtx.currentTime;

    if (type === 'tick') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(1600, now);
        osc.frequency.exponentialRampToValueAtTime(220, now + 0.02);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.02);
        osc.connect(gain); gain.connect(audioCtx.destination);
        osc.start(now); osc.stop(now + 0.02);
    } else if (type === 'lock') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(520, now);
        osc.frequency.exponentialRampToValueAtTime(75, now + 0.08);
        gain.gain.setValueAtTime(0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
        osc.connect(gain); gain.connect(audioCtx.destination);
        osc.start(now); osc.stop(now + 0.08);
    }
}
"""
if 'function playVaultSound' not in js:
    js = audio_js + js

# تحديث دالة فتح/إغلاق القائمة لإضافة الصوت
new_toggle_js = """
function toggleRadialMenu() {
    const menu = document.getElementById('radial-menu');
    const overlay = document.getElementById('radial-overlay');
    const fabMain = document.getElementById('fab-main');
    
    const isOpen = menu.classList.contains('open');
    
    if (!isOpen) {
        menu.classList.add('open');
        overlay.classList.add('active');
        fabMain.classList.add('active');
        fabMain.innerHTML = '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>';
        
        // تشغيل صوت التكات عند الفتح
        setTimeout(() => playVaultSound('tick'), 50);
        setTimeout(() => playVaultSound('tick'), 100);
        setTimeout(() => playVaultSound('tick'), 150);
    } else {
        menu.classList.remove('open');
        overlay.classList.remove('active');
        fabMain.classList.remove('active');
        
        const activeBtn = document.querySelector('.radial-item.active-tab');
        fabMain.innerHTML = activeBtn ? activeBtn.innerHTML : '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>';
        
        // تشغيل صوت القفل عند الإغلاق
        playVaultSound('lock');
    }
}

// إغلاق القائمة تلقائياً عند التمرير
window.addEventListener('scroll', () => {
    const menu = document.getElementById('radial-menu');
    if (menu && menu.classList.contains('open')) {
        toggleRadialMenu();
    }
});
"""
js = re.sub(r'function toggleRadialMenu\(\) \{.*?\n\}', new_toggle_js, js, flags=re.DOTALL)

with open("static/app.js", "w", encoding="utf-8") as f:
    f.write(js)
print("✅ تم إضافة الأصوات وإغلاق القائمة عند التمرير.")

# 3. كسر الكاش
with open("static/sw.js", "r", encoding="utf-8") as f:
    sw = f.read()
sw = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = 'kodnaqi-v48';", sw)
with open("static/sw.js", "w", encoding="utf-8") as f:
    f.write(sw)
print("✅ تم تحديث الكاش إلى v48.")

print("\n🎉 اكتمل الإصلاح! ارفع الكود الآن.")
