import os
import threading
import time
import requests
from flask import Flask
from bs4 import BeautifulSoup

# جلب المتغيرات من بيئة Render
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# رابط النشرة
VISA_BULLETIN_URL = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2025/visa-bulletin-for-augest-2025.html"

# الجملة التي تدل على أن الصفحة غير موجودة (404)
PAGE_404_SIGNATURE = "we’re sorry, we can’t find that page"
CHECK_INTERVAL = 180  # كل 3 دقائق

# إنشاء تطبيق Flask
app = Flask(__name__)

# دالة التحقق من الموقع
def check_visa_update():
    while True:
        print("🔁 بدأ التحقق من صفحة النشرة...")
        try:
            res = requests.get(VISA_BULLETIN_URL, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                page_text = soup.get_text().lower()
                if PAGE_404_SIGNATURE in page_text:
                    print("❌ لم يتم إصدار النشرة بعد (صفحة 404).")
                else:
                    print("✅ على الأرجح تم إصدار النشرة!")
                    send_alert("🔔 من المحتمل صدور نشرة فيزا جديدة! راجع الموقع الآن.")
            else:
                print(f"⚠️ لم يتم الوصول للموقع. الكود: {res.status_code}")
        except Exception as e:
            print("❌ خطأ أثناء التحقق:", e)
        time.sleep(CHECK_INTERVAL)

# دالة إرسال الإشعار عبر تيليجرام
def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
    }
    try:
        requests.post(url, data=data)
        print("📨 تم إرسال تنبيه.")
    except Exception as e:
        print("⚠️ فشل في إرسال التنبيه:", e)

# صفحة بسيطة لواجهة Flask
@app.route("/")
def home():
    return "✅ Visa Bulletin Watcher Bot is running."

# تشغيل البوت والخدمة
if __name__ == "__main__":
    threading.Thread(target=check_visa_update, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
