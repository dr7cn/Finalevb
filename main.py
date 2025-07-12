import os
import threading
import time
import requests
from flask import Flask
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

VISA_BULLETIN_URL = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2025/visa-bulletin-for-augest-2025.html"
OLD_SIGNATURE_TEXT = "The Department of State will issue the August Visa Bulletin"
CHECK_INTERVAL = 180  # 3 دقائق

app = Flask(__name__)

def check_visa_update():
    while True:
        try:
            res = requests.get(VISA_BULLETIN_URL, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                page_text = soup.get_text()
                if OLD_SIGNATURE_TEXT not in page_text:
                    send_alert("🔔 من المحتمل صدور نشرة فيزا جديدة! راجع الموقع الآن.")
                else:
                    print("✅ لا يوجد تغيير في الصفحة.")
            else:
                print("⚠️ فشل في الوصول للموقع.")
        except Exception as e:
            print("❌ خطأ:", e)
        time.sleep(CHECK_INTERVAL)

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
    return "Visa Bulletin Watcher Bot is running."

threading.Thread(target=check_visa_update, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
