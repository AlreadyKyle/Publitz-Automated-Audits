"""Utility functions for the Publitz Automated Audits tool."""

import re
from typing import Optional, Dict, Any
from datetime import datetime


def extract_app_id(steam_url: str) -> Optional[str]:
    """
    Extract Steam App ID from various Steam URL formats.

    Examples:
        https://store.steampowered.com/app/1234567/GameName/
        https://store.steampowered.com/app/1234567/
        store.steampowered.com/app/1234567
    """
    patterns = [
        r'store\.steampowered\.com/app/(\d+)',
        r'/app/(\d+)',
        r'^(\d+)$'  # Just the ID
    ]

    for pattern in patterns:
        match = re.search(pattern, steam_url)
        if match:
            return match.group(1)

    return None


def is_valid_steam_url(url: str) -> bool:
    """Check if the URL is a valid Steam store page URL."""
    return extract_app_id(url) is not None


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amounts properly."""
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥",
        "BRL": "R$",
        "RUB": "₽",
        "INR": "₹",
        "CAD": "C$",
        "AUD": "A$"
    }

    symbol = symbols.get(currency, currency + " ")

    if currency == "JPY":
        return f"{symbol}{int(amount)}"

    return f"{symbol}{amount:,.2f}"


def calculate_readiness_score(compliance_data: Dict[str, Any]) -> int:
    """
    Calculate launch readiness score based on compliance data.
    Returns score out of 100.
    """
    total_checks = 0
    passed_checks = 0

    for category, items in compliance_data.items():
        if isinstance(items, dict):
            total_checks += len(items)
            passed_checks += sum(1 for v in items.values() if v is True)
        elif isinstance(items, list):
            total_checks += len(items)
            passed_checks += sum(1 for item in items if item.get('status') == 'pass')

    if total_checks == 0:
        return 0

    return int((passed_checks / total_checks) * 100)


def categorize_issues(issues: list) -> Dict[str, list]:
    """
    Categorize issues into Critical, Important, and Nice-to-Have.
    """
    categorized = {
        "critical": [],
        "important": [],
        "nice_to_have": []
    }

    for issue in issues:
        severity = issue.get('severity', 'important').lower()
        if severity in categorized:
            categorized[severity].append(issue)

    return categorized


def detect_launch_status(release_date: Optional[str], coming_soon: bool) -> str:
    """
    Detect if game is pre-launch or post-launch.

    Returns:
        "pre_launch" or "post_launch"
    """
    if coming_soon:
        return "pre_launch"

    if release_date:
        # Check if release date is in the past
        try:
            # Try various date formats
            for fmt in ["%d %b, %Y", "%b %d, %Y", "%Y-%m-%d", "%d %B, %Y"]:
                try:
                    release_dt = datetime.strptime(release_date, fmt)
                    if release_dt <= datetime.now():
                        return "post_launch"
                    else:
                        return "pre_launch"
                except ValueError:
                    continue
        except:
            pass

    # Default to pre-launch if uncertain
    return "pre_launch"


def clean_text(text: str) -> str:
    """Clean and normalize text from web scraping."""
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def parse_price(price_text: str) -> Optional[float]:
    """Parse price text into float value."""
    if not price_text:
        return None

    # Remove currency symbols and text
    price_text = re.sub(r'[^\d.,]', '', price_text)

    # Handle different decimal separators
    if ',' in price_text and '.' in price_text:
        # Assume comma is thousands separator
        price_text = price_text.replace(',', '')
    elif ',' in price_text:
        # Could be decimal separator (European format)
        if price_text.count(',') == 1 and len(price_text.split(',')[1]) == 2:
            price_text = price_text.replace(',', '.')

    try:
        return float(price_text)
    except ValueError:
        return None


def estimate_revenue_impact(current_metric: float, target_metric: float,
                            base_revenue: float) -> float:
    """Estimate revenue impact of improving a metric."""
    if current_metric == 0:
        return 0

    improvement_ratio = target_metric / current_metric
    potential_revenue = base_revenue * improvement_ratio

    return potential_revenue - base_revenue


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage values."""
    return f"{value:.{decimals}f}%"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix
