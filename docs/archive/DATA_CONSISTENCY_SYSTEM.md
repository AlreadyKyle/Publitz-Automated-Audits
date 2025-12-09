# Data Consistency Validation System

## ✅ FULLY INTEGRATED - Automatic Validation

The data consistency validation system ensures that **all numbers in reports are accurate and consistent**. Prevents contradictions like "0 reviews" in one place and "5 reviews" in another.

---

## The Problem

Before data consistency validation:
- Reports might say "$0 revenue" in executive summary but "$379 revenue" in metrics
- Show "0 reviews" in one section but "5 reviews (80%)" in another
- Display review counts that exceed owner counts (mathematically impossible)
- Include negative revenue or other impossible values

**Result:** These contradictions destroy trust and credibility.

---

## The Solution

### Single Source of Truth: GameMetrics Class

All systems must pull from the `GameMetrics` class. This class:
1. **Validates data on initialization** - Catches contradictions immediately
2. **Computes derived metrics** - Daily revenue, review percentage, etc.
3. **Provides consistent values** - All components use the same numbers
4. **Logs errors/warnings** - Clear feedback about data quality issues

---

## How It Works (Automatic)

When you generate any report:

```python
from src.report_orchestrator import ReportOrchestrator

orchestrator = ReportOrchestrator()
report = orchestrator.generate_complete_report(game_data)

# Data consistency validation AUTOMATICALLY:
# 1. Validates all input data for contradictions
# 2. Creates GameMetrics as single source of truth
# 3. Catches critical errors (blocks report generation)
# 4. Flags warnings (allows report with disclaimers)
# 5. All components pull from validated GameMetrics
```

**No manual intervention needed** - validation runs automatically before every report.

---

## Validation Rules

### Critical Errors (Block Report Generation)

These prevent report generation entirely:

| Error | Check | Example |
|-------|-------|---------|
| **Negative Revenue** | `revenue >= 0` | ❌ Revenue: -$1000 |
| **Reviews Exceed Owners** | `reviews <= owners` | ❌ 500 reviews, 100 owners |
| **Review Math Error** | `positive + negative = total` | ❌ 4 + 1 ≠ 6 |
| **Negative Counts** | All counts >= 0 | ❌ -5 reviews |
| **Invalid Price** | `0 <= price <= 200` | ❌ Price: -$10 or $500 |
| **Invalid Days** | `days_since_launch > 0` | ❌ Days: 0 or -7 |

### Warnings (Allow Report)

These generate warnings but don't block reports:

| Warning | Check | Reason |
|---------|-------|--------|
| **Revenue Too Low** | Revenue vs owners × price | May indicate data quality issues |
| **Revenue Too High** | Revenue vs owners × price | May indicate data quality issues |
| **Low Review Rate** | < 1% reviews per owner | Typical: 2-5%, suggests incomplete data |
| **High Review Rate** | > 15% reviews per owner | May indicate review manipulation |
| **Small Sample Size** | < 10 reviews + high score | Score may not be representative |
| **Very Low Daily Revenue** | < $10/day with many owners | Check data quality |

---

## GameMetrics Class Structure

### Input Fields

```python
class GameMetrics:
    # Identity
    app_id: str
    game_name: str

    # Revenue
    revenue_gross: float          # Total revenue
    days_since_launch: int        # Days live

    # Reviews
    review_count_total: int       # Total reviews
    review_count_positive: int    # Positive reviews
    review_count_negative: int    # Negative reviews

    # Ownership
    owner_count: int              # Total owners

    # Pricing
    price_usd: float              # Current price

    # Metadata
    release_date: str
    genres: List[str]
```

### Computed Properties (Automatic)

```python
    # Automatically calculated in __post_init__:
    revenue_after_steam_cut: float    # revenue_gross × 0.7
    daily_revenue: float              # revenue_gross / days_since_launch
    monthly_revenue: float            # daily_revenue × 30
    review_percentage: float          # (positive / total) × 100
    review_rate: float                # (reviews / owners) × 100
    revenue_per_owner: float          # revenue_gross / owners
```

### Validation Results

```python
    # Set after validation:
    validation_errors: List[ValidationError]   # Critical errors
    validation_warnings: List[ValidationError] # Non-critical warnings
    is_valid: bool                            # Overall validity
```

---

## Usage Examples

### Example 1: Valid Data

```python
from src.data_consistency import pre_flight_check

game_data = {
    'app_id': '1234567',
    'name': 'Retrace the Light',
    'revenue': 379,
    'days_since_launch': 7,
    'review_count': 5,
    'review_score': 80.0,
    'positive_reviews': 4,
    'negative_reviews': 1,
    'owners': 100,
    'price': 14.99,
    'release_date': '2024-11-18',
    'genres': ['Adventure', 'Indie']
}

# Run validation
is_valid, metrics, messages = pre_flight_check(game_data)

# Result:
# is_valid: True
# messages: []
# metrics.daily_revenue: $54.14
# metrics.review_percentage: 80.0%
# metrics.review_rate: 5.00%
```

**Output:**
```
✅ All validation checks passed

Computed Metrics:
  Revenue (gross): $379
  Revenue (after Steam cut): $265.30
  Daily Revenue: $54.14
  Monthly Revenue: $1,624.29
  Review Percentage: 80.0%
  Review Rate: 5.00%
  Revenue per Owner: $3.79
```

### Example 2: Invalid Data (Reviews > Owners)

```python
game_data = {
    'app_id': '1234567',
    'name': 'Bad Data Game',
    'revenue': 1000,
    'days_since_launch': 7,
    'review_count': 500,    # ❌ More than owners!
    'review_score': 80.0,
    'positive_reviews': 400,
    'negative_reviews': 100,
    'owners': 100,          # Only 100 owners
    'price': 14.99,
    # ... other fields
}

is_valid, metrics, messages = pre_flight_check(game_data)

# Result:
# is_valid: False
# messages: [
#     "❌ ERROR: Review count (500) exceeds owner count (100)"
# ]
```

**Output:**
```
❌ ERROR: Review count (500) exceeds owner count (100)

Report generation blocked - fix data errors first
```

### Example 3: Warning Case (Low Review Rate)

```python
game_data = {
    'app_id': '1234567',
    'name': 'Low Review Rate Game',
    'revenue': 50000,
    'days_since_launch': 30,
    'review_count': 5,       # Only 5 reviews
    'owners': 10000,         # But 10,000 owners (0.05% rate)
    'price': 14.99,
    # ... other fields
}

is_valid, metrics, messages = pre_flight_check(game_data)

# Result:
# is_valid: True (warnings don't block)
# messages: [
#     "⚠️  WARNING: Very low review rate: 0.05% (5 reviews from 10,000 owners). Typical: 2-5%"
# ]
```

**Output:**
```
⚠️  WARNING: Very low review rate: 0.05% (5 reviews from 10,000 owners). Typical: 2-5%

Report will be generated with data quality disclaimers
```

---

## Integration with Report Orchestrator

The data consistency system is fully integrated into the report generation pipeline:

### Validation Flow

```python
def generate_complete_report(game_data):
    # Step 0a: DATA CONSISTENCY VALIDATION
    is_valid, data_metrics, messages = pre_flight_check(game_data)

    if not is_valid:
        # Critical errors - return error report
        return generate_data_error_report(game_data, messages)

    if messages:
        # Warnings logged but report continues
        log_warnings(messages)

    # Step 0b: SCORE VALIDATION
    # (Uses validated data_metrics)

    # Step 1-N: Generate report
    # (All components pull from validated data_metrics)
```

### Error Report Generated

When critical errors are found:

```markdown
# Game Audit Report: Bad Data Game

**Report Type**: Data Consistency Error
**Generated**: 2025-11-25 14:30
**App ID**: 1234567

---

## ❌ DATA CONSISTENCY ERRORS

The provided game data contains critical inconsistencies that prevent report generation:

❌ ERROR: Review count (500) exceeds owner count (100)
❌ ERROR: Review math doesn't add up: 400 + 100 ≠ 500

**What This Means:**

The data contains contradictions (e.g., review count exceeds owner count, negative revenue,
mathematical impossibilities). These errors must be fixed at the data source before a report
can be generated.

**Next Steps:**

1. Verify data sources (Steam API, SteamSpy, etc.)
2. Check for data collection errors
3. Ensure all metrics are from the same time period
4. Re-run data collection and try again

**Common Causes:**

- Mixing data from different time periods
- API errors or rate limiting
- Manual data entry mistakes
- Cached stale data
```

---

## Advanced Features

### Report Consistency Scanning

After report generation, you can scan for any remaining inconsistencies:

```python
from src.data_consistency import validate_report_consistency

# After generating report
report_text = report['tier_1_executive']
inconsistencies = validate_report_consistency(report_text, metrics)

# Returns list of potential inconsistencies:
# [
#     {
#         'type': 'revenue_mismatch',
#         'found': '$1,000',
#         'expected_values': ['$379', '$265'],
#         'context': 'Found revenue figure that doesn\'t match any known metric',
#         'severity': 'warning'
#     }
# ]
```

### Auto-Fix (Use With Caution)

For obvious contradictions (like "0 reviews" when we know there are reviews):

```python
from src.data_consistency import auto_fix_inconsistencies

# Fix obvious errors
corrected_report = auto_fix_inconsistencies(report_text, metrics)

# Fixes applied:
#   "0 reviews" → "5 reviews"
#   "$0 revenue" → "$379 revenue"
```

**Warning:** Auto-fix is conservative and only fixes obvious patterns. Better to fix at source.

---

## Common Validation Scenarios

### Scenario 1: Mixed Time Period Data

**Problem:**
```python
game_data = {
    'revenue': 50000,        # From last month
    'review_count': 200,     # From this week
    'owners': 5000,          # From Steam API (current)
}
```

**Detection:** Revenue per owner seems inconsistent ($10 per owner is too high)

**Solution:** Ensure all data is from the same time snapshot

### Scenario 2: API Rate Limiting

**Problem:**
```python
game_data = {
    'revenue': 0,            # ❌ API returned error, defaulted to 0
    'review_count': 150,
    'owners': 10000,
}
```

**Detection:** Revenue suspiciously low for owner count

**Solution:** Retry API calls, implement exponential backoff

### Scenario 3: Manual Entry Mistakes

**Problem:**
```python
game_data = {
    'review_count': 50,
    'positive_reviews': 40,
    'negative_reviews': 15,  # ❌ 40 + 15 = 55, not 50
}
```

**Detection:** Review math doesn't add up

**Solution:** Recalculate from source or fix entry error

---

## Monitoring & Debugging

### Logging

The system logs all validation decisions:

```
INFO - Running pre-flight data consistency check...
INFO - Data consistency check passed
WARNING - Data consistency warnings for Bad Game:
WARNING -   ⚠️  WARNING: Very low review rate: 0.05% (5 reviews from 10,000 owners)
ERROR - Data consistency check failed for Broken Game
ERROR -   ❌ ERROR: Review count (500) exceeds owner count (100)
```

### Validation Summary

Get human-readable validation summary:

```python
metrics = GameMetrics.from_game_data(game_data)
summary = metrics.get_validation_summary()
print(summary)

# Output:
# ✅ All validation checks passed
#
# OR
#
# ❌ 2 critical error(s):
#   - Review count (500) exceeds owner count (100)
#   - Revenue cannot be negative: $-1000
# ⚠️  1 warning(s):
#   - Very low review rate: 0.05%
```

### Accessing Detailed Errors

```python
for error in metrics.validation_errors:
    print(f"Type: {error.error_type}")
    print(f"Field: {error.field}")
    print(f"Message: {error.message}")
    print(f"Expected: {error.expected}")
    print(f"Actual: {error.actual}")
    print(f"Severity: {error.severity}")
```

---

## Configuration

### Adjusting Validation Thresholds

To make validation more/less strict, edit `src/data_consistency.py`:

```python
class GameMetrics:
    def _validate_warnings(self):
        # Make review rate check more lenient
        if self.review_rate < 0.5:  # Changed from 1.0 (more lenient)
            self.validation_warnings.append(...)

        # Make price check stricter
        if self.price_usd > 100:  # Changed from 200 (stricter)
            self.validation_errors.append(...)
```

### Disabling Specific Checks

To disable a specific validation (not recommended):

```python
def _validate_critical(self):
    # Revenue check (leave enabled)
    if self.revenue_gross < 0:
        self.validation_errors.append(...)

    # Review vs owner check (DISABLED)
    # if self.review_count_total > self.owner_count:
    #     self.validation_errors.append(...)
```

---

## Testing

### Unit Tests

```bash
# Test validation module standalone
python src/data_consistency.py

# Expected:
# ✅ All validation checks passed
```

### Integration Tests

```bash
# Test with report orchestrator
python test_data_consistency_integration.py

# Expected:
# ✅ PASSED: Valid Data
# ✅ PASSED: Invalid: Reviews > Owners
# ✅ PASSED: Invalid: Negative Revenue
# ✅ PASSED: Warning: Low Review Rate
```

### Manual Testing

```python
from src.data_consistency import GameMetrics, pre_flight_check

# Test with your data
game_data = {...}

is_valid, metrics, messages = pre_flight_check(game_data)

print(f"Valid: {is_valid}")
print(f"Messages: {messages}")
print(f"Daily Revenue: ${metrics.daily_revenue:.2f}")
print(f"Review Rate: {metrics.review_rate:.2f}%")
```

---

## Best Practices

### 1. Always Use GameMetrics as Source of Truth

**❌ DON'T:**
```python
# Different components using raw game_data
revenue = game_data['revenue']
daily_rev = game_data['revenue'] / game_data['days_since_launch']
# Risk of inconsistency!
```

**✅ DO:**
```python
# All components use validated metrics
revenue = metrics.revenue_gross
daily_rev = metrics.daily_revenue
# Guaranteed consistency!
```

### 2. Check Validation Results

**❌ DON'T:**
```python
# Ignore validation
metrics = GameMetrics.from_game_data(game_data)
# Continue regardless of validity
```

**✅ DO:**
```python
# Check validity first
is_valid, metrics, messages = pre_flight_check(game_data)
if not is_valid:
    handle_error(messages)
    return
# Proceed with valid data
```

### 3. Log Warnings

**❌ DON'T:**
```python
# Silent warnings
if metrics.validation_warnings:
    pass  # Ignore
```

**✅ DO:**
```python
# Log all warnings
if metrics.validation_warnings:
    for warning in metrics.validation_warnings:
        logger.warning(f"Data quality issue: {warning.message}")
# Add disclaimers to report
```

---

## Philosophy

### Why Single Source of Truth?

Multiple places calculating the same value = guaranteed inconsistency:

**Before:**
```python
# Component A
daily_revenue = revenue / days

# Component B
daily_revenue = revenue / max(days, 1)

# Component C
daily_revenue = (revenue * 0.7) / days

# Result: Three different values in same report!
```

**After:**
```python
# All components
daily_revenue = metrics.daily_revenue

# Result: One consistent value everywhere
```

### Why Validate Early?

Catching errors early prevents:
- Generating reports with bad data
- Wasting API calls on invalid games
- Confusing/contradictory outputs
- Loss of trust and credibility

**Better to block one bad report than generate 100 reports with contradictions.**

---

## Summary

### ✅ What's Working

- **Automatic validation** catches contradictions before report generation
- **Single source of truth** (GameMetrics) ensures consistency
- **Critical errors** block report generation with clear explanations
- **Warnings** allow reports but flag data quality issues
- **Comprehensive checks** cover all major contradiction types
- **Fully integrated** into report orchestrator

### ✅ Validation Coverage

- ✅ Negative values (revenue, counts)
- ✅ Mathematical impossibilities (reviews > owners)
- ✅ Internal consistency (review math)
- ✅ Reasonable ranges (price, days)
- ✅ Statistical anomalies (review rates)
- ✅ Data quality indicators (small samples)

### ✅ Production Ready

The data consistency system is fully integrated and working automatically. All reports now pull from validated GameMetrics, ensuring zero contradictions.

---

**Status: ✅ PRODUCTION READY**

Last updated: 2025-11-25
