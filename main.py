import os
import requests
from flask import Flask
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

VISA_BULLETIN_URL = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2025/visa-bulletin-for-august-2025.html"
PAGE_404_SIGNATURE = "sorry, we couldn't find that page on travel.state.gov. here are several suggestions to help you find what you’re looking for:"

app = Flask(__name__)

def check_visa_update():
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

@app.route("/")
def home():
    return "✅ Visa Bulletin Watcher Bot is running."

# جدولة المهمة
scheduler = BackgroundScheduler()
scheduler.add_job(check_visa_update, "interval", minutes=3)
scheduler.start()
print("⏰ جدولة الفحص بدأت بنجاح.")

check_visa_update()  # ← تشغيل أولي عند بدء التشغيل

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
