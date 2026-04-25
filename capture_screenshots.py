import time
import os
import shutil
import traceback
from playwright.sync_api import sync_playwright

def capture_screenshots():
    out_dir = "UI-screenshoots"
    
    # 1. Clean previous screenshots
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    
    # 2. Strict UI Layout rules (Landscape, 1600x900 viewport means no rolling white space)
    VIEWPORT = {'width': 1600, 'height': 850}
    
    with sync_playwright() as p:
        # Launch browser headless
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORT)
        page = context.new_page()

        try:
            print("Capturing Landing Pages...")
            page.goto("http://127.0.0.1:8000/roles")
            time.sleep(1)
            # Removed full_page=True to strictly capture the viewport feature area
            page.screenshot(path=os.path.join(out_dir, "role_selection.png"))

            page.goto("http://127.0.0.1:8000/login")
            time.sleep(1)
            page.screenshot(path=os.path.join(out_dir, "login_page.png"))

            # --- STEP 2: STUDENT ---
            print("Logging in as Student...")
            page.fill("input[name='email']", "bineethbaby2005@gmail.com")
            page.fill("input[name='password']", "bineeth@123B")
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            time.sleep(1.5)
            
            print("Capturing Student Dashboard...")
            page.screenshot(path=os.path.join(out_dir, "student_dashboard.png"))

            print("Capturing Upload Notes...")
            page.goto("http://127.0.0.1:8000/student/upload")
            time.sleep(1.5)
            page.screenshot(path=os.path.join(out_dir, "upload_notes.png"))

            print("Capturing Browse Notes...")
            page.goto("http://127.0.0.1:8000/student/browse")
            time.sleep(1.5)
            page.screenshot(path=os.path.join(out_dir, "browse_notes.png"))

            print("Capturing AI Assistant...")
            page.goto("http://127.0.0.1:8000/student/ai")
            time.sleep(1.5)
            # Only capture the cards grid area to avoid the empty "About" space scrolling
            try:
                # Select the direct grid containing the tools
                tools_grid = page.locator(".ai-cards-container")
                tools_grid.screenshot(path=os.path.join(out_dir, "ai_assistant.png"))
            except:
                # Fallback to viewport if selector fails
                page.screenshot(path=os.path.join(out_dir, "ai_assistant.png"))

            print("Logging out Student...")
            page.goto("http://127.0.0.1:8000/logout")
            time.sleep(1)

            # --- STEP 3: FACULTY ---
            print("Logging in as Faculty...")
            page.goto("http://127.0.0.1:8000/login")
            page.fill("input[name='email']", "joseph@gmail.com")
            page.fill("input[name='password']", "bineeth@123B")
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            time.sleep(1.5)
            
            print("Capturing Faculty Dashboard...")
            page.screenshot(path=os.path.join(out_dir, "faculty_dashboard.png"))

            print("Capturing Faculty Review Notes...")
            page.goto("http://127.0.0.1:8000/faculty/approvals")
            time.sleep(1.5)
            page.screenshot(path=os.path.join(out_dir, "faculty_review_notes.png"))

            print("Logging out Faculty...")
            page.goto("http://127.0.0.1:8000/logout")
            time.sleep(1)

            # --- STEP 4: ADMIN ---
            print("Logging in as Admin...")
            page.goto("http://127.0.0.1:8000/login")
            page.fill("input[name='email']", "A001@studyvault.com")
            page.fill("input[name='password']", "bineeth@123B")
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            time.sleep(1.5)
            
            print("Capturing Admin Dashboard...")
            page.screenshot(path=os.path.join(out_dir, "admin_dashboard.png"))

            print("Capturing Manage Users...")
            page.goto("http://127.0.0.1:8000/admin/users")
            time.sleep(1.5)
            page.screenshot(path=os.path.join(out_dir, "manage_users.png"))

            print("Capturing Reports Moderation...")
            page.goto("http://127.0.0.1:8000/admin/reports")
            time.sleep(1.5)
            page.screenshot(path=os.path.join(out_dir, "reports_moderation.png"))

            print("Logging out Admin...")
            page.goto("http://127.0.0.1:8000/logout")

            print("✅ Perfect landscape UI screenshots captured directly into UI-screenshoots/")

        except Exception as e:
            print("Failed capturing screenshot on URL:", page.url)
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    capture_screenshots()
