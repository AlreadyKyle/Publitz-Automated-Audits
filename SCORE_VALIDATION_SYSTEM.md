# Score Validation System - Master Hard Caps

## ✅ FULLY INTEGRATED - Automatic Enforcement

The score validation system ensures that **no game can score higher than what commercial reality justifies**. A game with $379 revenue and 5 reviews can **NEVER** score above 50/100, regardless of other metrics.

---

## System Overview

### The Problem

Before validation:
- Games with terrible revenue scored too high based on hypothetical potential
- $379 revenue game could score 88/100 (completely unrealistic)
- Scores didn't reflect actual market performance

### The Solution

Three-layer validation system:
1. **Revenue Cap**: Based on daily revenue performance
2. **Review Volume Cap**: Based on data sufficiency
3. **Review Quality Cap**: Based on player satisfaction

**Final score = MINIMUM of all three caps**

This prevents score inflation from any single optimistic metric.

---

## How It Works (Automatic)

When you generate any report:

```python
from src.report_orchestrator import ReportOrchestrator

orchestrator = ReportOrchestrator()
report = orchestrator.generate_complete_report(game_data)

# Validation system AUTOMATICALLY:
# 1. Validates data sufficiency
# 2. Calculates hard caps based on revenue/reviews
# 3. Enforces caps on final score
# 4. Generates cap explanations
# 5. Includes improvement paths
```

---

## Hard Cap Thresholds

### Revenue Cap (Commercial Reality)

| Daily Revenue | Cap | Reason |
|--------------|-----|--------|
| < $100/day | 40/100 | Crisis tier - not commercially viable |
| $100-500/day | 60/100 | Struggling - severe challenges |
| $500-2K/day | 75/100 | Viable - has potential |
| $2K-10K/day | 90/100 | Strong - performing well |
| > $10K/day | 100/100 | Exceptional - commercial success |

### Review Volume Cap (Data Sufficiency)

| Review Count | Cap | Reason |
|-------------|-----|--------|
| < 10 reviews | 45/100 | Insufficient data for reliable assessment |
| 10-50 reviews | 65/100 | Limited validation |
| 50-100 reviews | 80/100 | Early stage but meaningful |
| 100-500 reviews | 90/100 | Well-validated |
| > 500 reviews | 100/100 | Extensively validated |

### Review Quality Cap (Player Satisfaction)

| Review Score | Cap | Reason |
|-------------|-----|--------|
| < 70% positive | 50/100 | Quality issues evident |
| 70-80% positive | 70/100 | Mixed reception |
| 80-90% positive | 85/100 | Good reception |
| > 90% positive | 100/100 | Excellent reception |

---

## Example: Retrace the Light

### Input Data
- Revenue: $379 (7 days) = $54/day
- Reviews: 5 total, 80% positive
- Owners: 100

### Calculated Caps
- **Revenue Cap**: 40/100 ($54/day = crisis tier)
- **Review Volume Cap**: 45/100 (5 reviews = insufficient data)
- **Review Quality Cap**: 85/100 (80% positive = good)

### Final Result
- **Maximum Possible Score**: 40/100 (limited by revenue)
- **Calculated Score** (after revenue modifiers): 32/100
- **Final Score**: 32/100 (within cap, no additional capping needed)

**Outcome**: Score reflects commercial reality. Game with $54/day revenue cannot score above 40/100.

---

## Validation Stages

### Stage 1: Data Sufficiency Check

Before generating any report, the system validates:

```python
# Check if game has enough data for meaningful audit
if review_count == 0 and owners < 50:
    return "INSUFFICIENT DATA - Cannot generate report"
```

**Blocks report generation for:**
- 0 reviews AND <50 owners (90% speculation)
- Completely new games with no market validation

**Allows with warning for:**
- <5 reviews (preliminary audit only)
- Limited data games (with clear disclaimers)

### Stage 2: Cap Calculation

System calculates three independent caps:

```python
caps = calculate_maximum_possible_score(game_metrics)

# Returns:
# {
#     'revenue_cap': 40,
#     'review_volume_cap': 45,
#     'review_quality_cap': 85,
#     'maximum_score': 40,  # Minimum of all three
#     'limiting_factor': 'revenue',
#     'limiting_reason': '$54/day (crisis tier)'
# }
```

### Stage 3: Score Enforcement

After calculating the score through normal scoring logic:

```python
cap_result = enforce_score_cap(calculated_score, caps, game_metrics)

# If calculated_score > maximum_score:
#   - Force score down to maximum
#   - Generate explanation
#   - Provide improvement path
```

### Stage 4: Report Integration

Cap explanations appear in all report tiers:

1. **Executive Brief**: Cap explanation after reality check warning
2. **Strategic Overview**: Full cap breakdown with improvement paths
3. **Deep-Dive**: Complete cap analysis with actionable steps

---

## Real-World Scenarios

### Scenario 1: Crisis Game ($379 revenue, 7 days)

**Input:**
- Daily revenue: $54/day
- Reviews: 5 total, 80% positive
- Hypothetical calculated score: 88/100

**Caps Applied:**
- Revenue: 40/100
- Review volume: 45/100
- Review quality: 85/100
- **Maximum: 40/100**

**Output:**
- Capped score: 40/100
- Explanation: "Limited by revenue ($54/day = crisis tier)"
- Path: "Increase daily revenue above $100 to unlock 60/100 cap"

### Scenario 2: Good Game, Insufficient Reviews

**Input:**
- Daily revenue: $1,200/day (viable)
- Reviews: 8 total, 92% positive
- Hypothetical calculated score: 85/100

**Caps Applied:**
- Revenue: 75/100
- Review volume: 45/100 ← LIMITING
- Review quality: 100/100
- **Maximum: 45/100**

**Output:**
- Capped score: 45/100
- Explanation: "Limited by review volume (8 reviews = insufficient data)"
- Path: "Reach 10+ reviews to unlock 65/100 cap"

### Scenario 3: High Revenue, Poor Quality

**Input:**
- Daily revenue: $3,500/day (strong)
- Reviews: 850 total, 62% positive
- Hypothetical calculated score: 75/100

**Caps Applied:**
- Revenue: 90/100
- Review volume: 90/100
- Review quality: 50/100 ← LIMITING
- **Maximum: 50/100**

**Output:**
- Capped score: 50/100
- Explanation: "Limited by review quality (62% positive = quality issues)"
- Path: "Fix quality issues to raise review score above 70%"

---

## Integration Points

### In `report_orchestrator.py`

The validation system is integrated at these points:

```python
def generate_complete_report(game_data):
    # Step 0: Validate data sufficiency
    should_generate, warning = validate_before_generation(game_metrics)
    if not should_generate:
        return insufficient_data_report()

    # Step 1: Calculate maximum possible score
    score_caps = calculate_maximum_possible_score(game_metrics)

    # Step 2-4: Calculate score with revenue modifiers
    calculated_score = calculate_with_revenue_modifiers()

    # Step 5: ENFORCE HARD CAPS
    cap_result = enforce_score_cap(calculated_score, score_caps, game_metrics)
    final_score = cap_result['final_score']

    # Step 6: Generate cap explanation
    cap_explanation = generate_cap_explanation_report(...)

    # Step 7-8: Add to all report tiers
    reports = assemble_reports_with_cap_explanation(...)
```

### Metadata Tracking

Report metadata includes validation info:

```python
metadata = ReportMetadata(
    overall_score=final_score,
    score_caps=score_caps,              # Cap details
    was_capped=True/False,              # Whether capping was applied
    original_score=88,                   # Pre-cap score
    cap_explanation="Limited by..."      # Explanation
)
```

---

## Improvement Paths

The system generates actionable guidance for raising caps:

### Revenue-Limited Games

```markdown
**To raise your score above 40/100:**

Your score is limited by revenue performance. Current: $54/day

**Immediate Goal:** Reach $100/day to unlock 60/100 cap

**Action Plan:**
1. Review "Critical Blockers" section for revenue-killing issues
2. Fix core gameplay/quality problems before marketing
3. Optimize pricing and visibility on Steam
4. Track daily revenue and iterate on fixes

**Reality Check:** Most games at this revenue level never recover.
Focus on whether the game is salvageable before investing more time.
```

### Review Volume-Limited Games

```markdown
**To raise your score above 45/100:**

Your score is limited by insufficient review data. Current: 5 reviews

**Immediate Goal:** Reach 10 reviews to unlock 65/100 cap

**Action Plan:**
1. Focus on player outreach and community building
2. Implement review prompts at natural engagement points
3. Engage with streamers/content creators for exposure
4. Ensure game quality justifies asking for reviews

**Warning:** Do NOT artificially inflate reviews. Focus on genuine player acquisition.
```

### Quality-Limited Games

```markdown
**To raise your score above 50/100:**

Your score is limited by player satisfaction. Current: 62% positive

**Immediate Goal:** Reach 70% positive to unlock 70/100 cap

**Action Plan:**
1. Analyze negative reviews for common complaints
2. Fix top 3 most-mentioned issues immediately
3. Respond to negative reviews showing you're listening
4. Update game and announce fixes to community

**Reality Check:** Raising review scores requires fixing actual problems, not marketing.
```

---

## Configuration

### Adjusting Thresholds

To make caps more/less strict, edit `src/score_validation.py`:

```python
def calculate_maximum_possible_score(game_metrics: GameMetrics):
    # Make revenue cap stricter
    if daily_revenue < 100:
        return 35  # Changed from 40 (more aggressive)

    # Make review volume cap more lenient
    if review_count < 10:
        return 50  # Changed from 45 (less restrictive)
```

### Disabling Specific Caps

You can disable individual caps (not recommended):

```python
# In enforce_score_cap()
overall_cap = min(
    caps['revenue_cap'],
    # caps['review_volume_cap'],  # Disabled
    caps['review_quality_cap']
)
```

---

## Testing

### Unit Tests

```bash
# Test validation module standalone
python src/score_validation.py

# Expected:
# ✅ TEST PASSED - Score capped at 40/100
```

### Integration Tests

```bash
# Test full integration with report orchestrator
python test_validation_integration.py

# Expected:
# ✅ ALL TESTS PASSED - Validation system working correctly
```

### Manual Testing

```python
from src.report_orchestrator import ReportOrchestrator

game_data = {
    'revenue': 379,
    'days_since_launch': 7,
    'review_count': 5,
    'review_score': 80.0,
    'owners': 100,
    # ... other fields
}

orchestrator = ReportOrchestrator()
report = orchestrator.generate_complete_report(game_data)

print(f"Final Score: {report['metadata'].overall_score}/100")
print(f"Was Capped: {report['metadata'].was_capped}")
print(f"Maximum Possible: {report['metadata'].score_caps.maximum_score}/100")
```

---

## Monitoring

The system logs all validation decisions:

```
INFO - Maximum possible score: 40/100 (limited by revenue)
INFO - Calculated score (after revenue adjustment): 88/100
WARNING - Score CAPPED: 88/100 → 40/100 (limited by revenue)
```

Check logs to verify caps are being applied correctly.

---

## Philosophy

### Why Hard Caps?

1. **Commercial Reality**: No game with $54/day revenue can realistically be "excellent"
2. **Data Reliability**: Can't confidently rate games with 5 reviews
3. **Quality Assurance**: Poor review scores indicate real problems
4. **Credibility**: Scores must reflect actual market performance, not speculation

### Why Minimum of All Caps?

Using the MINIMUM ensures no single optimistic metric inflates the score:

- High revenue + bad reviews = Capped by quality
- Good reviews + no revenue = Capped by revenue
- High revenue + 5 reviews = Capped by volume

This prevents games from "gaming" the system by excelling in one area while failing in others.

---

## Summary

### ✅ What's Working

- **Automatic validation** prevents score inflation
- **Three-layer caps** based on revenue, review volume, and quality
- **Hard enforcement** - scores can NEVER exceed caps
- **Clear explanations** tell developers exactly what's limiting them
- **Actionable paths** show how to raise caps
- **Fully integrated** into all report tiers

### ✅ Test Results

- **Retrace the Light**:
  - Revenue: $379 (7 days)
  - Reviews: 5 total, 80% positive
  - Maximum cap: 40/100
  - Final score: 32/100 ✅
  - Score reflects commercial reality ✅

### ✅ Production Ready

The validation system is fully integrated and working automatically. No manual configuration needed - just generate reports as normal.

---

**Status: ✅ PRODUCTION READY**

Last updated: 2025-11-25
