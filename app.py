import streamlit as st
import os
import time
import re
from datetime import datetime
from src.ai_generator import AIGenerator
from src.game_search import GameSearch
from src.steamdb_scraper import SteamDBScraper
from src.pdf_generator import create_downloadable_pdf

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="Publitz Automated Audits",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

def main():
    # Header
    st.title("📊 Publitz Automated Game Audits")
    st.markdown("Paste a Steam game URL to generate a professional audit report")
    st.markdown("---")

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
                st.warning("⚠️ Please enter your Anthropic API Key to continue")
                st.info("💡 **Tip**: Set ANTHROPIC_API_KEY environment variable to skip this step")
                st.stop()

    # Validate API key format (basic check)
    if api_key:
        api_key = api_key.strip()
        if len(api_key) < 20:
            st.error("❌ Invalid API key format. Please check your API key.")
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
    col1, col2 = st.columns([3, 1])
    with col1:
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
    with col2:
        if st.session_state.report_generated:
            if st.button("🔄 Generate New Report", use_container_width=True, key="new_report_btn"):
                # Reset session state
                st.session_state.report_generated = False
                st.session_state.report_data = None
                st.session_state.game_name = None
                st.session_state.generating = False
                st.rerun()

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
                ai_generator = AIGenerator(api_key)

            # Progress tracking
            progress_bar = st.progress(0, text="Starting...")

            # Phase 2.2: Step 1 - Parse URL and get game data
            progress_bar.progress(10, text="🔍 Fetching game data from Steam...")
            with st.spinner("🔍 Fetching game data from Steam..."):
                game_data = game_search.get_game_from_url(steam_url)

            if not game_data:
                st.error("❌ Invalid Steam URL or game not found. Please check the URL and try again.")
                st.stop()

            game_name = game_data.get('name', 'Unknown Game')
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
                sales_data = steamdb_scraper.get_sales_data(game_data['app_id'])
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
                for competitor in competitor_data:
                    try:
                        competitor['steam_data'] = steamdb_scraper.get_sales_data(competitor['app_id'])
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
                # Use 3-pass system for all reports
                report_data, audit_results = ai_generator.generate_report_with_audit(
                    game_data,
                    sales_data,
                    competitor_data,
                    steamdb_data=sales_data,
                    report_type=report_type,
                    review_stats=review_stats,
                    capsule_analysis=capsule_analysis
                )

            progress_bar.progress(100, text="✅ Report generated successfully!")

            # Store in session state
            st.session_state.report_generated = True
            st.session_state.report_data = report_data
            st.session_state.audit_results = audit_results  # Phase 3: Store audit results
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

        except Exception as e:
            # Phase 2.1: Reset generating state on error
            st.session_state.generating = False
            st.error(f"❌ An error occurred: {str(e)}")
            with st.expander("🔍 Error Details"):
                st.exception(e)
            st.info("💡 **Tip**: Make sure the Steam URL is correct and the game is publicly available.")
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
                pdf_bytes, pdf_filename = create_downloadable_pdf(
                    st.session_state.report_data,
                    st.session_state.game_name,
                    st.session_state.report_type,
                    st.session_state.audit_results
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
            except Exception as e:
                st.error(f"PDF generation unavailable: {str(e)}")

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
                pdf_bytes, pdf_filename = create_downloadable_pdf(
                    st.session_state.report_data,
                    st.session_state.game_name,
                    st.session_state.report_type,
                    st.session_state.audit_results
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
            except Exception as e:
                st.error(f"PDF generation unavailable: {str(e)}")

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

        # Success message
        st.success("✅ Report generated successfully! Download as PDF or Markdown, or use '🔄 Generate New Report' to analyze another game.")

if __name__ == "__main__":
    main()
