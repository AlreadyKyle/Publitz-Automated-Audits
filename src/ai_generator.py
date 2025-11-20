import anthropic
from typing import Dict, List, Any
import json

class AIGenerator:
    """AI-powered report generator using Claude API"""

    def __init__(self, api_key: str):
        """
        Initialize the AI generator with Anthropic API key

        Args:
            api_key: Anthropic API key
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        # FIXED: Using the correct Claude model name
        # The old model 'claude-3-5-sonnet-20240620' does not exist
        # Using the latest Claude Sonnet 4.5 model
        self.model = "claude-sonnet-4-5-20250929"

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
