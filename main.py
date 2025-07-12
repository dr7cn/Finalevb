import os
import requests
from flask import Flask
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import threading

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

VISA_BULLETIN_URL = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2025/visa-bulletin-for-august-2025.html"
PAGE_404_SIGNATURE = "sorry, we couldn't find that page on travel.state.gov. here are several suggestions to help you find what you’re looking for:"

app = Flask(__name__)

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def check_visa_update():
    log("🔁 بدأ التحقق من صفحة النشرة...")
    try:
        res = requests.get(VISA_BULLETIN_URL, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            page_text = soup.get_text().lower()
            if PAGE_404_SIGNATURE in page_text:
                log("❌ لم يتم إصدار النشرة بعد (صفحة 404).")
            else:
                log("✅ على الأرجح تم إصدار النشرة!")
                send_alert("🔔 من المحتمل صدور نشرة فيزا جديدة! راجع الموقع الآن.")
        else:
            log(f"⚠️ لم يتم الوصول للموقع. الكود: {res.status_code}")
    except Exception as e:
        log(f"❌ خطأ أثناء التحقق: {e}")

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
    }
    try:
        requests.post(url, data=data)
        log("📨 تم إرسال تنبيه.")
    except Exception as e:
        log(f"⚠️ فشل في إرسال التنبيه: {e}")

@app.route("/")
def home():
    return "✅ Visa Bulletin Watcher Bot is running."

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_visa_update, "interval", minutes=3)
    scheduler.start()
    log("⏰ جدولة الفحص بدأت بنجاح.")

    # تأكد من بقاء التطبيق حي
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
    # تشغيل المجدول في thread خاص
    threading.Thread(target=start_scheduler, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
