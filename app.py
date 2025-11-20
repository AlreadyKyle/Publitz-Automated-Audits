import streamlit as st
import os
import time
from datetime import datetime
from src.ai_generator import AIGenerator
from src.game_search import GameSearch
from src.steamdb_scraper import SteamDBScraper

# Page config
st.set_page_config(
    page_title="Publitz Automated Audits",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
                help="Enter your Anthropic API key. Get one at https://console.anthropic.com/"
            )

            if not api_key:
                st.warning("⚠️ Please enter your Anthropic API Key to continue")
                st.info("💡 **Tip**: Set ANTHROPIC_API_KEY environment variable to skip this step")
                st.stop()

    # Main input - Steam URL
    st.markdown("### 🎮 Enter Steam Game URL")

    steam_url = st.text_input(
        "Steam Store URL",
        placeholder="https://store.steampowered.com/app/12345/Game_Name/",
        help="Paste the full URL from Steam store page",
        label_visibility="collapsed"
    )

    # Example URLs
    with st.expander("📝 Example URLs"):
        st.code("https://store.steampowered.com/app/292030/The_Witcher_3_Wild_Hunt/", language="text")
        st.code("https://store.steampowered.com/app/730/CounterStrike_2/", language="text")
        st.code("https://store.steampowered.com/app/570/Dota_2/", language="text")

    # Generate button
    generate_button = st.button("🚀 Generate Audit Report", type="primary", use_container_width=True)

    if generate_button:
        if not steam_url:
            st.error("❌ Please enter a Steam URL")
            st.stop()

        try:
            # Initialize components
            game_search = GameSearch()
            steamdb_scraper = SteamDBScraper()
            ai_generator = AIGenerator(api_key)

            # Progress container
            progress_container = st.container()

            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Parse URL and get game data
                status_text.text("🔍 Fetching game data from Steam...")
                progress_bar.progress(10)

                game_data = game_search.get_game_from_url(steam_url)

                if not game_data:
                    st.error("❌ Invalid Steam URL or game not found. Please check the URL and try again.")
                    st.stop()

                game_name = game_data.get('name', 'Unknown Game')
                st.success(f"✅ Found game: **{game_name}**")
                progress_bar.progress(20)

                # Step 2: Auto-detect launch status
                status_text.text("🔎 Detecting launch status...")
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

                progress_bar.progress(30)

                # Step 3: Find competitor games
                status_text.text("🔍 Finding competitor games...")
                competitor_data = game_search.find_competitors(game_data, min_competitors=3, max_competitors=10)

                num_competitors = len(competitor_data)
                if num_competitors == 0:
                    status_text.text("🔍 Expanding competitor search...")
                    competitor_data = game_search.find_competitors_broad(game_data, min_competitors=5)
                    num_competitors = len(competitor_data)

                st.success(f"✅ Found {num_competitors} competitor games")
                progress_bar.progress(50)

                # Step 4: Gather Steam data
                status_text.text("📊 Gathering Steam market data...")
                sales_data = steamdb_scraper.get_sales_data(game_data['app_id'])
                progress_bar.progress(65)

                # Step 5: Gather competitor Steam data
                status_text.text("📊 Analyzing competitor performance...")
                for competitor in competitor_data:
                    competitor['steam_data'] = steamdb_scraper.get_sales_data(competitor['app_id'])
                progress_bar.progress(75)

                # Step 6: Generate AI report
                status_text.text("🤖 Generating comprehensive audit report with Claude AI...")

                if report_type == "Post-Launch":
                    report_data = ai_generator.generate_post_launch_report(
                        game_data,
                        sales_data,
                        competitor_data,
                        steamdb_data=sales_data
                    )
                else:
                    report_data = ai_generator.generate_pre_launch_report(
                        game_data,
                        competitor_data
                    )

                progress_bar.progress(100)
                status_text.text("✅ Report generated successfully!")

            # Clear progress indicators after short delay
            time.sleep(1)
            progress_container.empty()

            # Display results
            st.markdown("---")
            st.markdown("## 📋 Audit Report Results")

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Game", game_name)
            with col2:
                st.metric("Report Type", report_type)
            with col3:
                st.metric("Competitors", num_competitors)
            with col4:
                if sales_data and report_type == "Post-Launch":
                    st.metric("Est. Revenue", sales_data.get('estimated_revenue', 'N/A'))
                else:
                    st.metric("App ID", game_data.get('app_id', 'N/A'))

            # Display full report
            st.markdown("---")
            st.markdown("### 📝 Full Audit Report")

            # Report in expandable container
            with st.container():
                st.markdown(report_data)

            # Download button
            st.markdown("---")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{game_name.replace(' ', '_')}_{report_type.replace('-', '_')}_Report_{timestamp}.md"

            st.download_button(
                label="📥 Download Report as Markdown",
                data=report_data,
                file_name=filename,
                mime="text/markdown",
                type="primary",
                use_container_width=True
            )

            # Success message
            st.success("✅ Report generated successfully! Click the button above to download.")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            with st.expander("🔍 Error Details"):
                st.exception(e)
            st.info("💡 **Tip**: Make sure the Steam URL is correct and the game is publicly available.")

if __name__ == "__main__":
    main()
