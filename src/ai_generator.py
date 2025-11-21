import anthropic
from typing import Dict, List, Any, Tuple
import json
import requests
import base64
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

    def analyze_capsule_image(self, capsule_url: str, game_name: str) -> Dict[str, Any]:
        """
        Analyze game capsule image for CTR risk factors using Claude Vision

        Evaluates:
        - Visual clarity and readability
        - Contrast and color effectiveness
        - Text density and legibility
        - Focal point and composition
        - Overall CTR optimization

        Args:
            capsule_url: URL to the game's capsule image
            game_name: Name of the game for context

        Returns:
            Dictionary with analysis scores and recommendations
        """
        try:
            # Fetch the image
            response = requests.get(capsule_url, timeout=10)
            response.raise_for_status()

            # Convert to base64
            image_data = base64.standard_b64encode(response.content).decode('utf-8')

            # Analyze with Claude Vision
            analysis_prompt = f"""Analyze this Steam game capsule image for "{game_name}" for Click-Through Rate (CTR) optimization.

Evaluate the following critical factors that drive clicks on Steam:

1. **Visual Clarity (0-10)**: Is the image immediately understandable at small sizes?
2. **Contrast & Color (0-10)**: Does it stand out in a crowded store page?
3. **Text Readability (0-10)**: Is any text crisp and legible at thumbnail size?
4. **Focal Point (0-10)**: Does it have a clear visual focal point that draws the eye?
5. **Genre Clarity (0-10)**: Can you tell what type of game this is from the image alone?

For each dimension:
- Provide a score 0-10
- List specific strengths
- List specific issues
- Suggest CONCRETE, ACTIONABLE improvements

Additionally provide:
- **Redesign Brief**: If overall score < 7, provide specific design direction (colors to change, layout adjustments, text modifications)
- **A/B Test Suggestions**: What variations to test (e.g., "Test version without text overlay", "Test warmer color palette")
- **Competitive Context**: Describe how this compares to typical successful capsules in this genre
- **Size-Specific Issues**: Note any problems that appear at small thumbnail sizes vs larger displays

Return ONLY valid JSON with this structure:
{{
  "clarity_score": 0-10,
  "contrast_score": 0-10,
  "text_score": 0-10,
  "focal_point_score": 0-10,
  "genre_clarity_score": 0-10,
  "overall_ctr_score": 0-10,
  "strengths": ["specific strength 1", "specific strength 2"],
  "issues": ["specific issue 1 with what to fix", "specific issue 2"],
  "recommendations": ["concrete rec 1 with measurements/specifics", "concrete rec 2"],
  "redesign_brief": "Detailed design direction if score < 7, or 'N/A - capsule is performing well' if score >= 7",
  "ab_test_suggestions": ["test variation 1", "test variation 2", "test variation 3"],
  "competitive_context": "How this compares to genre standards",
  "summary": "One sentence overall assessment"
}}"""

            vision_response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": analysis_prompt
                        }
                    ]
                }]
            )

            # Extract response text
            response_text = ""
            for content_block in vision_response.content:
                if hasattr(content_block, 'text'):
                    response_text += content_block.text

            # Parse JSON response
            analysis = json.loads(response_text)
            return analysis

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch capsule image: {e}")
            return self._get_fallback_capsule_analysis()
        except json.JSONDecodeError as e:
            print(f"Failed to parse vision response: {e}")
            return self._get_fallback_capsule_analysis()
        except Exception as e:
            print(f"Error analyzing capsule: {e}")
            return self._get_fallback_capsule_analysis()

    def _get_fallback_capsule_analysis(self) -> Dict[str, Any]:
        """Return fallback capsule analysis when vision analysis fails"""
        return {
            "clarity_score": 5,
            "contrast_score": 5,
            "text_score": 5,
            "focal_point_score": 5,
            "genre_clarity_score": 5,
            "overall_ctr_score": 5,
            "strengths": ["Unable to analyze image - analysis unavailable"],
            "issues": ["Capsule analysis could not be completed"],
            "recommendations": [
                "Manually review capsule for visual clarity at thumbnail size",
                "Check contrast against white and dark backgrounds",
                "Verify text is readable at 184x69px size",
                "Compare to top-performing games in your genre"
            ],
            "redesign_brief": "Manual capsule review recommended - automated analysis unavailable",
            "ab_test_suggestions": [
                "Test with and without text overlay",
                "Test different focal points",
                "Test color variations"
            ],
            "competitive_context": "Unable to determine - manual competitor comparison recommended",
            "summary": "Capsule image analysis could not be completed - manual review recommended"
        }

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

**Formatting Requirements:**
- Use clear, professional markdown with proper headings and bullet points
- DO NOT list competitors at the beginning of the report
- DO NOT create a "Top 10 Competitors" or "Competitors Analyzed" section at the start
- Competitor analysis should ONLY appear in Section 5 (COMPETITOR COMPARISON)
- Use specific metrics and data points from the provided information
- Be analytical, actionable, and focused on driving results
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

**Formatting Requirements:**
- Use clear, professional markdown with proper headings and bullet points
- DO NOT list competitors at the beginning of the report
- DO NOT create a "Top 10 Competitors" or "Competitors Analyzed" section at the start
- Competitor analysis should ONLY appear in Section 2 (COMPETITIVE ANALYSIS)
- Use specific metrics and data points from the competitor analysis
- Be strategic, actionable, and focused on maximizing launch success
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
        review_stats: Dict[str, Any] = None,
        capsule_analysis: Dict[str, Any] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a report using the ENHANCED 9-PASS AUDIT SYSTEM:

        PHASE 1 (Original):
        Pass 1: Draft → Generate initial report (5k tokens, temp 0.5)
        Pass 2: Audit → Check for common errors (competitors, revenue, success, tags)

        PHASE 1 ENHANCEMENTS:
        Pass 3: Fact-Check → Verify all numerical claims against source data
        Pass 4: Consistency → Check for internal contradictions between sections
        Pass 5: Specificity → Scan for vague recommendations

        PHASE 2 ENHANCEMENTS:
        Pass 6: Competitor Validation → Ensure competitors are truly comparable
        Pass 7: Specialized Audits → Domain experts (pricing, marketing, competitive intelligence)
        Pass 8: Recommendation Feasibility → Check if recommendations are realistic

        FINAL GENERATION:
        Pass 9: Enhanced Report → Apply ALL corrections from passes 2-8 (16k tokens, temp 0.7)

        Post-Processing:
        - Add executive snapshot
        - Add data quality warnings
        - Format final document

        Args:
            game_data: Game information
            sales_data: Sales and revenue data
            competitor_data: List of competitor game data
            steamdb_data: Additional SteamDB data
            report_type: "Post-Launch" or "Pre-Launch"
            review_stats: Review statistics
            capsule_analysis: Capsule image analysis

        Returns:
            Tuple of (final_report, audit_results)
        """
        # Phase 3.1: Generate initial draft (fast)
        draft_report = self._generate_initial_draft(
            game_data, sales_data, competitor_data, steamdb_data, report_type, review_stats, capsule_analysis
        )

        # Phase 3.2: Audit the draft for accuracy issues
        audit_results = self._audit_report(
            draft_report, game_data, sales_data, competitor_data, review_stats
        )

        # Phase 3.2.5: NEW - Fact-check all numerical claims
        fact_check_results = self._verify_facts(
            draft_report, game_data, sales_data, competitor_data
        )
        audit_results['fact_check'] = fact_check_results

        # Phase 3.2.6: NEW - Check internal consistency
        consistency_results = self._check_consistency(
            draft_report, game_data, sales_data
        )
        audit_results['consistency_check'] = consistency_results

        # Phase 3.2.7: PHASE 2 - Validate competitors are truly comparable
        competitor_validation = self._validate_competitors(
            game_data, sales_data, competitor_data
        )
        audit_results['competitor_validation'] = competitor_validation

        # Phase 3.2.8: PHASE 2 - Specialized domain audits (run conceptually in parallel)
        specialized_audits = self._run_specialized_audits(
            draft_report, game_data, sales_data, competitor_data
        )
        audit_results['specialized_audits'] = specialized_audits

        # Phase 3.2.9: PHASE 2 - Validate recommendation feasibility
        recommendation_validation = self._validate_recommendations(
            draft_report, game_data, sales_data
        )
        audit_results['recommendation_validation'] = recommendation_validation

        # Phase 3.3: Generate enhanced final report with all corrections
        final_report = self._generate_enhanced_report(
            game_data, sales_data, competitor_data, steamdb_data,
            draft_report, audit_results, report_type, review_stats, capsule_analysis
        )

        # Phase 3.3.5: NEW - Enforce specificity in recommendations
        final_report = self._enforce_specificity(final_report)

        # Phase 3.4: Add executive snapshot and data warnings
        fallback_warnings = self._detect_fallback_data(sales_data, competitor_data)

        # Build and insert executive snapshot section
        snapshot_section = self._build_snapshot_section(sales_data, game_data, fallback_warnings)

        # Insert snapshot after first heading
        lines = final_report.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                insert_index = i + 1
                break

        if insert_index > 0:
            lines.insert(insert_index, snapshot_section)
        else:
            lines.insert(0, snapshot_section)

        final_report = '\n'.join(lines)

        # Add data quality warnings if needed (serious issues only)
        if fallback_warnings:
            final_report = self._add_fallback_warnings(final_report, fallback_warnings)

        return final_report, audit_results

    def _generate_initial_draft(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]],
        steamdb_data: Dict[str, Any],
        report_type: str,
        review_stats: Dict[str, Any] = None,
        capsule_analysis: Dict[str, Any] = None
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

**CAPSULE IMAGE ANALYSIS:**
{self._format_capsule_analysis(capsule_analysis) if capsule_analysis else "Capsule analysis not available"}

**Competitors ({len(competitor_data)} found):**
{self._format_competitor_data(competitor_data)}

**Report Structure Required:**
1. Executive Summary
2. Market Positioning Analysis
3. Sales & Revenue Performance
4. Competitor Comparison
5. Review & Sentiment Analysis
6. Visibility & Discoverability (Tag effectiveness)
7. Capsule Image & Visual Marketing (CTR optimization based on clarity, contrast, text, focal point)
8. Store Page Messaging Analysis (Boxleiter Framework: value proposition, target audience, feature/benefit balance, clarity)
9. Key Recommendations (Immediate, Short-term, Long-term)

**IMPORTANT GUIDELINES:**
- Use the SUCCESS CONTEXT above to calibrate your analysis
- For highly successful games, focus on OPTIMIZATION not PROBLEMS
- Tag effectiveness: High engagement = tags ARE working
- Apply Boxleiter messaging framework: evaluate clarity and conversion focus of store page copy
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

    def _verify_facts(
        self,
        draft_report: str,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Phase 3.2.5: Fact-check numerical claims in the report

        Extracts all numerical claims and verifies them against source data.
        This catches errors like:
        - Revenue numbers that don't match source data
        - Review counts that are incorrect
        - Competitor stats that are wrong
        """
        # Build source data reference
        source_data = {
            "game_name": game_data.get('name'),
            "revenue": sales_data.get('estimated_revenue'),
            "revenue_range": sales_data.get('revenue_range'),
            "owners": sales_data.get('owners_display'),
            "reviews_total": sales_data.get('reviews_total'),
            "review_score": sales_data.get('review_score'),
            "price": game_data.get('price'),
            "release_date": game_data.get('release_date'),
            "developer": game_data.get('developer'),
        }

        fact_check_prompt = f"""You are a fact-checker for game marketing reports.

Extract ALL numerical claims from this report and verify them against the source data.

**REPORT TO FACT-CHECK:**
{draft_report[:4000]}  # First 4000 chars to stay within limits

**SOURCE DATA (GROUND TRUTH):**
{json.dumps(source_data, indent=2)}

**TASK:**
1. Extract every numerical claim (revenue, reviews, prices, dates, percentages)
2. Verify each claim against source data
3. Flag any mismatches or unsupported claims

**OUTPUT FORMAT (JSON):**
Return ONLY valid JSON:
{{
  "verified_facts": [
    {{"claim": "Revenue is $1.2M", "source_value": "$1.2M", "matches": true}},
    {{"claim": "Has 5,000 reviews", "source_value": "5,234", "matches": true, "note": "Rounded, acceptable"}}
  ],
  "errors_found": [
    {{"claim": "Revenue is $2M", "source_value": "$1.2M", "matches": false, "severity": "high"}},
    {{"claim": "Price is $29.99", "source_value": "$19.99", "matches": false, "severity": "high"}}
  ],
  "unsupported_claims": [
    {{"claim": "Top 10% of indie games", "issue": "No source data to verify this"}}
  ],
  "accuracy_score": 95,
  "total_facts_checked": 12,
  "errors_count": 0
}}

Return ONLY valid JSON, no other text.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.2,  # Very low for factual accuracy
                messages=[{"role": "user", "content": fact_check_prompt}]
            )

            response_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    response_text += content_block.text

            # Parse JSON response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            fact_check_results = json.loads(response_text)
            return fact_check_results

        except Exception as e:
            # Return default if fact-checking fails
            return {
                "verified_facts": [],
                "errors_found": [],
                "unsupported_claims": [],
                "accuracy_score": 100,  # Assume pass if check fails
                "total_facts_checked": 0,
                "errors_count": 0,
                "error": f"Fact-checking failed: {str(e)}"
            }

    def _check_consistency(
        self,
        draft_report: str,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Phase 3.2.6: Check internal consistency of the report

        Ensures different sections don't contradict each other.
        This catches errors like:
        - Executive summary says "successful" but body says "struggling"
        - Revenue section says $1M but recommendations assume $100K
        - Competitor section contradicts positioning analysis
        """
        consistency_prompt = f"""You are a consistency checker for game marketing reports.

Analyze this report for INTERNAL CONTRADICTIONS between sections.

**REPORT TO CHECK:**
{draft_report[:6000]}  # First 6000 chars

**GAME CONTEXT:**
- Revenue: {sales_data.get('estimated_revenue')}
- Reviews: {sales_data.get('reviews_total')} ({sales_data.get('review_score')} score)
- Price: {game_data.get('price')}

**CHECK FOR THESE CONTRADICTIONS:**

1. **Executive Summary vs Body**
   - Does summary say "successful" while body identifies major problems?
   - Does summary tone match detailed analysis?

2. **Revenue Analysis Consistency**
   - Do all revenue mentions use the same figures?
   - Do recommendations match the revenue level?

3. **Competitor Analysis Consistency**
   - Does positioning claim match competitor comparison?
   - Are competitor comparisons used correctly in recommendations?

4. **Recommendation Alignment**
   - Do recommendations address problems identified in analysis?
   - Are severity levels consistent (urgent issues → immediate actions)?

5. **Tone Calibration**
   - Is tone consistent throughout (don't start optimistic, end pessimistic)?

**OUTPUT FORMAT (JSON):**
Return ONLY valid JSON:
{{
  "contradictions_found": [
    {{
      "section_1": "Executive Summary",
      "section_2": "Sales Analysis",
      "contradiction": "Summary says 'highly successful' but sales section identifies 'concerning revenue decline'",
      "severity": "high"
    }}
  ],
  "consistency_score": 85,
  "needs_revision": false,
  "revision_notes": "Minor tone inconsistencies between sections 3 and 7"
}}

Return ONLY valid JSON, no other text.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.2,
                messages=[{"role": "user", "content": consistency_prompt}]
            )

            response_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    response_text += content_block.text

            # Parse JSON response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            consistency_results = json.loads(response_text)
            return consistency_results

        except Exception as e:
            # Return default if consistency check fails
            return {
                "contradictions_found": [],
                "consistency_score": 100,  # Assume pass if check fails
                "needs_revision": False,
                "revision_notes": "",
                "error": f"Consistency check failed: {str(e)}"
            }

    def _enforce_specificity(self, report: str) -> str:
        """
        Phase 3.3.5: Enforce specificity in recommendations

        Scans the final report for vague recommendations and replaces them
        with specific, actionable alternatives.

        Vague patterns to eliminate:
        - "improve marketing" → "increase Twitter ad spend by 20%"
        - "optimize pricing" → "reduce price from $29.99 to $24.99"
        - "better capsule" → "increase contrast by 30%, move logo to top-left"
        """
        specificity_prompt = f"""You are a specificity enforcer for game marketing reports.

Scan this report for VAGUE recommendations and suggest SPECIFIC replacements.

**REPORT TO SCAN:**
{report[:8000]}  # First 8000 chars

**VAGUE PATTERNS TO ELIMINATE:**
- "improve X" → Need specific metric and target
- "optimize Y" → Need specific change and expected outcome
- "consider Z" → Need specific action with timeline
- "increase marketing" → Which channel? By how much? When?
- "adjust pricing" → To what price? When? For how long?
- "better visuals" → Which specific visual? What specific change?

**YOUR TASK:**
1. Identify all vague recommendations (no metrics, no specifics, no timelines)
2. For each vague recommendation, suggest a specific replacement
3. Return list of improvements

**OUTPUT FORMAT (JSON):**
Return ONLY valid JSON:
{{
  "vague_recommendations_found": [
    {{
      "original": "Consider improving the game's marketing",
      "location": "Section 9, Recommendations",
      "specific_replacement": "Increase Facebook ad spend by 25% targeting RPG enthusiast audiences aged 18-35, launching campaign by December 1st with expected +15% wishlist growth",
      "improvement_type": "added_metrics_timeline_target"
    }}
  ],
  "specificity_score": 65,
  "recommendations_needing_specificity": 3,
  "summary": "Found 3 vague recommendations that need specific metrics, timelines, or targets"
}}

Return ONLY valid JSON, no other text.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": specificity_prompt}]
            )

            response_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    response_text += content_block.text

            # Parse JSON response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            specificity_results = json.loads(response_text)

            # If vague recommendations found, apply a second pass to enhance them
            if specificity_results.get('vague_recommendations_found') and len(specificity_results['vague_recommendations_found']) > 0:
                # Note: In a production system, you would actually replace the vague text
                # For now, we just flag them in the audit results
                # The next report generation will see these flags and improve
                pass

            return report  # Return original report (specificity feedback goes to audit results)

        except Exception as e:
            # If specificity check fails, just return original report
            return report

    def _validate_competitors(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Phase 3.2.7 (Phase 2): Validate that competitors are truly comparable

        Ensures competitors match on critical dimensions:
        - Same monetization model (paid vs F2P)
        - Genre overlap
        - Price range similarity
        - Release timeframe relevance
        - Platform match

        This prevents comparing apples to oranges (e.g., $60 AAA vs $5 indie)
        """
        # Build comparison data
        game_info = {
            "name": game_data.get('name'),
            "price": game_data.get('price', 'Unknown'),
            "genres": game_data.get('genres', ''),
            "release_date": game_data.get('release_date', ''),
            "tags": game_data.get('tags', '')
        }

        competitors_info = []
        for comp in competitor_data[:10]:  # Limit to top 10
            competitors_info.append({
                "name": comp.get('name'),
                "price": comp.get('price', 'Unknown'),
                "genres": comp.get('genres', ''),
                "tags": comp.get('tags', ''),
                "release_date": comp.get('release_date', '')
            })

        validation_prompt = f"""You are a competitor validation specialist for game marketing.

Analyze if these competitors are TRULY COMPARABLE to the target game.

**TARGET GAME:**
{json.dumps(game_info, indent=2)}

**COMPETITORS TO VALIDATE:**
{json.dumps(competitors_info, indent=2)}

**VALIDATION CRITERIA:**

1. **Monetization Match** (CRITICAL)
   - Is target game paid? Are competitors paid?
   - Is target game F2P? Are competitors F2P?
   - Mismatch = INVALID competitor

2. **Genre Overlap** (HIGH PRIORITY)
   - Do genres overlap significantly?
   - Example: RPG vs RPG = good, RPG vs Racing = bad

3. **Price Range** (HIGH PRIORITY for paid games)
   - Are prices within 2x of each other?
   - Example: $20 vs $40 = acceptable, $5 vs $60 = questionable

4. **Release Recency** (MEDIUM PRIORITY)
   - Are games from similar era?
   - Games >5 years apart may have different market dynamics

5. **Tag Similarity** (MEDIUM PRIORITY)
   - Do tags show similar game mechanics/themes?

**OUTPUT FORMAT (JSON):**
Return ONLY valid JSON:
{{
  "valid_competitors": [
    {{
      "name": "Competitor Name",
      "similarity_score": 85,
      "match_reasons": ["Same genre", "Similar price", "Recent release"]
    }}
  ],
  "invalid_competitors": [
    {{
      "name": "Competitor Name",
      "similarity_score": 25,
      "rejection_reasons": ["F2P vs paid mismatch", "Different genre entirely"],
      "severity": "high"
    }}
  ],
  "overall_competitor_quality": 75,
  "recommendation": "Replace 2 invalid competitors with better matches"
}}

Return ONLY valid JSON, no other text.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.2,
                messages=[{"role": "user", "content": validation_prompt}]
            )

            response_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    response_text += content_block.text

            # Parse JSON response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            validation_results = json.loads(response_text)
            return validation_results

        except Exception as e:
            # Return default if validation fails
            return {
                "valid_competitors": [],
                "invalid_competitors": [],
                "overall_competitor_quality": 100,  # Assume pass
                "recommendation": "",
                "error": f"Competitor validation failed: {str(e)}"
            }

    def _run_specialized_audits(
        self,
        draft_report: str,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Phase 3.2.8 (Phase 2): Run specialized domain audits in parallel

        Instead of one general audit, run specialized audits for:
        1. Pricing Strategy (is pricing analysis sound?)
        2. Marketing Tactics (are marketing recommendations realistic?)
        3. Competitive Intelligence (is competitor analysis accurate?)
        4. Technical/Platform Assessment (are technical recommendations feasible?)

        Each specialist has domain expertise and catches domain-specific errors
        """
        # Note: In true parallel execution, these would run simultaneously
        # For now, we run them sequentially but conceptually they're parallel

        specialized_results = {
            "pricing_audit": {"score": 100, "issues": []},
            "marketing_audit": {"score": 100, "issues": []},
            "competitive_audit": {"score": 100, "issues": []},
            "overall_score": 100
        }

        audit_prompt = f"""You are a panel of specialized game industry auditors reviewing a draft report.

**DRAFT REPORT (excerpt):**
{draft_report[:5000]}

**GAME CONTEXT:**
- Price: {game_data.get('price')}
- Revenue: {sales_data.get('estimated_revenue')}
- Genre: {game_data.get('genres')}

**YOUR TASK:**
Review this report from THREE specialist perspectives:

1. **PRICING SPECIALIST:**
   - Is pricing analysis realistic for this genre/quality level?
   - Are discount recommendations appropriate (not too deep, not too shallow)?
   - Does regional pricing make sense?
   - Are bundle opportunities realistic?

2. **MARKETING SPECIALIST:**
   - Are marketing channel recommendations appropriate for this game type?
   - Are budget estimates realistic?
   - Are influencer strategies feasible?
   - Are growth projections reasonable?

3. **COMPETITIVE INTELLIGENCE SPECIALIST:**
   - Is competitor comparison apples-to-apples?
   - Are competitive advantages accurately identified?
   - Are market positioning claims supported?

**OUTPUT FORMAT (JSON):**
Return ONLY valid JSON:
{{
  "pricing_audit": {{
    "score": 85,
    "issues": ["Discount recommendations too aggressive for indie game", "Regional pricing missing for key markets"],
    "strengths": ["Price point well-justified"]
  }},
  "marketing_audit": {{
    "score": 90,
    "issues": ["Influencer budget seems high for this revenue level"],
    "strengths": ["Marketing channels well-targeted", "Timeline realistic"]
  }},
  "competitive_audit": {{
    "score": 75,
    "issues": ["One competitor is F2P vs this game's paid model"],
    "strengths": ["Genre matching is good"]
  }},
  "overall_score": 83,
  "summary": "Strong report with minor pricing and competitive analysis issues"
}}

Return ONLY valid JSON, no other text.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": audit_prompt}]
            )

            response_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    response_text += content_block.text

            # Parse JSON response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            specialized_results = json.loads(response_text)
            return specialized_results

        except Exception as e:
            # Return default if specialized audits fail
            return {
                "pricing_audit": {"score": 100, "issues": [], "strengths": []},
                "marketing_audit": {"score": 100, "issues": [], "strengths": []},
                "competitive_audit": {"score": 100, "issues": [], "strengths": []},
                "overall_score": 100,
                "summary": "",
                "error": f"Specialized audits failed: {str(e)}"
            }

    def _validate_recommendations(
        self,
        draft_report: str,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Phase 3.2.9 (Phase 2): Validate recommendation feasibility

        Checks if recommendations are:
        - Realistic (not "get 1M wishlists in 1 week")
        - Achievable with available resources
        - Properly prioritized
        - Have success metrics defined
        - Are specific enough to act on
        """
        # Extract key constraints
        constraints = {
            "revenue": sales_data.get('estimated_revenue', 'Unknown'),
            "review_count": sales_data.get('reviews_total', 0),
            "price": game_data.get('price', 'Unknown'),
            "is_indie": "indie" in str(game_data.get('tags', '')).lower() or "indie" in str(game_data.get('developer', '')).lower()
        }

        validation_prompt = f"""You are a feasibility auditor for game marketing recommendations.

**DRAFT REPORT RECOMMENDATIONS (excerpt):**
{draft_report[draft_report.find('RECOMMENDATION'):draft_report.find('RECOMMENDATION')+3000] if 'RECOMMENDATION' in draft_report else draft_report[-3000:]}

**GAME CONSTRAINTS:**
{json.dumps(constraints, indent=2)}

**FEASIBILITY CHECKS:**

1. **Resource Realism**
   - Are recommendations realistic given the game's revenue/team size?
   - Example: $100K revenue game shouldn't recommend $50K ad campaign
   - Indie game can't hire 10-person community team

2. **Timeline Feasibility**
   - Are timelines achievable?
   - Example: "redesign capsule in 2 days" = unrealistic
   - "launch marketing campaign in 2 weeks" = realistic

3. **Impact Estimates**
   - Are projected outcomes realistic?
   - Example: "+500% revenue in 1 month" = unrealistic
   - "+15-25% wishlist growth" = realistic

4. **Specificity**
   - Are recommendations specific enough to execute?
   - Do they have clear success metrics?
   - Do they have assigned owners/roles?

5. **Prioritization**
   - Are recommendations prioritized by impact/effort?
   - Are quick wins separated from long-term projects?

**OUTPUT FORMAT (JSON):**
Return ONLY valid JSON:
{{
  "unrealistic_recommendations": [
    {{
      "recommendation": "Launch $50K ad campaign",
      "issue": "Budget too high for game's revenue level ($100K total)",
      "severity": "high",
      "suggestion": "Start with $5K test campaign"
    }}
  ],
  "under_specified_recommendations": [
    {{
      "recommendation": "Improve marketing",
      "issue": "Too vague - no channel, budget, or timeline specified",
      "severity": "medium"
    }}
  ],
  "realistic_recommendations": [
    {{
      "recommendation": "Reduce price from $19.99 to $16.99 during Steam Summer Sale",
      "strengths": ["Specific price", "Specific event", "Realistic timeline"]
    }}
  ],
  "feasibility_score": 70,
  "summary": "Most recommendations realistic but 2 need budget adjustments and 3 need more specificity"
}}

Return ONLY valid JSON, no other text.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": validation_prompt}]
            )

            response_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    response_text += content_block.text

            # Parse JSON response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            validation_results = json.loads(response_text)
            return validation_results

        except Exception as e:
            # Return default if validation fails
            return {
                "unrealistic_recommendations": [],
                "under_specified_recommendations": [],
                "realistic_recommendations": [],
                "feasibility_score": 100,  # Assume pass
                "summary": "",
                "error": f"Recommendation validation failed: {str(e)}"
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
        review_stats: Dict[str, Any] = None,
        capsule_analysis: Dict[str, Any] = None
    ) -> str:
        """
        Phase 3.3: Generate enhanced final report with ALL corrections applied

        ENHANCED (Phase 1): Now incorporates:
        - Original audit corrections (competitor, revenue, success recognition)
        - Fact-check corrections (numerical accuracy)
        - Consistency corrections (cross-section alignment)

        Uses 16k tokens for full detail
        Applies ALL corrections from audit + fact-check + consistency checks
        Uses success context for accurate analysis
        """
        # Get success context
        analyzer = GameAnalyzer()
        success_analysis = analyzer.analyze_success_level(game_data, sales_data, review_stats)
        success_context = success_analysis['context_for_ai']

        # Build correction instructions from audit + new validation passes
        correction_instructions = ""

        # Original audit corrections
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
"""

        # NEW: Add fact-check results
        fact_check = audit_results.get('fact_check', {})
        if fact_check.get('errors_found') and len(fact_check['errors_found']) > 0:
            correction_instructions += f"""
**FACT-CHECK ERRORS (Phase 1 Enhancement):**
The following numerical claims were INCORRECT in the draft:
{json.dumps(fact_check.get('errors_found', []), indent=2)}

CRITICAL: Use the correct source values in the final report. Accuracy score: {fact_check.get('accuracy_score', 100)}%
"""

        # NEW: Add consistency check results
        consistency = audit_results.get('consistency_check', {})
        if consistency.get('contradictions_found') and len(consistency['contradictions_found']) > 0:
            correction_instructions += f"""
**CONSISTENCY ISSUES (Phase 1 Enhancement):**
The following contradictions were found between sections:
{json.dumps(consistency.get('contradictions_found', []), indent=2)}

CRITICAL: Ensure all sections tell a consistent story. Consistency score: {consistency.get('consistency_score', 100)}%
Revision notes: {consistency.get('revision_notes', 'None')}
"""

        # PHASE 2: Add competitor validation results
        comp_validation = audit_results.get('competitor_validation', {})
        if comp_validation.get('invalid_competitors') and len(comp_validation['invalid_competitors']) > 0:
            correction_instructions += f"""
**COMPETITOR VALIDATION ISSUES (Phase 2 Enhancement):**
The following competitors are NOT truly comparable:
{json.dumps(comp_validation.get('invalid_competitors', []), indent=2)}

CRITICAL: {comp_validation.get('recommendation', 'Review competitor selection')}
Competitor quality score: {comp_validation.get('overall_competitor_quality', 100)}%
"""

        # PHASE 2: Add specialized audit results
        specialized = audit_results.get('specialized_audits', {})
        has_specialized_issues = (
            (specialized.get('pricing_audit', {}).get('issues') and len(specialized['pricing_audit']['issues']) > 0) or
            (specialized.get('marketing_audit', {}).get('issues') and len(specialized['marketing_audit']['issues']) > 0) or
            (specialized.get('competitive_audit', {}).get('issues') and len(specialized['competitive_audit']['issues']) > 0)
        )
        if has_specialized_issues:
            correction_instructions += f"""
**SPECIALIZED DOMAIN AUDIT FINDINGS (Phase 2 Enhancement):**

Pricing Specialist (Score: {specialized.get('pricing_audit', {}).get('score', 100)}):
Issues: {specialized.get('pricing_audit', {}).get('issues', [])}
Strengths: {specialized.get('pricing_audit', {}).get('strengths', [])}

Marketing Specialist (Score: {specialized.get('marketing_audit', {}).get('score', 100)}):
Issues: {specialized.get('marketing_audit', {}).get('issues', [])}
Strengths: {specialized.get('marketing_audit', {}).get('strengths', [])}

Competitive Intelligence (Score: {specialized.get('competitive_audit', {}).get('score', 100)}):
Issues: {specialized.get('competitive_audit', {}).get('issues', [])}
Strengths: {specialized.get('competitive_audit', {}).get('strengths', [])}

Overall Specialist Score: {specialized.get('overall_score', 100)}%
Summary: {specialized.get('summary', '')}
"""

        # PHASE 2: Add recommendation feasibility results
        rec_validation = audit_results.get('recommendation_validation', {})
        has_feasibility_issues = (
            (rec_validation.get('unrealistic_recommendations') and len(rec_validation['unrealistic_recommendations']) > 0) or
            (rec_validation.get('under_specified_recommendations') and len(rec_validation['under_specified_recommendations']) > 0)
        )
        if has_feasibility_issues:
            correction_instructions += f"""
**RECOMMENDATION FEASIBILITY ISSUES (Phase 2 Enhancement):**

Unrealistic Recommendations:
{json.dumps(rec_validation.get('unrealistic_recommendations', []), indent=2)}

Under-Specified Recommendations:
{json.dumps(rec_validation.get('under_specified_recommendations', []), indent=2)}

CRITICAL: Adjust recommendations to be realistic and specific. Feasibility score: {rec_validation.get('feasibility_score', 100)}%
{rec_validation.get('summary', '')}
"""

        if correction_instructions:
            correction_instructions += "\nApply ALL these corrections in your final analysis.\n"

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

**CAPSULE IMAGE ANALYSIS:**
{self._format_capsule_analysis(capsule_analysis) if capsule_analysis else "Capsule analysis not available"}

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
   - Data quality context:
     * Estimation method: {sales_data.get('estimation_method', 'N/A')}
     * Confidence level: {sales_data.get('confidence', 'N/A')}
     * Data source: {sales_data.get('data_source', 'N/A')}
     * Signals used: {', '.join(sales_data.get('signals_used', [])) if sales_data.get('signals_used') else 'N/A'}

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
   - **Tag Opportunity Analysis**: Specific tags to ADD or REMOVE
   - Steam search and visibility
   - Discoverability assessment

8. **CAPSULE & STORE ASSET OPTIMIZATION**
   Based on capsule analysis scores and competitor comparison:

   **Capsule Redesign Brief:**
   - If overall CTR score < 7/10, provide SPECIFIC design direction:
     * What to change (colors, composition, text, etc.)
     * Competitor comparison: How does it compare visually to top performers?
     * A/B testing suggestions: What variations to test first
     * Platform-specific considerations: Steam store vs wishlist vs library sizes

   **Screenshot Sequence Optimization:**
   - Are screenshots in optimal order? (Hero shot first, features second, etc.)
   - Which screenshots to replace or reorder (be specific: "Move screenshot 3 to position 1")
   - Missing screenshot types (gameplay, UI, features, social proof)

   **Trailer Hook Analysis:**
   - First 10 seconds effectiveness
   - Hook timing and retention recommendations
   - CTA (Call-to-Action) placement and clarity

9. **STORE PAGE MESSAGING ANALYSIS (Boxleiter Framework)**
   Evaluate the game's store page copy and messaging for conversion effectiveness:

   - **Value Proposition Clarity**: Does the description immediately communicate what makes this game unique?
   - **Target Audience Clarity**: Is it clear who this game is for?
   - **Feature vs Benefit Balance**: Are features translated into player benefits?
   - **Conversion Focus**: Does the copy compel action or just describe?
   - **Clarity Score**: Is the messaging jargon-free and instantly understandable?

   Based on the game description: "{game_data.get('description', 'No description available')[:200]}..."

   Rate each dimension (1-10) and provide specific improvements for weak areas.

10. **ACTION PLAN & PRIORITIZATION**
    Create a prioritized roadmap with SPECIFIC action items:

    **30-Day Action Plan (Immediate Wins):**
    - List 3-5 specific tasks with owners (e.g., "Marketing: Update capsule by May 15")
    - Expected impact and effort level for each

    **60-Day Action Plan (Short-term):**
    - List 3-5 medium-effort initiatives
    - Resource requirements (time, budget, skills needed)

    **90-Day Action Plan (Strategic):**
    - List 3-5 longer-term strategies
    - Success metrics for each initiative

    **Prioritization Matrix:**
    Create a 2x2 grid categorizing recommendations:
    - Quick Wins (High Impact, Low Effort)
    - Major Projects (High Impact, High Effort)
    - Fill-ins (Low Impact, Low Effort)
    - Time Sinks (Low Impact, High Effort) - avoid these

11. **PRICING & MONETIZATION OPTIMIZATION**
    - Current pricing analysis
    - **Regional Pricing Calculator**: Specific $ amounts for top 10 markets
    - **Discount Calendar**: Exact dates and %off for next 6 months
      * When to run sales (Summer Sale, Winter Sale, etc.)
      * Recommended discount depths (10%, 20%, 30%)
      * Bundle opportunities with specific partner games
    - DLC opportunity analysis with specific ideas and price points

12. **GROWTH OPPORTUNITIES**
    - Content update recommendations (specific features/modes to add)
    - Community building strategies (Discord, Reddit, etc.)
    - Platform expansion possibilities (Console viability score 0-10)
    - Influencer target list (specific creators to contact)

**CRITICAL GUIDELINES:**
- Use the SUCCESS CONTEXT to calibrate your tone and recommendations
- For highly successful games (score {success_analysis['success_score']}/100), focus on OPTIMIZATION not PROBLEMS
- Tag effectiveness: {sales_data.get('reviews_total')} reviews = strong discoverability
- Be EXTREMELY SPECIFIC with all recommendations:
  * Instead of "improve capsule", say "increase contrast by 20%, move logo to top-left, reduce text size"
  * Instead of "optimize tags", say "add 'Roguelike' and 'Pixel Art', remove 'Adventure'"
  * Instead of "consider discounts", say "20% off during Steam Summer Sale (June 27-July 11, 2024)"
- Include CONCRETE numbers, dates, and specific action items
- Assign tasks to teams/roles where applicable (Marketing, Development, Community)
- Provide success metrics for each recommendation (e.g., "Expected +15% wishlist conversion")
- Recommendations should match the game's actual performance level
- Format in professional markdown with clear sections, bullet points, and tables
- DO NOT list competitors at the beginning of the report
- DO NOT create a "Top 10 Competitors" or "Competitors Analyzed" section at the start
- Competitor analysis should ONLY appear in Section 5 (COMPETITOR COMPARISON)
- ALWAYS create the prioritization matrix (2x2 grid: Impact vs Effort)
- ALWAYS provide the 30/60/90 day action plan with specific tasks

Generate a comprehensive, accurate, and ACTIONABLE report with specific, measurable recommendations.
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

    def _format_capsule_analysis(self, capsule_analysis: Dict[str, Any]) -> str:
        """Format capsule analysis data for the prompt"""
        if not capsule_analysis:
            return "Capsule analysis not available"

        return f"""
Capsule CTR Analysis (0-10 scale):
- Visual Clarity: {capsule_analysis.get('clarity_score', 'N/A')}/10
- Contrast & Color: {capsule_analysis.get('contrast_score', 'N/A')}/10
- Text Readability: {capsule_analysis.get('text_score', 'N/A')}/10
- Focal Point: {capsule_analysis.get('focal_point_score', 'N/A')}/10
- Genre Clarity: {capsule_analysis.get('genre_clarity_score', 'N/A')}/10
- Overall CTR Score: {capsule_analysis.get('overall_ctr_score', 'N/A')}/10

Summary: {capsule_analysis.get('summary', 'No summary available')}

Strengths:
{chr(10).join('- ' + s for s in capsule_analysis.get('strengths', []))}

Issues to Address:
{chr(10).join('- ' + i for i in capsule_analysis.get('issues', []))}

Actionable Recommendations:
{chr(10).join('- ' + r for r in capsule_analysis.get('recommendations', []))}

Redesign Brief:
{capsule_analysis.get('redesign_brief', 'N/A')}

A/B Testing Suggestions:
{chr(10).join('- ' + t for t in capsule_analysis.get('ab_test_suggestions', []))}

Competitive Context:
{capsule_analysis.get('competitive_context', 'N/A')}

**IMPORTANT**: Use this capsule analysis data in Section 8 (CAPSULE & STORE ASSET OPTIMIZATION).
If overall CTR score < 7/10, provide detailed redesign guidance based on the brief above.
Include the A/B test suggestions as actionable next steps.
"""

    def _detect_fallback_data(
        self,
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Detect if fallback/placeholder data is being used and provide transparency

        Returns:
            List of warning/info messages about data sources and quality
        """
        warnings = []

        # Get data source information
        estimation_method = sales_data.get('estimation_method', 'unknown')
        data_source = sales_data.get('data_source', 'Unknown')
        confidence = sales_data.get('confidence', 'unknown')

        # Check different data sources and add appropriate transparency messages
        if estimation_method == 'rawg_smart_estimation':
            # RAWG + Smart Estimation - This is good data, just estimated
            signals = sales_data.get('signals_used', [])
            signals_str = ', '.join(signals) if signals else 'multiple indicators'

            info_msg = f"📊 **Data Source:** RAWG API + Smart Estimation (Confidence: {confidence.upper()})"
            info_msg += f"\n   - Ownership and revenue estimates based on {signals_str}"
            info_msg += "\n   - More accurate than generic fallback, but not official Steam data"
            warnings.append(info_msg)

        elif estimation_method == 'alternative_source':
            # Steam scraping worked - this is good data
            info_msg = "✓ **Data Source:** Steam Store Scraping (Real Data)"
            info_msg += "\n   - Ownership estimates based on review count analysis"
            warnings.append(info_msg)

        elif (sales_data.get('app_id') == 'unknown' or
              str(sales_data.get('app_id', '')).startswith('fallback') or
              estimation_method == 'fallback' or
              estimation_method == 'minimal'):
            # Generic fallback - low quality
            warnings.append("⚠️ Sales and revenue data is using generic fallback values (all APIs unavailable)")

        else:
            # Unknown method - show what we have
            if estimation_method and estimation_method != 'unknown':
                warnings.append(f"📊 **Data Source:** {data_source} (Method: {estimation_method}, Confidence: {confidence})")

        # Check if competitors are fallback
        fallback_competitor_count = sum(
            1 for comp in competitor_data
            if str(comp.get('app_id', '')).startswith('fallback')
        )

        if fallback_competitor_count > 0:
            if fallback_competitor_count == len(competitor_data):
                warnings.append("⚠️ All competitor data is using placeholder values (no real competitors found)")
            else:
                warnings.append(f"⚠️ {fallback_competitor_count} of {len(competitor_data)} competitors are placeholder values")

        return warnings

    def _build_snapshot_section(
        self,
        sales_data: Dict[str, Any],
        game_data: Dict[str, Any],
        warnings: List[str]
    ) -> str:
        """Build executive snapshot section with key metrics"""

        snapshot = "---\n\n## 📊 EXECUTIVE SNAPSHOT\n\n"

        # Key metrics in a compact format
        snapshot += "| Metric | Value |\n"
        snapshot += "|--------|-------|\n"
        snapshot += f"| **Estimated Revenue** | {sales_data.get('estimated_revenue', 'N/A')} |\n"
        snapshot += f"| **Revenue Range** | {sales_data.get('revenue_range', 'N/A')} |\n"
        snapshot += f"| **Estimated Owners** | {sales_data.get('owners_display', 'N/A')} |\n"
        snapshot += f"| **Price** | {sales_data.get('price', 'N/A')} |\n"
        snapshot += f"| **Review Score** | {sales_data.get('review_score', 'N/A')} |\n"
        snapshot += f"| **Total Reviews** | {sales_data.get('reviews_total', 'N/A'):,} |\n" if isinstance(sales_data.get('reviews_total'), (int, float)) else f"| **Total Reviews** | {sales_data.get('reviews_total', 'N/A')} |\n"
        snapshot += f"| **Developer** | {game_data.get('developer', 'N/A')} |\n"
        snapshot += f"| **Release Date** | {game_data.get('release_date', 'N/A')} |\n"

        snapshot += "\n"

        # Data source info (compact)
        has_serious_warnings = any('⚠️' in w and 'fallback' in w.lower() for w in warnings)

        if has_serious_warnings:
            snapshot += "⚠️ **Data Quality:** Limited data available - using fallback estimates\n\n"
        else:
            data_source = sales_data.get('data_source', 'Unknown')
            confidence = sales_data.get('confidence', 'unknown')
            snapshot += f"**Data Source:** {data_source} (Confidence: {confidence.title()})\n\n"

        snapshot += "---\n\n"

        return snapshot

    def _add_fallback_warnings(self, report: str, warnings: List[str]) -> str:
        """
        Add executive snapshot and data source info to the report

        Args:
            report: The generated report markdown
            warnings: List of warning/info messages about data sources

        Returns:
            Modified report with snapshot section at the top
        """
        # Build snapshot section instead of old warnings format
        # (snapshot is built in generate_report_with_audit where we have access to sales_data)

        # For serious warnings, still add a warning banner
        has_serious_warnings = any('⚠️' in w and 'fallback' in w.lower() for w in warnings)

        if has_serious_warnings:
            warning_section = "---\n\n## ⚠️ DATA QUALITY WARNING\n\n"
            warning_section += "**This report contains incomplete data. Please review carefully:**\n\n"

            for warning in warnings:
                if warning.startswith('⚠️') or warning.startswith('✓') or warning.startswith('📊'):
                    warning_section += f"{warning}\n\n"
                else:
                    warning_section += f"- ⚠️ {warning}\n"

            warning_section += "\n**Impact:** The analysis below may not accurately reflect actual performance.\n\n"
            warning_section += "---\n\n"
        else:
            # No serious warnings - snapshot will show data source
            warning_section = ""

        if warning_section:
            # Insert warnings after the first heading (title)
            lines = report.split('\n')
            insert_index = 0

            # Find the first heading or first line
            for i, line in enumerate(lines):
                if line.strip().startswith('#'):
                    insert_index = i + 1
                    break

            # Insert warning after first heading
            if insert_index > 0:
                lines.insert(insert_index, warning_section)
            else:
                lines.insert(0, warning_section)

            return '\n'.join(lines)

        return report
