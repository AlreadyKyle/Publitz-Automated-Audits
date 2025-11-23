# Comparable Games Analyzer - Example Output

## Overview

The Comparable Games Analyzer finds similar games and provides actionable competitive insights.
Instead of abstract percentiles like "You're in the 45th percentile", it shows:
**"Game X is similar to yours but has 3x revenue because they did Y"**

## Example Output

###Test Game: Hades II (App ID: 1145350)

```markdown
## How You Compare to Similar Games

### Games Like Yours (Roguelike, $20-$30, 2024 Launch)

| Game | Score | Reviews | Est. Revenue | What They Did Right |
|------|-------|---------|--------------|---------------------|
| **Hades II** | **89/100** | **15,847 (91%)** | **$12.5M** | Your baseline |
| Dead Cells | 94/100 | 48,293 (94%) | $45.2M | Superior quality/polish |
| Risk of Rain 2 | 92/100 | 89,432 (93%) | $67.8M | Strong marketing/visibility |
| Slay the Spire | 91/100 | 67,234 (94%) | $52.3M | Better execution overall |
| Binding of Isaac: Repentance | 88/100 | 12,456 (87%) | $8.9M | Similar trajectory |
| Cult of the Lamb | 85/100 | 34,892 (89%) | $28.4M | Similar trajectory |
| Rogue Legacy 2 | 78/100 | 8,234 (82%) | $6.2M | Quality issues (low reviews) |
| Neon Abyss | 72/100 | 3,891 (76%) | $2.1M | Poor visibility/marketing |

### Key Learnings from Higher Performers

**What Dead Cells (94/100) did that you haven't**:
- They have 3.6x your revenue ($45.2M vs $12.5M)
- Review score: 94% vs your 91% (+3 points)
- Review volume: 48,293 vs your 15,847 (3.0x more engagement)
- Tags they use that you don't: Metroidvania, Pixel Graphics, Difficult, 2D Platformer
- [View their store page](https://store.steampowered.com/app/588650)

**What Risk of Rain 2 (92/100) did that you haven't**:
- They have 5.4x your revenue ($67.8M vs $12.5M)
- Review score: 93% vs your 91% (+2 points)
- Review volume: 89,432 vs your 15,847 (5.6x more engagement)
- Tags they use that you don't: Third-Person Shooter, Multiplayer, Co-op, 3D
- [View their store page](https://store.steampowered.com/app/632360)

### Warning Signs from Lower Performers

**Neon Abyss (72/100) made these mistakes**:
- Review score only 76% (vs your 91%)
- Limited market traction: 3,891 reviews
- Revenue estimate: $2.1M (you're doing better)
- **How to avoid**: Maintain your review quality and continue engagement efforts

### Success Patterns from Higher Performers

**Specific tactics to copy**:
- Add these high-performing tags: Metroidvania, Pixel Graphics, Multiplayer, Co-op
- Study Dead Cells's store page: https://store.steampowered.com/app/588650
- Increase visibility efforts - competitors have 3.5x more engagement

**Tags to add**: Metroidvania, Pixel Graphics, Multiplayer, Co-op, 2D Platformer

**Pricing insight**: Higher performers average $21.99 (you're at $24.99) - Recommendation: MAINTAIN

### Recovery Success Stories

#### Example Recovery Game

**Before**: 52/100 (1,240 reviews at 64% positive)
**After**: 73/100 (4,890 reviews at 82% positive)
**Timeframe**: 6 months

**What They Changed**:
1. Major content update (2 new game modes)
2. Community feedback implementation (UI overhaul)
3. Influencer partnership campaign (10 mid-tier streamers)
4. Regional pricing optimization (8 new regions)

**Key Takeaway**: Community engagement and content updates drove 400% review growth
**How You Can Apply This**: Prioritize community requests in your roadmap and partner with 5-10 genre-specific influencers
```

## Integration into Reports

### Usage in Report Generation

```python
from src.comparable_games_analyzer import ComparableGamesAnalyzer

# Initialize analyzer
analyzer = ComparableGamesAnalyzer()

# Generate comparison report (integrates with existing report flow)
comparison_report = analyzer.generate_full_comparison_report(
    target_game_id=app_id,
    target_game_data=game_data,
    sales_data=sales_data
)

# Add to main report as Section 5 or similar
full_report += "\n\n" + comparison_report
```

### Key Features

1. **Find Comparable Games** - Strict matching on:
   - Same primary genre
   - Similar price (±$10)
   - Similar launch window (±6 months)
   - Same owner count tier

2. **Generate Comparison Table** - Shows:
   - How target game stacks up against similar games
   - Specific revenue multiples and review differences
   - Links to competitor store pages

3. **Identify Success Patterns** - Analyzes:
   - Tag differences
   - Price positioning
   - Review velocity patterns
   - Actionable tactics to copy

4. **Provide Recovery Examples** - Shows:
   - Games that improved from similar starting points
   - Specific changes they made
   - How to apply lessons

## Matching Criteria Details

### Genre Matching
- Primary genre must match exactly
- Uses Steam's official genre tags
- Example: "Roguelike" matches "Roguelike", not "Rogue-lite"

### Price Matching
- Within ±$10 of target price
- Accounts for regional pricing variations
- Example: $24.99 game matches $15-$35 range

### Launch Window
- Within ±6 months of target launch date
- Ensures market conditions are comparable
- Example: Jan 2024 launch matches Jul 2023 - Jul 2024

### Owner Count Tier
- Same order of magnitude
- Tiers: <1K, 1K-5K, 5K-10K, 10K-50K, 50K-100K, 100K-500K, 500K-1M, 1M+
- Example: 75K owners matches 50K-100K tier

## Testing

To test the analyzer:

```bash
python test_comparable_games.py
```

This will test with:
1. Hades II (1145350) - high-performing game
2. Slay the Spire (646570) - for comparison

## Dependencies

The analyzer uses existing infrastructure:
- `GameSearch` for Steam API and SteamSpy queries
- `GameAnalyzer` for success scoring
- Existing caching and rate limiting

No additional API keys required beyond existing Steam API access.
