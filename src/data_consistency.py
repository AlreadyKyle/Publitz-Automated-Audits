"""
Data Consistency Validation System

Ensures all numbers in reports are consistent and accurate. Prevents contradictions
like "0 reviews" in one place and "5 reviews" in another.

Single source of truth: All systems must pull from GameMetrics class.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a data consistency error"""
    error_type: str
    message: str
    severity: str  # 'critical', 'warning', 'info'
    field: str
    expected: Any = None
    actual: Any = None


@dataclass
class GameMetrics:
    """
    Single source of truth for all game metrics.

    All report sections MUST pull from this class to ensure consistency.
    Validates data on initialization and provides computed properties.

    Usage:
        metrics = GameMetrics(raw_data)
        # All systems now use metrics.revenue_gross, metrics.review_count_total, etc.
    """

    # Raw inputs (from API/database)
    app_id: str
    game_name: str

    # Revenue metrics
    revenue_gross: float
    days_since_launch: int

    # Review metrics
    review_count_total: int
    review_count_positive: int
    review_count_negative: int

    # Ownership metrics
    owner_count: int

    # Pricing
    price_usd: float

    # Metadata
    release_date: str = ""
    genres: List[str] = field(default_factory=list)

    # Computed properties (set in __post_init__)
    revenue_after_steam_cut: float = field(init=False)
    daily_revenue: float = field(init=False)
    monthly_revenue: float = field(init=False)
    review_percentage: float = field(init=False)
    review_rate: float = field(init=False)  # Reviews per 100 owners
    revenue_per_owner: float = field(init=False)

    # Validation results
    validation_errors: List[ValidationError] = field(default_factory=list, init=False)
    validation_warnings: List[ValidationError] = field(default_factory=list, init=False)
    is_valid: bool = field(default=True, init=False)

    def __post_init__(self):
        """Calculate computed properties and validate"""

        # Calculate computed properties
        self.revenue_after_steam_cut = self.revenue_gross * 0.7  # 30% Steam cut
        self.daily_revenue = self.revenue_gross / max(self.days_since_launch, 1)
        self.monthly_revenue = self.daily_revenue * 30

        # Review percentage
        if self.review_count_total > 0:
            self.review_percentage = (self.review_count_positive / self.review_count_total) * 100
        else:
            self.review_percentage = 0.0

        # Review rate (reviews per 100 owners)
        if self.owner_count > 0:
            self.review_rate = (self.review_count_total / self.owner_count) * 100
        else:
            self.review_rate = 0.0

        # Revenue per owner
        if self.owner_count > 0:
            self.revenue_per_owner = self.revenue_gross / self.owner_count
        else:
            self.revenue_per_owner = 0.0

        # Run validation
        self._validate()

    def _validate(self):
        """Run comprehensive validation checks"""

        # Critical errors (prevent report generation)
        self._validate_critical()

        # Warnings (allow report but flag issues)
        self._validate_warnings()

        # Set validity flag
        self.is_valid = len(self.validation_errors) == 0

        # Log results
        if not self.is_valid:
            logger.error(f"Data validation failed for {self.game_name}: {len(self.validation_errors)} errors")
            for error in self.validation_errors:
                logger.error(f"  - {error.message}")

        if self.validation_warnings:
            logger.warning(f"Data validation warnings for {self.game_name}: {len(self.validation_warnings)} warnings")
            for warning in self.validation_warnings:
                logger.warning(f"  - {warning.message}")

    def _validate_critical(self):
        """Critical validation errors that prevent report generation"""

        # Revenue cannot be negative
        if self.revenue_gross < 0:
            self.validation_errors.append(ValidationError(
                error_type='negative_revenue',
                message=f"Revenue cannot be negative: ${self.revenue_gross}",
                severity='critical',
                field='revenue_gross',
                expected='>= 0',
                actual=self.revenue_gross
            ))

        # Reviews cannot exceed owners
        if self.review_count_total > self.owner_count:
            self.validation_errors.append(ValidationError(
                error_type='reviews_exceed_owners',
                message=f"Review count ({self.review_count_total}) exceeds owner count ({self.owner_count})",
                severity='critical',
                field='review_count_total',
                expected=f'<= {self.owner_count}',
                actual=self.review_count_total
            ))

        # Positive + negative must equal total
        calculated_total = self.review_count_positive + self.review_count_negative
        if calculated_total != self.review_count_total:
            self.validation_errors.append(ValidationError(
                error_type='review_math_error',
                message=f"Review math doesn't add up: {self.review_count_positive} positive + "
                       f"{self.review_count_negative} negative ≠ {self.review_count_total} total",
                severity='critical',
                field='review_count_total',
                expected=calculated_total,
                actual=self.review_count_total
            ))

        # Review counts cannot be negative
        if self.review_count_total < 0 or self.review_count_positive < 0 or self.review_count_negative < 0:
            self.validation_errors.append(ValidationError(
                error_type='negative_reviews',
                message=f"Review counts cannot be negative",
                severity='critical',
                field='review_count_total'
            ))

        # Owner count cannot be negative
        if self.owner_count < 0:
            self.validation_errors.append(ValidationError(
                error_type='negative_owners',
                message=f"Owner count cannot be negative: {self.owner_count}",
                severity='critical',
                field='owner_count',
                expected='>= 0',
                actual=self.owner_count
            ))

        # Price must be reasonable
        if self.price_usd < 0:
            self.validation_errors.append(ValidationError(
                error_type='negative_price',
                message=f"Price cannot be negative: ${self.price_usd}",
                severity='critical',
                field='price_usd',
                expected='>= 0',
                actual=self.price_usd
            ))

        if self.price_usd > 200:
            self.validation_errors.append(ValidationError(
                error_type='unreasonable_price',
                message=f"Price ${self.price_usd} is unreasonably high (>$200)",
                severity='critical',
                field='price_usd',
                expected='<= 200',
                actual=self.price_usd
            ))

        # Days since launch must be positive
        if self.days_since_launch <= 0:
            self.validation_errors.append(ValidationError(
                error_type='invalid_days_since_launch',
                message=f"Days since launch must be positive: {self.days_since_launch}",
                severity='critical',
                field='days_since_launch',
                expected='> 0',
                actual=self.days_since_launch
            ))

    def _validate_warnings(self):
        """Non-critical warnings about suspicious data patterns"""

        # Revenue should approximately match owners × price
        if self.owner_count > 0 and self.price_usd > 0 and self.revenue_gross > 0:
            expected_revenue_min = self.owner_count * self.price_usd * 0.5  # Assuming 50%+ bought on sale
            expected_revenue_max = self.owner_count * self.price_usd * 1.0  # All full price

            if self.revenue_gross < expected_revenue_min * 0.5:
                self.validation_warnings.append(ValidationError(
                    error_type='revenue_too_low',
                    message=f"Revenue ${self.revenue_gross:,.0f} is suspiciously low for "
                           f"{self.owner_count:,} owners at ${self.price_usd} "
                           f"(expected ${expected_revenue_min:,.0f}-${expected_revenue_max:,.0f})",
                    severity='warning',
                    field='revenue_gross',
                    expected=f'${expected_revenue_min:,.0f}-${expected_revenue_max:,.0f}',
                    actual=f'${self.revenue_gross:,.0f}'
                ))

            if self.revenue_gross > expected_revenue_max * 1.5:
                self.validation_warnings.append(ValidationError(
                    error_type='revenue_too_high',
                    message=f"Revenue ${self.revenue_gross:,.0f} is suspiciously high for "
                           f"{self.owner_count:,} owners at ${self.price_usd} "
                           f"(expected ${expected_revenue_min:,.0f}-${expected_revenue_max:,.0f})",
                    severity='warning',
                    field='revenue_gross',
                    expected=f'${expected_revenue_min:,.0f}-${expected_revenue_max:,.0f}',
                    actual=f'${self.revenue_gross:,.0f}'
                ))

        # Review rate warnings
        if self.owner_count > 100 and self.review_rate < 1:
            self.validation_warnings.append(ValidationError(
                error_type='low_review_rate',
                message=f"Very low review rate: {self.review_rate:.1f}% "
                       f"({self.review_count_total} reviews from {self.owner_count:,} owners). "
                       f"Typical: 2-5%",
                severity='warning',
                field='review_count_total'
            ))

        if self.review_rate > 15:
            self.validation_warnings.append(ValidationError(
                error_type='high_review_rate',
                message=f"Unusually high review rate: {self.review_rate:.1f}% "
                       f"({self.review_count_total} reviews from {self.owner_count:,} owners). "
                       f"Typical: 2-5%. May indicate review manipulation.",
                severity='warning',
                field='review_count_total'
            ))

        # Small sample size warnings
        if self.review_count_total < 10 and self.review_percentage > 90:
            self.validation_warnings.append(ValidationError(
                error_type='small_sample_high_score',
                message=f"Review score {self.review_percentage:.0f}% may not be representative "
                       f"(only {self.review_count_total} reviews)",
                severity='warning',
                field='review_percentage'
            ))

        # Extreme daily revenue
        if self.daily_revenue < 10 and self.owner_count > 500:
            self.validation_warnings.append(ValidationError(
                error_type='very_low_daily_revenue',
                message=f"Daily revenue ${self.daily_revenue:.2f} is extremely low for "
                       f"{self.owner_count:,} owners. Check data quality.",
                severity='warning',
                field='revenue_gross'
            ))

    def get_validation_summary(self) -> str:
        """Get human-readable validation summary"""
        if self.is_valid and not self.validation_warnings:
            return "✅ All validation checks passed"

        summary = []

        if self.validation_errors:
            summary.append(f"❌ {len(self.validation_errors)} critical error(s):")
            for error in self.validation_errors:
                summary.append(f"  - {error.message}")

        if self.validation_warnings:
            summary.append(f"⚠️  {len(self.validation_warnings)} warning(s):")
            for warning in self.validation_warnings:
                summary.append(f"  - {warning.message}")

        return "\n".join(summary)

    @classmethod
    def from_game_data(cls, game_data: Dict[str, Any]) -> 'GameMetrics':
        """
        Create GameMetrics from raw game_data dict.

        This is the main entry point for converting raw API data into validated metrics.
        """
        # Calculate positive/negative reviews with proper rounding to avoid truncation errors
        review_count = game_data.get('review_count', 0)
        review_score_pct = game_data.get('review_score', 0)

        # Use round() instead of int() to avoid truncation errors (e.g., 355.68 + 100.32 = 456)
        positive_default = round(review_count * review_score_pct / 100)
        negative_default = review_count - positive_default  # Calculate from remainder to ensure sum equals total

        return cls(
            app_id=str(game_data.get('app_id', '')),
            game_name=game_data.get('name', 'Unknown'),
            revenue_gross=float(game_data.get('revenue', 0)),
            days_since_launch=int(game_data.get('days_since_launch', 1)),
            review_count_total=int(review_count),
            review_count_positive=int(game_data.get('positive_reviews', positive_default)),
            review_count_negative=int(game_data.get('negative_reviews', negative_default)),
            owner_count=int(game_data.get('owners', 0)),
            price_usd=float(game_data.get('price', 0)),
            release_date=game_data.get('release_date', ''),
            genres=game_data.get('genres', [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Export metrics to dict for compatibility with existing code"""
        return {
            'app_id': self.app_id,
            'name': self.game_name,
            'revenue': self.revenue_gross,
            'revenue_after_cut': self.revenue_after_steam_cut,
            'daily_revenue': self.daily_revenue,
            'monthly_revenue': self.monthly_revenue,
            'days_since_launch': self.days_since_launch,
            'review_count': self.review_count_total,
            'positive_reviews': self.review_count_positive,
            'negative_reviews': self.review_count_negative,
            'review_score': self.review_percentage,
            'review_rate': self.review_rate,
            'owners': self.owner_count,
            'revenue_per_owner': self.revenue_per_owner,
            'price': self.price_usd,
            'release_date': self.release_date,
            'genres': self.genres
        }


def validate_report_consistency(report_text: str, metrics: GameMetrics) -> List[Dict[str, Any]]:
    """
    Scan generated report for any numbers that contradict GameMetrics.

    Args:
        report_text: Complete report text
        metrics: Validated GameMetrics object

    Returns:
        List of inconsistencies found
    """

    inconsistencies = []

    # Extract all revenue mentions ($X or $X,XXX)
    revenue_pattern = r'\$(\d{1,3}(?:,\d{3})*)'
    revenue_mentions = re.findall(revenue_pattern, report_text)

    for mention in revenue_mentions:
        amount = int(mention.replace(',', ''))

        # Check if this matches our known revenue values
        expected_values = [
            metrics.revenue_gross,
            metrics.revenue_after_steam_cut,
            metrics.daily_revenue,
            metrics.monthly_revenue,
            metrics.price_usd
        ]

        # Allow 1% tolerance for rounding
        matches_expected = any(abs(amount - val) / max(val, 1) < 0.01 for val in expected_values if val > 0)

        if not matches_expected and amount > 100:  # Ignore small amounts (could be examples)
            inconsistencies.append({
                'type': 'revenue_mismatch',
                'found': f'${mention}',
                'expected_values': [f'${v:,.0f}' for v in expected_values if v > 0],
                'context': 'Found revenue figure that doesn\'t match any known metric',
                'severity': 'warning'
            })

    # Extract review count mentions
    review_pattern = r'(\d+)\s+reviews?'
    review_mentions = re.findall(review_pattern, report_text, re.IGNORECASE)

    for mention in review_mentions:
        count = int(mention)

        # Check against known review counts
        expected_counts = [
            metrics.review_count_total,
            metrics.review_count_positive,
            metrics.review_count_negative
        ]

        if count not in expected_counts and count > 0:
            inconsistencies.append({
                'type': 'review_count_mismatch',
                'found': f'{count} reviews',
                'expected_values': [str(c) for c in expected_counts],
                'context': 'Found review count that doesn\'t match known totals',
                'severity': 'warning'
            })

    # Extract owner count mentions
    owner_pattern = r'(\d{1,3}(?:,\d{3})*)\s+owners?'
    owner_mentions = re.findall(owner_pattern, report_text, re.IGNORECASE)

    for mention in owner_mentions:
        count = int(mention.replace(',', ''))

        # Allow 10% tolerance for owner count (estimates vary)
        if abs(count - metrics.owner_count) / max(metrics.owner_count, 1) > 0.1:
            inconsistencies.append({
                'type': 'owner_count_mismatch',
                'found': f'{count:,} owners',
                'expected': f'{metrics.owner_count:,} owners',
                'context': 'Found owner count significantly different from source data',
                'severity': 'warning'
            })

    # Extract percentage mentions
    percentage_pattern = r'(\d+(?:\.\d+)?)%'
    percentage_mentions = re.findall(percentage_pattern, report_text)

    for mention in percentage_mentions:
        pct = float(mention)

        # Check if this matches review percentage
        if abs(pct - metrics.review_percentage) < 0.5:
            continue  # Match found, skip

        # If it's a review-related percentage and doesn't match, flag it
        if pct > 50 and pct < 100:  # Likely a review score
            inconsistencies.append({
                'type': 'percentage_mismatch',
                'found': f'{pct}%',
                'expected': f'{metrics.review_percentage:.1f}%',
                'context': 'Found percentage that may not match review score',
                'severity': 'info'
            })

    if inconsistencies:
        logger.warning(f"Found {len(inconsistencies)} potential inconsistencies in report")
        for inc in inconsistencies:
            logger.warning(f"  - {inc['type']}: {inc['found']} (context: {inc['context']})")

    return inconsistencies


def auto_fix_inconsistencies(report_text: str, metrics: GameMetrics) -> str:
    """
    Replace inconsistent numbers with correct values from GameMetrics.

    This is a nuclear option - use with caution. Better to fix at source.

    Args:
        report_text: Report text with potential inconsistencies
        metrics: Validated GameMetrics object

    Returns:
        Corrected report text
    """

    logger.info("Attempting auto-fix of report inconsistencies...")

    # Note: Auto-fix is tricky because we don't want to replace legitimate numbers
    # (like "Top 10 actions" or "30-day plan")
    # For now, we'll be conservative and only fix obvious patterns

    fixes_applied = 0

    # Fix specific patterns only
    # Example: "0 reviews" when we know there are reviews
    if metrics.review_count_total > 0:
        original = report_text
        report_text = re.sub(
            r'\b0\s+reviews?\b',
            f'{metrics.review_count_total} reviews',
            report_text,
            flags=re.IGNORECASE
        )
        if report_text != original:
            fixes_applied += 1
            logger.info(f"  Fixed: '0 reviews' → '{metrics.review_count_total} reviews'")

    # Fix "$0 revenue" when we know there's revenue
    if metrics.revenue_gross > 0:
        original = report_text
        report_text = re.sub(
            r'\$0\s+(?:revenue|gross)',
            f'${metrics.revenue_gross:,.0f}',
            report_text,
            flags=re.IGNORECASE
        )
        if report_text != original:
            fixes_applied += 1
            logger.info(f"  Fixed: '$0 revenue' → '${metrics.revenue_gross:,.0f}'")

    logger.info(f"Auto-fix complete: {fixes_applied} fixes applied")

    return report_text


def pre_flight_check(game_data: Dict[str, Any]) -> Tuple[bool, GameMetrics, List[str]]:
    """
    Run comprehensive validation before generating report.

    This is the main entry point for validation. Call this before report generation.

    Args:
        game_data: Raw game data dict

    Returns:
        Tuple of (is_valid, metrics, error_messages)
        - is_valid: True if data passes critical checks
        - metrics: GameMetrics object (even if invalid, for inspection)
        - error_messages: List of error/warning messages
    """

    logger.info(f"Running pre-flight check for {game_data.get('name', 'Unknown')}...")

    try:
        # Create GameMetrics (runs validation automatically)
        metrics = GameMetrics.from_game_data(game_data)

        # Collect all messages
        messages = []

        # Add critical errors
        for error in metrics.validation_errors:
            messages.append(f"❌ ERROR: {error.message}")

        # Add warnings
        for warning in metrics.validation_warnings:
            messages.append(f"⚠️  WARNING: {warning.message}")

        # Determine if we can proceed
        can_proceed = metrics.is_valid

        if can_proceed:
            if metrics.validation_warnings:
                logger.warning(f"Pre-flight check passed with {len(metrics.validation_warnings)} warnings")
            else:
                logger.info("Pre-flight check passed - data is valid")
        else:
            logger.error(f"Pre-flight check FAILED: {len(metrics.validation_errors)} critical errors")

        return can_proceed, metrics, messages

    except Exception as e:
        logger.error(f"Pre-flight check failed with exception: {e}")
        # Return a minimal metrics object
        minimal_metrics = GameMetrics(
            app_id=str(game_data.get('app_id', '')),
            game_name=game_data.get('name', 'Unknown'),
            revenue_gross=0,
            days_since_launch=1,
            review_count_total=0,
            review_count_positive=0,
            review_count_negative=0,
            owner_count=0,
            price_usd=0
        )
        return False, minimal_metrics, [f"❌ CRITICAL: Data validation failed: {str(e)}"]


# ============================================================================
# TESTING
# ============================================================================

def test_retrace_the_light():
    """Test data consistency with Retrace the Light data"""

    print("\n" + "="*80)
    print("DATA CONSISTENCY TEST: Retrace the Light")
    print("="*80 + "\n")

    # Actual game data
    game_data = {
        'app_id': '1234567',
        'name': 'Retrace the Light',
        'revenue': 379,
        'days_since_launch': 7,
        'review_count': 5,
        'review_score': 80.0,  # 80% positive
        'owners': 100,
        'price': 14.99,
        'release_date': '2024-11-18',
        'genres': ['Adventure', 'Indie']
    }

    print("INPUT DATA:")
    print(f"  Game: {game_data['name']}")
    print(f"  Revenue: ${game_data['revenue']}")
    print(f"  Days Since Launch: {game_data['days_since_launch']}")
    print(f"  Reviews: {game_data['review_count']} ({game_data['review_score']}% positive)")
    print(f"  Owners: {game_data['owners']}")
    print(f"  Price: ${game_data['price']}")
    print()

    # Run pre-flight check
    print("RUNNING PRE-FLIGHT CHECK...")
    print()

    is_valid, metrics, messages = pre_flight_check(game_data)

    print("VALIDATION RESULTS:")
    print(f"  Valid: {is_valid}")
    print()

    if messages:
        print("MESSAGES:")
        for msg in messages:
            print(f"  {msg}")
        print()

    print("COMPUTED METRICS:")
    print(f"  Revenue (gross): ${metrics.revenue_gross:,.0f}")
    print(f"  Revenue (after Steam cut): ${metrics.revenue_after_steam_cut:,.2f}")
    print(f"  Daily Revenue: ${metrics.daily_revenue:.2f}")
    print(f"  Monthly Revenue: ${metrics.monthly_revenue:.2f}")
    print(f"  Review Percentage: {metrics.review_percentage:.1f}%")
    print(f"  Positive Reviews: {metrics.review_count_positive}")
    print(f"  Negative Reviews: {metrics.review_count_negative}")
    print(f"  Review Rate: {metrics.review_rate:.2f}%")
    print(f"  Revenue per Owner: ${metrics.revenue_per_owner:.2f}")
    print()

    print("VALIDATION SUMMARY:")
    print(metrics.get_validation_summary())
    print()

    print("="*80 + "\n")

    return is_valid, metrics


if __name__ == "__main__":
    test_retrace_the_light()
