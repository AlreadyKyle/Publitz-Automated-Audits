"""
A/B Testing Recommendations for Store Pages

Generates specific A/B test variations for store page elements
with expected impact predictions and implementation guidance.
"""

from typing import Dict, Any, List, Tuple


class ABTestingRecommender:
    """Generates A/B testing recommendations for Steam store pages"""

    # Test types with expected impact ranges
    TEST_TYPES = {
        'capsule_image': {
            'impact_range': '5-15% CTR improvement',
            'difficulty': 'EASY',
            'time_to_test': '7-14 days',
            'sample_size_needed': 1000
        },
        'title_variation': {
            'impact_range': '3-8% CTR improvement',
            'difficulty': 'EASY',
            'time_to_test': '7-14 days',
            'sample_size_needed': 1000
        },
        'short_description': {
            'impact_range': '8-20% wishlist conversion',
            'difficulty': 'EASY',
            'time_to_test': '14-21 days',
            'sample_size_needed': 2000
        },
        'screenshot_order': {
            'impact_range': '5-12% engagement improvement',
            'difficulty': 'EASY',
            'time_to_test': '7-14 days',
            'sample_size_needed': 1500
        },
        'tag_combinations': {
            'impact_range': '10-25% impression increase',
            'difficulty': 'MEDIUM',
            'time_to_test': '14-30 days',
            'sample_size_needed': 3000
        },
        'pricing_psychology': {
            'impact_range': '8-15% purchase conversion',
            'difficulty': 'MEDIUM',
            'time_to_test': '30-60 days',
            'sample_size_needed': 5000
        },
        'launch_discount': {
            'impact_range': '20-40% day 1 revenue',
            'difficulty': 'EASY',
            'time_to_test': 'Launch only',
            'sample_size_needed': 1000
        }
    }

    def __init__(self):
        """Initialize the A/B testing recommender"""
        pass

    def generate_recommendations(
        self,
        game_data: Dict[str, Any],
        sales_data: Dict[str, Any],
        competitor_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate A/B testing recommendations

        Args:
            game_data: Game information
            sales_data: Sales data
            competitor_data: Competitor information

        Returns:
            A/B testing recommendations with specific variations
        """
        genres = game_data.get('genres', '').lower()
        tags = game_data.get('tags', '').lower()
        price = game_data.get('price', '$0')
        game_name = game_data.get('name', 'Your Game')

        # Generate test recommendations
        capsule_tests = self._generate_capsule_tests(game_name, genres, tags)
        title_tests = self._generate_title_tests(game_name, genres, tags)
        description_tests = self._generate_description_tests(game_name, genres, tags)
        screenshot_tests = self._generate_screenshot_tests(genres)
        tag_tests = self._generate_tag_tests(genres, tags)
        pricing_tests = self._generate_pricing_tests(price, competitor_data)
        discount_tests = self._generate_discount_tests(price)

        # Prioritize tests
        all_tests = (
            capsule_tests + title_tests + description_tests +
            screenshot_tests + tag_tests + pricing_tests + discount_tests
        )
        prioritized_tests = self._prioritize_tests(all_tests, sales_data)

        # Generate testing timeline
        testing_timeline = self._generate_testing_timeline(prioritized_tests)

        return {
            'recommended_tests': prioritized_tests,
            'testing_timeline': testing_timeline,
            'measurement_guide': self._generate_measurement_guide(),
            'statistical_significance_calculator': self._generate_significance_calculator()
        }

    def _generate_capsule_tests(
        self,
        game_name: str,
        genres: str,
        tags: str
    ) -> List[Dict[str, Any]]:
        """Generate capsule image A/B test variations"""
        tests = []

        # Test 1: Action vs Atmosphere
        tests.append({
            'test_id': 'CAPSULE-001',
            'test_type': 'capsule_image',
            'test_name': 'Action Moment vs Atmospheric Scene',
            'priority': 'HIGH',
            'hypothesis': 'Action-packed capsule will have higher CTR than atmospheric scene',
            'control': 'Current capsule image',
            'variation_a': 'High-action gameplay moment (combat, ability usage, dramatic event)',
            'variation_b': 'Atmospheric scene (beautiful vista, moody environment)',
            'expected_winner': 'Variation A for action genres, Variation B for exploration/story games',
            'expected_impact': '+8-12% CTR',
            'implementation': [
                '1. Create 2 capsule variations (620x465px)',
                '2. Use Steam\'s traffic allocation (50/50 split)',
                '3. Run for 14 days or 1,000+ impressions per variation',
                '4. Measure CTR difference'
            ],
            'measurement_metrics': ['Impressions', 'Clicks', 'CTR %', 'Statistical significance'],
            'difficulty': 'EASY',
            'time_required': '7-14 days'
        })

        # Test 2: Character vs Environment
        tests.append({
            'test_id': 'CAPSULE-002',
            'test_type': 'capsule_image',
            'test_name': 'Character Focus vs Environment Focus',
            'priority': 'MEDIUM',
            'hypothesis': 'Character-focused capsule will perform better for character-driven games',
            'control': 'Current capsule image',
            'variation_a': 'Prominent character(s) in foreground',
            'variation_b': 'Environment/world showcase with small/no characters',
            'expected_winner': 'Variation A for RPG/story games, Variation B for strategy/simulation',
            'expected_impact': '+5-10% CTR',
            'implementation': [
                '1. Create character-focused version (close-up, emotional)',
                '2. Create environment-focused version (world-building)',
                '3. Test with 50/50 split',
                '4. Segment results by genre affinity if possible'
            ],
            'measurement_metrics': ['CTR by genre tag', 'Wishlist conversion rate'],
            'difficulty': 'EASY',
            'time_required': '7-14 days'
        })

        # Test 3: Text Overlay vs Clean
        tests.append({
            'test_id': 'CAPSULE-003',
            'test_type': 'capsule_image',
            'test_name': 'Text Overlay vs Clean Image',
            'priority': 'MEDIUM',
            'hypothesis': 'Clean capsule without text performs better (game name shows separately)',
            'control': 'Current capsule',
            'variation_a': 'Clean capsule with no text overlay',
            'variation_b': 'Capsule with tagline/USP text ("Roguelike Deckbuilder", "1M+ Wishlists")',
            'expected_winner': 'Variation A (Steam shows title separately, text clutters)',
            'expected_impact': '+3-7% CTR',
            'implementation': [
                '1. Remove all text from capsule (keep logo if integrated into art)',
                '2. Test clean vs text overlay',
                '3. Measure CTR and attention heatmaps if available'
            ],
            'measurement_metrics': ['CTR', 'Bounce rate'],
            'difficulty': 'EASY',
            'time_required': '7 days'
        })

        return tests

    def _generate_title_tests(
        self,
        game_name: str,
        genres: str,
        tags: str
    ) -> List[Dict[str, Any]]:
        """Generate game title A/B test variations"""
        tests = []

        # Test 1: Descriptive vs Evocative
        tests.append({
            'test_id': 'TITLE-001',
            'test_type': 'title_variation',
            'test_name': 'Descriptive Title vs Evocative Title',
            'priority': 'LOW',
            'hypothesis': 'Descriptive subtitle increases genre clarity',
            'control': f'{game_name}',
            'variation_a': f'{game_name}: [Genre Descriptor]',
            'variation_b': f'{game_name}: [Evocative Tagline]',
            'expected_winner': 'Variation A for niche genres (helps discoverability)',
            'expected_impact': '+3-6% CTR',
            'implementation': [
                '1. WARNING: Title changes require Steam approval, risky',
                '2. Only test during pre-release if possible',
                '3. Use subtitle, not main title change',
                '4. Examples: "Game Name: A Roguelike Adventure" vs "Game Name: Descent into Madness"'
            ],
            'measurement_metrics': ['Search impressions', 'CTR', 'Genre tag click-through'],
            'difficulty': 'HIGH',
            'time_required': 'N/A - risky, low priority'
        })

        return tests

    def _generate_description_tests(
        self,
        game_name: str,
        genres: str,
        tags: str
    ) -> List[Dict[str, Any]]:
        """Generate short description A/B tests"""
        tests = []

        # Test 1: Feature-focused vs Emotion-focused
        tests.append({
            'test_id': 'DESC-001',
            'test_type': 'short_description',
            'test_name': 'Feature List vs Emotional Hook',
            'priority': 'HIGH',
            'hypothesis': 'Emotional hook in first sentence drives more wishlists',
            'control': 'Current short description',
            'variation_a': '"[Game] is a [genre] with [feature list]"',
            'variation_b': '"[Emotional hook]. [Single compelling benefit]. [Call to action]"',
            'expected_winner': 'Variation B (emotion-first approach)',
            'expected_impact': '+10-18% wishlist conversion',
            'implementation': [
                '1. Write 2 short descriptions (280 chars max)',
                '2. Variation A: Start with features ("Deck-building roguelike with 500+ cards...")',
                '3. Variation B: Start with emotion ("Every run tells a story. Build devastating combos...")',
                '4. A/B test via external landing page or Steam events'
            ],
            'measurement_metrics': ['Wishlist conversion rate', 'Time on page', 'Read depth'],
            'difficulty': 'EASY',
            'time_required': '14-21 days'
        })

        # Test 2: Social Proof vs No Social Proof
        tests.append({
            'test_id': 'DESC-002',
            'test_type': 'short_description',
            'test_name': 'Social Proof Inclusion Test',
            'priority': 'MEDIUM',
            'hypothesis': 'Including social proof increases trust and conversions',
            'control': 'Description without social proof',
            'variation_a': 'Description without any metrics or reviews',
            'variation_b': 'Description with social proof ("50K+ wishlists", "Very Positive reviews")',
            'expected_winner': 'Variation B (if you have strong social proof)',
            'expected_impact': '+8-15% wishlist conversion',
            'implementation': [
                '1. Only test if you have positive social proof (>5K wishlists OR >80% positive)',
                '2. Add social proof to first or last sentence',
                '3. Examples: "Join 50,000+ players", "Overwhelmingly Positive (95%)"',
                '4. Update regularly as numbers grow'
            ],
            'measurement_metrics': ['Wishlist conversion', 'Purchase intent'],
            'difficulty': 'EASY',
            'time_required': '14 days'
        })

        return tests

    def _generate_screenshot_tests(self, genres: str) -> List[Dict[str, Any]]:
        """Generate screenshot order A/B tests"""
        tests = []

        tests.append({
            'test_id': 'SCREENSHOT-001',
            'test_type': 'screenshot_order',
            'test_name': 'Hero Shot First vs Gameplay First',
            'priority': 'MEDIUM',
            'hypothesis': 'Exciting hero moment first increases engagement',
            'control': 'Current screenshot order',
            'variation_a': 'Hero moment → Gameplay → Features → Variety → Polish',
            'variation_b': 'Gameplay → Hero moment → Features → Variety → Polish',
            'expected_winner': 'Variation A (hook attention immediately)',
            'expected_impact': '+5-10% screenshot click-through',
            'implementation': [
                '1. Reorder screenshots in Steam dashboard',
                '2. Screenshot 1 is critical (shows in search results)',
                '3. Test 2 orders for 14 days each',
                '4. Measure: Screenshot views, time spent on store page'
            ],
            'measurement_metrics': ['Screenshot engagement', 'Store page time', 'Wishlist rate'],
            'difficulty': 'EASY',
            'time_required': '7 days per variation'
        })

        return tests

    def _generate_tag_tests(self, genres: str, tags: str) -> List[Dict[str, Any]]:
        """Generate tag combination A/B tests"""
        tests = []

        tests.append({
            'test_id': 'TAG-001',
            'test_type': 'tag_combinations',
            'test_name': 'Broad vs Specific Tag Mix',
            'priority': 'HIGH',
            'hypothesis': 'Specific tags (higher conversion) outperform broad tags (more impressions)',
            'control': 'Current tag set',
            'variation_a': 'Mix of broad (Indie, Action, RPG) + specific tags',
            'variation_b': 'Mostly specific tags (Roguelike, Deckbuilder, Turn-Based)',
            'expected_winner': 'Variation B (better targeted traffic)',
            'expected_impact': '+15-25% tag impression quality',
            'implementation': [
                '1. Create two tag sets (15-20 tags each)',
                '2. Control: 50% broad, 50% specific',
                '3. Variation: 80% specific, 20% broad',
                '4. Measure impression-to-wishlist conversion by tag'
            ],
            'measurement_metrics': ['Impressions by tag', 'Wishlist conversion by tag source', 'Tag click-through'],
            'difficulty': 'MEDIUM',
            'time_required': '14-30 days'
        })

        return tests

    def _generate_pricing_tests(
        self,
        price: str,
        competitor_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate pricing psychology A/B tests"""
        tests = []

        # Extract price value
        price_val = self._extract_price_value(price)

        # Test 1: Charm pricing
        if price_val > 10:
            tests.append({
                'test_id': 'PRICE-001',
                'test_type': 'pricing_psychology',
                'test_name': 'Charm Pricing Test ($19.99 vs $20.00)',
                'priority': 'MEDIUM',
                'hypothesis': '.99 pricing increases purchase conversion',
                'control': f'${price_val:.2f}',
                'variation_a': f'${int(price_val)}.99',
                'variation_b': f'${int(price_val) + 1}.00',
                'expected_winner': 'Variation A (.99 pricing)',
                'expected_impact': '+8-12% purchase conversion',
                'implementation': [
                    '1. WARNING: Price changes are visible to all users',
                    '2. Test during sale periods or pre-launch',
                    '3. $19.99 vs $20.00 type comparison',
                    '4. Monitor purchase conversion rate closely'
                ],
                'measurement_metrics': ['Purchase conversion %', 'Revenue per visitor', 'Cart abandonment'],
                'difficulty': 'MEDIUM',
                'time_required': '30-60 days'
            })

        return tests

    def _generate_discount_tests(self, price: str) -> List[Dict[str, Any]]:
        """Generate launch discount A/B tests"""
        tests = []

        price_val = self._extract_price_value(price)

        tests.append({
            'test_id': 'DISCOUNT-001',
            'test_type': 'launch_discount',
            'test_name': 'Launch Discount Percentage Test',
            'priority': 'HIGH',
            'hypothesis': '15% discount is sweet spot for launch conversion',
            'control': f'No discount (${price_val:.2f})',
            'variation_a': f'10% discount (${price_val * 0.9:.2f})',
            'variation_b': f'15% discount (${price_val * 0.85:.2f})',
            'variation_c': f'20% discount (${price_val * 0.8:.2f})',
            'expected_winner': 'Variation B (15% - best revenue vs conversion balance)',
            'expected_impact': '+30-50% day 1 revenue',
            'implementation': [
                '1. CRITICAL: Only test on launch day/week',
                '2. 10%: Conservative, premium positioning',
                '3. 15%: Industry standard, strong conversion',
                '4. 20%: Aggressive, may signal desperation',
                '5. Measure total revenue, not just units sold'
            ],
            'measurement_metrics': ['Total revenue', 'Units sold', 'Discount to full-price ratio post-launch'],
            'difficulty': 'EASY',
            'time_required': 'Launch week only'
        })

        return tests

    def _prioritize_tests(
        self,
        all_tests: List[Dict[str, Any]],
        sales_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prioritize tests by expected ROI and ease of implementation"""

        priority_weights = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        difficulty_weights = {'EASY': 3, 'MEDIUM': 2, 'HIGH': 1}

        for test in all_tests:
            priority = test.get('priority', 'MEDIUM')
            difficulty = test.get('difficulty', 'MEDIUM')

            # Calculate priority score
            score = priority_weights.get(priority, 2) * difficulty_weights.get(difficulty, 2)
            test['priority_score'] = score

        # Sort by priority score
        sorted_tests = sorted(all_tests, key=lambda x: x['priority_score'], reverse=True)

        return sorted_tests

    def _generate_testing_timeline(
        self,
        prioritized_tests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommended testing timeline"""
        timeline = []

        current_week = 0
        for i, test in enumerate(prioritized_tests[:8], 1):  # Top 8 tests
            time_req = test.get('time_required', '14 days')

            # Parse time requirement
            if 'days' in time_req:
                days = int(time_req.split('-')[0].replace('days', '').strip())
            else:
                days = 14  # Default

            weeks = max(1, days // 7)

            timeline.append({
                'week_start': current_week + 1,
                'week_end': current_week + weeks,
                'test_id': test['test_id'],
                'test_name': test['test_name'],
                'priority': test['priority'],
                'expected_impact': test.get('expected_impact', 'Unknown')
            })

            current_week += weeks

        return timeline

    def _generate_measurement_guide(self) -> Dict[str, Any]:
        """Generate guide for measuring test results"""
        return {
            'key_metrics': {
                'capsule_ctr': 'Clicks / Impressions = CTR %',
                'wishlist_conversion': 'Wishlists / Visits = Conversion %',
                'purchase_conversion': 'Purchases / Wishlists = Purchase %',
                'revenue_per_visitor': 'Total Revenue / Total Visits = RPV'
            },
            'sample_size_requirements': {
                'minimum': '1,000 visitors per variation',
                'ideal': '2,000+ visitors per variation',
                'high_confidence': '5,000+ visitors per variation'
            },
            'statistical_significance': {
                'target': '95% confidence level',
                'minimum': '90% confidence level',
                'p_value': '<0.05 (5% chance of random result)'
            },
            'testing_best_practices': [
                'Run tests for minimum 7 days (capture weekly patterns)',
                'Don\'t stop test early even if winning (data may shift)',
                'Only change ONE variable per test',
                'Run tests sequentially, not simultaneously (avoid interaction effects)',
                'Document everything (hypothesis, results, learnings)',
                'Implement winning variations permanently',
                'Re-test periodically (audience changes over time)'
            ]
        }

    def _generate_significance_calculator(self) -> str:
        """Generate statistical significance calculator guide"""
        calculator = "# Statistical Significance Calculator\n\n"
        calculator += "Use this formula to determine if your test results are statistically significant:\n\n"
        calculator += "```\n"
        calculator += "1. Calculate conversion rates:\n"
        calculator += "   Control Rate = (Control Conversions / Control Visitors) × 100\n"
        calculator += "   Variation Rate = (Variation Conversions / Variation Visitors) × 100\n\n"
        calculator += "2. Calculate lift:\n"
        calculator += "   Lift % = ((Variation Rate - Control Rate) / Control Rate) × 100\n\n"
        calculator += "3. Use online calculator for p-value:\n"
        calculator += "   - https://www.evanmiller.org/ab-testing/chi-squared.html\n"
        calculator += "   - Input: Visitors and conversions for both variants\n"
        calculator += "   - Target: p-value < 0.05 (95% confidence)\n\n"
        calculator += "4. Decision:\n"
        calculator += "   - p < 0.05: Statistically significant, implement winner\n"
        calculator += "   - p > 0.05: Not significant, need more data or no real difference\n"
        calculator += "```\n\n"
        calculator += "## Example Calculation\n\n"
        calculator += "```\n"
        calculator += "Control: 1,500 visitors, 300 wishlists = 20% conversion\n"
        calculator += "Variation: 1,500 visitors, 360 wishlists = 24% conversion\n\n"
        calculator += "Lift: ((24 - 20) / 20) × 100 = 20% improvement\n\n"
        calculator += "P-value: 0.023 (using chi-squared test)\n"
        calculator += "Result: p < 0.05, so result is statistically significant!\n"
        calculator += "Decision: Implement variation permanently\n"
        calculator += "```\n"

        return calculator

    def _extract_price_value(self, price_str: str) -> float:
        """Extract numeric price from price string"""
        if not price_str or price_str == 'Free':
            return 0.0

        import re
        price_clean = re.sub(r'[^0-9.]', '', price_str)
        try:
            return float(price_clean)
        except:
            return 0.0
