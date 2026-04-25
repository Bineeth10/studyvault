# How to Compile the LaTeX Report

## Prerequisites
- Install **MiKTeX** or **TeX Live** (LaTeX distribution)
- The `sgcproject.cls` document class file must be in the same folder as `report.tex`
- All required images are already in `../UI-screenshoots/` (relative to the report/ folder)

## Folder Structure Required
```
studyvault/
├── UI-screenshoots/          ← All images used in the report
│   ├── dfd_level0.png
│   ├── dfd_level1.png
│   ├── use_case_diagram.png
│   ├── database_schema.png
│   ├── role_selection.png
│   ├── login_page.png
│   ├── student_dashboard.png
│   ├── faculty_dashboard.png
│   ├── admin_dashboard.png
│   ├── upload_notes.png
│   ├── browse_notes.png
│   ├── faculty_review_notes.png
│   ├── manage_users.png
│   ├── reports_moderation.png
│   └── ai_assistant.png
└── report/
    ├── report.tex            ← Main LaTeX source (compile from here)
    ├── sgcproject.cls        ← Place your college's class file here
    └── README_COMPILE.md
```

## Compile Commands (run pdflatex TWICE for correct TOC / LoF / LoT)

```powershell
cd C:\Users\Lenovo\studyvault\report
pdflatex report.tex
pdflatex report.tex
```

The output will be `report.pdf` in the same folder.

## Using Overleaf
1. Create a new project on https://overleaf.com
2. Upload `report.tex` and `sgcproject.cls`
3. Create a folder called `UI-screenshoots` and upload all PNG images into it
4. Set the **main document** to `report.tex` and click **Compile**

## Image Path Note
All images are referenced with `../UI-screenshoots/<filename>.png`.
This path resolves correctly when you compile from inside the `report/` directory.
Do NOT move the `UI-screenshoots` folder or rename images after placing them.

## Troubleshooting
| Problem | Solution |
|---|---|
| `File not found: sgcproject.cls` | Copy the class file into the `report/` folder |
| `Cannot find image file` | Make sure every PNG listed above is in `UI-screenshoots/` |
| TOC/LoF page numbers wrong | Run `pdflatex` a second time |
| `appendices` package missing | Install `appendix` package via MiKTeX package manager |
| `listings` package missing | Install `listings` package via MiKTeX package manager |
