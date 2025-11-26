#!/usr/bin/env python3
"""
Configuration Loader - Loads business rules from YAML config file

This module provides access to all business logic thresholds and rules
from config/business_rules.yaml
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Loads and provides access to business rules configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            # Default: look for config/business_rules.yaml relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / 'config' / 'business_rules.yaml'
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                "Please ensure config/business_rules.yaml exists."
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML config: {e}")
    
    def get(self, *keys, default=None):
        """
        Get configuration value by dotted path.
        
        Args:
            *keys: Sequence of keys to navigate config dict
            default: Default value if path not found
        
        Returns:
            Configuration value or default
        
        Example:
            config.get('pricing', 'catastrophic_threshold')  # returns 2.00
            config.get('scoring', 'hard_caps', 'enable')  # returns True
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    # ========================================================================
    # PRICING CONFIGURATION
    # ========================================================================
    
    def get_catastrophic_threshold(self) -> float:
        """Get catastrophic pricing threshold ($2.00)"""
        return self.get('pricing', 'catastrophic_threshold', default=2.00)
    
    def get_optimal_price_range(self, category='indie') -> Dict[str, float]:
        """
        Get optimal price range for category.
        
        Args:
            category: 'indie' or 'aaa'
        
        Returns:
            {'min': float, 'max': float}
        """
        min_key = f'{category}_min'
        max_key = f'{category}_max'
        return {
            'min': self.get('pricing', 'optimal_range', min_key, default=4.99),
            'max': self.get('pricing', 'optimal_range', max_key, default=29.99)
        }
    
    def get_price_severity_level(self, price: float) -> Optional[Dict[str, Any]]:
        """
        Get severity level for a given price.
        
        Args:
            price: Game price in USD
        
        Returns:
            Severity level dict or None
        """
        levels = self.get('pricing', 'severity_levels', default={})
        for level_name, level_data in levels.items():
            if price >= level_data['min'] and price <= level_data['max']:
                return {
                    'level': level_name,
                    **level_data
                }
        return None
    
    def get_competitor_threshold(self, threshold_type: str) -> float:
        """
        Get competitor comparison threshold.
        
        Args:
            threshold_type: 'severe_underpricing', 'moderate_underpricing', etc.
        
        Returns:
            Threshold value
        """
        return self.get('pricing', 'competitor_comparison', threshold_type, default=1.0)
    
    # ========================================================================
    # GENERIC DETECTION CONFIGURATION
    # ========================================================================
    
    def get_generic_threshold(self, category: str) -> float:
        """
        Get generic detection threshold for category.
        
        Args:
            category: 'subreddits', 'influencers', 'curators', 'tags'
        
        Returns:
            Threshold value (0.0-1.0)
        """
        return self.get('generic_detection', category, 'generic_threshold', default=0.6)
    
    def get_generic_penalty(self, category: str, severity: str) -> int:
        """
        Get penalty points for generic data.
        
        Args:
            category: 'subreddits', 'influencers', 'curators', 'tags'
            severity: 'penalty_severe', 'penalty_moderate', 'penalty_minor'
        
        Returns:
            Penalty points
        """
        return self.get('generic_detection', category, severity, default=0)
    
    def get_min_specific_influencers(self) -> int:
        """Get minimum number of specific influencers required"""
        return self.get('generic_detection', 'influencers', 'min_specific', default=3)
    
    # ========================================================================
    # SCORING CONFIGURATION
    # ========================================================================
    
    def is_hard_caps_enabled(self) -> bool:
        """Check if score capping is enabled"""
        return self.get('scoring', 'hard_caps', 'enable', default=True)
    
    def is_revenue_based_scoring_enabled(self) -> bool:
        """Check if revenue-based scoring is enabled"""
        return self.get('scoring', 'hard_caps', 'revenue_based', default=True)
    
    def get_review_quality_threshold(self, quality_level: str) -> int:
        """
        Get review quality threshold.
        
        Args:
            quality_level: 'excellent', 'good', 'acceptable', 'poor'
        
        Returns:
            Threshold percentage
        """
        key = f'{quality_level}_threshold'
        return self.get('scoring', 'review_quality', key, default=70)
    
    def get_revenue_tier_threshold(self, tier: int) -> int:
        """
        Get minimum revenue for tier.
        
        Args:
            tier: 1-5
        
        Returns:
            Minimum revenue in USD
        """
        key = f'tier_{tier}_min'
        return self.get('scoring', 'revenue_tiers', key, default=0)
    
    # ========================================================================
    # COMMUNITY REACH CONFIGURATION
    # ========================================================================
    
    def get_community_weights(self) -> Dict[str, float]:
        """Get community reach component weights"""
        return {
            'subreddits': self.get('community', 'weights', 'subreddits', default=0.4),
            'influencers': self.get('community', 'weights', 'influencers', default=0.4),
            'curators': self.get('community', 'weights', 'curators', default=0.2)
        }
    
    def get_community_base_score(self, component: str) -> int:
        """
        Get base score for community component.
        
        Args:
            component: 'subreddits', 'influencers', 'curators'
        
        Returns:
            Base score (0-100)
        """
        return self.get('community', 'base_scores', component, default=75)
    
    # ========================================================================
    # DATA CONSISTENCY CONFIGURATION
    # ========================================================================
    
    def get_typical_review_rate(self) -> Dict[str, float]:
        """Get typical review rate range"""
        return {
            'min': self.get('data_consistency', 'review_rate', 'typical_min', default=0.02),
            'max': self.get('data_consistency', 'review_rate', 'typical_max', default=0.05)
        }
    
    def get_suspicious_review_rate(self) -> float:
        """Get suspicious review rate threshold"""
        return self.get('data_consistency', 'review_rate', 'suspicious_high', default=0.15)
    
    def get_min_daily_revenue(self) -> float:
        """Get minimum expected daily revenue"""
        return self.get('data_consistency', 'revenue', 'min_daily_revenue', default=1.00)
    
    # ========================================================================
    # REPORT GENERATION CONFIGURATION
    # ========================================================================
    
    def get_word_count_range(self, tier: int) -> Dict[str, int]:
        """
        Get word count range for tier.
        
        Args:
            tier: 1, 2, or 3
        
        Returns:
            {'min': int, 'max': int}
        """
        return {
            'min': self.get('report', 'word_counts', f'tier_{tier}_min', default=800),
            'max': self.get('report', 'word_counts', f'tier_{tier}_max', default=2000)
        }
    
    def get_minimum_data_completeness(self) -> int:
        """Get minimum data completeness percentage for quality report"""
        return self.get('report', 'quality', 'minimum_data_completeness', default=60)


# Global config instance (lazy loaded)
_config_instance = None


def get_config() -> ConfigLoader:
    """Get global configuration instance (singleton pattern)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader()
    return _config_instance


# Test the configuration loader
if __name__ == "__main__":
    print("="*80)
    print("CONFIGURATION LOADER TEST")
    print("="*80 + "\n")
    
    try:
        config = ConfigLoader()
        
        print("✅ Configuration loaded successfully\n")
        
        # Test pricing config
        print("Pricing Configuration:")
        print(f"  Catastrophic threshold: ${config.get_catastrophic_threshold():.2f}")
        print(f"  Optimal range (indie): ${config.get_optimal_price_range('indie')['min']:.2f}-${config.get_optimal_price_range('indie')['max']:.2f}")
        
        # Test generic detection
        print("\nGeneric Detection:")
        print(f"  Subreddit threshold: {config.get_generic_threshold('subreddits')*100:.0f}%")
        print(f"  Severe penalty: {config.get_generic_penalty('subreddits', 'penalty_severe')} points")
        
        # Test scoring
        print("\nScoring:")
        print(f"  Hard caps enabled: {config.is_hard_caps_enabled()}")
        print(f"  Excellent review threshold: {config.get_review_quality_threshold('excellent')}%")
        
        # Test community
        print("\nCommunity Reach:")
        weights = config.get_community_weights()
        print(f"  Weights: Subreddits={weights['subreddits']*100:.0f}%, Influencers={weights['influencers']*100:.0f}%, Curators={weights['curators']*100:.0f}%")
        
        # Test data consistency
        print("\nData Consistency:")
        review_rate = config.get_typical_review_rate()
        print(f"  Typical review rate: {review_rate['min']*100:.0f}%-{review_rate['max']*100:.0f}%")
        
        print("\n" + "="*80)
        print("ALL CONFIGURATION VALUES LOADED SUCCESSFULLY")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        import traceback
        traceback.print_exc()
