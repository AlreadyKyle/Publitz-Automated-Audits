# Report Orchestrator - Complete Assembly System

## Overview

The Report Orchestrator is the **master coordination system** that assembles all modular components into complete, tiered game audit reports.

Instead of manually combining components, the orchestrator:
1. Calculates overall performance score
2. Determines performance tier (1-4)
3. Generates appropriate components
4. Assembles three report versions
5. Validates quality
6. Returns production-ready reports

## Quick Start

```python
from src.report_orchestrator import ReportOrchestrator

# Initialize orchestrator
orchestrator = ReportOrchestrator(hourly_rate=50)

# Prepare game data
game_data = {
    'app_id': '1145350',
    'name': 'Hades II',
    'price': 29.99,
    'review_score': 91,
    'review_count': 15847,
    'owners': 500000,
    'revenue': 12500000,
    'genres': ['Roguelike', 'Action', 'Indie'],
    'release_date': '2024-05-06'
}

# Generate complete report
reports = orchestrator.generate_complete_report(game_data)

# Access three report tiers
tier_1 = reports['tier_1_executive']  # 2-3 pages, essential insights
tier_2 = reports['tier_2_strategic']  # 8-12 pages, strategic overview
tier_3 = reports['tier_3_deepdive']   # 30-40 pages, complete analysis

# Check metadata
metadata = reports['metadata']
print(f"Score: {metadata.overall_score}/100")
print(f"Tier: {metadata.tier_name}")
print(f"Word counts: T1={metadata.word_count['tier_1']}, "
      f"T2={metadata.word_count['tier_2']}, "
      f"T3={metadata.word_count['tier_3']}")
```

## Performance Tiers

The orchestrator automatically classifies games into 4 performance tiers:

### Tier 4: Exceptional (81-100 points)
- **Characteristics**: 90%+ reviews, 50K+ owners
- **Focus**: Scaling and maximization
- **Unique Sections**: DLC analysis, global expansion, brand building
- **Tone**: Celebratory, ambitious

### Tier 3: Solid (66-80 points)
- **Characteristics**: 80-90% reviews, 10K-50K owners
- **Focus**: Optimization and growth
- **Unique Sections**: Market expansion, content updates, influencer campaigns
- **Tone**: Encouraging, opportunity-focused

### Tier 2: Struggling (41-65 points)
- **Characteristics**: 70-80% reviews, mixed feedback
- **Focus**: Quality improvement and quick wins
- **Unique Sections**: Negative review analysis, fix-it plans
- **Tone**: Constructive, solution-oriented

### Tier 1: Crisis (0-40 points)
- **Characteristics**: <70% reviews, serious issues
- **Focus**: Immediate damage control
- **Unique Sections**: Salvageability assessment, critical bug fixes
- **Tone**: Urgent, honest, focused

## Scoring System

### Overall Score Formula

```
score = (review_percentage × 0.7) + owner_bonus - review_penalty
```

**Review Percentage (70% weight)**:
- Primary quality indicator
- 70% positive reviews = 49 base points
- 90% positive reviews = 63 base points

**Owner Bonus (30% weight)**:
- 100K+ owners: +15 points
- 50K-100K owners: +10 points
- 10K-50K owners: +5 points
- <10K owners: +0 points

**Review Penalty (validation)**:
- <50 reviews: -5 points (insufficient data)
- <100 reviews: -2 points (limited validation)
- 100+ reviews: 0 penalty

### Example Calculations

**Exceptional Game**:
- 96% reviews × 0.7 = 67.2
- 500K owners = +15
- 50K reviews = 0 penalty
- **Final Score: 82.2 → Tier 4**

**Struggling Game**:
- 72% reviews × 0.7 = 50.4
- 15K owners = +5
- 500 reviews = 0 penalty
- **Final Score: 55.4 → Tier 2**

**Crisis Game**:
- 58% reviews × 0.7 = 40.6
- 5K owners = 0
- 100 reviews = -2
- **Final Score: 38.6 → Tier 1**

## Report Structure

### Tier 1: Executive Brief (2-3 pages)

**Purpose**: Quick decision-making for busy developers

**Contents**:
1. **Executive Summary** - 300-500 words, tier-adaptive
2. **Data Confidence Scorecard** - Reliability of analysis
3. **Quick Start** - Top 3 actions with ROI
4. **Key Metrics Dashboard** - At-a-glance performance
5. **Critical Section** (tier-specific):
   - Tier 1-2: Salvageability assessment
   - Tier 3-4: Growth opportunity summary

**Target Audience**: Solo devs, small teams, decision makers

**Reading Time**: 5-10 minutes

### Tier 2: Strategic Overview (8-12 pages)

**Purpose**: Comprehensive strategic guidance

**Contents**:
- All of Tier 1, plus:
6. **Market Positioning Analysis** - Where you stand vs. competitors
7. **Comparable Games Comparison** - What similar games did right/wrong
8. **Revenue Performance** - Detailed revenue analysis
9. **Strategic Recommendations** - Tier-specific strategies
10. **30-Day Action Plan with ROI** - Prioritized actions with calculations
11. **Tier-Specific Deep Sections**:
    - Tier 1-2: Full negative review analysis
    - Tier 3-4: Market expansion strategies

**Target Audience**: Teams planning strategy, producers, publishers

**Reading Time**: 30-45 minutes

### Tier 3: Deep-Dive Report (30-40 pages)

**Purpose**: Complete analysis for serious optimization

**Contents**:
- All of Tier 1 & 2, plus:
12. **Detailed Competitive Analysis** - Deep competitor breakdowns
13. **Regional Market Breakdowns** - Geographic opportunities
14. **Store Asset Optimization** - Page-by-page recommendations
15. **DLC Analysis** (Tier 3-4 only) - DLC viability and ROI
16. **Complete Methodology** - How scores were calculated
17. **Appendices** - Raw data, references, calculations

**Target Audience**: Optimization specialists, data analysts, long-term planning

**Reading Time**: 2-3 hours

## Component Integration

The orchestrator integrates these pre-built components:

### Always Included (All Tiers)

```python
from src.executive_summary_generator import ExecutiveSummaryGenerator
from src.roi_calculator import ROICalculator
from src.comparable_games_analyzer import ComparableGamesAnalyzer

# Universal components
exec_summary = ExecutiveSummaryGenerator().generate_summary(...)
roi_actions = ROICalculator().generate_roi_table(...)
comparables = ComparableGamesAnalyzer().find_comparable_games(...)
```

### Tier-Specific Components

**Tiers 1-2 (Crisis/Struggling)**:
```python
from src.negative_review_analyzer import NegativeReviewAnalyzer

# Only for struggling games with <80% reviews
if tier <= 2 and review_score < 80:
    negative_analysis = NegativeReviewAnalyzer().analyze_reviews(app_id)
    salvageability = NegativeReviewAnalyzer().assess_salvageability(...)
```

**Tiers 3-4 (Solid/Exceptional)**:
```python
# Growth-focused components
market_expansion = orchestrator._generate_market_expansion(game_data)
dlc_analysis = orchestrator._generate_dlc_analysis(game_data)
competitive_analysis = orchestrator._generate_detailed_competitive(game_data)
```

## Quality Validation

Before delivery, reports are validated for quality:

```python
from src.report_orchestrator import validate_report

# Run validation
issues = validate_report(reports, tier)

if issues:
    print(f"⚠️  {len(issues)} quality issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ All quality checks passed")
```

### Quality Checks

1. **Completeness**: All three report tiers exist and are non-empty
2. **Structure**: Executive summary, quick start, and key sections present
3. **Length**: Word counts are appropriate for tier (T1<T2<T3)
4. **Confidence Indicators**: High/Medium/Low markers present
5. **ROI Calculations**: Action plan includes ROI data
6. **Tier-Specific Sections**: Appropriate sections for performance tier
7. **Methodology**: Tier 3 includes complete methodology
8. **No Placeholders**: No "Coming soon" or error messages
9. **Formatting**: Clean markdown, consistent structure
10. **Data Integrity**: No contradictions in recommendations

## Testing Framework

The orchestrator includes a comprehensive test suite:

```bash
# Run full test suite
python3 -c "from src.report_orchestrator import test_report_generation; test_report_generation()"
```

### Test Cases

**Test 1: Crisis Game (Tier 1)**
- Score: 38.6/100
- 58% reviews, 123 count, 5K owners
- Expected: Salvageability assessment, critical bug fixes
- Should NOT include: DLC analysis, market expansion

**Test 2: Struggling Game (Tier 2)**
- Score: 55.4/100
- 72% reviews, 487 count, 15K owners
- Expected: Negative review analysis, quick wins
- Should NOT include: DLC analysis

**Test 3: Solid Game (Tier 3)**
- Score: 72.0/100
- 85% reviews, 2,847 count, 75K owners
- Expected: Market expansion, optimization strategies
- Should NOT include: Salvageability assessment

**Test 4: Exceptional Game (Tier 4)**
- Score: 88.5/100
- 96.5% reviews, 50,302 count, 500K owners
- Expected: DLC analysis, scaling strategies, global expansion
- Should NOT include: Crisis management

## Integration Examples

### Example 1: Basic Report Generation

```python
from src.report_orchestrator import ReportOrchestrator

orchestrator = ReportOrchestrator(hourly_rate=50)

game_data = {
    'app_id': '646570',
    'name': 'Slay the Spire',
    'price': 24.99,
    'review_score': 94,
    'review_count': 67234,
    'owners': 2000000,
    'revenue': 35000000,
    'genres': ['Roguelike', 'Deck Building', 'Strategy'],
    'release_date': '2019-01-23'
}

reports = orchestrator.generate_complete_report(game_data)

# Save to file
with open('slay_the_spire_executive.md', 'w') as f:
    f.write(reports['tier_1_executive'])

with open('slay_the_spire_strategic.md', 'w') as f:
    f.write(reports['tier_2_strategic'])

with open('slay_the_spire_deepdive.md', 'w') as f:
    f.write(reports['tier_3_deepdive'])
```

### Example 2: Batch Report Generation

```python
from src.report_orchestrator import ReportOrchestrator
from src.game_search import GameSearch

orchestrator = ReportOrchestrator()
game_search = GameSearch()

# List of games to audit
app_ids = ['1145350', '646570', '863550', '632360']

for app_id in app_ids:
    # Fetch game data
    game_details = game_search.get_game_details(int(app_id))
    spy_data = game_search.get_steamspy_data(int(app_id))

    # Prepare data
    game_data = {
        'app_id': app_id,
        'name': game_details.get('name'),
        'price': game_details.get('price_raw', 0),
        'review_score': game_details.get('review_score_raw', 0),
        'review_count': game_details.get('review_count', 0),
        'owners': spy_data.get('owners_avg', 0),
        'revenue': spy_data.get('revenue_estimate', 0),
        'genres': game_details.get('genres', []),
        'release_date': game_details.get('release_date', '')
    }

    # Generate report
    reports = orchestrator.generate_complete_report(game_data)

    # Save executive summary
    filename = f"{game_data['name'].replace(' ', '_')}_audit.md"
    with open(filename, 'w') as f:
        f.write(reports['tier_1_executive'])

    print(f"✅ Generated report for {game_data['name']} "
          f"(Tier {reports['metadata'].performance_tier}, "
          f"Score: {reports['metadata'].overall_score:.1f}/100)")
```

### Example 3: Custom Component Integration

```python
from src.report_orchestrator import ReportOrchestrator

# Extend the orchestrator with custom components
class CustomOrchestrator(ReportOrchestrator):

    def _generate_custom_section(self, game_data):
        """Add your custom analysis"""
        md = "## Custom Analysis\n\n"
        # Your custom logic here
        return md

    def _assemble_executive_brief(self, components, game_data, tier):
        """Override to add custom sections"""
        report = super()._assemble_executive_brief(components, game_data, tier)
        report += "\n\n" + self._generate_custom_section(game_data)
        return report

# Use custom orchestrator
custom_orch = CustomOrchestrator()
reports = custom_orch.generate_complete_report(game_data)
```

## Performance Optimization

### Caching

The orchestrator leverages existing caching in component modules:

```python
# GameSearch already caches Steam API calls
# ComparableGamesAnalyzer reuses cached data
# ROICalculator is stateless and fast
# NegativeReviewAnalyzer caches Claude API calls
```

### Parallel Component Generation

For production use, consider parallelizing component generation:

```python
from concurrent.futures import ThreadPoolExecutor

def generate_component_parallel(game_data, tier):
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all component generation tasks
        future_exec_summary = executor.submit(
            orchestrator._generate_executive_summary, game_data, tier, score
        )
        future_comparable = executor.submit(
            orchestrator._generate_comparable_games, game_data
        )
        future_roi = executor.submit(
            orchestrator._generate_action_plan_with_roi, game_data, tier
        )

        # Wait for results
        exec_summary = future_exec_summary.result()
        comparable = future_comparable.result()
        roi = future_roi.result()
```

## Error Handling

The orchestrator includes graceful error handling:

```python
try:
    reports = orchestrator.generate_complete_report(game_data)
except Exception as e:
    logger.error(f"Report generation failed: {e}")
    # Each component has fallback behavior
    # "*Analysis unavailable*" instead of crashing
```

**Component-Level Fallbacks**:
- Executive summary: Generic template if tier detection fails
- Comparable games: "No comparable games found" if search fails
- Negative reviews: "Analysis unavailable" if API fails
- ROI calculations: Skip invalid actions gracefully

## API Reference

### ReportOrchestrator

**Constructor**:
```python
ReportOrchestrator(hourly_rate: float = 50.0)
```

**Main Method**:
```python
generate_complete_report(game_data: Dict[str, Any]) -> Dict[str, Any]
```

**Returns**:
```python
{
    'tier_1_executive': str,  # 2-3 page report
    'tier_2_strategic': str,  # 8-12 page report
    'tier_3_deepdive': str,   # 30-40 page report
    'metadata': ReportMetadata,
    'components': ReportComponents
}
```

### ReportMetadata

```python
@dataclass
class ReportMetadata:
    overall_score: float           # 0-100
    performance_tier: int          # 1-4
    tier_name: str                 # "Crisis", "Struggling", "Solid", "Exceptional"
    generated_at: datetime
    game_name: str
    app_id: str
    confidence_level: str          # "High", "Medium", "Low"
    word_count: Dict[str, int]     # {'tier_1': 800, 'tier_2': 3500, ...}
    has_negative_reviews: bool
    has_comparables: bool
```

### Validation Function

```python
validate_report(
    report_dict: Dict[str, Any],
    tier: int
) -> List[str]  # Returns list of issues (empty if valid)
```

## Best Practices

### 1. Always Validate

```python
reports = orchestrator.generate_complete_report(game_data)
issues = validate_report(reports, reports['metadata'].performance_tier)

if not issues:
    # Safe to deliver
    deliver_report(reports['tier_1_executive'])
```

### 2. Check Data Quality First

```python
# Verify minimum data requirements
if game_data['review_count'] < 10:
    print("⚠️  Warning: Very low review count, results may be unreliable")

if not game_data.get('genres'):
    print("⚠️  Warning: No genre data, comparable games analysis will be limited")
```

### 3. Use Appropriate Tier for Audience

```python
# For client email/summary
send_email(reports['tier_1_executive'])

# For strategy meeting
present(reports['tier_2_strategic'])

# For deep optimization work
analyze(reports['tier_3_deepdive'])
```

### 4. Monitor Component Performance

```python
import time

start = time.time()
reports = orchestrator.generate_complete_report(game_data)
duration = time.time() - start

print(f"Report generated in {duration:.1f}s")

# Typical performance:
# - Tier 1: 5-10 seconds
# - Tier 2: 15-30 seconds (includes comparable games search)
# - Tier 3: 30-60 seconds (includes negative review analysis if applicable)
```

## Troubleshooting

### Issue: "No comparable games found"

**Cause**: Game is too unique or has unusual characteristics

**Solution**:
- Check if genre tags are present
- Verify price is reasonable ($1-$60)
- Ensure release date is recent (<5 years)
- Lower matching strictness in comparable analyzer

### Issue: "Negative review analysis unavailable"

**Cause**: API rate limits or no negative reviews

**Solution**:
- Check Claude API key is valid
- Verify game has negative reviews (<80% positive)
- Check Steam API access

### Issue: Word count too low

**Cause**: Missing data or component failures

**Solution**:
- Check all required fields in game_data
- Review component error logs
- Validate Steam API responses

### Issue: Tier classification seems wrong

**Cause**: Edge case in scoring

**Solution**:
- Review score calculation manually
- Check owner count accuracy
- Verify review count penalty isn't too harsh

## Next Steps

1. **Integration**: Connect to your game data pipeline
2. **Customization**: Add game-specific components
3. **Automation**: Set up batch processing for multiple games
4. **Delivery**: Build PDF/email delivery system
5. **Analytics**: Track which recommendations get implemented

## Support

For issues or questions:
- Check component-specific documentation (ROI_CALCULATOR_EXAMPLE.md, etc.)
- Review test cases for examples
- Check logs for component-level errors
