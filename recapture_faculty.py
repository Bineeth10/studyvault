import time
import os
import traceback
from playwright.sync_api import sync_playwright

def recapture_faculty_approval():
    out_dir = "UI-screenshoots"
    target_file = os.path.join(out_dir, "faculty_review_notes.png")
    
    # 1. Delete previous screenshot if it exists
    if os.path.exists(target_file):
        os.remove(target_file)
        print(f"Deleted old screenshot: {target_file}")
    
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
            
            print("Navigating to Faculty Review Notes...")
            page.goto("http://127.0.0.1:8000/faculty/approvals")
            time.sleep(2)  # Wait for rows, AI badges, and the new title to render
            
            print("Capturing updated Faculty Review Notes screenshot...")
            page.screenshot(path=target_file)

            print("Logging out Faculty...")
            page.goto("http://127.0.0.1:8000/logout")
            time.sleep(1)

            print("✅ New Faculty Approvals screenshot captured perfectly into UI-screenshoots/faculty_review_notes.png")

        except Exception as e:
            print("Failed capturing screenshot on URL:", page.url)
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    recapture_faculty_approval()
