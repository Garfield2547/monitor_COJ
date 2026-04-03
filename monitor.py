import requests
from bs4 import BeautifulSoup
import os

# ดึงค่าจาก GitHub Secrets
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL = "https://op.coj.go.th/th/page/item/index/id/1"
FILE_NAME = "last_update.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram: {e}")

def check_website():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"Web Error: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ค้นหาหัวข้อข่าวล่าสุด (ในเว็บศาลมักจะอยู่ใน <div class="item-list"> หรือตาราง)
        # ตัวอย่างนี้จะดึงข้อความจากลิงก์แรกที่พบในเนื้อหาหลัก
        item = soup.find('a', href=True) # ปรับจูนจุดนี้ตามโครงสร้างหน้าเว็บจริง
        
        if not item:
            print("ไม่พบข้อมูลที่ต้องการดึง")
            return

        latest_title = item.text.strip()
        
        # อ่านค่าเดิม
        old_title = ""
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                old_title = f.read().strip()

        if latest_title != old_title:
            print("พบข้อมูลใหม่!")
            msg = f"<b>🔔 มีอัปเดตใหม่จากศาลยุติธรรม!</b>\n\nหัวข้อ: {latest_title}\n\n🔗 <a href='{URL}'>คลิกเพื่อดูรายละเอียด</a>"
            send_telegram(msg)

            with open(FILE_NAME, "w", encoding="utf-8") as f:
                f.write(latest_title)
        else:
            print("ไม่มีการเปลี่ยนแปลง")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_website()