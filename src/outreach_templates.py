#!/usr/bin/env python3
"""
Outreach Templates - Email and message templates for marketing outreach
Provides customizable templates for curators, streamers, YouTubers, and press
"""

from typing import Dict, Any
from datetime import datetime
from src.logger import get_logger

logger = get_logger(__name__)


class OutreachTemplates:
    """Generate personalized outreach templates"""

    def __init__(self):
        logger.info("OutreachTemplates initialized")

    def generate_curator_email(self, game_data: Dict[str, Any],
                               curator_name: str,
                               personalization: str = "") -> str:
        """
        Generate Steam curator outreach email

        Args:
            game_data: Game information
            curator_name: Name of the curator
            personalization: Optional personalized message

        Returns:
            Email template string
        """
        game_name = game_data.get('name', 'Our Game')
        genres = ', '.join([g.get('description', '') for g in game_data.get('genres', [])])
        short_description = game_data.get('short_description', '')[:200]

        template = f"""Subject: {game_name} - {genres} Game Key Request

Hi {curator_name},

{personalization if personalization else f"I hope this email finds you well. I've been following your curator page and really appreciate your coverage of {genres.lower()} games."}

I'm reaching out to offer you an early key for our upcoming game, **{game_name}**.

**About {game_name}:**
{short_description}

**Why I think it's a fit for your audience:**
- Genre: {genres}
- Unique gameplay mechanics
- Strong community response in playtesting
- Launching on Steam in [LAUNCH DATE]

If you're interested, I'd be happy to send you a key and any additional materials you might need. No pressure to cover it - I'd just love for you to check it out.

You can find more info on our Steam page: {game_data.get('steam_url', '[STEAM URL]')}

Thanks for your time and for all the great work you do showcasing indie games!

Best regards,
[YOUR NAME]
[YOUR STUDIO]
[CONTACT EMAIL]

P.S. Feel free to reach out if you have any questions or need specific assets for your coverage.
"""
        return template

    def generate_streamer_email(self, game_data: Dict[str, Any],
                               streamer_name: str,
                               platform: str = "Twitch",
                               personalization: str = "") -> str:
        """
        Generate Twitch/YouTube streamer outreach email

        Args:
            game_data: Game information
            streamer_name: Name of the streamer
            platform: "Twitch" or "YouTube"
            personalization: Optional personalized message

        Returns:
            Email template string
        """
        game_name = game_data.get('name', 'Our Game')
        genres = ', '.join([g.get('description', '') for g in game_data.get('genres', [])])

        template = f"""Subject: {game_name} - Key Offer for {platform} Stream

Hi {streamer_name},

{personalization if personalization else f"I'm a big fan of your {platform} channel, especially your {genres.lower()} content!"}

I'm the developer of **{game_name}**, a {genres} game launching soon on Steam, and I think it would be perfect for your audience.

**What makes it stream-friendly:**
- [GAMEPLAY HOOK - e.g., "Procedurally generated runs with tons of variety"]
- [VIEWER ENGAGEMENT - e.g., "Chat-friendly pacing with decision points"]
- [UNIQUE FEATURE - e.g., "Unique art style that looks great on stream"]

**What I'm offering:**
✅ Early access key before launch
✅ High-res assets and overlays for your stream
✅ Direct line to the dev (me!) for any questions
✅ No obligations - stream it if you enjoy it!

I'm not looking for sponsored content - just hoping you'll genuinely enjoy the game and maybe share it with your community if it clicks.

Interested? I can send you a key right away.

Steam page: {game_data.get('steam_url', '[STEAM URL]')}

Thanks for considering it, and keep up the awesome streams!

Best,
[YOUR NAME]
[YOUR STUDIO]
[CONTACT EMAIL]
"""
        return template

    def generate_youtube_email(self, game_data: Dict[str, Any],
                              channel_name: str,
                              video_type: str = "review",
                              personalization: str = "") -> str:
        """
        Generate YouTube channel outreach email

        Args:
            game_data: Game information
            channel_name: Name of the YouTube channel
            video_type: Type of content ("review", "let's play", "first impressions")
            personalization: Optional personalized message

        Returns:
            Email template string
        """
        game_name = game_data.get('name', 'Our Game')
        genres = ', '.join([g.get('description', '') for g in game_data.get('genres', [])])

        video_suggestions = {
            'review': 'an honest review',
            'lets_play': 'a let\'s play series',
            'first_impressions': 'a first impressions video',
            'gameplay': 'gameplay coverage'
        }

        suggested_content = video_suggestions.get(video_type, 'coverage')

        template = f"""Subject: {game_name} - YouTube Key Offer

Hi {channel_name} team,

{personalization if personalization else f"I've been watching your channel and love your {genres.lower()} game coverage!"}

I'm developing **{game_name}**, a {genres} game, and I think your audience would really enjoy it. I'd love to offer you an early key.

**Game Details:**
- Genre: {genres}
- Platform: Steam (PC)
- Launch: [LAUNCH DATE]
- Key Features: [LIST 2-3 UNIQUE FEATURES]

**Why I think it fits your channel:**
[EXPLAIN WHY IT'S A GOOD FIT FOR THEIR CONTENT STYLE]

**What I can provide:**
- Early access key
- Press kit with high-res screenshots and trailers
- Direct access to me for any questions
- B-roll footage if needed

I'm thinking it could work well for {suggested_content}, but I'm open to whatever format works best for your channel.

No strings attached - I just want you to check it out and share your honest thoughts if you enjoy it.

Steam page: {game_data.get('steam_url', '[STEAM URL]')}

Let me know if you're interested, and I'll send everything over right away!

Thanks,
[YOUR NAME]
[YOUR STUDIO]
[CONTACT EMAIL]
[TWITTER/DISCORD]
"""
        return template

    def generate_press_email(self, game_data: Dict[str, Any],
                            publication_name: str,
                            hook: str = "") -> str:
        """
        Generate press/media outreach email

        Args:
            game_data: Game information
            publication_name: Name of the publication
            hook: News hook or angle

        Returns:
            Email template string
        """
        game_name = game_data.get('name', 'Our Game')
        genres = ', '.join([g.get('description', '') for g in game_data.get('genres', [])])

        template = f"""Subject: {game_name} - {hook if hook else 'New ' + genres + ' Game Announcement'}

Hi {publication_name} team,

{hook if hook else f"I wanted to share our newly announced {genres} game with you."}

**{game_name}** is [ELEVATOR PITCH - 1-2 sentences describing the game and what makes it unique].

**Key Details:**
- Genre: {genres}
- Platform: Steam (PC) [+ other platforms if applicable]
- Release: [LAUNCH DATE or LAUNCH WINDOW]
- Price: [PRICE]
- Developer: [STUDIO NAME]

**What makes it newsworthy:**
- [UNIQUE ANGLE #1]
- [UNIQUE ANGLE #2]
- [UNIQUE ANGLE #3]

**Available Assets:**
- Press release
- High-resolution screenshots
- Gameplay trailer
- Developer quotes
- Review keys (available upon request)

I've attached our press kit, and you can find more details on our Steam page: {game_data.get('steam_url', '[STEAM URL]')}

Would you be interested in coverage? I'm happy to arrange an interview or provide any additional information you need.

Thank you for considering {game_name}!

Best regards,
[YOUR NAME]
[YOUR TITLE]
[YOUR STUDIO]
[CONTACT EMAIL]
[PHONE]
[PRESS KIT URL]
"""
        return template

    def generate_follow_up_email(self, recipient_name: str,
                                original_date: str,
                                game_name: str) -> str:
        """
        Generate follow-up email template

        Args:
            recipient_name: Name of recipient
            original_date: Date of original email
            game_name: Name of the game

        Returns:
            Follow-up email template
        """
        template = f"""Subject: Re: {game_name} - Following Up

Hi {recipient_name},

I hope this email finds you well! I wanted to follow up on my email from {original_date} about {game_name}.

I completely understand if you're busy or the game isn't a fit for your content - no worries at all! I just wanted to make sure my original message didn't get lost.

If you're still interested, I'm happy to send over a key and any materials you need. If not, I totally understand and wish you all the best with your channel/publication.

Thanks again for your time!

Best,
[YOUR NAME]
[YOUR STUDIO]
"""
        return template

    def generate_template_package(self, game_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate complete template package

        Args:
            game_data: Game information

        Returns:
            Dict of {template_name: template_content}
        """
        logger.info("Generating complete template package")

        return {
            'curator_template.txt': self.generate_curator_email(game_data, "[CURATOR NAME]"),
            'twitch_streamer_template.txt': self.generate_streamer_email(game_data, "[STREAMER NAME]", "Twitch"),
            'youtube_template.txt': self.generate_youtube_email(game_data, "[CHANNEL NAME]", "review"),
            'press_template.txt': self.generate_press_email(game_data, "[PUBLICATION NAME]"),
            'follow_up_template.txt': self.generate_follow_up_email("[RECIPIENT NAME]", "[DATE]", game_data.get('name', 'Your Game'))
        }


# Convenience function
def generate_outreach_templates(game_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate all outreach templates

    Args:
        game_data: Game information

    Returns:
        Dict of {template_filename: template_content}
    """
    templates = OutreachTemplates()
    return templates.generate_template_package(game_data)
