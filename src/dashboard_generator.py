"""
Custom Dashboard Generator

Generates custom tracking dashboard templates for Steam game monitoring.
Includes KPI tracking, competitor monitoring, and conversion calculators.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


class DashboardGenerator:
    """Generates custom dashboard templates and tracking tools"""

    def __init__(self):
        """Initialize the dashboard generator"""
        pass

    def generate_dashboard(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate custom dashboard with tracking templates

        Args:
            game_data: Game information
            sales_data: Sales data
            competitor_data: Competitor information

        Returns:
            Dashboard templates and tracking tools
        """
        game_name = game_data.get('name', 'Your Game')

        # Generate KPI tracking template
        kpi_template = self._generate_kpi_tracker(game_name, sales_data)

        # Generate competitor monitoring template
        competitor_template = self._generate_competitor_tracker(competitor_data)

        # Generate conversion calculator
        conversion_calculator = self._generate_conversion_calculator(game_data, sales_data)

        # Generate launch timeline
        launch_timeline = self._generate_launch_timeline()

        # Generate marketing tracker
        marketing_tracker = self._generate_marketing_tracker()

        return {
            'kpi_tracker': kpi_template,
            'competitor_tracker': competitor_template,
            'conversion_calculator': conversion_calculator,
            'launch_timeline': launch_timeline,
            'marketing_tracker': marketing_tracker,
            'instructions': self._generate_instructions()
        }

    def _generate_kpi_tracker(
        self,
        game_name: str,
        sales_data: Dict[str, Any]
    ) -> str:
        """Generate KPI tracking template"""
        template = f"# KPI Tracker: {game_name}\n\n"
        template += "**Instructions:** Copy this table to Google Sheets or Excel. Update daily/weekly.\n\n"

        template += "## Daily Metrics\n\n"
        template += "| Date | Wishlists | Daily +/- | Followers | Reviews | Review Score | Revenue Estimate |\n"
        template += "|------|-----------|-----------|-----------|---------|--------------|------------------|\n"

        # Add 14 days of sample rows
        today = datetime.now()
        for i in range(14):
            date = (today - timedelta(days=13-i)).strftime("%Y-%m-%d")
            template += f"| {date} | 0 | 0 | 0 | 0 | 0% | $0 |\n"

        template += "\n"

        template += "## Weekly Goals\n\n"
        template += "| Week | Wishlist Target | Actual | Follower Target | Actual | Status |\n"
        template += "|------|-----------------|--------|-----------------|--------|--------|\n"
        template += "| Week 1 | 500 | 0 | 100 | 0 | 🔴 |\n"
        template += "| Week 2 | 750 | 0 | 150 | 0 | 🔴 |\n"
        template += "| Week 3 | 1000 | 0 | 200 | 0 | 🔴 |\n"
        template += "| Week 4 | 1500 | 0 | 300 | 0 | 🔴 |\n"

        template += "\n"

        template += "## Key Milestones\n\n"
        template += "| Milestone | Target Date | Actual Date | Status | Notes |\n"
        template += "|-----------|-------------|-------------|--------|-------|\n"
        template += "| Store Page Live | YYYY-MM-DD | | ⏳ | |\n"
        template += "| 1,000 Wishlists | YYYY-MM-DD | | ⏳ | |\n"
        template += "| 5,000 Wishlists | YYYY-MM-DD | | ⏳ | |\n"
        template += "| Launch | YYYY-MM-DD | | ⏳ | |\n"
        template += "| 100 Reviews | YYYY-MM-DD | | ⏳ | |\n"
        template += "| 500 Reviews | YYYY-MM-DD | | ⏳ | |\n"

        template += "\n"

        return template

    def _generate_competitor_tracker(
        self,
        competitor_data: List[Dict[str, Any]]
    ) -> str:
        """Generate competitor monitoring template"""
        template = "# Competitor Monitor\n\n"
        template += "**Instructions:** Track top 5 competitors weekly. Watch for trends.\n\n"

        template += "| Competitor | Current Wishlists | Current Reviews | Review Score | Price | Last Updated |\n"
        template += "|------------|-------------------|-----------------|--------------|-------|---------------|\n"

        # Add top 5 competitors
        for i, comp in enumerate(competitor_data[:5], 1):
            name = comp.get('name', f'Competitor {i}')
            reviews = comp.get('reviews_total', 0)
            score = comp.get('review_score', 0)
            price = comp.get('price', '$0')
            template += f"| {name} | 0 | {reviews} | {score}% | {price} | {datetime.now().strftime('%Y-%m-%d')} |\n"

        template += "\n"

        template += "## Competitor Launch Tracker\n\n"
        template += "| Game Name | Genre | Launch Date | Wishlist at Launch | Day 1 Reviews | Price |\n"
        template += "|-----------|-------|-------------|--------------------|----------------|-------|\n"
        template += "| Example Game 1 | Roguelike | 2024-XX-XX | 15000 | 120 | $19.99 |\n"
        template += "| Example Game 2 | Platformer | 2024-XX-XX | 8000 | 85 | $14.99 |\n"
        template += "| Your Game | TBD | YYYY-MM-DD | ? | ? | $?.?? |\n"

        template += "\n"

        template += "## Competitive Intelligence Notes\n\n"
        template += "| Date | Competitor | Observation | Impact on Us |\n"
        template += "|------|------------|-------------|---------------|\n"
        template += "| YYYY-MM-DD | Competitor Name | Price drop to $X | Consider price positioning |\n"
        template += "| YYYY-MM-DD | Competitor Name | Major update released | Watch review sentiment |\n"

        template += "\n"

        return template

    def _generate_conversion_calculator(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any]
    ) -> str:
        """Generate conversion calculator template"""
        template = "# Conversion Calculator\n\n"
        template += "**Instructions:** Input your actual numbers. Formulas calculate projections.\n\n"

        template += "## Input Your Metrics\n\n"
        template += "| Metric | Your Value | Industry Benchmark |\n"
        template += "|--------|------------|--------------------|\n"
        template += "| Monthly Impressions | 0 | 50,000 |\n"
        template += "| Capsule CTR (%) | 0% | 3.0% |\n"
        template += "| Wishlist Conversion (%) | 0% | 25% |\n"
        template += "| Purchase Conversion (%) | 0% | 15% |\n"
        template += "| Game Price | $0 | $15 |\n"

        template += "\n"

        template += "## Projected Monthly Revenue\n\n"
        template += "| Impressions | Visits | Wishlists | Purchases | Revenue |\n"
        template += "|-------------|--------|-----------|-----------|----------|\n"
        template += "| 10,000 | 300 | 75 | 11 | $165 |\n"
        template += "| 50,000 | 1,500 | 375 | 56 | $840 |\n"
        template += "| 100,000 | 3,000 | 750 | 113 | $1,695 |\n"
        template += "| 250,000 | 7,500 | 1,875 | 281 | $4,215 |\n"
        template += "| 500,000 | 15,000 | 3,750 | 563 | $8,445 |\n"

        template += "\n"
        template += "*Formula: Impressions × CTR = Visits | Visits × Wishlist % = Wishlists | Wishlists × Purchase % = Purchases*\n\n"

        template += "## Scenario Planning\n\n"
        template += "| Scenario | Monthly Impressions | Expected Revenue | Notes |\n"
        template += "|----------|---------------------|------------------|-------|\n"
        template += "| Conservative | 25,000 | $420 | Minimal marketing, organic only |\n"
        template += "| Realistic | 75,000 | $1,260 | Standard indie launch |\n"
        template += "| Optimistic | 200,000 | $3,360 | Strong marketing, influencer coverage |\n"
        template += "| Viral | 500,000+ | $8,400+ | Featured by major influencer or Steam |\n"

        template += "\n"

        return template

    def _generate_launch_timeline(self) -> str:
        """Generate launch timeline template"""
        template = "# Launch Timeline\n\n"
        template += "**Instructions:** Set your launch date and work backwards. Update status weekly.\n\n"

        template += "## Pre-Launch Checklist\n\n"
        template += "| Weeks Before Launch | Task | Owner | Status | Notes |\n"
        template += "|---------------------|------|-------|--------|-------|\n"
        template += "| 12 weeks | Store page live | Team | ⏳ | |\n"
        template += "| 10 weeks | Trailer #1 released | Marketing | ⏳ | |\n"
        template += "| 8 weeks | Press kit ready | Marketing | ⏳ | |\n"
        template += "| 8 weeks | Reach out to creators | Marketing | ⏳ | |\n"
        template += "| 6 weeks | Beta testing begins | QA | ⏳ | 50+ testers |\n"
        template += "| 4 weeks | Submit to Steam festivals | Marketing | ⏳ | |\n"
        template += "| 3 weeks | Trailer #2 released | Marketing | ⏳ | |\n"
        template += "| 2 weeks | Creator embargo lifts | Marketing | ⏳ | |\n"
        template += "| 1 week | Launch countdown | Marketing | ⏳ | Daily social posts |\n"
        template += "| Launch Day | Monitor reviews & bugs | Everyone | ⏳ | All hands on deck |\n"

        template += "\n"

        template += "## Post-Launch Checklist\n\n"
        template += "| Days After Launch | Task | Owner | Status | Notes |\n"
        template += "|-------------------|------|-------|--------|-------|\n"
        template += "| Day 1 | Monitor crash reports | Dev | ⏳ | Hotfix ready |\n"
        template += "| Day 1 | Respond to all reviews | CM | ⏳ | <4h response time |\n"
        template += "| Day 3 | Patch critical bugs | Dev | ⏳ | |\n"
        template += "| Week 1 | Performance analysis | Marketing | ⏳ | Compare to projections |\n"
        template += "| Week 2 | Content Update #1 | Dev | ⏳ | Bug fixes + QoL |\n"
        template += "| Week 4 | Content Update #2 | Dev | ⏳ | New content |\n"
        template += "| Month 2 | Major Update | Dev | ⏳ | Based on feedback |\n"

        template += "\n"

        return template

    def _generate_marketing_tracker(self) -> str:
        """Generate marketing activity tracker"""
        template = "# Marketing Activity Tracker\n\n"
        template += "**Instructions:** Log all marketing activities and measure impact.\n\n"

        template += "## Activity Log\n\n"
        template += "| Date | Channel | Activity | Reach | Wishlists +/- | Notes |\n"
        template += "|------|---------|----------|-------|---------------|-------|\n"
        template += "| YYYY-MM-DD | Reddit | r/indiegaming post | 5K views | +120 | Positive response |\n"
        template += "| YYYY-MM-DD | YouTube | SplatterCat video | 15K views | +380 | High conversion |\n"
        template += "| YYYY-MM-DD | Twitter | Devlog thread | 2K impressions | +25 | |\n"

        template += "\n"

        template += "## Creator Outreach Status\n\n"
        template += "| Creator | Subscribers | Contact Date | Status | Coverage Date | Wishlists Impact |\n"
        template += "|---------|-------------|--------------|--------|---------------|------------------|\n"
        template += "| SplatterCat | 250K | YYYY-MM-DD | ⏳ Pending | TBD | 0 |\n"
        template += "| Wanderbots | 180K | YYYY-MM-DD | ⏳ Pending | TBD | 0 |\n"
        template += "| NorthernLion | 1M | YYYY-MM-DD | ⏳ Pending | TBD | 0 |\n"

        template += "\n"

        template += "## Channel Performance\n\n"
        template += "| Channel | Posts | Total Reach | Wishlists Generated | Cost | ROI |\n"
        template += "|---------|-------|-------------|---------------------|------|-----|\n"
        template += "| Reddit | 0 | 0 | 0 | $0 | N/A |\n"
        template += "| YouTube (Creators) | 0 | 0 | 0 | $0 | N/A |\n"
        template += "| Twitter | 0 | 0 | 0 | $0 | N/A |\n"
        template += "| Discord | 0 | 0 | 0 | $0 | N/A |\n"
        template += "| TikTok | 0 | 0 | 0 | $0 | N/A |\n"

        template += "\n"

        template += "## Budget Tracker\n\n"
        template += "| Expense Category | Budgeted | Actual | Remaining | Notes |\n"
        template += "|------------------|----------|--------|-----------|-------|\n"
        template += "| Creator Payments | $2,000 | $0 | $2,000 | |\n"
        template += "| Paid Ads | $500 | $0 | $500 | |\n"
        template += "| PR/Press | $300 | $0 | $300 | |\n"
        template += "| Tools/Software | $200 | $0 | $200 | |\n"
        template += "| **Total** | **$3,000** | **$0** | **$3,000** | |\n"

        template += "\n"

        return template

    def _generate_instructions(self) -> str:
        """Generate usage instructions"""
        instructions = "# Dashboard Usage Instructions\n\n"

        instructions += "## Setup\n\n"
        instructions += "1. **Copy templates to Google Sheets** - Create separate sheets for each template\n"
        instructions += "2. **Set your launch date** - Use launch timeline to work backwards\n"
        instructions += "3. **Define weekly goals** - Set realistic wishlist/follower targets\n"
        instructions += "4. **Add competitors** - Monitor top 5 direct competitors\n"
        instructions += "5. **Budget allocation** - Assign marketing budget across channels\n\n"

        instructions += "## Daily Tasks (5 minutes)\n\n"
        instructions += "- Update KPI tracker with current wishlists, followers, reviews\n"
        instructions += "- Log any marketing activities in marketing tracker\n"
        instructions += "- Respond to Steam reviews (maintain <24h response time)\n"
        instructions += "- Check for crash reports or critical bugs\n\n"

        instructions += "## Weekly Tasks (30 minutes)\n\n"
        instructions += "- Review progress against weekly goals\n"
        instructions += "- Update competitor tracker (check their stats)\n"
        instructions += "- Analyze channel performance and adjust strategy\n"
        instructions += "- Plan next week's marketing activities\n"
        instructions += "- Update launch timeline checklist\n\n"

        instructions += "## Monthly Tasks (2 hours)\n\n"
        instructions += "- Deep dive into conversion funnel performance\n"
        instructions += "- Competitor analysis (new launches, pricing changes)\n"
        instructions += "- Review budget vs actual spend\n"
        instructions += "- Strategic planning for next month\n"
        instructions += "- Content roadmap adjustment based on data\n\n"

        instructions += "## Key Metrics to Watch\n\n"
        instructions += "- **Wishlist Velocity:** Are wishlists accelerating or plateauing?\n"
        instructions += "- **Review Score:** Maintain 80%+ positive (Very Positive tier)\n"
        instructions += "- **Conversion Rate:** CTR → Wishlist → Purchase rates\n"
        instructions += "- **Channel ROI:** Which marketing channels drive best results?\n"
        instructions += "- **Competitor Gaps:** Where can you differentiate?\n\n"

        instructions += "## Red Flags (Take Immediate Action)\n\n"
        instructions += "- 🚨 Review score drops below 70%\n"
        instructions += "- 🚨 Wishlist velocity drops 50%+ week-over-week\n"
        instructions += "- 🚨 First 10 reviews mention same bug/issue\n"
        instructions += "- 🚨 Competitor launches cheaper, similar game\n"
        instructions += "- 🚨 Major creator coverage has no wishlist impact\n\n"

        return instructions

    def generate_google_sheets_formulas(self) -> str:
        """Generate Google Sheets formula guide"""
        formulas = "# Google Sheets Formula Guide\n\n"

        formulas += "## Conversion Calculator Formulas\n\n"
        formulas += "```\n"
        formulas += "// Cell B2: Monthly Impressions input\n"
        formulas += "// Cell B3: CTR % input\n"
        formulas += "// Cell B4: Wishlist Conversion % input\n"
        formulas += "// Cell B5: Purchase Conversion % input\n"
        formulas += "// Cell B6: Price input\n\n"

        formulas += "// Visits = Impressions × CTR\n"
        formulas += "=B2 * (B3/100)\n\n"

        formulas += "// Wishlists = Visits × Wishlist Conversion\n"
        formulas += "=C7 * (B4/100)\n\n"

        formulas += "// Purchases = Wishlists × Purchase Conversion\n"
        formulas += "=D7 * (B5/100)\n\n"

        formulas += "// Revenue = Purchases × Price\n"
        formulas += "=E7 * B6\n"
        formulas += "```\n\n"

        formulas += "## KPI Tracking Formulas\n\n"
        formulas += "```\n"
        formulas += "// Daily +/- (Column C)\n"
        formulas += "=B2-B1  // Current day wishlists minus previous day\n\n"

        formulas += "// Week-over-week growth %\n"
        formulas += "=(B8-B1)/B1*100  // Current week vs last week\n\n"

        formulas += "// Conditional formatting for status\n"
        formulas += "=IF(C2>B2,\"🟢\",IF(C2>B2*0.8,\"🟡\",\"🔴\"))\n"
        formulas += "// Green if target met, yellow if 80%+, red otherwise\n"
        formulas += "```\n\n"

        formulas += "## Competitor Monitoring Formulas\n\n"
        formulas += "```\n"
        formulas += "// Days since last update\n"
        formulas += "=TODAY()-F2  // Where F2 is \"Last Updated\" date\n\n"

        formulas += "// Alert if competitor not checked in 7+ days\n"
        formulas += "=IF((TODAY()-F2)>7,\"⚠️ UPDATE NEEDED\",\"✓\")\n"
        formulas += "```\n\n"

        return formulas
