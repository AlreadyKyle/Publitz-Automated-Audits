"""PDF report generation from AI-generated content."""

from typing import Dict, Any
from datetime import datetime
import markdown
from weasyprint import HTML, CSS
from io import BytesIO
import os


class ReportGenerator:
    """Generate professional PDF reports."""

    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')

    def generate_pdf(self, report_data: Dict[str, Any], output_path: str = None) -> BytesIO:
        """
        Generate PDF report from structured data.

        Args:
            report_data: Structured report data from AI generator
            output_path: Optional file path to save PDF

        Returns:
            BytesIO buffer containing PDF data
        """
        # Convert report to HTML
        html_content = self._generate_html(report_data)

        # Generate PDF
        pdf_buffer = BytesIO()

        HTML(string=html_content).write_pdf(
            pdf_buffer,
            stylesheets=[CSS(string=self._get_css())]
        )

        pdf_buffer.seek(0)

        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            pdf_buffer.seek(0)

        return pdf_buffer

    def _generate_html(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML from report data."""

        game_name = report_data.get('game_name', 'Unknown Game')
        report_type = report_data.get('report_type', 'audit')
        report_text = report_data.get('report_text', '')
        generated_at = datetime.now().strftime('%B %d, %Y')

        # Convert markdown to HTML
        report_html = markdown.markdown(
            report_text,
            extensions=['tables', 'fenced_code', 'nl2br']
        )

        # Build full HTML document
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{game_name} - Steam Audit Report</title>
</head>
<body>
    <div class="header">
        <h1>{'Pre-Launch' if report_type == 'pre_launch' else 'Post-Launch'} Steam Audit Report</h1>
        <div class="game-info">
            <h2>{game_name}</h2>
            <p class="date">Report Generated: {generated_at}</p>
            <p class="author">By: Kyle Smith</p>
        </div>
    </div>

    <div class="content">
        {report_html}
    </div>

    <div class="footer">
        <p>Publitz - Steam Launch Optimization</p>
        <p class="disclaimer">This report is confidential and intended for internal use only.</p>
    </div>
</body>
</html>
"""

        return html

    def _get_css(self) -> str:
        """Get CSS styling for the PDF report."""

        css = """
@page {
    size: Letter;
    margin: 1in;
    @top-right {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #666;
    }
}

body {
    font-family: 'Helvetica', 'Arial', sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #333;
}

.header {
    margin-bottom: 30px;
    border-bottom: 3px solid #0066cc;
    padding-bottom: 20px;
}

.header h1 {
    color: #0066cc;
    font-size: 24pt;
    margin: 0 0 10px 0;
    font-weight: bold;
}

.game-info h2 {
    font-size: 18pt;
    margin: 15px 0 5px 0;
    color: #333;
}

.game-info .date,
.game-info .author {
    font-size: 10pt;
    color: #666;
    margin: 3px 0;
}

.content {
    margin: 30px 0;
}

h1 {
    font-size: 18pt;
    color: #0066cc;
    margin: 25px 0 15px 0;
    padding-top: 10px;
    border-top: 2px solid #e0e0e0;
    page-break-after: avoid;
}

h2 {
    font-size: 14pt;
    color: #0066cc;
    margin: 20px 0 10px 0;
    page-break-after: avoid;
}

h3 {
    font-size: 12pt;
    color: #333;
    margin: 15px 0 8px 0;
    font-weight: bold;
    page-break-after: avoid;
}

h4 {
    font-size: 11pt;
    color: #555;
    margin: 12px 0 6px 0;
    font-weight: bold;
}

p {
    margin: 8px 0;
    text-align: justify;
}

ul, ol {
    margin: 10px 0;
    padding-left: 25px;
}

li {
    margin: 5px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    page-break-inside: avoid;
}

th {
    background-color: #0066cc;
    color: white;
    padding: 10px;
    text-align: left;
    font-weight: bold;
    font-size: 10pt;
}

td {
    padding: 8px;
    border: 1px solid #ddd;
    font-size: 9pt;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

.highlight {
    background-color: #fff3cd;
    padding: 15px;
    border-left: 4px solid #ffc107;
    margin: 15px 0;
}

.warning {
    background-color: #f8d7da;
    padding: 15px;
    border-left: 4px solid #dc3545;
    margin: 15px 0;
}

.success {
    background-color: #d4edda;
    padding: 15px;
    border-left: 4px solid #28a745;
    margin: 15px 0;
}

.info {
    background-color: #d1ecf1;
    padding: 15px;
    border-left: 4px solid #17a2b8;
    margin: 15px 0;
}

blockquote {
    border-left: 4px solid #0066cc;
    padding-left: 15px;
    margin: 15px 0;
    color: #555;
    font-style: italic;
}

code {
    background-color: #f4f4f4;
    padding: 2px 5px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
}

pre {
    background-color: #f4f4f4;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    page-break-inside: avoid;
}

pre code {
    background-color: transparent;
    padding: 0;
}

.footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 2px solid #e0e0e0;
    text-align: center;
    font-size: 9pt;
    color: #666;
}

.footer .disclaimer {
    font-style: italic;
    margin-top: 10px;
}

/* Score boxes */
.score-box {
    display: inline-block;
    padding: 10px 20px;
    margin: 10px 10px 10px 0;
    border-radius: 5px;
    font-weight: bold;
    font-size: 12pt;
}

.score-high {
    background-color: #d4edda;
    color: #155724;
}

.score-medium {
    background-color: #fff3cd;
    color: #856404;
}

.score-low {
    background-color: #f8d7da;
    color: #721c24;
}

/* Page breaks */
.page-break {
    page-break-after: always;
}

/* Avoid breaking these elements */
.keep-together {
    page-break-inside: avoid;
}
"""

        return css

    def generate_markdown_preview(self, report_data: Dict[str, Any]) -> str:
        """
        Generate a markdown preview of the report (for Streamlit display).

        Args:
            report_data: Structured report data

        Returns:
            Markdown formatted string
        """
        game_name = report_data.get('game_name', 'Unknown Game')
        report_type = report_data.get('report_type', 'audit')
        report_text = report_data.get('report_text', '')
        generated_at = datetime.now().strftime('%B %d, %Y')

        title = 'Pre-Launch' if report_type == 'pre_launch' else 'Post-Launch'

        markdown_preview = f"""# {title} Steam Audit Report

## {game_name}

**Report Generated:** {generated_at}
**By:** Kyle Smith

---

{report_text}

---

*Publitz - Steam Launch Optimization*
*This report is confidential and intended for internal use only.*
"""

        return markdown_preview
