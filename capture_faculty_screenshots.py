import time
import os
import traceback
from playwright.sync_api import sync_playwright

def capture_faculty_screenshots():
    out_dir = "UI-screenshoots"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1920px width, height tuned to crop out bottom whitespace while keeping the main content
    VIEWPORT = {'width': 1920, 'height': 850}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT)
        page = context.new_page()

        try:
            print("Going to Role Selection Page...")
            page.goto("http://127.0.0.1:8000/roles")
            time.sleep(1)

            print("Clicking Faculty Role...")
            page.click(".role-card[data-role='faculty']")
            time.sleep(1)
            page.click("#continueBtn")
            
            # Wait for navigation to login page
            page.wait_for_url("**/login")
            time.sleep(1)

            print("Logging in as Faculty...")
            page.fill("input[name='email']", "joseph@gmail.com")
            page.fill("input[name='password']", "bineeth@123B")
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            print("Capturing Faculty Dashboard...")
            page.screenshot(path=os.path.join(out_dir, "faculty_dashboard.png"))

            print("Capturing Faculty Review Notes...")
            page.goto("http://127.0.0.1:8000/faculty/approvals")
            time.sleep(2)
            # Ensure elements like AI safety bags and approve/reject buttons render
            page.screenshot(path=os.path.join(out_dir, "faculty_review_notes.png"))

            print("Logging out Faculty...")
            page.goto("http://127.0.0.1:8000/logout")
            time.sleep(1)

            print("✅ Faculty UI screenshots captured successfully into UI-screenshoots/")

        except Exception as e:
            print("Failed capturing screenshot on URL:", page.url)
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    capture_faculty_screenshots()
