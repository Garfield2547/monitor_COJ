import requests
from bs4 import BeautifulSoup
import os

# ข้อมูลจาก GitHub Secrets
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- ใช้ URL ของ Google Apps Script ที่คุณเพิ่งสร้าง ---
URL = "https://script.google.com/macros/s/AKfycby_1zg8lA6V3nROK31DOmPoUWVsFHlzGGzAe5gLDR6C7pAFhFp2So5-mI4ujqh_kkU/exec"
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
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"❌ ส่ง Telegram ไม่สำเร็จ: {e}")

def check_website():
    try:
        print("🔄 กำลังดึงข้อมูลผ่าน Google Proxy...")
        # ดึงข้อมูลจาก Google Apps Script (เพิ่ม allow_redirects=True เพื่อรองรับการ Redirect ของ Google)
        response = requests.get(URL, timeout=60, allow_redirects=True)
        
        if response.status_code != 200:
            print(f"❌ Google Proxy ตอบกลับด้วย Error: {response.status_code}")
            return

        # ตรวจสอบว่าได้เนื้อหาเว็บมาจริงไหม
        if "d2ms-box-main" not in response.text:
            print("❌ ไม่พบโครงสร้างเว็บศาลในข้อมูลที่ดึงมา (อาจโดนบล็อกหรือดึงผิดหน้า)")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ค้นหาใน d2ms-box-main ตามที่คุณ Inspect ไว้
        main_content = soup.find('div', class_='d2ms-box-main')
        links = main_content.find_all('a', href=True)
        
        target_item = None
        for l in links:
            text = l.get_text(strip=True)
            # ข่าวจริงต้องมีความยาวพอสมควร
            if len(text) > 20: 
                target_item = l
                break

        if target_item:
            title = target_item.get_text(strip=True)
            link = target_item['href']
            if not link.startswith('http'):
                link = "https://op.coj.go.th" + link
            
            current_data = f"{title} | {link}"
            print(f"🔍 บอทมองเห็นหัวข้อข่าวล่าสุด: {title}")

            # อ่านค่าเก่ามาเทียบ
            old_data = ""
            if os.path.exists(FILE_NAME):
                with open(FILE_NAME, "r", encoding="utf-8") as f:
                    old_data = f.read().strip()

            if current_data != old_data:
                print("🚀 พบการอัปเดตใหม่! กำลังส่ง Telegram...")
                msg = f"<b>📢 ข่าวประชาสัมพันธ์ใหม่ (ศาลยุติธรรม)</b>\n\n📌 {title}\n\n🔗 <a href='{link}'>คลิกเพื่ออ่านรายละเอียด</a>"
                send_telegram(msg)

                # เซฟค่าใหม่ลงไฟล์
                with open(FILE_NAME, "w", encoding="utf-8") as f:
                    f.write(current_data)
            else:
                print("😴 ข้อมูลยังเหมือนเดิม")
        else:
            print("❌ ไม่พบลิงก์ข่าวที่เข้าเงื่อนไข")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    check_website()