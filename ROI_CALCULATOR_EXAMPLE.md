# ROI Calculator - Standardized ROI for Every Action

## Overview

The ROI Calculator provides **data-driven, justified investment and return estimates** for every recommended action in game audit reports.

Indie devs need to justify every hour and dollar spent. Instead of generic advice like "optimize your pricing", the ROI calculator provides:

> **Regional Pricing Optimization**: 12 hours, $600 total investment, 1.8x ROI, payback in 1 week. Expected revenue: $735-$2.2K. Confidence: High.

## When to Use

Use the ROI Calculator for **every action recommendation** in reports:
- Pricing changes (regional pricing, discounts)
- Marketing campaigns (influencer outreach, review score marketing)
- Content updates (minor updates, major updates, DLC)
- Bug fixes (critical, moderate, minor)
- Store page optimization
- Any other recommended actions

## Calculation Framework

For each action, the calculator provides:

###1. **Time Investment**
- Research hours
- Implementation hours
- Testing/QA hours
- **Total hours** (with weeks conversion)

### 2. **Financial Investment**
- Tools/software costs
- Services (design, translation, outsourcing)
- Marketing spend
- **Total cost**

### 3. **Expected Revenue Impact**
- **Conservative estimate** (50-70% of likely)
- **Likely estimate** (base case, most probable)
- **Optimistic estimate** (150-200% of likely)

### 4. **ROI Calculations**
- ROI ratio for each scenario
- Formula: (Revenue - Investment) / Investment
- Example: $2K revenue / $600 investment = 3.3x ROI

### 5. **Payback Period**
- Weeks to recover investment
- Based on revenue timeline
- Conservative/Likely/Optimistic scenarios

### 6. **Confidence Level**
- ✅ **High** (>75% confidence) - Proven strategies, clear data
- ⚠️ **Medium** (50-75% confidence) - Reasonable estimates, some variability
- ❌ **Low** (<50% confidence) - Speculative, high uncertainty

### 7. **Priority Score**
- Formula: `(ROI × Confidence × Risk Factor) / Time Factor`
- Higher score = Do this first
- Automatically ranks all actions

## Example Output

### ROI Comparison Matrix

| Action | Investment | Revenue Impact | ROI | Payback | Confidence | Priority |
|--------|------------|----------------|-----|---------|------------|----------|
| Micro-Tier Influencer Campaign | $1.2K (9h) | $12K - $50K | 21.1x | 0w | ⚠️ Medium | 10.1 |
| Price Reduction (20%) | $100 (2h) | $197 - $997 | 6.0x | 1w | ⚠️ Medium | 2.9 |
| Regional Pricing Optimization | $600 (12h) | $735 - $2K | 1.8x | 1w | ✅ High | 1.4 |
| Store Page Optimization | $2.2K (15h) | $540 - $1K | 0.4x | 9w | ✅ High | 0.3 |
| Review Score Marketing Emphasis | $700 (4h) | $150 - $225 | 0.3x | 7w | ✅ High | 0.2 |
| Critical Bug Fix | $3.2K (64h) | $375 - $1K | 0.2x | 9w | ✅ High | 0.2 |
| Major Content Update | $12.5K (200h) | $900 - $2K | 0.1x | 1.9y | ⚠️ Medium | 0.0 |

**Priority Score Formula**: (ROI × Confidence × Risk Factor) / Time Factor
**Higher priority score = Do this first**

### Detailed Action Report

```markdown
## Micro-Tier Influencer Campaign

Partner with 5 micro-tier influencers for sponsored content

### Investment Required

| Category | Amount | Details |
|----------|--------|---------|
| **Time** | 9 hours | Research: 2h, Implementation: 5h, Testing: 1h |
| **Money** | $750 | Services: $750 |
| **Total Investment** | $1,188 | Time valued at $50/hour + financial costs |

### Expected Returns

| Scenario | Revenue Impact | ROI | Payback Period |
|----------|----------------|-----|----------------|
| **Conservative** | $12K | 10.5x | 0 weeks |
| **Likely** | $25K | 21.1x | 0 weeks |
| **Optimistic** | $50K | 42.1x | 0 weeks |

**Confidence Level**: ⚠️ Medium

**Based on**: Industry benchmarks, similar games data, and conversion rate analysis

### Success Metrics

Track these to validate ROI:
- Reach 25,000 potential customers
- Generate 500 sales
- Track referral links for attribution

**Timeline to Results**: 4 weeks

### Risk Factors

⚠️ **Risk 1**: Influencer audience may not match your game
- **Probability**: Medium
- **Impact if occurs**: May reduce expected ROI by 20-30%
- **Mitigation**: Monitor closely and adjust approach based on early results

⚠️ **Risk 2**: Conversion rates vary significantly
- **Mitigation**: Continuous monitoring and adjustment

---
```

## Available Action Templates

The calculator includes pre-built ROI calculators for:

### 1. **Regional Pricing Optimization**
```python
calculator.calculate_regional_pricing_roi(
    current_revenue=5000,  # Monthly revenue
    current_regions=1,     # Number of regions with pricing
    game_genre="indie"
)
```

**Typical Results**:
- Investment: 12 hours, $0-200
- Revenue Impact: +15-25% from new regions
- ROI: 5-15x
- Confidence: High

### 2. **Price Reduction Test**
```python
calculator.calculate_price_reduction_roi(
    current_price=19.99,
    current_revenue=5000,
    current_units_sold=250,
    price_reduction_percent=20
)
```

**Typical Results**:
- Investment: 2 hours, $0
- Revenue Impact: Variable (depends on price elasticity)
- ROI: 3-10x if elastic, <1x if inelastic
- Confidence: Medium

### 3. **Content Update**
```python
calculator.calculate_content_update_roi(
    current_revenue=5000,
    content_type="major",  # 'minor', 'major', 'dlc'
    current_review_score=72
)
```

**Typical Results**:
- Minor: 52h, $700, 10-30% revenue lift
- Major: 200h, $2500, 30-50% revenue lift
- DLC: 252h, $6000, 50-100% revenue lift
- Confidence: Medium

### 4. **Bug Fix**
```python
calculator.calculate_bug_fix_roi(
    current_revenue=5000,
    current_review_score=65,
    bug_severity="critical"  # 'minor', 'moderate', 'critical'
)
```

**Typical Results**:
- Critical: 64h, $3200, +15% revenue, +8% reviews
- Moderate: 28h, $1400, +5% revenue, +3% reviews
- Minor: 7h, $350, +2% revenue, +1% reviews
- Confidence: High (for critical), Medium (for others)

### 5. **Influencer Campaign**
```python
calculator.calculate_influencer_campaign_roi(
    current_revenue=5000,
    influencer_tier="micro",  # 'micro', 'mid', 'major'
    num_influencers=5
)
```

**Typical Results**:
- Micro (5): 9h, $750, 10-40x ROI
- Mid (3): 6h, $2250, 5-15x ROI
- Major (1): 4h, $3000, 2-10x ROI
- Confidence: Medium (variable conversion rates)

### 6. **Review Score Marketing**
```python
calculator.calculate_review_score_marketing_roi(
    current_ad_spend=500,
    current_conversion_rate=2.5,
    review_score=89,
    current_revenue=5000
)
```

**Typical Results**:
- Investment: 4h, $500
- Conversion lift: +5-25% (based on review score)
- ROI: 0.2-2x
- Confidence: High

### 7. **Store Page Optimization**
```python
calculator.calculate_store_page_optimization_roi(
    current_traffic=10000,  # Monthly store views
    current_conversion_rate=3.0,
    issues_identified=3,  # Number of major issues
    average_price=19.99
)
```

**Typical Results**:
- Investment: ~5h per issue, $500 per issue
- Conversion lift: +3-8% per issue fixed
- ROI: 0.3-2x depending on traffic
- Confidence: High

## Usage in Reports

### Quick Integration

```python
from src.roi_calculator import ROICalculator

# Initialize calculator (default: $50/hr dev time)
calculator = ROICalculator(hourly_rate=50)

# Calculate ROI for recommended actions
regional_pricing = calculator.calculate_regional_pricing_roi(
    current_revenue=game_revenue,
    current_regions=1
)

bug_fix = calculator.calculate_bug_fix_roi(
    current_revenue=game_revenue,
    current_review_score=review_percentage,
    bug_severity="critical"
)

# Generate comparison table
all_actions = [regional_pricing, bug_fix, ...]
roi_comparison = calculator.generate_roi_table(all_actions)

# Add to report
report += "\n\n" + roi_comparison

# Add detailed breakdown for top 3 actions
sorted_actions = sorted(all_actions, key=lambda a: a.priority_score, reverse=True)
for action in sorted_actions[:3]:
    report += calculator.generate_detailed_roi_report(action)
```

### Custom Actions

For actions not in the templates:

```python
from src.roi_calculator import (
    ROICalculation,
    TimeInvestment,
    FinancialInvestment,
    RevenueImpact,
    ConfidenceLevel
)

custom_action = ROICalculation(
    action_name="Steam Deck Optimization",
    description="Add Steam Deck support and verification",
    time_investment=TimeInvestment(
        research_hours=8,
        implementation_hours=40,
        testing_hours=16
    ),
    financial_investment=FinancialInvestment(
        tools_software=0,
        services=500,  # Steam Deck hardware for testing
        marketing_spend=0
    ),
    revenue_impact=RevenueImpact(
        conservative=2000,
        likely=4000,
        optimistic=8000
    ),
    confidence_level=ConfidenceLevel.MEDIUM,
    timeline_weeks=8,
    success_metrics=[
        "Steam Deck verified badge obtained",
        "10-15% sales increase from Deck users",
        "Positive reviews mention Deck compatibility"
    ],
    risk_factors=[
        "Development may take longer than estimated",
        "Deck market share varies by genre"
    ]
)
```

## Key Benefits

### 1. **Justified Recommendations**
Instead of: "You should optimize your pricing"
You get: "Regional pricing: 12h investment, 1.8x ROI, $735-$2.2K return, payback in 1 week"

### 2. **Priority Ranking**
Actions automatically sorted by priority score so devs know what to do first

### 3. **Risk-Aware**
Every recommendation includes risk factors and mitigation strategies

### 4. **Success Metrics**
Clear targets to track whether the action actually worked

### 5. **Confidence Levels**
Honest assessment of estimate reliability

## Formulas Used

### Regional Pricing
- Revenue Lift = Regions Added × 3% per region
- Conservative: 70% of expected
- Likely: Full expected
- Optimistic: 150% of expected

### Price Reduction
- Uses price elasticity of demand (typically 1.5-2.5x for games)
- Conservative: 1.5x elasticity
- Likely: 2.0x elasticity
- Optimistic: 2.5x elasticity

### Content Updates
- Minor: +10% revenue lift
- Major: +30% revenue lift
- DLC: +50% revenue lift (new revenue stream)

### Bug Fixes
- Critical: +15% revenue (prevents refunds)
- Moderate: +5% revenue
- Minor: +2% revenue

### Influencer Campaigns
- Micro: 5K viewers, 2% conversion
- Mid: 25K viewers, 1.5% conversion
- Major: 100K viewers, 1% conversion

### Store Page Optimization
- +3-8% conversion per major issue fixed
- Caps at +60% total improvement

## Testing

To test the calculator:

```bash
python3 -c "from src.roi_calculator import test_roi_calculator; test_roi_calculator()"
```

This will calculate ROI for 7 different actions and display comparison table + detailed report for top action.

## Dependencies

- Pure Python 3.7+
- No external dependencies
- Integrates with existing report generation system

## Next Steps

The ROI calculator is ready to integrate into all report recommendations. Every action should include:

1. **Investment breakdown** (time + money)
2. **Expected returns** (conservative/likely/optimistic)
3. **ROI ratios** for each scenario
4. **Payback period** in weeks
5. **Confidence level** (High/Medium/Low)
6. **Priority score** for ranking
7. **Success metrics** to track
8. **Risk factors** and mitigation

This transforms generic advice into justified, actionable recommendations that indie devs can confidently execute.
