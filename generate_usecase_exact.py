import urllib.request
import json
import os
from PIL import Image
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

title StudyVault – Online Notes Sharing Platform with AI Moderation

left to right direction

actor Student
actor Faculty
actor Admin

rectangle "StudyVault System" {

  (Register Account) as UC1
  (Login) as UC2
  (Upload Notes) as UC3
  (View My Notes) as UC4
  (Browse Notes) as UC5
  (Download Notes) as UC6
  (Add to Favorites) as UC7
  (Send Messages) as UC8
  (View Announcements) as UC9
  (Receive Notifications) as UC10

  (Use AI Study Assistant) as UC11
  (Generate Summary) as UC12
  (Create Flashcards) as UC13
  (Ask Questions) as UC14

  (View Uploaded Notes) as UC15
  (Review Notes) as UC16
  (Approve Notes) as UC17
  (Reject Notes) as UC18
  (View AI Safety Results) as UC19
  (Report Plagiarism) as UC20

  (Manage Users) as UC21
  (Manage Subjects) as UC22
  (Manage Announcements) as UC23
  (Moderate Reports) as UC24
  (Monitor System) as UC25
}

Student --> UC1
Student --> UC2
Student --> UC3
Student --> UC4
Student --> UC5
Student --> UC6
Student --> UC7
Student --> UC8
Student --> UC9
Student --> UC10
Student --> UC11

UC11 --> UC12
UC11 --> UC13
UC11 --> UC14

Faculty --> UC2
Faculty --> UC15
Faculty --> UC16
Faculty --> UC17
Faculty --> UC18
Faculty --> UC19
Faculty --> UC20

Admin --> UC2
Admin --> UC21
Admin --> UC22
Admin --> UC23
Admin --> UC24
Admin --> UC25

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
