#!/usr/bin/env python3
"""
Data Validation Utilities
Centralized type validation and sanitization for game data
"""

from typing import Any, Dict, Union


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert any value to float

    Args:
        value: Value to convert (can be string, int, float, or None)
        default: Default value if conversion fails

    Returns:
        float value or default

    Examples:
        safe_float("85.3%") -> 85.3
        safe_float("85.3") -> 85.3
        safe_float(85) -> 85.0
        safe_float("N/A") -> 0.0
        safe_float(None, 50.0) -> 50.0
    """
    if value is None:
        return default

    try:
        # If it's a string, try to strip percentage signs
        if isinstance(value, str):
            value = value.rstrip('%').strip()
            if value.lower() in ('n/a', 'unknown', ''):
                return default

        return float(value)
    except (ValueError, TypeError, AttributeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert any value to int

    Args:
        value: Value to convert (can be string, int, float, or None)
        default: Default value if conversion fails

    Returns:
        int value or default

    Examples:
        safe_int("1000") -> 1000
        safe_int(1000.5) -> 1000
        safe_int("N/A") -> 0
        safe_int(None, 100) -> 100
    """
    if value is None:
        return default

    try:
        # If it's a string, try to remove commas and strip
        if isinstance(value, str):
            value = value.replace(',', '').strip()
            if value.lower() in ('n/a', 'unknown', ''):
                return default

        return int(float(value))  # Convert via float to handle "1000.5"
    except (ValueError, TypeError, AttributeError):
        return default


def safe_format_number(value: Any, default: str = "0") -> str:
    """
    Safely format a number with commas

    Args:
        value: Value to format
        default: Default string if formatting fails

    Returns:
        Formatted string like "1,000" or default

    Examples:
        safe_format_number(1000) -> "1,000"
        safe_format_number("1000") -> "1,000"
        safe_format_number("N/A") -> "0"
        safe_format_number(None, "Unknown") -> "Unknown"
    """
    try:
        numeric = safe_int(value, None)
        if numeric is None:
            return default
        return f"{numeric:,}"
    except (ValueError, TypeError):
        return default


def validate_game_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize game data to ensure consistent types

    Args:
        data: Raw game data dictionary

    Returns:
        Sanitized dictionary with guaranteed types

    Ensures:
        - review_score_raw is always float
        - reviews_total is always int
        - price_raw is always float
        - owners_avg is always int
    """
    validated = data.copy()

    # Ensure review score is numeric
    if 'review_score_raw' in validated:
        validated['review_score_raw'] = safe_float(validated['review_score_raw'])

    if 'review_score' in validated and 'review_score_raw' not in validated:
        # Infer review_score_raw from review_score if missing
        validated['review_score_raw'] = safe_float(validated['review_score'])

    # Ensure review_score is formatted string
    if 'review_score_raw' in validated and isinstance(validated.get('review_score'), (int, float)):
        score = validated['review_score_raw']
        validated['review_score'] = f"{score:.1f}%" if score > 0 else "N/A"

    # Ensure reviews_total is numeric
    if 'reviews_total' in validated:
        validated['reviews_total'] = safe_int(validated['reviews_total'])

    # Ensure price_raw is numeric
    if 'price_raw' in validated:
        validated['price_raw'] = safe_float(validated['price_raw'])

    # Ensure owners_avg is numeric
    if 'owners_avg' in validated:
        validated['owners_avg'] = safe_int(validated['owners_avg'])

    return validated


def validate_sales_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize sales data to ensure consistent types

    Args:
        data: Raw sales data dictionary

    Returns:
        Sanitized dictionary with guaranteed types
    """
    return validate_game_data(data)  # Same validation rules


def validate_competitor_data(competitors: list) -> list:
    """
    Validate and sanitize a list of competitor data

    Args:
        competitors: List of competitor dictionaries

    Returns:
        List of sanitized competitor dictionaries
    """
    return [validate_game_data(comp) for comp in competitors]
