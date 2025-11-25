# Revenue-Based Scoring Integration Guide

## Overview

This system prevents score inflation by adjusting all scores based on actual commercial performance. A game with $379 revenue in 7 days should score 36/100, not 88/100.

## Test Results

✅ **System working correctly:**
- Input: $379 revenue (7 days), 80% reviews (5 total)
- Old score: 88/100 (inflated)
- New score: 36/100 (realistic)
- Score reduction: 60% modifier applied
- Reality check: ACTIVE

## Integration Steps

### 1. Import the Module

```python
from src.revenue_based_scoring import (
    classify_revenue_tier,
    apply_revenue_modifier,
    calculate_overall_score,
    generate_reality_check_warning,
    format_revenue_report
)
```

### 2. Basic Integration (Minimum Changes)

Add this to your existing report generation:

```python
def generate_report_with_revenue_reality(game_data):
    """
    Generate report with revenue-based score modifiers
    """
    # Your existing code to calculate section scores
    section_scores = {
        'community': calculate_community_score(game_data),
        'influencer': calculate_influencer_score(game_data),
        'regional': calculate_regional_score(game_data),
        # ... other sections
    }

    # NEW: Classify revenue tier
    revenue_tier = classify_revenue_tier(
        revenue_estimate=game_data['revenue'],
        days_since_launch=game_data['days_since_launch']
    )

    # NEW: Apply revenue modifier to all sections
    modified_sections = apply_revenue_modifier(section_scores, revenue_tier)

    # NEW: Calculate overall score with revenue weight
    review_metrics = {
        'review_percentage': game_data['review_score'],
        'review_count': game_data['review_count']
    }

    overall = calculate_overall_score(
        modified_sections,
        revenue_tier,
        review_metrics
    )

    # NEW: Generate reality check warning if needed
    warning = generate_reality_check_warning(
        revenue_tier,
        overall['overall_score'],
        modified_sections
    )

    # Build report with modified scores
    report = {
        'overall_score': overall['overall_score'],
        'revenue_tier': revenue_tier.tier_name,
        'section_scores': modified_sections,
        'reality_check_warning': warning,
        # ... rest of your report data
    }

    return report
```

### 3. Full Integration Example

```python
# In your report_orchestrator.py or main report generation

def generate_complete_report(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate report with revenue-based reality check
    """
    # Step 1: Calculate raw section scores (your existing code)
    raw_scores = {
        'community': self._calculate_community_score(game_data),
        'influencer': self._calculate_influencer_score(game_data),
        'regional': self._calculate_regional_score(game_data),
        'conversion': self._calculate_conversion_score(game_data),
        'retention': self._calculate_retention_score(game_data),
    }

    # Step 2: Apply revenue-based modifiers
    revenue_tier = classify_revenue_tier(
        revenue_estimate=game_data.get('revenue', 0),
        days_since_launch=game_data.get('days_since_launch', 1)
    )

    modified_scores = apply_revenue_modifier(raw_scores, revenue_tier)

    # Step 3: Calculate overall score with revenue weight
    review_metrics = {
        'review_percentage': game_data.get('review_score', 0),
        'review_count': game_data.get('review_count', 0)
    }

    overall_calc = calculate_overall_score(
        modified_scores,
        revenue_tier,
        review_metrics
    )

    # Step 4: Add revenue report to executive summary
    revenue_report = format_revenue_report(
        revenue_tier,
        modified_scores,
        overall_calc
    )

    # Step 5: Generate reality check warning
    reality_warning = generate_reality_check_warning(
        revenue_tier,
        overall_calc['overall_score'],
        modified_scores
    )

    # Build complete report
    report = {
        'overall_score': overall_calc['overall_score'],
        'revenue_tier': revenue_tier.tier_name,
        'revenue_analysis': revenue_report,
        'reality_check': reality_warning,
        'section_scores': modified_scores,
        'raw_scores': raw_scores,  # Keep for reference
        # ... rest of your report
    }

    return report
```

### 4. Add to Executive Summary

Insert the reality check warning at the top of your executive summary:

```python
def _generate_executive_summary(self, game_data, revenue_tier, overall_score, modified_scores):
    """
    Generate executive summary with revenue reality check
    """
    summary = "# Executive Summary\n\n"

    # Add reality check warning FIRST (if applicable)
    warning = generate_reality_check_warning(
        revenue_tier,
        overall_score,
        modified_scores
    )

    if warning:
        summary += warning + "\n\n---\n\n"

    # Rest of your executive summary
    summary += "## Bottom Line\n\n"
    summary += f"**Overall Score: {overall_score}/100 ({revenue_tier.tier_name} Tier)**\n\n"
    # ... rest of summary

    return summary
```

### 5. Display Score Changes in Report

Show clients what happened to their scores:

```python
def _generate_score_breakdown(self, modified_scores, revenue_tier):
    """
    Show how revenue modifier affected scores
    """
    md = "## Score Breakdown\n\n"

    if revenue_tier.reality_check:
        md += f"**⚠️ Revenue modifier applied: {revenue_tier.modifier} ({(1-revenue_tier.modifier)*100:.0f}% reduction)**\n\n"
        md += f"Due to ${revenue_tier.daily_revenue:.0f}/day revenue performance, all scores have been adjusted to reflect commercial reality.\n\n"

    md += "| Section | Raw Score | Final Score | Change |\n"
    md += "|---------|-----------|-------------|--------|\n"

    for section, scores in modified_scores.items():
        change = scores['final_score'] - scores['raw_score']
        change_str = f"{change:+d}" if change != 0 else "—"

        md += f"| {section.title()} | {scores['raw_score']} | **{scores['final_score']}** | {change_str} |\n"

    return md
```

## Revenue Tier Thresholds

Understanding when modifiers apply:

| Daily Revenue | Monthly Equiv | Tier | Modifier | Max Score |
|--------------|---------------|------|----------|-----------|
| < $100/day | < $3K/month | Crisis | 0.40 (60% off) | 65 |
| $100-500/day | $3K-15K/month | Struggling | 0.65 (35% off) | 65 |
| $500-2K/day | $15K-60K/month | Viable | 0.85 (15% off) | None |
| $2K-10K/day | $60K-300K/month | Strong | 0.95 (5% off) | None |
| > $10K/day | > $300K/month | Exceptional | 1.0 (no change) | None |

## Score Calculation Formula

```
Overall Score =
    (Revenue Tier × 20) × 35% +        # Revenue performance (most important)
    (Review %) × 25% +                  # Review quality
    (Review Volume Score) × 15% +       # Review volume (logarithmic)
    (Section Average) × 25%             # Modified section scores
```

## Examples

### Example 1: Crisis Game ($379 in 7 days)

```
Input:
- Revenue: $379 (7 days) = $54/day
- Reviews: 5 total, 80% positive
- Section scores: Community 85, Influencer 90, Regional 90

Output:
- Revenue Tier: Crisis (Tier 1)
- Modifier: 0.40 (60% reduction)
- Modified scores: Community 34, Influencer 36, Regional 36
- Overall: 36/100
- Reality check: ACTIVE
```

### Example 2: Viable Game ($50K in 90 days)

```
Input:
- Revenue: $50,000 (90 days) = $555/day
- Reviews: 500 total, 82% positive
- Section scores: Community 80, Influencer 75, Regional 85

Output:
- Revenue Tier: Viable (Tier 3)
- Modifier: 0.85 (15% reduction)
- Modified scores: Community 68, Influencer 64, Regional 72
- Overall: 68/100
- Reality check: Not triggered
```

### Example 3: Exceptional Game ($500K in 90 days)

```
Input:
- Revenue: $500,000 (90 days) = $5,555/day
- Reviews: 5000 total, 92% positive
- Section scores: Community 88, Influencer 85, Regional 90

Output:
- Revenue Tier: Strong (Tier 4)
- Modifier: 0.95 (5% reduction)
- Modified scores: Community 84, Influencer 81, Regional 86
- Overall: 87/100
- Reality check: Not triggered
```

## Configuration Options

### Adjust Revenue Thresholds

Edit `classify_revenue_tier()` in `revenue_based_scoring.py`:

```python
# Make crisis threshold stricter ($50/day instead of $100/day)
if daily_revenue < 50:
    return RevenueTier(tier=1, ...)
```

### Adjust Score Weights

Edit `calculate_overall_score()`:

```python
# Give revenue even more weight (50% instead of 35%)
overall = (
    revenue_score * 0.50 +    # Changed from 0.35
    review_score * 0.20 +     # Reduced from 0.25
    volume_score * 0.15 +
    section_avg * 0.15        # Reduced from 0.25
)
```

### Adjust Modifiers

Edit tier definitions to be more/less harsh:

```python
# Make crisis modifier even harsher
return RevenueTier(
    tier=1,
    modifier=0.30,  # Changed from 0.40 (70% reduction)
    ...
)
```

## Testing

Run the test suite to verify integration:

```bash
python src/revenue_based_scoring.py
```

Expected output:
```
✅ TEST PASSED - Score is in expected range (30-45)
```

## Troubleshooting

### Q: Scores still seem too high?

**A:** Adjust modifiers to be more aggressive:
- Crisis: 0.30 instead of 0.40
- Struggling: 0.50 instead of 0.65

### Q: How do I handle games with no revenue data?

**A:** Default to crisis tier:

```python
revenue = game_data.get('revenue', 0) or 0
days = game_data.get('days_since_launch') or 1

if revenue == 0:
    # Assume crisis tier for missing data
    revenue = 100  # $100 total = $100/day for 1 day = crisis tier
```

### Q: Can I disable reality check for certain games?

**A:** Yes, add override parameter:

```python
def apply_revenue_modifier(section_scores, revenue_tier, disable_reality_check=False):
    if disable_reality_check:
        revenue_tier.reality_check = False
    # ... rest of function
```

### Q: What if I want different weights per section?

**A:** Modify the section average calculation:

```python
# Custom weights
weights = {
    'community': 0.3,
    'influencer': 0.2,
    'regional': 0.2,
    'conversion': 0.15,
    'retention': 0.15
}

section_avg = sum(
    scores['final_score'] * weights[section]
    for section, scores in section_scores.items()
)
```

## API Reference

### `classify_revenue_tier(revenue_estimate, days_since_launch)`

**Returns:** `RevenueTier` object with:
- `tier`: int (1-5)
- `tier_name`: str
- `modifier`: float (0.3-1.0)
- `reality_check`: bool
- `message`: str
- `daily_revenue`: float
- `monthly_equivalent`: float

### `apply_revenue_modifier(section_scores, revenue_tier)`

**Returns:** Dict of modified scores with:
- `raw_score`: Original score
- `final_score`: Modified score
- `modifier_applied`: Modifier used
- `reduction`: Points reduced
- `warning`: Optional warning message

### `calculate_overall_score(section_scores, revenue_tier, review_metrics)`

**Returns:** Dict with:
- `overall_score`: int (0-100)
- `components`: Dict of score components
- `breakdown`: String showing calculation

### `generate_reality_check_warning(revenue_tier, overall_score, section_scores)`

**Returns:** Formatted warning string or None

### `format_revenue_report(revenue_tier, section_scores, overall_calculation)`

**Returns:** Formatted markdown report

## Next Steps

1. ✅ Test system with Retrace the Light data (PASSED)
2. ⬜ Integrate into your main report generation
3. ⬜ Add revenue report to executive summary
4. ⬜ Test with multiple game scenarios
5. ⬜ Deploy to production

## Support

If you need help integrating this system:

1. Check existing scores are being calculated correctly
2. Verify `days_since_launch` is accurate
3. Ensure revenue estimate is in USD
4. Run test suite to verify system works
5. Check logs for any errors

## Credits

System designed to solve score inflation problem where $379 revenue games were scoring 88/100. Now correctly scores such games at 36/100 with clear reality check warnings.
