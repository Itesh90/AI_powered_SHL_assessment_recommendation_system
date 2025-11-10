"""
Script to convert APPROACH.md to a 2-page PDF report
Creates an HTML file that can be printed to PDF from browser
"""
import markdown
from pathlib import Path

def create_pdf_report():
    """Convert APPROACH.md to HTML for PDF conversion"""
    # Read the markdown file
    md_file = Path("APPROACH.md")
    if not md_file.exists():
        print("Error: APPROACH.md not found")
        return
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    try:
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'tables']
        )
    except:
        # Fallback if extensions not available
        html_content = markdown.markdown(md_content)
    
    # Wrap in HTML document with styling for 2-page layout
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SHL Assessment Recommendation System - Approach Document</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-size: 10pt;
            }}
        }}
        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #333;
            max-width: 100%;
            margin: 0;
            padding: 20px;
        }}
        h1 {{
            font-size: 18pt;
            margin-top: 0;
            margin-bottom: 12pt;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8pt;
        }}
        h2 {{
            font-size: 14pt;
            margin-top: 16pt;
            margin-bottom: 8pt;
            color: #34495e;
            page-break-after: avoid;
        }}
        h3 {{
            font-size: 12pt;
            margin-top: 12pt;
            margin-bottom: 6pt;
            color: #555;
            page-break-after: avoid;
        }}
        p {{
            margin: 6pt 0;
            text-align: justify;
        }}
        ul, ol {{
            margin: 8pt 0;
            padding-left: 20pt;
        }}
        li {{
            margin: 4pt 0;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2pt 4pt;
            border-radius: 3pt;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 8pt;
            border-radius: 4pt;
            overflow-x: auto;
            font-size: 9pt;
            page-break-inside: avoid;
        }}
        strong {{
            color: #2c3e50;
            font-weight: bold;
        }}
        .print-instructions {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        @media print {{
            .print-instructions {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="print-instructions">
        <strong>To create PDF:</strong><br>
        1. Press <strong>Ctrl+P</strong> (or Cmd+P on Mac)<br>
        2. Select "Save as PDF" as the destination<br>
        3. Set margins to "Minimum" or "None"<br>
        4. Enable "Background graphics"<br>
        5. Click "Save"
    </div>
    {html_content}
</body>
</html>"""
    
    # Save HTML file
    html_file = Path("APPROACH_REPORT.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"[OK] HTML report created: {html_file}")
    print(f"   File size: {html_file.stat().st_size / 1024:.1f} KB")
    print("\nTo create PDF:")
    print("   1. Open APPROACH_REPORT.html in your browser")
    print("   2. Press Ctrl+P (or Cmd+P on Mac)")
    print("   3. Select 'Save as PDF'")
    print("   4. Set margins to 'Minimum'")
    print("   5. Click 'Save'")
    print("\n   The HTML file is optimized for 2-page printing.")

if __name__ == "__main__":
    create_pdf_report()

