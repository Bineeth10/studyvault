import time
import os
import traceback
from playwright.sync_api import sync_playwright

def capture_student_screenshots():
    out_dir = "UI-screenshoots"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1920px width, height tuned to crop out bottom whitespace while keeping the main content
    VIEWPORT = {'width': 1920, 'height': 850}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT)
        page = context.new_page()

        try:
            print("Logging in as Student...")
            page.goto("http://127.0.0.1:8000/login")
            page.fill("input[name='email']", "bineethbaby2005@gmail.com")
            page.fill("input[name='password']", "bineeth@123B")
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            print("Capturing Student Dashboard...")
            page.screenshot(path=os.path.join(out_dir, "student_dashboard.png"))

            print("Capturing Upload Notes...")
            page.goto("http://127.0.0.1:8000/student/upload")
            time.sleep(2)
            page.screenshot(path=os.path.join(out_dir, "upload_notes.png"))

            print("Capturing Browse Notes...")
            page.goto("http://127.0.0.1:8000/student/browse")
            time.sleep(2)
            page.screenshot(path=os.path.join(out_dir, "browse_notes.png"))

            print("Capturing AI Assistant...")
            page.goto("http://127.0.0.1:8000/student/ai")
            time.sleep(2)
            # Only capture the cards grid area to avoid the empty "About AI Assistant" section
            try:
                tools_grid = page.locator(".ai-cards-container")
                tools_grid.screenshot(path=os.path.join(out_dir, "ai_assistant.png"))
            except Exception as e:
                print("Locator failed, falling back to viewport cropped screenshot...")
                page.screenshot(path=os.path.join(out_dir, "ai_assistant.png"), clip={'x': 0, 'y': 0, 'width': 1920, 'height': 800})

            print("Logging out Student...")
            page.goto("http://127.0.0.1:8000/logout")
            time.sleep(1)

            print("✅ Student UI screenshots captured successfully into UI-screenshoots/")

        except Exception as e:
            print("Failed capturing screenshot on URL:", page.url)
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    capture_student_screenshots()
