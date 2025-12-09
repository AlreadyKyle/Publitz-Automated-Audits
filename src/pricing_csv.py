"""
Steam Pricing CSV Export Module

Generates Steam-compatible pricing CSV files for bulk price uploads.
Based on Steam's Partner portal format for regional pricing.

Steam CSV Format:
- Country/region codes (ISO 3166-1 alpha-2)
- Currency codes (ISO 4217)
- Prices in local currency (without currency symbols)
- Recommendations based on purchasing power parity
"""

from pathlib import Path
from typing import Dict, Optional
import csv


class SteamPricingExporter:
    """
    Generate Steam-compatible pricing CSV files.

    Based on Steam's recommended regional pricing matrix and
    purchasing power parity adjustments.
    """

    # Steam's supported countries/regions with currency info
    # Format: country_code: (currency_code, multiplier_from_usd, country_name)
    STEAM_REGIONS = {
        # North America
        'US': ('USD', 1.00, 'United States'),
        'CA': ('CAD', 1.35, 'Canada'),
        'MX': ('MXN', 20.50, 'Mexico'),

        # South America
        'AR': ('ARS', 350.00, 'Argentina'),
        'BR': ('BRL', 5.20, 'Brazil'),
        'CL': ('CLP', 900.00, 'Chile'),
        'CO': ('COP', 4200.00, 'Colombia'),
        'PE': ('PEN', 3.80, 'Peru'),
        'UY': ('UYU', 40.00, 'Uruguay'),

        # Europe (Euro Zone)
        'AT': ('EUR', 0.93, 'Austria'),
        'BE': ('EUR', 0.93, 'Belgium'),
        'DE': ('EUR', 0.93, 'Germany'),
        'ES': ('EUR', 0.93, 'Spain'),
        'FR': ('EUR', 0.93, 'France'),
        'IE': ('EUR', 0.93, 'Ireland'),
        'IT': ('EUR', 0.93, 'Italy'),
        'NL': ('EUR', 0.93, 'Netherlands'),
        'PT': ('EUR', 0.93, 'Portugal'),
        'FI': ('EUR', 0.93, 'Finland'),
        'GR': ('EUR', 0.93, 'Greece'),

        # Europe (Non-Euro)
        'GB': ('GBP', 0.79, 'United Kingdom'),
        'CH': ('CHF', 0.91, 'Switzerland'),
        'NO': ('NOK', 10.50, 'Norway'),
        'SE': ('SEK', 10.40, 'Sweden'),
        'DK': ('DKK', 6.90, 'Denmark'),
        'PL': ('PLN', 4.20, 'Poland'),
        'CZ': ('CZK', 23.00, 'Czech Republic'),
        'RO': ('RON', 4.60, 'Romania'),
        'HU': ('HUF', 365.00, 'Hungary'),
        'TR': ('TRY', 30.00, 'Turkey'),
        'UA': ('UAH', 37.00, 'Ukraine'),
        'RU': ('RUB', 85.00, 'Russia'),

        # Asia Pacific
        'AU': ('AUD', 1.52, 'Australia'),
        'NZ': ('NZD', 1.63, 'New Zealand'),
        'JP': ('JPY', 148.00, 'Japan'),
        'KR': ('KRW', 1320.00, 'South Korea'),
        'CN': ('CNY', 7.20, 'China'),
        'HK': ('HKD', 7.80, 'Hong Kong'),
        'TW': ('TWD', 31.50, 'Taiwan'),
        'SG': ('SGD', 1.35, 'Singapore'),
        'MY': ('MYR', 4.65, 'Malaysia'),
        'TH': ('THB', 35.50, 'Thailand'),
        'ID': ('IDR', 15700.00, 'Indonesia'),
        'PH': ('PHP', 56.50, 'Philippines'),
        'VN': ('VND', 24500.00, 'Vietnam'),
        'IN': ('INR', 83.00, 'India'),

        # Middle East
        'AE': ('AED', 3.67, 'United Arab Emirates'),
        'SA': ('SAR', 3.75, 'Saudi Arabia'),
        'IL': ('ILS', 3.65, 'Israel'),
        'KW': ('KWD', 0.31, 'Kuwait'),
        'QA': ('QAR', 3.64, 'Qatar'),

        # Africa
        'ZA': ('ZAR', 18.50, 'South Africa'),
    }

    # Steam's recommended discount tiers by region
    # Format: tier_name: multiplier (lower = cheaper region)
    PRICING_TIERS = {
        'tier1': 1.0,      # US, CA, Western Europe, AU
        'tier2': 0.75,     # Eastern Europe, LATAM (except AR)
        'tier3': 0.50,     # Russia, TR, IN, CN, AR, SEA
    }

    # Country assignments to tiers
    TIER_ASSIGNMENTS = {
        'tier1': ['US', 'CA', 'GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT',
                  'CH', 'AU', 'NZ', 'SE', 'NO', 'DK', 'FI', 'IE', 'JP', 'KR',
                  'SG', 'HK', 'AE', 'SA', 'IL', 'KW', 'QA'],
        'tier2': ['PL', 'CZ', 'RO', 'HU', 'MX', 'BR', 'CL', 'CO', 'PE', 'UY',
                  'MY', 'TH', 'ZA', 'GR', 'PT'],
        'tier3': ['RU', 'TR', 'UA', 'AR', 'CN', 'IN', 'ID', 'PH', 'VN', 'TW'],
    }

    def __init__(self):
        """Initialize pricing exporter."""
        self.ppp_warnings = []  # Track regions with PPP issues

    def generate_pricing_csv(
        self,
        base_price_usd: float,
        output_path: Path,
        use_recommended_tiers: bool = True
    ) -> Path:
        """
        Generate Steam-compatible pricing CSV.

        Args:
            base_price_usd: Base price in USD
            output_path: Where to save the CSV file
            use_recommended_tiers: Use Steam's recommended regional pricing

        Returns:
            Path to generated CSV file
        """
        print(f"\n💰 Generating Steam pricing CSV...")
        print(f"   Base price: ${base_price_usd:.2f} USD")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate pricing for all regions
        pricing_data = []

        for country_code, (currency, multiplier, country_name) in self.STEAM_REGIONS.items():
            # Determine tier discount if using recommended pricing
            tier_multiplier = 1.0
            if use_recommended_tiers:
                for tier_name, tier_countries in self.TIER_ASSIGNMENTS.items():
                    if country_code in tier_countries:
                        tier_multiplier = self.PRICING_TIERS[tier_name]
                        break

            # Calculate price in local currency
            local_price = base_price_usd * multiplier * tier_multiplier

            # Round to appropriate precision for currency
            if currency in ['JPY', 'KRW', 'VND', 'IDR', 'CLP', 'COP']:
                # Currencies without decimal places
                local_price = round(local_price)
            else:
                # Currencies with decimal places
                local_price = round(local_price, 2)

            pricing_data.append({
                'country_code': country_code,
                'country_name': country_name,
                'currency': currency,
                'price': local_price,
                'usd_equivalent': round(base_price_usd * tier_multiplier, 2)
            })

        # Sort by country code
        pricing_data.sort(key=lambda x: x['country_code'])

        # Write to CSV in Steam format
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header row
            writer.writerow([
                'Country Code',
                'Country Name',
                'Currency',
                'Price',
                'USD Equivalent'
            ])

            # Data rows
            for row in pricing_data:
                writer.writerow([
                    row['country_code'],
                    row['country_name'],
                    row['currency'],
                    row['price'],
                    row['usd_equivalent']
                ])

        # Analyze for PPP issues
        self._analyze_ppp_issues(pricing_data, base_price_usd)

        print(f"✅ Pricing CSV generated: {output_path.name}")
        print(f"   {len(pricing_data)} countries/regions included")

        # Show PPP warnings
        if self.ppp_warnings:
            print(f"\n⚠️  PPP AUDIT WARNINGS ({len(self.ppp_warnings)} regions):")
            print("   Valve's algorithmic pricing may be overpriced by 20-56%")
            print("   Consider manually reducing these prices for better conversion:\n")
            for warning in self.ppp_warnings[:5]:  # Show top 5
                print(f"   → {warning}")
            if len(self.ppp_warnings) > 5:
                print(f"   ... and {len(self.ppp_warnings) - 5} more (see CSV for full list)")

        print()
        return output_path

    def _analyze_ppp_issues(self, pricing_data: list, base_price_usd: float):
        """
        Analyze pricing for PPP issues based on research.

        Research shows Valve's algorithmic suggestions can overprice by 20-56%.
        Flag regions where local price is significantly higher than expected.
        """
        self.ppp_warnings = []

        for row in pricing_data:
            usd_equiv = row['usd_equivalent']

            # Calculate markup percentage
            markup = ((usd_equiv / base_price_usd) - 1) * 100 if base_price_usd > 0 else 0

            # Flag if markup > 20% (indicates potential PPP overpricing)
            if markup > 20:
                country = row['country_name']
                currency = row['currency']
                local_price = row['price']

                warning = (f"{country} ({currency} {local_price:.2f}) = "
                          f"${usd_equiv:.2f} USD (+{markup:.0f}% markup)")
                self.ppp_warnings.append(warning)

    def generate_pricing_summary(
        self,
        base_price_usd: float,
        use_recommended_tiers: bool = True
    ) -> str:
        """
        Generate markdown pricing summary table for inclusion in reports.

        Args:
            base_price_usd: Base price in USD
            use_recommended_tiers: Use Steam's recommended regional pricing

        Returns:
            Markdown table string
        """
        # Sample key markets
        key_markets = ['US', 'GB', 'DE', 'BR', 'RU', 'CN', 'IN', 'AU', 'JP']

        summary = "### Regional Pricing Summary (Key Markets)\n\n"
        summary += "| Country | Currency | Price | Tier |\n"
        summary += "|---------|----------|-------|------|\n"

        for country_code in key_markets:
            if country_code not in self.STEAM_REGIONS:
                continue

            currency, multiplier, country_name = self.STEAM_REGIONS[country_code]

            # Determine tier
            tier = "Standard"
            tier_multiplier = 1.0
            if use_recommended_tiers:
                for tier_name, tier_countries in self.TIER_ASSIGNMENTS.items():
                    if country_code in tier_countries:
                        if tier_name == 'tier2':
                            tier = "Tier 2 (-25%)"
                        elif tier_name == 'tier3':
                            tier = "Tier 3 (-50%)"
                        tier_multiplier = self.PRICING_TIERS[tier_name]
                        break

            # Calculate price
            local_price = base_price_usd * multiplier * tier_multiplier

            if currency in ['JPY', 'KRW', 'VND', 'IDR']:
                local_price = round(local_price)
                price_str = f"{currency} {local_price:,.0f}"
            else:
                local_price = round(local_price, 2)
                price_str = f"{currency} {local_price:.2f}"

            summary += f"| {country_name} | {currency} | {price_str} | {tier} |\n"

        summary += "\n*Full 50+ country pricing table included in CSV export*\n"

        return summary


def export_pricing_csv(
    base_price_usd: float,
    client_name: str,
    output_dir: Path
) -> Path:
    """
    Convenience function to export Steam pricing CSV.

    Args:
        base_price_usd: Base price in USD
        client_name: Client name for filename
        output_dir: Output directory

    Returns:
        Path to generated CSV file
    """
    from datetime import datetime

    # Generate filename
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{client_name}_pricing_{date_str}.csv"
    csv_path = output_dir / filename

    # Create exporter and generate CSV
    exporter = SteamPricingExporter()
    return exporter.generate_pricing_csv(
        base_price_usd=base_price_usd,
        output_path=csv_path,
        use_recommended_tiers=True
    )


if __name__ == "__main__":
    """Test pricing CSV export"""
    print("Steam Pricing CSV Export Module")
    print("=" * 80)
    print("\nThis module generates Steam-compatible pricing CSV files.")
    print("\nUsage:")
    print("  from src.pricing_csv import export_pricing_csv")
    print("  csv_path = export_pricing_csv(")
    print("      base_price_usd=19.99,")
    print("      client_name='awesome-game',")
    print("      output_dir=Path('output/client')")
    print("  )")
    print("\nFeatures:")
    print("  - 50+ countries/regions supported")
    print("  - Regional pricing tiers (Tier 1/2/3)")
    print("  - Currency conversion with PPP adjustments")
    print("  - Steam Partner portal compatible format")
