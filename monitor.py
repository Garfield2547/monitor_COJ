import requests
from bs4 import BeautifulSoup
import os
import time

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL = "https://op.coj.go.th/th/content/category/articles/id/10/cid/21"
FILE_NAME = "last_update.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass

def check_website():
    # ใช้ User-Agent ที่ดูเหมือน Browser ทั่วไปมากขึ้น
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept-Language': 'th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    response = None
    # พยายามดึงข้อมูล 3 ครั้ง ถ้าล้มเหลวให้รอแล้วลองใหม่
    for i in range(3):
        try:
            print(f"🔄 พยายามเชื่อมต่อครั้งที่ {i+1}...")
            response = requests.get(URL, headers=headers, timeout=30) # เพิ่มเวลาเป็น 30 วินาที
            if response.status_code == 200:
                break
        except Exception as e:
            print(f"⚠️ ครั้งที่ {i+1} ล้มเหลว: {e}")
            time.sleep(5) # รอ 5 วินาทีก่อนลองใหม่

    if not response or response.status_code != 200:
        print("❌ ไม่สามารถเข้าถึงเว็บไซต์ได้หลังจากพยายามหลายครั้ง")
        return

    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # ค้นหาเนื้อหาใน d2ms-box-main
    main_content = soup.find('div', class_='d2ms-box-main')
    if not main_content:
        print("❌ หา d2ms-box-main ไม่เจอ")
        return

    links = main_content.find_all('a', href=True)
    target_item = None
    for l in links:
        text = l.get_text(strip=True)
        if len(text) > 20:
            target_item = l
            break

    if target_item:
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
            msg = f"<b>📢 ข่าวประชาสัมพันธ์ใหม่</b>\n\n📌 {title}\n\n🔗 <a href='{link}'>อ่านรายละเอียด</a>"
            send_telegram(msg)
            with open(FILE_NAME, "w", encoding="utf-8") as f:
                f.write(current_data)
            print("🚀 อัปเดตและแจ้งเตือนเรียบร้อย!")
        else:
            print("😴 ข้อมูลยังเหมือนเดิม")

if __name__ == "__main__":
    check_website()