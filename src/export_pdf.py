"""
PDF Export Module - Convert markdown reports to professional PDFs

This module takes generated markdown reports and converts them to beautifully
formatted, customer-ready PDF documents worth $800 in value.

Features:
- Markdown → HTML → PDF pipeline
- Professional styling with custom CSS
- Client and Publitz branding
- Print-optimized layout
- Table of contents generation
- Page numbering and headers/footers
"""

import markdown
from markdown.extensions import tables, fenced_code, toc
from weasyprint import HTML, CSS
from jinja2 import Template
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import re

from config import Config


class PDFExporter:
    """
    Export markdown audit reports to professional PDF documents.

    Uses markdown → HTML → PDF pipeline with custom styling.
    """

    def __init__(self):
        """Initialize PDF exporter with templates and styles."""
        self.template_dir = Config.TEMPLATE_DIR
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Load HTML template
        self.html_template = self._load_html_template()

        # Load CSS styles
        self.css_styles = self._load_css_styles()

    def export_to_pdf(
        self,
        markdown_content: str,
        game_name: str,
        client_name: str,
        output_path: Path
    ) -> Path:
        """
        Convert markdown report to PDF.

        Args:
            markdown_content: The markdown report content
            game_name: Name of the game being audited
            client_name: Name of the client
            output_path: Path where PDF should be saved

        Returns:
            Path to the generated PDF file
        """
        print("\n" + "="*80)
        print("📄 PDF EXPORT")
        print("="*80)

        print("\n⏳ Converting markdown to HTML...")

        # Convert markdown to HTML
        html_content = self._markdown_to_html(markdown_content)

        print("⏳ Applying professional styling...")

        # Generate final HTML with template
        final_html = self._apply_template(
            html_content,
            game_name,
            client_name
        )

        print("⏳ Rendering PDF (this may take 10-20 seconds)...")

        # Convert HTML to PDF
        pdf_path = self._html_to_pdf(final_html, output_path)

        print(f"✅ PDF generated: {pdf_path.name}")
        print(f"📊 File size: {pdf_path.stat().st_size / 1024:.1f} KB\n")

        return pdf_path

    def _markdown_to_html(self, markdown_content: str) -> str:
        """
        Convert markdown to HTML with extensions.

        Args:
            markdown_content: Raw markdown text

        Returns:
            HTML string
        """
        # Configure markdown extensions
        extensions = [
            'tables',           # Tables support
            'fenced_code',      # Code blocks
            'toc',              # Table of contents
            'nl2br',            # Newline to <br>
            'sane_lists',       # Better list handling
        ]

        # Configure markdown
        md = markdown.Markdown(
            extensions=extensions,
            extension_configs={
                'toc': {
                    'title': 'Table of Contents',
                    'baselevel': 2,
                }
            }
        )

        # Convert to HTML
        html = md.convert(markdown_content)

        return html

    def _apply_template(
        self,
        html_content: str,
        game_name: str,
        client_name: str
    ) -> str:
        """
        Apply HTML template with branding and styling.

        Args:
            html_content: Converted HTML from markdown
            game_name: Game name for header
            client_name: Client name for branding

        Returns:
            Complete HTML document
        """
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")

        # Create Jinja2 template
        template = Template(self.html_template)

        # Render template
        final_html = template.render(
            title=f"Pre-Launch Steam Audit: {game_name}",
            game_name=game_name,
            client_name=client_name,
            date=current_date,
            content=html_content,
            css=self.css_styles
        )

        return final_html

    def _html_to_pdf(self, html_content: str, output_path: Path) -> Path:
        """
        Convert HTML to PDF using WeasyPrint.

        Args:
            html_content: Complete HTML document
            output_path: Where to save the PDF

        Returns:
            Path to generated PDF
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to PDF
        HTML(string=html_content).write_pdf(output_path)

        return output_path

    def _load_html_template(self) -> str:
        """
        Load HTML template for PDF generation.

        Returns:
            HTML template string
        """
        template_path = self.template_dir / "pdf_template.html"

        if template_path.exists():
            return template_path.read_text()
        else:
            # Return embedded default template
            return self._get_default_html_template()

    def _load_css_styles(self) -> str:
        """
        Load CSS styles for PDF.

        Returns:
            CSS stylesheet string
        """
        css_path = self.template_dir / "pdf_styles.css"

        if css_path.exists():
            return css_path.read_text()
        else:
            # Return embedded default styles
            return self._get_default_css_styles()

    def _get_default_html_template(self) -> str:
        """
        Get default HTML template if template file doesn't exist.

        Returns:
            Default HTML template string
        """
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        {{ css }}
    </style>
</head>
<body>
    <div class="cover-page">
        <div class="cover-content">
            <div class="publitz-logo">
                <h1>PUBLITZ</h1>
                <p class="tagline">Professional Game Publishing Audits</p>
            </div>

            <div class="report-title">
                <h2>Pre-Launch Steam Audit</h2>
                <h3>{{ game_name }}</h3>
            </div>

            <div class="client-info">
                <p><strong>Prepared for:</strong> {{ client_name }}</p>
                <p><strong>Date:</strong> {{ date }}</p>
            </div>
        </div>
    </div>

    <div class="content">
        {{ content }}
    </div>

    <div class="footer">
        <p>© {{ date.split()[-1] }} Publitz - Professional Game Publishing Audits</p>
    </div>
</body>
</html>"""

    def _get_default_css_styles(self) -> str:
        """
        Get default CSS styles if styles file doesn't exist.

        Returns:
            Default CSS stylesheet string
        """
        return """
        /* Professional PDF Styles for Publitz Audits */

        /* Page setup */
        @page {
            size: A4;
            margin: 2cm 2.5cm;

            @top-center {
                content: "Pre-Launch Steam Audit";
                font-family: 'Arial', sans-serif;
                font-size: 10pt;
                color: #666;
            }

            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-family: 'Arial', sans-serif;
                font-size: 9pt;
                color: #666;
            }
        }

        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', 'Helvetica', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }

        /* Cover page */
        .cover-page {
            page-break-after: always;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: -2cm -2.5cm;
            padding: 2cm;
        }

        .cover-content {
            max-width: 600px;
        }

        .publitz-logo h1 {
            font-size: 48pt;
            font-weight: bold;
            letter-spacing: 4px;
            margin-bottom: 10px;
        }

        .publitz-logo .tagline {
            font-size: 14pt;
            opacity: 0.9;
            margin-bottom: 60px;
        }

        .report-title h2 {
            font-size: 32pt;
            margin-bottom: 20px;
            font-weight: 300;
        }

        .report-title h3 {
            font-size: 24pt;
            margin-bottom: 60px;
            font-weight: 500;
        }

        .client-info {
            font-size: 14pt;
            opacity: 0.9;
        }

        .client-info p {
            margin: 10px 0;
        }

        /* Content area */
        .content {
            padding: 20px 0;
        }

        /* Headings */
        h1 {
            font-size: 28pt;
            color: #667eea;
            margin: 40px 0 20px 0;
            page-break-after: avoid;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }

        h2 {
            font-size: 22pt;
            color: #764ba2;
            margin: 30px 0 15px 0;
            page-break-after: avoid;
        }

        h3 {
            font-size: 16pt;
            color: #555;
            margin: 20px 0 10px 0;
            page-break-after: avoid;
        }

        h4 {
            font-size: 13pt;
            color: #666;
            margin: 15px 0 10px 0;
            page-break-after: avoid;
        }

        /* Paragraphs */
        p {
            margin: 10px 0;
            text-align: justify;
        }

        /* Lists */
        ul, ol {
            margin: 15px 0 15px 30px;
        }

        li {
            margin: 8px 0;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            page-break-inside: avoid;
        }

        th {
            background-color: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }

        td {
            border: 1px solid #ddd;
            padding: 10px;
        }

        tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        /* Code blocks */
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }

        pre {
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
            page-break-inside: avoid;
        }

        pre code {
            background: none;
            padding: 0;
        }

        /* Blockquotes */
        blockquote {
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
            color: #555;
        }

        /* Horizontal rules */
        hr {
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }

        /* Links */
        a {
            color: #667eea;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        /* Badges and icons (emojis) */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 10pt;
            font-weight: bold;
            margin: 0 5px;
        }

        .badge-success {
            background-color: #4CAF50;
            color: white;
        }

        .badge-warning {
            background-color: #FF9800;
            color: white;
        }

        .badge-danger {
            background-color: #f44336;
            color: white;
        }

        /* Strong emphasis */
        strong {
            color: #333;
            font-weight: bold;
        }

        em {
            font-style: italic;
        }

        /* Page breaks */
        .page-break {
            page-break-after: always;
        }

        /* Footer */
        .footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 9pt;
        }

        /* Print optimizations */
        @media print {
            body {
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }
        }
        """


def export_report_to_pdf(
    markdown_path: Path,
    game_name: str,
    client_name: str,
    output_dir: Path
) -> Path:
    """
    Convenience function to export a markdown report to PDF.

    Args:
        markdown_path: Path to markdown report file
        game_name: Name of the game
        client_name: Name of the client
        output_dir: Directory where PDF should be saved

    Returns:
        Path to generated PDF file
    """
    # Read markdown content
    markdown_content = markdown_path.read_text()

    # Generate PDF filename
    pdf_filename = markdown_path.stem + ".pdf"
    pdf_path = output_dir / pdf_filename

    # Create exporter and generate PDF
    exporter = PDFExporter()
    return exporter.export_to_pdf(
        markdown_content,
        game_name,
        client_name,
        pdf_path
    )


if __name__ == "__main__":
    """Test PDF export module"""
    print("PDF Export Module")
    print("=" * 80)
    print("\nThis module converts markdown audit reports to professional PDFs.")
    print("\nUsage:")
    print("  from src.export_pdf import export_report_to_pdf")
    print("  pdf_path = export_report_to_pdf(")
    print("      markdown_path=Path('output/client/report.md'),")
    print("      game_name='My Awesome Game',")
    print("      client_name='Awesome Studio',")
    print("      output_dir=Path('output/client')")
    print("  )")
    print("\nRequires:")
    print("  - markdown")
    print("  - weasyprint")
    print("  - jinja2")
