import urllib.request
import json
import os
from PIL import Image, ImageOps
import io

plantuml_code = '''@startuml
skinparam dpi 300
skinparam defaultFontName Arial
skinparam titleFontSize 18
skinparam usecase {
  BackgroundColor White
  BorderColor Black
  ArrowColor #333333
}
skinparam actor {
  BackgroundColor White
  BorderColor Black
}
skinparam rectangle {
  BorderColor #666666
  BackgroundColor Transparent
}

title StudyVault - Online Notes Sharing Platform with AI Moderation

left to right direction

actor "Student" as student
actor "Faculty" as faculty
actor "Admin" as admin

rectangle "StudyVault System" {
  usecase "Register Account" as s1
  usecase "Login" as s2
  usecase "Upload Notes" as s3
  usecase "View My Notes" as s4
  usecase "Browse Notes" as s5
  usecase "Download Notes" as s6
  usecase "Add to Favorites" as s7
  usecase "Send Messages" as s8
  usecase "Use AI Study Assistant" as sAI
  usecase "Generate Summary" as ai1
  usecase "Create Flashcards" as ai2
  usecase "Ask Questions" as ai3
  usecase "View Announcements" as s9
  usecase "Receive Notifications" as s10

  usecase "View Uploaded Notes" as f1
  usecase "Review Notes" as f2
  usecase "Approve Notes" as f3
  usecase "Reject Notes" as f4
  usecase "View AI Safety Results" as f5
  usecase "Report Plagiarism" as f6

  usecase "Manage Users" as a1
  usecase "Manage Subjects" as a2
  usecase "Manage Announcements" as a3
  usecase "Moderate Reports" as a4
  usecase "Monitor System" as a5
}

student --> s1
student --> s2
student --> s3
student --> s4
student --> s5
student --> s6
student --> s7
student --> s8
student --> sAI
student --> s9
student --> s10

sAI <.. ai1 : <<include>>
sAI <.. ai2 : <<include>>
sAI <.. ai3 : <<include>>

s2 <-- faculty
f1 <-- faculty
f2 <-- faculty
f3 <-- faculty
f4 <-- faculty
f5 <-- faculty
f6 <-- faculty

s2 <-- admin
a1 <-- admin
a2 <-- admin
a3 <-- admin
a4 <-- admin
a5 <-- admin

@enduml'''

data = {
    "diagram_source": plantuml_code,
    "diagram_type": "plantuml",
    "output_format": "png"
}

req = urllib.request.Request(
    'https://kroki.io/', 
    data=json.dumps(data).encode('utf-8'), 
    headers={
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
)
print("Generating 1400x800 Landscape UML Use Case Diagram...")
try:
    with urllib.request.urlopen(req) as response:
        png_data = response.read()

    # Load image in PIL
    img = Image.open(io.BytesIO(png_data))
    
    # Calculate exactly 1400x800 bounding box with padding
    target_width, target_height = 1400, 800
    
    # Fit the image nicely into the dimensions, preserving aspect ratio and padding with white
    img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Create white canvas and paste
    new_img = Image.new("RGB", (target_width, target_height), "white")
    x_offset = (target_width - img.width) // 2
    y_offset = (target_height - img.height) // 2
    new_img.paste(img, (x_offset, y_offset))

    out_dir = "UI-screenshoots"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'use_case_diagram.png')
    
    new_img.save(out_path, format="PNG")
    print(f"✅ Diagram successfully saved to: {out_path} (Resolution: 1400x800)")
except Exception as e:
    print(f"Failed to generate diagram: {e}")
