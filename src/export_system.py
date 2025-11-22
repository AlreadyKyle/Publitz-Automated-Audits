#!/usr/bin/env python3
"""
Export System - CSV and structured data exports
Provides downloadable exports for action items, contacts, and analysis data
"""

from typing import Dict, List, Any
import csv
import io
from datetime import datetime
from src.logger import get_logger

logger = get_logger(__name__)


class ExportSystem:
    """Handles all data exports for the audit system"""

    def __init__(self):
        logger.info("ExportSystem initialized")

    def export_action_items(self, structured_data: Dict[str, Any]) -> str:
        """
        Export all action items/recommendations to CSV

        Args:
            structured_data: Complete report structured data

        Returns:
            CSV string
        """
        logger.info("Exporting action items to CSV")

        output = io.StringIO()
        fieldnames = ['priority', 'category', 'action', 'impact', 'time_estimate', 'status']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        # Extract recommendations from all sections
        sections = structured_data.get('sections', [])

        for section in sections:
            section_name = section.get('name', 'Unknown')
            # TODO: Access recommendations from section objects
            # For now, placeholder

        # Placeholder data
        writer.writerow({
            'priority': 'High',
            'category': 'Store Page',
            'action': 'Add 3 more screenshots',
            'impact': 'High',
            'time_estimate': '1 hour',
            'status': 'Pending'
        })

        return output.getvalue()

    def export_curator_contacts(self, phase2_data: Dict[str, Any]) -> str:
        """
        Export Steam curator contact list to CSV

        Args:
            phase2_data: Phase 2 enrichment data

        Returns:
            CSV string
        """
        logger.info("Exporting curator contacts to CSV")

        curators = phase2_data.get('curators', {}).get('curators', [])

        if not curators:
            return "name,followers,focus,response_rate,priority,steam_url,contact_method\n"

        output = io.StringIO()
        fieldnames = ['name', 'followers', 'focus', 'response_rate', 'priority',
                     'estimated_reach', 'steam_url', 'contact_method', 'notes']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for curator in curators:
            writer.writerow({
                'name': curator.get('name', ''),
                'followers': curator.get('followers', 0),
                'focus': curator.get('focus', ''),
                'response_rate': curator.get('response_rate', ''),
                'priority': curator.get('priority', 0),
                'estimated_reach': curator.get('estimated_reach', 0),
                'steam_url': curator.get('steam_url', ''),
                'contact_method': curator.get('contact_method', ''),
                'notes': ''
            })

        logger.info(f"Exported {len(curators)} curator contacts")
        return output.getvalue()

    def export_streamer_contacts(self, phase2_data: Dict[str, Any]) -> str:
        """
        Export Twitch streamer contact list to CSV

        Args:
            phase2_data: Phase 2 enrichment data

        Returns:
            CSV string
        """
        logger.info("Exporting streamer contacts to CSV")

        streamers = phase2_data.get('twitch', {}).get('streamers', [])

        if not streamers:
            return "name,followers,avg_viewers,priority,roi_score,twitch_url,notes\n"

        output = io.StringIO()
        fieldnames = ['name', 'followers', 'avg_viewers', 'priority', 'roi_score',
                     'twitch_url', 'estimated_cost', 'notes']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for streamer in streamers:
            writer.writerow({
                'name': streamer.get('name', ''),
                'followers': streamer.get('followers', 0),
                'avg_viewers': streamer.get('avg_viewers', 0),
                'priority': streamer.get('priority', ''),
                'roi_score': streamer.get('roi_score', 0),
                'twitch_url': streamer.get('url', ''),
                'estimated_cost': streamer.get('estimated_cost', '$100-500'),
                'notes': ''
            })

        logger.info(f"Exported {len(streamers)} streamer contacts")
        return output.getvalue()

    def export_youtube_contacts(self, phase2_data: Dict[str, Any]) -> str:
        """
        Export YouTube channel contact list to CSV

        Args:
            phase2_data: Phase 2 enrichment data

        Returns:
            CSV string
        """
        logger.info("Exporting YouTube contacts to CSV")

        channels = phase2_data.get('youtube', {}).get('channels', [])

        if not channels:
            return "name,subscribers,avg_views,priority,roi_score,url,contact_method,notes\n"

        output = io.StringIO()
        fieldnames = ['name', 'subscribers', 'avg_views_per_video', 'priority',
                     'roi_score', 'url', 'contact_method', 'recommended_content', 'notes']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for channel in channels:
            contact_info = channel.get('contact_method', {})
            recommended_types = channel.get('recommended_video_types', [])

            writer.writerow({
                'name': channel.get('name', ''),
                'subscribers': channel.get('subscribers', 0),
                'avg_views_per_video': channel.get('avg_views_per_video', 0),
                'priority': channel.get('outreach_priority', ''),
                'roi_score': channel.get('roi_score', 0),
                'url': channel.get('url', ''),
                'contact_method': contact_info.get('primary_method', '') if isinstance(contact_info, dict) else contact_info,
                'recommended_content': ', '.join(recommended_types),
                'notes': ''
            })

        logger.info(f"Exported {len(channels)} YouTube contacts")
        return output.getvalue()

    def export_regional_pricing(self, phase2_data: Dict[str, Any]) -> str:
        """
        Export regional pricing recommendations to CSV

        Args:
            phase2_data: Phase 2 enrichment data

        Returns:
            CSV string
        """
        logger.info("Exporting regional pricing data to CSV")

        pricing_data = phase2_data.get('regional_pricing', {})
        recommended_prices = pricing_data.get('recommended_prices', {})

        if not recommended_prices:
            return "region,currency,recommended_price,market_size,ppp_adjusted\n"

        output = io.StringIO()
        fieldnames = ['region_code', 'region_name', 'currency', 'recommended_price',
                     'market_size', 'ppp_adjusted_price']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for region_code, region_data in recommended_prices.items():
            writer.writerow({
                'region_code': region_code,
                'region_name': region_data.get('name', ''),
                'currency': region_data.get('currency', ''),
                'recommended_price': f"{region_data.get('recommended_price', 0):.2f}",
                'market_size': region_data.get('market_size', ''),
                'ppp_adjusted_price': f"{region_data.get('ppp_adjusted', 0):.2f}"
            })

        logger.info(f"Exported {len(recommended_prices)} regional prices")
        return output.getvalue()

    def export_localization_roi(self, phase2_data: Dict[str, Any]) -> str:
        """
        Export localization ROI analysis to CSV

        Args:
            phase2_data: Phase 2 enrichment data

        Returns:
            CSV string
        """
        logger.info("Exporting localization ROI data to CSV")

        localization_data = phase2_data.get('localization', {})
        missing_languages = localization_data.get('missing_languages', [])

        if not missing_languages:
            return "language,cost,potential_revenue,roi_percent,priority,payback_units\n"

        output = io.StringIO()
        fieldnames = ['language_code', 'language', 'localization_cost', 'potential_revenue',
                     'roi_percent', 'priority', 'payback_units', 'market_reach_percent']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for lang in missing_languages:
            if lang.get('priority') in ['high', 'medium']:  # Only export viable options
                writer.writerow({
                    'language_code': lang.get('language_code', ''),
                    'language': lang.get('language', ''),
                    'localization_cost': f"${lang.get('localization_cost', 0):,}",
                    'potential_revenue': f"${lang.get('additional_revenue', 0):,.0f}",
                    'roi_percent': f"{lang.get('roi_percent', 0):.0f}%",
                    'priority': lang.get('priority', ''),
                    'payback_units': lang.get('payback_units', 0),
                    'market_reach_percent': f"{lang.get('market_reach_percent', 0):.0f}%"
                })

        logger.info(f"Exported {len([l for l in missing_languages if l.get('priority') in ['high', 'medium']])} localization opportunities")
        return output.getvalue()

    def export_subreddit_list(self, phase2_data: Dict[str, Any]) -> str:
        """
        Export Reddit subreddit list to CSV

        Args:
            phase2_data: Phase 2 enrichment data

        Returns:
            CSV string
        """
        logger.info("Exporting subreddit list to CSV")

        subreddits = phase2_data.get('reddit', {}).get('subreddits', [])

        if not subreddits:
            return "subreddit,subscribers,active_users,url,self_promotion_allowed,notes\n"

        output = io.StringIO()
        fieldnames = ['subreddit', 'subscribers', 'active_users', 'url',
                     'self_promotion_allowed', 'description', 'notes']

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for sub in subreddits:
            writer.writerow({
                'subreddit': f"r/{sub.get('name', '')}",
                'subscribers': sub.get('subscribers', 0),
                'active_users': sub.get('active_users', 0),
                'url': sub.get('url', ''),
                'self_promotion_allowed': 'Yes' if sub.get('self_promotion_allowed') else 'No',
                'description': sub.get('description', '')[:100],
                'notes': ''
            })

        logger.info(f"Exported {len(subreddits)} subreddits")
        return output.getvalue()

    def export_all_contacts(self, phase2_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Export all contact lists

        Args:
            phase2_data: Phase 2 enrichment data

        Returns:
            Dict of {filename: csv_content}
        """
        logger.info("Exporting all contact lists")

        return {
            'steam_curators.csv': self.export_curator_contacts(phase2_data),
            'twitch_streamers.csv': self.export_streamer_contacts(phase2_data),
            'youtube_channels.csv': self.export_youtube_contacts(phase2_data),
            'reddit_communities.csv': self.export_subreddit_list(phase2_data)
        }

    def export_all_analysis(self, phase2_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Export all analysis data

        Args:
            phase2_data: Phase 2 enrichment data

        Returns:
            Dict of {filename: csv_content}
        """
        logger.info("Exporting all analysis data")

        return {
            'regional_pricing.csv': self.export_regional_pricing(phase2_data),
            'localization_roi.csv': self.export_localization_roi(phase2_data)
        }

    def create_export_package(self, structured_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create complete export package with all CSV files

        Args:
            structured_data: Complete report structured data

        Returns:
            Dict of {filename: csv_content} for all exports
        """
        logger.info("Creating complete export package")

        exports = {}

        # Get Phase 2 data if available
        phase2_data = structured_data.get('phase2_data', {})

        if phase2_data:
            # Contact lists
            exports.update(self.export_all_contacts(phase2_data))

            # Analysis data
            exports.update(self.export_all_analysis(phase2_data))

        # Action items (always included)
        # exports['action_items.csv'] = self.export_action_items(structured_data)

        logger.info(f"Export package created with {len(exports)} files")

        return exports


# Convenience function
def create_csv_exports(structured_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Create all CSV exports from structured report data

    Args:
        structured_data: Complete report structured data

    Returns:
        Dict of {filename: csv_content}
    """
    exporter = ExportSystem()
    return exporter.create_export_package(structured_data)
