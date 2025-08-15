# save as multi_incognito_signup.py
import asyncio
import random
import csv
from pathlib import Path
from faker import Faker
from playwright.async_api import async_playwright, TimeoutError as PWTimeoutError
from datetime import datetime
from proxies import PROXIES
fake = Faker()

# CONFIG
#TEST_URL = "http://localhost:3000/signup"  # <-- đổi thành trang test của bạn
TEST_URL = "https://accounts.google.com/SignUp"  # <-- đổi thành trang test của bạn
WORKERS = 1              # số incognito contexts (cửa sổ ẩn danh)
TABS_PER_WORKER = 3      # số tab (page) mỗi context
MAX_CONCURRENT_TASKS = 12 # giới hạn concurrency
TIMEOUT = 30000           # ms
OUTPUT_CSV = Path("generated_accounts.csv")
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

# Selectors - chỉnh theo form của bạn
SELECTORS = {
    "first_name": 'input[name="firstName"]',
    "last_name":  'input[name="lastName"]',
    "email":      'input[name="email"]',
    "submit":     'button[type="submit"]',
    "username":   'input[name="Username"]',  # Cập nhật selector cho trường "Username"
    "password":   'input[name="Passwd"]',
    "confirm_password": 'input[name="PasswdAgain"]',
}

async def fill_and_submit(page, payload, take_screenshot=True):
    """Điền form và submit. Bắt lỗi nhẹ để script tiếp tục."""
    try:
        await page.goto(TEST_URL, timeout=TIMEOUT)
    except PWTimeoutError:
        print("Timeout khi load:", TEST_URL)
        return {"status": "failed", "reason": "timeout_load"}

    # Điền thông tin ban đầu
    await page.fill(SELECTORS["first_name"], payload["first_name"])
    await page.fill(SELECTORS["last_name"], payload["last_name"])

    # Click nút "Tiếp theo"
    btn = page.locator("button[jsname='LgbsSe']").first
    if await btn.is_visible() and not await btn.is_disabled():
        await btn.click()
        print("✅ Đã bấm nút 'Tiếp theo'")
    else:
        print("Nút 'Tiếp theo' không khả dụng.")
        return {"status": "failed", "reason": "button_unavailable"}

    # Chờ trang mới tải xong
    await page.wait_for_load_state("networkidle")

    # Điền thông tin ngày sinh và giới tính
    print("Đang điền thông tin mới...")

    # Mở dropdown "Month" và chọn giá trị
    await page.locator('#month').click()  # Click để mở dropdown
    await page.locator('#month li', has_text="January").click()  # Chọn tháng "January"

    # Điền "Day" và "Year"
    await page.fill('input[name="day"]', payload["day"])
    await page.fill('input[name="year"]', payload["year"])

    # Mở dropdown "Gender" và chọn giá trị
    await page.locator('#gender').click()  # Click để mở dropdown
    await page.locator('#gender li[data-value="1"]').click()  # Chọn giá trị "1" (Male)

    print("✅ Đã điền thông tin ngày tháng năm")
    # Click nút "Tiếp theo"
    btn2 = page.locator("button[jsname='LgbsSe']").first
    if await btn2.is_visible() and not await btn2.is_disabled():
        await btn2.click()
        print("✅ Đã bấm nút 'Tiếp theo 2'")
    else:
        print("Nút 'Tiếp theo 2' không khả dụng.")
        return {"status": "failed", "reason": "button_unavailable"}

    # Kiểm tra và điền dữ liệu vào trường "Username"
    try:
        await page.wait_for_selector('input[name="Username"]', timeout=5000)  # Chờ tối đa 5 giây
        username_input = page.locator('input[name="Username"]')
        if await username_input.count() > 0:
            await username_input.fill(payload["username"])
            print("✅ Đã điền dữ liệu vào 'Username'.")
        else:
            raise Exception("Trường 'Username' không tồn tại.")
    except Exception as e:
        # Nếu không tìm thấy, chọn tùy chọn đầu tiên
        print("Không tìm thấy trường nhập liệu 'Username'. Chọn tùy chọn đầu tiên.")
        radiogroup_option = page.locator('div[role="radiogroup"] div[data-value]').first
        if await radiogroup_option.count() > 0:
            await radiogroup_option.click()
            print("✅ Đã chọn giá trị đầu tiên trong radiogroup.")
        else:
            print("❌ Không tìm thấy bất kỳ giá trị nào trong radiogroup.")

     # Click nút "Tiếp theo"
    btn3 = page.locator("button[jsname='LgbsSe']").first
    if await btn3.is_visible() and not await btn3.is_disabled():
        await btn3.click()
        print("✅ Đã bấm nút 'Tiếp theo 3'")
    else:
        print("Nút 'Tiếp theo 3' không khả dụng.")
        return {"status": "failed", "reason": "button_unavailable"}

    # Kiểm tra và điền dữ liệu vào trường "Password" và "Confirm Password"
    try:
        # Điền mật khẩu
        await page.wait_for_selector('input[name="Passwd"]', timeout=5000)  # Chờ tối đa 5 giây
        password_input = page.locator('input[name="Passwd"]')
        await password_input.fill(payload["password"])
        print("✅ Đã điền dữ liệu vào 'Password'.")

        # Chờ trường "Confirm Password" xuất hiện
        await page.wait_for_selector('input[name="PasswdAgain"]', timeout=5000)
        confirm_password_input = page.locator('input[name="PasswdAgain"]')
        await confirm_password_input.fill(payload["password"])
        print("✅ Đã điền dữ liệu vào 'Confirm Password'.")
    except Exception as e:
        print("❌ Lỗi khi điền mật khẩu hoặc xác nhận mật khẩu:", e)


      # Click nút "Tiếp theo"
    btn4 = page.locator("button[jsname='LgbsSe']").first
    if await btn4.is_visible() and not await btn4.is_disabled():
        await btn4.click()
        print("✅ Đã bấm nút 'Tiếp theo password'")
    else:
        print("Nút 'Tiếp theo password' không khả dụng.")
        return {"status": "failed", "reason": "button_unavailable"}


    # Chụp ảnh màn hình nếu cần
    if take_screenshot:
        screenshot_path = SCREENSHOT_DIR / f"{payload['email'].replace('@','_at_')}_error.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"❌ Đã chụp màn hình lỗi tại: {screenshot_path}")

    # Giữ trình duyệt mở để debug
    print("Giữ trình duyệt mở để kiểm tra lỗi.")
    await asyncio.sleep(3600)  # Giữ trình duyệt mở trong 1 giờ

    return {"status": "ok", "email": payload["email"]}

async def worker_task(page, worker_id, tab_id):
    """Thực hiện tác vụ trên một tab."""
    try:
        # Tạo dữ liệu random
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{fake.pystr(min_chars=6, max_chars=10)}"
        email = f"{username}@gmail.com"
        password = "Asd!@!#050697"

        # Tạo dữ liệu ngày sinh ngẫu nhiên
        current_year = datetime.now().year
        birth_year = random.randint(current_year - 15, current_year - 1)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)

        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "month": datetime(1900, birth_month, 1).strftime("%B"),
            "day": str(birth_day),
            "year": str(birth_year),
            "gender": "Female",
            "username": username,
        }

        print(f"[W{worker_id}-T{tab_id}] Start -> {email}")
        result = await fill_and_submit(page, payload, take_screenshot=True)
        print(f"[W{worker_id}-T{tab_id}] Done -> {result.get('status')}")
    finally:
        # Đóng tab sau khi hoàn thành
        await page.close()
    return result

async def main():
    # Prepare CSV
    if not OUTPUT_CSV.exists():
        with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["email", "first_name", "last_name", "password", "status", "note"])

    sem = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Đặt True nếu muốn chạy không hiển thị giao diện
            args=[
                "--start-maximized",  # Mở trình duyệt ở chế độ toàn màn hình
            ]
        )
        tasks = []

        for w in range(WORKERS):
            for t in range(TABS_PER_WORKER):
                # Lấy proxy từ danh sách
                proxy = PROXIES[(w * TABS_PER_WORKER + t) % len(PROXIES)]

                # Tạo context với proxy và thông tin xác thực
                async def run_task(wid=w, tid=t, proxy=proxy):
                    async with sem:
                        context = await browser.new_context(
                            proxy={"server": proxy["server"]},
                            http_credentials={"username": proxy["username"], "password": proxy["password"]}
                        )
                        page = await context.new_page()  # Tạo tab mới trong context
                        try:
                            return await worker_task(page, wid, tid)
                        finally:
                            await context.close()  # Đóng context sau khi hoàn thành

                # Thêm tác vụ vào danh sách
                tasks.append(asyncio.create_task(run_task()))

        # gather results
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # persist results
        with OUTPUT_CSV.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for res in results:
                if isinstance(res, Exception):
                    print("Task raised exception:", res)
                    writer.writerow(["", "", "", "", "error", str(res)])
                else:
                    if res.get("status") == "ok":
                        email = res.get("email", "")
                        writer.writerow([email, "", "", "", "ok", ""])
                    else:
                        writer.writerow([res.get("email", ""), "", "", "", res.get("status"), res.get("reason", "")])

        # Đóng trình duyệt sau khi hoàn thành
        #await browser.close()
        print("Trình duyệt đã được đóng.")
    print("Hoàn tất. Kết quả lưu ở", OUTPUT_CSV)

async def test_proxy(proxy):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # headless=True để test nhanh hơn
        try:
            print(f"Đang kiểm tra proxy: {proxy['server']} với username: {proxy.get('username')} và password: {proxy.get('password')}")
            context = await browser.new_context(
                proxy={
                    "server": proxy["server"],
                    "username": proxy.get("username"),
                    "password": proxy.get("password")
                }
            )
            page = await context.new_page()
            await page.goto("https://httpbin.org/ip", timeout=15000)  # timeout 15s
            content = await page.text_content("pre")
            print(f"[OK] Proxy {proxy['server']} hoạt động. IP hiển thị: {content}")
        except Exception as e:
            print(f"[FAIL] Proxy {proxy['server']} không hoạt động. Lỗi: {e}")
        finally:
            print(f"[FAIL] Proxy {proxy['server']} không hoạt động.")

            #await browser.close()


if __name__ == "__main__":
    async def main():
        for proxy in PROXIES:
            await test_proxy(proxy)

    asyncio.run(main())
