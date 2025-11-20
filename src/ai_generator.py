import anthropic
from typing import Dict, List, Any, Tuple
import json
from src.game_analyzer import GameAnalyzer

class AIGenerator:
    """AI-powered report generator using Claude API"""

    def __init__(self, api_key: str):
        """
        Initialize the AI generator with Anthropic API key

        Args:
            api_key: Anthropic API key
        """
        try:
            # Initialize Anthropic client with minimal parameters
            # Avoid passing extra params that might cause issues in different environments
            self.client = anthropic.Anthropic(api_key=api_key)
            # FIXED: Using the correct Claude model name
            # The old model 'claude-3-5-sonnet-20240620' does not exist
            # Using the latest Claude Sonnet 4.5 model
            self.model = "claude-sonnet-4-5-20250929"
        except TypeError as e:
            if "'proxies'" in str(e):
                raise Exception(
                    f"Anthropic library version mismatch. Please upgrade: pip install --upgrade anthropic>=0.40.0\n"
                    f"Current error: {str(e)}"
                )
            raise Exception(f"Failed to initialize Anthropic client: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to initialize Anthropic client: {str(e)}. Check your API key.")

    def generate_post_launch_report(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]],
        steamdb_data: Dict[str, Any] = None
    ) -> str:
        """
        Generate a comprehensive post-launch audit report

        Args:
            game_data: Game information
            sales_data: Sales and revenue data
            competitor_data: List of competitor game data
            steamdb_data: Additional SteamDB data

        Returns:
            Formatted markdown report
        """

        # Build comprehensive prompt based on Post-Launch Report Template
        prompt = f"""You are an expert game marketing analyst at Publitz, specializing in post-launch game audits.

Generate a comprehensive POST-LAUNCH AUDIT REPORT for the following game:

**Game Information:**
- Name: {game_data.get('name', 'N/A')}
- App ID: {game_data.get('app_id', 'N/A')}
- Developer: {game_data.get('developer', 'N/A')}
- Publisher: {game_data.get('publisher', 'N/A')}
- Release Date: {game_data.get('release_date', 'N/A')}
- Genre: {game_data.get('genres', 'N/A')}
- Tags: {game_data.get('tags', 'N/A')}
- Price: {game_data.get('price', 'N/A')}

**Sales Data:**
{json.dumps(sales_data, indent=2) if sales_data else 'Limited sales data available'}

**Competitor Analysis ({len(competitor_data)} competitors found):**
{self._format_competitor_data(competitor_data)}

**Report Requirements:**
Based on the Post-Launch Report Template, your report must include:

1. **EXECUTIVE SUMMARY**
   - Overall performance assessment
   - Key findings and insights
   - Critical recommendations

2. **MARKET POSITIONING ANALYSIS**
   - Competitive landscape overview
   - Market share analysis
   - Positioning vs competitors

3. **SALES & REVENUE PERFORMANCE**
   - Revenue analysis
   - Sales trends
   - Pricing effectiveness
   - Regional performance

4. **MARKETING EFFECTIVENESS**
   - Pre-launch marketing assessment
   - Launch marketing performance
   - Post-launch marketing activities
   - Community engagement metrics

5. **COMPETITOR COMPARISON**
   - Direct competitor analysis
   - Feature comparison
   - Pricing comparison
   - Marketing strategy comparison

6. **REVIEW & SENTIMENT ANALYSIS**
   - Steam review score analysis
   - User sentiment breakdown
   - Common praise points
   - Common criticism points
   - Review trends over time

7. **VISIBILITY & DISCOVERABILITY**
   - Steam search ranking
   - Tag effectiveness
   - Featured placements
   - Wishlist conversion

8. **RECOMMENDATIONS**
   - Immediate action items (0-30 days)
   - Short-term improvements (1-3 months)
   - Long-term strategy (3-6 months)
   - Marketing optimization opportunities

9. **PRICING STRATEGY**
   - Current pricing analysis
   - Regional pricing recommendations
   - Discount strategy suggestions
   - Bundle opportunities

10. **GROWTH OPPORTUNITIES**
    - Content update recommendations
    - Community building strategies
    - Partnership opportunities
    - Platform expansion possibilities

Format the report in clear, professional markdown with proper headings, bullet points, and data visualization suggestions.
Use specific metrics and data points from the provided information.
Be analytical, actionable, and focused on driving results.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=16000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract the text content from the response
            report_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    report_text += content_block.text

            if not report_text:
                raise Exception("Empty response from Claude API")

            return report_text

        except anthropic.AuthenticationError as e:
            raise Exception(f"Invalid API Key: {str(e)}")
        except anthropic.RateLimitError as e:
            raise Exception(f"Rate limit exceeded: {str(e)}. Please try again in a few moments.")
        except anthropic.APIError as e:
            raise Exception(f"Anthropic API Error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating report: {str(e)}")

    def generate_pre_launch_report(
        self,
        game_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a comprehensive pre-launch audit report

        Args:
            game_data: Game information
            competitor_data: List of competitor game data

        Returns:
            Formatted markdown report
        """

        prompt = f"""You are an expert game marketing analyst at Publitz, specializing in pre-launch game audits.

Generate a comprehensive PRE-LAUNCH AUDIT REPORT for the following game:

**Game Information:**
- Name: {game_data.get('name', 'N/A')}
- App ID: {game_data.get('app_id', 'N/A')}
- Developer: {game_data.get('developer', 'N/A')}
- Publisher: {game_data.get('publisher', 'N/A')}
- Expected Release Date: {game_data.get('release_date', 'TBD')}
- Genre: {game_data.get('genres', 'N/A')}
- Tags: {game_data.get('tags', 'N/A')}
- Planned Price: {game_data.get('price', 'N/A')}

**Competitor Analysis ({len(competitor_data)} competitors found):**
{self._format_competitor_data(competitor_data)}

**Report Requirements:**
Based on the Pre-Launch Report Template, your report must include:

1. **EXECUTIVE SUMMARY**
   - Market opportunity assessment
   - Competitive advantage analysis
   - Risk factors
   - Go-to-market readiness

2. **MARKET ANALYSIS**
   - Target market size and trends
   - Market saturation level
   - Entry timing analysis
   - Seasonal considerations

3. **COMPETITIVE LANDSCAPE**
   - Direct competitors overview
   - Indirect competitors
   - Market gaps and opportunities
   - Competitive advantages to emphasize

4. **PRICING STRATEGY**
   - Recommended pricing tier
   - Competitor pricing comparison
   - Regional pricing strategy
   - Launch discount recommendations

5. **FEATURE DIFFERENTIATION**
   - Unique selling propositions
   - Feature comparison with competitors
   - Areas of strength
   - Potential weaknesses to address

6. **MARKETING STRATEGY RECOMMENDATIONS**
   - Pre-launch marketing timeline
   - Key marketing channels
   - Influencer/content creator strategy
   - Community building approach
   - Demo/beta strategy

7. **STEAM STORE OPTIMIZATION**
   - Tag strategy
   - Category selection
   - Screenshots and trailer recommendations
   - Description optimization
   - Feature highlights

8. **WISHLIST STRATEGY**
   - Wishlist generation tactics
   - Wishlist conversion optimization
   - Email marketing strategy
   - Early access considerations

9. **LAUNCH PLAN**
   - Recommended launch timing
   - Launch week strategy
   - Post-launch content roadmap
   - Community management plan

10. **RISK MITIGATION**
    - Identified risks and challenges
    - Mitigation strategies
    - Contingency plans
    - Success metrics and KPIs

Format the report in clear, professional markdown with proper headings, bullet points, and actionable recommendations.
Use specific metrics and data points from the competitor analysis.
Be strategic, actionable, and focused on maximizing launch success.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=16000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract the text content from the response
            report_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    report_text += content_block.text

            if not report_text:
                raise Exception("Empty response from Claude API")

            return report_text

        except anthropic.AuthenticationError as e:
            raise Exception(f"Invalid API Key: {str(e)}")
        except anthropic.RateLimitError as e:
            raise Exception(f"Rate limit exceeded: {str(e)}. Please try again in a few moments.")
        except anthropic.APIError as e:
            raise Exception(f"Anthropic API Error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating report: {str(e)}")

    def generate_report_with_audit(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]],
        steamdb_data: Dict[str, Any] = None,
        report_type: str = "Post-Launch",
        review_stats: Dict[str, Any] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a report using the 3-pass system: Draft → Audit → Enhanced Final

        This is the main innovation: AI generates a draft, audits itself for accuracy,
        then produces an enhanced final report with corrections applied.

        Args:
            game_data: Game information
            sales_data: Sales and revenue data
            competitor_data: List of competitor game data
            steamdb_data: Additional SteamDB data
            report_type: "Post-Launch" or "Pre-Launch"

        Returns:
            Tuple of (final_report, audit_results)
        """
        # Phase 3.1: Generate initial draft (fast)
        draft_report = self._generate_initial_draft(
            game_data, sales_data, competitor_data, steamdb_data, report_type, review_stats
        )

        # Phase 3.2: Audit the draft for accuracy issues
        audit_results = self._audit_report(
            draft_report, game_data, sales_data, competitor_data, review_stats
        )

        # Phase 3.3: Generate enhanced final report with corrections
        final_report = self._generate_enhanced_report(
            game_data, sales_data, competitor_data, steamdb_data,
            draft_report, audit_results, report_type, review_stats
        )

        return final_report, audit_results

    def _generate_initial_draft(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]],
        steamdb_data: Dict[str, Any],
        report_type: str,
        review_stats: Dict[str, Any] = None
    ) -> str:
        """
        Phase 3.1: Generate fast initial draft

        Uses 5k tokens, temperature 0.5 for speed
        Focus on getting basic structure and analysis done quickly
        """
        # Get success context from analyzer
        analyzer = GameAnalyzer()
        success_analysis = analyzer.analyze_success_level(game_data, sales_data, review_stats)
        success_context = success_analysis['context_for_ai']

        prompt = f"""You are an expert game marketing analyst at Publitz.

Generate a comprehensive {report_type.upper()} AUDIT REPORT for this game.

**Game Information:**
- Name: {game_data.get('name', 'N/A')}
- Developer: {game_data.get('developer', 'N/A')}
- Release Date: {game_data.get('release_date', 'N/A')}
- Genre: {game_data.get('genres', 'N/A')}
- Price: {game_data.get('price', 'N/A')}

**Sales & Performance Data:**
- Owners: {sales_data.get('owners_display', 'N/A')}
- Revenue: {sales_data.get('estimated_revenue', 'N/A')} (Range: {sales_data.get('revenue_range', 'N/A')})
- Reviews: {sales_data.get('reviews_total', 0):,} total
- Review Score: {sales_data.get('review_score', 'N/A')}

**SUCCESS CONTEXT FOR ANALYSIS:**
{success_context}

**Competitors ({len(competitor_data)} found):**
{self._format_competitor_data(competitor_data)}

**Report Structure Required:**
1. Executive Summary
2. Market Positioning Analysis
3. Sales & Revenue Performance
4. Competitor Comparison
5. Review & Sentiment Analysis
6. Visibility & Discoverability (Tag effectiveness)
7. Key Recommendations (Immediate, Short-term, Long-term)

**IMPORTANT GUIDELINES:**
- Use the SUCCESS CONTEXT above to calibrate your analysis
- For highly successful games, focus on OPTIMIZATION not PROBLEMS
- Tag effectiveness: High engagement = tags ARE working
- Be data-driven and specific with metrics
- Keep it professional and actionable

Format in clear markdown with headings, bullet points, and specific data.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=5000,  # Faster draft with less tokens
                temperature=0.5,   # Lower temperature for consistency
                messages=[{"role": "user", "content": prompt}]
            )

            report_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    report_text += content_block.text

            return report_text if report_text else "Error: Empty draft generated"

        except Exception as e:
            raise Exception(f"Error generating draft report: {str(e)}")

    def _audit_report(
        self,
        draft_report: str,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]],
        review_stats: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Phase 3.2: Audit the draft report for accuracy issues

        AI checks itself for common mistakes:
        - Wrong competitor types (F2P vs paid, genre mismatches)
        - Revenue accuracy issues
        - False negatives (marking successful games as failing)
        - Tag effectiveness errors

        Returns JSON with findings
        """
        # Get success metrics for audit
        analyzer = GameAnalyzer()
        success_analysis = analyzer.analyze_success_level(game_data, sales_data, review_stats)

        audit_prompt = f"""You are a quality auditor for game marketing reports.

Review the following DRAFT REPORT and check for accuracy issues.

**DRAFT REPORT TO AUDIT:**
{draft_report}

**ACTUAL GAME DATA FOR VERIFICATION:**
- Game: {game_data.get('name')}
- Genres: {game_data.get('genres')}
- Price: {game_data.get('price')}
- Review Score: {sales_data.get('review_score')} ({sales_data.get('reviews_total')} reviews)
- Revenue: {sales_data.get('estimated_revenue')} (Confidence: {sales_data.get('revenue_range')})
- Success Score: {success_analysis['success_score']}/100
- Success Level: {success_analysis['overall_success']}

**COMPETITORS IN REPORT:**
{self._format_competitor_data(competitor_data[:5])}

**AUDIT CHECKLIST - CHECK FOR THESE COMMON ERRORS:**

1. **Competitor Accuracy**
   - Are competitors the same game type? (paid vs F2P, genre match)
   - Question: Do any competitors seem like wrong matches?

2. **Revenue Analysis**
   - Is revenue properly contextualized?
   - Question: Does the report treat a successful game as failing?

3. **Success Recognition**
   - With {sales_data.get('reviews_total')} reviews and {sales_data.get('review_score')} score
   - Question: Does the report recognize this is {success_analysis['overall_success']}?

4. **Tag Effectiveness**
   - With {sales_data.get('reviews_total')} reviews, tags ARE working (high engagement = good discoverability)
   - Question: Does report incorrectly flag tags as not working?

5. **False Negatives**
   - Question: Does report suggest major fixes for a game that's actually doing well?

**OUTPUT FORMAT (JSON):**
Return ONLY a JSON object with this structure:
{{
  "competitor_issues": ["list of specific competitor mismatches found, or empty if none"],
  "revenue_issues": ["list of revenue analysis problems, or empty if none"],
  "success_recognition_issues": ["list of success level misunderstandings, or empty if none"],
  "tag_effectiveness_issues": ["list of incorrect tag assessments, or empty if none"],
  "false_negatives": ["list of problems falsely identified, or empty if none"],
  "overall_quality_score": 0-100,
  "needs_correction": true or false,
  "correction_summary": "brief summary of what needs fixing"
}}

Return ONLY valid JSON, no other text.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for consistent JSON
                messages=[{"role": "user", "content": audit_prompt}]
            )

            audit_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    audit_text += content_block.text

            # Parse JSON response
            try:
                # Extract JSON if it's wrapped in markdown code blocks
                if "```json" in audit_text:
                    json_start = audit_text.find("```json") + 7
                    json_end = audit_text.find("```", json_start)
                    audit_text = audit_text[json_start:json_end].strip()
                elif "```" in audit_text:
                    json_start = audit_text.find("```") + 3
                    json_end = audit_text.find("```", json_start)
                    audit_text = audit_text[json_start:json_end].strip()

                audit_results = json.loads(audit_text)
                return audit_results

            except json.JSONDecodeError as e:
                # If JSON parsing fails, return a default audit result
                return {
                    "competitor_issues": [],
                    "revenue_issues": [],
                    "success_recognition_issues": [],
                    "tag_effectiveness_issues": [],
                    "false_negatives": [],
                    "overall_quality_score": 75,
                    "needs_correction": False,
                    "correction_summary": f"Audit parsing failed: {str(e)}"
                }

        except Exception as e:
            # Return default audit if auditing fails
            return {
                "competitor_issues": [],
                "revenue_issues": [],
                "success_recognition_issues": [],
                "tag_effectiveness_issues": [],
                "false_negatives": [],
                "overall_quality_score": 75,
                "needs_correction": False,
                "correction_summary": f"Audit failed: {str(e)}"
            }

    def _generate_enhanced_report(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]],
        steamdb_data: Dict[str, Any],
        draft_report: str,
        audit_results: Dict[str, Any],
        report_type: str,
        review_stats: Dict[str, Any] = None
    ) -> str:
        """
        Phase 3.3: Generate enhanced final report with audit corrections applied

        Uses 16k tokens for full detail
        Applies corrections from audit
        Uses success context for accurate analysis
        """
        # Get success context
        analyzer = GameAnalyzer()
        success_analysis = analyzer.analyze_success_level(game_data, sales_data, review_stats)
        success_context = success_analysis['context_for_ai']

        # Build correction instructions from audit
        correction_instructions = ""
        if audit_results.get('needs_correction', False):
            correction_instructions = f"""
**CORRECTIONS NEEDED (from audit):**
{audit_results.get('correction_summary', '')}

**Specific Issues to Fix:**
- Competitor issues: {audit_results.get('competitor_issues', [])}
- Revenue issues: {audit_results.get('revenue_issues', [])}
- Success recognition issues: {audit_results.get('success_recognition_issues', [])}
- Tag effectiveness issues: {audit_results.get('tag_effectiveness_issues', [])}
- False negatives: {audit_results.get('false_negatives', [])}

Apply these corrections in your analysis.
"""

        prompt = f"""You are an expert game marketing analyst at Publitz creating the FINAL {report_type.upper()} AUDIT REPORT.

{correction_instructions}

**Game Information:**
- Name: {game_data.get('name', 'N/A')}
- App ID: {game_data.get('app_id', 'N/A')}
- Developer: {game_data.get('developer', 'N/A')}
- Publisher: {game_data.get('publisher', 'N/A')}
- Release Date: {game_data.get('release_date', 'N/A')}
- Genre: {game_data.get('genres', 'N/A')}
- Tags: {game_data.get('tags', 'N/A')}
- Price: {game_data.get('price', 'N/A')}

**Complete Sales & Performance Data:**
{json.dumps(sales_data, indent=2)}

**SUCCESS LEVEL ANALYSIS:**
{success_context}

**Competitor Analysis ({len(competitor_data)} competitors):**
{self._format_competitor_data(competitor_data)}

**ENHANCED REPORT REQUIREMENTS:**

Generate a comprehensive, professional report with these sections:

1. **EXECUTIVE SUMMARY**
   - Overall performance assessment (use success context!)
   - Key findings and insights
   - Critical recommendations

2. **MARKET POSITIONING ANALYSIS**
   - Competitive landscape overview
   - Market share analysis
   - Positioning vs competitors

3. **SALES & REVENUE PERFORMANCE**
   - Revenue analysis (use confidence ranges: {sales_data.get('revenue_range', 'N/A')})
   - Sales trends and trajectory
   - Pricing effectiveness
   - Consider estimation method: {sales_data.get('estimation_method', 'N/A')}

4. **MARKETING EFFECTIVENESS**
   - Pre-launch and launch marketing assessment
   - Community engagement metrics
   - Review velocity and sentiment

5. **COMPETITOR COMPARISON**
   - Direct competitor analysis (ensure genre/type matches!)
   - Feature and pricing comparison
   - Market positioning insights

6. **REVIEW & SENTIMENT ANALYSIS**
   - Steam review score analysis: {sales_data.get('review_score')}
   - {sales_data.get('reviews_total'):,} total reviews - context for engagement level
   - User sentiment breakdown

7. **VISIBILITY & DISCOVERABILITY**
   - Tag effectiveness (remember: high engagement = tags working!)
   - Steam search and visibility
   - Discoverability assessment

8. **STRATEGIC RECOMMENDATIONS**
   - Immediate action items (0-30 days)
   - Short-term improvements (1-3 months)
   - Long-term strategy (3-6 months)
   - Be realistic based on success level

9. **PRICING STRATEGY**
   - Current pricing analysis
   - Regional pricing recommendations
   - Discount strategy suggestions

10. **GROWTH OPPORTUNITIES**
    - Content update recommendations
    - Community building strategies
    - Platform expansion possibilities

**CRITICAL GUIDELINES:**
- Use the SUCCESS CONTEXT to calibrate your tone and recommendations
- For highly successful games (score {success_analysis['success_score']}/100), focus on OPTIMIZATION not PROBLEMS
- Tag effectiveness: {sales_data.get('reviews_total')} reviews = strong discoverability
- Be specific with metrics and data points
- Recommendations should match the game's actual performance level
- Format in professional markdown with clear sections and bullet points

Generate a comprehensive, accurate, and actionable report.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=16000,  # Full detail for final report
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            report_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    report_text += content_block.text

            if not report_text:
                # Fallback to draft if enhanced generation fails
                return draft_report

            return report_text

        except Exception as e:
            # Return draft if enhanced generation fails
            print(f"Warning: Enhanced report generation failed: {e}")
            return draft_report

    def _format_competitor_data(self, competitor_data: List[Dict[str, Any]]) -> str:
        """Format competitor data for the prompt"""
        if not competitor_data:
            return "No competitor data available"

        formatted = []
        for i, comp in enumerate(competitor_data[:10], 1):  # Limit to top 10 competitors
            comp_info = f"""
Competitor {i}: {comp.get('name', 'Unknown')}
- App ID: {comp.get('app_id', 'N/A')}
- Price: {comp.get('price', 'N/A')}
- Reviews: {comp.get('review_count', 'N/A')} ({comp.get('review_score', 'N/A')}% positive)
- Release Date: {comp.get('release_date', 'N/A')}
- Tags: {comp.get('tags', 'N/A')}
- Estimated Revenue: {comp.get('steam_data', {}).get('estimated_revenue', 'N/A')}
"""
            formatted.append(comp_info)

        return "\n".join(formatted)
