import requests
from bs4 import BeautifulSoup
import os

# ดึงค่าจาก GitHub Secrets
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
# เปลี่ยนเป็น URL ใหม่ที่คุณต้องการ
URL = "https://op.coj.go.th/th/content/category/articles/id/10/cid/21"
FILE_NAME = "last_update.txt"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
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
        response = requests.get(URL, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"Web Error: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # เจาะจงไปที่ d2ms-box-main ตามภาพ Inspect ของคุณ
        # และค้นหาลิงก์ข่าวตัวแรกที่อยู่ในส่วนเนื้อหา
        main_content = soup.find('div', class_='d2ms-box-main')
        if not main_content:
            # สำรองไว้ถ้าหา class บนไม่เจอ ให้หาจาก ID หลัก
            main_content = soup.find(id='d2ms-section-main-content-main')

        if main_content:
            # ค้นหา <a> ตัวแรกที่เป็นหัวข้อข่าว
            # ปกติจะเป็นลิงก์ที่มีข้อความยาวๆ ในส่วนลิสต์
            item = main_content.find('a', href=True)
            
            if item:
                title = item.get_text(strip=True)
                # ป้องกันกรณีดึงเอาข้อความสั้นๆ เช่น "อ่านต่อ" หรือ "NEW"
                if len(title) < 5: 
                    all_links = main_content.find_all('a', href=True)
                    for link in all_links:
                        if len(link.get_text(strip=True)) > 10:
                            item = link
                            title = item.get_text(strip=True)
                            break

                link = item['href']
                if not link.startswith('http'):
                    link = "https://op.coj.go.th" + link
                
                current_data = f"{title} | {link}"
                print(f"🔍 ดึงข้อมูลล่าสุดได้: {title}")

                # อ่านค่าเก่า
                old_data = ""
                if os.path.exists(FILE_NAME):
                    with open(FILE_NAME, "r", encoding="utf-8") as f:
                        old_data = f.read().strip()

                if current_data != old_data:
                    print("🚀 พบการอัปเดตใหม่! กำลังส่ง Telegram...")
                    msg = f"<b>📢 ข่าวประชาสัมพันธ์ใหม่ (สำนักประธานศาลฯ)</b>\n\n📌 {title}\n\n🔗 <a href='{link}'>คลิกเพื่ออ่านรายละเอียด</a>"
                    send_telegram(msg)

                    with open(FILE_NAME, "w", encoding="utf-8") as f:
                        f.write(current_data)
                else:
                    print("😴 ข้อมูลยังเป็นตัวเดิม")
            else:
                print("❌ ไม่พบลิงก์ข่าวใน d2ms-box-main")
        else:
            print("❌ ไม่พบส่วนเนื้อหา d2ms-box-main")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    check_website()