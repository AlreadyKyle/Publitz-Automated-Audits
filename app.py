import streamlit as st
import os
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from src.ai_generator import AIGenerator
from src.game_search import GameSearch
from src.steamdb_scraper import SteamDBScraper
from src.pdf_generator import create_downloadable_pdf
from src.logger import get_logger, setup_logger
from src.export_system import create_csv_exports
from src.outreach_templates import generate_outreach_templates
from src.exceptions import (
    PublitzError,
    InvalidSteamURLError,
    GameNotFoundError,
    SteamAPIError,
    AuthenticationError,
    AIGenerationError,
    RateLimitError,
    TimeoutError,
    PDFGenerationError
)
from src.data_validation import validate_game_data, validate_sales_data, validate_competitor_data

# Load environment variables from .env file
load_dotenv()

# Initialize logger
setup_logger(level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="Publitz Automated Audits",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Streamlit secrets into environment variables for compatibility
# This allows os.getenv() to work with both .env files and Streamlit Cloud secrets
if hasattr(st, 'secrets'):
    try:
        for key, value in st.secrets.items():
            if key not in os.environ:
                os.environ[key] = str(value)
    except Exception:
        pass  # Secrets may not be configured yet

# Initialize session state
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'game_name' not in st.session_state:
    st.session_state.game_name = None
if 'report_type' not in st.session_state:
    st.session_state.report_type = None
if 'num_competitors' not in st.session_state:
    st.session_state.num_competitors = 0
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = None
if 'game_data' not in st.session_state:
    st.session_state.game_data = None
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'audit_results' not in st.session_state:
    st.session_state.audit_results = None
if 'structured_data' not in st.session_state:
    st.session_state.structured_data = None

def main():
    # Header
    st.title("📊 Publitz Automated Game Audits")

    # If report is generated, show it prominently and collapse input form
    if st.session_state.report_generated:
        col_title, col_button = st.columns([4, 1])
        with col_title:
            st.markdown(f"**Current Report:** {st.session_state.game_name}")
        with col_button:
            if st.button("🔄 New Report", type="primary", use_container_width=True, key="header_new_report"):
                st.session_state.report_generated = False
                st.session_state.report_data = None
                st.session_state.game_name = None
                st.session_state.generating = False
                st.rerun()
    else:
        st.markdown("Paste a Steam game URL to generate a professional audit report")

    st.markdown("---")

    # Collapse input form when report is shown, expand when generating new report
    input_expanded = not st.session_state.report_generated
    input_container = st.expander("🎮 Generate Audit Report", expanded=input_expanded)

    with input_container:
        # API Key input (can be hidden in sidebar or environment variable)
        api_key = os.getenv("ANTHROPIC_API_KEY", "")

        if not api_key:
            with st.expander("⚙️ API Configuration", expanded=True):
                api_key = st.text_input(
                    "Anthropic API Key",
                    type="password",
                    help="Enter your Anthropic API key. Get one at https://console.anthropic.com/",
                    key="api_key_input"
                )

                if not api_key:
                    logger.info("User prompted for API key")
                    st.warning("⚠️ Please enter your Anthropic API Key to continue")
                    st.info("💡 **Tip**: Set ANTHROPIC_API_KEY environment variable to skip this step")
                    st.stop()

        # Validate API key format (basic check)
        if api_key:
            api_key = api_key.strip()
            if len(api_key) < 20:
                logger.warning("Invalid API key format provided")
                st.error("❌ Invalid API key format. Please check your API key.")
                st.info("💡 API keys start with 'sk-ant-' and are much longer")
                st.stop()

        # Main input - Steam URL
        st.markdown("### 🎮 Enter Steam Game URL")

        steam_url = st.text_input(
            "Steam Store URL",
            placeholder="https://store.steampowered.com/app/12345/Game_Name/",
            help="Paste the full URL from Steam store page",
            label_visibility="collapsed",
            key="steam_url_input"
        )

        # Example URLs
        with st.expander("📝 Example URLs"):
            st.code("https://store.steampowered.com/app/292030/The_Witcher_3_Wild_Hunt/", language="text")
            st.code("https://store.steampowered.com/app/730/CounterStrike_2/", language="text")
            st.code("https://store.steampowered.com/app/570/Dota_2/", language="text")

        # Generate button
        # Phase 2.1 & 2.4: Disable button during generation and show state
        button_text = "⏳ Generating Report..." if st.session_state.generating else "🚀 Generate Audit Report"

        # Callback to set generating state immediately when button is clicked
        def start_generation():
            st.session_state.generating = True

        generate_button = st.button(
            button_text,
            type="primary",
            use_container_width=True,
            key="generate_btn",
            disabled=st.session_state.generating,
            on_click=start_generation
        )

    # Only generate if button clicked and not already generated
    if generate_button and not st.session_state.report_generated:
        if not steam_url:
            st.error("❌ Please enter a Steam URL")
            st.stop()

        # Phase 2.1: State is now set via button callback
        try:
            # Initialize components
            with st.spinner("Initializing components..."):
                game_search = GameSearch()
                steamdb_scraper = SteamDBScraper()

                # Initialize AI generator with optional multi-model ensemble support
                openai_key = os.getenv("OPENAI_API_KEY")
                google_key = os.getenv("GOOGLE_API_KEY")
                ai_generator = AIGenerator(
                    api_key,
                    openai_api_key=openai_key,
                    google_api_key=google_key
                )

            # Progress tracking
            progress_bar = st.progress(0, text="Starting...")

            # Phase 2.2: Step 1 - Parse URL and get game data
            logger.info(f"Starting report generation for URL: {steam_url}")
            progress_bar.progress(10, text="🔍 Fetching game data from Steam...")
            with st.spinner("🔍 Fetching game data from Steam..."):
                game_data = game_search.get_game_from_url(steam_url)

            if not game_data:
                logger.error("Game data not returned from URL")
                st.error("❌ Invalid Steam URL or game not found. Please check the URL and try again.")
                st.stop()

            game_name = game_data.get('name', 'Unknown Game')
            logger.info(f"Successfully fetched game: {game_name}")

            # FIX: Validate and sanitize game data to ensure consistent types
            game_data = validate_game_data(game_data)

            st.success(f"✅ Found game: **{game_name}**")
            progress_bar.progress(20, text="🔎 Detecting launch status...")

            # Phase 2.2: Step 2 - Auto-detect launch status
            with st.spinner("🔎 Detecting launch status..."):
                report_type = game_search.detect_launch_status(game_data)

            # Show detected status
            status_col1, status_col2 = st.columns([1, 3])
            with status_col1:
                if report_type == "Pre-Launch":
                    st.info(f"📅 **Detected**: {report_type}")
                else:
                    st.success(f"🚀 **Detected**: {report_type}")
            with status_col2:
                st.caption(f"Release Date: {game_data.get('release_date', 'Unknown')}")

            progress_bar.progress(30, text="🔍 Finding competitor games...")

            # Phase 2.2: Step 3 - Find competitor games
            with st.spinner("🔍 Finding competitor games..."):
                competitor_data = game_search.find_competitors(game_data, min_competitors=3, max_competitors=10)
            num_competitors = len(competitor_data)

            if num_competitors == 0:
                progress_bar.progress(40, text="🔍 Expanding competitor search...")
                with st.spinner("🔍 Expanding competitor search..."):
                    competitor_data = game_search.find_competitors_broad(game_data, min_competitors=5)
                    num_competitors = len(competitor_data)

            st.success(f"✅ Found {num_competitors} competitor games")
            progress_bar.progress(50, text="📊 Gathering Steam market data...")

            # Phase 2.2: Step 4 - Gather Steam data
            with st.spinner("📊 Gathering Steam market data..."):
                sales_data = steamdb_scraper.get_sales_data(game_data['app_id'], game_name=game_name)

                # FIX: Validate and sanitize sales data to ensure consistent types
                sales_data = validate_sales_data(sales_data)

                # Get review velocity data
                review_stats = steamdb_scraper.get_review_stats(game_data['app_id'])
                # Analyze capsule image for CTR optimization
                capsule_url = game_data.get('capsule_images', {}).get('capsule_main')
                if capsule_url:
                    capsule_analysis = ai_generator.analyze_capsule_image(capsule_url, game_name)
                else:
                    capsule_analysis = None
            progress_bar.progress(65, text="📊 Analyzing competitor performance...")

            # Phase 2.2: Step 5 - Gather competitor Steam data
            with st.spinner("📊 Analyzing competitor performance..."):
                # FIX: Validate all competitor data for consistent types
                competitor_data = validate_competitor_data(competitor_data)

                for competitor in competitor_data:
                    try:
                        competitor['steam_data'] = steamdb_scraper.get_sales_data(
                            competitor['app_id'],
                            game_name=competitor.get('name', 'Unknown')
                        )
                    except Exception as e:
                        print(f"Warning: Failed to get data for competitor {competitor.get('name', 'Unknown')}: {e}")
                        competitor['steam_data'] = {}

            # Phase 3: Multi-Pass AI System - Draft → Audit → Enhanced Final
            progress_bar.progress(70, text="🤖 Step 1/3: Generating initial draft...")

            with st.spinner("🤖 Step 1/3: Generating initial draft report..."):
                # Draft phase - shown to user
                pass

            progress_bar.progress(80, text="🔍 Step 2/3: AI auditing for accuracy...")

            with st.spinner("🔍 Step 2/3: AI self-auditing for accuracy issues..."):
                # Audit phase - checking for errors
                pass

            progress_bar.progress(90, text="✨ Step 3/3: Generating enhanced final report...")

            with st.spinner("✨ Step 3/3: Multi-pass AI analysis with vision + corrections... (this may take 4-5 minutes)"):
                # Use enhanced report system: Structured analysis + AI insights
                from src.report_integration import create_report_with_ai

                report_data, report_metadata = create_report_with_ai(
                    game_data,
                    sales_data,
                    competitor_data,
                    steamdb_data=sales_data,
                    report_type=report_type,
                    ai_generator=ai_generator,
                    review_stats=review_stats,
                    capsule_analysis=capsule_analysis
                )

                # Extract audit results from metadata
                audit_results = report_metadata.get('audit_results')

            progress_bar.progress(100, text="✅ Report generated successfully!")

            # Store in session state
            logger.info(f"Report generation completed successfully for {game_name}")
            st.session_state.report_generated = True
            st.session_state.report_data = report_data
            st.session_state.audit_results = audit_results  # Phase 3: Store audit results
            st.session_state.structured_data = report_metadata  # Phase 3: Store structured data for exports
            st.session_state.game_name = game_name
            st.session_state.report_type = report_type
            st.session_state.num_competitors = num_competitors
            st.session_state.sales_data = sales_data
            st.session_state.game_data = game_data

            # Phase 2.1: Reset generating state
            st.session_state.generating = False

            # Clear progress bar
            time.sleep(0.5)
            progress_bar.empty()

            # Force rerun to display results
            st.rerun()

        except InvalidSteamURLError as e:
            # Reset generating state on error
            st.session_state.generating = False
            logger.warning(f"Invalid Steam URL provided: {steam_url}")
            st.error(f"❌ {e.user_message}")
            st.info("💡 **Valid URL format**: `https://store.steampowered.com/app/12345/Game_Name/`")
            with st.expander("📝 Example URLs"):
                st.code("https://store.steampowered.com/app/292030/The_Witcher_3_Wild_Hunt/")
                st.code("https://store.steampowered.com/app/730/CounterStrike_2/")
            st.stop()

        except GameNotFoundError as e:
            st.session_state.generating = False
            logger.error(f"Game not found: {e.app_id}")
            st.error(f"❌ {e.user_message}")
            st.warning("🔍 **Possible reasons:**")
            st.markdown("""
            - The game is private or delisted
            - The URL contains an incorrect App ID
            - The game is region-locked
            """)
            st.stop()

        except AuthenticationError as e:
            st.session_state.generating = False
            logger.error(f"Authentication failed for {e.service}")
            st.error(f"❌ {e.user_message}")
            st.info(f"💡 **Solution**: Check your {e.service} API key in the configuration or .env file")
            st.stop()

        except AIGenerationError as e:
            st.session_state.generating = False
            logger.error(f"AI generation failed: {e.message}", exc_info=True)
            st.error(f"❌ {e.user_message}")
            st.warning("🔄 **Try these solutions:**")
            st.markdown("""
            - Verify your Anthropic API key is valid
            - Check your API usage limits at console.anthropic.com
            - Wait a moment and try again
            """)
            if e.recoverable:
                if st.button("🔄 Retry Generation"):
                    st.rerun()
            st.stop()

        except RateLimitError as e:
            st.session_state.generating = False
            logger.warning(f"Rate limit exceeded for {e.service}")
            st.warning(f"⏱️ {e.user_message}")
            if e.retry_after:
                st.info(f"💡 Please wait {e.retry_after} seconds before trying again")
            else:
                st.info("💡 Please wait a few moments before trying again")
            st.stop()

        except TimeoutError as e:
            st.session_state.generating = False
            logger.error(f"Timeout during {e.operation}")
            st.error(f"⏱️ {e.user_message}")
            st.info("💡 This may be due to slow network connection or Steam servers being busy")
            if st.button("🔄 Try Again"):
                st.rerun()
            st.stop()

        except SteamAPIError as e:
            st.session_state.generating = False
            logger.error(f"Steam API error: {e.message}", exc_info=True)
            st.error(f"❌ {e.user_message}")
            st.warning("🔄 **Try these solutions:**")
            st.markdown("""
            - Check if the Steam URL is correct
            - Try again in a few moments (Steam API may be temporarily unavailable)
            - Verify the game is publicly accessible
            """)
            st.stop()

        except PublitzError as e:
            # Catch all other custom errors
            st.session_state.generating = False
            logger.error(f"Publitz error: {e.message}", exc_info=True)
            st.error(f"❌ {e.user_message}")
            if e.recoverable:
                if st.button("🔄 Try Again"):
                    st.rerun()
            with st.expander("🔍 Technical Details"):
                st.code(e.message)
            st.stop()

        except Exception as e:
            # Catch-all for unexpected errors
            st.session_state.generating = False
            logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
            st.error("❌ An unexpected error occurred")
            st.warning("🛠️ **Please report this error:**")
            with st.expander("🔍 Error Details"):
                st.exception(e)
            st.info("💡 Try refreshing the page or contact support if the issue persists")
            st.stop()

    # Display results if report has been generated
    if st.session_state.report_generated and st.session_state.report_data:
        st.markdown("---")
        st.markdown("## 📋 Audit Report Results")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Game", st.session_state.game_name)
        with col2:
            st.metric("Report Type", st.session_state.report_type)
        with col3:
            st.metric("Competitors", st.session_state.num_competitors)
        with col4:
            if st.session_state.sales_data and st.session_state.report_type == "Post-Launch":
                st.metric("Est. Revenue", st.session_state.sales_data.get('estimated_revenue', 'N/A'))
            else:
                st.metric("App ID", st.session_state.game_data.get('app_id', 'N/A'))

        # Phase 2.3 & Phase 4: Download buttons at top for easy access
        st.markdown("---")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_game_name = re.sub(r'[^\w\s-]', '', st.session_state.game_name).strip().replace(' ', '_')
        safe_game_name = safe_game_name[:50]

        # Two column layout for download buttons
        dl_col1, dl_col2 = st.columns(2)

        with dl_col1:
            # PDF Download
            try:
                # Enhance audit results with section scores if available
                enhanced_audit_results = st.session_state.audit_results.copy() if st.session_state.audit_results else {}

                if st.session_state.structured_data and 'sections' in st.session_state.structured_data:
                    sections = st.session_state.structured_data['sections']
                    section_scores = {s['name']: {'score': s['score'], 'rating': s['rating']}
                                    for s in sections if 'name' in s and 'score' in s}

                    if section_scores:
                        enhanced_audit_results['section_scores'] = section_scores
                        enhanced_audit_results['overall_score'] = st.session_state.structured_data.get('overall_score', 0)

                pdf_bytes, pdf_filename = create_downloadable_pdf(
                    st.session_state.report_data,
                    st.session_state.game_name,
                    st.session_state.report_type,
                    enhanced_audit_results
                )

                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_bytes,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    key="download_pdf_top"
                )
            except PDFGenerationError as e:
                logger.error(f"PDF generation failed: {e.message}")
                st.error(f"📄 {e.user_message}")
            except Exception as e:
                logger.error(f"Unexpected PDF error: {e}", exc_info=True)
                st.warning("📄 PDF generation unavailable. You can still download the Markdown version.")

        with dl_col2:
            # Markdown Download
            md_filename = f"{safe_game_name}_{st.session_state.report_type.replace('-', '_')}_Report_{timestamp}.md"

            st.download_button(
                label="📥 Download as Markdown",
                data=st.session_state.report_data,
                file_name=md_filename,
                mime="text/markdown",
                type="secondary",
                use_container_width=True,
                key="download_md_top"
            )

        # Display visual score summary if structured data available
        if st.session_state.structured_data and 'sections' in st.session_state.structured_data:
            st.markdown("---")
            st.markdown("### 📊 Score Summary")

            overall_score = st.session_state.structured_data.get('overall_score', 0)

            # Overall score with large metric
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                score_delta = None
                score_color = "normal"

                if overall_score >= 80:
                    score_label = "🟢 Excellent"
                    score_color = "normal"
                elif overall_score >= 65:
                    score_label = "🔵 Good"
                    score_color = "normal"
                elif overall_score >= 50:
                    score_label = "🟡 Fair"
                    score_color = "off"
                else:
                    score_label = "🔴 Needs Work"
                    score_color = "off"

                st.metric(
                    label="Overall Score",
                    value=f"{overall_score}/100",
                    delta=score_label,
                    delta_color=score_color
                )

            st.markdown("")

            # Section scores in expandable
            with st.expander("📋 Section Breakdown", expanded=False):
                sections = st.session_state.structured_data.get('sections', [])

                # Display sections in 2-column grid
                for idx in range(0, len(sections), 2):
                    col1, col2 = st.columns(2)

                    # First column
                    with col1:
                        if idx < len(sections):
                            section = sections[idx]
                            section_name = section.get('name', 'Unknown')
                            section_score = section.get('score', 0)
                            section_rating = section.get('rating', 'unknown')

                            st.markdown(f"**{section_name}**")
                            st.progress(section_score / 100)
                            st.caption(f"{section_score}/100 - {section_rating.title()}")
                            st.markdown("")

                    # Second column
                    with col2:
                        if idx + 1 < len(sections):
                            section = sections[idx + 1]
                            section_name = section.get('name', 'Unknown')
                            section_score = section.get('score', 0)
                            section_rating = section.get('rating', 'unknown')

                            st.markdown(f"**{section_name}**")
                            st.progress(section_score / 100)
                            st.caption(f"{section_score}/100 - {section_rating.title()}")
                            st.markdown("")

        # Display key metrics dashboard if Phase 2 data available
        if st.session_state.structured_data and st.session_state.structured_data.get('phase2_data'):
            st.markdown("---")
            st.markdown("### 🎯 Key Opportunities")

            phase2_data = st.session_state.structured_data['phase2_data']

            # Calculate key metrics
            total_reach = 0
            total_contacts = 0

            # Influencer reach
            if 'twitch' in phase2_data:
                streamers = phase2_data['twitch'].get('streamers', [])
                total_contacts += len(streamers)
                total_reach += sum(s.get('followers', 0) for s in streamers)

            if 'youtube' in phase2_data:
                channels = phase2_data['youtube'].get('channels', [])
                total_contacts += len(channels)
                total_reach += sum(c.get('subscribers', 0) for c in channels)

            if 'curators' in phase2_data:
                curators = phase2_data['curators'].get('curators', [])
                total_contacts += len(curators)
                total_reach += sum(c.get('followers', 0) for c in curators)

            # Community reach
            if 'reddit' in phase2_data:
                total_reach += phase2_data['reddit'].get('total_reach', 0)

            # Display metrics in columns
            metric_cols = st.columns(4)

            with metric_cols[0]:
                st.metric(
                    label="Total Reach",
                    value=f"{total_reach:,}",
                    help="Combined followers/subscribers across all influencers and communities"
                )

            with metric_cols[1]:
                st.metric(
                    label="Influencer Contacts",
                    value=total_contacts,
                    help="Total number of streamers, YouTubers, and curators identified"
                )

            with metric_cols[2]:
                revenue_impact = 0
                if 'regional_pricing' in phase2_data:
                    revenue_impact = phase2_data['regional_pricing'].get('revenue_impact', {}).get('revenue_increase_percent', 0)

                st.metric(
                    label="Revenue Potential",
                    value=f"+{revenue_impact:.0f}%",
                    help="Estimated revenue increase with optimized regional pricing"
                )

            with metric_cols[3]:
                loc_languages = 0
                if 'localization' in phase2_data:
                    missing_langs = phase2_data['localization'].get('missing_languages', [])
                    loc_languages = len([l for l in missing_langs if l.get('priority') == 'high'])

                st.metric(
                    label="High-ROI Languages",
                    value=loc_languages,
                    help="Number of high-priority language localizations identified"
                )

        # Display full report
        st.markdown("---")
        st.markdown("### 📝 Full Audit Report")

        # Report in expandable container
        with st.container():
            st.markdown(st.session_state.report_data)

        # Download buttons at bottom
        st.markdown("---")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_game_name = re.sub(r'[^\w\s-]', '', st.session_state.game_name).strip().replace(' ', '_')
        safe_game_name = safe_game_name[:50]

        # Two column layout for bottom download buttons
        dl_col1_bottom, dl_col2_bottom = st.columns(2)

        with dl_col1_bottom:
            # PDF Download
            try:
                # Enhance audit results with section scores if available
                enhanced_audit_results = st.session_state.audit_results.copy() if st.session_state.audit_results else {}

                if st.session_state.structured_data and 'sections' in st.session_state.structured_data:
                    sections = st.session_state.structured_data['sections']
                    section_scores = {s['name']: {'score': s['score'], 'rating': s['rating']}
                                    for s in sections if 'name' in s and 'score' in s}

                    if section_scores:
                        enhanced_audit_results['section_scores'] = section_scores
                        enhanced_audit_results['overall_score'] = st.session_state.structured_data.get('overall_score', 0)

                pdf_bytes, pdf_filename = create_downloadable_pdf(
                    st.session_state.report_data,
                    st.session_state.game_name,
                    st.session_state.report_type,
                    enhanced_audit_results
                )

                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_bytes,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    key="download_pdf_bottom"
                )
            except PDFGenerationError as e:
                logger.error(f"PDF generation failed (bottom): {e.message}")
                st.error(f"📄 {e.user_message}")
            except Exception as e:
                logger.error(f"Unexpected PDF error (bottom): {e}", exc_info=True)
                st.warning("📄 PDF generation unavailable. You can still download the Markdown version.")

        with dl_col2_bottom:
            # Markdown Download
            md_filename = f"{safe_game_name}_{st.session_state.report_type.replace('-', '_')}_Report_{timestamp}.md"

            st.download_button(
                label="📥 Download as Markdown",
                data=st.session_state.report_data,
                file_name=md_filename,
                mime="text/markdown",
                type="secondary",
                use_container_width=True,
                key="download_md_bottom"
            )

        # CSV Exports & Templates Section
        if st.session_state.structured_data and st.session_state.structured_data.get('phase2_data'):
            st.markdown("---")
            st.markdown("### 📦 Additional Resources")

            # Create tabs for different export types
            export_tabs = st.tabs(["📊 CSV Exports", "✉️ Outreach Templates", "📚 Marketing Guides"])

            # Tab 1: CSV Exports
            with export_tabs[0]:
                st.markdown("**Download structured data for your project management tools:**")

                try:
                    csv_exports = create_csv_exports(st.session_state.structured_data)

                    if csv_exports:
                        # Display available exports
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("#### Contact Lists")
                            for filename, csv_content in csv_exports.items():
                                if 'curator' in filename or 'streamer' in filename or 'youtube' in filename or 'reddit' in filename:
                                    st.download_button(
                                        label=f"📥 {filename}",
                                        data=csv_content,
                                        file_name=filename,
                                        mime="text/csv",
                                        key=f"csv_{filename}",
                                        use_container_width=True
                                    )

                        with col2:
                            st.markdown("#### Analysis Data")
                            for filename, csv_content in csv_exports.items():
                                if 'pricing' in filename or 'localization' in filename:
                                    st.download_button(
                                        label=f"📥 {filename}",
                                        data=csv_content,
                                        file_name=filename,
                                        mime="text/csv",
                                        key=f"csv_{filename}_analysis",
                                        use_container_width=True
                                    )

                        st.info("💡 **Tip**: Import these CSV files into spreadsheet tools for tracking outreach progress")
                    else:
                        st.info("No CSV exports available for this report")

                except Exception as e:
                    logger.error(f"CSV export error: {e}")
                    st.warning("CSV exports temporarily unavailable")

            # Tab 2: Outreach Templates
            with export_tabs[1]:
                st.markdown("**Customizable email templates for your outreach campaigns:**")

                try:
                    templates = generate_outreach_templates(st.session_state.game_data)

                    if templates:
                        template_cols = st.columns(3)

                        idx = 0
                        for template_name, template_content in templates.items():
                            with template_cols[idx % 3]:
                                display_name = template_name.replace('_template.txt', '').replace('_', ' ').title()
                                st.download_button(
                                    label=f"📧 {display_name}",
                                    data=template_content,
                                    file_name=template_name,
                                    mime="text/plain",
                                    key=f"template_{template_name}",
                                    use_container_width=True
                                )
                            idx += 1

                        st.info("💡 **Tip**: Customize these templates with game-specific details and personal touches")
                    else:
                        st.info("Templates temporarily unavailable")

                except Exception as e:
                    logger.error(f"Template generation error: {e}")
                    st.warning("Templates temporarily unavailable")

            # Tab 3: Marketing Guides
            with export_tabs[2]:
                st.markdown("**Comprehensive guides for Steam marketing success:**")

                guides = [
                    ("📄 Steam Store Optimization", "resources/steam_store_optimization.md", "Complete guide to optimizing your Steam store page"),
                    ("🎯 Influencer Outreach", "resources/influencer_outreach_guide.md", "Best practices for working with content creators"),
                    ("🚀 Launch Checklist", "resources/launch_checklist.md", "Step-by-step launch preparation timeline")
                ]

                for title, filepath, description in guides:
                    with st.expander(title):
                        st.markdown(f"**{description}**")

                        try:
                            guide_path = os.path.join(os.path.dirname(__file__), filepath)
                            if os.path.exists(guide_path):
                                with open(guide_path, 'r', encoding='utf-8') as f:
                                    guide_content = f.read()

                                st.download_button(
                                    label=f"📥 Download {title}",
                                    data=guide_content,
                                    file_name=os.path.basename(filepath),
                                    mime="text/markdown",
                                    key=f"guide_{os.path.basename(filepath)}",
                                    use_container_width=True
                                )

                                # Show preview
                                with st.expander("👀 Preview"):
                                    st.markdown(guide_content[:1000] + "..." if len(guide_content) > 1000 else guide_content)
                            else:
                                st.info(f"Guide not yet available: {filepath}")
                        except Exception as e:
                            logger.error(f"Guide read error for {filepath}: {e}")
                            st.info("Guide temporarily unavailable")

                st.info("💡 **Tip**: Save these guides for reference during your marketing campaign")

        # Success message
        st.success("✅ Report generated successfully! Download as PDF or Markdown, or use '🔄 Generate New Report' to analyze another game.")

if __name__ == "__main__":
    main()
