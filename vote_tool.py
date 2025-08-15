import requests
import datetime
import json
import time

# File chứa danh sách user
VOTERS_FILE = "voters.json"

def load_voters():
    with open(VOTERS_FILE, "r") as f:
        return json.load(f)

def save_voters(voters):
    with open(VOTERS_FILE, "w") as f:
        json.dump(voters, f, indent=2, default=str)

def vote_for_user(user):
    now = datetime.datetime.utcnow()
    last_voted = datetime.datetime.fromisoformat(user["last_voted"])

    if (now - last_voted).total_seconds() < 86400:
        print(f"⏳ {user['email']} chưa đến 24h, bỏ qua.")
        return False

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://under35.fpt.com",
        "Referer": "https://under35.fpt.com/2025/ung-vien/nguyen-xuan-thanh",
        "User-Agent": "Mozilla/5.0",
        "X-CSRF-TOKEN": user["csrf_token"]
    }

    url = "https://under35.fpt.com/api/top-candidate/39/vote"

    try:
        response = requests.post(url, headers=headers, cookies=user["cookies"])
        if response.status_code == 200:
            print(f"✅ Vote thành công cho {user['email']}")
            user["last_voted"] = now.isoformat()
            return True
        else:
            print(f"❌ Vote thất bại cho {user['email']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Lỗi khi vote cho {user['email']}: {str(e)}")
        return False

def main_loop():
    while True:
        print(f"\n🔁 Bắt đầu vòng lặp mới: {datetime.datetime.now()}")
        voters = load_voters()
        for user in voters:
            vote_for_user(user)
        save_voters(voters)

        print("⏱️ Đợi 30 phút rồi tiếp tục...\n")
        time.sleep(1800)  # 30 phút

if __name__ == "__main__":
    main_loop()
