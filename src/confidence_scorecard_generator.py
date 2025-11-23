"""
Data Confidence Scorecard Generator for Publitz Audit Reports

Generates a comprehensive confidence assessment showing users which insights
they can act on immediately vs. which need validation. Dynamically adapts
based on which data sources were actually used in the report.
"""

from typing import Dict, List, Tuple, Optional, Any


# Confidence level definitions
CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"

# Importance weights for overall confidence calculation (sum to 100)
CATEGORY_WEIGHTS = {
    "review_score": 15,      # Review scores are critical for decision-making
    "owner_count": 20,       # Owner counts drive revenue estimates
    "revenue_estimates": 25, # Revenue is the most important metric
    "regional_revenue": 5,   # Regional split is nice-to-have
    "sentiment": 10,         # Sentiment themes guide strategy
    "competitor_data": 10,   # Competitive positioning matters
    "influencer_data": 5,    # Influencer outreach is tactical
    "regional_pricing": 10   # Pricing optimization is important
}

# Confidence score mapping to numeric values
CONFIDENCE_SCORES = {
    CONFIDENCE_HIGH: 100,
    CONFIDENCE_MEDIUM: 60,
    CONFIDENCE_LOW: 20
}


def generate_confidence_scorecard(
    data_sources_used: Dict[str, Any],
    section_mapping: Optional[Dict[str, List[str]]] = None
) -> str:
    """
    Generate a data confidence assessment scorecard.

    Args:
        data_sources_used: Dictionary describing which data sources were used.
            Expected keys:
            - 'review_data_available': bool
            - 'steamspy_available': bool
            - 'revenue_method': str (e.g., 'calculated', 'estimated', 'direct')
            - 'regional_revenue_source': str (e.g., 'industry_average', 'actual')
            - 'sentiment_analyzed': bool (True if real reviews analyzed)
            - 'sentiment_sample_size': int (number of reviews analyzed)
            - 'competitor_data_available': bool
            - 'influencer_data_available': bool
            - 'regional_pricing_method': str (e.g., 'ppp', 'manual', 'industry')

        section_mapping: Optional dict mapping section names to confidence categories.
            If not provided, uses default mapping.

    Returns:
        Markdown-formatted confidence scorecard string
    """
    # Calculate confidence levels for each category
    categories = _get_category_confidence_levels(data_sources_used)

    # Calculate overall weighted confidence score
    overall_score, overall_badge = _calculate_overall_confidence(categories)

    # Generate category insights by confidence level
    high_insights, medium_insights, low_insights = _categorize_insights(
        categories, data_sources_used
    )

    # Get section mapping if not provided
    if section_mapping is None:
        section_mapping = _get_default_section_mapping()

    # Build the markdown
    scorecard = f"""## 2. DATA CONFIDENCE ASSESSMENT

**Why This Matters**: This report aggregates data from {len([c for c in categories.values() if c['used']])} different sources with varying reliability. Understanding confidence levels helps you prioritize actions—act immediately on high-confidence insights, validate medium-confidence findings before major spend, and treat low-confidence data as directional only.

**Overall Report Confidence: {overall_badge} ({overall_score:.0f}/100)**

---

### Data Quality by Category

| Data Category | Confidence | Source | Impact on Decisions |
|--------------|------------|---------|-------------------|
{_generate_category_table_rows(categories, data_sources_used)}

---

### How to Interpret Confidence Levels

#### ✅ **High Confidence - Act With Confidence**

These insights are based on verified, real-time data from official APIs. You can make strategic decisions and allocate budget based on these findings without additional validation.

**In This Report:**
{_format_insight_list(high_insights)}

**Recommended Actions**: Use these insights for immediate decision-making, budget allocation, and strategic planning.

---

#### ⚠️ **Medium Confidence - Validate Before Major Investment**

These insights are calculated or estimated from reliable sources but include assumptions. They're directionally accurate but may have ±25-35% variance. Validate with additional research before committing significant resources.

**In This Report:**
{_format_insight_list(medium_insights)}

**Recommended Actions**: Use for directional planning. Test assumptions in 1-2 markets before full rollout. Cross-reference with your own analytics if available.

---

#### ❌ **Low Confidence - Use as Hypotheses Only**

These insights are based on industry averages or genre patterns, not your actual data. Treat as hypotheses to investigate, not facts to act on. Always validate before making decisions.

**In This Report:**
{_format_insight_list(low_insights)}

**Recommended Actions**: Use to generate questions and areas to investigate. Seek primary data (surveys, actual sales data, player interviews) before acting.

---

### Section-by-Section Confidence Reference

{_generate_section_reference(section_mapping, categories)}

**Bottom Line**: This report has an overall confidence of **{overall_score:.0f}/100** ({overall_badge}). Focus your immediate actions on the {len(high_insights)} high-confidence insights listed above.
"""

    return scorecard


def _get_category_confidence_levels(data_sources: Dict[str, Any]) -> Dict[str, Dict]:
    """
    Determine confidence level for each data category based on sources used.

    Returns dict with structure:
    {
        'category_name': {
            'confidence': 'high'/'medium'/'low',
            'badge': '✅'/'⚠️'/'❌',
            'source': 'description of source',
            'notes': 'additional context',
            'used': True/False (whether this category has data in report)
        }
    }
    """
    categories = {}

    # Review Score & Volume
    categories['review_score'] = {
        'name': 'Review Score & Volume',
        'confidence': CONFIDENCE_HIGH if data_sources.get('review_data_available', True) else CONFIDENCE_LOW,
        'badge': '✅' if data_sources.get('review_data_available', True) else '❌',
        'source': 'Steam API (direct)' if data_sources.get('review_data_available', True) else 'Unavailable',
        'notes': 'Real-time verified Steam review data' if data_sources.get('review_data_available', True) else 'Review data unavailable',
        'used': True  # Always used
    }

    # Owner Count Range
    categories['owner_count'] = {
        'name': 'Owner Count Range',
        'confidence': CONFIDENCE_MEDIUM if data_sources.get('steamspy_available', True) else CONFIDENCE_LOW,
        'badge': '⚠️' if data_sources.get('steamspy_available', True) else '❌',
        'source': 'SteamSpy API (estimated)' if data_sources.get('steamspy_available', True) else 'Unavailable',
        'notes': 'Range provided; ±20-30% accuracy' if data_sources.get('steamspy_available', True) else 'Fallback estimates used',
        'used': True  # Always used
    }

    # Revenue Estimates
    revenue_method = data_sources.get('revenue_method', 'calculated')
    if revenue_method == 'direct':
        rev_conf = CONFIDENCE_HIGH
        rev_badge = '✅'
        rev_source = 'Publisher-provided data'
        rev_notes = 'Actual sales data'
    elif revenue_method in ['calculated', 'enhanced']:
        rev_conf = CONFIDENCE_MEDIUM
        rev_badge = '⚠️'
        rev_source = 'Calculated from owners × price × factors'
        rev_notes = 'Based on SteamSpy estimates; ±25-35% accuracy'
    else:
        rev_conf = CONFIDENCE_LOW
        rev_badge = '❌'
        rev_source = 'Industry benchmarks'
        rev_notes = 'Estimated from genre averages; ±40-50% accuracy'

    categories['revenue_estimates'] = {
        'name': 'Revenue Estimates',
        'confidence': rev_conf,
        'badge': rev_badge,
        'source': rev_source,
        'notes': rev_notes,
        'used': True  # Always used
    }

    # Regional Revenue Split
    regional_source = data_sources.get('regional_revenue_source', 'industry_average')
    categories['regional_revenue'] = {
        'name': 'Regional Revenue Split',
        'confidence': CONFIDENCE_HIGH if regional_source == 'actual' else CONFIDENCE_LOW,
        'badge': '✅' if regional_source == 'actual' else '❌',
        'source': 'Actual sales data' if regional_source == 'actual' else 'Industry averages',
        'notes': 'Real regional breakdown' if regional_source == 'actual' else 'Typical Steam distribution patterns; no actual regional sales data',
        'used': True  # Always used
    }

    # Sentiment Breakdown
    sentiment_analyzed = data_sources.get('sentiment_analyzed', False)
    sentiment_sample = data_sources.get('sentiment_sample_size', 0)

    if sentiment_analyzed and sentiment_sample >= 150:
        sent_conf = CONFIDENCE_HIGH
        sent_badge = '✅'
        sent_source = f'Claude API analysis of {sentiment_sample} reviews'
        sent_notes = 'Real review text analysis with theme categorization'
    elif sentiment_analyzed and sentiment_sample > 0:
        sent_conf = CONFIDENCE_MEDIUM
        sent_badge = '⚠️'
        sent_source = f'Claude API analysis of {sentiment_sample} reviews'
        sent_notes = 'Small sample size; may not represent full playerbase'
    else:
        sent_conf = CONFIDENCE_LOW
        sent_badge = '❌'
        sent_source = 'Genre patterns'
        sent_notes = 'Estimated themes without actual review analysis'

    categories['sentiment'] = {
        'name': 'Sentiment Theme Analysis',
        'confidence': sent_conf,
        'badge': sent_badge,
        'source': sent_source,
        'notes': sent_notes,
        'used': True  # Always used
    }

    # Competitor Comparisons
    categories['competitor_data'] = {
        'name': 'Competitor Comparisons',
        'confidence': CONFIDENCE_HIGH if data_sources.get('competitor_data_available', True) else CONFIDENCE_LOW,
        'badge': '✅' if data_sources.get('competitor_data_available', True) else '❌',
        'source': 'Steam API + SteamSpy' if data_sources.get('competitor_data_available', True) else 'Limited data',
        'notes': 'Direct comparison of public metrics' if data_sources.get('competitor_data_available', True) else 'Competitor data unavailable',
        'used': data_sources.get('competitor_data_available', True)
    }

    # Influencer Database
    categories['influencer_data'] = {
        'name': 'Influencer Database',
        'confidence': CONFIDENCE_HIGH if data_sources.get('influencer_data_available', True) else CONFIDENCE_MEDIUM,
        'badge': '✅' if data_sources.get('influencer_data_available', True) else '⚠️',
        'source': 'Twitch/YouTube APIs (real-time)' if data_sources.get('influencer_data_available', True) else 'Curated recommendations',
        'notes': 'Live follower counts and engagement rates' if data_sources.get('influencer_data_available', True) else 'Genre-appropriate fallback influencers',
        'used': True  # Always used
    }

    # Regional Pricing Recommendations
    pricing_method = data_sources.get('regional_pricing_method', 'ppp')
    if pricing_method == 'manual':
        price_conf = CONFIDENCE_HIGH
        price_badge = '✅'
        price_source = 'Manual market research'
        price_notes = 'Custom analysis for each region'
    elif pricing_method == 'ppp':
        price_conf = CONFIDENCE_MEDIUM
        price_badge = '⚠️'
        price_source = 'PPP data + Steam market research'
        price_notes = 'Purchasing power parity calculations'
    else:
        price_conf = CONFIDENCE_LOW
        price_badge = '❌'
        price_source = 'Industry averages'
        price_notes = 'Generic regional multipliers'

    categories['regional_pricing'] = {
        'name': 'Regional Pricing Recommendations',
        'confidence': price_conf,
        'badge': price_badge,
        'source': price_source,
        'notes': price_notes,
        'used': True  # Always used
    }

    return categories


def _calculate_overall_confidence(categories: Dict[str, Dict]) -> Tuple[float, str]:
    """
    Calculate weighted overall confidence score.

    Returns:
        (score, badge) tuple where score is 0-100 and badge is emoji + text
    """
    total_weight = 0
    weighted_sum = 0

    for cat_key, category in categories.items():
        if category['used'] and cat_key in CATEGORY_WEIGHTS:
            weight = CATEGORY_WEIGHTS[cat_key]
            confidence_score = CONFIDENCE_SCORES[category['confidence']]

            weighted_sum += weight * confidence_score
            total_weight += weight

    # Calculate overall score
    overall_score = weighted_sum / total_weight if total_weight > 0 else 50

    # Determine badge
    if overall_score >= 80:
        badge = "✅ HIGH"
    elif overall_score >= 60:
        badge = "⚠️ MEDIUM-HIGH"
    elif overall_score >= 40:
        badge = "⚠️ MEDIUM"
    else:
        badge = "❌ MEDIUM-LOW"

    return overall_score, badge


def _categorize_insights(
    categories: Dict[str, Dict],
    data_sources: Dict[str, Any]
) -> Tuple[List[str], List[str], List[str]]:
    """
    Categorize insights by confidence level for the report.

    Returns:
        (high_insights, medium_insights, low_insights) tuple of lists
    """
    high_insights = []
    medium_insights = []
    low_insights = []

    # Review Score
    if categories['review_score']['confidence'] == CONFIDENCE_HIGH:
        high_insights.append("**Review scores and volume** → Use to validate product-market fit and identify improvement areas")

    # Owner Count
    if categories['owner_count']['confidence'] == CONFIDENCE_MEDIUM:
        medium_insights.append("**Owner count ranges** → Use for market sizing; treat midpoint as best estimate (±25% variance)")
    elif categories['owner_count']['confidence'] == CONFIDENCE_LOW:
        low_insights.append("**Owner count estimates** → Directional only; validate with your own analytics")

    # Revenue
    if categories['revenue_estimates']['confidence'] == CONFIDENCE_HIGH:
        high_insights.append("**Revenue estimates** → Reliable for forecasting and ROI calculations")
    elif categories['revenue_estimates']['confidence'] == CONFIDENCE_MEDIUM:
        medium_insights.append("**Revenue estimates** → Use ranges for planning; validate before committing large budgets (±30% variance)")
    else:
        low_insights.append("**Revenue estimates** → Highly uncertain; seek publisher data or better tracking")

    # Regional Revenue
    if categories['regional_revenue']['confidence'] == CONFIDENCE_LOW:
        low_insights.append("**Regional revenue split** → Based on industry averages, not your actual data; test in 1-2 regions first")

    # Sentiment
    if categories['sentiment']['confidence'] == CONFIDENCE_HIGH:
        high_insights.append(f"**Sentiment theme analysis** → Based on {data_sources.get('sentiment_sample_size', 200)} real reviews; use to prioritize fixes and marketing messages")
    elif categories['sentiment']['confidence'] == CONFIDENCE_MEDIUM:
        medium_insights.append(f"**Sentiment theme analysis** → Based on {data_sources.get('sentiment_sample_size', 0)} reviews; small sample but directionally accurate")
    else:
        low_insights.append("**Sentiment themes** → Generic genre patterns; analyze actual reviews for accurate priorities")

    # Competitor Data
    if categories['competitor_data']['confidence'] == CONFIDENCE_HIGH and categories['competitor_data']['used']:
        high_insights.append("**Competitor comparisons** → Direct metric comparisons; use for positioning and benchmarking")

    # Influencer Data
    if categories['influencer_data']['confidence'] == CONFIDENCE_HIGH:
        high_insights.append("**Influencer contact database** → Real-time data; reach out immediately to recommended creators")
    elif categories['influencer_data']['confidence'] == CONFIDENCE_MEDIUM:
        medium_insights.append("**Influencer recommendations** → Curated list; verify current follower counts before outreach")

    # Regional Pricing
    if categories['regional_pricing']['confidence'] == CONFIDENCE_HIGH:
        high_insights.append("**Regional pricing recommendations** → Custom market research; implement with confidence")
    elif categories['regional_pricing']['confidence'] == CONFIDENCE_MEDIUM:
        medium_insights.append("**Regional pricing recommendations** → PPP-based calculations; test in 2-3 markets before full rollout")
    else:
        low_insights.append("**Regional pricing recommendations** → Generic multipliers; research local pricing expectations before implementing")

    return high_insights, medium_insights, low_insights


def _format_insight_list(insights: List[str]) -> str:
    """Format list of insights as markdown bullets."""
    if not insights:
        return "- *None in this report*"
    return "\n".join([f"- {insight}" for insight in insights])


def _generate_category_table_rows(categories: Dict[str, Dict], data_sources: Dict[str, Any]) -> str:
    """Generate table rows for category confidence levels."""
    rows = []

    # Define order for display
    category_order = [
        'review_score',
        'owner_count',
        'revenue_estimates',
        'regional_revenue',
        'sentiment',
        'competitor_data',
        'influencer_data',
        'regional_pricing'
    ]

    for cat_key in category_order:
        if cat_key in categories and categories[cat_key]['used']:
            cat = categories[cat_key]

            # Format confidence badge with text
            conf_display = f"{cat['badge']} **{cat['confidence'].upper()}**"

            row = f"| {cat['name']} | {conf_display} | {cat['source']} | {cat['notes']} |"
            rows.append(row)

    return "\n".join(rows)


def _get_default_section_mapping() -> Dict[str, List[str]]:
    """
    Get default mapping of report sections to confidence categories.

    Returns dict like:
    {
        'Section 4: Sales & Revenue Performance': ['revenue_estimates', 'owner_count'],
        'Section 7: Review & Sentiment Analysis': ['review_score', 'sentiment']
    }
    """
    return {
        'Section 1: Executive Summary': ['revenue_estimates', 'review_score', 'sentiment'],
        'Section 3: Market Positioning Analysis': ['competitor_data'],
        'Section 4: Sales & Revenue Performance': ['revenue_estimates', 'owner_count', 'regional_revenue'],
        'Section 5: Marketing Effectiveness': ['review_score', 'influencer_data'],
        'Section 6: Growth & Momentum': ['owner_count', 'review_score'],
        'Section 7: Review & Sentiment Analysis': ['review_score', 'sentiment'],
        'Section 8: Visibility & Discoverability': ['review_score', 'competitor_data'],
        'Section 11: Action Plan & Prioritization': ['revenue_estimates', 'sentiment', 'regional_pricing'],
        'Section 12: Regional Pricing Analysis': ['regional_pricing', 'regional_revenue'],
        'Section 14: Influencer Outreach Strategy': ['influencer_data']
    }


def _generate_section_reference(section_mapping: Dict[str, List[str]], categories: Dict[str, Dict]) -> str:
    """Generate section-by-section confidence reference."""
    lines = []

    for section, category_keys in section_mapping.items():
        # Get confidence badges for this section's categories
        badges = []
        for cat_key in category_keys:
            if cat_key in categories and categories[cat_key]['used']:
                badges.append(categories[cat_key]['badge'])

        if badges:
            # Determine overall section confidence
            if '❌' in badges:
                section_conf = "❌ Contains Low-Confidence Data"
            elif '⚠️' in badges:
                section_conf = "⚠️ Medium Confidence"
            else:
                section_conf = "✅ High Confidence"

            lines.append(f"- **{section}**: {section_conf}")

    return "\n".join(lines) if lines else "- *No section mapping provided*"


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("EXAMPLE 1: High-Confidence Report (Real sentiment analysis)")
    print("=" * 80)

    data_sources_1 = {
        'review_data_available': True,
        'steamspy_available': True,
        'revenue_method': 'calculated',
        'regional_revenue_source': 'industry_average',
        'sentiment_analyzed': True,
        'sentiment_sample_size': 200,
        'competitor_data_available': True,
        'influencer_data_available': True,
        'regional_pricing_method': 'ppp'
    }

    scorecard_1 = generate_confidence_scorecard(data_sources_1)
    print(scorecard_1)

    print("\n\n")
    print("=" * 80)
    print("EXAMPLE 2: Medium-Confidence Report (No sentiment analysis)")
    print("=" * 80)

    data_sources_2 = {
        'review_data_available': True,
        'steamspy_available': True,
        'revenue_method': 'estimated',
        'regional_revenue_source': 'industry_average',
        'sentiment_analyzed': False,
        'sentiment_sample_size': 0,
        'competitor_data_available': True,
        'influencer_data_available': False,
        'regional_pricing_method': 'industry'
    }

    scorecard_2 = generate_confidence_scorecard(data_sources_2)
    print(scorecard_2)

    print("\n\n")
    print("=" * 80)
    print("EXAMPLE 3: Low-Confidence Report (Limited data)")
    print("=" * 80)

    data_sources_3 = {
        'review_data_available': True,
        'steamspy_available': False,
        'revenue_method': 'industry_benchmark',
        'regional_revenue_source': 'industry_average',
        'sentiment_analyzed': False,
        'sentiment_sample_size': 0,
        'competitor_data_available': False,
        'influencer_data_available': False,
        'regional_pricing_method': 'industry'
    }

    scorecard_3 = generate_confidence_scorecard(data_sources_3)
    print(scorecard_3)
