#!/usr/bin/env python3
"""
PDF Report Generator
Converts markdown audit reports to professional PDFs
"""

from fpdf import FPDF
import re
from datetime import datetime
from typing import Dict, Any


class PDFReportGenerator(FPDF):
    """Custom PDF generator for audit reports with professional formatting"""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)

        # Professional color palette
        self.color_primary = (41, 128, 185)      # Professional blue
        self.color_secondary = (52, 73, 94)      # Dark slate gray
        self.color_accent = (46, 204, 113)       # Success green
        self.color_warning = (241, 196, 15)      # Warning amber
        self.color_text = (50, 50, 50)           # Dark gray text
        self.color_light_gray = (245, 245, 245)  # Light background

    def header(self):
        """Add professional header to each page"""
        if self.page_no() == 1:
            return  # Skip header on title page

        # Header bar with gradient-like effect
        self.set_fill_color(250, 250, 250)
        self.rect(10, 10, 190, 15, 'F')

        # Company name and report title
        self.set_font('Arial', 'B', 11)
        self.set_text_color(*self.color_primary)
        self.set_xy(15, 13)
        self.cell(100, 8, 'PUBLITZ GAME AUDIT REPORT', 0, 0, 'L')

        # Page indicator
        self.set_font('Arial', '', 9)
        self.set_text_color(120, 120, 120)
        self.set_xy(140, 13)
        self.cell(50, 8, 'CONFIDENTIAL', 0, 0, 'R')

        self.ln(20)

    def footer(self):
        """Add professional footer to each page"""
        self.set_y(-20)

        # Footer separator line
        self.set_draw_color(200, 200, 200)
        self.line(20, self.get_y(), 190, self.get_y())

        self.ln(3)

        # Footer content
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)

        # Left: Copyright
        self.set_x(20)
        self.cell(60, 5, f'(c) {datetime.now().year} Publitz', 0, 0, 'L')

        # Center: Confidentiality
        self.cell(80, 5, 'This report is confidential', 0, 0, 'C')

        # Right: Page number
        self.cell(50, 5, f'Page {self.page_no()}', 0, 0, 'R')

    def chapter_title(self, title: str, level: int = 1):
        """Add a chapter title with professional styling"""

        if level == 1:
            # Major section - add page break and decorative element
            if self.get_y() > 50:  # Don't break if we're already at top
                self.add_page()

            self.ln(5)

            # Section number bar (decorative)
            self.set_fill_color(*self.color_primary)
            self.rect(15, self.get_y(), 4, 10, 'F')

            self.set_font('Arial', 'B', 18)
            self.set_text_color(*self.color_primary)
            self.set_x(25)
            self.multi_cell(0, 10, title)

            # Underline
            y = self.get_y()
            self.set_draw_color(*self.color_primary)
            self.set_line_width(0.5)
            self.line(20, y + 2, 190, y + 2)

            self.ln(8)
            self.set_text_color(*self.color_text)

        elif level == 2:
            self.ln(6)

            # Subsection with colored bar
            self.set_fill_color(*self.color_secondary)
            self.rect(17, self.get_y(), 2, 8, 'F')

            self.set_font('Arial', 'B', 14)
            self.set_text_color(*self.color_secondary)
            self.set_x(22)
            self.multi_cell(0, 7, title)
            self.ln(4)
            self.set_text_color(*self.color_text)

        else:
            self.ln(4)
            self.set_font('Arial', 'B', 12)
            self.set_text_color(*self.color_secondary)
            self.multi_cell(0, 6, title)
            self.ln(2)
            self.set_text_color(*self.color_text)

    def chapter_body(self, body: str):
        """Add chapter body text with professional spacing"""
        self.set_font('Arial', '', 10)
        self.set_text_color(*self.color_text)
        self.multi_cell(0, 6, body)
        self.ln(3)

    def add_callout_box(self, title: str, content: str, box_type: str = "info"):
        """Add a callout box for important information"""
        # Set colors based on type
        if box_type == "success":
            bg_color = (236, 255, 241)
            border_color = self.color_accent
            title_color = self.color_accent
        elif box_type == "warning":
            bg_color = (255, 249, 229)
            border_color = self.color_warning
            title_color = (200, 140, 0)
        else:  # info
            bg_color = (235, 245, 255)
            border_color = self.color_primary
            title_color = self.color_primary

        self.ln(3)

        # Draw box
        x = self.get_x()
        y = self.get_y()

        # Background
        self.set_fill_color(*bg_color)
        self.rect(x, y, 170, 20, 'F')

        # Left border accent
        self.set_fill_color(*border_color)
        self.rect(x, y, 3, 20, 'F')

        # Title
        self.set_xy(x + 8, y + 4)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*title_color)
        self.cell(0, 5, title)

        # Content
        self.set_xy(x + 8, y + 10)
        self.set_font('Arial', '', 9)
        self.set_text_color(*self.color_text)
        self.multi_cell(155, 4, content)

        self.ln(8)
        self.set_text_color(*self.color_text)

    def add_section_separator(self):
        """Add a visual separator between sections"""
        self.ln(5)
        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.3)
        self.line(30, self.get_y(), 180, self.get_y())
        self.ln(5)

    def draw_score_card(self, title: str, score: int, x: float, y: float, width: float = 80, height: float = 35):
        """
        Draw a visual score card with progress bar

        Args:
            title: Card title
            score: Score value (0-100)
            x, y: Position coordinates
            width, height: Card dimensions
        """
        # Determine color based on score
        if score >= 80:
            bar_color = (46, 204, 113)  # Green
            rating = "Excellent"
        elif score >= 65:
            bar_color = (52, 152, 219)  # Blue
            rating = "Good"
        elif score >= 50:
            bar_color = (241, 196, 15)  # Yellow
            rating = "Fair"
        else:
            bar_color = (231, 76, 60)  # Red
            rating = "Needs Work"

        # Card background
        self.set_fill_color(250, 250, 250)
        self.rect(x, y, width, height, 'F')

        # Card border
        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.5)
        self.rect(x, y, width, height, 'D')

        # Title
        self.set_xy(x + 5, y + 5)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(70, 70, 70)
        self.cell(width - 10, 5, title, 0, 0, 'L')

        # Score number (large)
        self.set_xy(x + 5, y + 12)
        self.set_font('Arial', 'B', 18)
        self.set_text_color(*bar_color)
        self.cell(25, 8, str(score), 0, 0, 'C')

        # Rating text
        self.set_xy(x + 30, y + 14)
        self.set_font('Arial', '', 9)
        self.set_text_color(100, 100, 100)
        self.cell(width - 35, 6, rating, 0, 0, 'L')

        # Progress bar background
        bar_y = y + height - 10
        bar_width = width - 10
        self.set_fill_color(230, 230, 230)
        self.rect(x + 5, bar_y, bar_width, 5, 'F')

        # Progress bar fill
        fill_width = (score / 100) * bar_width
        self.set_fill_color(*bar_color)
        self.rect(x + 5, bar_y, fill_width, 5, 'F')

    def draw_score_summary_page(self, section_scores: Dict[str, Dict[str, Any]], overall_score: int):
        """
        Draw a visual summary page of all section scores

        Args:
            section_scores: Dict of {section_name: {'score': int, 'rating': str}}
            overall_score: Overall score (0-100)
        """
        self.add_page()

        # Page title with decorative element
        self.set_fill_color(*self.color_primary)
        self.rect(15, self.get_y(), 4, 10, 'F')

        self.set_font('Arial', 'B', 18)
        self.set_text_color(*self.color_primary)
        self.set_x(25)
        self.cell(0, 10, 'Score Summary')

        # Underline
        y = self.get_y() + 10
        self.set_draw_color(*self.color_primary)
        self.set_line_width(0.5)
        self.line(20, y + 2, 190, y + 2)

        self.ln(15)

        # Overall score card (centered, larger)
        overall_y = self.get_y()
        self.draw_score_card('OVERALL SCORE', overall_score, 55, overall_y, 100, 40)

        self.ln(50)

        # Section scores header
        self.set_font('Arial', 'B', 12)
        self.set_text_color(*self.color_secondary)
        self.cell(0, 8, 'Section Breakdown', 0, 1, 'L')

        self.ln(5)

        # Draw section score cards in 2-column grid
        x_left = 20
        x_right = 110
        card_width = 80
        card_height = 35
        y_offset = self.get_y()

        section_list = list(section_scores.items())
        for idx, (section_name, section_data) in enumerate(section_list):
            score = section_data.get('score', 0)

            # Calculate position
            row = idx // 2
            col = idx % 2
            x = x_left if col == 0 else x_right
            y = y_offset + (row * (card_height + 5))

            self.draw_score_card(section_name, score, x, y, card_width, card_height)

        # Move cursor below cards
        rows_needed = (len(section_list) + 1) // 2
        self.set_y(y_offset + (rows_needed * (card_height + 5)) + 5)


def generate_pdf_report(
    report_markdown: str,
    game_name: str,
    report_type: str,
    audit_results: Dict[str, Any] = None
) -> bytes:
    """
    Generate a PDF report from markdown content

    Args:
        report_markdown: The markdown report content
        game_name: Name of the game
        report_type: Type of report (Pre-Launch or Post-Launch)
        audit_results: Optional audit results dictionary

    Returns:
        PDF file as bytes
    """
    pdf = PDFReportGenerator()
    pdf.add_page()

    # === PROFESSIONAL TITLE PAGE ===

    # Top decorative bar
    pdf.set_fill_color(*pdf.color_primary)
    pdf.rect(0, 0, 210, 8, 'F')

    # Company branding
    pdf.ln(25)
    pdf.set_font('Arial', 'B', 28)
    pdf.set_text_color(*pdf.color_primary)
    pdf.cell(0, 12, 'PUBLITZ', 0, 1, 'C')

    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, 'Game Marketing Intelligence', 0, 1, 'C')

    # Decorative line
    pdf.ln(15)
    pdf.set_draw_color(*pdf.color_primary)
    pdf.set_line_width(0.8)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())

    # Report type banner
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 22)
    pdf.set_text_color(*pdf.color_primary)
    pdf.cell(0, 10, f'{report_type} Audit Report', 0, 1, 'C')

    # Game name in professional box
    pdf.ln(15)

    # Background box for game name
    box_y = pdf.get_y()
    pdf.set_fill_color(245, 248, 252)
    pdf.rect(40, box_y, 130, 25, 'F')

    # Left accent bar
    pdf.set_fill_color(*pdf.color_accent)
    pdf.rect(40, box_y, 4, 25, 'F')

    # Game name
    pdf.set_xy(50, box_y + 8)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(*pdf.color_secondary)
    pdf.multi_cell(110, 8, game_name, 0, 'C')

    # Report metadata
    pdf.ln(35)
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f'Report Generated: {datetime.now().strftime("%B %d, %Y")}', 0, 1, 'C')
    pdf.cell(0, 6, f'Report ID: {datetime.now().strftime("%Y%m%d-%H%M")}', 0, 1, 'C')

    # Add audit quality badge if available
    if audit_results:
        quality_score = audit_results.get('overall_quality_score', 0)
        needs_correction = audit_results.get('needs_correction', False)

        pdf.ln(20)

        # Quality badge with colored background
        badge_y = pdf.get_y()

        if not needs_correction and quality_score >= 80:
            bg_color = (236, 255, 241)
            border_color = pdf.color_accent
            text_color = (39, 174, 96)
            badge_label = 'HIGH QUALITY REPORT'
        elif quality_score >= 60:
            bg_color = (255, 249, 229)
            border_color = pdf.color_warning
            text_color = (200, 140, 0)
            badge_label = 'VERIFIED REPORT'
        else:
            bg_color = (235, 245, 255)
            border_color = pdf.color_primary
            text_color = (52, 152, 219)
            badge_label = 'ANALYZED REPORT'

        # Badge box
        pdf.set_fill_color(*bg_color)
        pdf.rect(65, badge_y, 80, 20, 'F')

        # Badge border
        pdf.set_draw_color(*border_color)
        pdf.set_line_width(0.8)
        pdf.rect(65, badge_y, 80, 20, 'D')

        # Badge text
        pdf.set_xy(65, badge_y + 6)
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(*text_color)
        pdf.cell(80, 6, badge_label, 0, 1, 'C')

        pdf.set_xy(65, badge_y + 12)
        pdf.set_font('Arial', '', 9)
        pdf.cell(80, 5, f'Quality Score: {quality_score}/100', 0, 1, 'C')

    # Report description
    pdf.ln(30)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, 'This comprehensive audit report was generated by Publitz\'s AI-powered game analysis system, '
                         'combining data from multiple sources including Steam, RAWG, IGDB, Google Trends, '
                         'YouTube Analytics, and proprietary market intelligence algorithms.', 0, 'C')

    # Confidentiality notice at bottom
    pdf.set_y(-50)
    pdf.set_draw_color(220, 220, 220)
    pdf.line(40, pdf.get_y(), 170, pdf.get_y())

    pdf.ln(5)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_text_color(*pdf.color_warning)
    pdf.cell(0, 5, 'CONFIDENTIAL', 0, 1, 'C')

    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 4, 'This report contains proprietary market analysis and should be treated as confidential. '
                         'Distribution should be limited to authorized personnel only.', 0, 'C')

    # Add score summary page if audit results contain section scores
    if audit_results and 'section_scores' in audit_results and 'overall_score' in audit_results:
        section_scores = audit_results['section_scores']
        overall_score = audit_results['overall_score']

        if section_scores:
            pdf.draw_score_summary_page(section_scores, overall_score)

    # Start new page for content
    pdf.add_page()

    # Parse and add markdown content
    _parse_markdown_to_pdf(pdf, report_markdown)

    # Return PDF as bytes
    return bytes(pdf.output())


def _clean_unicode_for_pdf(text: str) -> str:
    """Replace Unicode characters with ASCII equivalents for PDF compatibility"""
    # Replace checkmarks and symbols
    replacements = {
        '✓': '[YES]',
        '✗': '[NO]',
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v',
        '•': '*',
        '…': '...',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '—': '-',
        '–': '-',
        '×': 'x',
        '÷': '/',
        '≈': '~',
        '≥': '>=',
        '≤': '<=',
        '≠': '!=',
        '°': ' degrees',
        '©': '(c)',
        '®': '(R)',
        '™': '(TM)',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
    }

    for unicode_char, ascii_replacement in replacements.items():
        text = text.replace(unicode_char, ascii_replacement)

    # Remove any remaining non-ASCII characters
    text = text.encode('ascii', 'ignore').decode('ascii')

    return text


def _remove_markdown_formatting(text: str) -> str:
    """Remove all markdown formatting from text"""
    # Remove bold and italic markers (order matters!)
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)  # Bold+Italic
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # Italic
    text = re.sub(r'___(.*?)___', r'\1', text)  # Bold+Italic (underscore)
    text = re.sub(r'__(.*?)__', r'\1', text)  # Bold (underscore)
    text = re.sub(r'_(.*?)_', r'\1', text)  # Italic (underscore)
    text = re.sub(r'`(.*?)`', r'\1', text)  # Inline code
    text = re.sub(r'~~(.*?)~~', r'\1', text)  # Strikethrough

    # Remove any stray asterisks or underscores that might be left
    # (in case of malformed markdown)
    text = re.sub(r'(?<!\w)\*+(?!\w)', '', text)  # Lone asterisks
    text = re.sub(r'(?<!\w)_+(?!\w)', '', text)  # Lone underscores

    return text


def _parse_markdown_to_pdf(pdf: PDFReportGenerator, markdown_text: str):
    """Parse markdown and add to PDF with professional formatting"""

    # Clean Unicode characters before parsing
    markdown_text = _clean_unicode_for_pdf(markdown_text)

    lines = markdown_text.split('\n')
    in_table = False
    table_rows = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Detect tables (markdown format: | col1 | col2 |)
        if line.startswith('|') and '|' in line[1:]:
            if not in_table:
                in_table = True
                table_rows = []

            # Skip separator rows (|---|---|)
            if not re.match(r'^\|[\s\-:]+\|', line):
                table_rows.append(line)

            i += 1
            continue

        # End of table - render it
        if in_table and not line.startswith('|'):
            _render_table(pdf, table_rows)
            table_rows = []
            in_table = False

        if not line:
            pdf.ln(2)
            i += 1
            continue

        # H1 headers (# )
        if line.startswith('# '):
            title = line[2:].strip()
            title = _remove_markdown_formatting(title)
            pdf.chapter_title(title, level=1)

        # H2 headers (## ) - check for special sections
        elif line.startswith('## '):
            title = line[3:].strip()
            title = _remove_markdown_formatting(title)

            # Special formatting for EXECUTIVE SNAPSHOT
            if 'EXECUTIVE SNAPSHOT' in title.upper():
                pdf.add_callout_box(
                    'EXECUTIVE SNAPSHOT',
                    'Key metrics and performance indicators at a glance',
                    'info'
                )
            elif 'DATA QUALITY WARNING' in title.upper():
                pdf.add_callout_box(
                    'DATA QUALITY WARNING',
                    'This section contains important information about data limitations',
                    'warning'
                )
            else:
                pdf.chapter_title(title, level=2)

        # H3 headers (### )
        elif line.startswith('### '):
            title = line[4:].strip()
            title = _remove_markdown_formatting(title)
            pdf.chapter_title(title, level=3)

        # Bullet points (- or *)
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            text = _remove_markdown_formatting(text)

            # Indent based on leading spaces
            indent_level = len(lines[i]) - len(lines[i].lstrip())
            indent = max(0, indent_level // 2)

            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(*pdf.color_text)
            pdf.set_x(20 + indent * 5)
            pdf.cell(5, 6, '*', 0, 0)
            pdf.set_x(25 + indent * 5)
            pdf.multi_cell(170 - indent * 5, 6, text)

        # Numbered lists
        elif re.match(r'^\d+\.', line):
            text = re.sub(r'^\d+\.\s*', '', line)
            text = _remove_markdown_formatting(text)

            # Extract number
            number = re.match(r'^(\d+)\.', line).group(1)

            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(*pdf.color_text)
            pdf.set_x(20)
            pdf.cell(10, 6, f'{number}.', 0, 0)
            pdf.set_x(30)
            pdf.multi_cell(160, 6, text)

        # Regular paragraph
        else:
            text = _remove_markdown_formatting(line)

            # Skip horizontal rules (add separator instead)
            if text.strip() in ['---', '___', '***', '']:
                pdf.add_section_separator()
                i += 1
                continue

            # Check for special inline formatting (bold keywords)
            if text:
                # Detect warning/info patterns
                if text.startswith('WARNING:') or text.startswith('[WARNING]'):
                    pdf.add_callout_box('Warning', text.replace('WARNING:', '').replace('[WARNING]', '').strip(), 'warning')
                elif text.startswith('INFO:') or text.startswith('[INFO]'):
                    pdf.add_callout_box('Information', text.replace('INFO:', '').replace('[INFO]', '').strip(), 'info')
                elif text.startswith('SUCCESS:') or text.startswith('[SUCCESS]'):
                    pdf.add_callout_box('Success', text.replace('SUCCESS:', '').replace('[SUCCESS]', '').strip(), 'success')
                else:
                    pdf.chapter_body(text)

        i += 1

    # Render any remaining table
    if in_table and table_rows:
        _render_table(pdf, table_rows)


def _render_table(pdf: PDFReportGenerator, table_rows: list):
    """Render a markdown table with professional styling"""
    if not table_rows:
        return

    pdf.ln(5)

    # Parse table data
    header = [cell.strip() for cell in table_rows[0].split('|')[1:-1]]
    data_rows = []

    for row in table_rows[1:]:
        cells = [cell.strip() for cell in row.split('|')[1:-1]]
        if cells:  # Skip empty rows
            data_rows.append(cells)

    if not data_rows:
        return

    # Calculate column widths (distribute evenly for now)
    num_cols = len(header)
    col_width = 170 / num_cols  # Total width 170mm

    # Table header with background
    pdf.set_fill_color(41, 128, 185)  # Primary blue
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 10)

    x_start = pdf.get_x()
    y_start = pdf.get_y()

    for i, col in enumerate(header):
        pdf.set_xy(x_start + i * col_width, y_start)
        pdf.cell(col_width, 8, col, 1, 0, 'C', True)

    pdf.ln(8)

    # Table data rows with alternating colors
    pdf.set_font('Arial', '', 9)

    for row_idx, row in enumerate(data_rows):
        # Alternating row colors
        if row_idx % 2 == 0:
            pdf.set_fill_color(250, 250, 250)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.set_text_color(*pdf.color_text)

        y_start = pdf.get_y()

        # Calculate row height based on content
        max_height = 7

        for i, cell in enumerate(row):
            pdf.set_xy(x_start + i * col_width, y_start)
            pdf.cell(col_width, max_height, cell[:50], 1, 0, 'L', True)  # Limit cell text length

        pdf.ln(max_height)

    pdf.ln(5)
    pdf.set_text_color(*pdf.color_text)


def create_downloadable_pdf(
    report_markdown: str,
    game_name: str,
    report_type: str,
    audit_results: Dict[str, Any] = None
) -> tuple[bytes, str]:
    """
    Create a downloadable PDF report

    Returns:
        Tuple of (pdf_bytes, filename)
    """
    pdf_bytes = generate_pdf_report(report_markdown, game_name, report_type, audit_results)

    # Generate filename
    safe_game_name = re.sub(r'[^\w\s-]', '', game_name).strip().replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f"{safe_game_name}_{report_type}_Audit_{timestamp}.pdf"

    return pdf_bytes, filename
