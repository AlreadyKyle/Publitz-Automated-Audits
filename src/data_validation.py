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


def normalize_steam_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Steam API data inconsistencies at the entry point

    Steam API returns the same fields in different formats depending on the game/endpoint.
    This function normalizes all fields to consistent types to prevent crashes throughout the app.

    Args:
        data: Raw game data from Steam API

    Returns:
        Normalized dictionary with consistent types
    """
    normalized = data.copy()

    # === GENRES: Normalize to list of dicts with 'description' key ===
    genres_raw = normalized.get('genres', [])
    if isinstance(genres_raw, str):
        # "Action, Adventure" -> [{'description': 'Action'}, {'description': 'Adventure'}]
        normalized['genres'] = [{'description': g.strip()} for g in genres_raw.split(',') if g.strip()]
    elif isinstance(genres_raw, list):
        if not genres_raw:
            normalized['genres'] = []
        elif isinstance(genres_raw[0], str):
            # ['Action', 'Adventure'] -> [{'description': 'Action'}, {'description': 'Adventure'}]
            normalized['genres'] = [{'description': g} for g in genres_raw]
        elif isinstance(genres_raw[0], dict):
            # Already correct format
            normalized['genres'] = genres_raw
    else:
        normalized['genres'] = []

    # === TAGS: Normalize to list of strings ===
    tags_raw = normalized.get('tags', [])
    if isinstance(tags_raw, str):
        # "RPG, Strategy" -> ['RPG', 'Strategy']
        normalized['tags'] = [t.strip() for t in tags_raw.split(',') if t.strip()]
    elif isinstance(tags_raw, dict):
        # {'RPG': 100, 'Strategy': 50} -> ['RPG', 'Strategy']
        normalized['tags'] = list(tags_raw.keys())
    elif isinstance(tags_raw, list):
        # Ensure all elements are strings
        normalized['tags'] = [str(t) for t in tags_raw]
    else:
        normalized['tags'] = []

    # === DEVELOPERS: Normalize to list of strings ===
    devs_raw = normalized.get('developers', [])
    if isinstance(devs_raw, str):
        normalized['developers'] = [devs_raw]
    elif not isinstance(devs_raw, list):
        normalized['developers'] = []

    # === PUBLISHERS: Normalize to list of strings ===
    pubs_raw = normalized.get('publishers', [])
    if isinstance(pubs_raw, str):
        normalized['publishers'] = [pubs_raw]
    elif not isinstance(pubs_raw, list):
        normalized['publishers'] = []

    # === PRICE_OVERVIEW: Ensure it exists and 'final' is numeric ===
    if 'price_overview' not in normalized or normalized['price_overview'] is None:
        normalized['price_overview'] = {'final': 0, 'currency': 'USD'}
    else:
        price_final = normalized['price_overview'].get('final', 0)
        normalized['price_overview']['final'] = safe_int(price_final, 0)

    # === RECOMMENDATIONS: Ensure it exists ===
    if 'recommendations' not in normalized or normalized['recommendations'] is None:
        normalized['recommendations'] = {'total': 0}
    elif isinstance(normalized['recommendations'], dict):
        total = normalized['recommendations'].get('total', 0)
        normalized['recommendations']['total'] = safe_int(total, 0)

    # === CATEGORIES: Ensure it's a list ===
    if 'categories' not in normalized or not isinstance(normalized.get('categories'), list):
        normalized['categories'] = []

    # === SCREENSHOTS: Ensure it's a list ===
    if 'screenshots' not in normalized or not isinstance(normalized.get('screenshots'), list):
        normalized['screenshots'] = []

    # === MOVIES: Ensure it's a list ===
    if 'movies' not in normalized or not isinstance(normalized.get('movies'), list):
        normalized['movies'] = []

    # === SUPPORTED_LANGUAGES: Ensure it exists ===
    if 'supported_languages' not in normalized:
        normalized['supported_languages'] = []

    return normalized


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
    # First normalize Steam API inconsistencies
    validated = normalize_steam_data(data)

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
