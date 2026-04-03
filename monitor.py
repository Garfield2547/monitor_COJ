import requests
from bs4 import BeautifulSoup
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL = "https://op.coj.go.th/th/content/category/articles/id/10/cid/21"
FILE_NAME = "last_update.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, json=payload, timeout=10)

def check_website():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- วิธีใหม่: ค้นหาทุกลิงก์ที่อยู่ใน d2ms-box-main ---
        main_content = soup.find('div', class_='d2ms-box-main')
        if not main_content:
            print("❌ ไม่พบส่วนเนื้อหา d2ms-box-main")
            return

        # ดึงลิงก์ทั้งหมดออกมา
        links = main_content.find_all('a', href=True)
        
        target_item = None
        for l in links:
            text = l.get_text(strip=True)
            # ข่าวจริงต้องมีตัวอักษรยาวระดับหนึ่ง (ป้องกันพวกคำว่า 'NEW' หรือ 'อ่านต่อ')
            if len(text) > 20: 
                target_item = l
                break # เอาลิงก์แรกที่ยาวเกิน 20 ตัวอักษร (ซึ่งคือข่าวล่าสุด)

        if not target_item:
            print("❌ ไม่พบหัวข้อข่าวที่เข้าเงื่อนไข")
            return

        title = target_item.get_text(strip=True)
        link = target_item['href']
        if not link.startswith('http'):
            link = "https://op.coj.go.th" + link

        current_data = f"{title} | {link}"
        print(f"🔍 บอทมองเห็นหัวข้อ: {title}")

        old_data = ""
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                old_data = f.read().strip()

        if current_data != old_data:
            print("🚀 พบการอัปเดตใหม่!")
            msg = f"<b>📢 ข่าวประชาสัมพันธ์ใหม่</b>\n\n📌 {title}\n\n🔗 <a href='{link}'>อ่านรายละเอียด</a>"
            send_telegram(msg)
            with open(FILE_NAME, "w", encoding="utf-8") as f:
                f.write(current_data)
        else:
            print("😴 ข้อมูลเหมือนเดิม (ไม่มีการส่งแจ้งเตือน)")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_website()