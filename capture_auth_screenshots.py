import time
import os
import shutil
import traceback
from playwright.sync_api import sync_playwright

def capture_auth_screenshots():
    out_dir = "UI-screenshoots"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1920px browser width, keeping landscape height
    VIEWPORT = {'width': 1920, 'height': 1080}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT)
        page = context.new_page()

        try:
            print("Capturing Role Selection Page...")
            page.goto("http://127.0.0.1:8000/roles")
            time.sleep(2)  # Wait for animations
            page.screenshot(path=os.path.join(out_dir, "role_selection.png"))

            print("Clicking Student Role...")
            page.click(".role-card[data-role='student']")
            time.sleep(1)
            page.click("#continueBtn")
            
            # Wait for navigation to login page
            page.wait_for_url("**/login")
            time.sleep(1.5)
            
            print("Capturing Login Page...")
            page.screenshot(path=os.path.join(out_dir, "login_page.png"))

            print("✅ Auth UI screenshots captured successfully into UI-screenshoots/")

        except Exception as e:
            print("Failed capturing screenshot on URL:", page.url)
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    capture_auth_screenshots()
