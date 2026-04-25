import urllib.request
import json
import os
from PIL import Image
import io

plantuml_code = '''@startuml
skinparam dpi 300
skinparam defaultFontName Arial
skinparam titleFontSize 18
skinparam nodesep 60
skinparam ranksep 100

skinparam rectangle {
  BackgroundColor White
  BorderColor Black
  ArrowColor #333333
  FontSize 15
  FontWeight bold
}

skinparam usecase {
  BackgroundColor White
  BorderColor Black
  FontSize 16
  FontWeight bold
}

title "StudyVault – Online Notes Sharing Platform with AI Moderation\\nLevel-0 Data Flow Diagram"

left to right direction

rectangle "Student" as Student
rectangle "Faculty" as Faculty
rectangle "Admin" as Admin

usecase "0\\nStudyVault Notes\\nSharing System" as System

Student -right-> System : Upload Notes\\nBrowse Notes\\nDownload Notes\\nUse AI Study Assistant
System -left-> Student : Notifications\\nStudy Material Access\\nAI Study Assistance

System <-right- Faculty : Review Requests\\nModerate Notes
Faculty <-left- System : Notes for Approval\\nAI Safety Results

System <-right- Admin : Manage Users\\nManage Subjects\\nModerate Reports
Admin <-left- System : System Activity\\nUser Reports

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
print("Generating Level-0 Data Flow Diagram...")
try:
    with urllib.request.urlopen(req) as response:
        png_data = response.read()

    img = Image.open(io.BytesIO(png_data))
    
    out_dir = "UI-screenshoots"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'dfd_level0.png')
    
    img.save(out_path, format="PNG")
    print(f"✅ DFD Level-0 Diagram successfully generated and saved to: {out_path}")
except Exception as e:
    print(f"Failed to generate diagram: {e}")
