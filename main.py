import os
import threading
import time
import requests
from flask import Flask
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

VISA_BULLETIN_URL = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2025/visa-bulletin-for-augest-2025.html"
ERROR_SIGNATURE = "Sorry, we couldn't find that page on travel.state.gov. Here are several suggestions to help you find what you’re looking for".lower()

CHECK_INTERVAL = 120  # كل 3 دقائق

app = Flask(__name__)

def check_visa_update():
    already_notified = False
    while True:
        try:
            res = requests.get(VISA_BULLETIN_URL, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                page_text = soup.get_text().lower()

                if ERROR_SIGNATURE not in page_text:
                    if not already_notified:
                        send_alert("🔔 تم تحديث الصفحة! من المحتمل صدور نشرة فيزا جديدة. راجع الرابط الآن.")
                        already_notified = True
                    else:
                        print("🔁 الصفحة الجديدة موجودة ولكن تم الإشعار سابقًا.")
                else:
                    print("⏳ لم يتم صدور النشرة بعد (صفحة 404).")
            else:
                print("⚠️ فشل في الوصول للموقع (Status Code:", res.status_code, ")")
        except Exception as e:
            print("❌ خطأ أثناء التحقق:", e)
        time.sleep(CHECK_INTERVAL)

def send_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
    }
    try:
        requests.post(url, data=data)
        print("📨 تم إرسال التنبيه.")
    except Exception as e:
        print("⚠️ فشل في إرسال التنبيه:", e)

@app.route("/")
def home():
    return "Visa Bulletin Watcher Bot is running."

# بدء تشغيل التحقق في خلفية الخادم
threading.Thread(target=check_visa_update, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
