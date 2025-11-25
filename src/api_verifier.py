"""
API Verification and Tracking System

Tracks API calls during report generation to show clients which data sources
were successfully used. Provides transparency about data quality and completeness.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class APIStatus(Enum):
    """Status of an API call"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    NOT_CONFIGURED = "not_configured"


@dataclass
class APICallResult:
    """Result of a single API call"""
    api_name: str
    endpoint: str
    status: APIStatus
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    data_retrieved: bool = False

    @property
    def status_emoji(self) -> str:
        """Get emoji representation of status"""
        if self.status == APIStatus.SUCCESS:
            return "✅"
        elif self.status == APIStatus.FAILED:
            return "❌"
        elif self.status == APIStatus.SKIPPED:
            return "⏭️"
        else:
            return "⚠️"


class APIVerifier:
    """
    Tracks API calls during report generation and provides status summaries.

    Usage:
        verifier = APIVerifier()

        # Record API calls
        verifier.record_call("Steam Store API", "/api/appdetails", APIStatus.SUCCESS)
        verifier.record_call("SteamSpy", "/api.php", APIStatus.FAILED, "403 Forbidden")

        # Get status report
        status_section = verifier.generate_status_section()
    """

    def __init__(self):
        self.calls: List[APICallResult] = []
        self.start_time = datetime.now()

    def record_call(
        self,
        api_name: str,
        endpoint: str,
        status: APIStatus,
        error_message: Optional[str] = None,
        response_time_ms: Optional[float] = None,
        data_retrieved: bool = False
    ) -> APICallResult:
        """
        Record an API call result.

        Args:
            api_name: Human-readable API name (e.g., "Steam Store API")
            endpoint: API endpoint or purpose (e.g., "/api/appdetails")
            status: APIStatus enum value
            error_message: Error message if call failed
            response_time_ms: Response time in milliseconds
            data_retrieved: Whether useful data was retrieved

        Returns:
            The APICallResult object
        """
        result = APICallResult(
            api_name=api_name,
            endpoint=endpoint,
            status=status,
            error_message=error_message,
            response_time_ms=response_time_ms,
            data_retrieved=data_retrieved or (status == APIStatus.SUCCESS)
        )
        self.calls.append(result)
        return result

    def record_success(self, api_name: str, endpoint: str, response_time_ms: Optional[float] = None) -> APICallResult:
        """Shorthand to record successful API call"""
        return self.record_call(api_name, endpoint, APIStatus.SUCCESS, response_time_ms=response_time_ms, data_retrieved=True)

    def record_failure(self, api_name: str, endpoint: str, error_message: str) -> APICallResult:
        """Shorthand to record failed API call"""
        return self.record_call(api_name, endpoint, APIStatus.FAILED, error_message=error_message)

    def record_skipped(self, api_name: str, endpoint: str, reason: str) -> APICallResult:
        """Shorthand to record skipped API call"""
        return self.record_call(api_name, endpoint, APIStatus.SKIPPED, error_message=reason)

    def record_not_configured(self, api_name: str, endpoint: str) -> APICallResult:
        """Shorthand to record API that's not configured"""
        return self.record_call(api_name, endpoint, APIStatus.NOT_CONFIGURED, error_message="API key not configured")

    @property
    def successful_calls(self) -> List[APICallResult]:
        """Get all successful API calls"""
        return [c for c in self.calls if c.status == APIStatus.SUCCESS]

    @property
    def failed_calls(self) -> List[APICallResult]:
        """Get all failed API calls"""
        return [c for c in self.calls if c.status == APIStatus.FAILED]

    @property
    def total_calls(self) -> int:
        """Total number of API calls attempted"""
        return len([c for c in self.calls if c.status in [APIStatus.SUCCESS, APIStatus.FAILED]])

    @property
    def success_rate(self) -> float:
        """Success rate as percentage (0-100)"""
        if self.total_calls == 0:
            return 0.0
        return (len(self.successful_calls) / self.total_calls) * 100

    def get_apis_by_status(self) -> Dict[str, List[APICallResult]]:
        """Group API calls by status"""
        result = {
            'success': [],
            'failed': [],
            'skipped': [],
            'not_configured': []
        }

        for call in self.calls:
            if call.status == APIStatus.SUCCESS:
                result['success'].append(call)
            elif call.status == APIStatus.FAILED:
                result['failed'].append(call)
            elif call.status == APIStatus.SKIPPED:
                result['skipped'].append(call)
            elif call.status == APIStatus.NOT_CONFIGURED:
                result['not_configured'].append(call)

        return result

    def generate_status_section(self, include_timing: bool = False, detailed: bool = True) -> str:
        """
        Generate formatted status section for inclusion in reports.

        Args:
            include_timing: Whether to include response times
            detailed: Whether to include full details or just summary

        Returns:
            Formatted markdown section
        """
        if not self.calls:
            return "## Data Sources\n\nNo API calls were made during report generation.\n"

        by_status = self.get_apis_by_status()

        # Build section
        lines = [
            "## Data Sources & API Status",
            "",
            f"**Report generated using {len(self.successful_calls)}/{self.total_calls} operational APIs ({self.success_rate:.0f}% success rate)**",
            ""
        ]

        # Successful APIs
        if by_status['success']:
            lines.append("### ✅ Successfully Retrieved")
            lines.append("")
            for call in by_status['success']:
                timing = f" ({call.response_time_ms:.0f}ms)" if include_timing and call.response_time_ms else ""
                lines.append(f"- **{call.api_name}**{timing}")
                if detailed:
                    lines.append(f"  - Endpoint: `{call.endpoint}`")
                    lines.append(f"  - Status: Data retrieved successfully")
            lines.append("")

        # Failed APIs
        if by_status['failed']:
            lines.append("### ❌ Failed to Retrieve")
            lines.append("")
            for call in by_status['failed']:
                lines.append(f"- **{call.api_name}**")
                if detailed:
                    lines.append(f"  - Endpoint: `{call.endpoint}`")
                    lines.append(f"  - Error: {call.error_message}")
                    lines.append(f"  - Impact: Report may have limited data for this source")
            lines.append("")

        # Not configured
        if by_status['not_configured']:
            lines.append("### ⚠️ Not Configured")
            lines.append("")
            for call in by_status['not_configured']:
                lines.append(f"- **{call.api_name}**")
                if detailed:
                    lines.append(f"  - Note: API key not provided")
            lines.append("")

        # Skipped
        if by_status['skipped']:
            lines.append("### ⏭️ Skipped")
            lines.append("")
            for call in by_status['skipped']:
                lines.append(f"- **{call.api_name}**: {call.error_message}")
            lines.append("")

        # Data quality note
        lines.append("---")
        lines.append("")
        if self.success_rate >= 80:
            lines.append("**Data Quality**: ✅ Excellent - All primary data sources available")
        elif self.success_rate >= 60:
            lines.append("**Data Quality**: ⚠️ Good - Most data sources available, some gaps may exist")
        elif self.success_rate >= 40:
            lines.append("**Data Quality**: ⚠️ Limited - Several data sources unavailable, analysis may be incomplete")
        else:
            lines.append("**Data Quality**: ❌ Poor - Majority of data sources unavailable, analysis is limited")

        return "\n".join(lines)

    def generate_compact_status(self) -> str:
        """
        Generate compact one-line status for executive summaries.

        Returns:
            Compact status string (e.g., "Data sources: 5/7 operational (Steam ✅, SteamSpy ✅, ...)")
        """
        if not self.calls:
            return "Data sources: No APIs used"

        # Get unique APIs (deduplicate multiple calls to same API)
        api_status = {}
        for call in self.calls:
            if call.api_name not in api_status or call.status == APIStatus.SUCCESS:
                api_status[call.api_name] = call.status_emoji

        status_list = [f"{name} {emoji}" for name, emoji in api_status.items()]

        return f"**Data sources**: {len(self.successful_calls)}/{self.total_calls} operational ({', '.join(status_list)})"

    def get_summary_dict(self) -> Dict[str, Any]:
        """
        Get summary as dictionary for programmatic use.

        Returns:
            Dictionary with summary statistics
        """
        by_status = self.get_apis_by_status()

        return {
            'total_calls': self.total_calls,
            'successful': len(self.successful_calls),
            'failed': len(self.failed_calls),
            'success_rate': self.success_rate,
            'apis': {
                'success': [{'name': c.api_name, 'endpoint': c.endpoint} for c in by_status['success']],
                'failed': [{'name': c.api_name, 'endpoint': c.endpoint, 'error': c.error_message} for c in by_status['failed']],
                'skipped': [{'name': c.api_name, 'reason': c.error_message} for c in by_status['skipped']],
                'not_configured': [{'name': c.api_name} for c in by_status['not_configured']]
            },
            'data_quality': self._get_quality_rating()
        }

    def _get_quality_rating(self) -> str:
        """Get data quality rating based on success rate"""
        if self.success_rate >= 80:
            return "excellent"
        elif self.success_rate >= 60:
            return "good"
        elif self.success_rate >= 40:
            return "limited"
        else:
            return "poor"

    def reset(self):
        """Reset verifier for new report generation"""
        self.calls = []
        self.start_time = datetime.now()


# Example usage
if __name__ == "__main__":
    # Create verifier
    verifier = APIVerifier()

    # Simulate some API calls
    verifier.record_success("Steam Store API", "/api/appdetails", response_time_ms=234.5)
    verifier.record_success("Steam Reviews API", "/appreviews/{appid}", response_time_ms=456.2)
    verifier.record_failure("SteamSpy API", "/api.php?request=appdetails", "403 Forbidden - Network blocked")
    verifier.record_failure("RAWG API", "/api/games", "403 Forbidden - Network blocked")
    verifier.record_success("Claude API", "Messages endpoint", response_time_ms=1234.6)
    verifier.record_not_configured("YouTube API", "/v3/search")
    verifier.record_not_configured("Twitch API", "/helix/streams")

    # Generate status section
    print(verifier.generate_status_section(include_timing=True, detailed=True))
    print("\n" + "="*80 + "\n")
    print(verifier.generate_compact_status())
    print("\n" + "="*80 + "\n")

    # Get summary
    import json
    print(json.dumps(verifier.get_summary_dict(), indent=2))
